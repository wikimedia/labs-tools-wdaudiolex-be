import unittest

from app import app


class TestHealth(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_root_redirects_to_prefix(self):
        response = self.client.get("/", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith("/api"))

    def test_health_ok(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["service"], "wdaudiolex-be")
        self.assertIn("version", payload)


if __name__ == "__main__":
    unittest.main()
