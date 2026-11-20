#!/usr/bin/env python3
"""Score frozen threshold candidates against adjudicated manual labels."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import random

try:
    from scripts.build_threshold_benchmark import _prediction
except ModuleNotFoundError:
    from build_threshold_benchmark import _prediction


def _truth(value) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def _positive_prediction(row: dict, threshold: float) -> bool:
    return _prediction(row, threshold)


def _safe_div(numerator, denominator):
    return numerator / denominator if denominator else None


def _metrics(totals):
    precision = _safe_div(totals["tp"], totals["tp"] + totals["fp"])
    recall = _safe_div(totals["tp"], totals["tp"] + totals["fn"])
    f1 = _safe_div(2 * precision * recall, precision + recall) if precision is not None and recall is not None else None
    beta2 = 0.25
    f05 = _safe_div((1 + beta2) * precision * recall, beta2 * precision + recall) if precision is not None and recall is not None else None
    return {"precision": precision, "recall": recall, "f1": f1, "f0_5": f05}


def _percentile(values, probability):
    ordered = sorted(value for value in values if value is not None)
    if not ordered:
        return None
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def score(sample_rows, candidate_rows, bootstrap_iterations=0, seed=20260918):
    labeled = [
        row for row in sample_rows
        if row.get("adjudicated_label", "").strip().lower() in {"positive", "negative"}
    ]
    output = []
    for candidate in candidate_rows:
        metric_id = candidate["metric_id"]
        rows = [row for row in labeled if row["metric_id"] == metric_id]
        if not rows:
            continue
        threshold = float(candidate["threshold"])
        totals = {"tp": 0.0, "fp": 0.0, "tn": 0.0, "fn": 0.0}
        project_totals = {}
        for row in rows:
            weight = float(row.get("sampling_weight") or 1)
            predicted = _positive_prediction(row, threshold)
            actual = row["adjudicated_label"].strip().lower() == "positive"
            key = "tp" if predicted and actual else "fp" if predicted else "fn" if actual else "tn"
            totals[key] += weight
            bucket = project_totals.setdefault(
                row.get("project") or "__unknown__",
                {"tp": 0.0, "fp": 0.0, "tn": 0.0, "fn": 0.0},
            )
            bucket[key] += weight
        metrics = _metrics(totals)
        intervals = {}
        if bootstrap_iterations and project_totals:
            projects = sorted(project_totals)
            generator = random.Random(f"{seed}:{metric_id}:{candidate['threshold']}")
            draws = {name: [] for name in metrics}
            for _ in range(bootstrap_iterations):
                sampled = [generator.choice(projects) for _ in projects]
                replicate = {
                    key: sum(project_totals[project][key] for project in sampled)
                    for key in totals
                }
                for name, value in _metrics(replicate).items():
                    draws[name].append(value)
            for name, values in draws.items():
                intervals[f"{name}_ci_low"] = _percentile(values, 0.025)
                intervals[f"{name}_ci_high"] = _percentile(values, 0.975)
        output.append({
            "metric_id": metric_id,
            "candidate_sources": candidate["candidate_sources"],
            "threshold": candidate["threshold"],
            "labeled_rows": len(rows),
            **{key: round(value, 6) for key, value in totals.items()},
            **metrics,
            **intervals,
        })
    return output


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("sample")
    parser.add_argument("candidates")
    parser.add_argument("--output", required=True)
    parser.add_argument("--bootstrap-iterations", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=20260918)
    args = parser.parse_args(argv)
    with Path(args.sample).open(newline="", encoding="utf-8") as stream:
        sample = list(csv.DictReader(stream))
    with Path(args.candidates).open(newline="", encoding="utf-8") as stream:
        candidates = list(csv.DictReader(stream))
    results = score(
        sample, candidates,
        bootstrap_iterations=args.bootstrap_iterations,
        seed=args.seed,
    )
    output = Path(args.output)
    if output.suffix == ".json":
        output.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        fields = list(results[0]) if results else ["metric_id", "threshold"]
        with output.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
