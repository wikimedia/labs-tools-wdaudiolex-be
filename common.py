import json
import os

import dotenv


def _as_bool(value, default=True):
    if value is None:
        return default
    return str(value).strip().lower() in ("1", "true", "yes", "on")


class ENVIRONMENT:
    def __init__(self):
        root = os.path.dirname(os.path.abspath(__file__))
        dotenv.load_dotenv(os.path.join(root, ".env"))

        self.port = os.getenv("PORT", "5000")
        self.prefix = os.getenv("PREFIX", "/api")
        self.domain = os.getenv("DOMAIN", "localhost")
        self.base_url = os.getenv(
            "BASE_URL", "https://www.wikidata.org/w/api.php")
        self.commons_url = os.getenv(
            "WM_COMMONS_URL", "https://commons.wikimedia.org/w/api.php")
        self.consumer_key = os.getenv("CONSUMER_KEY", "")
        self.consumer_secret = os.getenv("CONSUMER_SECRET", "")
        self.app_version = os.getenv("APP_VERSION", "0.1.0")
        self.app_secret = os.getenv("APP_SECRET", "dev-secret-change-me")
        self.is_dev = _as_bool(os.getenv("IS_DEV"), True)
        self.dev_fe_url = os.getenv("DEV_FE_URL", "http://localhost:3000")
        self.prod_fe_url = os.getenv("PROD_FE_URL", "")
        self.auth_base_url = os.getenv(
            "OAUTH_BASE_URL", "https://www.wikidata.org")
        self.commons_image_base_url = os.getenv(
            "WM_COMMONS_IMAGE_BASE_URL",
            "https://commons.wikimedia.org/wiki/Special:FilePath/")
        self.wm_commons_audio_base_url = os.getenv(
            "WM_COMMONS_AUDIO_BASE_URL",
            "https://upload.wikimedia.org/wikipedia/commons/")
        self.sparql_endpoint_url = os.getenv(
            "SPARQL_ENDPOINT_URL", "https://query.wikidata.org/sparql")
        self.database_uri = os.getenv("SQLALCHEMY_DATABASE_URI", "")
        self.tool_contact = os.getenv(
            "TOOL_CONTACT",
            "https://github.com/Wikidata-Cameroon/WdLexAudioBE")

    def get_instance(self):
        if not hasattr(self, "_instance"):
            self._instance = ENVIRONMENT()
        return self._instance


_env = ENVIRONMENT().get_instance()

domain = _env.domain
port = _env.port
prefix = _env.prefix
base_url = _env.base_url
commons_url = _env.commons_url
consumer_key = _env.consumer_key
consumer_secret = _env.consumer_secret
app_version = _env.app_version
app_secret = _env.app_secret
is_dev = _env.is_dev
dev_fe_url = _env.dev_fe_url
prod_fe_url = _env.prod_fe_url
auth_base_url = _env.auth_base_url
wm_commons_image_base_url = _env.commons_image_base_url
wm_commons_audio_base_url = _env.wm_commons_audio_base_url
sparql_endpoint_url = _env.sparql_endpoint_url
database_uri = _env.database_uri
tool_contact = _env.tool_contact


def swagger_server_url():
    if is_dev:
        return f"http://{domain}:{port}{prefix}"
    return f"https://{domain}{prefix}"


def load_swagger_config():
    config_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "swagger",
        "config.json",
    )
    with open(config_file_path, "r", encoding="utf-8") as handle:
        config_data = json.load(handle)
    config_data["servers"] = [{"url": swagger_server_url()}]
    return config_data
