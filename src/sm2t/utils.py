#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utility functions"""

__author__ = "Christina Ludwig, GIScience Research Group, Heidelberg University"
__email__ = "christina.ludwig@uni-heidelberg.de"

import datetime


def parse_bbox(bbox):
    """
    Parse coordinates and return output file name
    :return:
    """
    coords = [float(x) for x in bbox.split(",")]
    rounded = [int(round(x * 1e6, 0)) for x in coords]
    date = datetime.date.today().strftime("%Y%m%d")

    c0 = f"w{rounded[0] * -1}" if rounded[0] < 0 else f"e{rounded[0]}"
    c2 = f"w{rounded[2] * -1}" if rounded[2] < 0 else f"e{rounded[2]}"
    c1 = f"s{rounded[1] * -1}" if rounded[1] < 0 else f"n{rounded[1]}"
    c3 = f"s{rounded[3] * -1}" if rounded[3] < 0 else f"n{rounded[3]}"

    return coords, f"sm2t-{date}-{c0}_{c1}_{c2}_{c3}.csv"
