from collections import namedtuple
from datetime import datetime, timedelta, timezone

import jwt

from common import jwt_secret
from service import app, db
from service.models import UserModel

AccessToken = namedtuple("AccessToken", "key secret")


def make_user(username="Ada", pref_langs="en", temp_token="temp-ada"):
    user = UserModel(
        username=username,
        pref_langs=pref_langs,
        temp_token=temp_token,
    )
    db.session.add(user)
    db.session.commit()
    return user


def make_jwt(user, access_key="user-key", access_secret="user-secret"):
    payload = {
        "token": user.temp_token,
        "access_token": {"key": access_key, "secret": access_secret},
        "exp": datetime.now(timezone.utc) + timedelta(minutes=45),
    }
    return jwt.encode(payload, jwt_secret(), algorithm="HS256")


class DbTestCase:
    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
