import os

from flask import Flask, jsonify
from flask_cors import CORS
from flask_restful import Api, MethodNotAllowed, NotFound
from flask_sqlalchemy import SQLAlchemy
from flask_swagger_ui import get_swaggerui_blueprint

from common import app_secret, database_uri, is_dev, prefix, swagger_server_url

app = Flask(__name__)

CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "*"}})

basedir = os.path.abspath(os.path.dirname(__file__))
default_sqlite = "sqlite:///" + os.path.join(basedir, "app.sqlite")
app.config["SQLALCHEMY_DATABASE_URI"] = database_uri or default_sqlite
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = app_secret

db = SQLAlchemy(app)
api = Api(app, prefix=prefix, catch_all_404s=True)

swaggerui_blueprint = get_swaggerui_blueprint(
    prefix,
    f"{swagger_server_url()}/swagger-config",
    config={
        "app_name": "WDAudioLex API",
        "layout": "BaseLayout",
        "docExpansion": "none",
    },
)
app.register_blueprint(swaggerui_blueprint, url_prefix=prefix)


@app.errorhandler(NotFound)
def handle_not_found(error):
    response = jsonify({"message": str(error)})
    response.status_code = 404
    return response


@app.errorhandler(MethodNotAllowed)
def handle_method_not_allowed(error):
    response = jsonify({"message": str(error)})
    response.status_code = 405
    return response


if is_dev:
    app.app_context().push()
