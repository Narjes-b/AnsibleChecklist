#!/usr/bin/env python3
"""Run, validate, aggregate, report, and compare an N-repository study."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import statistics
import subprocess
import sys
import time
from typing import Any

import yaml

from ansibleguard import __version__
from ansibleguard.profiles import REVIEW_RULES
from ansibleguard.report.findings import finding_category

try:
    from scripts.run_study_pilot import (
        classification_manifest_path,
        load_collected,
        output_path,
        run_row,
    )
    from scripts.scan_and_summarize_repositories import summarize_snapshot, write_summary
    from scripts.compare_validation_versions import compare_version_occurrences
    from scripts.study_reporting import (
        bar_chart,
        heatmap,
        markdown_table,
        optional_png,
        pie_chart,
        read_csv,
        write_csv,
    )
except ModuleNotFoundError:  # direct execution
    from run_study_pilot import (  # type: ignore[no-redef]
        classification_manifest_path,
        load_collected,
        output_path,
        run_row,
    )
    from scan_and_summarize_repositories import (  # type: ignore[no-redef]
        summarize_snapshot,
        write_summary,
    )
    from compare_validation_versions import compare_version_occurrences  # type: ignore[no-redef]
    from study_reporting import (  # type: ignore[no-redef]
        bar_chart,
        heatmap,
        markdown_table,
        optional_png,
        pie_chart,
        read_csv,
        write_csv,
    )


SCHEMA_VERSION = 1
OUTPUT_ARTIFACTS = {
    "run_metadata.json": ("run_metadata.json",),
    # v0.0.7 writes flat canonical artifacts. Older pipeline fixtures and
    # historical runs used raw/ and canonical/ subdirectories.
    "findings.json": ("findings.json", "raw/findings.json"),
    "occurrences.json": ("occurrences.json", "canonical/occurrences.json"),
}
RUN_DIRS = (
    "input", "status", "repositories", "logs", "aggregate", "tables",
    "charts", "report", "labels", "comparison",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def load_json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return default


def items(path: Path) -> list[dict]:
    payload = load_json(path, {})
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict) and isinstance(payload.get("items"), list):
        return [item for item in payload["items"] if isinstance(item, dict)]
    return []


def snapshot_artifact(snapshot: Path, name: str) -> Path:
    """Resolve current flat and historical nested output layouts."""
    candidates = OUTPUT_ARTIFACTS[name]
    for relative in candidates:
        path = snapshot / relative
        if path.is_file():
            return path
    return snapshot / candidates[0]


def resolve_path(value: str | Path, root: Path) -> Path:
    path = Path(value).expanduser()
    return path if path.is_absolute() else root / path


def resolve_python(value: str | Path, root: Path) -> Path:
    """Resolve a configured interpreter path, tolerating Unix/Windows venv layout differences."""
    path = resolve_path(value, root)
    if path.is_file():
        return path
    venv_dir = path.parent.parent
    for candidate in (venv_dir / "Scripts" / "python.exe", venv_dir / "bin" / "python"):
        if candidate.is_file():
            return candidate
    return path


def load_config(path: Path) -> dict:
    path = Path(path).resolve()
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("study configuration must be a YAML mapping")
    for section in ("run", "tool", "repositories", "output"):
        if not isinstance(payload.get(section), dict):
            raise ValueError(f"missing configuration section: {section}")
    if not payload["run"].get("id"):
        raise ValueError("run.id is required")
    if not payload["repositories"].get("manifest"):
        raise ValueError("repositories.manifest is required")
    if not payload["repositories"].get("file_manifests_dir"):
        raise ValueError("repositories.file_manifests_dir is required")
    try:
        import jsonschema
    except ImportError:
        jsonschema = None
    if jsonschema is not None:
        schema_path = Path.cwd() / "study" / "schemas" / "study-pipeline-config.schema.json"
        if schema_path.is_file():
            jsonschema.validate(payload, json.loads(schema_path.read_text(encoding="utf-8")))
    payload["_config_path"] = str(path)
    payload["_root"] = str(Path.cwd().resolve())
    return payload


def run_dir(config: dict) -> Path:
    root = resolve_path(config["output"].get("root", "study/runs"), Path(config["_root"]))
    return root / str(config["run"]["id"])


def manifest_path(config: dict) -> Path:
    return resolve_path(config["repositories"]["manifest"], Path(config["_root"]))


def classifications_dir(config: dict) -> Path:
    return resolve_path(config["repositories"]["file_manifests_dir"], Path(config["_root"]))


def selected_rows(config: dict) -> list[dict[str, str]]:
    rows = load_collected(manifest_path(config))
    limit = config["repositories"].get("limit")
    if limit is not None:
        if int(limit) < 1:
            raise ValueError("repositories.limit must be positive")
        rows = rows[: int(limit)]
    # The manifest's own repository_path column is a snapshot from whatever
    # machine/environment last regenerated the manifest (e.g. recorded during
    # discovery on a different host) and is not necessarily where this run's
    # own acquire() step actually checks repositories out (checkout_root).
    # acquire() already computes its destination independently from
    # checkout_root, not from this column; override it here too so preflight
    # (which does read this column) agrees with where repositories actually
    # are for *this* run, on *this* machine.
    checkout_root_value = config.get("repositories", {}).get("checkout_root")
    if checkout_root_value:
        checkout_root = resolve_path(checkout_root_value, Path(config["_root"]))
        for row in rows:
            project = row.get("project", "")
            if project:
                row["repository_path"] = str(checkout_root.joinpath(*project.split("/")))
    return rows


def git_resolve(reference: str, root: Path) -> str:
    return subprocess.run(
        ["git", "rev-parse", reference], cwd=root, check=True,
        capture_output=True, text=True, timeout=30,
    ).stdout.strip()


def tool_version(python: Path) -> str:
    result = subprocess.run(
        [str(python), "-c", "import ansibleguard; print(ansibleguard.__version__)"],
        check=True, capture_output=True, text=True, timeout=30,
    )
    return result.stdout.strip()


def build_identity(config: dict) -> dict:
    root = Path(config["_root"])
    tool = config["tool"]
    configured_python = tool.get("python")
    # sys.executable is portable across activated virtual environments,
    # GitHub Actions, and the research container.  A configured path remains
    # supported for explicitly isolated installed-tool executions.
    python = (
        resolve_python(configured_python, root)
        # Do not resolve this path: a virtual environment commonly exposes
        # ``.venv/bin/python`` as a symlink to the base interpreter, and
        # resolving it discards the virtual environment's site-packages.
        if configured_python else Path(sys.executable)
    )
    expected_version = str(tool.get("version", "")).strip()
    actual_version = tool_version(python)
    if expected_version and actual_version != expected_version:
        raise ValueError(
            f"configured tool version {expected_version} does not match {python}: {actual_version}"
        )
    reference = str(tool.get("git_ref", "HEAD"))
    mode = str(tool.get("mode", "current-worktree"))
    resolved_sha = ""
    if mode == "current-worktree":
        resolved_sha = git_resolve(reference, root)
        head = git_resolve("HEAD", root)
        if resolved_sha != head:
            raise ValueError(
                "current-worktree mode can only execute HEAD; use a dedicated "
                "environment and tool.mode=installed for another version"
            )
        dirty = bool(subprocess.run(
            ["git", "status", "--porcelain"], cwd=root, check=True,
            capture_output=True, text=True, timeout=30,
        ).stdout.strip())
        if dirty and not bool(tool.get("allow_dirty", False)):
            raise ValueError(
                "current worktree is dirty; commit the implementation or set "
                "tool.allow_dirty=true only for a development run"
            )
    else:
        resolved_sha = str(tool.get("commit_sha", ""))
        if not resolved_sha:
            raise ValueError("installed tool mode requires tool.commit_sha provenance")
    return {
        "mode": mode,
        "python": str(python),
        "version": actual_version,
        "git_ref": reference,
        "commit_sha": resolved_sha,
        "working_tree_dirty": dirty if mode == "current-worktree" else None,
    }


def prepare(config: dict) -> dict:
    destination = run_dir(config)
    for name in RUN_DIRS:
        (destination / name).mkdir(parents=True, exist_ok=True)
    config_path = Path(config["_config_path"])
    copied_config = destination / "run-config.yaml"
    if copied_config.exists() and sha256_file(copied_config) != sha256_file(config_path):
        raise ValueError(f"run ID already exists with different configuration: {destination}")
    if not copied_config.exists():
        shutil.copy2(config_path, copied_config)
    rows = selected_rows(config)
    if not rows:
        raise ValueError("manifest contains no collected repositories")
    expected = config["repositories"].get("expected_count")
    if expected is not None and len(rows) != int(expected):
        raise ValueError(f"expected {expected} repositories, selected {len(rows)}")
    identity = build_identity(config)
    for row in rows:
        classification = classification_manifest_path(
            classifications_dir(config), row.get("project", ""), row.get("commit_sha", "")
        )
        row["classification_manifest"] = str(classification)
        row["classification_manifest_sha256"] = sha256_file(classification) if classification.is_file() else ""
    resolved_manifest = destination / "input" / "repositories.csv"
    fields = list(dict.fromkeys(key for row in rows for key in row))
    write_csv(resolved_manifest, rows, fields)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "kind": "ansibleguard-study-run",
        "run_id": config["run"]["id"],
        "created_at_utc": utc_now(),
        "repository_count": len(rows),
        "profile": config["run"].get("profile", "technical-full"),
        "ansible_lint_scope": config["run"].get("ansible_lint_scope", "v005-selected"),
        "configuration_sha256": sha256_file(copied_config),
        "source_manifest": str(manifest_path(config)),
        "source_manifest_sha256": sha256_file(manifest_path(config)),
        "resolved_manifest": str(resolved_manifest),
        "resolved_manifest_sha256": sha256_file(resolved_manifest),
        "file_manifests_dir": str(classifications_dir(config)),
        "tool": identity,
        "state": "prepared",
    }
    existing = load_json(destination / "run-manifest.json", {})
    if existing:
        for key in ("configuration_sha256", "source_manifest_sha256", "repository_count"):
            if existing.get(key) != payload.get(key):
                raise ValueError(f"existing run manifest differs for {key}: {destination}")
        if existing.get("tool", {}).get("commit_sha") != identity["commit_sha"]:
            raise ValueError(
                f"run ID already belongs to tool commit "
                f"{existing.get('tool', {}).get('commit_sha')}: {destination}"
            )
        payload["created_at_utc"] = existing.get("created_at_utc", payload["created_at_utc"])
        for key in ("state", "scanned_at_utc", "completed_at_utc", "report"):
            if key in existing:
                payload[key] = existing[key]
    atomic_json(destination / "run-manifest.json", payload)
    return payload


def preflight(config: dict) -> list[dict]:
    destination = run_dir(config)
    if not (destination / "run-manifest.json").is_file():
        prepare(config)
    rows = read_csv(destination / "input" / "repositories.csv")
    seen_projects, seen_paths = set(), set()
    results = []
    for row in rows:
        project = row.get("project", "")
        repository = Path(row.get("repository_path", ""))
        expected_sha = row.get("commit_sha", "")
        errors = []
        if not project or project in seen_projects:
            errors.append("missing-or-duplicate-project")
        if not expected_sha or not re.fullmatch(r"[0-9a-f]{40}", expected_sha):
            errors.append("invalid-commit-sha")
        if not repository.is_dir():
            errors.append("repository-missing")
        elif str(repository.resolve()) in seen_paths:
            errors.append("duplicate-repository-path")
        else:
            try:
                actual = subprocess.run(
                    ["git", "rev-parse", "HEAD"], cwd=repository, check=True,
                    capture_output=True, text=True, timeout=30,
                ).stdout.strip()
                if actual != expected_sha:
                    errors.append("repository-head-mismatch")
            except (OSError, subprocess.SubprocessError):
                errors.append("repository-git-check-failed")
        classification = classification_manifest_path(
            classifications_dir(config), project, expected_sha
        )
        if not classification.is_file():
            errors.append("classification-manifest-missing")
        seen_projects.add(project)
        if repository.exists():
            seen_paths.add(str(repository.resolve()))
        results.append({
            "project": project,
            "commit_sha": expected_sha,
            "repository_path": str(repository),
            "classification_manifest": str(classification),
            "status": "passed" if not errors else "failed",
            "errors": ";".join(errors),
        })
    write_csv(destination / "status" / "preflight.csv", results)
    summary = {
        "schema_version": SCHEMA_VERSION,
        "checked_at_utc": utc_now(),
        "repositories": len(results),
        "passed": sum(row["status"] == "passed" for row in results),
        "failed": sum(row["status"] == "failed" for row in results),
        "status": "passed" if results and all(row["status"] == "passed" for row in results) else "failed",
    }
    atomic_json(destination / "status" / "preflight.json", summary)
    return results


def scan(config: dict) -> list[dict]:
    destination = run_dir(config)
    checks = preflight(config)
    failed = [row for row in checks if row["status"] != "passed"]
    if failed:
        # Only tolerate failures already explicitly excluded and documented at
        # the acquisition stage (acquire()'s --max-acquisition-failures), for
        # the same known, structural, non-retriable reason (a frozen commit
        # SHA no longer fetchable from the remote) -- never a blanket
        # tolerance. Any failure here that ISN'T one of those pre-excluded
        # projects (e.g. a corrupt checkout, wrong SHA on a repo that should
        # have succeeded) still aborts the run.
        excluded_path = destination / "status" / "acquisition-excluded.json"
        excluded_projects = {
            row["project"] for row in load_json(excluded_path, {}).get("excluded_projects", [])
        }
        # A project that failed acquisition can surface at preflight as
        # repository-missing (no directory at all), repository-git-check-failed
        # (a stale, content-less directory from an aborted clone attempt), or
        # repository-head-mismatch (a stale partial checkout at the wrong
        # revision) -- all are consequences of the same already-documented
        # acquisition failure, not independent new problems, so any preflight
        # error is tolerated for a project already on the exclusion record.
        unexplained = [row for row in failed if row["project"] not in excluded_projects]
        if unexplained:
            raise RuntimeError(
                f"preflight failed for {len(unexplained)} repositories with no acquisition-stage "
                f"exclusion on record; see status/preflight.csv"
            )
    passed_projects = {row["project"] for row in checks if row["status"] == "passed"}
    rows = [row for row in read_csv(destination / "input" / "repositories.csv") if row["project"] in passed_projects]
    workers = max(1, int(config["run"].get("workers", 1)))
    timeout = config["run"].get("repository_timeout", 3600)
    profile = config["run"].get("profile", "technical-full")
    lint_scope = config["run"].get("ansible_lint_scope", "v005-selected")
    resume = bool(config["run"].get("resume", True))
    stop_on_error = bool(config["run"].get("stop_on_error", False))
    python = build_identity(config)["python"]

    def execute(row):
        started = time.monotonic()
        project = row["project"]
        try:
            status, snapshot = run_row(
                row,
                destination / "repositories",
                destination / "logs",
                skip_existing=resume,
                file_manifests_dir=classifications_dir(config),
                profile=profile,
                repository_timeout=float(timeout) if timeout is not None else None,
                ansible_lint_scope=lint_scope,
                python_executable=python,
            )
            return {
                "project": project,
                "commit_sha": row["commit_sha"],
                "status": status,
                "snapshot_path": str(snapshot),
                "duration_seconds": round(time.monotonic() - started, 3),
                "error": "",
            }
        except Exception as exc:  # repository boundary: preserve all failures
            if stop_on_error:
                raise
            snapshot = output_path(
                destination / "repositories", project, row["commit_sha"], profile
            )
            message = f"{type(exc).__name__}: {exc}"
            return {
                "project": project,
                "commit_sha": row.get("commit_sha", ""),
                "status": "timeout" if "timed out after" in message.lower() else "failed",
                "snapshot_path": str(snapshot),
                "duration_seconds": round(time.monotonic() - started, 3),
                "error": message,
            }

    results_by_index = {}
    with ThreadPoolExecutor(max_workers=min(workers, len(rows))) as executor:
        futures = {executor.submit(execute, row): index for index, row in enumerate(rows)}
        for future in as_completed(futures):
            result = future.result()
            results_by_index[futures[future]] = result
            print(f"[{len(results_by_index)}/{len(rows)}] {result['project']}: {result['status']}", flush=True)
    results = [results_by_index[index] for index in range(len(rows))]
    write_csv(destination / "status" / "repository-status.csv", results)
    run_manifest = load_json(destination / "run-manifest.json", {})
    run_manifest.update({"state": "scanned", "scanned_at_utc": utc_now()})
    atomic_json(destination / "run-manifest.json", run_manifest)
    return results


def snapshot_for(config: dict, row: dict) -> Path:
    return output_path(
        run_dir(config) / "repositories", row["project"], row["commit_sha"],
        config["run"].get("profile", "technical-full"),
    )


def validate(config: dict) -> dict:
    destination = run_dir(config)
    rows = read_csv(destination / "input" / "repositories.csv")
    required_providers = config.get("providers", {})
    seen_occurrences, seen_findings = set(), set()
    observed_rule_hashes, observed_tool_commits = set(), set()
    details = []
    for row in rows:
        snapshot = snapshot_for(config, row)
        errors, warnings = [], []
        for artifact in OUTPUT_ARTIFACTS:
            if not snapshot_artifact(snapshot, artifact).is_file():
                errors.append(f"missing:{artifact}")
        metadata = load_json(snapshot / "run_metadata.json", {})
        if metadata:
            if metadata.get("profile", {}).get("name") != config["run"].get("profile", "technical-full"):
                errors.append("profile-mismatch")
            resolved = metadata.get("source", {}).get("resolved_sha")
            if resolved and resolved != row["commit_sha"]:
                errors.append("source-sha-mismatch")
            requested_classification_hash = row.get("classification_manifest_sha256", "")
            actual_classification_hash = metadata.get("file_selection", {}).get("manifest_sha256", "")
            if requested_classification_hash and actual_classification_hash != requested_classification_hash:
                errors.append("classification-manifest-hash-mismatch")
            rule_hash = metadata.get("profile", {}).get("rules_sha256")
            if rule_hash:
                observed_rule_hashes.add(rule_hash)
            reproducibility = metadata.get("reproducibility", {})
            tool_commit = reproducibility.get("ansibleguard_git_sha")
            if tool_commit:
                observed_tool_commits.add(tool_commit)
                expected_tool_commit = load_json(destination / "run-manifest.json", {}).get("tool", {}).get("commit_sha")
                if expected_tool_commit and tool_commit != expected_tool_commit:
                    errors.append("tool-commit-mismatch")
        tools = metadata.get("tools", {}) if isinstance(metadata, dict) else {}
        for provider, required in (
            ("ansible_lint", required_providers.get("require_ansible_lint", True)),
            ("gitleaks", required_providers.get("require_gitleaks", True)),
        ):
            provider_status = str(tools.get(provider, "missing"))
            if provider_status != "completed":
                (errors if required else warnings).append(f"{provider}:{provider_status}")
        occurrences = items(snapshot_artifact(snapshot, "occurrences.json"))
        findings = items(snapshot_artifact(snapshot, "findings.json"))
        duplicate_occurrences = 0
        duplicate_findings = 0
        for item in occurrences:
            identifier = item.get("occurrence_id")
            key = (row["project"], identifier)
            if not identifier or key in seen_occurrences:
                duplicate_occurrences += 1
            seen_occurrences.add(key)
            if int(item.get("line") or 1) < 1:
                errors.append("invalid-line-number")
        for item in findings:
            identifier = item.get("finding_id")
            key = (row["project"], identifier)
            if not identifier or key in seen_findings:
                duplicate_findings += 1
            seen_findings.add(key)
        if duplicate_occurrences:
            errors.append(f"duplicate-occurrences:{duplicate_occurrences}")
        if duplicate_findings:
            errors.append(f"duplicate-findings:{duplicate_findings}")
        status = "failed" if errors else ("partial" if warnings else "complete")
        details.append({
            "project": row["project"], "commit_sha": row["commit_sha"],
            "status": status, "raw_findings": len(findings),
            "canonical_occurrences": len(occurrences),
            "ansible_lint_status": tools.get("ansible_lint", "missing"),
            "gitleaks_status": tools.get("gitleaks", "missing"),
            "errors": ";".join(dict.fromkeys(errors)),
            "warnings": ";".join(dict.fromkeys(warnings)),
        })
    write_csv(destination / "status" / "validation.csv", details)
    counts = Counter(row["status"] for row in details)
    result = {
        "schema_version": SCHEMA_VERSION,
        "validated_at_utc": utc_now(),
        "expected_repositories": len(rows),
        "repository_status_counts": dict(sorted(counts.items())),
        "complete": counts.get("complete", 0),
        "partial": counts.get("partial", 0),
        "failed": counts.get("failed", 0),
        "status": "passed" if details and counts.get("failed", 0) == 0 else "failed",
        "publication_ready": bool(details) and counts.get("complete", 0) == len(details),
        "observed_profile_rule_hashes": sorted(observed_rule_hashes),
        "observed_tool_commits": sorted(observed_tool_commits),
    }
    if len(observed_rule_hashes) > 1 or len(observed_tool_commits) > 1:
        result["status"] = "failed"
        result["cross_repository_identity_error"] = "inconsistent rule or tool identity"
    atomic_json(destination / "status" / "validation-report.json", result)
    return result


def _native_rule(item: dict) -> str:
    rules = item.get("native_rules") or []
    provider = str(item.get("canonical_provider") or item.get("provider") or "")
    if provider:
        provider_rules = sorted(
            str(rule) for rule in rules
            if str(rule).startswith(f"{provider}/")
        )
        if provider_rules:
            return provider_rules[0]
    return str(rules[0]) if rules else str(item.get("rule_id") or item.get("concept_id") or "unknown")


def _is_review_occurrence(item: dict) -> bool:
    concept = str(item.get("concept_id") or "")
    native_rules = {
        str(rule).removeprefix("ansibleguard/")
        for rule in (item.get("native_rules") or [])
    }
    return concept in REVIEW_RULES or bool(native_rules & REVIEW_RULES)


def aggregate(config: dict) -> dict:
    destination = run_dir(config)
    rows = read_csv(destination / "input" / "repositories.csv")
    validation_rows = (
        read_csv(destination / "status" / "validation.csv")
        if (destination / "status" / "validation.csv").is_file()
        else []
    )
    validation_by_project = {row["project"]: row for row in validation_rows}
    execution_rows = (
        read_csv(destination / "status" / "repository-status.csv")
        if (destination / "status" / "repository-status.csv").is_file()
        else []
    )
    execution_by_project = {row["project"]: row for row in execution_rows}
    repo_summaries, raw_rows, occurrence_rows = [], [], []
    for manifest_row in rows:
        snapshot = snapshot_for(config, manifest_row)
        metadata = load_json(snapshot / "run_metadata.json", {})
        classification = classification_manifest_path(
            classifications_dir(config), manifest_row["project"], manifest_row["commit_sha"]
        )
        try:
            summary = summarize_snapshot(manifest_row, snapshot, classification, "existing")
        except Exception as exc:
            summary = {
                "project": manifest_row["project"], "commit_sha": manifest_row["commit_sha"],
                "scan_status": "failed", "scan_error": f"{type(exc).__name__}: {exc}",
                "selected_files": 0, "selected_loc": 0, "raw_findings": 0,
                "canonical_occurrences": 0, "diagnostics_total": 0,
            }
        files = int(summary.get("selected_files") or 0)
        loc = int(summary.get("selected_loc") or 0)
        canonical = int(summary.get("canonical_occurrences") or 0)
        summary["canonical_per_100_files"] = round(canonical * 100 / files, 4) if files else ""
        summary["canonical_per_1000_loc"] = round(canonical * 1000 / loc, 4) if loc else ""
        execution = execution_by_project.get(manifest_row["project"], {})
        scan_status = execution.get("status", "")
        if scan_status and scan_status != "completed":
            # A failed or timed-out scan is an unavailable measurement. Keep
            # execution metadata, but never publish its synthesized zeros as
            # detector results.
            summary.update({
                "scan_status": scan_status,
                "scan_error": execution.get("error", ""),
                "raw_findings": "",
                "canonical_occurrences": "",
                "canonical_per_100_files": "",
                "canonical_per_1000_loc": "",
                "diagnostics_total": "",
            })
        repo_summaries.append(summary)
        for item in items(snapshot_artifact(snapshot, "findings.json")):
            provider = item.get("provider", "ansibleguard")
            provider_key = "ansible_lint" if provider == "ansible-lint" else provider
            provider_status = "completed" if provider == "ansibleguard" else metadata.get("tools", {}).get(provider_key, "missing") if isinstance(metadata, dict) else "missing"
            raw_rows.append({
                "run_id": config["run"]["id"], "project": manifest_row["project"],
                "commit_sha": manifest_row["commit_sha"], "profile": config["run"].get("profile", "technical-full"),
                "finding_id": item.get("finding_id", ""), "provider": provider,
                "provider_status": provider_status,
                "provider_comparison_eligible": provider_status == "completed",
                "rule_id": item.get("rule_id", ""), "file": item.get("file", ""),
                "line": item.get("line", 1), "severity": item.get("severity", ""),
                "message": item.get("message", ""),
            })
        for item in items(snapshot_artifact(snapshot, "occurrences.json")):
            provider = item.get("canonical_provider", "ansibleguard")
            provider_key = "ansible_lint" if provider == "ansible-lint" else provider
            provider_status = "completed" if provider == "ansibleguard" else metadata.get("tools", {}).get(provider_key, "missing") if isinstance(metadata, dict) else "missing"
            is_review = _is_review_occurrence(item)
            benchmark_population = (
                "review"
                if is_review
                else "whole-repository-gitleaks"
                if provider == "gitleaks"
                else "selected-ansible-source"
            )
            occurrence_rows.append({
                "run_id": config["run"]["id"], "tool_version": config["tool"].get("version", __version__),
                "project": manifest_row["project"], "commit_sha": manifest_row["commit_sha"],
                "profile": config["run"].get("profile", "technical-full"),
                "occurrence_id": item.get("occurrence_id", ""), "concept_id": item.get("concept_id", "unknown"),
                "rule_id": _native_rule(item), "category": item.get("finding_category") or finding_category(item),
                "severity": item.get("severity", "unknown"), "certainty": item.get("semantic_status", "NOT_APPLICABLE"),
                "confidence": item.get("confidence", "unknown"), "provider": provider,
                "provider_status": provider_status,
                "provider_comparison_eligible": provider_status == "completed",
                "file": item.get("file", ""), "line": item.get("line", 1),
                "scan_mode": "review" if is_review else item.get("scan_mode", "source"),
                "benchmark_population": benchmark_population,
                "analysis_population": item.get("analysis_population", ""),
                "source_population": item.get("source_population", ""),
                "semantic_key": item.get("semantic_key", ""),
                "native_rules": json.dumps(item.get("native_rules", []), separators=(",", ":")),
                "policy": item.get("policy", ""), "actionability": item.get("actionability", ""),
                "resolution_status": item.get("resolution_status", "DETECTOR_RESULT"),
                "resolution_scope": item.get("resolution_scope", "rule-static"),
                "uncertainty_sources": json.dumps(
                    item.get("uncertainty_sources", []), separators=(",", ":")
                ),
                "resolution_evidence": json.dumps(
                    item.get("resolution_evidence", {}), separators=(",", ":")
                ),
                "message": item.get("message", ""),
            })
    write_summary(repo_summaries, destination / "aggregate" / "repository-summary.csv")
    write_csv(destination / "aggregate" / "all-raw-findings.csv", raw_rows)
    write_csv(destination / "aggregate" / "all-canonical-occurrences.csv", occurrence_rows)
    analyzable_projects = [
        row["project"]
        for row in rows
        if validation_by_project.get(row["project"], {}).get("status") != "failed"
    ]
    provider_projects = {
        "ansibleguard": analyzable_projects,
        "ansible-lint": [
            project for project in analyzable_projects
            if validation_by_project.get(project, {}).get("ansible_lint_status") == "completed"
        ],
        "gitleaks": [
            project for project in analyzable_projects
            if validation_by_project.get(project, {}).get("gitleaks_status") == "completed"
        ],
    }
    # A cross-provider comparison is valid only where every provider completed;
    # review-range rules describe Git history and are not a static-source
    # population, so they never enter provider-comparable tables.
    comparable_projects = [
        project for project in provider_projects["ansible-lint"]
        if project in set(provider_projects["gitleaks"])
    ]
    comparable_project_set = set(comparable_projects)
    comparable_occurrences = [
        row for row in occurrence_rows
        if row["provider_comparison_eligible"]
        and row["scan_mode"] != "review"
        and row["project"] in comparable_project_set
    ]
    internal_occurrences = [
        row for row in occurrence_rows if row["provider"] == "ansibleguard"
    ]
    review_occurrences = [row for row in occurrence_rows if row["scan_mode"] == "review"]
    static_occurrences = [row for row in occurrence_rows if row["scan_mode"] != "review"]
    internal_source_occurrences = [
        row for row in static_occurrences if row["provider"] == "ansibleguard"
    ]
    ansible_lint_occurrences = [
        row for row in static_occurrences if row["provider"] == "ansible-lint"
    ]
    gitleaks_occurrences = [
        row for row in static_occurrences if row["provider"] == "gitleaks"
    ]
    ansible_lint_comparable_occurrences = [
        row for row in ansible_lint_occurrences
        if row["provider_comparison_eligible"]
    ]
    gitleaks_comparable_occurrences = [
        row for row in gitleaks_occurrences
        if row["provider_comparison_eligible"]
    ]
    uncertain_occurrences = [
        row for row in occurrence_rows if row["certainty"] == "UNCERTAIN"
    ]
    write_csv(
        destination / "aggregate" / "all-provider-comparable-occurrences.csv",
        comparable_occurrences,
    )
    write_csv(
        destination / "aggregate" / "all-internal-occurrences.csv",
        internal_occurrences,
    )
    for name, population in (
        ("all-static-source-occurrences.csv", static_occurrences),
        ("all-internal-source-occurrences.csv", internal_source_occurrences),
        ("all-ansible-lint-occurrences.csv", ansible_lint_occurrences),
        ("all-ansible-lint-comparable-occurrences.csv", ansible_lint_comparable_occurrences),
        ("all-gitleaks-occurrences.csv", gitleaks_occurrences),
        ("all-gitleaks-comparable-occurrences.csv", gitleaks_comparable_occurrences),
        ("all-review-occurrences.csv", review_occurrences),
        ("all-uncertain-occurrences.csv", uncertain_occurrences),
    ):
        write_csv(destination / "aggregate" / name, population)

    per_project_provider = Counter(
        (row["project"], row["provider"]) for row in static_occurrences
    )
    per_project_review = Counter(row["project"] for row in review_occurrences)
    summaries_by_project = {row["project"]: row for row in repo_summaries}
    for project in analyzable_projects:
        summary = summaries_by_project[project]
        files = int(summary.get("selected_files") or 0)
        loc = int(summary.get("selected_loc") or 0)
        internal = per_project_provider[(project, "ansibleguard")]
        lint = per_project_provider[(project, "ansible-lint")]
        secrets = per_project_provider[(project, "gitleaks")]
        summary.update({
            "internal_source_occurrences": internal,
            "ansible_lint_occurrences": lint,
            "gitleaks_occurrences": secrets,
            "review_occurrences": per_project_review[project],
            "internal_source_per_100_files": round(internal * 100 / files, 4) if files else "",
            "internal_source_per_1000_selected_loc": round(internal * 1000 / loc, 4) if loc else "",
            "ansible_lint_per_1000_selected_loc": round(lint * 1000 / loc, 4) if loc else "",
        })
    # Re-write after adding population-specific counts and valid denominators.
    write_summary(repo_summaries, destination / "aggregate" / "repository-summary.csv")

    def grouped(
        field: str,
        name: str,
        source_rows=None,
        *,
        eligible_projects=None,
        normalize_selected_loc=False,
    ) -> list[dict]:
        source_rows = occurrence_rows if source_rows is None else source_rows
        eligible_projects = list(
            analyzable_projects if eligible_projects is None else eligible_projects
        )
        counter = Counter(row[field] or "unknown" for row in source_rows)
        project_counter = Counter(
            ((row[field] or "unknown"), row["project"]) for row in source_rows
        )
        projects = defaultdict(set)
        for row in source_rows:
            projects[row[field] or "unknown"].add(row["project"])
        result = []
        repository_count = len(eligible_projects)
        total = len(source_rows)
        total_loc = sum(
            int(summaries_by_project[project].get("selected_loc") or 0)
            for project in eligible_projects
            if project in summaries_by_project
        )
        for value, count in sorted(counter.items(), key=lambda item: (-item[1], item[0])):
            affected = len(projects[value])
            per_repository = [
                project_counter[(value, project)]
                for project in eligible_projects
            ]
            ordered = sorted(per_repository)
            midpoint = len(ordered) // 2
            lower = ordered[:midpoint]
            upper = ordered[midpoint + (len(ordered) % 2):]
            result.append({
                name: value, "findings": count,
                "share_percent": round(count * 100 / total, 2) if total else 0,
                "eligible_repositories": repository_count,
                "missing_repositories": len(rows) - repository_count,
                "repositories_affected": affected,
                "repository_prevalence_percent": round(affected * 100 / repository_count, 2) if repository_count else 0,
                "median_per_repository": round(statistics.median(ordered), 4) if ordered else 0,
                "q1_per_repository": round(statistics.median(lower), 4) if lower else (ordered[0] if ordered else 0),
                "q3_per_repository": round(statistics.median(upper), 4) if upper else (ordered[-1] if ordered else 0),
                "findings_per_1000_selected_loc": (
                    round(count * 1000 / total_loc, 4)
                    if normalize_selected_loc and total_loc else ""
                ),
            })
        return result

    category_rows = grouped("category", "category")
    rule_rows = grouped("rule_id", "rule_id")
    concept_rows = grouped("concept_id", "concept_id")
    resolution_rows = grouped("resolution_status", "resolution_status")
    severity_rows = grouped("severity", "severity")
    certainty_rows = grouped("certainty", "certainty")
    provider_rows = []
    for provider in ("ansibleguard", "ansible-lint", "gitleaks"):
        provider_population = [row for row in occurrence_rows if row["provider"] == provider]
        eligible_population = [
            row for row in provider_population
            if row["provider_comparison_eligible"]
        ]
        eligible = provider_projects[provider]
        affected = len({row["project"] for row in eligible_population})
        provider_rows.append({
            "provider": provider,
            "findings": len(provider_population),
            "eligible_findings": len(eligible_population),
            "share_percent": round(len(provider_population) * 100 / len(occurrence_rows), 2) if occurrence_rows else 0,
            "eligible_repositories": len(eligible),
            "missing_repositories": len(rows) - len(eligible),
            "repositories_affected": affected,
            "repository_prevalence_percent": round(affected * 100 / len(eligible), 2) if eligible else 0,
            "median_per_repository": "",
            "q1_per_repository": "",
            "q3_per_repository": "",
            "findings_per_1000_selected_loc": "",
        })
    for name, data in (
        ("category-summary.csv", category_rows), ("rule-summary.csv", rule_rows),
        ("concept-summary.csv", concept_rows),
        ("resolution-summary.csv", resolution_rows),
        ("severity-summary.csv", severity_rows), ("certainty-summary.csv", certainty_rows),
        ("provider-summary.csv", provider_rows),
    ):
        write_csv(destination / "aggregate" / name, data)
    for population, source_rows, eligible, normalize in (
        ("internal", internal_source_occurrences, provider_projects["ansibleguard"], True),
        ("ansible-lint", ansible_lint_comparable_occurrences, provider_projects["ansible-lint"], True),
        ("gitleaks", gitleaks_comparable_occurrences, provider_projects["gitleaks"], False),
        ("review", review_occurrences, analyzable_projects, False),
        ("provider-comparable", comparable_occurrences, comparable_projects, False),
    ):
        write_csv(
            destination / "aggregate" / f"category-summary-{population}.csv",
            grouped(
                "category", "category", source_rows,
                eligible_projects=eligible,
                normalize_selected_loc=normalize,
            ),
        )
        write_csv(
            destination / "aggregate" / f"rule-summary-{population}.csv",
            grouped(
                "rule_id", "rule_id", source_rows,
                eligible_projects=eligible,
                normalize_selected_loc=normalize,
            ),
        )
        write_csv(
            destination / "aggregate" / f"concept-summary-{population}.csv",
            grouped(
                "concept_id", "concept_id", source_rows,
                eligible_projects=eligible,
                normalize_selected_loc=normalize,
            ),
        )
    matrix_counter = Counter((row["project"], row["category"]) for row in occurrence_rows)
    categories = sorted({row["category"] for row in occurrence_rows})
    matrix_rows = []
    for manifest_row in rows:
        matrix_rows.append({
            "project": manifest_row["project"],
            **{category: matrix_counter[(manifest_row["project"], category)] for category in categories},
        })
    write_csv(destination / "aggregate" / "repository-category-matrix.csv", matrix_rows, ["project", *categories])
    internal_matrix_counter = Counter(
        (row["project"], row["category"]) for row in internal_source_occurrences
    )
    internal_categories = sorted({row["category"] for row in internal_source_occurrences})
    internal_matrix_rows = [
        {
            "project": project,
            **{
                category: internal_matrix_counter[(project, category)]
                for category in internal_categories
            },
        }
        for project in analyzable_projects
    ]
    write_csv(
        destination / "aggregate" / "repository-category-matrix-internal-source.csv",
        internal_matrix_rows,
        ["project", *internal_categories],
    )
    rules = sorted({row["rule_id"] for row in occurrence_rows})
    rule_counter = Counter((row["project"], row["rule_id"]) for row in occurrence_rows)
    rule_matrix_rows = [
        {"project": manifest_row["project"], **{rule: rule_counter[(manifest_row["project"], rule)] for rule in rules}}
        for manifest_row in rows
    ]
    write_csv(destination / "aggregate" / "repository-rule-matrix.csv", rule_matrix_rows, ["project", *rules])
    provider_health = []
    for provider, field in (("ansible-lint", "ansible_lint_status"), ("gitleaks", "gitleaks_status")):
        counts = Counter(row.get(field, "missing") or "missing" for row in validation_rows)
        provider_health.append({"provider": provider, **dict(sorted(counts.items())), "repositories": len(validation_rows)})
    write_csv(destination / "aggregate" / "provider-health.csv", provider_health)
    diagnostics_rows = [
        {"project": row.get("project", ""), "diagnostics": row.get("diagnostics_total", 0), "scan_status": row.get("scan_status", ""), "scan_error": row.get("scan_error", "")}
        for row in repo_summaries
    ]
    write_csv(destination / "aggregate" / "diagnostics-summary.csv", diagnostics_rows)
    result = {
        "schema_version": SCHEMA_VERSION, "run_id": config["run"]["id"],
        "repositories": len(rows), "analyzable_repositories": len(analyzable_projects),
        "failed_repositories": len(rows) - len(analyzable_projects),
        "raw_findings": len(raw_rows),
        "canonical_occurrences": len(occurrence_rows), "categories": len(category_rows),
        "rules": len(rule_rows), "generated_at_utc": utc_now(),
        "internal_occurrences": len(internal_occurrences),
        "internal_source_occurrences": len(internal_source_occurrences),
        "ansible_lint_occurrences": len(ansible_lint_occurrences),
        "ansible_lint_comparable_occurrences": len(ansible_lint_comparable_occurrences),
        "gitleaks_occurrences": len(gitleaks_occurrences),
        "gitleaks_comparable_occurrences": len(gitleaks_comparable_occurrences),
        "review_occurrences": len(review_occurrences),
        "uncertain_occurrences": len(uncertain_occurrences),
        "provider_comparable_occurrences": len(comparable_occurrences),
        "excluded_incomplete_provider_occurrences": len(occurrence_rows) - len(comparable_occurrences),
    }
    atomic_json(destination / "aggregate" / "aggregate-summary.json", result)
    return result


def report(config: dict) -> Path:
    destination = run_dir(config)
    aggregate_summary = load_json(destination / "aggregate" / "aggregate-summary.json")
    if not aggregate_summary:
        aggregate(config)
        aggregate_summary = load_json(destination / "aggregate" / "aggregate-summary.json")
    repository_rows = [row for row in read_csv(destination / "aggregate" / "repository-summary.csv") if row["project"] != "__ALL__"]
    category_rows = read_csv(destination / "aggregate" / "category-summary.csv")
    rule_rows = read_csv(destination / "aggregate" / "rule-summary.csv")
    concept_rows = read_csv(destination / "aggregate" / "concept-summary.csv")
    resolution_rows = read_csv(destination / "aggregate" / "resolution-summary.csv")
    severity_rows = read_csv(destination / "aggregate" / "severity-summary.csv")
    certainty_rows = read_csv(destination / "aggregate" / "certainty-summary.csv")
    provider_rows = read_csv(destination / "aggregate" / "provider-summary.csv")
    internal_category_rows = read_csv(destination / "aggregate" / "category-summary-internal.csv")
    internal_concept_rows = read_csv(destination / "aggregate" / "concept-summary-internal.csv")
    lint_category_rows = read_csv(destination / "aggregate" / "category-summary-ansible-lint.csv")
    gitleaks_category_rows = read_csv(destination / "aggregate" / "category-summary-gitleaks.csv")
    review_category_rows = read_csv(destination / "aggregate" / "category-summary-review.csv")
    comparable_category_rows = read_csv(destination / "aggregate" / "category-summary-provider-comparable.csv")
    provider_health = read_csv(destination / "aggregate" / "provider-health.csv")
    diagnostics_rows = read_csv(destination / "aggregate" / "diagnostics-summary.csv")
    validation = load_json(destination / "status" / "validation-report.json", {})
    charts = []
    for name, data, title in (
        # Category composition is reported for AnsibleGuard's own static-source
        # population; mixing providers and review-range rules would compare
        # incommensurable populations.
        ("findings-by-category.svg", internal_category_rows or category_rows,
         "AnsibleGuard static-source findings by category"),
        ("findings-by-severity.svg", severity_rows,
         "Severity, all providers and review rules combined (populations differ)"),
        ("findings-by-certainty.svg", certainty_rows,
         "Certainty, all providers combined (external findings default to CONFIRMED)"),
        ("findings-by-provider.svg", provider_rows,
         "Canonical findings by provider (provider populations differ)"),
    ):
        path = destination / "charts" / name
        key = next(key for key in data[0] if key not in {"findings", "share_percent", "repositories_affected", "repository_prevalence_percent"}) if data else ""
        pie_chart(path, [(row[key], float(row["findings"])) for row in data], title)
        charts.append(path)
    rule_chart = destination / "charts" / "top-rules.svg"
    bar_chart(rule_chart, [(row["rule_id"], float(row["findings"])) for row in rule_rows], "Top rules across all providers (populations differ; not validated defects)", limit=int(config.get("report", {}).get("top_rules", 25)))
    charts.append(rule_chart)
    concept_chart = destination / "charts" / "top-internal-concepts.svg"
    bar_chart(
        concept_chart,
        [(row["concept_id"], float(row["findings"])) for row in internal_concept_rows],
        "Top internal semantic concepts",
        limit=int(config.get("report", {}).get("top_rules", 25)),
    )
    charts.append(concept_chart)
    repo_chart = destination / "charts" / "normalized-internal-findings-by-repository.svg"
    density_rows = [row for row in repository_rows if row.get("internal_source_per_1000_selected_loc") not in {None, ""}]
    bar_chart(repo_chart, [(row["project"], float(row["internal_source_per_1000_selected_loc"])) for row in density_rows], "AnsibleGuard static-source findings per 1,000 selected LOC (analyzable repositories only)", limit=int(config.get("report", {}).get("top_repositories", 25)))
    charts.append(repo_chart)
    matrix_rows = read_csv(destination / "aggregate" / "repository-category-matrix-internal-source.csv")
    categories = [field for field in (matrix_rows[0].keys() if matrix_rows else []) if field != "project"]
    selected_repos = [row["project"] for row in sorted(matrix_rows, key=lambda row: -sum(int(row.get(cat) or 0) for cat in categories))]
    matrix = {(row["project"], category): int(row.get(category) or 0) for row in matrix_rows for category in categories}
    heatmap_path = destination / "charts" / "repository-category-heatmap.svg"
    heatmap(heatmap_path, selected_repos, categories, matrix, "Repository × category findings")
    charts.append(heatmap_path)
    health_chart = destination / "charts" / "provider-completeness.svg"
    bar_chart(
        health_chart,
        [
            (f"{row['provider']} complete", float(row.get("completed") or 0))
            for row in provider_health
        ],
        "Provider completeness",
    )
    charts.append(health_chart)
    pngs = optional_png(charts) if "png" in config.get("report", {}).get("formats", []) else []

    overview = [
        {"metric": "Run", "value": aggregate_summary["run_id"]},
        {"metric": "Tool version", "value": config["tool"].get("version", __version__)},
        {"metric": "Repositories", "value": aggregate_summary["repositories"]},
        {"metric": "Analyzable repositories", "value": aggregate_summary["analyzable_repositories"]},
        {"metric": "Failed repositories", "value": aggregate_summary["failed_repositories"]},
        {"metric": "Raw findings", "value": aggregate_summary["raw_findings"]},
        {"metric": "Canonical occurrences", "value": aggregate_summary["canonical_occurrences"]},
        {"metric": "Internal occurrences", "value": aggregate_summary["internal_occurrences"]},
        {"metric": "Internal static-source occurrences", "value": aggregate_summary["internal_source_occurrences"]},
        {"metric": "ansible-lint occurrences", "value": aggregate_summary["ansible_lint_occurrences"]},
        {"metric": "ansible-lint comparable occurrences", "value": aggregate_summary["ansible_lint_comparable_occurrences"]},
        {"metric": "GitLeaks whole-repository occurrences", "value": aggregate_summary["gitleaks_occurrences"]},
        {"metric": "GitLeaks comparable occurrences", "value": aggregate_summary["gitleaks_comparable_occurrences"]},
        {"metric": "Review-only occurrences", "value": aggregate_summary["review_occurrences"]},
        {"metric": "Uncertain occurrences", "value": aggregate_summary["uncertain_occurrences"]},
        {"metric": "Provider-comparable occurrences", "value": aggregate_summary["provider_comparable_occurrences"]},
        {"metric": "Excluded incomplete-provider occurrences", "value": aggregate_summary["excluded_incomplete_provider_occurrences"]},
        {"metric": "Rules observed", "value": aggregate_summary["rules"]},
        {"metric": "Validation", "value": validation.get("status", "not-run")},
    ]
    table_documents = {
        "overview.md": "# Study overview\n\n" + markdown_table(overview, ["metric", "value"]),
        "categories.md": "# Category statistics\n\n" + markdown_table(category_rows, list(category_rows[0]) if category_rows else ["category"]),
        "rules.md": "# Rule statistics\n\n" + markdown_table(rule_rows, list(rule_rows[0]) if rule_rows else ["rule_id"]),
        "concepts.md": "# Semantic concept statistics\n\n" + markdown_table(concept_rows, list(concept_rows[0]) if concept_rows else ["concept_id"]),
        "resolutions.md": "# Static resolution statistics\n\n" + markdown_table(resolution_rows, list(resolution_rows[0]) if resolution_rows else ["resolution_status"]),
        "repositories.md": "# Repository statistics\n\n" + markdown_table(repository_rows, list(repository_rows[0]) if repository_rows else ["project"]),
        "providers.md": "# Provider contribution and health\n\n## Contribution\n\n" + markdown_table(provider_rows, list(provider_rows[0]) if provider_rows else ["provider"]) + "\n## Health\n\n" + markdown_table(provider_health, list(provider_health[0]) if provider_health else ["provider"]),
        "analysis-populations.md": "# Analysis populations\n\n## Internal static-source categories\n\n" + markdown_table(internal_category_rows, list(internal_category_rows[0]) if internal_category_rows else ["category"]) + "\n## ansible-lint categories\n\n" + markdown_table(lint_category_rows, list(lint_category_rows[0]) if lint_category_rows else ["category"]) + "\n## GitLeaks whole-repository categories\n\n" + markdown_table(gitleaks_category_rows, list(gitleaks_category_rows[0]) if gitleaks_category_rows else ["category"]) + "\n## Review-only categories\n\n" + markdown_table(review_category_rows, list(review_category_rows[0]) if review_category_rows else ["category"]) + "\n## Provider-comparable categories\n\n" + markdown_table(comparable_category_rows, list(comparable_category_rows[0]) if comparable_category_rows else ["category"]),
        "diagnostics.md": "# Diagnostics by repository\n\n" + markdown_table(diagnostics_rows, ["project", "diagnostics", "scan_status", "scan_error"]),
    }
    for filename, content in table_documents.items():
        (destination / "tables" / filename).write_text(content, encoding="utf-8")
    sections = [
        "# AnsibleGuard repository-study report\n",
        "## Overview\n\n" + markdown_table(overview, ["metric", "value"]),
        "## Interpretation boundary\n\nCounts describe detector output, not confirmed defects. "
        "Certain, uncertain, partial-provider, and labeled results must remain separate. "
        "Rates per selected YAML LOC are valid only for internal and ansible-lint populations. "
        "GitLeaks scans the whole repository and review-only rules describe Git history, so neither is normalized by selected YAML LOC. Failed and provider-incomplete repositories are missing observations, never zero findings.\n",
        "## Analysis populations\n\nInternal static-source findings remain analyzable when an external provider is partial. Review-only rules, whole-repository GitLeaks results, and ansible-lint results are reported separately. Provider-comparable tables are restricted to repositories where AnsibleGuard, ansible-lint, and GitLeaks all completed, and exclude review-range rules; repositories outside that population are missing observations, not zero findings.\n\n### Internal static-source categories\n\n" + markdown_table(internal_category_rows, ["category", "findings", "share_percent", "eligible_repositories", "missing_repositories", "repositories_affected", "repository_prevalence_percent"]) + "\n### ansible-lint categories\n\n" + markdown_table(lint_category_rows, ["category", "findings", "share_percent", "eligible_repositories", "missing_repositories", "repositories_affected", "repository_prevalence_percent"]) + "\n### GitLeaks whole-repository categories\n\n" + markdown_table(gitleaks_category_rows, ["category", "findings", "share_percent", "eligible_repositories", "missing_repositories", "repositories_affected", "repository_prevalence_percent"]) + "\n### Review-only categories\n\n" + markdown_table(review_category_rows, ["category", "findings", "share_percent", "eligible_repositories", "missing_repositories", "repositories_affected", "repository_prevalence_percent"]),
        "## Category composition\n\n![Category chart](../charts/findings-by-category.svg)\n\n" + markdown_table(category_rows, ["category", "findings", "share_percent", "repositories_affected", "repository_prevalence_percent", "median_per_repository", "q1_per_repository", "q3_per_repository", "findings_per_1000_selected_loc"]),
        "## Rules\n\n![Top rules](../charts/top-rules.svg)\n\n" + markdown_table(rule_rows, ["rule_id", "findings", "share_percent", "repositories_affected", "repository_prevalence_percent", "median_per_repository", "findings_per_1000_selected_loc"]),
        "## Internal semantic concepts\n\nThe stable detector rule ID may map to more than one semantic concept. In particular, `ansibleguard/unguarded-variable` is divided into `missing-internal-variable`, `undeclared-input-contract`, and `unresolved-runtime-input`; the latter two retain low-confidence/uncertain status because static analysis cannot prove all runtime inputs.\n\n![Top internal concepts](../charts/top-internal-concepts.svg)\n\n" + markdown_table(internal_concept_rows, ["concept_id", "findings", "share_percent", "eligible_repositories", "missing_repositories", "repositories_affected", "repository_prevalence_percent", "median_per_repository", "findings_per_1000_selected_loc"]),
        "## Static resolution status\n\nResolution status records what static evidence proved and what still blocks a stronger conclusion. `DETECTOR_RESULT` is the compatibility default for rules that do not use the proof model.\n\n" + markdown_table(resolution_rows, ["resolution_status", "findings", "share_percent", "eligible_repositories", "missing_repositories", "repositories_affected", "repository_prevalence_percent"]),
        "## Repositories\n\n![Normalized internal source rates](../charts/normalized-internal-findings-by-repository.svg)\n\n" + markdown_table(repository_rows, ["project", "selected_files", "selected_loc", "internal_source_occurrences", "internal_source_per_100_files", "internal_source_per_1000_selected_loc", "ansible_lint_occurrences", "gitleaks_occurrences", "review_occurrences", "diagnostics_total"]),
        "## Certainty\n\n![Certainty](../charts/findings-by-certainty.svg)\n\n" + markdown_table(certainty_rows, ["certainty", "findings", "share_percent", "repositories_affected"]),
        "## Providers\n\n![Providers](../charts/findings-by-provider.svg)\n\n" + markdown_table(provider_rows, ["provider", "findings", "share_percent", "repositories_affected"]),
        "## Provider completeness\n\n![Provider completeness](../charts/provider-completeness.svg)\n\n" + markdown_table(provider_health, list(provider_health[0]) if provider_health else ["provider"]),
        "## Diagnostics and failed repositories\n\n" + markdown_table(diagnostics_rows, ["project", "diagnostics", "scan_status", "scan_error"]),
        "## Repository/category heatmap\n\n![Heatmap](../charts/repository-category-heatmap.svg)\n",
        "## Reproducibility\n\nSee `../run-manifest.json`, `../run-config.yaml`, "
        "`../input/repositories.csv`, and `../status/validation-report.json`.\n",
    ]
    report_path = destination / "report" / "FULL_STUDY_REPORT.md"
    report_path.write_text("\n".join(sections), encoding="utf-8")
    atomic_json(destination / "report" / "report-data.json", {
        "overview": overview, "category_summary": category_rows,
        "rule_summary": rule_rows, "concept_summary": concept_rows,
        "resolution_summary": resolution_rows,
        "internal_concept_summary": internal_concept_rows,
        "severity_summary": severity_rows,
        "certainty_summary": certainty_rows, "provider_summary": provider_rows,
        "provider_health": provider_health, "diagnostics_summary": diagnostics_rows,
        "internal_category_summary": internal_category_rows,
        "ansible_lint_category_summary": lint_category_rows,
        "gitleaks_category_summary": gitleaks_category_rows,
        "review_category_summary": review_category_rows,
        "provider_comparable_category_summary": comparable_category_rows,
        "charts": [str(path.relative_to(destination)) for path in charts + pngs],
    })
    return report_path


def compare_runs(base: Path, candidate: Path, output: Path) -> dict:
    base = Path(base)
    candidate = Path(candidate)
    base_repos = {row["project"]: (row.get("commit_sha", ""), row.get("classification_manifest_sha256", "")) for row in read_csv(base / "input" / "repositories.csv")}
    candidate_repos = {row["project"]: (row.get("commit_sha", ""), row.get("classification_manifest_sha256", "")) for row in read_csv(candidate / "input" / "repositories.csv")}
    if base_repos != candidate_repos:
        raise ValueError("run comparison requires identical repository projects and SHAs")
    if any(not classification_hash for _sha, classification_hash in base_repos.values()):
        raise ValueError("run comparison requires classification-manifest hashes")
    base_manifest = load_json(base / "run-manifest.json", {})
    candidate_manifest = load_json(candidate / "run-manifest.json", {})
    for field in ("profile", "ansible_lint_scope"):
        if base_manifest.get(field) != candidate_manifest.get(field):
            raise ValueError(f"run comparison requires identical {field}")
    base_rows = read_csv(base / "aggregate" / "all-canonical-occurrences.csv")
    candidate_rows = read_csv(candidate / "aggregate" / "all-canonical-occurrences.csv")
    changes = []
    for project in sorted(base_repos):
        def normalized(rows):
            normalized_rows = []
            for row in rows:
                if row["project"] != project:
                    continue
                item = dict(row)
                item["line"] = int(item.get("line") or 1)
                try:
                    item["native_rules"] = json.loads(item.get("native_rules") or "[]")
                except json.JSONDecodeError:
                    item["native_rules"] = []
                normalized_rows.append(item)
            return normalized_rows
        comparison = compare_version_occurrences(normalized(base_rows), normalized(candidate_rows))
        for status in ("fixed", "introduced"):
            for item in comparison[status]:
                changes.append({"status": status, "match": "", **item})
        for status in ("moved", "location", "uncertain", "unchanged"):
            for pair in comparison[status]:
                display = pair.get("head") or pair.get("base") or {}
                changes.append({"status": status, "match": pair.get("match", ""), **display})
    output.mkdir(parents=True, exist_ok=True)
    write_csv(output / "occurrence-comparison.csv", changes)
    counts = Counter(row["status"] for row in changes)
    grouped = Counter((row["status"], row.get("category", "unknown"), row.get("rule_id", "unknown")) for row in changes)
    summary_rows = [
        {"status": status, "category": category, "rule_id": rule, "findings": count}
        for (status, category, rule), count in sorted(grouped.items())
    ]
    write_csv(output / "comparison-summary.csv", summary_rows)
    result = {
        "schema_version": SCHEMA_VERSION, "base": str(base), "candidate": str(candidate),
        "repositories": len(base_repos), "status_counts": dict(sorted(counts.items())),
        "generated_at_utc": utc_now(),
    }
    atomic_json(output / "comparison-report.json", result)
    (output / "COMPARISON_REPORT.md").write_text(
        "# AnsibleGuard study-run comparison\n\n"
        + markdown_table(
            [{"metric": key, "value": value} for key, value in result.items() if key != "schema_version"],
            ["metric", "value"],
        )
        + "\n## Changes by category and rule\n\n"
        + markdown_table(summary_rows, ["status", "category", "rule_id", "findings"], 100),
        encoding="utf-8",
    )
    return result


def run_all(config: dict) -> None:
    prepare(config)
    scan(config)
    validation = validate(config)
    if validation["status"] != "passed":
        raise RuntimeError(
            "validation gate failed; inspect status/validation-report.json before aggregation"
        )
    aggregate(config)
    path = report(config)
    manifest = load_json(run_dir(config) / "run-manifest.json", {})
    manifest.update({"state": "reported", "completed_at_utc": utc_now(), "report": str(path)})
    atomic_json(run_dir(config) / "run-manifest.json", manifest)


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("prepare", "preflight", "scan", "validate", "aggregate", "report", "all"):
        child = subparsers.add_parser(command)
        child.add_argument("--config", type=Path, required=True)
    compare = subparsers.add_parser("compare")
    compare.add_argument("--base", type=Path, required=True)
    compare.add_argument("--candidate", type=Path, required=True)
    compare.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "compare":
        result = compare_runs(args.base, args.candidate, args.output)
        print(json.dumps(result, indent=2))
        return
    config = load_config(args.config)
    functions = {
        "prepare": prepare, "preflight": preflight, "scan": scan,
        "validate": validate, "aggregate": aggregate, "report": report,
        "all": run_all,
    }
    result = functions[args.command](config)
    if result is not None:
        print(result if isinstance(result, Path) else json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
