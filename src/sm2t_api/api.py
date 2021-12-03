#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""__description__
"""

__author__ = "Christina Ludwig, GIScience Research Group, Heidelberg University"
__email__ = "christina.ludwig@uni-heidelberg.de"

import datetime
import json

from flask import Flask, make_response
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
import pandas as pd
from io import BytesIO
from flask import send_file
from flask_restful import reqparse

# todo: https://flask-restful.readthedocs.io/en/latest/extending.html#response-formats

data_path = "/Users/chludwig/Development/spark/karlsruhe-regbez-75708-snappy"

app = Flask(__name__)
api = Api(app)

data = pd.DataFrame({"osmId": [1, 2],
                     "speed": [100, 80]})



def file_name(bbox):
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


class Traffic(Resource):

    def get(self):
        """
        Get traffic data for specified bounding box
        :param bounds:
        :return:
        """
        parser = reqparse.RequestParser()
        parser.add_argument('bbox', type=str, help='Bounding box', required=True)
        args = parser.parse_args()

        bbox, outfile = file_name(args["bbox"])

        response_stream = BytesIO(data.to_csv(index=False).encode())
        return send_file(
            response_stream,
            mimetype="text/csv",
            download_name=outfile,
        )


api.add_resource(Traffic, "/traffic")

if __name__ == "__main__":
    app.run(debug=True)
