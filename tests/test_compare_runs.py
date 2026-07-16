import unittest

from src.compare_runs import compare, render_markdown


class ComparisonTests(unittest.TestCase):
    def test_two_run_delta_and_markdown(self) -> None:
        comparison = {
            "models": {
                "small": {
                    "overall_exact_accuracy": 0.25,
                    "mean_latency_seconds": 0.5,
                    "exact_accuracy_by_variant": {"english": 0.5},
                    "exact_accuracy_by_category": {"logic": 0.25},
                },
                "large": {
                    "overall_exact_accuracy": 0.5,
                    "mean_latency_seconds": 1.0,
                    "exact_accuracy_by_variant": {"english": 0.75},
                    "exact_accuracy_by_category": {"logic": 0.75},
                },
            }
        }
        markdown = render_markdown(comparison)
        self.assertIn("small", markdown)
        self.assertIn("50.0%", markdown)


if __name__ == "__main__":
    unittest.main()
