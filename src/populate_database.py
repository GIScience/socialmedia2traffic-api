#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fill database with highway and speed data"""
import os
import time
from pathlib import Path
import geopandas as gpd
from sm2t.database import execute_query, open_engine
from geoalchemy2 import Geometry
from sqlalchemy import inspect
from sqlalchemy.sql import text
import re
from dotenv import load_dotenv
from sm2t.sql_utils import get_engine_from_environment
from sm2t.utils import init_logger

load_dotenv("../.env", verbose=True)

logger = init_logger("sm2t-api-populate-database")


def create_speed_table(conn):
    """Create tables"""
    query = """
    CREATE TABLE IF NOT EXISTS speed (
      id SERIAL PRIMARY KEY,
      osm_way_id integer,
      osm_start_node_id bigint,
      osm_end_node_id bigint,
      hour smallint,
      speed real,
      fid integer
    );
    """
    execute_query(conn, query)


def create_highways_table(conn):
    """Create tables"""
    query = """
    CREATE TABLE IF NOT EXISTS highways (
      id SERIAL PRIMARY KEY,
      fid integer,
      osm_way_id integer,
      osm_start_node_id bigint,
      osm_end_node_id bigint,
      geometry geometry(LINESTRING, 4326)
    );
    """
    execute_query(conn, query)


def import_highways(file, conn):
    """
    Imports highway geometries into database
    :param data_dir:
    :return:
    """
    assert Path(file).exists(), f"{file} does not exist"
    engine = open_engine()

    data = gpd.read_file(file)
    data = data.rename(
        columns={
            "u": "osm_start_node_id",
            "v": "osm_end_node_id",
            "osmid": "osm_way_id",
        }
    )
    data = data[
        ["fid", "osm_way_id", "osm_end_node_id", "osm_start_node_id", "geometry"]
    ]
    data.to_postgis(
        name="highways",
        con=engine,
        if_exists="append",
        index=False,
        dtype={"geometry": Geometry("LINESTRING", srid="4326")},
    )

    """
    PG = f"PG:host={conn.info.host} user={conn.info.user} password={conn.info.password} dbname={conn.info.dbname}"
    sql = f"SELECT u AS osm_start_node_id, v AS osm_end_node_id, osmid AS osm_way_id, fid FROM {filename}"
    cmd = [
        "ogr2ogr",
        "-f",
        "PostgreSQL",
        PG,
        file,
        "-nln",
        "highways",
        "-lco",
        "GEOMETRY_NAME=geom",
        "-sql",
        sql,
    ]
    try:
        success = subprocess.check_call(cmd)
    except subprocess.CalledProcessError as error:
        return cmd, error
    """

    return None, True


def import_speed_data(file, conn):
    """Import speed data"""
    assert Path(file).exists(), f"{file} does not exist"
    docker_file_path = Path("/data") / file.parents[0].stem / file.name
    import_csv_query = f"""
    COPY speed(osm_way_id, osm_start_node_id, osm_end_node_id, hour, speed, fid)
        FROM '{docker_file_path}'
        DELIMITER ','
        CSV HEADER;
    """
    execute_query(conn, import_csv_query)


def import_table(table_file):
    """
    Import table from file to database
    :param table_file: Path to file
    :return:
    """
    os.environ["PGPASSWORD"] = os.environ["POSTGRES_PASSWORD"]
    cmd = [
        "psql",
        "-d",
        os.environ["POSTGRES_DB"],
        "-p",
        os.environ["POSTGRES_PORT"],
        "-h",
        os.environ["HOST"],
        "-U",
        os.environ["POSTGRES_USER"],
        "<",
        str(table_file),
    ]
    os.system(" ".join(cmd))
    return True


def find_tables(engine, pattern):
    """
    Find matching tables
    :param engine:
    :return:
    """
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    pattern_filter = re.compile(pattern)
    edges_tables = list(filter(pattern_filter.match, tables))
    edges_tables.sort()
    return edges_tables


def create_views(engine):
    """
    Create view of all edges
    :return:
    """
    edges_tables = find_tables(engine, "edges_*")
    speed_tables = find_tables(engine, "speed_predicted_*")
    assert len(speed_tables) == len(edges_tables)

    i = 1
    for edge_table, speed_table in zip(edges_tables, speed_tables):
        print(edge_table)
        fid_offset = int(i * 10e10)
        with engine.connect() as con:
            query = f"UPDATE {edge_table} SET fid = fid + {fid_offset};"
            con.execute(text(query))
            query = f"UPDATE {speed_table} SET fid = fid + {fid_offset};"
            con.execute(text(query))

    with engine.connect() as con:
        con.execute(text("DROP TABLE IF EXISTS highways;"))
        union_terms = " ".join(
            [
                f" UNION SELECT fid, osm_way_id, osm_start_node_id, osm_end_node_id, geometry FROM {x}"
                for x in edges_tables[1:]
            ]
        )
        query = (
            f"CREATE TABLE highways AS "
            f"SELECT fid, osm_way_id, osm_start_node_id, osm_end_node_id, geometry FROM {edges_tables[0]} "
            + union_terms
        )
        con.execute(text(query))
        # Delete single tables
        for table in edges_tables:
            query = f"DROP TABLE IF EXISTS {table};"
            con.execute(text(query))

    with engine.connect() as con:
        con.execute(text("DROP TABLE IF EXISTS speed;"))
        union_terms = " ".join([f" UNION SELECT * FROM {x}" for x in speed_tables[1:]])
        query = (
            f"CREATE TABLE speed AS " f"SELECT * FROM {speed_tables[0]} " + union_terms
        )
        con.execute(text(query))
        # Delete single tables
        for table in speed_tables:
            query = f"DROP TABLE IF EXISTS {table};"
            con.execute(text(query))


def create_index(table_name, engine):
    """
    Creates spatial index for table
    :param table_name:
    :return:
    """
    with engine.connect() as con:
        index_query = (
            f"CREATE INDEX {table_name}_idx ON {table_name} USING GIST(geometry);"
        )
        con.execute(text(index_query))


def populate_database(input_dir: str):
    """
    Populate database with edges and predicted speed data from files
    :param input_dir: Path to directory containing data as .sql files. Each file should contain a table.
    The name of the file will be the table name.
    :return:
    """

    input_dir = Path(input_dir)
    engine = get_engine_from_environment()

    # Import edges tables
    edges_tables = find_tables(engine, "edges_*")
    edges_files = input_dir.glob("edges_*.sql")
    for edges_file in edges_files:
        if edges_file.stem in edges_tables:
            logger.info(f"Table {edges_file.stem} already exists. Skipped.")
            continue
        logger.info(f"Importing {edges_file}...")
        import_table(edges_file)

    # Import speed tables
    speed_files = input_dir.glob("speed_predicted_*.sql")
    for speed_file in speed_files:
        logger.info(f"Importing {speed_file}...")
        import_table(speed_file)

    # Create views for edges and speed data of all cities
    create_views(engine)
    create_index("highways", engine)


if __name__ == "__main__":

    # parser = argparse.ArgumentParser(
    #    description="Populates database with edges and speed data"
    # )
    # parser.add_argument(
    #    "--inputdir",
    #    "-i",
    #    required=True,
    #    dest="input_dir",
    #    type=str,
    #    help="Path to output directory",
    # )

    # args = parser.parse_args()
    # input_dir = args.input_dir

    # time.sleep(60)
    input_dir = os.environ["DB_DUMP_FILE"]

    populate_database(input_dir)
