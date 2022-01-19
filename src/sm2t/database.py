#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""__description__"""

__author__ = "Christina Ludwig, GIScience Research Group, Heidelberg University"
__email__ = "christina.ludwig@uni-heidelberg.de"

from pathlib import Path

import psycopg2
from geoalchemy2 import Geometry

from sm2t.config import config
import geopandas as gpd
import subprocess
import pandas as pd
import logging
from sqlalchemy import create_engine

# from dotenv import load_dotenv, find_dotenv

# Load settings from ./.env file
# load_dotenv("../../.env", verbose=True)
# load_dotenv(find_dotenv())

USER="postgres"
PASSWORD="postgres"
DATABASE="postgres"
PORT=5432
HOST="db"


def open_connection(filename):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config(filename)

        # connect to the PostgreSQL server
        logging.info("Connecting to the PostgreSQL database...")
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        # execute a statement
        logging.info("PostgreSQL database version:")
        cur.execute("SELECT version()")

        # display the PostgreSQL database server version
        db_version = cur.fetchone()
        logging.info(db_version)

    except (Exception, psycopg2.DatabaseError) as error:
        logging.critical(error)
        return False, error

    return conn, "Database connection working."


def execute_query(connection, query):
    # connection.autocommit = True
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()  # <-- ADD THIS LINE
        logging.info("Query executed successfully")
    except psycopg2.OperationalError as e:
        logging.critical(f"The error '{e}' occurred")
        connection.rollback()
    except psycopg2.errors.InFailedSqlTransaction as e:
        logging.critical(e)
        connection.rollback()



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
    engine = create_engine(f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")
    data = gpd.read_file(file)
    data = data.rename(columns={"u": "osm_start_node_id",
                                "v": "osm_end_node_id",
                                "osmid": "osm_way_id"})
    data = data[["fid", "osm_way_id", "osm_end_node_id", "osm_start_node_id", "geometry"]]
    data.to_postgis(name="highways",
                   con=engine,
                   if_exists="append",
                   index=False,
                   dtype={'geometry': Geometry('LINESTRING', srid='4326')})

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


def load_highways(bbox: tuple, conn):
    """Loads highways within bounding box from database"""
    bbox_str = ", ".join([str(x) for x in bbox])
    sql = f"SELECT * FROM highways WHERE highways.geom && ST_MakeEnvelope({bbox_str}, 4326);"
    highways = gpd.read_postgis(sql, con=conn)
    return highways


def load_speed_by_bbox(bbox, conn):
    """Load speed data of specified bounding box"""
    bbox_str = ", ".join([str(x) for x in bbox])
    query = f"""
        WITH selection AS (SELECT fid
        FROM highways
        WHERE highways.geometry && ST_MakeEnvelope({bbox_str}, 4326)) 
        SELECT osm_way_id, osm_start_node_id, osm_end_node_id, hour, speed
        FROM speed
        WHERE speed.fid IN (SELECT fid FROM selection);
    """
    df = pd.read_sql_query(query, con=conn)
    return df



if __name__ == "__main__":
    conn, message = open_connection()
    print(message)

    berlin_network_file = "/Users/chludwig/Development/sm2t/sm2t_api/data/berlin/edges.shp"
    bbox = (13.3472, 52.499, 13.4117, 52.5304)

    berlin_highways = gpd.read_file(berlin_network_file)
    berlin_highways = berlin_highways.rename(columns={"u": "osm_start_node_id",
                                        "v": "osm_end_node_id",
                                        "osmid": "osm_way_id"})
    berlin_highways["fid"] = 1
    berlin_highways = berlin_highways.rename(columns={"osm_start_": "u" ,
                                        "osm_end_no": "v",
                                        "osm_way_id": "osmid"})
    berlin_highways.to_file(berlin_network_file)

    berlin_file = "/Users/chludwig/Development/sm2t/sm2t_api/data/berlin/speed.csv"
    speed = pd.read_csv(berlin_file)
    speed["fid"] = 1
    speed.drop("id", axis=1, inplace=True)
    speed.set_index(['osm_way_id', 'osm_start_node_id', 'osm_end_node_id'], inplace=True)
    berlin_highways.set_index(['osm_way_id', 'osm_start_node_id', 'osm_end_node_id'], inplace=True)

    speed_test = speed.join(berlin_highways, how="inner")[['hour', 'speed', 'id']]

    speed.to_csv(berlin_file, index=False)

    #sql = "ALTER TABLE highways " "ALTER COLUMN osm_way TYPE INTEGER;"
    #execute_query(conn, sql)
    import_cities("../../data")