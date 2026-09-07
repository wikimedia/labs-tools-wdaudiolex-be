from uuid import uuid4

from common import consumer_key, consumer_secret


def generate_random_token():
    return str(uuid4())


def get_auth_object(payload):
    access = payload.get("access_token") or {}
    if not access.get("key") or not access.get("secret"):
        return None
    return {
        "consumer_key": consumer_key,
        "consumer_secret": consumer_secret,
        "access_token": access["key"],
        "access_secret": access["secret"],
    }
