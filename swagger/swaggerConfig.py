from flask import jsonify
from flask_restful import Resource

from common import load_swagger_config


class SwaggerConfig(Resource):
    def get(self):
        return jsonify(load_swagger_config())
