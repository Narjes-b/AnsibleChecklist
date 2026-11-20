#!/usr/bin/env python3
"""Compact full-corpus scan for the four internal rules changed after v0.0.4."""

from __future__ import annotations

import argparse
import csv
import gc
import json
from collections import Counter
from pathlib import Path

from ansibleguard.detectors.missing_checklist import detect_variable_use_before_definition
from ansibleguard.detectors.paper_candidates import detect_unguarded_variables
from ansibleguard.detectors.review_checklist import detect_silent_error_suppression
from ansibleguard.detectors.set_fact import (
    _repository_documents,
    unnecessary_set_fact_details,
)
from ansibleguard.symbol_index import build_repository_symbol_index


def _truthy(value):
    return str(value or "").strip().lower() in {"1", "true", "yes", "y"}


def _classification_path(directory: Path, project: str, commit_sha: str) -> Path:
    return directory / f"{project.replace('/', '__')}__{commit_sha}.csv"


def _selected_files(path: Path):
    with path.open(newline="", encoding="utf-8") as handle:
        return [row["path"] for row in csv.DictReader(handle) if _truthy(row["included"])]


def _append(output, project, relative, concept, details):
    for detail in details:
        output.append(
            {
                "project": project,
                "file": relative,
                "line": detail.get("line", 1),
                "concept_id": concept,
                "variable": detail.get("variable", ""),
                "message": detail.get("issue", ""),
            }
        )


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--classification-dir", type=Path, required=True)
    parser.add_argument("--repositories", type=Path, default=Path("study/repositories"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument(
        "--rule",
        action="append",
        choices=(
            "unguarded-variable",
            "unhandled-failure-suppression",
            "variable-use-before-definition",
            "unnecessary-set-fact",
        ),
        help="Rule to run (repeatable); default runs all four.",
    )
    args = parser.parse_args(argv)
    enabled = set(args.rule or (
        "unguarded-variable",
        "unhandled-failure-suppression",
        "variable-use-before-definition",
        "unnecessary-set-fact",
    ))

    with args.manifest.open(newline="", encoding="utf-8") as handle:
        repositories = list(csv.DictReader(handle))
    findings = []
    scanned_files = 0
    failed_files = []
    for number, row in enumerate(repositories, 1):
        project = row["project"]
        repository = args.repositories / project
        classification = _classification_path(
            args.classification_dir, project, row["commit_sha"]
        )
        selected = _selected_files(classification)
        index = build_repository_symbol_index(repository)
        before = len(findings)
        for relative in selected:
            source = repository / relative
            try:
                text = source.read_text(encoding="utf-8", errors="replace")
                if "unguarded-variable" in enabled and ("{{" in text or "{%" in text):
                    _append(
                        findings,
                        project,
                        relative,
                        "unguarded-variable",
                        detect_unguarded_variables(source, symbol_index=index)[1],
                    )
                if "unhandled-failure-suppression" in enabled and (
                    "ignore_errors:" in text or "failed_when:" in text
                ):
                    _append(
                        findings,
                        project,
                        relative,
                        "unhandled-failure-suppression",
                        detect_silent_error_suppression(source, symbol_index=index)[1],
                    )
                if "variable-use-before-definition" in enabled and (
                    "register:" in text or "set_fact:" in text
                ):
                    _append(
                        findings,
                        project,
                        relative,
                        "variable-use-before-definition",
                        detect_variable_use_before_definition(source, symbol_index=index)[1],
                    )
                if "unnecessary-set-fact" in enabled and "set_fact:" in text:
                    _append(
                        findings,
                        project,
                        relative,
                        "unnecessary-set-fact",
                        unnecessary_set_fact_details(source, symbol_index=index) or [],
                    )
                scanned_files += 1
            except Exception as exc:  # preserve diagnostics instead of aborting corpus scan
                failed_files.append(
                    {"project": project, "file": relative, "error": repr(exc)}
                )
        _repository_documents.cache_clear()
        del index
        gc.collect()
        print(
            f"Scanned {number}/{len(repositories)} repositories: {project} "
            f"({len(selected)} files, {len(findings) - before} findings)",
            flush=True,
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fields = ["project", "file", "line", "concept_id", "variable", "message"]
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(findings)
    counts = Counter(item["concept_id"] for item in findings)
    payload = {
        "repositories": len(repositories),
        "selected_files": scanned_files,
        "finding_count": len(findings),
        "rule_counts": dict(sorted(counts.items())),
        "enabled_rules": sorted(enabled),
        "failed_files": failed_files,
    }
    args.summary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2), flush=True)


if __name__ == "__main__":
    main()
