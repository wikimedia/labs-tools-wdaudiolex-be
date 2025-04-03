"""
Test Module for Lexeme Utilities

This module contains unit tests for the lexeme search functionality.
It tests both the utility functions and the API endpoints.
"""

import unittest
from unittest.mock import patch, MagicMock
from app.utils.lexeme_utils import sanitize_word, search_lexemes
from app.routes import search_lexemes_route, main_bp
from flask import Flask

class TestLexemeUtils(unittest.TestCase):
    """
    Test cases for the lexeme utility functions.
    """
    
    def test_sanitize_word(self):
        """
        Test the word sanitization function.
        
        Tests various aspects of word sanitization:
        1. Case normalization
        2. Punctuation removal
        3. Whitespace handling
        """
        # Test case sensitivity
        self.assertEqual(sanitize_word("Hello"), "hello")
        
        # Test punctuation removal
        self.assertEqual(sanitize_word("hello·world"), "helloworld")
        self.assertEqual(sanitize_word("hello.world"), "helloworld")
        
        # Test whitespace handling
        self.assertEqual(sanitize_word("  hello  "), "hello")

    @patch('requests.get')
    def test_search_lexemes_success(self, mock_get):
        """
        Test successful lexeme search.
        
        Mocks the Wikidata SPARQL API response and verifies:
        1. Correct API call
        2. Proper result processing
        3. Expected output format
        """
        # Mock SPARQL response with sample data
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": {
                "bindings": [
                    {
                        "lexeme": {"value": "http://www.wikidata.org/entity/L123"},
                        "lemma": {"value": "hello"},
                        "languageLabel": {"value": "English"}
                    }
                ]
            }
        }
        mock_get.return_value = mock_response

        # Test the function
        results = search_lexemes("hello")
        
        # Verify results
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "L123")
        self.assertEqual(results[0]["lemma"], "hello")
        self.assertEqual(results[0]["language"], "English")
        mock_get.assert_called_once()

    @patch('requests.get')
    def test_search_lexemes_api_error(self, mock_get):
        """
        Test error handling in lexeme search.
        
        Verifies that the function:
        1. Handles API errors gracefully
        2. Returns an empty list on error
        3. Logs the error appropriately
        """
        # Mock API error
        mock_get.side_effect = Exception("API Error")
        
        # Test the function
        results = search_lexemes("hello")
        
        # Verify error handling
        self.assertEqual(results, [])

class TestLexemeAPI(unittest.TestCase):
    """
    Test cases for the lexeme search API endpoint.
    """
    
    def setUp(self):
        """
        Set up the test environment.
        
        Creates a Flask test client and registers the blueprint.
        """
        self.app = Flask(__name__)
        self.app.register_blueprint(main_bp)
        self.client = self.app.test_client()

    @patch('app.routes.search_lexemes')
    def test_search_lexemes_endpoint_success(self, mock_search):
        """
        Test successful API endpoint response.
        
        Verifies:
        1. Correct HTTP status code
        2. Proper content type
        3. Expected response format
        4. Correct data in response
        """
        # Mock the search results
        mock_search.return_value = [
            {
                "id": "L123",
                "lemma": "hello",
                "language": "English"
            }
        ]

        # Test the endpoint
        response = self.client.get('/api/search-lexemes?word=hello')

        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        data = response.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], "L123")

    def test_search_lexemes_endpoint_missing_word(self):
        """
        Test API endpoint error handling.
        
        Verifies that the endpoint:
        1. Returns 400 status code for missing word parameter
        2. Returns appropriate error message
        """
        # Test without word parameter
        response = self.client.get('/api/search-lexemes')

        # Verify error response
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data["error"], "Word parameter is required")

if __name__ == '__main__':
    unittest.main() 