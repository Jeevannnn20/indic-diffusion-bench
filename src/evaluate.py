from __future__ import annotations

import argparse
import json
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

from .data import VARIANTS, load_jsonl, validate_records
from .models import MockModel, OllamaModel, ReplayModel
from .scoring import score_response


ANSWER_INSTRUCTIONS = {
    "hindi_devanagari": "आपका पूरा उत्तर केवल अंतिम उत्तर होना चाहिए। कोई व्याख्या, लेबल या मार्कडाउन नहीं। अधिकतम पाँच शब्द।",
    "roman_hindi": "Aapka poora response sirf final answer hona chahiye. Koi explanation, label ya markdown nahin. Adhiktam paanch shabd.",
    "hinglish": "Your complete response must contain only the final answer. No explanation, label or markdown. Maximum five words.",
    "english": "Your complete response must contain only the final answer. No explanation, label or markdown. Maximum five words.",
}

PROMPT_VERSION = "answer-only-v1"


def with_answer_instruction(
    messages: list[dict[str, str]], variant: str
) -> list[dict[str, str]]:
    copied = [dict(message) for message in messages]
    copied.insert(0, {"role": "system", "content": ANSWER_INSTRUCTIONS[variant]})
    copied[-1]["content"] = (
        f"{copied[-1]['content']}\n\n{ANSWER_INSTRUCTIONS[variant]}"
    )
    return copied


def evaluate_records(
    records: Iterable[dict[str, Any]], model: Any, variants: Iterable[str] = VARIANTS
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for record in records:
        for variant in variants:
            messages = with_answer_instruction(record["variants"][variant], variant)
            started = time.perf_counter()
            response = model.generate(
                messages, item_id=record["id"], variant=variant
            )
            latency_seconds = time.perf_counter() - started
            scores = score_response(response, record["accepted_answers"][variant])
            output.append(
                {
                    "id": record["id"],
                    "category": record["category"],
                    "variant": variant,
                    "model": model.name,
                    "prompt_version": PROMPT_VERSION,
                    "response": response,
                    "canonical_answer": record["canonical_answer"],
                    "latency_seconds": round(latency_seconds, 4),
                    **scores,
                }
            )
    return output


def _accuracy(rows: Iterable[dict[str, Any]], field: str = "exact_correct") -> float:
    rows = list(rows)
    return sum(bool(row[field]) for row in rows) / len(rows) if rows else 0.0


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_variant: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_category: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_variant[row["variant"]].append(row)
        by_category[row["category"]].append(row)

    variant_accuracy = {
        variant: round(_accuracy(group), 4)
        for variant, group in sorted(by_variant.items())
    }
    english_accuracy = variant_accuracy.get("english", 0.0)
    language_gaps = {
        variant: round(english_accuracy - accuracy, 4)
        for variant, accuracy in variant_accuracy.items()
        if variant != "english"
    }
    return {
        "model": rows[0]["model"] if rows else None,
        "evaluations": len(rows),
        "overall_exact_accuracy": round(_accuracy(rows), 4),
        "overall_answer_mention_rate": round(_accuracy(rows, "answer_mentioned"), 4),
        "mean_latency_seconds": round(
            sum(row["latency_seconds"] for row in rows) / len(rows), 4
        ) if rows else 0.0,
        "total_latency_seconds": round(
            sum(row["latency_seconds"] for row in rows), 4
        ),
        "exact_accuracy_by_variant": variant_accuracy,
        "english_minus_variant_gap": language_gaps,
        "exact_accuracy_by_category": {
            category: round(_accuracy(group), 4)
            for category, group in sorted(by_category.items())
        },
        "warning": "Pilot results are for pipeline validation and are not research findings.",
    }


def build_model(args: argparse.Namespace) -> Any:
    if args.provider == "mock":
        return MockModel()
    if args.provider == "ollama":
        return OllamaModel(args.model, args.base_url)
    if args.provider == "replay":
        if not args.replay_file:
            raise ValueError("--replay-file is required for the replay provider")
        return ReplayModel(args.replay_file)
    raise ValueError(f"Unsupported provider: {args.provider}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--provider", choices=("mock", "ollama", "replay"), default="mock")
    parser.add_argument("--model", default="")
    parser.add_argument("--base-url", default="http://localhost:11434")
    parser.add_argument("--replay-file")
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--variants",
        nargs="+",
        choices=VARIANTS,
        default=list(VARIANTS),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    records = load_jsonl(args.dataset)
    validate_records(records)
    rows = evaluate_records(records, build_model(args), args.variants)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    summary = summarize(rows)
    summary_path = output_path.with_suffix(".summary.json")
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Saved item-level results to {output_path}")
    print(f"Saved summary to {summary_path}")


if __name__ == "__main__":
    main()
