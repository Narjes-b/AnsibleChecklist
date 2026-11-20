#!/usr/bin/env python3
"""Validate a completed two-reviewer ledger and summarize agreement."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

try:
    from scripts.prepare_manual_validation import summarize_validation
except ModuleNotFoundError:
    from prepare_manual_validation import summarize_validation


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Validate and summarize an AnsibleGuard manual-validation ledger."
    )
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--output", "-o", type=Path, required=True)
    args = parser.parse_args(argv)
    with args.ledger.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    summary = summarize_validation(rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote validation summary to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
