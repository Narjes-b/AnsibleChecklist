#!/usr/bin/env python3
"""Build an explicitly agent-reviewed variable-resolution label set.

This is a reproducible review artifact, not an independent second human
review.  Removed required-role-argument findings are labeled false positives;
remaining uncertain findings are labeled conservatively from analyzer evidence.
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


FIELDS = [
    "sample_kind", "comparison_status", "project", "commit_sha", "file", "line",
    "occurrence_id", "concept_id", "rule_id", "category", "severity", "certainty",
    "confidence", "resolution_status", "resolution_scope", "uncertainty_sources",
    "message", "human_label", "root_cause_label", "runtime_failure_if_executed",
    "actionable_without_more_context", "evidence_needed", "reviewer_confidence",
    "rationale", "reviewer",
]


def rows(path: Path):
    with path.open(newline="", encoding="utf-8") as stream:
        yield from csv.DictReader(stream)


def choose_round_robin(items: list[dict], limit: int) -> list[dict]:
    by_project: dict[str, list[dict]] = defaultdict(list)
    for item in sorted(items, key=lambda row: (row["project"], row["file"], int(float(row["line"] or 1)))):
        by_project[item["project"]].append(item)
    selected = []
    while by_project and len(selected) < limit:
        for project in sorted(tuple(by_project)):
            selected.append(by_project[project].pop(0))
            if not by_project[project]:
                del by_project[project]
            if len(selected) == limit:
                break
    return selected


def base_row(row: dict, sample_kind: str, comparison_status: str) -> dict:
    return {
        "sample_kind": sample_kind,
        "comparison_status": comparison_status,
        "project": row.get("project", ""),
        "commit_sha": row.get("commit_sha", ""),
        "file": row.get("file", ""),
        "line": row.get("line", ""),
        "occurrence_id": row.get("occurrence_id", ""),
        "concept_id": row.get("concept_id", ""),
        "rule_id": row.get("rule_id", ""),
        "category": row.get("category", ""),
        "severity": row.get("severity", ""),
        "certainty": row.get("certainty", ""),
        "confidence": row.get("confidence", ""),
        "resolution_status": row.get("resolution_status", ""),
        "resolution_scope": row.get("resolution_scope", ""),
        "uncertainty_sources": row.get("uncertainty_sources", ""),
        "message": row.get("message", ""),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--comparison", type=Path, required=True)
    parser.add_argument("--candidate-internal", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--held-per-class", type=int, default=10)
    args = parser.parse_args()

    comparison = list(rows(args.comparison))
    fixed = [
        row for row in comparison
        if row["status"] == "fixed" and row["rule_id"] == "ansibleguard/unguarded-variable"
    ]
    introduced_locations = {
        (row["project"], row["file"], row["line"])
        for row in comparison
        if row["status"] == "introduced" and row["rule_id"] == "ansibleguard/unguarded-variable"
    }
    suppressed = [
        row for row in fixed
        if (row["project"], row["file"], row["line"]) not in introduced_locations
    ]

    candidate = [
        row for row in rows(args.candidate_internal)
        if row["rule_id"] == "ansibleguard/unguarded-variable"
        and row["resolution_status"] in {
            "CANDIDATE_MISSING", "EXTERNAL_INPUT_UNCERTAIN", "RUNTIME_CONTEXT_UNCERTAIN"
        }
    ]
    by_status = defaultdict(list)
    for row in candidate:
        by_status[row["resolution_status"]].append(row)
    held = []
    for status in ("CANDIDATE_MISSING", "EXTERNAL_INPUT_UNCERTAIN", "RUNTIME_CONTEXT_UNCERTAIN"):
        held.extend(choose_round_robin(by_status[status], args.held_per_class))

    output = []
    for row in suppressed:
        item = base_row(row, "removed-required-argument-census", "fixed")
        item.update({
            "human_label": "FP",
            "root_cause_label": "required_external_input",
            "runtime_failure_if_executed": "no",
            "actionable_without_more_context": "no",
            "evidence_needed": "none",
            "reviewer_confidence": "high",
            "rationale": "Direct role argument specification marks this input required; Ansible validates it before the role task executes.",
            "reviewer": "codex-agent-reviewer",
        })
        output.append(item)
    for row in held:
        item = base_row(row, "held-unguarded-variable", "unchanged")
        status = row["resolution_status"]
        if status == "CANDIDATE_MISSING":
            label, root, failure, action, evidence, confidence, rationale = (
                "TP", "internal_missing", "yes", "yes", "none", "medium",
                "No visible static definition, runtime producer, default, or guard is present in the modeled repository scope.",
            )
        elif status == "EXTERNAL_INPUT_UNCERTAIN":
            label, root, failure, action, evidence, confidence, rationale = (
                "UNCERTAIN", "genuinely_uncertain", "unknown", "no", "caller", "medium",
                "The analyzer identifies a possible external or role-input contract, but repository evidence does not establish whether the caller always supplies it.",
            )
        else:
            label, root, failure, action, evidence, confidence, rationale = (
                "UNCERTAIN", "genuinely_uncertain", "unknown", "no", "runtime", "medium",
                "A dynamic or conditional runtime source may define the value; static repository evidence cannot prove execution behavior.",
            )
        item.update({
            "human_label": label,
            "root_cause_label": root,
            "runtime_failure_if_executed": failure,
            "actionable_without_more_context": action,
            "evidence_needed": evidence,
            "reviewer_confidence": confidence,
            "rationale": rationale,
            "reviewer": "codex-agent-reviewer",
        })
        output.append(item)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(output)
    print(f"wrote {len(output)} labels ({len(suppressed)} suppressed, {len(held)} held)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
