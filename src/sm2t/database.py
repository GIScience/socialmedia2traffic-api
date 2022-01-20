#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""__description__"""

__author__ = "Christina Ludwig, GIScience Research Group, Heidelberg University"
__email__ = "christina.ludwig@uni-heidelberg.de"

import os
import psycopg2
import geopandas as gpd
import pandas as pd
import logging
from sqlalchemy import create_engine


def open_engine():
    """Opens a sqlalchemy engine"""
    return create_engine(f"postgresql://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@{os.environ['HOST']}:{os.environ['PORT']}/{os.environ['POSTGRES_DB']}")


def open_connection():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # connect to the PostgreSQL server
        logging.info("Connecting to the PostgreSQL database...")
        conn = psycopg2.connect(host=os.environ['HOST'],
                                port=os.environ['PORT'],
                                dbname=os.environ['POSTGRES_DB'],
                                user=os.environ['POSTGRES_USER'],
                                password=os.environ['POSTGRES_PASSWORD'])

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
        connection.commit()
        logging.info("Query executed successfully")
    except psycopg2.OperationalError as e:
        logging.critical(f"The error '{e}' occurred")
        connection.rollback()
    except psycopg2.errors.InFailedSqlTransaction as e:
        logging.critical(e)
        connection.rollback()


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