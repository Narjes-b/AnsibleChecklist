#!/usr/bin/env python3
"""Compare two independent threshold-benchmark reviewers."""

from __future__ import annotations

import argparse
from collections import Counter
import csv
import json
from pathlib import Path


VALID_LABELS = {"positive", "negative", "uncertain"}


def agreement(rows, first="reviewer_1_label", second="reviewer_2_label"):
    paired = [
        row for row in rows
        if row.get(first, "").strip().lower() in VALID_LABELS
        and row.get(second, "").strip().lower() in VALID_LABELS
    ]
    if not paired:
        return {
            "paired_items": 0, "raw_agreement": None, "cohens_kappa": None,
            "gwet_ac1": None, "label_prevalence": {},
            "label_specific_agreement": {}, "confusion_matrix": {},
            "agreements": 0, "disagreements": 0,
        }
    pairs = [
        (row[first].strip().lower(), row[second].strip().lower())
        for row in paired
    ]
    agreements = sum(a == b for a, b in pairs)
    observed = agreements / len(pairs)
    first_counts = Counter(a for a, _ in pairs)
    second_counts = Counter(b for _, b in pairs)
    expected = sum(
        (first_counts[label] / len(pairs)) * (second_counts[label] / len(pairs))
        for label in VALID_LABELS
    )
    kappa = None if expected == 1 else (observed - expected) / (1 - expected)
    categories = sorted(VALID_LABELS)
    mean_marginals = {
        label: (first_counts[label] + second_counts[label]) / (2 * len(pairs))
        for label in categories
    }
    ac1_expected = sum(
        probability * (1 - probability) for probability in mean_marginals.values()
    ) / (len(categories) - 1)
    gwet_ac1 = None if ac1_expected == 1 else (observed - ac1_expected) / (1 - ac1_expected)
    matrix = {
        first_label: {
            second_label: sum(a == first_label and b == second_label for a, b in pairs)
            for second_label in sorted(VALID_LABELS)
        }
        for first_label in sorted(VALID_LABELS)
    }
    return {
        "paired_items": len(pairs),
        "agreements": agreements,
        "disagreements": len(pairs) - agreements,
        "raw_agreement": observed,
        "cohens_kappa": kappa,
        "gwet_ac1": gwet_ac1,
        "label_prevalence": {
            label: {
                "reviewer_1": first_counts[label] / len(pairs),
                "reviewer_2": second_counts[label] / len(pairs),
            }
            for label in categories
        },
        "label_specific_agreement": {
            label: (
                2 * matrix[label][label]
                / (first_counts[label] + second_counts[label])
                if first_counts[label] + second_counts[label] else None
            )
            for label in categories
        },
        "confusion_matrix": matrix,
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("sample")
    parser.add_argument("--target", type=float, default=0.80)
    parser.add_argument("--minimum-paired", type=int, default=50)
    parser.add_argument("--first-column", default="reviewer_1_label")
    parser.add_argument("--second-column", default="reviewer_2_label")
    parser.add_argument("--output")
    parser.add_argument("--disagreements")
    args = parser.parse_args(argv)
    with Path(args.sample).open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    result = agreement(rows, args.first_column, args.second_column)
    result["first_column"] = args.first_column
    result["second_column"] = args.second_column
    kappa = result["cohens_kappa"]
    result["target"] = args.target
    result["minimum_paired"] = args.minimum_paired
    result["status"] = (
        "insufficient-independent-labels"
        if result["paired_items"] < args.minimum_paired
        else "agreement-target-reached"
        if kappa is not None and kappa >= args.target
        else "refine-codebook-and-run-new-pilot"
    )
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    if args.disagreements:
        fields = list(rows[0]) if rows else []
        with Path(args.disagreements).open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(
                row for row in rows
                if row.get(args.first_column, "").strip().lower() in VALID_LABELS
                and row.get(args.second_column, "").strip().lower() in VALID_LABELS
                and row[args.first_column].strip().lower() != row[args.second_column].strip().lower()
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
