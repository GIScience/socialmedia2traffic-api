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
          hour_of_day int,
          speed_kph_p85 int,
          geometry geometry(LINESTRING, 4326),
          CONSTRAINT fid_pk PRIMARY KEY (fid, hour_of_day)
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
          speed_kph_p85 int,
          CONSTRAINT fid_hour_pk PRIMARY KEY (fid, hour_of_day)
        );
        """
        con.execute(text(query))


def edit_fid(table_name, engine, fid_offset):
    """
    Offset fid of the table so that they are unique across cities
    :param table_name:
    :type table_name:
    :param engine:
    :type engine:
    :return:
    :rtype:
    """
    with engine.connect() as con:
        logger.info(f"UPDATE {table_name} SET fid = fid + {int(fid_offset)};")
        query = f"UPDATE {table_name} SET fid = fid + {str(int(fid_offset))};"
        con.execute(text(query))


def insert_highways(table_name, engine):
    """
    insert_into_table
    :param engine:
    :return:
    """
    with engine.connect() as con:
        query = (
            f"INSERT INTO highways(fid, osm_way_id, osm_start_node_id, osm_end_node_id, hour_of_day, speed_kph_p85, geometry) "
            f"SELECT fid, osm_way_id, osm_start_node_id, osm_end_node_id, hour_of_day, speed_kph_p85, geometry FROM {table_name};"
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


def join_tables(table_highways, table_speed, table_joined, engine):
    """
    Join two tables
    :param table1:
    :type table1:
    :param table2:
    :type table2:
    :return:
    :rtype:
    """
    with engine.connect() as con:
        query = f"""
            CREATE TABLE {table_joined} AS SELECT {table_highways}.fid, {table_highways}.osm_way_id, {table_highways}.osm_start_node_id,
            {table_highways}.osm_end_node_id, {table_speed}.hour_of_day, {table_speed}.speed_kph_p85, {table_highways}.geometry
             FROM {table_speed}
            LEFT OUTER JOIN {table_highways} ON ({table_speed}.fid = {table_highways}.fid);
            """
        con.execute(text(query))
        query = "DELETE FROM {table_joined} WHERE fid is NULL;"
        con.execute(text(query))


def delete_highway_pedestrian(table_name, engine):
    """
    Filter edges by highway tag. Delete all edges with highway=path
    :return:
    :rtype:
    """
    with engine.connect() as con:
        query = f"DELETE FROM {table_name} WHERE highway = 'pedestrian';"
        logger.info(query)
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
    create_speed_table(engine)

    # edges_tables = find_tables(engine, "edges_*")
    # speed_tables = find_tables(engine, "speed_predicted_*")

    # Offsets
    edges_files = list(input_dir.glob("edges_*.sql"))
    for i, edges_file in enumerate(edges_files):

        city_name = edges_file.stem.split("_")[1]
        speed_file = list(input_dir.glob(f"speed_predicted_{city_name}.sql"))
        if len(speed_file) != 1:
            logger.warning(f"speed_predicted_{city_name}.sql not found.")
            continue
        else:
            speed_file = speed_file[0]

        fid_offset = int(i * 10e10)

        logger.info(f"Importing {edges_file}...")
        edges_table_name = edges_file.stem
        import_table(edges_file)
        logger.info(f"Editing fid: {str(int(fid_offset))}")
        edit_fid(edges_table_name, engine, fid_offset)
        logger.info(f"Deleting rows in {edges_table_name}...")
        delete_highway_pedestrian(edges_table_name, engine)

        logger.info(f"Importing {speed_file}...")
        speed_table_name = speed_file.stem
        import_table(speed_file)
        logger.info(f"Editing fid: {str(int(fid_offset))}")
        edit_fid(speed_table_name, engine, fid_offset)

        # Join highways and speed
        join_tables(
            edges_table_name, speed_table_name, f"highways_speed_{city_name}", engine
        )

        insert_highways(f"highways_speed_{city_name}", engine)

        drop_table(edges_table_name, engine)
        drop_table(speed_table_name, engine)
        drop_table(f"highways_speed_{city_name}", engine)

        # insert_speed(speed_file.stem, engine)

    # Create views for edges and speed data of all cities
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
