from functools import wraps

import jwt
from flask import abort, request
from jwt import ExpiredSignatureError, InvalidTokenError

from common import consumer_secret
from service.models import UserModel


def _read_token():
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ", 1)[1]
    return request.headers.get("x-access-tokens")


def _user_from_token(token):
    secret = consumer_secret or "dev-secret-change-me"
    data = jwt.decode(token, secret, algorithms=["HS256"])
    return UserModel.query.filter_by(temp_token=data.get("token")).first()


def token_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
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
            current_user = _user_from_token(token)
        except ExpiredSignatureError:
            abort(401, description="Token has expired.")
        except InvalidTokenError:
            abort(401, description="Invalid token.")
        except Exception as error:
            abort(401, description=f"Error decoding token: {error}")

        if not current_user:
            abort(401, description="User not found or token invalid.")
        return func(current_user, *args, **kwargs)

    return inner


def optional_token(func):
    @wraps(func)
    def inner(*args, **kwargs):
        token = _read_token()
        current_user = None
        if token:
            try:
                current_user = _user_from_token(token)
            except (ExpiredSignatureError, InvalidTokenError, Exception):
                current_user = None
        return func(current_user, *args, **kwargs)

    return inner
