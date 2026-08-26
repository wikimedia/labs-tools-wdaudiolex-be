import unittest
from unittest.mock import patch

from app import app
from service.utils.languages import language_record


class TestMatchLexemesRoute(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.igbo = language_record("ig", "ibo", "Q33578", "Igbo")
        self.lexeme = {
            "id": "L123",
            "language": "Q33578",
            "lemmas": {"ig": {"value": "ulo"}},
            "forms": [{
                "id": "L123-F1",
                "representations": {"ig": {"value": "ulo"}},
                "grammaticalFeatures": ["Q110786"],
                "claims": {},
            }],
        }

    @patch("service.resources.matching.matching.get_lexemes")
    @patch("service.resources.matching.matching.search_lexeme_ids")
    @patch("service.resources.matching.matching.resolve_language")
    def test_match_from_word(self, mock_resolve, mock_search, mock_get):
        mock_resolve.return_value = self.igbo
        mock_search.return_value = ["L123"]
        mock_get.return_value = [self.lexeme]

        response = self.client.post("/api/match-lexemes", json={
            "lang": "ibo",
            "files": [{"title": "File:LL-Q33578 (ibo)-Ada-ulo.wav", "word": "ulo"}],
        })
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["language"]["qid"], "Q33578")
        candidates = payload["results"][0]["candidates"]
        self.assertEqual(candidates[0]["form_id"], "L123-F1")
        self.assertEqual(candidates[0]["confidence"], "exact")
        self.assertFalse(candidates[0]["already_has_audio"])
        mock_search.assert_called_once_with("ulo", "ig")

    @patch("service.resources.matching.matching.get_lexemes")
    @patch("service.resources.matching.matching.search_lexeme_ids")
    @patch("service.resources.matching.matching.resolve_language")
    def test_word_from_filename(self, mock_resolve, mock_search, mock_get):
        mock_resolve.return_value = self.igbo
        mock_search.return_value = []
        mock_get.return_value = []
        response = self.client.post("/api/match-lexemes", json={
            "lang": "ibo",
            "files": [{"title": "LL-Q33578 (ibo)-Ada-ulo.wav"}],
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["results"][0]["word"], "ulo")
        mock_search.assert_called_once_with("ulo", "ig")

    @patch("service.resources.matching.matching.get_lexemes")
    @patch("service.resources.matching.matching.search_lexeme_ids")
    @patch("service.resources.matching.matching.resolve_language")
    def test_iso3_only_converts_to_639_1(
        self, mock_resolve, mock_search, mock_get
    ):
        mock_resolve.return_value = language_record(
            None, "ibo", "Q33578", "Igbo"
        )
        mock_search.return_value = []
        mock_get.return_value = []
        response = self.client.post("/api/match-lexemes", json={
            "lang": "ibo",
            "files": [{"word": "ulo"}],
        })
        self.assertEqual(response.status_code, 200)
        mock_search.assert_called_once_with("ulo", "ig")

    @patch("service.resources.matching.matching.get_lexemes")
    @patch("service.resources.matching.matching.search_lexeme_ids")
    @patch("service.resources.matching.matching.resolve_language")
    def test_drops_other_language_lexemes(
        self, mock_resolve, mock_search, mock_get
    ):
        mock_resolve.return_value = self.igbo
        mock_search.return_value = ["L1"]
        mock_get.return_value = [{
            "id": "L1",
            "language": "Q1860",
            "lemmas": {"en": {"value": "ulo"}},
            "forms": [{
                "id": "L1-F1",
                "representations": {"en": {"value": "ulo"}},
                "claims": {},
            }],
        }]
        response = self.client.post("/api/match-lexemes", json={
            "lang": "ibo",
            "files": [{"word": "ulo"}],
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["results"][0]["candidates"], [])

    def test_requires_lang_and_files(self):
        response = self.client.post("/api/match-lexemes", json={"lang": "ibo"})
        self.assertEqual(response.status_code, 400)

    def test_rejects_too_many_files(self):
        response = self.client.post("/api/match-lexemes", json={
            "lang": "ibo",
            "files": [{"word": "x"}] * 26,
        })
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
