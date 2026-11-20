#!/usr/bin/env python3
"""Estimate precision uncertainty by resampling repository clusters."""

from __future__ import annotations

import argparse
import csv
import json
import random
from collections import defaultdict
from pathlib import Path


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("labels", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cluster-field", default="project")
    parser.add_argument("--label-field", default="adjudicated_label")
    parser.add_argument("--iterations", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=404)
    args = parser.parse_args(argv)
    clusters = defaultdict(list)
    with args.labels.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            label = row.get(args.label_field, "").strip().lower()
            label = {"tp": "true-positive", "fp": "false-positive"}.get(
                label, label
            )
            if label in {"true-positive", "false-positive"}:
                clusters[row.get(args.cluster_field, "")].append(label)
    names = sorted(name for name in clusters if name)
    if not names:
        parser.error("no decided labels with non-empty repository clusters")
    rng = random.Random(args.seed)
    estimates = []
    for _ in range(args.iterations):
        sampled = [rng.choice(names) for _ in names]
        labels = [label for name in sampled for label in clusters[name]]
        estimates.append(labels.count("true-positive") / len(labels))
    estimates.sort()
    lower = estimates[int(0.025 * (len(estimates) - 1))]
    upper = estimates[int(0.975 * (len(estimates) - 1))]
    observed = [label for name in names for label in clusters[name]]
    payload = {
        "schema_version": 1,
        "method": "repository-cluster-bootstrap",
        "clusters": len(names),
        "decided_occurrences": len(observed),
        "estimate": observed.count("true-positive") / len(observed),
        "confidence_interval_95": [lower, upper],
        "iterations": args.iterations,
        "seed": args.seed,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
