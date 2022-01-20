#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test utility functions"""

from sm2t.utils import parse_bbox
import datetime


def test_parse_bbox():
    """
    Test if name of output file is correct
    :return:
    """
    bbox = "8.3197,-48.9405,-8.4041,49.0511"
    date = datetime.date.today().strftime("%Y%m%d")
    expected_coordinates = [8.3197, -48.9405, -8.4041, 49.0511]
    expected_outfile = f"sm2t-{date}-e8319700_s48940500_w8404100_n49051100.csv"
    coordinates, outfile = parse_bbox(bbox)
    assert coordinates == expected_coordinates
    assert expected_outfile == outfile
