import requests
from requests_oauthlib import OAuth1

from common import app_version, tool_contact


def get_user_agent():
    """Return the User-Agent required by Wikimedia API policy."""
    return {
        "User-Agent": f"WDAudioLex/{app_version} ({tool_contact})"
    }


def make_api_request(url, params, headers=None):
    request_headers = get_user_agent()
    if headers:
        request_headers.update(headers)
    try:
        response = requests.get(url, params=params, headers=request_headers)
        response.raise_for_status()
        return response.json()
    except Exception as error:
        return {
            "error": str(error),
            "status_code": getattr(error, "response", None)
            and error.response.status_code or 503,
        }


def generate_csrf_token(url, app_key, app_secret, user_key, user_secret):
    auth = OAuth1(app_key, app_secret, user_key, user_secret)
    try:
        token_request = requests.get(
            url,
            params={
                "action": "query",
                "meta": "tokens",
                "format": "json",
            },
            auth=auth,
            headers=get_user_agent(),
        )
        token_request.raise_for_status()
        payload = token_request.json()
        if "error" in payload:
            return {
                "info": "Unable to get csrf token",
                "status_code": 503,
            }
        return payload["query"]["tokens"]["csrftoken"], auth
    except Exception as error:
        return {
            "info": f"Unable to get csrf token: {error}",
            "status_code": 503,
        }
