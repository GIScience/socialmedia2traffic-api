#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test database functions"""


from sm2t.database import (
    open_connection,
    load_highways,
    load_speed_by_bbox,
)
from populate_database import import_speed_data, import_highways
import pandas as pd


def test_import_highways():
    """Tests whether highway data is imported into database"""
    conn, message = open_connection()
    test_geometry_file = "../data/berlin/edges.shp"
    cmd, success = import_highways(test_geometry_file, conn)
    conn.close()
    assert success is True


def test_import_speed_data():
    """Tests whether speed data is imported into database"""
    conn, message = open_connection()
    test_speed_file = "../data/berlin/speed.csv"
    cmd, success = import_speed_data(test_speed_file, conn)
    conn.close()
    assert success is True


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


def test_load_speed_by_bbox():
    """Tests whether speed data can be loaded"""
    bbox = (13.3472, 52.499, 13.4117, 52.5304)
    conn, message = open_connection()
    df = load_speed_by_bbox(bbox, conn)
    assert len(df) == 120
