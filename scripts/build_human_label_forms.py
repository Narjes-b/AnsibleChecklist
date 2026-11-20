#!/usr/bin/env python3
"""Build blinded, identical labelling forms for two human reviewers.

Reads an unlabelled sample (no label columns) and writes one form per
reviewer with the evidence columns and empty decision columns. Nothing from
any earlier label pass is copied, so each reviewer labels blind to it.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path

CODEBOOKS = {
    "Maintainability/complexity": "FAMILY_MAINTAINABILITY_V2.md",
    "Objective correctness": "FAMILY_OBJECTIVE_CORRECTNESS_V2.md",
    "Review/history": "FAMILY_REVIEW_HISTORY_V2.md",
    "Security": "FAMILY_SECURITY_V2.md",
    "Structure/reuse": "FAMILY_STRUCTURE_V2.md",
    "Style/policy": "FAMILY_STYLE_POLICY_V2.md",
    "Variable/reference reasoning": "FAMILY_VARIABLES_V2.md",
}
EVIDENCE = ["sample_id", "review_family", "codebook", "rule_id", "repository", "commit_sha", "path", "line",
            "message", "source_context"]
# Field names follow codebook v2.1 (COMMON_V2.md, sections C4-C5).
DECISIONS = ["semantic_label", "semantic_reason", "actionability_label", "actionability_reason",
             "context_sufficient", "requires_external_context", "external_context_type", "evidence_notes"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", type=Path,
                        default=Path("study/exploratory-labels/stratified-sample/stratified-sample.csv"))
    parser.add_argument("--codebook-dir", default="study/validation-v007-human/codebooks-v2")
    parser.add_argument("--output-dir", type=Path, default=Path("study/human-labels-400"))
    parser.add_argument("--reviewers", nargs="+", default=["reviewer-a", "reviewer-b"])
    args = parser.parse_args(argv)
    with args.sample.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    forbidden = [c for c in rows[0] if "label" in c or c.startswith("ai_")]
    if forbidden:
        raise SystemExit(f"sample already contains label columns: {forbidden}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for reviewer in args.reviewers:
        path = args.output_dir / f"{reviewer}.csv"
        if path.exists():
            raise SystemExit(f"{path} exists; refusing to overwrite a form that may hold labels")
        with path.open("w", newline="", encoding="utf-8") as target:
            writer = csv.DictWriter(target, fieldnames=EVIDENCE + DECISIONS)
            writer.writeheader()
            for row in rows:
                writer.writerow({**{k: row.get(k, "") for k in EVIDENCE},
                                 "codebook": f"{args.codebook_dir}/{CODEBOOKS.get(row['review_family'], 'COMMON_V2.md')}",
                                 **{k: "" for k in DECISIONS}})
        print(path, hashlib.sha256(path.read_bytes()).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
