#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utility functions"""

import datetime


def parse_bbox(bbox: str):
    """
    Parse coordinates and return output file name
    :param bbox: Bounding box as str min_lon,min_lat,max_lon,max_lat
    :return: List of coordinates, filename with bounding box
    """
    coords = [float(x) for x in bbox.split(",")]
    rounded = [int(round(x * 1e6, 0)) for x in coords]
    date = datetime.date.today().strftime("%Y%m%d")

    c0 = f"w{rounded[0] * -1}" if rounded[0] < 0 else f"e{rounded[0]}"
    c2 = f"w{rounded[2] * -1}" if rounded[2] < 0 else f"e{rounded[2]}"
    c1 = f"s{rounded[1] * -1}" if rounded[1] < 0 else f"n{rounded[1]}"
    c3 = f"s{rounded[3] * -1}" if rounded[3] < 0 else f"n{rounded[3]}"

    return coords, f"sm2t-{date}-{c0}_{c1}_{c2}_{c3}.csv"


def check_bbox(bbox: list, bbox_max: float):
    """
    Check if size of bbox is lower than maximum
    :param bbox:
    :return:
    """
    if ((bbox[2] - bbox[0]) > bbox_max) or ((bbox[3] - bbox[1]) > bbox_max):
        return False
    else:
        return True
