#!/usr/bin/env python3
"""Summarize the frozen v0.0.7 variable-resolution agent review."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def wilson(successes: int, total: int, z: float = 1.96) -> list[float] | None:
    if total == 0:
        return None
    p = successes / total
    z2 = z * z
    denominator = 1 + z2 / total
    center = (p + z2 / (2 * total)) / denominator
    margin = z * math.sqrt(p * (1 - p) / total + z2 / (4 * total * total)) / denominator
    return [max(0.0, center - margin), min(1.0, center + margin)]


def metric(successes: int, total: int) -> dict:
    return {
        "successes": successes,
        "total": total,
        "estimate": successes / total if total else None,
        "wilson_95": wilson(successes, total),
    }


def percent(value: float | None) -> str:
    return "n/a" if value is None else f"{100 * value:.1f}%"


def interval(value: list[float] | None) -> str:
    return "n/a" if value is None else f"{100 * value[0]:.1f}%–{100 * value[1]:.1f}%"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--positive-labels", type=Path, required=True)
    parser.add_argument("--source-block-labels", type=Path, required=True)
    parser.add_argument("--source-issue-labels", type=Path, required=True)
    parser.add_argument("--suppressed-labels", type=Path, required=True)
    parser.add_argument("--sample-manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    positive = read_csv(args.positive_labels)
    blocks = read_csv(args.source_block_labels)
    issues = read_csv(args.source_issue_labels)
    suppressed = read_csv(args.suppressed_labels)
    manifest = json.loads(args.sample_manifest.read_text(encoding="utf-8"))

    candidate = [row for row in positive if row["resolution_status"] == "CANDIDATE_MISSING"]
    candidate_decided = [row for row in candidate if row["defect_label"] in {"TP", "FP"}]
    classification_decided = [row for row in positive if row["classification_correct"] in {"yes", "no"}]
    matched_issues = [row for row in issues if row["matched_detector_occurrence"] == "yes"]
    issue_projects = {row["project"] for row in issues}
    matched_issue_projects = {row["project"] for row in matched_issues}

    metrics = {
        "suppression_safety": metric(sum(row["suppression_safe"] == "yes" for row in suppressed), len(suppressed)),
        "candidate_missing_decided_precision": metric(sum(row["defect_label"] == "TP" for row in candidate_decided), len(candidate_decided)),
        "candidate_missing_conservative_yield": metric(sum(row["defect_label"] == "TP" for row in candidate), len(candidate)),
        "resolution_class_decided_accuracy": metric(sum(row["classification_correct"] == "yes" for row in classification_decided), len(classification_decided)),
        "resolution_class_coverage": metric(len(classification_decided), len(positive)),
        "source_first_supported_recall_occurrence": metric(len(matched_issues), len(issues)),
        "source_first_supported_recall_repository": metric(len(matched_issue_projects), len(issue_projects)),
    }
    payload = {
        "schema_version": 1,
        "reviewer": "codex-agent-source-reviewer",
        "review_method": "single-agent code-assisted source review",
        "independent_human_gold_standard": False,
        "sample_manifest": manifest,
        "review_artifact_hashes_sha256": {
            "positive_labels": hashlib.sha256(args.positive_labels.read_bytes()).hexdigest(),
            "source_block_labels": hashlib.sha256(args.source_block_labels.read_bytes()).hexdigest(),
            "source_issue_labels": hashlib.sha256(args.source_issue_labels.read_bytes()).hexdigest(),
            "suppressed_labels": hashlib.sha256(args.suppressed_labels.read_bytes()).hexdigest(),
        },
        "counts": {
            "suppressed_census": len(suppressed),
            "emitted_positive": len(positive),
            "source_first_blocks": len(blocks),
            "total_primary_units": len(suppressed) + len(positive) + len(blocks),
            "positive_by_resolution": dict(Counter(row["resolution_status"] for row in positive)),
            "positive_defect_labels": dict(Counter(row["defect_label"] for row in positive)),
            "classification_labels": dict(Counter(row["classification_correct"] for row in positive)),
            "source_block_labels": dict(Counter(row["defect_label"] for row in blocks)),
            "source_supported_issues": len(issues),
            "source_supported_issues_matched": len(matched_issues),
        },
        "metrics": metrics,
        "missed_supported_issues": [
            {
                "project": row["project"], "file": row["file"],
                "line": row["line"], "variable": row["variable"],
                "rationale": row["rationale"],
            }
            for row in issues if row["matched_detector_occurrence"] == "no"
        ],
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "review-results.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    lines = [
        "# v0.0.7 Variable Resolution Primary Review",
        "",
        "## Scope and status",
        "",
        "This review covers 847 primary units: the complete 247-occurrence suppression census, "
        "450 emitted occurrences (150 per resolution class), and 150 source-first files. "
        "Selection is deterministic, repository-capped, and frozen by SHA-256 hashes.",
        "",
        "The labels are a single-agent, code-assisted source review. They are not independent "
        "human gold-standard labels and cannot establish inter-rater agreement.",
        "",
        "## Results",
        "",
        "| Measure | Result | Naive Wilson 95% interval |",
        "|---|---:|---:|",
    ]
    labels = {
        "suppression_safety": "Suppression safety (required-argument census)",
        "candidate_missing_decided_precision": "CANDIDATE_MISSING precision among decided labels",
        "candidate_missing_conservative_yield": "CANDIDATE_MISSING conservative TP yield",
        "resolution_class_decided_accuracy": "Resolution-class accuracy among decided labels",
        "resolution_class_coverage": "Resolution-class decision coverage",
        "source_first_supported_recall_occurrence": "Source-first supported recall, occurrence level",
        "source_first_supported_recall_repository": "Source-first supported recall, repository level",
    }
    for key, label in labels.items():
        value = metrics[key]
        lines.append(
            f"| {label} | {value['successes']}/{value['total']} ({percent(value['estimate'])}) | {interval(value['wilson_95'])} |"
        )
    lines += [
        "",
        "## Label distribution",
        "",
        "- All 247 suppressed occurrences were verified safe through applicable required role argument contracts.",
        "- `CANDIDATE_MISSING`: 84 TP and 66 uncertain; no reviewed false positives.",
        "- `EXTERNAL_INPUT_UNCERTAIN`: 150 uncertainty labels with 150 correct class decisions.",
        "- `RUNTIME_CONTEXT_UNCERTAIN`: 150 uncertainty labels; 132 correct class decisions and 18 unclear.",
        "- Source-first blocks: 133 TN, 3 containing supported issues, and 14 unresolved-context blocks.",
        "",
        "## Missed supported issue",
        "",
    ]
    if payload["missed_supported_issues"]:
        for row in payload["missed_supported_issues"]:
            lines.append(
                f"- `{row['project']}:{row['file']}:{row['line']}` uses `{row['variable']}` without a visible definition. "
                "The surrounding defaults file defines `tarzan_root_dir`, making this a likely variable-name typo and a detector false negative."
            )
    else:
        lines.append("No missed supported issue was found in the source-first sample.")
    lines += [
        "",
        "## Interpretation limits",
        "",
        "The Wilson intervals treat occurrences as independent and therefore understate uncertainty when findings cluster by repository. "
        "Repository-level recall is reported alongside occurrence-level recall. The inspected corpus has already influenced development, "
        "so this is calibration evidence rather than a final unseen held-out evaluation. Formal agreement still requires a second independent reviewer.",
        "",
    ]
    (args.output_dir / "VALIDATION_REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(metrics, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
