#!/usr/bin/env python3
"""Create a source-first recall cohort from the validation inventory."""

from __future__ import annotations

import argparse
import csv
import random
from collections import defaultdict
from pathlib import Path


def build_recall_sample(rows: list[dict], seed: int = 42, total: int = 100, per_project_cap: int = 2) -> list[dict]:
    """Sample eligible production files without carrying finding columns forward."""
    pool = [
        row for row in rows
        if row.get("eligible_for_clean_review", "").lower() == "true"
        and row.get("primary_ansibleguard_cohort", "").lower() == "true"
    ]
    rng = random.Random(seed)
    rng.shuffle(pool)
    counts = defaultdict(int)
    capped = []
    for row in pool:
        project = row.get("project", "")
        if counts[project] >= per_project_cap:
            continue
        counts[project] += 1
        capped.append(row)
    probability = min(1.0, total / len(capped)) if capped else 0.0
    fields = (
        "project", "commit_sha", "path", "document_type", "loc",
        "ansible_artifact_kind", "project_size_quartile", "file_loc_quartile",
        "project_purpose_auto", "repository_family",
    )
    return [
        {
            **{field: row.get(field, "") for field in fields},
            "validation_unit": "source-first-recall",
            "sampling_seed": seed,
            "sampling_stratum": "eligible-production-source",
            "stratum_population": len(capped),
            "inclusion_probability": f"{probability:.12g}",
        }
        for row in capped[:total]
    ]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inventory", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--total", type=int, default=100)
    parser.add_argument("--per-project-cap", type=int, default=2)
    args = parser.parse_args(argv)
    with args.inventory.open(newline="", encoding="utf-8") as stream:
        sample = build_recall_sample(
            list(csv.DictReader(stream)), args.seed, args.total, args.per_project_cap
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(sample[0]) if sample else [])
        if sample:
            writer.writeheader()
            writer.writerows(sample)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
