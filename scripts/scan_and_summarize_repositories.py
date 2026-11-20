#!/usr/bin/env python3
"""Scan every collected repository and export one wide study-summary CSV.

The CSV contains one row per repository plus a final ``__ALL__`` row.  It
combines the frozen file-classification manifest with AnsibleGuard's canonical
occurrences and run metadata.  Column prefixes make the counted population
explicit (for example ``selected_artifact_tasks`` and
``finding_category_security``).
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
import json
import os
from pathlib import Path
import re

from ansibleguard.profiles import PROFILE_NAMES
from ansibleguard.report.findings import finding_category

try:
    from scripts.run_study_pilot import (
        classification_manifest_path,
        load_collected,
        output_path,
        run_row,
    )
except ModuleNotFoundError:  # Direct execution: python scripts/<this-file>.py
    from run_study_pilot import (  # type: ignore[no-redef]
        classification_manifest_path,
        load_collected,
        output_path,
        run_row,
    )


DEFAULT_MANIFEST = Path("study/manifests/github-v2-final-frozen.csv")
DEFAULT_CLASSIFICATIONS = Path("study/manifests/file-classification")
DEFAULT_SNAPSHOTS = Path("study/snapshots/technical-full-v2")
DEFAULT_LOGS = Path("study/logs")
DEFAULT_OUTPUT = Path("study/results/all-repositories-summary.csv")

IDENTITY_FIELDS = (
    "project",
    "commit_sha",
    "repository_path",
    "snapshot_path",
    "scan_status",
    "scan_error",
    "profile",
    "ansible_lint_status",
    "gitleaks_status",
)
BASE_COUNT_FIELDS = (
    "repositories",
    "manifest_yaml_files",
    "manifest_yaml_loc",
    "selected_files",
    "selected_loc",
    "primary_ansibleguard_files",
    "paper_comparable_files",
    "processed_files",
    "structurally_analyzed_files",
    "diagnostics_total",
    "raw_findings",
    "canonical_occurrences",
    "canonical_uncertain_occurrences",
    "canonical_non_uncertain_occurrences",
    "symbol_definitions",
    "symbol_variables",
)
COUNT_PREFIXES = (
    "manifest_parse_",
    "manifest_document_",
    "manifest_class_",
    "manifest_artifact_",
    "selected_parse_",
    "selected_document_",
    "selected_class_",
    "selected_artifact_",
    "scan_parse_",
    "scan_document_",
    "scan_structural_",
    "file_state_",
    "diagnostic_status_",
    "diagnostic_stage_",
    "severity_",
    "provider_",
    "finding_category_",
    "finding_concept_",
    "confirmed_finding_concept_",
    "finding_semantic_status_",
    "finding_rule_",
    "finding_file_class_",
    "finding_artifact_",
    "symbol_kind_",
)


def available_memory_mb() -> int | None:
    """Return best-effort available physical memory without extra packages."""
    try:
        pages = os.sysconf("SC_AVPHYS_PAGES")
        page_size = os.sysconf("SC_PAGE_SIZE")
        return int(pages * page_size / (1024 * 1024))
    except (AttributeError, OSError, ValueError):
        return None


def resolve_jobs(
    requested, workload: int, memory_per_job_mb: int = 1024,
    *, cpu_count=None, memory_mb=None,
) -> int:
    """Resolve explicit/automatic concurrency under CPU and RAM budgets."""
    if workload <= 0:
        return 1
    if str(requested).lower() != "auto":
        try:
            jobs = int(requested)
        except (TypeError, ValueError) as exc:
            raise ValueError("--jobs must be a positive integer or 'auto'") from exc
        if jobs < 1:
            raise ValueError("--jobs must be at least 1")
        return min(jobs, workload)
    cpus = max(1, int(cpu_count or os.cpu_count() or 1))
    available = memory_mb if memory_mb is not None else available_memory_mb()
    memory_jobs = (
        max(1, int(available) // max(1, memory_per_job_mb))
        if available is not None else cpus
    )
    return max(1, min(workload, cpus, memory_jobs))


def run_repository_jobs(items, jobs, worker):
    """Execute repository units concurrently and return input-stable results."""
    indexed = list(enumerate(items))
    if not indexed:
        return []
    results = {}
    with ThreadPoolExecutor(max_workers=jobs) as executor:
        futures = {
            executor.submit(worker, item): index for index, item in indexed
        }
        for future in as_completed(futures):
            results[futures[future]] = future.result()
    return [results[index] for index, _item in indexed]


def _key(value: object) -> str:
    """Normalize an output label into a stable CSV column suffix."""
    text = str(value or "unknown").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text).strip("_")
    return text or "unknown"


def _truthy(value: object) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y"}


def _load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return default


def _items(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("items"), list):
        return payload["items"]
    return []


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def _increment(row: dict, prefix: str, value: object, amount: int = 1) -> None:
    field = f"{prefix}{_key(value)}"
    row[field] = int(row.get(field, 0)) + amount


def _manifest_counts(row: dict, manifest_path: Path):
    rows = _read_csv(manifest_path)
    selected = []
    for item in rows:
        loc = int(item.get("loc") or 0)
        row["manifest_yaml_files"] += 1
        row["manifest_yaml_loc"] += loc
        _increment(row, "manifest_parse_", item.get("parse_status"))
        _increment(row, "manifest_document_", item.get("document_type"))
        _increment(row, "manifest_class_", item.get("file_class"))
        _increment(
            row,
            "manifest_artifact_",
            item.get("ansible_artifact_kind") or item.get("document_type"),
        )
        if not _truthy(item.get("included")):
            continue
        selected.append(item)
        row["selected_files"] += 1
        row["selected_loc"] += loc
        row["primary_ansibleguard_files"] += int(
            _truthy(item.get("primary_ansibleguard_cohort"))
        )
        row["paper_comparable_files"] += int(
            _truthy(item.get("paper_comparable_cohort"))
        )
        _increment(row, "selected_parse_", item.get("parse_status"))
        _increment(row, "selected_document_", item.get("document_type"))
        _increment(row, "selected_class_", item.get("file_class"))
        _increment(
            row,
            "selected_artifact_",
            item.get("ansible_artifact_kind") or item.get("document_type"),
        )
    return {item.get("path", "").replace("\\", "/"): item for item in selected}


def summarize_snapshot(
    manifest_row: dict[str, str],
    snapshot: Path,
    classification_manifest: Path,
    scan_status: str,
    scan_error: str = "",
) -> dict:
    """Return one flat, numeric summary row for a repository snapshot."""
    row = {
        "project": manifest_row.get("project", ""),
        "commit_sha": manifest_row.get("commit_sha", ""),
        "repository_path": manifest_row.get("repository_path", ""),
        "snapshot_path": str(snapshot),
        "scan_status": scan_status,
        "scan_error": scan_error,
        "profile": "",
        "ansible_lint_status": "",
        "gitleaks_status": "",
        "repositories": 1,
        **{field: 0 for field in BASE_COUNT_FIELDS if field != "repositories"},
    }
    selected_by_path = _manifest_counts(row, classification_manifest)

    metadata = _load_json(snapshot / "run_metadata.json", {})
    row["profile"] = metadata.get("profile", {}).get("name", "")
    tools = metadata.get("tools", {})
    row["ansible_lint_status"] = tools.get("ansible_lint", "")
    row["gitleaks_status"] = tools.get("gitleaks", "")
    scope = metadata.get("analysis_scope", {}).get("internal", {})
    file_states = metadata.get("file_states", {})
    row["processed_files"] = int(
        scope.get("processed_files")
        if scope.get("processed_files") is not None
        else sum(int(value or 0) for value in file_states.values())
    )
    row["structurally_analyzed_files"] = int(
        scope.get("structurally_analyzed_files")
        if scope.get("structurally_analyzed_files") is not None
        else int(file_states.get("analyzed") or 0)
    )
    for state, count in file_states.items():
        _increment(row, "file_state_", state, int(count or 0))
    symbols = metadata.get("symbol_index", {})
    row["symbol_definitions"] = int(symbols.get("definition_count") or 0)
    row["symbol_variables"] = int(symbols.get("variable_count") or 0)
    for kind, count in symbols.get("kinds", {}).items():
        _increment(row, "symbol_kind_", kind, int(count or 0))

    diagnostics = _items(
        _load_json(snapshot / "summary" / "diagnostics.json", [])
    ) or _items(_load_json(snapshot / "diagnostics.json", []))
    row["diagnostics_total"] = len(diagnostics)
    for diagnostic in diagnostics:
        _increment(row, "diagnostic_status_", diagnostic.get("status"))
        _increment(row, "diagnostic_stage_", diagnostic.get("stage"))

    summary_path = snapshot / "summary" / "summary.csv"
    if not summary_path.is_file():
        summary_path = snapshot / "summary.csv"
    if summary_path.is_file():
        for item in _read_csv(summary_path):
            file = str(item.get("file") or "").replace("\\", "/")
            if file not in selected_by_path:
                continue
            _increment(row, "scan_parse_", item.get("parse_status"))
            _increment(row, "scan_document_", item.get("document_type"))
            _increment(row, "scan_structural_", item.get("structural_status"))

    findings = _items(_load_json(snapshot / "raw" / "findings.json", []))
    if not findings:
        findings = _items(_load_json(snapshot / "findings.json", []))
    row["raw_findings"] = len(findings)
    for item in findings:
        _increment(row, "provider_", item.get("provider", "ansibleguard"))
        _increment(row, "finding_rule_", item.get("rule_id"))

    occurrences = _items(
        _load_json(snapshot / "canonical" / "occurrences.json", [])
    )
    if not occurrences:
        occurrences = _items(_load_json(snapshot / "occurrences.json", []))
    row["canonical_occurrences"] = len(occurrences)
    for item in occurrences:
        semantic_status = item.get("semantic_status") or "NOT_APPLICABLE"
        uncertain = semantic_status == "UNCERTAIN"
        row[
            "canonical_uncertain_occurrences"
            if uncertain else "canonical_non_uncertain_occurrences"
        ] += 1
        _increment(row, "finding_semantic_status_", semantic_status)
        _increment(row, "severity_", item.get("severity"))
        _increment(row, "finding_category_", finding_category(item))
        _increment(row, "finding_concept_", item.get("concept_id"))
        if not uncertain:
            _increment(
                row, "confirmed_finding_concept_", item.get("concept_id")
            )
        selected_file = selected_by_path.get(
            str(item.get("file") or "").replace("\\", "/"), {}
        )
        _increment(
            row,
            "finding_file_class_",
            selected_file.get("file_class") or "project_or_external",
        )
        _increment(
            row,
            "finding_artifact_",
            selected_file.get("ansible_artifact_kind")
            or selected_file.get("document_type")
            or "project_or_external",
        )
    return row


def _is_count_field(field: str) -> bool:
    return field in BASE_COUNT_FIELDS or field.startswith(COUNT_PREFIXES)


def total_row(rows: list[dict]) -> dict:
    total = {field: "" for field in IDENTITY_FIELDS}
    total.update(
        {
            "project": "__ALL__",
            "scan_status": "aggregate",
            "repositories": len(rows),
        }
    )
    for row in rows:
        for field, value in row.items():
            if _is_count_field(field) and field != "repositories":
                total[field] = int(total.get(field) or 0) + int(value or 0)
    total["repositories"] = len(rows)
    return total


def _ordered_fields(rows: list[dict]) -> list[str]:
    present = {field for row in rows for field in row}
    fields = [field for field in IDENTITY_FIELDS if field in present]
    fields.extend(field for field in BASE_COUNT_FIELDS if field in present)
    fields.extend(sorted(present - set(fields)))
    return fields


def write_summary(rows: list[dict], output: Path) -> None:
    """Atomically publish repository rows and their aggregate total."""
    output.parent.mkdir(parents=True, exist_ok=True)
    published_rows = [*rows, total_row(rows)]
    fields = _ordered_fields(published_rows)
    temporary = output.with_name(f".{output.name}.tmp")
    with temporary.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in published_rows:
            writer.writerow(
                {
                    field: row.get(field, 0 if _is_count_field(field) else "")
                    for field in fields
                }
            )
    temporary.replace(output)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "Scan all collected repositories and write one per-repository plus "
            "aggregate findings/statistics CSV. Existing valid scans are reused."
        )
    )
    parser.add_argument("manifest", nargs="?", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_SNAPSHOTS)
    parser.add_argument("--logs-dir", type=Path, default=DEFAULT_LOGS)
    parser.add_argument(
        "--file-manifests-dir", type=Path, default=DEFAULT_CLASSIFICATIONS
    )
    parser.add_argument("--profile", choices=PROFILE_NAMES, default="technical-full")
    parser.add_argument("--limit", type=int)
    parser.add_argument(
        "--jobs",
        default="1",
        help="Repository worker processes: positive integer or 'auto' (default: 1).",
    )
    parser.add_argument(
        "--memory-per-job-mb",
        type=int,
        default=1024,
        help="RAM budget used by --jobs auto (default: 1024 MiB per repository).",
    )
    parser.add_argument(
        "--repository-timeout",
        type=float,
        default=3600,
        help="maximum seconds for one repository worker (default: 3600)",
    )
    parser.add_argument(
        "--aggregate-only",
        action="store_true",
        help="Do not run AnsibleGuard; summarize snapshots that already exist.",
    )
    parser.add_argument(
        "--rescan-existing",
        action="store_true",
        help="Run AnsibleGuard again even when a compatible snapshot exists.",
    )
    parser.add_argument(
        "--stop-on-error",
        action="store_true",
        help="Stop at the first failed repository instead of recording and continuing.",
    )
    parser.add_argument(
        "--require-research-container",
        action="store_true",
        help=(
            "Refuse to scan unless immutable image and build-commit provenance "
            "are present in the environment."
        ),
    )
    args = parser.parse_args(argv)

    if args.require_research_container:
        missing = [
            name for name in (
                "ANSIBLEGUARD_RESEARCH_IMAGE_DIGEST",
                "ANSIBLEGUARD_BUILD_GIT_SHA",
            )
            if not os.environ.get(name)
            or os.environ.get(name) == "unknown"
        ]
        if missing:
            parser.error(
                "research-container provenance is missing: " + ", ".join(missing)
            )

    manifest_rows = load_collected(args.manifest)
    if args.limit is not None:
        manifest_rows = manifest_rows[: args.limit]
    try:
        jobs = resolve_jobs(
            args.jobs, len(manifest_rows), args.memory_per_job_mb
        )
    except ValueError as exc:
        parser.error(str(exc))
    print(
        f"Scheduling {len(manifest_rows)} repositories with {jobs} worker(s).",
        flush=True,
    )

    def process(manifest_row):
        project = manifest_row["project"]
        sha = manifest_row["commit_sha"]
        snapshot = output_path(args.output_root, project, sha, args.profile)
        classification = classification_manifest_path(
            args.file_manifests_dir, project, sha
        )
        scan_status = "existing"
        scan_error = ""
        try:
            if not classification.is_file():
                raise RuntimeError(
                    f"classification manifest not found: {classification}"
                )
            if args.aggregate_only:
                if not (snapshot / "run_metadata.json").is_file():
                    raise RuntimeError(f"snapshot not found: {snapshot}")
            else:
                scan_status, snapshot = run_row(
                    manifest_row,
                    args.output_root,
                    args.logs_dir,
                    skip_existing=not args.rescan_existing,
                    file_manifests_dir=args.file_manifests_dir,
                    profile=args.profile,
                    repository_timeout=args.repository_timeout,
                )
            summary = summarize_snapshot(
                manifest_row, snapshot, classification, scan_status
            )
        except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as exc:
            if args.stop_on_error:
                raise
            scan_error = f"{type(exc).__name__}: {exc}"
            print(f"  failed: {scan_error}", flush=True)
            summary = {
                "project": project,
                "commit_sha": sha,
                "repository_path": manifest_row.get("repository_path", ""),
                "snapshot_path": str(snapshot),
                "scan_status": "failed",
                "scan_error": scan_error,
                "profile": args.profile,
                "ansible_lint_status": "",
                "gitleaks_status": "",
                "repositories": 1,
                **{
                    field: 0
                    for field in BASE_COUNT_FIELDS
                    if field != "repositories"
                },
            }
        return summary

    rows = run_repository_jobs(manifest_rows, jobs, process)
    write_summary(rows, args.output)
    for index, summary in enumerate(rows, 1):
        print(
            f"[{index}/{len(rows)}] {summary['project']}: "
            f"{summary['scan_status']}",
            flush=True,
        )
    print(f"Done: {len(rows)} repositories summarized in {args.output}")


if __name__ == "__main__":
    main()
