#!/usr/bin/env python3
"""Run the v0.0.5 frozen-corpus study with isolated repository failures.

This wrapper intentionally uses v0.0.5-specific output locations so a new
semantic-engine run cannot be mixed with historical v0.0.3/v0.0.4 snapshots by
accident.  The frozen repository cohort remains the same; callers may choose a
historical classification-manifest directory for a paired same-population run
or the v0.0.5 classification directory for native v0.0.5 selection.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from ansibleguard.profiles import PROFILE_NAMES

try:
    from scripts.run_study_pilot import (
        classification_manifest_path,
        load_collected,
        output_path,
        run_row,
    )
    from scripts.scan_and_summarize_repositories import (
        BASE_COUNT_FIELDS,
        resolve_jobs,
        run_repository_jobs,
        summarize_snapshot,
        write_summary,
    )
except ModuleNotFoundError:  # Direct execution: python scripts/<this-file>.py
    from run_study_pilot import (  # type: ignore[no-redef]
        classification_manifest_path,
        load_collected,
        output_path,
        run_row,
    )
    from scan_and_summarize_repositories import (  # type: ignore[no-redef]
        BASE_COUNT_FIELDS,
        resolve_jobs,
        run_repository_jobs,
        summarize_snapshot,
        write_summary,
    )


DEFAULT_MANIFEST = Path("study/manifests/github-v2-final-frozen.csv")
DEFAULT_CLASSIFICATIONS = Path("study/manifests/file-classification-v005")
DEFAULT_SNAPSHOTS = Path("study/snapshots/technical-full-v005")
DEFAULT_LOGS = Path("study/logs/technical-full-v005")
DEFAULT_OUTPUT = Path("study/results/v005/all-repositories-summary.csv")


def _failed_summary(manifest_row, snapshot, profile, exc):
    return {
        "project": manifest_row.get("project", ""),
        "commit_sha": manifest_row.get("commit_sha", ""),
        "repository_path": manifest_row.get("repository_path", ""),
        "snapshot_path": str(snapshot),
        "scan_status": "failed",
        "scan_error": f"{type(exc).__name__}: {exc}",
        "profile": profile,
        "ansible_lint_status": "",
        "gitleaks_status": "",
        "repositories": 1,
        **{
            field: 0
            for field in BASE_COUNT_FIELDS
            if field != "repositories"
        },
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "Run the v0.0.5 research scan with version-specific destinations "
            "and repository-level failure isolation."
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
        help="Repository workers: positive integer or 'auto' (default: 1).",
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
        help="Maximum seconds for one repository worker (default: 3600).",
    )
    parser.add_argument(
        "--aggregate-only",
        action="store_true",
        help="Do not scan; summarize snapshots that already exist.",
    )
    parser.add_argument(
        "--rescan-existing",
        action="store_true",
        help="Run AnsibleGuard again even when compatible output already exists.",
    )
    parser.add_argument(
        "--stop-on-error",
        action="store_true",
        help="Re-raise the first repository exception instead of recording it.",
    )
    parser.add_argument(
        "--allow-failed-repositories",
        action="store_true",
        help="Return exit status 0 after recording failed repository units.",
    )
    parser.add_argument(
        "--ansible-lint-scope",
        choices=("v004-target", "v005-selected"),
        default="v005-selected",
        help=(
            "Use v005-selected for the native architecture or v004-target "
            "for a provider-comparable historical replay."
        ),
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
            name
            for name in (
                "ANSIBLEGUARD_RESEARCH_IMAGE_DIGEST",
                "ANSIBLEGUARD_BUILD_GIT_SHA",
            )
            if not os.environ.get(name) or os.environ.get(name) == "unknown"
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
        f"Scheduling {len(manifest_rows)} v0.0.5 repositories with {jobs} worker(s).",
        flush=True,
    )
    print(f"  classifications: {args.file_manifests_dir}", flush=True)
    print(f"  snapshots:       {args.output_root}", flush=True)
    print(f"  summary:         {args.output}", flush=True)

    def process(manifest_row):
        project = manifest_row["project"]
        sha = manifest_row["commit_sha"]
        snapshot = output_path(args.output_root, project, sha, args.profile)
        classification = classification_manifest_path(
            args.file_manifests_dir, project, sha
        )
        try:
            if not classification.is_file():
                raise RuntimeError(
                    f"classification manifest not found: {classification}"
                )
            if args.aggregate_only:
                if not (snapshot / "run_metadata.json").is_file():
                    raise RuntimeError(f"snapshot not found: {snapshot}")
                scan_status = "existing"
            else:
                scan_status, snapshot = run_row(
                    manifest_row,
                    args.output_root,
                    args.logs_dir,
                    skip_existing=not args.rescan_existing,
                    file_manifests_dir=args.file_manifests_dir,
                    profile=args.profile,
                    repository_timeout=args.repository_timeout,
                    ansible_lint_scope=args.ansible_lint_scope,
                )
            return summarize_snapshot(
                manifest_row, snapshot, classification, scan_status
            )
        except Exception as exc:
            # This is the repository isolation boundary.  One malformed or
            # inaccessible checkout must not abort the other frozen units.
            # KeyboardInterrupt/SystemExit remain uncaught because they derive
            # from BaseException rather than Exception.
            if args.stop_on_error:
                raise
            summary = _failed_summary(
                manifest_row, snapshot, args.profile, exc
            )
            print(
                f"  failed {project}: {summary['scan_error']}",
                flush=True,
            )
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
    failed = sum(row.get("scan_status") == "failed" for row in rows)
    if failed:
        print(
            f"Recorded {failed} failed repository unit(s); inspect scan_error "
            "before interpreting aggregate results.",
            flush=True,
        )
    return 1 if failed and not args.allow_failed_repositories else 0


if __name__ == "__main__":
    raise SystemExit(main())
