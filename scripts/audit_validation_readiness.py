#!/usr/bin/env python3
"""Create a machine-readable Phase 0 validation-readiness audit.

This does not claim detector accuracy.  It freezes code/profile metadata and
checks whether a label ledger can support the claims made from it.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import subprocess
from collections import Counter
from pathlib import Path

from ansibleguard import __version__
from ansibleguard.profiles import PROFILE_NAMES, profile_metadata
from ansibleguard.report.findings import RULE_CATALOG


def _git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], check=False, capture_output=True, text=True
    )
    return result.stdout.strip()


def _sha256_json(value) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def audit_ledger(rows: list[dict], expected_repositories: int | None = None) -> dict:
    occurrences = [row for row in rows if row.get("validation_unit") == "occurrence"]
    clean = [row for row in rows if row.get("validation_unit") == "clean-file-review"]
    label_of = lambda row: row.get("adjudicated_label") or row.get("consensus_label", "")
    consensus = Counter(label_of(row) for row in rows)
    occurrence_consensus = Counter(
        label_of(row) for row in occurrences
    )
    dual_reviewed = [
        row
        for row in rows
        if row.get("reviewer_1_label") and row.get("reviewer_2_label")
    ]
    exact = sum(
        row.get("reviewer_1_label") == row.get("reviewer_2_label")
        for row in dual_reviewed
    )
    decidable = (
        occurrence_consensus["true-positive"]
        + occurrence_consensus["false-positive"]
    )
    repositories = {row.get("project", "") for row in rows if row.get("project")}
    warnings = []
    if "selection_probability" not in (rows[0] if rows else {}):
        warnings.append("selection probabilities absent; overall precision is unweighted")
    if expected_repositories is not None and len(repositories) != expected_repositories:
        warnings.append(
            f"sample represents {len(repositories)} of {expected_repositories} expected repositories"
        )
    if not rows or any(not label_of(row) for row in rows):
        warnings.append("one or more rows lack a consensus label")
    if len(dual_reviewed) != len(rows):
        warnings.append("one or more rows lack two independent reviewer labels")
    return {
        "items": len(rows),
        "occurrences": len(occurrences),
        "clean_file_reviews": len(clean),
        "repositories_represented": len(repositories),
        "dual_reviewer_items": len(dual_reviewed),
        "exact_reviewer_agreement_count": exact,
        "exact_reviewer_agreement_rate": (
            exact / len(dual_reviewed) if dual_reviewed else None
        ),
        "pre_reconciliation_disagreement_count": len(dual_reviewed) - exact,
        "consensus_labels_all_items": dict(consensus),
        "consensus_labels_occurrences": dict(occurrence_consensus),
        "occurrence_precision_unweighted": (
            occurrence_consensus["true-positive"] / decidable if decidable else None
        ),
        "warnings": warnings,
    }


def build_audit(sample: Path | None, expected_repositories: int | None) -> dict:
    status = _git("status", "--porcelain")
    catalog = {
        rule_id: {
            key: metadata.get(key)
            for key in ("level", "category", "confidence", "status")
        }
        for rule_id, metadata in sorted(RULE_CATALOG.items())
    }
    audit = {
        "phase": "validation-readiness",
        "tool_version": __version__,
        "git_commit": _git("rev-parse", "HEAD"),
        "git_worktree_clean": not bool(status),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "rule_catalog_sha256": _sha256_json(catalog),
        "rule_status_counts": dict(
            Counter(metadata["status"] for metadata in RULE_CATALOG.values())
        ),
        "profiles": {name: profile_metadata(name) for name in PROFILE_NAMES},
        "warnings": [],
    }
    if status:
        audit["warnings"].append(
            "worktree is dirty; do not call this an immutable validation release"
        )
    if sample is not None:
        with sample.open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        audit["sample"] = {
            "path": str(sample),
            "sha256": hashlib.sha256(sample.read_bytes()).hexdigest(),
            **audit_ledger(rows, expected_repositories),
        }
        audit["warnings"].extend(audit["sample"]["warnings"])
    return audit


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", type=Path)
    parser.add_argument("--expected-repositories", type=int)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    audit = build_audit(args.sample, args.expected_repositories)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote validation-readiness audit to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
