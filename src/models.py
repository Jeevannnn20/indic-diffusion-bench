from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Protocol


class ModelAdapter(Protocol):
    name: str

    def generate(
        self, messages: list[dict[str, str]], *, item_id: str, variant: str
    ) -> str: ...


class MockModel:
    """A deliberately non-intelligent adapter for testing the evaluation pipeline."""

    name = "mock-unknown"

    def generate(
        self, messages: list[dict[str, str]], *, item_id: str, variant: str
    ) -> str:
        del messages, item_id
        return "अज्ञात" if variant == "hindi_devanagari" else "unknown"


class ReplayModel:
    def __init__(self, path: str | Path):
        self.name = f"replay:{Path(path).name}"
        self._responses: dict[tuple[str, str], str] = {}
        with Path(path).open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                row = json.loads(line)
                try:
                    key = (row["id"], row["variant"])
                    self._responses[key] = row["response"]
                except KeyError as exc:
                    raise ValueError(
                        f"Replay line {line_number} is missing {exc.args[0]!r}"
                    ) from exc

    def generate(
        self, messages: list[dict[str, str]], *, item_id: str, variant: str
    ) -> str:
        del messages
        try:
            return self._responses[(item_id, variant)]
        except KeyError as exc:
            raise KeyError(f"No replay response for {item_id}/{variant}") from exc


class OllamaModel:
    def __init__(self, model: str, base_url: str = "http://localhost:11434"):
        if not model:
            raise ValueError("--model is required for the Ollama provider")
        self.model = model
        self.name = f"ollama:{model}"
        self.endpoint = f"{base_url.rstrip('/')}/api/chat"

    def generate(
        self, messages: list[dict[str, str]], *, item_id: str, variant: str
    ) -> str:
        del item_id, variant
        payload = json.dumps(
            {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "think": False,
                "options": {"temperature": 0, "seed": 42, "num_predict": 64},
            },
            ensure_ascii=False,
        ).encode("utf-8")
        request = urllib.request.Request(
            self.endpoint,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                body: dict[str, Any] = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Could not reach Ollama at {self.endpoint}: {exc}") from exc
        try:
            return str(body["message"]["content"])
        except KeyError as exc:
            raise RuntimeError(f"Unexpected Ollama response: {body}") from exc
