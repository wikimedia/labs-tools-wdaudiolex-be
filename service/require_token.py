from flask import abort, g, request
from functools import wraps

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from common import jwt_secret
from service.models import UserModel


def _read_token():
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ", 1)[1]
    body = request.get_json(silent=True) or {}
    if body.get("token"):
        return body["token"]
    return request.headers.get("x-access-tokens")


def _authenticate():
    token = _read_token()
    if token is None:
        abort(
            401,
            description=(
                "Token is required. Provide an Authorization Bearer "
                "token or x-access-tokens header."
            ),
        )
    try:
        payload = jwt.decode(token, jwt_secret(), algorithms=["HS256"])
    except ExpiredSignatureError:
        abort(401, description="Token has expired.")
    except InvalidTokenError:
        abort(401, description="Invalid token.")
    except Exception as error:
        abort(401, description=f"Error decoding token: {error}")

    current_user = UserModel.query.filter_by(
        temp_token=payload.get("token")
    ).first()
    if not current_user:
        abort(401, description="User not found or token invalid.")
    g.jwt_payload = payload
    g.current_user = current_user
    return current_user, payload


def _call_resource(func, current_user, args, kwargs):
    if args:
        return func(args[0], current_user, *args[1:], **kwargs)
    return func(current_user, **kwargs)


def token_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        current_user, _payload = _authenticate()
        return _call_resource(func, current_user, args, kwargs)

    return inner


def optional_token(func):
    @wraps(func)
    def inner(*args, **kwargs):
        token = _read_token()
        current_user = None
        g.jwt_payload = None
        if token:
            try:
                payload = jwt.decode(
                    token, jwt_secret(), algorithms=["HS256"]
                )
                current_user = UserModel.query.filter_by(
                    temp_token=payload.get("token")
                ).first()
                g.jwt_payload = payload
            except (ExpiredSignatureError, InvalidTokenError, Exception):
                current_user = None
        g.current_user = current_user
        return _call_resource(func, current_user, args, kwargs)

    return inner
