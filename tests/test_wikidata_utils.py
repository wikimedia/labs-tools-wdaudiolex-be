import unittest
from unittest.mock import patch

from service.resources.wikidata.utils import get_lexemes, search_lexeme_ids


class TestWikidataUtils(unittest.TestCase):
    @patch("service.resources.wikidata.utils.make_api_request")
    def test_search_lexeme_ids(self, mock_request):
        mock_request.return_value = {
            "search": [{"id": "L123"}, {"id": "L456"}]
        }
        self.assertEqual(search_lexeme_ids("ulo", "ig"), ["L123", "L456"])

    @patch("service.resources.wikidata.utils.make_api_request")
    def test_search_error(self, mock_request):
        mock_request.return_value = {"error": "down", "status_code": 503}
        result = search_lexeme_ids("ulo", "ig")
        self.assertEqual(result["status_code"], 503)

    @patch("service.resources.wikidata.utils.make_api_request")
    def test_get_lexemes_skips_missing(self, mock_request):
        mock_request.return_value = {
            "entities": {
                "L123": {"id": "L123", "language": "Q33578"},
                "L999": {"id": "L999", "missing": ""},
            }
        }
        lexemes = get_lexemes(["L123", "L999"])
        self.assertEqual(len(lexemes), 1)
        self.assertEqual(lexemes[0]["id"], "L123")

    def test_get_lexemes_empty(self):
        self.assertEqual(get_lexemes([]), [])


if __name__ == "__main__":
    unittest.main()
