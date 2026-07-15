from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


VARIANTS = ("hindi_devanagari", "roman_hindi", "hinglish", "english")
CATEGORIES = (
    "arithmetic_time",
    "family_relationship",
    "spatial_reasoning",
    "logical_constraints",
    "multi_turn_correction",
)
ROLES = {"system", "user", "assistant"}


class DatasetValidationError(ValueError):
    """Raised when one or more benchmark items violate the pilot contract."""


def load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise DatasetValidationError(
                    f"Invalid JSON on line {line_number}: {exc.msg}"
                ) from exc
    return records


def validate_records(records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    records = list(records)
    errors: list[str] = []
    ids: set[str] = set()
    categories: Counter[str] = Counter()

    if not records:
        errors.append("Dataset contains no records")

    required = {
        "id",
        "category",
        "difficulty",
        "original_language",
        "review_status",
        "variants",
        "accepted_answers",
        "canonical_answer",
        "split",
    }

    for index, record in enumerate(records, start=1):
        label = record.get("id", f"row_{index}")
        missing = required - record.keys()
        if missing:
            errors.append(f"{label}: missing fields {sorted(missing)}")
            continue

        if record["id"] in ids:
            errors.append(f"{label}: duplicate id")
        ids.add(record["id"])

        if record["category"] not in CATEGORIES:
            errors.append(f"{label}: unknown category {record['category']!r}")
        categories[record["category"]] += 1

        variants = record["variants"]
        answers = record["accepted_answers"]
        if set(variants) != set(VARIANTS):
            errors.append(f"{label}: variants must be exactly {list(VARIANTS)}")
        if set(answers) != set(VARIANTS):
            errors.append(f"{label}: accepted_answers must match all variants")

        for variant in VARIANTS:
            messages = variants.get(variant)
            if not isinstance(messages, list) or not messages:
                errors.append(f"{label}/{variant}: messages must be a non-empty list")
                continue
            for message_index, message in enumerate(messages, start=1):
                if not isinstance(message, dict):
                    errors.append(
                        f"{label}/{variant}/{message_index}: message must be an object"
                    )
                    continue
                if message.get("role") not in ROLES:
                    errors.append(
                        f"{label}/{variant}/{message_index}: invalid message role"
                    )
                if not isinstance(message.get("content"), str) or not message["content"].strip():
                    errors.append(
                        f"{label}/{variant}/{message_index}: empty message content"
                    )
            accepted = answers.get(variant)
            if not isinstance(accepted, list) or not accepted or not all(
                isinstance(answer, str) and answer.strip() for answer in accepted
            ):
                errors.append(f"{label}/{variant}: invalid accepted_answers")

    if errors:
        raise DatasetValidationError("\n".join(errors))

    return {
        "items": len(records),
        "variants_per_item": len(VARIANTS),
        "total_prompts": len(records) * len(VARIANTS),
        "categories": dict(sorted(categories.items())),
        "review_statuses": dict(
            sorted(Counter(record["review_status"] for record in records).items())
        ),
    }

