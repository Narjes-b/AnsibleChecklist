#!/usr/bin/env python3
"""Audit candidate rates for configurable experimental rule thresholds.

This is an engineering sensitivity audit, not a precision estimator: it does
not turn tool-selected v0.0.3 labels into an unbiased threshold optimum.
"""

from __future__ import annotations

import argparse
from contextlib import redirect_stdout
import csv
import io
import json
from pathlib import Path

from ansibleguard.detectors.detect_large_play import calculate_metrics_play
from ansibleguard.detectors.detect_large_playbook import calculate_metrics_playbook
from ansibleguard.detectors.high_coupling import high_coupling
from ansibleguard.detectors.large_task import calculate_metrics_task
from ansibleguard.detectors.paper_candidates import (
    _iter_tasks,
    _load,
    detect_missing_abstraction,
)


def _complexity_evidence(path):
    document, _ = _load(path)
    rows = []
    import re

    for task, depth in _iter_tasks(document):
        condition = task.get("when", "")
        if isinstance(condition, list):
            condition = " and ".join(str(item) for item in condition)
        condition = str(condition)
        rows.append(
            {
                "boolean_ops": len(re.findall(r"\b(?:and|or)\b", condition, re.I)),
                "jinja_filters": len(re.findall(r"\|\s*[A-Za-z_]\w*", condition)),
                "nesting_depth": depth,
            }
        )
    return rows


# (metric_key, current production threshold, values to test around it) for
# each family whose finding is "this metric exceeds threshold X" on a single
# task/play/playbook-level number already produced by an existing metric
# function -- reusing calculate_metrics_task/_play/_playbook rather than
# reimplementing them, following the same candidate-rate (not precision)
# pattern already established for high_coupling/undocumented_complex_task.
TASK_METRIC_THRESHOLDS = {
    "large_task": ("LOC_task", (10, 15, 20)),
    "long_task_name": ("task_name_len", (50, 75, 100)),
}
PLAY_METRIC_THRESHOLDS = {
    "large_play_loc": ("LOC_play", (35, 50, 65)),
    "large_play_task_count": ("num_tasks_in_play", (5, 7, 10)),
    "large_play_avg_task_size": ("avg_task_play", (10, 15, 20)),
}
PLAYBOOK_METRIC_THRESHOLDS = {
    "large_playbook_loc": ("LOC_playbook", (80, 110, 140)),
    "large_playbook_num_plays": ("num_plays", (3, 4, 6)),
    "large_playbook_avg_play_size": ("avg_play_size", (35, 50, 65)),
    "large_playbook_num_tasks": ("num_nested_tasks_playbook", (10, 15, 20)),
    "large_playbook_avg_task_size": ("avg_nested_task_playbook", (10, 15, 20)),
}
MISSING_ABSTRACTION_THRESHOLDS = (7, 10, 13)


def audit_paths(paths, coupling_thresholds=(4, 6, 8), complexity_thresholds=(3, 4, 5)):
    result = {
        "files": len(paths),
        "high_coupling": {str(value): 0 for value in coupling_thresholds},
        "undocumented_complex_task": {
            str(value): 0 for value in complexity_thresholds
        },
        "not_applicable_or_unreadable_files": 0,
    }
    families = {**TASK_METRIC_THRESHOLDS, **PLAY_METRIC_THRESHOLDS, **PLAYBOOK_METRIC_THRESHOLDS}
    for family, (_, values) in families.items():
        result[family] = {str(value): 0 for value in values}
    result["missing_abstraction"] = {str(value): 0 for value in MISSING_ABSTRACTION_THRESHOLDS}

    for path in paths:
        with redirect_stdout(io.StringIO()):
            coupling = high_coupling(path)
        if coupling is None:
            result["not_applicable_or_unreadable_files"] += 1
            continue
        for threshold in coupling_thresholds:
            if max(coupling.get("Num_Imports", 0), coupling.get("Num_Roles", 0)) > threshold:
                result["high_coupling"][str(threshold)] += 1
        evidence = _complexity_evidence(path)
        for threshold in complexity_thresholds:
            if any(
                row["boolean_ops"] >= threshold
                or row["jinja_filters"] >= threshold
                or row["nesting_depth"] > threshold + 1
                for row in evidence
            ):
                result["undocumented_complex_task"][str(threshold)] += 1

        with redirect_stdout(io.StringIO()):
            task_metrics, _ = calculate_metrics_task(path)
            play_metrics = calculate_metrics_play(path) or {"Plays": []}
            playbook_metrics = calculate_metrics_playbook(path) or {}
        for family, (metric_key, values) in TASK_METRIC_THRESHOLDS.items():
            for value in values:
                if any(row.get(metric_key, 0) > value for row in task_metrics):
                    result[family][str(value)] += 1
        for family, (metric_key, values) in PLAY_METRIC_THRESHOLDS.items():
            for value in values:
                if any(play.get(metric_key, 0) > value for play in play_metrics.get("Plays", [])):
                    result[family][str(value)] += 1
        for family, (metric_key, values) in PLAYBOOK_METRIC_THRESHOLDS.items():
            for value in values:
                if playbook_metrics.get(metric_key, 0) > value:
                    result[family][str(value)] += 1
        for threshold in MISSING_ABSTRACTION_THRESHOLDS:
            with redirect_stdout(io.StringIO()):
                count, _ = detect_missing_abstraction(path, threshold=threshold)
            if count:
                result["missing_abstraction"][str(threshold)] += 1

    all_families = (
        "high_coupling", "undocumented_complex_task", "missing_abstraction",
        *TASK_METRIC_THRESHOLDS, *PLAY_METRIC_THRESHOLDS, *PLAYBOOK_METRIC_THRESHOLDS,
    )
    for family in all_families:
        result[f"{family}_candidate_rates"] = {
            threshold: round(count / len(paths), 6) if paths else 0
            for threshold, count in result[family].items()
        }
    return result


def sample_paths(sample, repositories):
    paths = set()
    with Path(sample).open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            project = row.get("project", "")
            relative = row.get("path", "")
            if not project or not relative:
                continue
            candidate = Path(repositories) / project / relative
            if candidate.is_file():
                paths.add(candidate.resolve())
    return sorted(paths)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", required=True)
    parser.add_argument("--repositories", required=True)
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    paths = sample_paths(args.sample, args.repositories)
    result = audit_paths(paths)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
