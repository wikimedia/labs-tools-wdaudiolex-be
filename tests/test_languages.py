import unittest

from service.utils.languages import (
    LanguageNotResolved,
    codes_from_tag,
    language_record,
    list_languages,
    reset_language_cache,
    resolve_language,
    set_language_index_for_tests,
)


class TestLanguageResolver(unittest.TestCase):
    def setUp(self):
        reset_language_cache()
        igbo = language_record("ig", "ibo", "Q33578", "Igbo")
        english = language_record("en", "eng", "Q1860", "English")
        set_language_index_for_tests("en", {
            "list": [igbo, english],
            "by_key": {
                "ig": igbo,
                "ibo": igbo,
                "q33578": igbo,
                "en": english,
                "eng": english,
                "q1860": english,
            },
        })

    def tearDown(self):
        reset_language_cache()

    def test_codes_from_tag(self):
        self.assertEqual(codes_from_tag("ig"), ("ig", "ibo"))
        self.assertEqual(codes_from_tag("ibo"), ("ig", "ibo"))
        self.assertEqual(codes_from_tag("en"), ("en", "eng"))

    def test_resolve_iso_iso3_and_qid(self):
        for code in ("ig", "ibo", "Q33578", "q33578"):
            resolved = resolve_language(code, "en")
            self.assertEqual(resolved["iso"], "ig")
            self.assertEqual(resolved["iso3"], "ibo")
            self.assertEqual(resolved["qid"], "Q33578")
            self.assertEqual(
                resolved["commons_category"],
                "Lingua Libre pronunciation-ibo",
            )

    def test_list_languages(self):
        languages = list_languages("en")
        self.assertEqual(len(languages), 2)
        self.assertEqual(languages[0]["iso3"], "ibo")

    def test_empty_code(self):
        with self.assertRaises(LanguageNotResolved):
            resolve_language("  ", "en")


if __name__ == "__main__":
    unittest.main()
