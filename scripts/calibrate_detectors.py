#!/usr/bin/env python3
"""Run and score a versioned labeled AnsibleGuard calibration corpus."""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import hashlib
import json
from pathlib import Path

from ansibleguard.cli import analyze_path


LABEL_FIELDS = ("case_id", "file", "rule_id", "expected", "rationale")


def load_labels(path):
    with Path(path).open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    if not rows or tuple(rows[0]) != LABEL_FIELDS:
        raise ValueError(f"labels must have columns: {', '.join(LABEL_FIELDS)}")
    seen = set()
    for row in rows:
        key = (row["file"], row["rule_id"])
        if not row["case_id"] or not row["file"] or not row["rule_id"]:
            raise ValueError("case_id, file, and rule_id are required")
        if row["expected"] not in {"present", "absent"}:
            raise ValueError("expected must be present or absent")
        if key in seen:
            raise ValueError(f"duplicate label for {key[0]} / {key[1]}")
        seen.add(key)
    return rows


def _ratio(numerator, denominator):
    return round(numerator / denominator, 4) if denominator else None


def _f1(precision, recall):
    """Harmonic mean of precision and recall.

    None (not 0) only when precision or recall is itself undefined
    (denominator zero, e.g. no positive predictions or no actual positives
    at all) -- a real precision/recall of 0.0 still yields a real F1 of 0.0,
    not None; those are different states and must not be conflated.
    """
    if precision is None or recall is None:
        return None
    if precision + recall == 0:
        return 0.0
    return round(2 * precision * recall / (precision + recall), 4)


def score_labels(labels, findings):
    observed = {
        (str(item.get("file", "")).replace("\\", "/").lstrip("./"), item.get("rule_id"))
        for item in findings
    }
    cases = []
    totals = defaultdict(lambda: {"tp": 0, "fp": 0, "tn": 0, "fn": 0})
    for label in labels:
        key = (label["file"].replace("\\", "/").lstrip("./"), label["rule_id"])
        detected = key in observed or any(
            file.endswith("/" + key[0]) and rule == key[1]
            for file, rule in observed
        )
        expected = label["expected"] == "present"
        outcome = "tp" if expected and detected else "fn" if expected else "fp" if detected else "tn"
        totals[label["rule_id"]][outcome] += 1
        cases.append({**label, "detected": detected, "outcome": outcome})

    rules = {}
    for rule_id, count in sorted(totals.items()):
        precision = _ratio(count["tp"], count["tp"] + count["fp"])
        recall = _ratio(count["tp"], count["tp"] + count["fn"])
        rules[rule_id] = {
            **count,
            "precision": precision,
            "recall": recall,
            "specificity": _ratio(count["tn"], count["tn"] + count["fp"]),
            "f1": _f1(precision, recall),
        }
    combined = {key: sum(row[key] for row in totals.values()) for key in ("tp", "fp", "tn", "fn")}
    combined_precision = _ratio(combined["tp"], combined["tp"] + combined["fp"])
    combined_recall = _ratio(combined["tp"], combined["tp"] + combined["fn"])
    combined.update(
        {
            "precision": combined_precision,
            "recall": combined_recall,
            "specificity": _ratio(combined["tn"], combined["tn"] + combined["fp"]),
            "f1": _f1(combined_precision, combined_recall),
        }
    )
    return {"combined": combined, "rules": rules, "cases": cases}


def calibrate(corpus, labels_path, output_dir):
    corpus = Path(corpus).resolve()
    labels_path = Path(labels_path).resolve()
    output_dir = Path(output_dir)
    scan_output = output_dir / "scan"
    output_dir.mkdir(parents=True, exist_ok=True)
    run = analyze_path(corpus, scan_output, profile="quality")
    findings = json.loads((scan_output / "findings.json").read_text(encoding="utf-8"))
    labels = load_labels(labels_path)
    score = score_labels(labels, findings)
    payload = {
        "schema_version": 1,
        "corpus": str(corpus),
        "labels": str(labels_path),
        "labels_sha256": hashlib.sha256(labels_path.read_bytes()).hexdigest(),
        "profile": "quality",
        "analysis_failures": run.get("analysis_failures", 0),
        **score,
    }
    (output_dir / "calibration.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    with (output_dir / "cases.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=(*LABEL_FIELDS, "detected", "outcome"))
        writer.writeheader()
        writer.writerows(score["cases"])
    return payload


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", type=Path)
    parser.add_argument("labels", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    payload = calibrate(args.corpus, args.labels, args.output)
    print(json.dumps(payload["combined"], indent=2))
    if payload["analysis_failures"] or payload["combined"]["fp"] or payload["combined"]["fn"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
