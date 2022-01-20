#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""__description__
"""

__author__ = "Christina Ludwig, GIScience Research Group, Heidelberg University"
__email__ = "christina.ludwig@uni-heidelberg.de"

import requests


if __name__ == "__main__":
    BASE = "http://127.0.0.1:5000/"

    response = requests.get(BASE + "traffic/csv?bbox=13.3472,52.499,13.4117,52.5304")
    print(response)
    print(response.content)