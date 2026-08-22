import unittest
from unittest.mock import patch

from app import app
from service.utils.languages import language_record


class TestLanguageRoutes(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.igbo = language_record("ig", "ibo", "Q33578", "Igbo")

    @patch("service.resources.languages.languages.list_languages")
    def test_list_languages(self, mock_list):
        mock_list.return_value = [self.igbo]
        response = self.client.get("/api/languages?ui_lang=en")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload[0]["iso3"], "ibo")
        self.assertEqual(
            payload[0]["commons_category"],
            "Lingua Libre pronunciation-ibo",
        )
        mock_list.assert_called_once_with("en")

    @patch("service.resources.languages.languages.resolve_language")
    def test_resolve_language(self, mock_resolve):
        mock_resolve.return_value = self.igbo
        response = self.client.get("/api/languages/ibo")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["qid"], "Q33578")

    @patch("service.resources.languages.languages.resolve_language")
    def test_unknown_language(self, mock_resolve):
        from service.utils.languages import LanguageNotResolved
        mock_resolve.side_effect = LanguageNotResolved("Unsupported")
        response = self.client.get("/api/languages/zzzx")
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
