from __future__ import annotations

import argparse
import json

from .data import load_jsonl, validate_records


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate an IndicDiffusionBench JSONL file")
    parser.add_argument("--dataset", required=True)
    args = parser.parse_args()
    summary = validate_records(load_jsonl(args.dataset))
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

