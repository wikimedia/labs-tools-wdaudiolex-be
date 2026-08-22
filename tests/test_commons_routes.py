import unittest
from unittest.mock import patch

from app import app
from service.utils.languages import language_record


class TestCommonsRoutes(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.igbo = language_record("ig", "ibo", "Q33578", "Igbo")

    @patch("service.resources.commons.commons.list_lingua_libre_files")
    @patch("service.resources.commons.commons.resolve_language")
    def test_list_files(self, mock_resolve, mock_list):
        mock_resolve.return_value = self.igbo
        mock_list.return_value = {
            "files": [{
                "title": "File:LL-Q33578 (ibo)-Ada-ulo.wav",
                "url": "https://example.org/ulo.wav",
                "iso3": "ibo",
                "lang_qid": "Q33578",
                "speaker": "Ada",
                "word": "ulo",
                "transcription": "ulo",
            }],
            "continue": None,
        }
        response = self.client.get("/api/commons/files?lang=ibo&limit=20")
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["language"]["iso3"], "ibo")
        self.assertEqual(payload["files"][0]["word"], "ulo")
        mock_list.assert_called_once()

    @patch("service.resources.commons.commons.list_lingua_libre_files")
    @patch("service.resources.commons.commons.resolve_language")
    def test_speaker_filter(self, mock_resolve, mock_list):
        mock_resolve.return_value = self.igbo
        mock_list.return_value = {
            "files": [
                {"speaker": "Ada", "word": "ulo"},
                {"speaker": "Chidi", "word": "aka"},
            ],
            "continue": None,
        }
        response = self.client.get(
            "/api/commons/files?lang=ibo&speaker=ada"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()["files"]), 1)
        self.assertEqual(response.get_json()["files"][0]["word"], "ulo")

    def test_missing_lang(self):
        response = self.client.get("/api/commons/files")
        self.assertEqual(response.status_code, 400)

    @patch("service.resources.commons.commons.get_file_url")
    def test_file_url_route(self, mock_url):
        mock_url.return_value = {
            "title": "File:ulo.wav",
            "url": "https://example.org/ulo.wav",
        }
        response = self.client.get("/api/file/url/ulo.wav")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json()["url"],
            "https://example.org/ulo.wav",
        )


if __name__ == "__main__":
    unittest.main()
