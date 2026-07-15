import unittest

from src.scoring import normalize_answer, score_response


class ScoringTests(unittest.TestCase):
    def test_normalization(self) -> None:
        self.assertEqual(normalize_answer("  Thursday. "), "thursday")
        self.assertEqual(normalize_answer("उत्तर–पूर्व"), "उत्तर-पूर्व")

    def test_exact_and_mention_are_distinct(self) -> None:
        exact = score_response("Rohan", ["Rohan"])
        verbose = score_response("The answer is Rohan.", ["Rohan"])
        self.assertTrue(exact["exact_correct"])
        self.assertFalse(verbose["exact_correct"])
        self.assertTrue(verbose["answer_mentioned"])


if __name__ == "__main__":
    unittest.main()

