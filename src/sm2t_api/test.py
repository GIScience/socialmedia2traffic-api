#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""__description__
"""

__author__ = "Christina Ludwig, GIScience Research Group, Heidelberg University"
__email__ = "christina.ludwig@uni-heidelberg.de"

from sm2t_api.api import file_name
import datetime



def test_output_name():
    """
    Parse coordinates and return output file name
    :return:
    """
    bbox = "8.3197,-48.9405,-8.4041,49.0511"
    date = datetime.date.today().strftime("%Y%m%d")
    expected_coordinates = [8.3197,-48.9405,-8.4041,49.0511]
    expected_outfile = f"sm2t-{date}-e8319700_s48940500_w8404100_n49051100.csv"
    coordinates, outfile = file_name(bbox)
    assert coordinates == expected_coordinates
    assert expected_outfile == outfile