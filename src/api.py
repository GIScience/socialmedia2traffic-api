#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""__description__
"""

__author__ = "Christina Ludwig, GIScience Research Group, Heidelberg University"
__email__ = "christina.ludwig@uni-heidelberg.de"

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


@api.representation('text/csv')
def output_csv(data, code, headers=None):
    resp = make_response(data.to_csv(), code)
    resp.headers.extend(headers or {})
    return resp


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

        bbox = args["bbox"]
        bbox_list = [float(x) for x in bbox.split(",")]
        response_stream = BytesIO(data.to_csv(index=False).encode())
        return send_file(
            response_stream,
            mimetype="text/csv",
            download_name=f"traffic_{bbox_list[0]}.csv",
        )


api.add_resource(Traffic, "/traffic")

if __name__ == "__main__":
    app.run(debug=True)
