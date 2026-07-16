from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .evaluate import summarize


def load_results(path: str | Path) -> list[dict[str, Any]]:
    with Path(path).open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def compare(result_paths: list[str | Path]) -> dict[str, Any]:
    summaries = [summarize(load_results(path)) for path in result_paths]
    models: dict[str, Any] = {}
    for path, summary in zip(result_paths, summaries):
        models[summary["model"]] = {
            "source": str(path),
            "overall_exact_accuracy": summary["overall_exact_accuracy"],
            "mean_latency_seconds": summary["mean_latency_seconds"],
            "exact_accuracy_by_variant": summary["exact_accuracy_by_variant"],
            "exact_accuracy_by_category": summary["exact_accuracy_by_category"],
        }

    deltas: dict[str, Any] = {}
    if len(summaries) == 2:
        baseline, candidate = summaries
        deltas = {
            "candidate_minus_baseline": {
                "baseline": baseline["model"],
                "candidate": candidate["model"],
                "overall_exact_accuracy": round(
                    candidate["overall_exact_accuracy"]
                    - baseline["overall_exact_accuracy"],
                    4,
                ),
                "mean_latency_seconds": round(
                    candidate["mean_latency_seconds"]
                    - baseline["mean_latency_seconds"],
                    4,
                ),
                "exact_accuracy_by_variant": _mapping_delta(
                    baseline["exact_accuracy_by_variant"],
                    candidate["exact_accuracy_by_variant"],
                ),
                "exact_accuracy_by_category": _mapping_delta(
                    baseline["exact_accuracy_by_category"],
                    candidate["exact_accuracy_by_category"],
                ),
            }
        }
    return {"models": models, **deltas}


def _mapping_delta(baseline: dict[str, float], candidate: dict[str, float]) -> dict[str, float]:
    keys = sorted(set(baseline) | set(candidate))
    return {
        key: round(candidate.get(key, 0.0) - baseline.get(key, 0.0), 4)
        for key in keys
    }


def render_markdown(comparison: dict[str, Any]) -> str:
    lines = ["# Automated Model Comparison", ""]
    lines += [
        "| Model | Exact accuracy | Mean latency (s) |",
        "|---|---:|---:|",
    ]
    for model, values in comparison["models"].items():
        lines.append(
            f"| {model} | {values['overall_exact_accuracy']:.1%} | "
            f"{values['mean_latency_seconds']:.3f} |"
        )

    for dimension, heading in (
        ("exact_accuracy_by_variant", "Strict accuracy by language form"),
        ("exact_accuracy_by_category", "Strict accuracy by category"),
    ):
        lines += ["", f"## {heading}", ""]
        model_values = comparison["models"]
        labels = sorted(
            {label for values in model_values.values() for label in values[dimension]}
        )
        model_names = list(model_values)
        lines.append("| Group | " + " | ".join(model_names) + " |")
        lines.append("|---|" + "---:|" * len(model_names))
        for label in labels:
            scores = [model_values[name][dimension].get(label, 0.0) for name in model_names]
            lines.append("| " + label + " | " + " | ".join(f"{score:.1%}" for score in scores) + " |")

    lines += [
        "",
        "> Generated from raw run files. Pilot results are not research findings.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare benchmark result JSONL files")
    parser.add_argument("results", nargs="+", help="Result JSONL files in comparison order")
    parser.add_argument("--json-output")
    parser.add_argument("--markdown-output")
    args = parser.parse_args()

    comparison = compare(args.results)
    rendered_json = json.dumps(comparison, ensure_ascii=False, indent=2) + "\n"
    if args.json_output:
        Path(args.json_output).write_text(rendered_json, encoding="utf-8")
    if args.markdown_output:
        Path(args.markdown_output).write_text(render_markdown(comparison), encoding="utf-8")
    print(rendered_json, end="")


if __name__ == "__main__":
    main()
