#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""__description__
"""

__author__ = "Christina Ludwig, GIScience Research Group, Heidelberg University"
__email__ = "christina.ludwig@uni-heidelberg.de"

import requests
import json

if __name__ == "__main__":
    BASE = "http://127.0.0.1:5000/"

    response = requests.get(BASE + "traffic?bbox=8.3197,48.9405,8.4041,49.0511")
    print(response)
    print(data)