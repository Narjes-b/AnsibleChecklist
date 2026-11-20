#!/usr/bin/env python3
"""Verify split/commit coverage of V0.0.7 threshold source observations.

This audit verifies source identity/schema fields. It does not interpret or
report metric values/predictions, and does not open historical reviewer labels.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


OBSERVATION_COLUMNS = {"project", "commit_sha", "metric_id", "rule_id", "unit"}
MAP_COLUMNS = {
    "metric_id",
    "human_condition_id",
    "rule_id",
    "source_object_unit",
    "object_identity_fields",
}
TIMEOUT_REPOSITORY = "encapsulate-xyz/cosmos-ansible"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        header = list(reader.fieldnames or [])
        if not header or len(header) != len(set(header)):
            raise ValueError(f"missing or duplicate CSV header: {path}")
        rows = []
        for line_number, row in enumerate(reader, start=2):
            if None in row:
                raise ValueError(f"extra CSV cells at {path}:{line_number}")
            rows.append({key: value or "" for key, value in row.items() if key is not None})
        return header, rows


def audit_threshold_source(
    observations_path: Path,
    benchmark_manifest_path: Path,
    split_path: Path,
    run_status_path: Path,
    condition_map_path: Path,
    *,
    expected_calibration_repositories: int = 144,
    expected_heldout_repositories: int = 62,
    timeout_repository: str = TIMEOUT_REPOSITORY,
) -> dict[str, Any]:
    """Check source checksum, metric map, frozen split, and exact run commits."""
    failures: list[str] = []
    benchmark = json.loads(benchmark_manifest_path.read_text(encoding="utf-8"))
    split_header, split_rows = _read_csv(split_path)
    status_header, status_rows = _read_csv(run_status_path)
    map_header, map_rows = _read_csv(condition_map_path)

    for column in {"repository", "split"}:
        if column not in split_header:
            failures.append(f"split CSV missing required column {column}")
    for column in {"repository", "commit_sha", "overall_status", "scan_status"}:
        if column not in status_header:
            failures.append(f"run status CSV missing required column {column}")
    for column in MAP_COLUMNS:
        if column not in map_header:
            failures.append(f"condition map missing required column {column}")

    split_by_repository: dict[str, str] = {}
    for row in split_rows:
        repository = row.get("repository", "")
        if not repository or repository in split_by_repository:
            failures.append("split CSV has a missing or duplicate repository")
            continue
        split_by_repository[repository] = row.get("split", "")
    split_counts = Counter(split_by_repository.values())
    if split_counts != Counter({"calibration": expected_calibration_repositories, "heldout": expected_heldout_repositories}):
        failures.append(f"repository split counts differ from frozen targets: {dict(split_counts)}")

    status_by_repository: dict[str, dict[str, str]] = {}
    for row in status_rows:
        repository = row.get("repository", "")
        if not repository or repository in status_by_repository:
            failures.append("frozen run status has a missing or duplicate repository")
            continue
        status_by_repository[repository] = row
    if not status_by_repository:
        failures.append("frozen run status is empty")

    condition_map: dict[str, dict[str, str]] = {}
    for row in map_rows:
        metric = row.get("metric_id", "")
        if not metric or metric in condition_map:
            failures.append("threshold condition map has a missing or duplicate metric")
            continue
        condition_map[metric] = row

    expected_observation_hash = benchmark.get("artifacts", {}).get("observations.csv.gz")
    actual_observation_hash = sha256_file(observations_path)
    if actual_observation_hash != expected_observation_hash:
        failures.append("threshold observations hash differs from benchmark manifest")

    expected_metrics = set(benchmark.get("candidate_thresholds", {}))
    map_metrics = set(condition_map)
    if map_metrics != expected_metrics:
        failures.append("threshold condition map metric IDs differ from benchmark manifest")

    row_count = 0
    observed_metrics: set[str] = set()
    observed_projects: set[str] = set()
    commits_by_project: dict[str, set[str]] = defaultdict(set)
    metric_schema: dict[str, set[tuple[str, str]]] = defaultdict(set)
    missing_identity_by_metric: Counter[str] = Counter()
    missing_run_status: set[str] = set()
    commit_mismatches: set[str] = set()
    metric_metadata_mismatches: set[str] = set()
    try:
        with gzip.open(observations_path, "rt", encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            header = set(reader.fieldnames or [])
            if not OBSERVATION_COLUMNS.issubset(header):
                failures.append(f"threshold observations missing columns: {sorted(OBSERVATION_COLUMNS - header)}")
            for row in reader:
                row_count += 1
                project = row.get("project", "") or ""
                commit_sha = row.get("commit_sha", "") or ""
                metric = row.get("metric_id", "") or ""
                rule_id = row.get("rule_id", "") or ""
                unit = row.get("unit", "") or ""
                observed_metrics.add(metric)
                observed_projects.add(project)
                commits_by_project[project].add(commit_sha)
                metric_schema[metric].add((rule_id, unit))

                run_row = status_by_repository.get(project)
                if run_row is None:
                    missing_run_status.add(project)
                elif commit_sha != run_row.get("commit_sha", ""):
                    commit_mismatches.add(project)

                mapping = condition_map.get(metric)
                if mapping:
                    expected_rule_id = mapping.get("rule_id", "").removeprefix("ansibleguard/")
                    if rule_id != expected_rule_id or unit != mapping.get("source_object_unit"):
                        metric_metadata_mismatches.add(metric)
                    for identity_field in mapping.get("object_identity_fields", "").split("+"):
                        if not identity_field or not row.get(identity_field, ""):
                            missing_identity_by_metric[metric] += 1
                            break
    except (OSError, UnicodeError, csv.Error) as error:
        failures.append(f"cannot read threshold observations: {error}")

    if row_count != benchmark.get("observation_count"):
        failures.append(f"observation row count differs from manifest: {row_count}")
    if len(observed_projects) != benchmark.get("repository_count"):
        failures.append(f"project count differs from manifest: {len(observed_projects)}")
    if observed_metrics != expected_metrics or observed_metrics != map_metrics:
        failures.append("observed metric IDs, candidate-threshold IDs, and condition-map IDs do not reconcile")
    if observed_projects != set(status_by_repository):
        failures.append("observed project set differs from frozen run status repository set")
    if not set(split_by_repository).issubset(observed_projects):
        failures.append("one or more frozen split repositories are absent from threshold observations")
    if missing_run_status:
        failures.append(f"threshold observations lack frozen run status for {len(missing_run_status)} projects")
    if metric_metadata_mismatches:
        failures.append(f"metric/rule/unit differs from condition map for metrics: {sorted(metric_metadata_mismatches)}")
    if commit_mismatches:
        failures.append(f"threshold observation commits differ from frozen run for {len(commit_mismatches)} projects")
    multi_commit = sorted(project for project, commits in commits_by_project.items() if len(commits) != 1)
    if multi_commit:
        failures.append(f"threshold observations do not have exactly one commit per project: {len(multi_commit)}")
    schema_mismatches = {
        metric: sorted(schema)
        for metric, schema in metric_schema.items()
        if metric in condition_map
        and schema != {
            (
                condition_map[metric].get("rule_id", "").removeprefix("ansibleguard/"),
                condition_map[metric].get("source_object_unit", ""),
            )
        }
    }
    if schema_mismatches:
        failures.append("one or more metrics contain inconsistent rule/unit metadata")
    if missing_identity_by_metric:
        failures.append(f"source-object identity fields are missing for metrics: {sorted(missing_identity_by_metric)}")

    out_of_split_projects = sorted(observed_projects - set(split_by_repository))
    if out_of_split_projects != [timeout_repository]:
        failures.append(f"out-of-split projects differ from the known timeout: {out_of_split_projects}")
    timeout_row = status_by_repository.get(timeout_repository, {})
    timeout_scan_status = timeout_row.get("scan_status", "")
    if timeout_scan_status != "timeout":
        failures.append(f"known extra project does not have timeout scan status: {timeout_scan_status!r}")

    return {
        "schema_version": 1,
        "created_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "passed": not failures,
        "failures": failures,
        "scope": "source identity/schema audit only; metric values and predictions are not analyzed and historical reviewer-label files are not opened",
        "artifacts": {
            "observations": {"path": str(observations_path), "sha256": actual_observation_hash, "rows": row_count},
            "benchmark_manifest": {"path": str(benchmark_manifest_path), "sha256": sha256_file(benchmark_manifest_path)},
            "repository_split": {"path": str(split_path), "sha256": sha256_file(split_path)},
            "run_status": {"path": str(run_status_path), "sha256": sha256_file(run_status_path)},
            "condition_map": {"path": str(condition_map_path), "sha256": sha256_file(condition_map_path)},
        },
        "counts": {
            "observations": row_count,
            "metrics": len(observed_metrics),
            "human_condition_families": len({row.get("human_condition_id", "") for row in condition_map.values()}),
            "projects": len(observed_projects),
            "frozen_split_repositories": len(split_by_repository),
            "calibration_repositories": split_counts.get("calibration", 0),
            "heldout_repositories": split_counts.get("heldout", 0),
            "out_of_split_projects": out_of_split_projects,
            "commit_mismatches": len(commit_mismatches),
            "missing_run_status": len(missing_run_status),
            "multi_commit_projects": len(multi_commit),
        },
    }


def write_report(output_dir: Path, report: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "threshold-source-audit.json"
    md_path = output_dir / "THRESHOLD_SOURCE_AUDIT.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    counts = report["counts"]
    lines = [
        "# V0.0.7 threshold source audit",
        "",
        f"Audit time: `{report['created_at_utc']}`",
        f"Result: **{'PASS' if report['passed'] else 'FAIL'}**",
        "",
        report["scope"],
        "",
        "## Verified population identity",
        "",
        f"- Threshold source rows: {counts['observations']:,}.",
        f"- Metrics mapped to human-condition families: {counts['metrics']} metrics / {counts['human_condition_families']} families.",
        f"- Project identities in source: {counts['projects']}; frozen split: {counts['frozen_split_repositories']} repositories ({counts['calibration_repositories']} calibration / {counts['heldout_repositories']} heldout).",
        f"- Commit mismatches: {counts['commit_mismatches']}; missing run-status joins: {counts['missing_run_status']}; multi-commit projects: {counts['multi_commit_projects']}.",
        f"- Projects outside the frozen split: {', '.join(counts['out_of_split_projects']) or 'none'} (the known timed-out repository is excluded).",
        "",
        "## Use boundary",
        "",
        "This verifies that threshold observations can be joined to the frozen repository split and run commits. It does not generate any threshold sample, inspect metric values/predictions, or consume historical reviewer labels. The exact execution order still requires agreement-pilot closeout and codebook freeze before generating calibration threshold batches; heldout observations remain unopened for human review until final freeze.",
        "",
    ]
    if report["failures"]:
        lines.extend(["## Failures", "", *[f"- {failure}" for failure in report["failures"]], ""])
    md_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--validation-dir", type=Path, default=Path("study/validation-v007-human"))
    parser.add_argument("--threshold-dir", type=Path, default=Path("study/threshold-benchmark-v007"))
    parser.add_argument("--run-dir", type=Path, default=Path("study/runs/v007-full-repro-2026"))
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()
    root = args.root.resolve()

    def resolve(path: Path) -> Path:
        return path if path.is_absolute() else root / path

    validation_dir = resolve(args.validation_dir)
    threshold_dir = resolve(args.threshold_dir)
    run_dir = resolve(args.run_dir)
    report = audit_threshold_source(
        threshold_dir / "observations.csv.gz",
        threshold_dir / "benchmark-manifest.json",
        validation_dir / "splits/repository-split.csv",
        run_dir / "tables/repository-execution-status.csv",
        validation_dir / "threshold-human-condition-map.csv",
    )
    write_report(resolve(args.output_dir) if args.output_dir else validation_dir, report)
    print(json.dumps({"passed": report["passed"], "failures": report["failures"], "counts": report["counts"]}, indent=2, sort_keys=True))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
