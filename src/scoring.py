from __future__ import annotations

import re
import unicodedata
from typing import Iterable


def normalize_answer(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).casefold().strip()
    text = text.replace("–", "-").replace("—", "-")
    text = re.sub(r"[^\w\s:\-\u0900-\u097f]", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def score_response(response: str, accepted_answers: Iterable[str]) -> dict[str, bool]:
    normalized_response = normalize_answer(response)
    normalized_answers = [normalize_answer(answer) for answer in accepted_answers]
    exact = normalized_response in normalized_answers

    padded_response = f" {normalized_response} "
    mention = exact or any(
        answer and f" {answer} " in padded_response for answer in normalized_answers
    )
    return {"exact_correct": exact, "answer_mentioned": mention}

