import unittest

from app import app


class TestSwagger(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_swagger_config(self):
        response = self.client.get("/api/swagger-config")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["openapi"], "3.0.3")
        self.assertEqual(payload["info"]["title"], "WDAudioLex API")
        self.assertIn("/health", payload["paths"])
        self.assertTrue(payload["servers"][0]["url"].endswith("/api"))


if __name__ == "__main__":
    unittest.main()
