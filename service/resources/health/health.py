from flask_restful import Resource

from common import app_version


class HealthGet(Resource):
    def get(self):
        return {
            "status": "ok",
            "service": "wdaudiolex-be",
            "version": app_version,
        }, 200
