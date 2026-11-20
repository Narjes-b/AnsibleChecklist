#!/usr/bin/env python3
"""Recheck changed internal rules against a frozen paired occurrence ledger."""

from __future__ import annotations

import argparse
import csv
import gc
import json
from collections import Counter, defaultdict
from pathlib import Path
import re

from ansibleguard.detectors.missing_checklist import detect_variable_use_before_definition
from ansibleguard.detectors.paper_candidates import detect_unguarded_variables
from ansibleguard.detectors.review_checklist import detect_silent_error_suppression
from ansibleguard.detectors.set_fact import (
    _repository_documents,
    unnecessary_set_fact_details,
)
from ansibleguard.symbol_index import build_repository_symbol_index


RULES = {
    "unguarded-variable",
    "unhandled-failure-suppression",
    "variable-use-before-definition",
    "unnecessary-set-fact",
}


def _message_variable(message: str) -> str:
    match = re.search(r"Variable '([^']+)'", message or "")
    return match.group(1) if match else ""


def _set_fact_variable(message: str) -> str:
    match = re.search(r"set_fact variable '([^']+)'", message or "")
    return match.group(1) if match else ""


def _load_targets(path: Path):
    by_project = defaultdict(list)
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["concept_id"] not in RULES:
                continue
            # Recheck every occurrence that exists in either side. Fixed rows
            # exercise rules that may have been over-suppressed in 0.0.4.
            by_project[row["project"]].append(row)
    return by_project


def _details_by_file(rows, repository: Path, index):
    requested = defaultdict(set)
    for row in rows:
        requested[row["concept_id"]].add(row["file"])
    result = defaultdict(dict)
    for relative in sorted(requested["unguarded-variable"]):
        result["unguarded-variable"][relative] = detect_unguarded_variables(
            repository / relative, symbol_index=index
        )[1]
    for relative in sorted(requested["unhandled-failure-suppression"]):
        result["unhandled-failure-suppression"][relative] = (
            detect_silent_error_suppression(repository / relative, symbol_index=index)[1]
        )
    for relative in sorted(requested["variable-use-before-definition"]):
        result["variable-use-before-definition"][relative] = (
            detect_variable_use_before_definition(repository / relative, symbol_index=index)[1]
        )
    for relative in sorted(requested["unnecessary-set-fact"]):
        result["unnecessary-set-fact"][relative] = (
            unnecessary_set_fact_details(repository / relative, symbol_index=index) or []
        )
    return result


def _row_survives(row, details):
    concept = row["concept_id"]
    old_line = int(row["line"] or 1)
    message = row["head_message"] or row["base_message"]
    if concept in {"unguarded-variable", "variable-use-before-definition"}:
        variable = _message_variable(message)
        return any(item.get("variable") == variable for item in details), variable
    if concept == "unhandled-failure-suppression":
        return any(int(item.get("line") or 1) == old_line for item in details), ""
    variable = _set_fact_variable(message)
    if variable:
        return any(item.get("variable") == variable for item in details), variable
    # Frozen 0.0.4 set-fact rows were file-level aggregates. Preserve that
    # identity only when the corrected detector still finds any unused fact.
    return bool(details), ""


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--paired", type=Path, required=True)
    parser.add_argument("--repositories", type=Path, default=Path("study/repositories"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    args = parser.parse_args(argv)

    targets = _load_targets(args.paired)
    output_rows = []
    counts = Counter()
    for number, (project, rows) in enumerate(sorted(targets.items()), 1):
        repository = args.repositories / project
        index = build_repository_symbol_index(repository)
        findings = _details_by_file(rows, repository, index)
        for row in rows:
            details = findings[row["concept_id"]].get(row["file"], [])
            survives, variable = _row_survives(row, details)
            decision = "still-reported" if survives else "removed-by-fix"
            counts[(row["concept_id"], row["status"], decision)] += 1
            output_rows.append(
                {
                    "project": project,
                    "file": row["file"],
                    "old_line": row["line"],
                    "concept_id": row["concept_id"],
                    "old_pair_status": row["status"],
                    "old_occurrence_id": row["head_occurrence_id"] or row["base_occurrence_id"],
                    "variable": variable,
                    "recheck_decision": decision,
                    "current_file_finding_count": len(details),
                }
            )
        _repository_documents.cache_clear()
        del index, findings
        gc.collect()
        print(f"Rechecked {number}/{len(targets)} repositories: {project}", flush=True)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fields = list(output_rows[0]) if output_rows else []
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(output_rows)
    payload = {
        "repositories": len(targets),
        "ledger_rows": len(output_rows),
        "counts": [
            {
                "concept_id": concept,
                "old_pair_status": status,
                "recheck_decision": decision,
                "count": count,
            }
            for (concept, status, decision), count in sorted(counts.items())
        ],
    }
    args.summary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2), flush=True)


if __name__ == "__main__":
    main()
