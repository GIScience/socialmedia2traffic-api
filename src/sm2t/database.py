#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""__description__"""

__author__ = "Christina Ludwig, GIScience Research Group, Heidelberg University"
__email__ = "christina.ludwig@uni-heidelberg.de"

from pathlib import Path

import psycopg2
from config import config
import geopandas as gpd
import subprocess

# from dotenv import load_dotenv, find_dotenv

# Load settings from ./.env file
# load_dotenv("../../.env", verbose=True)
# load_dotenv(find_dotenv())



def open_connection():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print("Connecting to the PostgreSQL database...")
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        # execute a statement
        print("PostgreSQL database version:")
        cur.execute("SELECT version()")

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        print(db_version)

    except (Exception, psycopg2.DatabaseError) as error:
        return False, error

    return conn, "Database connection working."


def import_highways(file, conn):
    """
    Imports highway geometries into database
    :param data_dir:
    :return:
    """
    assert Path(file).exists(), f"{file} does not exist"
    filename = Path(file).stem
    PG = f"PG:host={conn.info.host} user={conn.info.user} password={conn.info.password} dbname={conn.info.dbname}"
    sql = f"SELECT u AS osm_start_node_id, v AS osm_end_node_id, osmid AS osm_way_id FROM {filename}"
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
    return cmd, success


def load_highways(bbox: tuple, conn):
    """Loads highways within bounding box from database"""
    bbox_str = ", ".join([str(x) for x in bbox])
    sql = f"SELECT * FROM highways WHERE highways.geom && ST_MakeEnvelope({bbox_str}, 4326);"
    highways = gpd.read_postgis(sql, con=conn)
    return highways


def execute_query(connection, query):
    # connection.autocommit = True
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()  # <-- ADD THIS LINE
        print("Query executed successfully")
    except psycopg2.OperationalError as e:
        print(f"The error '{e}' occurred")
        connection.rollback()
    except psycopg2.errors.InFailedSqlTransaction as e:
        print(e)
        connection.rollback()


def create_speed_table(conn):
    """Create tables"""
    create_speed_table = """
    CREATE TABLE IF NOT EXISTS speed (
      id SERIAL PRIMARY KEY,
      osm_way integer,
      start_node bigint,
      end_node bigint,
      hour smallint,
      speed real
    );
    """
    execute_query(conn, create_speed_table)


def import_speed_data(file, conn):
    """Import speed data"""
    assert Path(file).exists(), f"{file} does not exist"
    docker_file_path = Path("/data") / file.parents[0].stem / file.name
    import_csv_query = f"""
    COPY speed(osm_way, start_node, end_node, speed, hour)
        FROM '{docker_file_path}'
        DELIMITER ','
        CSV HEADER;
    """
    execute_query(conn, import_csv_query)


def import_cities(data_dir):
    """Import data from each city"""
    data_dir = Path(data_dir)
    city_dirs = data_dir.iterdir()

    create_speed_table(conn)

    for city in city_dirs:
        city_name = city.stem
        print(f"Importing highways for {city_name}")
        try:
            import_highways(city / "edges.shp", conn)
        except Exception as e:
            print(e)
        print(f"Importing speed for {city_name}")
        try:
            import_speed_data(city / "speed.csv", conn)
        except Exception as e:
            print(e)

    conn.close()


if __name__ == "__main__":
    conn, message = open_connection()
    print(message)

    #berlin_network_file = "/Users/chludwig/Development/sm2t/sm2t_centrality/data/extracted/berlin/centrality_fmm/temp/network/edges.shp"
    #bbox = (13.3472, 52.499, 13.4117, 52.5304)

    #berlin_file = "../../data/speed_berlin.csv"
    #speed = pd.read_csv(berlin_file)
    #speed.drop("Unnamed: 0", axis=1, inplace=True)
    #speed.to_csv(berlin_file, index=False)

    #sql = "ALTER TABLE highways " "ALTER COLUMN osm_way TYPE INTEGER;"
    #execute_query(conn, sql)
    import_cities("../../data")