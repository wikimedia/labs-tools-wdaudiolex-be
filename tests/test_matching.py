import unittest

from service.utils.matching import (
    best_confidence,
    candidates_from_lexeme,
    form_has_audio,
    score_text,
    sort_candidates,
)


class TestMatchingScores(unittest.TestCase):
    def test_exact_ignores_case_and_punctuation(self):
        self.assertEqual(score_text("Ulo!", "ulo"), "exact")

    def test_close_match(self):
        self.assertEqual(score_text("hello", "hallo"), "close")

    def test_unrelated(self):
        self.assertIsNone(score_text("ulo", "computer"))

    def test_best_confidence_prefers_exact(self):
        self.assertEqual(best_confidence("ulo", ["ula", "ulo"]), "exact")


class TestCandidatesFromLexeme(unittest.TestCase):
    def setUp(self):
        self.lexeme = {
            "id": "L123",
            "language": "Q33578",
            "lemmas": {"ig": {"language": "ig", "value": "ulo"}},
            "forms": [
                {
                    "id": "L123-F1",
                    "representations": {"ig": {"value": "ulo"}},
                    "grammaticalFeatures": ["Q110786"],
                    "claims": {},
                },
                {
                    "id": "L123-F2",
                    "representations": {"ig": {"value": "ulo"}},
                    "grammaticalFeatures": ["Q146233"],
                    "claims": {
                        "P443": [{"mainsnak": {"datavalue": {"value": "x.wav"}}}]
                    },
                },
            ],
        }

    def test_skips_other_languages(self):
        self.assertEqual(
            candidates_from_lexeme(self.lexeme, "ulo", "Q1860", "ig"),
            [],
        )

    def test_exact_forms_and_audio_flag(self):
        candidates = candidates_from_lexeme(
            self.lexeme, "ulo", "Q33578", "ig"
        )
        self.assertEqual(len(candidates), 2)
        self.assertEqual(candidates[0]["form_id"], "L123-F1")
        self.assertFalse(candidates[0]["already_has_audio"])
        self.assertEqual(candidates[0]["confidence"], "exact")
        self.assertEqual(candidates[1]["form_id"], "L123-F2")
        self.assertTrue(candidates[1]["already_has_audio"])
        self.assertEqual(candidates[0]["grammatical_features"], ["Q110786"])

    def test_lemma_fallback(self):
        lexeme = {
            "id": "L9",
            "language": "Q33578",
            "lemmas": {"ig": {"value": "ulo"}},
            "forms": [{
                "id": "L9-F1",
                "representations": {"ig": {"value": "ụlọaha"}},
                "grammaticalFeatures": [],
                "claims": {},
            }],
        }
        candidates = candidates_from_lexeme(lexeme, "ulo", "Q33578", "ig")
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["matched_on"], "lemma")
        self.assertEqual(candidates[0]["confidence"], "exact")

    def test_form_has_audio(self):
        self.assertFalse(form_has_audio({"claims": {}}))
        self.assertTrue(form_has_audio({"claims": {"P443": [{}]}}))

    def test_sort_puts_needs_audio_first(self):
        ordered = sort_candidates([
            {"form_id": "b", "confidence": "exact", "already_has_audio": True},
            {"form_id": "a", "confidence": "exact", "already_has_audio": False},
            {"form_id": "c", "confidence": "close", "already_has_audio": False},
        ])
        self.assertEqual([item["form_id"] for item in ordered], ["a", "b", "c"])


if __name__ == "__main__":
    unittest.main()
