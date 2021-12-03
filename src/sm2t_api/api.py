#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""SM2T API"""

__author__ = "Christina Ludwig, GIScience Research Group, Heidelberg University"
__email__ = "christina.ludwig@uni-heidelberg.de"

from flask import Flask
from flask_restful import Api, Resource
import pandas as pd
from io import BytesIO
from flask import send_file
from flask_restful import reqparse
from sm2t_api import parse_bbox

app = Flask(__name__)
api = Api(app)

data = pd.DataFrame({"osmId": [1, 2],
                     "speed": [100, 80]})


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

        bbox, outfile = parse_bbox(args["bbox"])

        response_stream = BytesIO(data.to_csv(index=False).encode())
        return send_file(
            response_stream,
            mimetype="text/csv",
            download_name=outfile,
        )


api.add_resource(Traffic, "/traffic/csv")

if __name__ == "__main__":
    app.run(debug=True)
