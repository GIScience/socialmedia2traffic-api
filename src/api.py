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

    def get(self, bbox):
        """
        Get traffic data for specified bounding box
        :param bounds:
        :return:
        """
        bbox_list = [float(x) for x in bbox.split(",")]
        response_stream = BytesIO(data.to_csv(index=False).encode())
        return send_file(
            response_stream,
            mimetype="text/csv",
            download_name="traffic_bbox.csv",
        )


api.add_resource(Traffic, "/traffic/<string:bbox>")

if __name__ == "__main__":
    app.run(debug=True)
