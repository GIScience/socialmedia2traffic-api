#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Database management functions"""

import os
import psycopg2
import geopandas as gpd
import pandas as pd
import logging
from sqlalchemy import create_engine


def open_engine():
    """Opens a sqlalchemy engine"""
    return create_engine(
        f"postgresql://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@{os.environ['HOST']}:{os.environ['POSTGRES_PORT']}/{os.environ['POSTGRES_DB']}"
    )


def open_connection():
    """Connect to the PostgreSQL database server"""
    conn = None
    try:
        # connect to the PostgreSQL server
        logging.info("Connecting to the PostgreSQL database...")
        conn = psycopg2.connect(
            host=os.environ["HOST"],
            port=os.environ["POSTGRES_PORT"],
            dbname=os.environ["POSTGRES_DB"],
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
        )

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


def execute_query(connection, query: str):
    """
    Execute sql query
    :param connection: psycopg2.connection object
    :param query: SQL query string
    :return:
    """
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
    """Loads highways within bounding box from database
    :param bbox: Bounding box (min_lon, min_lat, max_lon, max_lat)
    :param conn: psycopg2.connection object
    :return: geopandas.GeoDataFrame
    """
    bbox_str = ", ".join([str(x) for x in bbox])
    sql = f"SELECT * FROM highways WHERE highways.geom && ST_MakeEnvelope({bbox_str}, 4326);"
    highways = gpd.read_postgis(sql, con=conn)
    return highways


def load_speed_by_bbox_old(bbox: str, conn):
    """Load speed data of specified bounding box
    :param bbox: Bounding box (min_lon, min_lat, max_lon, max_lat)
    :param conn: psycopg2.connection object
    :return: pandas.DataFrame
    """
    bbox_str = ", ".join([str(x) for x in bbox])
    query = f"""
        WITH selection AS (SELECT fid, osm_way_id, osm_start_node_id, osm_end_node_id
        FROM highways
        WHERE highways.geometry && ST_MakeEnvelope({bbox_str}, 4326))
        SELECT selection.osm_way_id, selection.osm_start_node_id, selection.osm_end_node_id, speed.hour_of_day, speed.speed_kph_p85
        FROM speed
        LEFT OUTER JOIN selection ON (speed.fid = selection.fid)
        WHERE speed.fid IN (SELECT fid FROM selection);
    """
    df = pd.read_sql_query(query, con=conn)
    return df


def load_speed_by_bbox(bbox: str, conn):
    """Load speed data of specified bounding box
    :param bbox: Bounding box (min_lon, min_lat, max_lon, max_lat)
    :param conn: psycopg2.connection object
    :return: pandas.DataFrame
    """
    bbox_str = ", ".join([str(x) for x in bbox])
    query = f"""
        SELECT fid, osm_way_id, osm_start_node_id, osm_end_node_id, hour_of_day, speed_kph_p85
        FROM highways
        WHERE highways.geometry && ST_MakeEnvelope({bbox_str}, 4326))
    """
    df = pd.read_sql_query(query, con=conn)
    return df
