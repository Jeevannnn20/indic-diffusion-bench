from pathlib import Path
import unittest

from src.data import load_jsonl, validate_records
from src.evaluate import evaluate_records, summarize, with_answer_instruction
from src.models import MockModel


ROOT = Path(__file__).resolve().parents[1]


class EvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.records = load_jsonl(ROOT / "data" / "pilot.jsonl")
        validate_records(cls.records)

    def test_mock_evaluates_every_variant(self) -> None:
        rows = evaluate_records(self.records, MockModel())
        self.assertEqual(len(rows), 40)
        summary = summarize(rows)
        self.assertEqual(summary["evaluations"], 40)
        self.assertIn("english", summary["exact_accuracy_by_variant"])

    def test_instruction_does_not_mutate_dataset(self) -> None:
        messages = [{"role": "user", "content": "Question?"}]
        prompted = with_answer_instruction(messages, "english")
        self.assertEqual(messages[0]["content"], "Question?")
        self.assertEqual(prompted[0]["role"], "system")
        self.assertIn("final answer", prompted[-1]["content"])


if __name__ == "__main__":
    unittest.main()
