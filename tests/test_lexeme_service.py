
import unittest
from app.services import lexeme_service

class TestLexemeService(unittest.TestCase):
    def test_match_lexemes(self):
        result = lexeme_service.match_lexemes('example', 'category_1')
        self.assertTrue(len(result) > 0)

if __name__ == '__main__':
    unittest.main()

