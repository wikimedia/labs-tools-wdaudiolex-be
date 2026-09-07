import json
from datetime import datetime, timedelta, timezone

import jwt
import mwoauth
from flask import abort, jsonify, make_response, request
from flask_restful import Resource, fields, marshal_with, reqparse

from common import (
    JWT_EXPIRY_MINUTES,
    auth_base_url,
    consumer_key,
    consumer_secret,
    jwt_secret,
)
from service import db
from service.models import UserModel
from service.resources.auth.utils import generate_random_token

auth_fields = {
    "token": fields.String,
    "username": fields.String,
    "pref_langs": fields.String,
}
auth_login_fields = {
    "redirect_string": fields.String,
    "request_token": fields.String,
}

callback_args = reqparse.RequestParser()
callback_args.add_argument(
    "request_token", type=str, required=True,
    help="Request token is required",
)
callback_args.add_argument(
    "query_string", type=str, required=True,
    help="Query string is required",
)


def _encode_session(user, access_token):
    payload = {
        "token": user.temp_token,
        "access_token": dict(zip(access_token._fields, access_token)),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRY_MINUTES),
    }
    return jwt.encode(payload, jwt_secret(), algorithm="HS256")


class AuthGet(Resource):
    @marshal_with(auth_login_fields)
    def get(self):
        if not consumer_key or not consumer_secret:
            abort(503, "OAuth consumer key and secret are not configured")
        consumer_token = mwoauth.ConsumerToken(consumer_key, consumer_secret)
        try:
            redirect_string, request_token = mwoauth.initiate(
                auth_base_url, consumer_token
            )
            request_token_json = json.dumps(
                dict(zip(request_token._fields, request_token))
            )
        except Exception as error:
            abort(400, f"mwoauth.initiate failed: {error}")
        return {
            "redirect_string": redirect_string,
            "request_token": request_token_json,
        }, 200


class AuthCallBackPost(Resource):
    @marshal_with(auth_fields)
    def post(self):
        args = callback_args.parse_args()
        try:
            request_token = mwoauth.RequestToken(
                **json.loads(args["request_token"])
            )
        except (json.JSONDecodeError, KeyError, TypeError) as error:
            abort(400, f"Invalid request token format: {error}")

        consumer_token = mwoauth.ConsumerToken(consumer_key, consumer_secret)
        try:
            access_token = mwoauth.complete(
                auth_base_url,
                consumer_token,
                request_token,
                args["query_string"],
            )
            identity = mwoauth.identify(
                auth_base_url, consumer_token, access_token
            )
        except Exception as error:
            abort(400, f"OAuth callback failed: {error}")

        username = identity.get("username")
        if not username:
            abort(400, "OAuth identity did not include a username")

        user = UserModel.query.filter_by(username=username).first()
        if user:
            user.temp_token = generate_random_token()
            db.session.commit()
        else:
            user = UserModel(
                username=username,
                pref_langs="en",
                temp_token=generate_random_token(),
            )
            db.session.add(user)
            try:
                db.session.commit()
            except Exception as error:
                db.session.rollback()
                abort(400, f"Error creating user: {error}")

        return {
            "token": _encode_session(user, access_token),
            "username": user.username,
            "pref_langs": user.pref_langs,
        }, 200


class AuthLogout(Resource):
    def post(self):
        body = request.get_json(silent=True) or {}
        token = body.get("token")
        if not token:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ", 1)[1]
            else:
                token = request.headers.get("x-access-tokens")
        if not token:
            abort(400, "Token is required")
        try:
            payload = jwt.decode(token, jwt_secret(), algorithms=["HS256"])
            user = UserModel.query.filter_by(
                temp_token=payload.get("token")
            ).first()
            if user:
                user.temp_token = generate_random_token()
                db.session.commit()
            return make_response(
                jsonify({"message": "Logged out successfully"}), 200
            )
        except jwt.InvalidTokenError:
            return make_response(jsonify({"message": "Invalid token"}), 400)
        except Exception as error:
            return make_response(
                jsonify({"message": f"Logout error: {error}"}), 500
            )
