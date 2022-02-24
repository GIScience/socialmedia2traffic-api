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


def create_index(engine):
    """
    Creates spatial index for table
    :param table_name:
    :return:
    """
    with engine.connect() as con:
        query = "DROP INDEX IF EXISTS highways_geometry_idx;"
        con.execute(text(query))
        query = "DROP INDEX IF EXISTS highways_fid_idx;"
        con.execute(text(query))
        query = "DROP INDEX IF EXISTS speed_fid_idx;"
        con.execute(text(query))

        index_query = (
            "CREATE INDEX highways_geometry_idx ON highways USING GIST(geometry);"
        )
        con.execute(text(index_query))
        index_query = "CREATE INDEX highways_fid_idx ON highways(fid);"
        con.execute(text(index_query))
        index_query = "CREATE INDEX speed_fid_idx ON speed(fid);"
        con.execute(text(index_query))


def create_highways_table(engine):
    """
    Create the highways table. If it exists drop it.
    :param engine:
    :return:
    """
    # Create table for highways
    with engine.connect() as con:
        query = "DROP TABLE IF EXISTS highways"
        con.execute(text(query))

        query = """
        CREATE TABLE highways (
          fid bigint,
          osm_way_id bigint,
          osm_start_node_id bigint,
          osm_end_node_id bigint,
          geometry geometry(LINESTRING, 4326)
        );"""
        con.execute(text(query))


def create_speed_table(engine):
    """Create tables"""

    with engine.connect() as con:
        query = "DROP TABLE IF EXISTS speed"
        con.execute(text(query))

        query = """
        CREATE TABLE speed (
          fid bigint,
          hour_of_day int,
          speed_kph_p85 int
        );
        """
        con.execute(text(query))


def insert_highways(table_name, engine):
    """
    insert_into_table
    :param engine:
    :return:
    """
    with engine.connect() as con:
        query = (
            f"INSERT INTO highways(fid, osm_way_id, osm_start_node_id, osm_end_node_id, geometry) "
            f"SELECT fid, osm_way_id, osm_start_node_id, osm_end_node_id, geometry FROM {table_name};"
        )
        con.execute(text(query))


def insert_speed(table_name, engine):
    """
    insert_into_table
    :param engine:
    :return:
    """
    with engine.connect() as con:
        query = (
            f"INSERT INTO speed(fid, hour_of_day, speed_kph_p85) "
            f"SELECT fid, hour_of_day, speed_kph_p85 FROM {table_name};"
        )
        con.execute(text(query))


def drop_table(table_name, engine):
    """
    Drops the table
    :param table_name:
    :param engine:
    :return:
    """
    with engine.connect() as con:
        query = f"DROP TABLE IF EXISTS {table_name};"
        con.execute(text(query))


def populate_database(input_dir: str):
    """
    Populate database with edges and predicted speed data from files
    :param input_dir: Path to directory containing data as .sql files. Each file should contain a table.
    The name of the file will be the table name.
    :return:
    """
    input_dir = Path(input_dir)
    engine = get_engine_from_environment()

    create_highways_table(engine)

    # Import edges tables
    edges_tables = find_tables(engine, "edges_*")
    edges_files = input_dir.glob("edges_*.sql")
    for edges_file in edges_files:
        if edges_file.stem in edges_tables:
            logger.info(f"Table {edges_file.stem} already exists. Skipped.")
            continue
        logger.info(f"Importing {edges_file}...")
        import_table(edges_file)
        insert_highways(edges_file.stem, engine)
        drop_table(edges_file.stem, engine)

    # Import speed tables
    create_speed_table(engine)
    speed_files = input_dir.glob("speed_predicted_*.sql")
    for speed_file in speed_files:
        logger.info(f"Importing {speed_file}...")
        import_table(speed_file)
        insert_speed(speed_file.stem, engine)
        drop_table(speed_file.stem, engine)

    # Create views for edges and speed data of all cities
    # create_views(engine)
    create_index(engine)


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
