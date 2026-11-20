import json
import unittest
from collections import namedtuple
from unittest.mock import patch

from service.models import UserModel
from tests.helpers import DbTestCase, make_jwt, make_user

RequestToken = namedtuple("RequestToken", "key secret")
AccessToken = namedtuple("AccessToken", "key secret")


class TestAuthRoutes(DbTestCase, unittest.TestCase):
    @patch("service.resources.auth.auth.consumer_secret", "oauth-secret")
    @patch("service.resources.auth.auth.consumer_key", "oauth-key")
    @patch("service.resources.auth.auth.mwoauth.initiate")
    def test_login_returns_redirect(self, mock_initiate):
        mock_initiate.return_value = (
            "https://wikidata.org/wiki/Special:OAuth/authorize?oauth_token=abc",
            RequestToken("req-key", "req-secret"),
        )
        response = self.client.get("/api/auth/login")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn("wikidata.org", payload["redirect_string"])
        token = json.loads(payload["request_token"])
        self.assertEqual(token["key"], "req-key")

    @patch("service.resources.auth.auth.consumer_secret", "")
    @patch("service.resources.auth.auth.consumer_key", "")
    def test_login_without_consumer_is_unavailable(self):
        response = self.client.get("/api/auth/login")
        self.assertEqual(response.status_code, 503)

    @patch("service.resources.auth.auth.consumer_secret", "oauth-secret")
    @patch("service.resources.auth.auth.consumer_key", "oauth-key")
    @patch("service.resources.auth.auth.mwoauth.identify")
    @patch("service.resources.auth.auth.mwoauth.complete")
    def test_callback_creates_user(self, mock_complete, mock_identify):
        mock_complete.return_value = AccessToken("acc-key", "acc-secret")
        mock_identify.return_value = {"username": "Ada"}
        response = self.client.post("/api/oauth-callback", json={
            "request_token": json.dumps({"key": "req-key", "secret": "req-secret"}),
            "query_string": "oauth_token=abc&oauth_verifier=xyz",
        })
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["username"], "Ada")
        self.assertTrue(payload["token"])
        self.assertIsNotNone(UserModel.query.filter_by(username="Ada").first())

    @patch(
        "service.resources.auth.auth.frontend_origin",
        return_value="https://wdaudiolex.toolforge.org",
    )
    def test_get_callback_redirects_to_frontend(self, _origin):
        response = self.client.get(
            "/api/oauth-callback?oauth_verifier=xyz&oauth_token=abc",
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.headers["Location"],
            "https://wdaudiolex.toolforge.org/oauth-callback"
            "?oauth_verifier=xyz&oauth_token=abc",
        )
        self.assertEqual(response.headers["Cache-Control"], "no-store")

    @patch(
        "service.resources.auth.auth.frontend_origin",
        return_value="http://localhost:3000",
    )
    def test_get_callback_without_verifier_still_leaves_the_api(self, _origin):
        response = self.client.get("/api/oauth-callback")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.headers["Location"],
            "http://localhost:3000/oauth-callback",
        )

    @patch(
        "service.resources.auth.auth.frontend_origin",
        return_value="javascript:alert(1)",
    )
    def test_get_callback_rejects_a_bad_frontend_origin(self, _origin):
        response = self.client.get(
            "/api/oauth-callback?oauth_verifier=xyz&oauth_token=abc",
        )
        self.assertEqual(response.status_code, 503)

    @patch(
        "service.resources.auth.auth.frontend_origin",
        return_value="https://wdaudiolex.toolforge.org",
    )
    def test_callback_location_rejects_header_injection(self, _origin):
        from werkzeug.exceptions import BadRequest

        from service.resources.auth.auth import _frontend_callback_location

        with self.assertRaises(BadRequest):
            _frontend_callback_location(
                "oauth_token=abc\r\nLocation: https://evil.example"
            )

    def test_logout_invalidates_token(self):
        user = make_user()
        token = make_jwt(user)
        response = self.client.post(
            "/api/auth/logout",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        db_user = UserModel.query.filter_by(username="Ada").first()
        self.assertNotEqual(db_user.temp_token, "temp-ada")


if __name__ == "__main__":
    unittest.main()
