import unittest

from service.utils.languages import (
    LanguageNotResolved,
    codes_from_tag,
    from_iso3,
    language_labels,
    language_record,
    list_languages,
    reset_language_cache,
    resolve_language,
    set_language_index_for_tests,
    wikidata_lang_code,
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

    def test_from_iso3_for_wikidata(self):
        converted = from_iso3("ibo", "fr")
        self.assertEqual(converted["iso"], "ig")
        self.assertEqual(converted["iso3"], "ibo")
        self.assertEqual(converted["name"], "Igbo")
        self.assertTrue(converted["label"])

    def test_from_iso3_without_639_1(self):
        converted = from_iso3("dag")
        self.assertEqual(converted["iso3"], "dag")
        self.assertIsNone(converted["iso"])
        self.assertTrue(converted["name"])

    def test_language_labels(self):
        labels = language_labels("ibo", ["en", "fr"])
        self.assertIn("en", labels)
        self.assertIn("fr", labels)
        self.assertEqual(labels["en"], "Igbo")

    def test_wikidata_lang_code_prefers_639_1(self):
        self.assertEqual(
            wikidata_lang_code({"iso": "ig", "iso3": "ibo"}),
            "ig",
        )
        self.assertEqual(
            wikidata_lang_code({"iso": None, "iso3": "ibo"}),
            "ig",
        )
        self.assertEqual(
            wikidata_lang_code({"iso": None, "iso3": "dag"}),
            "dag",
        )

    def test_from_iso3_rejects_empty(self):
        with self.assertRaises(LanguageNotResolved):
            from_iso3("")
        with self.assertRaises(LanguageNotResolved):
            resolve_language("  ", "en")


if __name__ == "__main__":
    unittest.main()
