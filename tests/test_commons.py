import unittest
from unittest.mock import patch

from service.resources.commons.utils import get_file_url, list_lingua_libre_files


class TestCommonsUtils(unittest.TestCase):
    @patch("service.resources.commons.utils.fetch_transcriptions")
    @patch("service.resources.commons.utils.make_api_request")
    def test_list_files_parses_ll_names(self, mock_request, mock_transcribe):
        mock_transcribe.return_value = {"12": "ulo"}
        mock_request.return_value = {
            "query": {
                "pages": {
                    "12": {
                        "pageid": 12,
                        "title": "File:LL-Q33578 (ibo)-Ada-ulo.wav",
                        "imageinfo": [{"url": "https://example.org/ulo.wav"}],
                    }
                }
            },
            "continue": {"gcmcontinue": "next-token"},
        }
        result = list_lingua_libre_files("ibo", limit=20)
        self.assertEqual(result["continue"], "next-token")
        self.assertEqual(len(result["files"]), 1)
        item = result["files"][0]
        self.assertEqual(item["word"], "ulo")
        self.assertEqual(item["speaker"], "Ada")
        self.assertEqual(item["iso3"], "ibo")
        self.assertEqual(item["lang_qid"], "Q33578")
        self.assertEqual(item["transcription"], "ulo")
        self.assertEqual(item["url"], "https://example.org/ulo.wav")

    @patch("service.resources.commons.utils.make_api_request")
    def test_list_uses_transcription_when_name_is_odd(self, mock_request):
        mock_request.side_effect = [
            {
                "query": {
                    "pages": {
                        "9": {
                            "pageid": 9,
                            "title": "File:odd-name.wav",
                            "imageinfo": [{"url": "https://example.org/odd.wav"}],
                        }
                    }
                }
            },
            {
                "entities": {
                    "M9": {
                        "claims": {
                            "P9533": [{
                                "mainsnak": {
                                    "datavalue": {"value": {"text": "ulo"}}
                                }
                            }]
                        }
                    }
                }
            },
        ]
        result = list_lingua_libre_files("ibo")
        self.assertEqual(result["files"][0]["word"], "ulo")
        self.assertEqual(result["files"][0]["transcription"], "ulo")

    @patch("service.resources.commons.utils.make_api_request")
    def test_file_url(self, mock_request):
        mock_request.return_value = {
            "query": {
                "pages": {
                    "1": {
                        "title": "File:LL-Q33578 (ibo)-Ada-ulo.wav",
                        "imageinfo": [{"url": "https://example.org/ulo.wav"}],
                    }
                }
            }
        }
        result = get_file_url("LL-Q33578 (ibo)-Ada-ulo.wav")
        self.assertEqual(result["url"], "https://example.org/ulo.wav")
        args = mock_request.call_args[0][1]
        self.assertTrue(args["titles"].startswith("File:"))


if __name__ == "__main__":
    unittest.main()
