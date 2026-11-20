#!/usr/bin/env python3
"""Summarize adjudicated false-positive mechanisms from a validation ledger."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


def _label(row: dict) -> str:
    return (
        row.get("consensus_label")
        or row.get("adjudicated_label")
        or row.get("reviewer_1_label")
        or ""
    ).strip().lower()


def _reason(row: dict) -> str:
    return (
        row.get("consensus_reason")
        or row.get("adjudicated_reason")
        or row.get("reviewer_1_reason")
        or "unspecified"
    ).strip() or "unspecified"


def summarize(rows: list[dict]) -> dict:
    mechanisms = Counter()
    by_concept = defaultdict(Counter)
    by_provider = defaultdict(Counter)
    reviewed = 0
    false_positives = 0
    for row in rows:
        label = _label(row)
        if not label:
            continue
        reviewed += 1
        if label != "false-positive":
            continue
        false_positives += 1
        reason = _reason(row)
        concept = row.get("concept_id") or "unknown"
        provider = row.get("provider") or "ansibleguard"
        mechanisms[reason] += 1
        by_concept[concept][reason] += 1
        by_provider[provider][reason] += 1
    return {
        "schema": "ansibleguard-fp-mechanisms-v1",
        "reviewed_labels": reviewed,
        "false_positives": false_positives,
        "mechanisms": dict(mechanisms.most_common()),
        "by_concept": {
            key: dict(counter.most_common()) for key, counter in sorted(by_concept.items())
        },
        "by_provider": {
            key: dict(counter.most_common()) for key, counter in sorted(by_provider.items())
        },
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("labels", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    with args.labels.open(newline="", encoding="utf-8") as stream:
        summary = summarize(list(csv.DictReader(stream)))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
