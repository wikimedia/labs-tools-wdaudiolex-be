import unittest

from service.utils.ll_filename import file_title, parse_ll_filename


class TestParseLlFilename(unittest.TestCase):
    def test_standard_file(self):
        parsed = parse_ll_filename("LL-Q33578 (ibo)-Ada-ulo.wav")
        self.assertEqual(parsed["title"], "File:LL-Q33578 (ibo)-Ada-ulo.wav")
        self.assertEqual(parsed["lang_qid"], "Q33578")
        self.assertEqual(parsed["iso3"], "ibo")
        self.assertEqual(parsed["speaker"], "Ada")
        self.assertEqual(parsed["word"], "ulo")
        self.assertEqual(parsed["normalized_word"], "ulo")
        self.assertEqual(parsed["extension"], "wav")

    def test_speaker_with_space(self):
        parsed = parse_ll_filename(
            "File:LL-Q1860 (eng)-Back ache-sun.wav"
        )
        self.assertEqual(parsed["speaker"], "Back ache")
        self.assertEqual(parsed["word"], "sun")
        self.assertEqual(parsed["lang_qid"], "Q1860")

    def test_word_with_space(self):
        parsed = parse_ll_filename(
            "LL-Q9288 (heb)-Ijon-שולמית הראבן.wav"
        )
        self.assertEqual(parsed["speaker"], "Ijon")
        self.assertEqual(parsed["word"], "שולמית הראבן")

    def test_invalid_name(self):
        parsed = parse_ll_filename("not-a-ll-file.ogg")
        self.assertIsNone(parsed["word"])
        self.assertEqual(parsed["title"], "File:not-a-ll-file.ogg")

    def test_file_title(self):
        self.assertEqual(file_title("sun.wav"), "File:sun.wav")
        self.assertEqual(file_title("File:sun.wav"), "File:sun.wav")


if __name__ == "__main__":
    unittest.main()
