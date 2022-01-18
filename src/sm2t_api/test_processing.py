#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""__description__"""

__author__ = "Christina Ludwig, GIScience Research Group, Heidelberg University"
__email__ = "christina.ludwig@uni-heidelberg.de"

from processing import open_connection, import_highways, load_highways, import_speed_data
import pandas as pd


def test_import_highways():
    """Tests whether highway data is imported into database"""
    conn, message = open_connection()
    test_geometry_file = "/Users/chludwig/Development/sm2t/sm2t_api/data/test_geometries_berlin.shp"
    cmd, success = import_highways(test_geometry_file, conn)
    conn.close()
    assert success == True


def test_import_speed_data():
    """Tests whether speed data is imported into database"""
    conn, message = open_connection()
    test_speed_file = "/Users/chludwig/Development/sm2t/sm2t_api/data/speed_berlin.shp"
    cmd, success = import_speed_data(test_speed_file, conn)
    conn.close()
    assert success == True


def test_load_highway_data():
    """Loads data from database within bounding box"""
    conn, message = open_connection()
    test_bbox = (13.3792, 52.5136, 13.3842, 52.5168)
    test = load_highways(test_bbox, conn)
    assert len(test) > 0
    conn.close()


def test_load_speed_data():
    """Tests whether speed data can be loaded"""
    conn, message = open_connection()
    df = pd.read_sql_query('select * from "speed"', con=conn)
    assert len(df) > 0

