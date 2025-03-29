import os
import requests
from flask import Flask
from requests_oauthlib import OAuth1
from .routes import main_bp  # Make sure the Blueprint is imported

def create_app():
    app = Flask(
        __name__,
        template_folder='templates'  # Changed from '../templates' to 'templates'
    )

    # Register the blueprint
    app.register_blueprint(main_bp)

    # Other app configurations can go here (e.g., database, sessions, etc.)
    return app


def generate_csrf_token(api_url, app_key, app_secret, user_key, user_secret):
    """
    Generate a CSRF token for the currently authenticated user using OAuth 1.0a.

    :param api_url: Base URL of the MediaWiki API (e.g., 'https://www.wikidata.org/w/api.php')
    :param app_key: The application's API key
    :param app_secret: The application's API secret
    :param user_key: The user's OAuth key
    :param user_secret: The user's OAuth secret
    :return: CSRF token as a string
    :raises Exception: If the token retrieval fails
    """
    # Set up OAuth1 authentication
    auth = OAuth1(app_key, app_secret, user_key, user_secret)

    # Define parameters to request a CSRF token
    params = {
        'action': 'query',
        'meta': 'tokens',
        'format': 'json'
    }

    # Make a GET request to the API to fetch the CSRF token
    response = requests.get(api_url, auth=auth, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        csrf_token = data.get('query', {}).get('tokens', {}).get('csrftoken')
        if csrf_token:
            return csrf_token
        else:
            raise Exception("CSRF token not found in the response.")
    else:
        raise Exception(f"Failed to fetch CSRF token: {response.status_code} - {response.text}")
