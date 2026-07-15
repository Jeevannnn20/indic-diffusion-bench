from pathlib import Path
import unittest

from src.data import DatasetValidationError, load_jsonl, validate_records


ROOT = Path(__file__).resolve().parents[1]


class DatasetTests(unittest.TestCase):
    def test_pilot_contract(self) -> None:
        records = load_jsonl(ROOT / "data" / "pilot.jsonl")
        summary = validate_records(records)
        self.assertEqual(summary["items"], 10)
        self.assertEqual(summary["total_prompts"], 40)
        self.assertEqual(set(summary["categories"].values()), {2})
        self.assertEqual(summary["review_statuses"], {"reviewed": 10})

    def test_duplicate_ids_are_rejected(self) -> None:
        record = load_jsonl(ROOT / "data" / "pilot.jsonl")[0]
        with self.assertRaises(DatasetValidationError):
            validate_records([record, record])


if __name__ == "__main__":
    unittest.main()
