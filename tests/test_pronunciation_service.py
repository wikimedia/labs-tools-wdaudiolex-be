
import unittest
from app.services import pronunciation_service

class TestPronunciationService(unittest.TestCase):
    def test_add_pronunciation(self):
        result = pronunciation_service.add_pronunciation(1, 'http://example.com/audio.mp3')
        self.assertEqual(result['message'], 'Pronunciation added successfully.')

if __name__ == '__main__':
    unittest.main()

