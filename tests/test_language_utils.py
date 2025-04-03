import unittest
from unittest.mock import patch, MagicMock
from app.utils.language_utils import get_supported_languages, get_language_label
from app.routes import get_languages, main_bp
from flask import Flask
import requests

class TestLanguageUtils(unittest.TestCase):
    def setUp(self):
        # Sample API response data
        self.mock_api_response = {
            "query": {
                "languageinfo": {
                    "en": {
                        "name": "English",
                        "autonym": "English"
                    },
                    "fr": {
                        "name": "French",
                        "autonym": "Français"
                    },
                    "de": {
                        "name": "German",
                        "autonym": "Deutsch"
                    }
                }
            }
        }

    @patch('requests.get')
    def test_get_supported_languages_success(self, mock_get):
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = self.mock_api_response
        mock_get.return_value = mock_response

        # Call the function
        result = get_supported_languages()

        # Assertions
        self.assertEqual(len(result), 3)
        self.assertEqual(result['en'], 'English')
        self.assertEqual(result['fr'], 'Français')
        self.assertEqual(result['de'], 'Deutsch')
        mock_get.assert_called_once()

    @patch('requests.get')
    def test_get_supported_languages_api_error(self, mock_get):
        # Mock API error
        mock_get.side_effect = requests.RequestException("API Error")

        # Call the function
        result = get_supported_languages()

        # Assertions
        self.assertEqual(result, {})

    def test_get_language_label(self):
        # Mock get_supported_languages to return test data
        with patch('app.utils.language_utils.get_supported_languages') as mock_get_languages:
            mock_get_languages.return_value = {
                'en': 'English',
                'fr': 'Français',
                'de': 'Deutsch'
            }

            # Test existing language code
            self.assertEqual(get_language_label('fr'), 'Français')
            
            # Test non-existing language code
            self.assertEqual(get_language_label('xx'), 'xx')

class TestLanguageAPI(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(main_bp)
        self.client = self.app.test_client()

    @patch('app.routes.get_supported_languages')
    def test_get_languages_endpoint(self, mock_get_languages):
        # Mock the language data
        mock_get_languages.return_value = {
            'en': 'English',
            'fr': 'Français',
            'de': 'Deutsch'
        }

        # Make request to the endpoint
        response = self.client.get('/api/languages')

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        data = response.get_json()
        self.assertEqual(len(data), 3)
        self.assertEqual(data['en'], 'English')
        self.assertEqual(data['fr'], 'Français')
        self.assertEqual(data['de'], 'Deutsch')

if __name__ == '__main__':
    unittest.main() 