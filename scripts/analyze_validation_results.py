#!/usr/bin/env python3
"""Aggregate canonical AnsibleGuard repository results for paper reporting.

The script deliberately counts both canonical occurrences and their underlying
detectors. This prevents cross-tool overlap from being mistaken for additional
independent defects while retaining provider-coverage measurements.
"""

from __future__ import annotations

import argparse
from collections import Counter
import csv
import json
from pathlib import Path


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_occurrences(path: Path) -> list[dict]:
    payload = load_json(path)
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and payload.get("kind") == "canonical-occurrences":
        return payload.get("items", [])
    raise ValueError(f"unsupported occurrence document: {path}")


def result_directories(root: Path):
    for metadata in sorted(root.glob("*/*/run_metadata.json")):
        yield metadata.parent


def selected_loc(metadata: dict) -> int | str:
    """Return LOC for included manifest rows, or an empty value if unavailable."""
    raw_manifest = metadata.get("file_selection", {}).get("manifest")
    if not raw_manifest:
        return ""
    manifest = Path(raw_manifest)
    if not manifest.is_file():
        return ""
    with manifest.open(newline="", encoding="utf-8") as stream:
        return sum(
            int(row.get("loc") or 0)
            for row in csv.DictReader(stream)
            if row.get("included", "").lower() == "true"
        )


def summarize_result(cohort: str, root: Path, result: Path):
    metadata = load_json(result / "run_metadata.json")
    occurrences = load_occurrences(result / "occurrences.json")
    diagnostics_path = result / "diagnostics.json"
    diagnostics = load_json(diagnostics_path) if diagnostics_path.is_file() else []
    provider_counts = Counter()
    rule_counts = Counter()
    cross_provider = 0
    same_provider_multi_detector = 0
    for occurrence in occurrences:
        providers = set()
        detectors = occurrence.get("detectors", [])
        for detector in detectors:
            provider = detector.get("provider", "unknown")
            providers.add(provider)
            provider_counts[provider] += 1
        if len(providers) > 1:
            cross_provider += 1
        elif len(detectors) > 1:
            same_provider_multi_detector += 1
        rule_counts[occurrence.get("concept_id", "unknown")] += 1

    relative = result.relative_to(root)
    project = relative.parts[0].replace("__", "/")
    commit_sha = relative.parts[1]
    selection = metadata.get("file_selection", {})
    tools = metadata.get("tools", {})
    row = {
        "cohort": cohort,
        "project": project,
        "commit_sha": commit_sha,
        "included_files": selection.get("included_files", ""),
        "included_loc": selected_loc(metadata),
        "raw_detectors": sum(provider_counts.values()),
        "canonical_occurrences": len(occurrences),
        "cross_provider_occurrences": cross_provider,
        "same_provider_multi_detector_occurrences": same_provider_multi_detector,
        "diagnostics": len(diagnostics),
        "ansibleguard_detectors": provider_counts["ansibleguard"],
        "ansible_lint_detectors": provider_counts["ansible-lint"],
        "gitleaks_detectors": provider_counts["gitleaks"],
        "ansible_lint_status": tools.get("ansible_lint", "unknown"),
        "gitleaks_status": tools.get("gitleaks", "unknown"),
        "repository_path": metadata.get("target", ""),
        "result_path": str(result),
    }
    return row, rule_counts, occurrences


def select_review_candidates(candidates: list[dict], limit: int) -> list[dict]:
    """Select deterministically while preferring repository diversity."""
    by_project = {}
    for candidate in candidates:
        by_project.setdefault(candidate["project"], []).append(candidate)
    selected = []
    while by_project and len(selected) < limit:
        for project in sorted(tuple(by_project)):
            selected.append(by_project[project].pop(0))
            if not by_project[project]:
                del by_project[project]
            if len(selected) == limit:
                break
    return selected


def write_csv(path: Path, rows: list[dict]):
    if not rows:
        raise ValueError("cannot write an empty result table")
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cohort",
        action="append",
        required=True,
        metavar="LABEL=RESULT_ROOT",
        help="repeat for every cohort to aggregate",
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--review-rule",
        action="append",
        default=[],
        help="canonical concept ID to include in the manual-review sample",
    )
    parser.add_argument("--samples-per-rule", type=int, default=5)
    args = parser.parse_args(argv)

    rows = []
    rules = Counter()
    review_pool = {rule: [] for rule in args.review_rule}
    for value in args.cohort:
        if "=" not in value:
            parser.error(f"invalid --cohort value: {value!r}")
        label, raw_root = value.split("=", 1)
        root = Path(raw_root)
        for result in result_directories(root):
            row, result_rules, occurrences = summarize_result(label, root, result)
            rows.append(row)
            rules.update(result_rules)
            for occurrence in occurrences:
                concept_id = occurrence.get("concept_id", "unknown")
                if concept_id not in review_pool:
                    continue
                review_pool[concept_id].append(
                    {
                        "cohort": label,
                        "project": row["project"],
                        "commit_sha": row["commit_sha"],
                        "concept_id": concept_id,
                        "occurrence_id": occurrence.get("occurrence_id", ""),
                        "file": occurrence.get("file", "."),
                        "line": occurrence.get("line", 1),
                        "providers": "+".join(
                            sorted(
                                {
                                    detector.get("provider", "unknown")
                                    for detector in occurrence.get("detectors", [])
                                }
                            )
                        ),
                        "message": occurrence.get("message", ""),
                        "repository_path": row["repository_path"],
                    }
                )
    if not rows:
        parser.error("no run_metadata.json files found in the supplied cohort roots")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "repositories.csv", rows)
    rule_rows = [
        {"concept_id": rule, "canonical_occurrences": count}
        for rule, count in rules.most_common()
    ]
    write_csv(args.output_dir / "rules.csv", rule_rows)

    numeric = (
        "included_files",
        "included_loc",
        "raw_detectors",
        "canonical_occurrences",
        "cross_provider_occurrences",
        "same_provider_multi_detector_occurrences",
        "diagnostics",
        "ansibleguard_detectors",
        "ansible_lint_detectors",
        "gitleaks_detectors",
    )
    totals = {key: sum(int(row[key] or 0) for row in rows) for key in numeric}
    totals["repositories"] = len(rows)
    totals["raw_to_canonical_reduction"] = (
        totals["raw_detectors"] - totals["canonical_occurrences"]
    )
    totals["raw_to_canonical_reduction_percent"] = round(
        100 * totals["raw_to_canonical_reduction"] / totals["raw_detectors"], 2
    )
    totals["all_external_tools_completed"] = all(
        row["ansible_lint_status"] == "completed"
        and row["gitleaks_status"] == "completed"
        for row in rows
    )
    payload = {
        "schema_version": 1,
        "method": "canonical occurrences with detector-level provider counts",
        "totals": totals,
        "repositories": rows,
        "rules": dict(rules.most_common()),
    }
    (args.output_dir / "aggregate.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    if review_pool:
        review_rows = []
        for rule in args.review_rule:
            review_rows.extend(
                select_review_candidates(review_pool[rule], args.samples_per_rule)
            )
        if review_rows:
            write_csv(args.output_dir / "review_candidates.csv", review_rows)


if __name__ == "__main__":
    main()
