import unittest

from service.utils.text import sanitize_word


class TestSanitizeWord(unittest.TestCase):
    def test_case_normalization(self):
        self.assertEqual(sanitize_word("Hello"), "hello")

    def test_punctuation_removal(self):
        self.assertEqual(sanitize_word("hello·world"), "helloworld")
        self.assertEqual(sanitize_word("hello.world"), "helloworld")

    def test_whitespace(self):
        self.assertEqual(sanitize_word("  hello  "), "hello")

    def test_none(self):
        self.assertEqual(sanitize_word(None), "")


if __name__ == "__main__":
    unittest.main()
