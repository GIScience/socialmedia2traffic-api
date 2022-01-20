#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fill database with highway and speed data"""

__author__ = "Christina Ludwig, GIScience Research Group, Heidelberg University"
__email__ = "christina.ludwig@uni-heidelberg.de"

from pathlib import Path
import geopandas as gpd
from sm2t.database import open_connection, execute_query, open_engine
from geoalchemy2 import Geometry
import os
import logging


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


def import_cities(data_dir):
    """Import data from each city"""
    data_dir = Path(data_dir)
    city_dirs = data_dir.iterdir()

    create_speed_table(conn)
    create_highways_table(conn)

    for city in city_dirs:
        city_name = city.stem
        logging.info(f"Importing highways for {city_name}")
        try:
            import_highways(city / "edges.shp", conn)
        except Exception as e:
            logging.info(e)
        logging.info(f"Importing speed for {city_name}")
        try:
            import_speed_data(city / "speed.csv", conn)
        except Exception as e:
            logging.info(e)


if __name__ == "__main__":
    conn, message = open_connection()
    logging.info(message)
    import_cities("/data")
    conn.close()
