#!/usr/bin/env python3
"""Reviewer form schema v2 (codebooks v2): blank-form builder and validator.

The frozen v1 schema (``v007_validation_pilot.REVIEWER_COLUMNS``) is untouched. v2 replaces
``reason_code`` with ``semantic_reason`` and ``actionability_reason``, makes
``external_context_type`` a controlled list, and adds ``bundle_issue``.

Commands:
  build     write a blank v2 form from a v1 master/blank form (same visible columns,
            ``codebook_path`` rewritten to the v2 family file);
  validate  check a returned v2 form against a blank one and report ALL problems.

Reason lists are read from ``codebooks-v2/FAMILY_*_V2.md`` (lines ``Positive semantic
reasons:``, ``Negative:``, ``Uncertain:``, ``Unreviewable:``, ``Actionability reasons:``) plus the
common sets defined here (mirrored in ``COMMON_V2.md`` and checked by a test).
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import re
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.v007_validation_pilot import REVIEWER_VISIBLE_COLUMNS  # noqa: E402

V2_DECISION_COLUMNS = [
    "semantic_label", "actionability_label", "context_sufficient", "requires_external_context",
    "external_context_type", "semantic_reason", "actionability_reason", "bundle_issue",
    "evidence_notes", "reviewer_notes",
]
V2_COLUMNS = [*REVIEWER_VISIBLE_COLUMNS, *V2_DECISION_COLUMNS]
SEMANTIC = ("positive", "negative", "uncertain", "unreviewable")
ACTIONABILITY = ("blocking", "actionable", "advisory", "not-actionable", "uncertain", "not-applicable")
YES_NO_UNCERTAIN = ("yes", "no", "uncertain")
EXTERNAL_TYPES = ("none", "ansible-version", "collection-docs", "other-repo-file", "runtime-value",
                  "inventory-or-caller", "organization-policy", "other")
BUNDLE_ISSUES = ("none", "truncated", "missing-subject", "redaction-hides", "anchor-mismatch",
                 "missing-file", "codebook-ambiguous", "other")
COMMON_SEMANTIC = {
    "positive": {"confirmed-defect", "confirmed-policy-violation", "other"},
    "negative": {"out-of-scope", "condition-absent", "other"},
    "uncertain": {"insufficient-source-context", "other"},
    "unreviewable": {"bundle-defect"},
}
COMMON_ACTIONABILITY = {"fix-is-proportionate", "low-value", "policy-optional", "test-or-fixture-context",
                        "needs-owner-decision"}
LINE_KEYS = {
    "Positive semantic reasons:": "positive", "Negative:": "negative", "Uncertain:": "uncertain",
    "Unreviewable:": "unreviewable", "Actionability reasons:": "actionability",
}


def family_reasons(path: Path) -> dict[str, set[str]]:
    result = {key: set() for key in (*SEMANTIC, "actionability")}
    for line in path.read_text(encoding="utf-8").splitlines():
        for prefix, kind in LINE_KEYS.items():
            if line.startswith(prefix):
                result[kind] |= set(re.findall(r"`([^`]+)`", line))
    for kind, extra in COMMON_SEMANTIC.items():
        result[kind] |= extra
    result["actionability"] |= COMMON_ACTIONABILITY
    return result


def v2_family_file(codebook_path: str) -> str:
    """Map a v1 family codebook path to its v2 file; a path that is already v2 is returned unchanged."""
    name = Path(codebook_path).name  # FAMILY_X.md or FAMILY_X_V2.md
    if name.endswith("_V2.md"):
        return f"codebooks-v2/{name}"
    return f"codebooks-v2/{name[:-3]}_V2.md"


def read_table(path: Path) -> list[dict[str, str]]:
    with open(path, newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def build_blank(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    out = []
    for row in rows:
        new = {column: row.get(column, "") for column in REVIEWER_VISIBLE_COLUMNS}
        new["codebook_path"] = v2_family_file(row["codebook_path"])
        new["review_question"] = row.get("review_question", "")
        out.append({**new, **{column: "" for column in V2_DECISION_COLUMNS}})
    return out


def check_row(row: dict[str, str], reasons: dict[str, set[str]]) -> list[str]:
    found = []
    get = lambda key: row.get(key, "").strip()  # noqa: E731
    semantic, action = get("semantic_label"), get("actionability_label")
    for column, allowed in (("semantic_label", SEMANTIC), ("actionability_label", ACTIONABILITY),
                            ("context_sufficient", YES_NO_UNCERTAIN), ("requires_external_context", YES_NO_UNCERTAIN),
                            ("external_context_type", EXTERNAL_TYPES), ("bundle_issue", BUNDLE_ISSUES)):
        if get(column) not in allowed:
            found.append(f"{column}={get(column)!r} not in {list(allowed)}")
    if semantic in SEMANTIC and action in ACTIONABILITY and (semantic in {"negative", "unreviewable"}) != (action == "not-applicable"):
        found.append(f"actionability {action!r} conflicts with semantic {semantic!r}")
    needed, kind = get("requires_external_context"), get("external_context_type")
    if needed == "no" and kind != "none":
        found.append("external_context_type must be 'none' when requires_external_context=no")
    if needed == "yes" and kind in {"", "none"}:
        found.append("external_context_type required when requires_external_context=yes")
    sem_reason, act_reason = get("semantic_reason"), get("actionability_reason")
    if semantic in SEMANTIC and sem_reason not in reasons[semantic]:
        found.append(f"semantic_reason={sem_reason!r} not allowed for a {semantic} label")
    if action == "not-applicable":
        if act_reason != "not-applicable":
            found.append("actionability_reason must be 'not-applicable' when actionability is not-applicable")
    elif act_reason not in reasons["actionability"]:
        found.append(f"actionability_reason={act_reason!r} not allowed")
    if (semantic == "unreviewable" or sem_reason == "bundle-defect") and get("bundle_issue") == "none":
        found.append("bundle_issue must name the defect for an unreviewable item / bundle-defect reason")
    if not get("evidence_notes"):
        found.append("evidence_notes empty")
    if (semantic in {"uncertain", "unreviewable"} or sem_reason == "other" or act_reason == "other") and not get("reviewer_notes"):
        found.append("reviewer_notes required for uncertain/unreviewable items and 'other' reasons")
    return found


def validate(blank: list[dict[str, str]], returned: list[dict[str, str]], validation_dir: Path) -> list[tuple[str, str]]:
    problems: list[tuple[str, str]] = []
    if returned and list(returned[0]) != V2_COLUMNS:
        problems.append(("*", "columns differ from the v2 schema"))
        return problems
    if [r["sample_id"] for r in returned] != [r["sample_id"] for r in blank]:
        problems.append(("*", "sample IDs or row order differ from the blank form"))
        return problems
    cache: dict[str, dict[str, set[str]]] = {}
    for form, row in zip(blank, returned):
        for column in REVIEWER_VISIBLE_COLUMNS:
            if form[column] != row[column]:
                problems.append((form["sample_id"], f"frozen evidence column {column} changed"))
        path = form["codebook_path"]
        if path not in cache:
            cache[path] = family_reasons(validation_dir / path)
        problems += [(form["sample_id"], text) for text in check_row(row, cache[path])]
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    b = sub.add_parser("build")
    b.add_argument("--source", type=Path, required=True, help="v1 master or blank reviewer CSV")
    b.add_argument("--output", type=Path, required=True)
    v = sub.add_parser("validate")
    v.add_argument("--blank", type=Path, required=True)
    v.add_argument("--returned", type=Path, required=True)
    v.add_argument("--validation-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "build":
        if args.output.exists():
            raise SystemExit(f"refusing to overwrite {args.output}")
        rows = build_blank(read_table(args.source))
        with open(args.output, "w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=V2_COLUMNS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        print(f"wrote {len(rows)} blank v2 rows")
        return 0
    problems = validate(read_table(args.blank), read_table(args.returned), args.validation_dir)
    for sample_id, text in problems:
        print(f"{sample_id}: {text}")
    print(f"problems {len(problems)}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
