#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utility functions"""

import datetime
import logging
import os


def parse_bbox(bbox: str):
    """
    Parse coordinates and return output file name
    :param bbox: Bounding box as str min_lon,min_lat,max_lon,max_lat
    :return: List of coordinates, filename with bounding box
    """
    coords = [float(x) for x in bbox.split(",")]
    if len(coords) < 4:
        return (
            False,
            "Bounding box is invalid. Required format: min_lon,min_lat,max_lon,max_lat",
        )
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
    if (bbox[2] < bbox[0]) or (bbox[3] < bbox[1]):
        return (
            False,
            "Bounding box is invalid. Required format: min_lon,min_lat,max_lon,max_lat. min_lon must be smaller than max_lon, min_lat must be smaller than max_lat.",
        )
    elif ((bbox[2] - bbox[0]) > bbox_max) or ((bbox[3] - bbox[1]) > bbox_max):
        return (
            False,
            f"Bounding box is too big. The maximum width and height of the bounding box is {os.getenv('MAX_BBOX_DEGREE')} degree.",
        )
    else:
        return True, None


def init_logger(name, log_file=None):
    """
    Set up a logger instance with stream and file logger
    :param name: Name of logger (str)
    :param log_file: path to log file (str)
    :return:
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%m-%d-%Y %I:%M:%S",
    )
    # Add stream handler
    streamhandler = logging.StreamHandler()
    streamhandler.setLevel(logging.INFO)
    streamhandler.setFormatter(formatter)
    logger.addHandler(streamhandler)
    # Log file handler
    if log_file:
        assert os.path.exists(
            os.path.dirname(log_file)
        ), "Error during logger setup: Directory of log file does not exist."
        filehandler = logging.FileHandler(filename=log_file)
        filehandler.setLevel(logging.INFO)
        filehandler.setFormatter(formatter)
        logger.addHandler(filehandler)
    return logger
