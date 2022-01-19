#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fill database with highway and speed data"""

__author__ = "Christina Ludwig, GIScience Research Group, Heidelberg University"
__email__ = "christina.ludwig@uni-heidelberg.de"

from pathlib import Path
from sm2t.database import open_connection, create_speed_table, import_highways, import_speed_data, create_highways_table

import logging
import logging.config
logging.config.fileConfig('logging.conf', disable_existing_loggers=False)


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
    conn, message = open_connection("./database.ini")
    logging.info(message)
    import_cities("/data")
    conn.close()
