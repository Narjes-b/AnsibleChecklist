#!/usr/bin/env python3
"""Merge per-family reference-label files into one file in the frozen reviewer schema.

Input: one CSV per review family (columns ``sample_id`` + the eight decision
columns + ``ai_confidence`` + ``bundle_issue``), as produced by the reference
labelling pass. Output (all write-once):

- ``<name>-agreement-pilot.csv``: the frozen blank reviewer form with the
  decision columns filled, so that ``scripts/v007_human_agreement.py`` can
  compare it with any human reviewer's returned file;
- ``<name>-extra.csv``: ``sample_id, ai_confidence, bundle_issue``;
- ``<name>-manifest.json``: checksums, counts, and the rule set used.

Every row is checked against the frozen validator's rules; ALL violations are
listed (the frozen validator stops at the first), then the whole file is passed
through the frozen validator itself.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.v007_human_agreement import (  # noqa: E402
    ACTIONABILITY_LABELS, SEMANTIC_LABELS, YES_NO_UNCERTAIN, ReviewerInputError,
    _reason_codes, validate_reviewer_file,
)
from scripts.v007_validation_pilot import REVIEWER_COLUMNS, REVIEWER_DECISION_COLUMNS  # noqa: E402

EXTRA = ("ai_confidence", "bundle_issue")
CONFIDENCE = {"high", "medium", "low"}


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with open(path, newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def problems(row: dict[str, str], codebook_reasons: set[str]) -> list[str]:
    found = []
    semantic, action = row["semantic_label"].strip(), row["actionability_label"].strip()
    if semantic not in SEMANTIC_LABELS:
        found.append(f"semantic_label={semantic!r}")
    if action not in ACTIONABILITY_LABELS:
        found.append(f"actionability_label={action!r}")
    for column in ("context_sufficient", "requires_external_context"):
        if row[column].strip() not in YES_NO_UNCERTAIN:
            found.append(f"{column}={row[column]!r}")
    if semantic in SEMANTIC_LABELS and action in ACTIONABILITY_LABELS:
        if (semantic in {"negative", "unreviewable"}) != (action == "not-applicable"):
            found.append(f"actionability {action!r} conflicts with semantic {semantic!r}")
    needed, kind = row["requires_external_context"].strip(), row["external_context_type"].strip()
    if needed == "no" and kind != "none":
        found.append("external_context_type must be 'none' when requires_external_context=no")
    if needed == "yes" and kind in {"", "none"}:
        found.append("external_context_type missing although external context is required")
    if not row["evidence_notes"].strip():
        found.append("evidence_notes empty")
    if semantic in {"uncertain", "unreviewable"} and not row["reviewer_notes"].strip():
        found.append("uncertainty not explained in reviewer_notes")
    if row["reason_code"].strip() not in codebook_reasons:
        found.append(f"reason_code={row['reason_code']!r} not in the codebook")
    if row.get("ai_confidence", "").strip() not in CONFIDENCE:
        found.append(f"ai_confidence={row.get('ai_confidence')!r}")
    if not row.get("bundle_issue", "").strip():
        found.append("bundle_issue empty")
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--validation-dir", type=Path, required=True)
    parser.add_argument("--label-dir", type=Path, required=True, help="directory with the per-family CSV files")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--name", default="model-reference")
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    validation = args.validation_dir.resolve()
    master_path = validation / "samples/agreement-pilot/agreement-pilot-master.csv"
    _, master = read_rows(master_path)
    _, blank = read_rows(validation / "reviewers/reviewer-a/agreement-pilot.csv")
    labels: dict[str, dict[str, str]] = {}
    for path in sorted(args.label_dir.glob("*.csv")):
        _, rows = read_rows(path)
        for row in rows:
            if row["sample_id"] in labels:
                raise SystemExit(f"duplicate label for {row['sample_id']}")
            labels[row["sample_id"]] = row
    missing = [row["sample_id"] for row in blank if row["sample_id"] not in labels]
    extra = sorted(set(labels) - {row["sample_id"] for row in blank})
    if missing or extra:
        raise SystemExit(f"coverage mismatch: missing={missing[:5]}({len(missing)}) unexpected={extra[:5]}({len(extra)})")
    reason_cache: dict[str, set[str]] = {}
    violations = []
    for form in blank:
        row = labels[form["sample_id"]]
        codebook = form["codebook_path"]
        if codebook not in reason_cache:
            reason_cache[codebook] = _reason_codes(validation, codebook)
        for text in problems(row, reason_cache[codebook]):
            violations.append((form["sample_id"], text))
    print(f"rows {len(blank)}; violations {len(violations)}")
    for sample_id, text in violations:
        print(f"  {sample_id}: {text}")
    if violations or args.check_only:
        return 1 if violations else 0
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    form_path = out / f"{args.name}-agreement-pilot.csv"
    extra_path = out / f"{args.name}-extra.csv"
    for path in (form_path, extra_path, out / f"{args.name}-manifest.json"):
        if path.exists():
            raise SystemExit(f"refusing to overwrite {path}")
    with open(form_path, "w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=REVIEWER_COLUMNS, lineterminator="\n")
        writer.writeheader()
        for form in blank:
            row = dict(form)
            for column in REVIEWER_DECISION_COLUMNS:
                row[column] = labels[form["sample_id"]][column].strip()
            writer.writerow(row)
    with open(extra_path, "w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["sample_id", *EXTRA])
        for form in blank:
            writer.writerow([form["sample_id"], *(labels[form["sample_id"]][c].strip() for c in EXTRA)])
    try:
        validate_reviewer_file(validation, master, form_path, name_for_errors := args.name)
        verdict = "passes the frozen reviewer validator"
    except ReviewerInputError as error:
        verdict = f"FAILS the frozen validator: {error}"
    manifest = {
        "name": args.name, "rows": len(blank), "frozen_validator": verdict,
        "sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (form_path, extra_path)},
    }
    (out / f"{args.name}-manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(verdict)
    return 0 if verdict.startswith("passes") else 1


if __name__ == "__main__":
    raise SystemExit(main())
