#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""__description__
"""

__author__ = "Christina Ludwig, GIScience Research Group, Heidelberg University"
__email__ = "christina.ludwig@uni-heidelberg.de"

import json

from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
import pandas as pd

# todo: https://flask-restful.readthedocs.io/en/latest/extending.html#response-formats

data_path = "/Users/chludwig/Development/spark/karlsruhe-regbez-75708-snappy"

app = Flask(__name__)
api = Api(app)

data = pd.DataFrame({"osmId": [1, 2],
                     "speed": [100, 80]})

class Traffic(Resource):

    def get(self, bbox):
        """
        Get traffic data for specified bounding box
        :param bounds:
        :return:
        """
        bbox_list = [float(x) for x in bbox.split(",")]

        return data.to_json()


api.add_resource(Traffic, "/traffic?<string:bbox>")

if __name__ == "__main__":
    app.run(debug=True)
