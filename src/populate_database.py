#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""__description__"""

__author__ = "Christina Ludwig, GIScience Research Group, Heidelberg University"
__email__ = "christina.ludwig@uni-heidelberg.de"

from pathlib import Path
from sm2t.database import create_speed_table, import_highways, import_speed_data, open_connection


def import_cities(data_dir):
    """Import data from each city"""
    data_dir = Path(data_dir)
    city_dirs = data_dir.iterdir()

    create_speed_table(conn)

    for city in city_dirs:
        city_name = city.stem
        print(f"Importing highways for {city_name}")
        try:
            import_highways(city / "edges.shp", conn)
        except Exception as e:
            print(e)
        print(f"Importing speed for {city_name}")
        try:
            import_speed_data(city / "speed.csv", conn)
        except Exception as e:
            print(e)

    conn.close()


if __name__ == "__main__":
    conn, message = open_connection()
    print(message)

    import_cities("../../data")