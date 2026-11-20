#!/usr/bin/env python3
"""Canonical, four-worker, reproducible v0.0.7 207-repository study run.

This orchestrator deliberately contains no detector logic.  It only freezes
inputs, acquires exact Git revisions, drives the existing study pipeline, and
packages its evidence.  It is safe to resume interrupted *downloads* because
every checkout is re-verified at its manifest SHA before analysis; analytical
outputs are never used as a cache for a new run.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import gzip
import hashlib
import json
import locale
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tarfile
from typing import Any

from ansibleguard.profiles import profile_metadata

try:  # package import when run with ``python -m`` from the repository root
    from scripts import study_pipeline
    from scripts.study_reporting import (
        bar_chart, heatmap, optional_png, scatter_chart, spearman, write_csv,
    )
except ModuleNotFoundError:  # direct ``python scripts/v007_full_repro.py``
    import study_pipeline  # type: ignore[no-redef]
    from study_reporting import (  # type: ignore[no-redef]
        bar_chart, heatmap, optional_png, scatter_chart, spearman, write_csv,
    )


RUN_ID = "v007-full-repro-2026"
WORKERS = 4
REQUIRED_PROVIDERS = {"ansibleguard", "ansible-lint", "gitleaks"}
# The archive contains the result package as well as the unpacked package.
# This deliberately conservative floor avoids a half-written "canonical"
# result when raw provider evidence expands during the run.
MINIMUM_FREE_GIB = 40
EXPECTED_INTERNAL_SOURCE_SHA256 = "7ea8943bf40a6b05f2e33c4140446757c45b6d218e81a75096591f046a81978b"
EXPECTED_INTERNAL_SOURCE_ROWS = 265434
EXPECTED_INTERNAL_SOURCE_RULES = 60


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _command(args: list[str], *, cwd: Path | None = None, timeout: int = 120) -> str:
    return subprocess.run(
        args, cwd=cwd, check=True, capture_output=True, text=True, timeout=timeout
    ).stdout.strip()


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def _iter_csv(path: Path):
    with path.open(newline="", encoding="utf-8") as source:
        yield from csv.DictReader(source)


def _manifest_rows(config: dict) -> list[dict[str, str]]:
    rows = study_pipeline.selected_rows(config)
    projects = [row.get("project", "") for row in rows]
    identities = [(row.get("project", ""), row.get("commit_sha", "")) for row in rows]
    errors = []
    if len(rows) != 207:
        errors.append(f"expected 207 rows, found {len(rows)}")
    if any(not row.get("clone_url") for row in rows):
        errors.append("one or more repositories lack clone_url")
    if any(not __import__("re").fullmatch(r"[0-9a-f]{40}", row.get("commit_sha", "")) for row in rows):
        errors.append("one or more repositories lack a 40-character lowercase commit SHA")
    if len(projects) != len(set(projects)):
        errors.append("duplicate repository identities")
    if len(identities) != len(set(identities)):
        errors.append("unexpected duplicate frozen identities")
    if errors:
        raise RuntimeError("invalid frozen manifest: " + "; ".join(errors))
    return rows


def verify_disk_budget(config: dict, minimum_free_gib: int = MINIMUM_FREE_GIB) -> None:
    """Fail before acquisition if raw evidence and its archive cannot fit safely."""
    checkout_root = study_pipeline.resolve_path(
        config["repositories"]["checkout_root"], Path(config["_root"])
    )
    probe = checkout_root
    while not probe.exists():
        probe = probe.parent
    available = shutil.disk_usage(probe).free
    required = minimum_free_gib * 1024 ** 3
    if available < required:
        raise RuntimeError(
            f"insufficient free disk for a complete raw-evidence package: "
            f"{available / 1024 ** 3:.1f} GiB available, at least "
            f"{minimum_free_gib} GiB required"
        )


def acquire(config: dict, max_failures: int = 0) -> list[dict[str, str]]:
    """Acquire each exact commit, with at most four independent Git jobs.

    ``max_failures`` tolerates up to that many acquisition failures instead of
    aborting the run. Default 0 preserves the original all-or-nothing
    behavior. A non-zero tolerance is for a known, structural, non-retriable
    failure class: some frozen commit SHAs are no longer shallow-fetchable
    from GitHub (`git fetch --depth=1 origin <sha>` exits 128) because the
    SHA is unreachable from any current ref on the remote (e.g. the branch
    it was on was force-pushed or deleted upstream after the manifest was
    frozen) — retrying does not help. This mirrors the precedent already set
    for the v0.0.7 run, which excluded a documented subset of repositories
    for the same reason (see study/v007-full-repro-results/README-SUBSET.md) rather
    than silently absorbing the failures or blocking the run indefinitely.
    """
    rows = _manifest_rows(config)
    root = study_pipeline.resolve_path(
        config["repositories"]["checkout_root"], Path(config["_root"])
    )
    reusable_root_value = config["repositories"].get("verified_checkout_cache")
    reusable_root = (
        study_pipeline.resolve_path(reusable_root_value, Path(config["_root"]))
        if reusable_root_value else None
    )
    log_root = study_pipeline.run_dir(config) / "logs" / "acquisition"
    root.mkdir(parents=True, exist_ok=True)
    log_root.mkdir(parents=True, exist_ok=True)

    def checkout(row: dict[str, str]) -> dict[str, str]:
        project, sha = row["project"], row["commit_sha"]
        destination = root.joinpath(*project.split("/"))
        log_path = log_root / f"{project.replace('/', '__')}__{sha[:12]}.log"
        commands: list[list[str]] = []
        try:
            def verified_checkout(path: Path) -> bool:
                if not (path / ".git").exists():
                    return False
                try:
                    actual = _command(["git", "-C", str(path), "rev-parse", "HEAD"], timeout=30)
                    dirty = _command(
                        ["git", "-C", str(path), "status", "--porcelain", "--untracked-files=all"],
                        timeout=60,
                    )
                    return actual == sha and not dirty
                except Exception:
                    return False

            destination.parent.mkdir(parents=True, exist_ok=True)
            # An old clone can only be reused after this independent SHA and
            # clean-worktree verification. The new cache contains a symlink,
            # so the resolved input path is still guarded again by preflight.
            candidate = reusable_root.joinpath(*project.split("/")) if reusable_root else None
            if candidate is not None and verified_checkout(candidate) and not verified_checkout(destination):
                # A prior interrupted attempt can leave a partial Git
                # directory at the canonical-cache path. Preserve it for
                # diagnosis, then prefer the independently verified local
                # source instead of downloading an already available commit.
                if destination.is_symlink():
                    destination.unlink()
                elif destination.exists():
                    quarantine = root / ".incomplete-cache" / f"{project.replace('/', '__')}__{sha[:12]}"
                    quarantine.parent.mkdir(parents=True, exist_ok=True)
                    if quarantine.exists():
                        raise RuntimeError(f"incomplete cache quarantine already exists: {quarantine}")
                    destination.rename(quarantine)
                destination.symlink_to(candidate.resolve(), target_is_directory=True)
                log_path.write_text(
                    f"reused verified local checkout\nsource={candidate}\ncommit={sha}\n",
                    encoding="utf-8",
                )
                return {
                    "project": project, "commit_sha": sha, "repository_path": str(destination),
                    "status": "complete", "acquisition": "reused-verified-local-cache", "error": "",
                }
            if verified_checkout(destination):
                log_path.write_text(
                    f"reused verified canonical cache checkout\nsource={destination}\ncommit={sha}\n",
                    encoding="utf-8",
                )
                return {
                    "project": project, "commit_sha": sha, "repository_path": str(destination),
                    "status": "complete", "acquisition": "reused-verified-canonical-cache", "error": "",
                }
            if (destination / ".git").is_dir():
                commands.append(["git", "-C", str(destination), "fetch", "--depth=1", "--no-tags", "origin", sha])
            elif destination.exists():
                raise RuntimeError(f"destination exists but is not a Git checkout: {destination}")
            else:
                # Fetch only the frozen commit.  A full clone makes the cache
                # depend on mutable remote history and needlessly consumes
                # disk; the detached commit is all analysis requires.
                commands.append(["git", "init", str(destination)])
                commands.append(["git", "-C", str(destination), "remote", "add", "origin", row["clone_url"]])
                commands.append(["git", "-C", str(destination), "fetch", "--depth=1", "--no-tags", "origin", sha])
            commands.append(["git", "-C", str(destination), "checkout", "--detach", "--force", sha])
            commands.append(["git", "-C", str(destination), "rev-parse", "HEAD"])
            output = []
            for command in commands:
                output.append("$ " + " ".join(command))
                output.append(_command(command, timeout=1800))
            actual = output[-1].strip()
            if actual != sha:
                raise RuntimeError(f"checkout SHA mismatch: expected {sha}, got {actual}")
            log_path.write_text("\n".join(output) + "\n", encoding="utf-8")
            return {
                "project": project, "commit_sha": sha, "repository_path": str(destination),
                "status": "complete", "acquisition": "fetched-frozen-commit", "error": "",
            }
        except Exception as exc:
            log_path.write_text(f"{type(exc).__name__}: {exc}\n", encoding="utf-8")
            return {
                "project": project, "commit_sha": sha, "repository_path": str(destination),
                "status": "failed", "acquisition": "failed", "error": f"{type(exc).__name__}: {exc}",
            }

    results: dict[str, dict[str, str]] = {}
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(checkout, row): row["project"] for row in rows}
        for future in as_completed(futures):
            item = future.result()
            results[item["project"]] = item
            print(f"acquire {len(results)}/{len(rows)} {item['project']}: {item['status']}", flush=True)
    ordered = [results[row["project"]] for row in rows]
    write_csv(study_pipeline.run_dir(config) / "status" / "acquisition.csv", ordered)
    if failures := [row for row in ordered if row["status"] != "complete"]:
        if len(failures) > max_failures:
            raise RuntimeError(
                f"acquisition failed for {len(failures)} repositories "
                f"(tolerance: {max_failures}); see logs/acquisition"
            )
        excluded_path = study_pipeline.run_dir(config) / "status" / "acquisition-excluded.json"
        _json(excluded_path, {
            "excluded_count": len(failures),
            "tolerance": max_failures,
            "excluded_projects": [
                {"project": row["project"], "commit_sha": row["commit_sha"], "error": row.get("error", "")}
                for row in failures
            ],
            "note": (
                "These repositories could not be acquired at their frozen commit SHA "
                "(see error per row) and were excluded from this run under an explicit "
                "--max-acquisition-failures tolerance. The resulting population is "
                f"{len(ordered) - len(failures)} of {len(ordered)} originally-selected "
                "repositories, not the full frozen manifest count."
            ),
        })
    return ordered


def _environment(destination: Path, config: dict) -> None:
    root = Path(config["_root"])
    environment = destination / "environment"
    environment.mkdir(parents=True, exist_ok=True)
    commands = {
        "python": [sys.executable, "--version"],
        "ansible": [sys.executable, "-m", "ansible", "--version"],
        "ansible-lint": [sys.executable, "-m", "ansiblelint", "--version"],
        "gitleaks": ["gitleaks", "version"],
        "docker": ["docker", "--version"],
    }
    versions: dict[str, str] = {}
    for name, command in commands.items():
        try:
            versions[name] = _command(command, cwd=root, timeout=30)
        except Exception as exc:
            versions[name] = f"unavailable: {type(exc).__name__}: {exc}"
    try:
        freeze = _command([sys.executable, "-m", "pip", "freeze"], cwd=root)
    except Exception as exc:
        freeze = f"unavailable: {type(exc).__name__}: {exc}\n"
    (environment / "pip-freeze.txt").write_text(freeze + "\n", encoding="utf-8")
    (environment / "tool-versions.txt").write_text(
        "\n".join(f"{name}: {value}" for name, value in sorted(versions.items())) + "\n",
        encoding="utf-8",
    )
    relevant_env = {
        name: value for name, value in sorted(os.environ.items())
        if name.startswith(("ANSIBLE", "ANSIBLEGUARD", "NLTK", "SPACY", "LANG", "LC_", "TZ"))
    }
    _json(environment / "environment.json", {
        "recorded_at_utc": _now(), "python_executable": sys.executable,
        "python_version": sys.version, "platform": platform.platform(),
        "architecture": platform.machine(), "cpu_count": os.cpu_count(),
        "locale": locale.setlocale(locale.LC_ALL, None), "timezone": time_zone(),
        "environment_variables": relevant_env, "tool_versions": versions,
        "tool_commit": _command(["git", "rev-parse", "HEAD"], cwd=root),
        "analysis_tool_commit": study_pipeline.load_json(
            destination / "run-manifest.json", {}
        ).get("tool", {}).get("commit_sha", "unknown"),
        "package_builder_commit": _command(["git", "rev-parse", "HEAD"], cwd=root),
        "tool_branch": _command(["git", "branch", "--show-current"], cwd=root),
        "working_tree_dirty": bool(_command(["git", "status", "--porcelain"], cwd=root)),
        "workers": WORKERS, "random_seeds": {"study": "none; deterministic ordering only"},
    })


def time_zone() -> str:
    return os.environ.get("TZ") or datetime.now().astimezone().tzname() or "unknown"


def _gzip_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = list(dict.fromkeys(key for row in rows for key in row))
    import io
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    with path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as zipped:
            zipped.write(buffer.getvalue().encode("utf-8"))


def _field_summary(rows: list[dict[str, str]], field: str, label: str) -> list[dict[str, Any]]:
    counts = Counter((row.get(field) or "unknown") for row in rows)
    total = len(rows)
    return [{label: value, "findings": count, "percentage": round(100 * count / total, 2) if total else 0}
            for value, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))]


def _tables(destination: Path, config: dict) -> dict[str, list[dict[str, Any]]]:
    aggregate = destination / "aggregate"
    tables = destination / "tables"
    tables.mkdir(exist_ok=True)
    canonical_count = sum(1 for _ in _iter_csv(aggregate / "all-canonical-occurrences.csv"))
    raw_count = 0
    raw_ansibleguard_by_rule: Counter[str] = Counter()
    for raw_row in _iter_csv(aggregate / "all-raw-findings.csv"):
        raw_count += 1
        if raw_row.get("provider") == "ansibleguard":
            raw_ansibleguard_by_rule[raw_row["rule_id"]] += 1
    repo_summary = [row for row in _read_csv(aggregate / "repository-summary.csv") if row.get("project") != "__ALL__"]
    validation = {row["project"]: row for row in _read_csv(destination / "status" / "validation.csv")}
    scans = {row["project"]: row for row in _read_csv(destination / "status" / "repository-status.csv")}
    source_repo_counts: Counter[str] = Counter()
    source_rule_uncertain: Counter[str] = Counter()
    source_rule_repo_counts: Counter[tuple[str, str]] = Counter()
    source_counts_by_actionability: Counter[str] = Counter()
    source_counts_by_certainty: Counter[str] = Counter()
    source_counts_by_confidence: Counter[str] = Counter()
    source_counts_by_severity: Counter[str] = Counter()
    source_row_count = 0
    for source_row in _iter_csv(aggregate / "all-internal-source-occurrences.csv"):
        source_row_count += 1
        if source_row.get("provider") != "ansibleguard":
            raise RuntimeError("internal static-source population contains a non-AnsibleGuard provider")
        if source_row.get("source_population") != "production_ansible":
            raise RuntimeError("internal static-source population contains a non-production source row")
        source_repo_counts[source_row["project"]] += 1
        source_rule_repo_counts[(source_row["project"], source_row["rule_id"])] += 1
        if source_row.get("certainty") == "UNCERTAIN":
            source_rule_uncertain[source_row["rule_id"]] += 1
        source_counts_by_actionability[source_row.get("actionability") or "unknown"] += 1
        source_counts_by_certainty[source_row.get("certainty") or "unknown"] += 1
        source_counts_by_confidence[source_row.get("confidence") or "unknown"] += 1
        source_counts_by_severity[source_row.get("severity") or "unknown"] += 1
    source_rule_summary = _read_csv(aggregate / "rule-summary-internal.csv")
    source_rule_rows = {row["rule_id"]: row for row in source_rule_summary}
    if sum(int(row.get("findings") or 0) for row in source_rule_summary) != source_row_count:
        raise RuntimeError("internal static-source rule summary does not reconcile to its occurrence file")
    status_rows = []
    repository_status = {}
    for summary in repo_summary:
        project = summary["project"]
        check, scan = validation.get(project, {}), scans.get(project, {})
        scan_status = scan.get("status", "not-run")
        core_result_available = scan_status == "completed"
        status_row = {
            "repository": project, "commit_sha": summary.get("commit_sha", ""),
            "overall_status": check.get("status", "failed"), "scan_status": scan_status,
            "ansibleguard_status": "completed" if core_result_available else "missing",
            "duration_seconds": scan.get("duration_seconds", ""), "files_analyzed": summary.get("selected_files", 0),
            "selected_loc": summary.get("selected_loc", "") if core_result_available else "",
            "raw_findings": summary.get("raw_findings", "") if core_result_available else "",
            "canonical_occurrences": summary.get("canonical_occurrences", "") if core_result_available else "",
            "ansible_lint_status": check.get("ansible_lint_status", "missing"),
            "gitleaks_status": check.get("gitleaks_status", "missing"),
            "error_type": scan.get("error", "").split(":", 1)[0] if scan.get("error") else "",
            "error_message": scan.get("error", ""),
        }
        status_rows.append(status_row)
        repository_status[project] = status_row
    rule_rows = []
    for rule_id, summary in source_rule_rows.items():
        short_rule_id = rule_id.partition("/")[2] if "/" in rule_id else rule_id
        rule_rows.append({
            "rule_id": rule_id,
            "rule_name": short_rule_id,
            "raw_ansibleguard_findings": raw_ansibleguard_by_rule[short_rule_id],
            "canonical_occurrences": int(summary.get("findings") or 0),
            "repositories_affected": int(summary.get("repositories_affected") or 0),
            "percentage_of_repositories": summary.get("repository_prevalence_percent", 0),
            "uncertain_count": source_rule_uncertain[rule_id],
        })
    rule_rows.sort(key=lambda row: (-row["canonical_occurrences"], row["rule_id"]))
    provider_rows = _read_csv(aggregate / "provider-summary.csv")
    prevalence = [{
        "rule_id": row["rule_id"], "repositories_affected": row["repositories_affected"],
        "percentage_of_repositories": row["repository_prevalence_percent"],
        "median_occurrences_among_affected_repositories": row["median_per_repository"],
    } for row in source_rule_summary]
    failures = [{
        "repository": row["repository"], "commit_sha": row["commit_sha"],
        "overall_status": row["overall_status"], "scan_status": row["scan_status"],
        "error_type": row["error_type"], "error_message": row["error_message"],
        "provider_state": f"ansibleguard={row['ansibleguard_status']};ansible-lint={row['ansible_lint_status']};gitleaks={row['gitleaks_status']}",
    } for row in status_rows if row["overall_status"] != "complete" or row["scan_status"] != "completed"]
    complete_core_and_optional = sum(
        row["ansibleguard_status"] == "completed"
        and row["ansible_lint_status"] == "completed"
        and row["gitleaks_status"] == "completed"
        for row in status_rows
    )
    core_with_optional_incomplete = sum(
        row["ansibleguard_status"] == "completed"
        and (row["ansible_lint_status"] != "completed" or row["gitleaks_status"] != "completed")
        for row in status_rows
    )
    core_result_missing = sum(row["ansibleguard_status"] != "completed" for row in status_rows)
    provider_completeness = [
        {"state": "core and optional providers complete", "repositories": complete_core_and_optional},
        {"state": "core complete; optional provider incomplete", "repositories": core_with_optional_incomplete},
        {"state": "core result missing", "repositories": core_result_missing},
    ]
    actionability_rows = [{"actionability": key, "findings": count} for key, count in sorted(source_counts_by_actionability.items())]
    repository_rows = []
    density_rows = []
    size_findings_rows = []
    for summary in repo_summary:
        project = summary["project"]
        status_row = repository_status[project]
        has_core = status_row["ansibleguard_status"] == "completed"
        source_count = source_repo_counts[project] if has_core else ""
        row = dict(summary)
        row["ansibleguard_status"] = status_row["ansibleguard_status"]
        row["internal_source_occurrences"] = source_count
        if has_core:
            loc = int(summary.get("selected_loc") or 0)
            density = round(source_count * 1000 / loc, 4) if loc else ""
            row["internal_source_per_1000_selected_loc"] = density
            density_rows.append({
                "repository": project,
                "internal_source_occurrences": source_count,
                "selected_loc": loc,
                "internal_source_per_1000_selected_loc": density,
            })
            size_findings_rows.append({
                "repository": project,
                "selected_loc": loc,
                "selected_files": summary.get("selected_files", ""),
                "internal_source_occurrences": source_count,
            })
        else:
            row["internal_source_per_1000_selected_loc"] = ""
            row["canonical_occurrences"] = ""
            row["canonical_per_1000_loc"] = ""
        repository_rows.append(row)
    internal_projects = sorted(
        row["repository"] for row in status_rows if row["ansibleguard_status"] == "completed"
    )
    internal_rules = sorted({rule for _, rule in source_rule_repo_counts})
    rule_matrix = [{
        "project": project,
        **{rule: source_rule_repo_counts[(project, rule)] for rule in internal_rules},
    } for project in internal_projects]
    def summarize_counter(counts: Counter[str], label: str) -> list[dict[str, Any]]:
        total = sum(counts.values())
        return [{
            label: value,
            "findings": count,
            "percentage": round(100 * count / total, 2) if total else 0,
        } for value, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))]
    table_data = {
        "repository-execution-status.csv": status_rows,
        "findings-by-rule.csv": rule_rows,
        "findings-by-provider.csv": provider_rows,
        "findings-by-repository.csv": repository_rows,
        "severity.csv": summarize_counter(source_counts_by_severity, "severity"),
        "confidence.csv": summarize_counter(source_counts_by_confidence, "confidence"),
        "certainty.csv": summarize_counter(source_counts_by_certainty, "certainty"),
        "actionability.csv": actionability_rows,
        "rule-prevalence.csv": prevalence,
        "provider-completeness.csv": provider_completeness,
        "failures-and-partials.csv": failures,
        "runtimes.csv": [{"repository": row["repository"], "duration_seconds": row["duration_seconds"], "overall_status": row["overall_status"]} for row in status_rows],
        # No committed equivalence mapping exists. Keep estimates blank so
        # absence of a mapping is never shown as zero overlap.
        "external-tool-overlap.csv": [{"mapping_status": "not-modelled", "ansibleguard_only": "", "ansible_lint_only": "", "gitleaks_only": "", "mapped_overlap": "", "note": "No explicit equivalence mapping is defined; overlap is not estimable."}],
        "raw-vs-canonical.csv": [{"measure": "raw findings", "count": raw_count}, {"measure": "canonical occurrences", "count": canonical_count}],
        "findings-density.csv": density_rows,
        "repository-size-vs-findings.csv": size_findings_rows,
        "rule-repository-matrix.csv": rule_matrix,
    }
    for name, rows in table_data.items():
        write_csv(tables / name, rows)
    for stale in (tables / "uncertainty.csv", tables / "uncertain-vs-actionable.csv"):
        stale.unlink(missing_ok=True)
    return table_data


def _charts(destination: Path, table_data: dict[str, list[dict[str, Any]]], config: dict) -> list[Path]:
    data_dir, svg_dir, png_dir = destination / "charts" / "data", destination / "charts" / "svg", destination / "charts" / "png"
    for directory in (data_dir, svg_dir, png_dir):
        directory.mkdir(parents=True, exist_ok=True)
    for stale_name in (
        "10-uncertain-vs-actionable.csv", "11-provider-completeness.csv",
        "12-runtime-distribution.csv", "13-repository-size-vs-findings.csv",
        "14-rule-repository-heatmap.csv", "15-external-tool-overlap.csv",
        "10-uncertain-vs-actionable.svg", "11-provider-completeness.svg",
        "12-runtime-distribution.svg", "13-repository-size-vs-findings.svg",
        "14-rule-repository-heatmap.svg", "15-external-tool-overlap.svg",
    ):
        (data_dir / stale_name).unlink(missing_ok=True)
        (svg_dir / stale_name).unlink(missing_ok=True)
    for stale_png in png_dir.glob("*.png"):
        stale_png.unlink()
    all_paths: list[Path] = []
    def bar(name: str, source: list[dict[str, Any]], label: str, value: str, title: str, limit: int | None = 25,
            *, order: str = "value", semantic_colors: bool = False, subtitle: str = "", labels=None) -> None:
        write_csv(data_dir / f"{name}.csv", source)
        path = svg_dir / f"{name}.svg"
        rows = [((labels or {}).get(str(row.get(label)), str(row.get(label, "unknown"))), float(row.get(value) or 0)) for row in source]
        bar_chart(path, rows, title, limit=limit, order=order, semantic_colors=semantic_colors, subtitle=subtitle)
        all_paths.append(path)

    def ordered(rows: list[dict[str, Any]], key: str, sequence: list[str]) -> list[dict[str, Any]]:
        rank = {name: index for index, name in enumerate(sequence)}
        return sorted(rows, key=lambda row: rank.get(str(row.get(key)), len(rank)))

    from ansibleguard.report.findings import finding_policy

    rule_rows = table_data["findings-by-rule.csv"]
    def rule_label(row: dict[str, Any]) -> str:
        rule = str(row["rule_id"])
        policy = finding_policy({"rule_id": rule.split("/")[-1], "native_rules": [rule], "concept_id": rule.split("/")[-1]})
        total = int(row.get("canonical_occurrences") or 0)
        uncertain = int(row.get("uncertain_count") or 0)
        notes = []
        if policy == "optional":
            notes.append("optional")
        if total and uncertain / total >= 0.5:
            notes.append(f"{round(100 * uncertain / total)}% uncertain")
        return f"{rule.removeprefix('ansibleguard/')} [{', '.join(notes)}]" if notes else rule.removeprefix("ansibleguard/")
    rule_labels = {str(row["rule_id"]): rule_label(row) for row in rule_rows}
    required_rule_rows = [row for row in rule_rows if "optional" not in rule_labels[str(row["rule_id"])]]
    def notice(name: str, title: str, message: str) -> None:
        path = svg_dir / f"{name}.svg"
        path.write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="150" viewBox="0 0 900 150" role="img">'
            f'<title>{title}</title><rect width="900" height="150" fill="#fff"/>'
            '<rect x="1" y="1" width="898" height="148" fill="none" stroke="#777"/>'
            f'<text x="24" y="44" font-family="sans-serif" font-size="20" font-weight="bold">{title}</text>'
            f'<text x="24" y="91" font-family="sans-serif" font-size="16">{message}</text></svg>\n',
            encoding="utf-8",
        )
        all_paths.append(path)
    statuses = table_data["repository-execution-status.csv"]
    status_counts = [{"status": value, "repositories": count} for value, count in Counter(row["overall_status"] for row in statuses).items()]
    bar("01-repository-execution-status", status_counts, "status", "repositories", "Repository execution status (207 targeted repositories)")
    bar("02-raw-vs-canonical", table_data["raw-vs-canonical.csv"], "measure", "count", "Raw findings versus canonical occurrences (all providers)")
    provider_rows = table_data["findings-by-provider.csv"]
    provider_labels = {
        str(row["provider"]): f'{row["provider"]} ({row.get("eligible_repositories", "?")} of 207 repositories)'
        for row in provider_rows
    }
    bar("03-findings-by-provider", provider_rows, "provider", "findings",
        "Canonical findings by provider (populations differ; do not compare bars)", None, order="given",
        labels=provider_labels,
        subtitle="ansibleguard includes 497 review-range occurrences (265,434 static-source + 497); "
                 "ansible-lint is complete for 171 repositories only")
    top_rules = int(config.get("report", {}).get("top_rules", 25))
    bar("04-top-rules", rule_rows, "rule_id", "canonical_occurrences",
        "AnsibleGuard static-source occurrences by rule (206 analyzable repositories)", top_rules,
        labels=rule_labels, subtitle="[optional] = optional style policy, not a defect; [N% uncertain] = variable resolution could not decide")
    bar("04b-top-required-rules", required_rule_rows, "rule_id", "canonical_occurrences",
        "AnsibleGuard static-source occurrences by rule, optional style policy excluded", top_rules,
        labels=rule_labels, subtitle="Counts are detector output, not validated defects")
    bar("05-rule-prevalence", table_data["rule-prevalence.csv"], "rule_id", "repositories_affected",
        "Rule prevalence: repositories affected out of 206 analyzable repositories", top_rules,
        labels=rule_labels, subtitle="[optional] = optional style policy; [N% uncertain] = variable resolution could not decide")
    density_rows = table_data["findings-density.csv"]
    def binned(values: list[float], edges: list[float], unit: str, integer: bool = True) -> list[dict[str, Any]]:
        rows = []
        for low, high in zip(edges, edges[1:] + [None]):
            count = sum(1 for value in values if value >= low and (high is None or value < high))
            if high is None:
                name = f"{low:g}+ {unit}"
            elif integer:
                name = f"{low:g}–{high - 1:g} {unit}"
            else:
                name = f"{low:g} to <{high:g} {unit}"
            rows.append({"bin": name, "repositories": count})
        return rows
    occurrence_values = [float(row.get("internal_source_occurrences") or 0) for row in density_rows]
    bar("06-findings-per-repository-distribution",
        binned(occurrence_values, [0, 10, 50, 100, 250, 500, 1000, 2500, 5000], "occurrences"),
        "bin", "repositories", f"Repositories by AnsibleGuard static-source occurrence count ({len(density_rows)} analyzable repositories)",
        None, order="given", subtitle="Bins have unequal widths: compare counts, not bar areas")
    density_values = [float(row.get("internal_source_per_1000_selected_loc") or 0) for row in density_rows]
    bar("07-findings-density",
        binned(density_values, [0, 25, 50, 100, 150, 200, 300], "per KLOC", integer=False),
        "bin", "repositories", f"Repositories by static-source occurrences per 1,000 selected Ansible LOC ({len(density_rows)} repositories)",
        None, order="given", subtitle="Bins have unequal widths: compare counts, not bar areas")
    bar("08-severity-distribution", ordered(table_data["severity.csv"], "severity", ["error", "warning", "note"]),
        "severity", "findings", "AnsibleGuard static-source occurrences by severity", None, order="given", semantic_colors=True)
    bar("09-confidence-distribution", ordered(table_data["confidence.csv"], "confidence", ["high", "medium", "low"]),
        "confidence", "findings", "AnsibleGuard static-source occurrences by detector confidence", None, order="given", semantic_colors=True)
    bar("10-certainty-distribution", table_data["certainty.csv"], "certainty", "findings",
        "AnsibleGuard static-source occurrences by resolution certainty", None,
        subtitle="CONFIRMED = the detector's evidence resolved; it is not human validation")
    bar("11-actionability-distribution", ordered(table_data["actionability.csv"], "actionability", ["blocking", "actionable", "advisory", "informational"]),
        "actionability", "findings", "AnsibleGuard static-source occurrences by actionability", None, order="given", semantic_colors=True)
    bar("12-provider-completeness", table_data["provider-completeness.csv"], "state", "repositories", "Exclusive provider-completeness states (207 repositories)")
    runtime_bins = Counter(int(float(row.get("duration_seconds") or 0) / 60) * 60 for row in table_data["runtimes.csv"])
    bar("13-runtime-distribution",
        [{"duration_seconds_bin": f"{key}-{key + 59}" + (" (timeout)" if key >= 1800 else ""), "repositories": value}
         for key, value in sorted(runtime_bins.items())],
        "duration_seconds_bin", "repositories", "Repository runtime distribution (seconds)", None, order="given",
        subtitle="No repository ran between 300 and 1,799 s; the last bin is the 1,800 s timeout")
    size = table_data["repository-size-vs-findings.csv"]
    write_csv(data_dir / "14-repository-size-vs-findings.csv", size)
    scatter = svg_dir / "14-repository-size-vs-findings.svg"
    scatter_rows = [(row["repository"], float(row.get("selected_loc") or 0), float(row.get("internal_source_occurrences") or 0)) for row in size]
    scatter_chart(scatter, scatter_rows, "Selected Ansible LOC versus AnsibleGuard static-source occurrences (206 analyzable repositories)",
        x_label="Selected Ansible LOC", y_label="AnsibleGuard static-source occurrences",
        subtitle=f"Spearman rank correlation {spearman([r[1] for r in scatter_rows], [r[2] for r in scatter_rows]):.2f}; "
                 "labelled: highest counts, largest repositories, highest and lowest density",
        log_scale=True, label_outliers=5)
    all_paths.append(scatter)
    matrix = table_data["rule-repository-matrix.csv"]
    rules = [key for key in matrix[0] if key != "project"] if matrix else []
    ranked_rules = sorted(rules, key=lambda rule: -sum(int(row.get(rule) or 0) for row in matrix))[:20]
    ranked_repos = sorted(matrix, key=lambda row: -sum(int(row.get(rule) or 0) for rule in ranked_rules))[:30]
    heatmap_data = [{"repository": row["project"], **{rule: row.get(rule, 0) for rule in ranked_rules}} for row in ranked_repos]
    write_csv(data_dir / "15-rule-repository-heatmap.csv", heatmap_data)
    heatmap_path = svg_dir / "15-rule-repository-heatmap.svg"
    heatmap(heatmap_path, [row["project"] for row in ranked_repos], ranked_rules, {(row["project"], rule): int(row.get(rule) or 0) for row in ranked_repos for rule in ranked_rules}, "AnsibleGuard static-source rule × repository heatmap (raw counts, 30 highest-volume repositories)", limit=30)
    all_paths.append(heatmap_path)
    write_csv(data_dir / "16-external-tool-overlap.csv", table_data["external-tool-overlap.csv"])
    notice("16-external-tool-overlap", "External-tool overlap", "No validated rule mapping is available; overlap is not estimated.")
    pngs = optional_png(all_paths)
    for png in pngs:
        shutil.copy2(png, png_dir / png.name)
    return all_paths + [png_dir / png.name for png in pngs]


def _sanity(destination: Path, config: dict, table_data: dict[str, list[dict[str, Any]]], chart_paths: list[Path]) -> None:
    canonical_count = 0
    canonical_identities = set()
    providers_valid = True
    for row in _iter_csv(destination / "aggregate" / "all-canonical-occurrences.csv"):
        canonical_count += 1
        canonical_identities.add((row.get("project"), row.get("occurrence_id")))
        providers_valid = providers_valid and row.get("provider") in REQUIRED_PROVIDERS
    raw_count = sum(1 for _ in _iter_csv(destination / "aggregate" / "all-raw-findings.csv"))
    source_count = 0
    source_stable_ids = set()
    source_occurrence_ids = set()
    source_context_complete = True
    source_population_valid = True
    for row in _iter_csv(destination / "aggregate" / "all-internal-source-occurrences.csv"):
        source_count += 1
        source_stable_ids.add((row.get("project"), row.get("commit_sha"), row.get("provider"), row.get("occurrence_id")))
        source_occurrence_ids.add(row.get("occurrence_id"))
        source_context_complete = (
            source_context_complete and bool(row.get("file"))
            and row.get("line", "").isdigit() and int(row.get("line", "0") or 0) > 0
        )
        source_population_valid = (
            source_population_valid and row.get("provider") == "ansibleguard"
            and row.get("source_population") == "production_ansible"
        )
    statuses = table_data["repository-execution-status.csv"]
    checks = []
    frozen = config["run"]["id"] == RUN_ID

    def frozen_check(name: str, passed: bool, detail: str) -> None:
        """Assert a v0.0.7 frozen expectation; for a new version only record what was observed."""
        if frozen:
            check(name, passed, detail)
        else:
            check(name, True, f"{detail} [observed; no frozen expectation for run {config['run']['id']}]")

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": passed, "detail": detail})
    check("frozen_repository_count", len(statuses) == 207, f"found {len(statuses)}")
    check("manifest_sha_present", all(row.get("commit_sha") for row in statuses), "each status row has an expected SHA")
    check("canonical_occurrence_identity_unique", len(canonical_identities) == canonical_count, f"{canonical_count} occurrences")
    check("valid_provider", providers_valid, "providers are constrained to modeled identities")
    check("raw_not_less_than_canonical", raw_count >= canonical_count, f"raw={raw_count}, canonical={canonical_count}")
    expected_chart_data = list((destination / "charts" / "data").glob("*.csv"))
    required_chart_data = {
        f"{number:02d}-{name}.csv" for number, name in (
            (1, "repository-execution-status"), (2, "raw-vs-canonical"),
            (3, "findings-by-provider"), (4, "top-rules"), (5, "rule-prevalence"),
            (6, "findings-per-repository-distribution"), (7, "findings-density"),
            (8, "severity-distribution"), (9, "confidence-distribution"),
            (10, "certainty-distribution"), (11, "actionability-distribution"),
            (12, "provider-completeness"), (13, "runtime-distribution"),
            (14, "repository-size-vs-findings"), (15, "rule-repository-heatmap"),
            (16, "external-tool-overlap"),
        )
    }
    existing_chart_data = {path.name for path in expected_chart_data}
    check("chart_source_data_present", required_chart_data <= existing_chart_data, f"missing={sorted(required_chart_data - existing_chart_data)}")
    svg_paths = [path for path in chart_paths if path.suffix == ".svg"]
    check("chart_svgs_present", len(svg_paths) == 17 and all(path.is_file() for path in svg_paths), f"verified {sum(path.is_file() for path in svg_paths)} of 17 chart SVGs")
    status_projects = [row["repository"] for row in statuses]
    check("repository_status_identity_unique", len(status_projects) == len(set(status_projects)), f"{len(status_projects)} repository status rows")
    core_rows = [row for row in statuses if row["ansibleguard_status"] == "completed"]
    failed_core_rows = [row for row in statuses if row["ansibleguard_status"] != "completed"]
    status_counts = Counter(row["overall_status"] for row in statuses)
    scan_counts = Counter(row["scan_status"] for row in statuses)
    frozen_check("execution_state_counts", status_counts == {"complete": 171, "partial": 35, "failed": 1} and scan_counts == {"completed": 206, "timeout": 1}, f"overall={dict(status_counts)} scan={dict(scan_counts)}")
    frozen_check("analyzable_core_population", len(core_rows) == 206, f"found {len(core_rows)} completed AnsibleGuard results")
    check("missing_core_result_not_zeroed", all(row.get("canonical_occurrences", "") == "" for row in failed_core_rows), "the timed-out repository retains missing counts")
    completeness_total = sum(int(row["repositories"]) for row in table_data["provider-completeness.csv"])
    completeness_counts = {row["state"]: int(row["repositories"]) for row in table_data["provider-completeness.csv"]}
    expected_completeness = {"core and optional providers complete": 171, "core complete; optional provider incomplete": 35, "core result missing": 1}
    check("provider_completeness_is_exclusive", completeness_total == len(statuses) and (completeness_counts == expected_completeness or not frozen), f"exclusive categories={completeness_counts}")
    source_path = destination / "aggregate" / "all-internal-source-occurrences.csv"
    source_digest = _sha256(source_path)
    check("internal_source_population", (source_count == EXPECTED_INTERNAL_SOURCE_ROWS or not frozen) and source_population_valid, f"{source_count} AnsibleGuard production-source occurrences")
    frozen_check("internal_source_sha256", source_digest == EXPECTED_INTERNAL_SOURCE_SHA256, f"sha256={source_digest}")
    internal_rule_count = sum(1 for _ in _iter_csv(destination / "aggregate" / "rule-summary-internal.csv"))
    frozen_check("internal_source_rule_count", internal_rule_count == EXPECTED_INTERNAL_SOURCE_RULES, f"{internal_rule_count} observed AnsibleGuard rules")
    check("validation_context_fields_present", source_context_complete, "every source occurrence has a relative file path and positive line")
    check("validation_stable_identity_unique", len(source_stable_ids) == source_count, f"namespaced IDs are unique; raw occurrence_id collisions={source_count - len(source_occurrence_ids)}")
    check("internal_density_excludes_missing_repository", (len(table_data["findings-density.csv"]) == 206 or not frozen) and all(row.get("internal_source_per_1000_selected_loc") != "" for row in table_data["findings-density.csv"]), "density includes only analyzable repositories")
    check("external_overlap_not_encoded_as_zero", all(not row.get("mapped_overlap") for row in table_data["external-tool-overlap.csv"]), "unmodeled overlap estimate is blank")
    check("misleading_uncertain_actionable_chart_removed", not (destination / "charts" / "data" / "10-uncertain-vs-actionable.csv").exists(), "certainty and actionability are reported separately")
    payload = {"status": "passed" if all(item["passed"] for item in checks) else "failed", "checked_at_utc": _now(), "checks": checks}
    _json(destination / "sanity-checks.json", payload)
    lines = ["# Sanity checks", "", f"Overall status: **{payload['status']}**", "", "| Check | Passed | Detail |", "|---|---:|---|"]
    lines.extend(f"| {item['name']} | {item['passed']} | {item['detail']} |" for item in checks)
    (destination / "SANITY_CHECKS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    if payload["status"] != "passed":
        raise RuntimeError("sanity checks failed; inspect sanity-checks.json")


def _checksums(destination: Path) -> None:
    output = destination / "checksums" / "outputs.sha256"
    files = sorted(path for path in destination.rglob("*") if path.is_file() and path != output and "checksums" not in path.parts[-2:])
    output.parent.mkdir(exist_ok=True)
    output.write_text("".join(f"{_sha256(path)}  {path.relative_to(destination)}\n" for path in files), encoding="utf-8")


def _determinism(destination: Path, config: dict) -> None:
    expected = [path for directory in (destination / "normalized", destination / "tables", destination / "charts" / "data") for path in directory.rglob("*") if path.is_file()]
    first = {str(path.relative_to(destination)): _sha256(path) for path in expected}
    # Run analytical post-processing again from the untouched raw snapshots.
    study_pipeline.aggregate(config)
    study_pipeline.report(config)
    table_data = _tables(destination, config)
    _charts(destination, table_data, config)
    second = {name: _sha256(destination / name) for name in first}
    rows = [{"artifact": name, "run_1_sha256": first[name], "run_2_sha256": second[name], "identical": first[name] == second[name], "reason_if_not_identical": "" if first[name] == second[name] else "unexpected analytical change"} for name in sorted(first)]
    write_csv(destination / "determinism-comparison.csv", rows)
    failures = [row for row in rows if not row["identical"]]
    (destination / "DETERMINISM_REPORT.md").write_text(
        "# Determinism report\n\n"
        f"Re-ran aggregation, reporting, tables, and chart-data generation from the same raw snapshots. Expected deterministic artifacts: {len(rows)}; identical: {len(rows) - len(failures)}.\n\n"
        + ("All expected deterministic artifacts matched.\n" if not failures else "Unexpected differences are listed in `determinism-comparison.csv`.\n"),
        encoding="utf-8",
    )
    if failures:
        raise RuntimeError(f"determinism check failed for {len(failures)} artifacts")


def package(destination: Path) -> Path:
    archive = destination.parent / f"{destination.name}-results.tar.gz"
    with tarfile.open(archive, "w:gz", format=tarfile.PAX_FORMAT) as tar:
        tar.add(destination, arcname=destination.name, recursive=True)
    archive.with_suffix(archive.suffix + ".sha256").write_text(f"{_sha256(archive)}  {archive.name}\n", encoding="utf-8")
    return archive


def postprocess(config: dict) -> Path:
    destination = study_pipeline.run_dir(config)
    # Recover a machine-readable timeout state from a completed scan whose
    # per-repository status was written by an earlier runner revision.
    scan_status_path = destination / "status" / "repository-status.csv"
    scan_status_rows = _read_csv(scan_status_path)
    manifest_rows = {
        row["project"]: row
        for row in _read_csv(destination / "input" / "repositories.csv")
    }
    normalized_scan_status = False
    for row in scan_status_rows:
        if "timed out after" in row.get("error", "").lower():
            row["status"] = "timeout"
            row["snapshot_path"] = str(
                study_pipeline.snapshot_for(config, manifest_rows[row["project"]])
            )
            normalized_scan_status = True
    if normalized_scan_status:
        write_csv(scan_status_path, scan_status_rows)
        study_pipeline.validate(config)
    # Rebuild every derived result before emitting normalized files, tables,
    # and the first determinism snapshot. Existing aggregate files may have
    # been produced by an earlier pipeline revision; comparing those against a
    # fresh aggregate would report stale-vs-current drift as nondeterminism.
    study_pipeline.aggregate(config)
    study_pipeline.report(config)
    _environment(destination, config)
    inputs = destination / "inputs"
    inputs.mkdir(exist_ok=True)
    shutil.copy2(destination / "input" / "repositories.csv", inputs / "frozen-repositories.csv")
    profile = profile_metadata(config["run"].get("profile", "technical-full"))
    _json(inputs / "rule-catalog.json", profile)
    (inputs / "input-checksums.sha256").write_text(
        f"{_sha256(inputs / 'frozen-repositories.csv')}  frozen-repositories.csv\n{_sha256(inputs / 'rule-catalog.json')}  rule-catalog.json\n",
        encoding="utf-8",
    )
    normalized = destination / "normalized"
    normalized.mkdir(exist_ok=True)
    _gzip_csv(normalized / "findings.csv.gz", _read_csv(destination / "aggregate" / "all-raw-findings.csv"))
    _gzip_csv(normalized / "canonical-occurrences.csv.gz", _read_csv(destination / "aggregate" / "all-canonical-occurrences.csv"))
    shutil.copy2(destination / "status" / "repository-status.csv", normalized / "repository-status.csv")
    # Raw provider artifacts stay in their per-repository snapshot directories
    # to avoid a second, potentially huge copy.  This index makes that layout
    # explicit and keeps the archive self-describing.
    raw_index = []
    for row in _read_csv(destination / "input" / "repositories.csv"):
        snapshot = study_pipeline.snapshot_for(config, row)
        raw_index.append({
            "repository": row["project"], "commit_sha": row["commit_sha"],
            "snapshot": str(snapshot.relative_to(destination)),
            "raw_findings": str(study_pipeline.snapshot_artifact(snapshot, "findings.json").relative_to(destination)),
            "canonical_occurrences": str(study_pipeline.snapshot_artifact(snapshot, "occurrences.json").relative_to(destination)),
            "partial_output_present": snapshot.exists(),
            "raw_findings_present": study_pipeline.snapshot_artifact(snapshot, "findings.json").is_file(),
            "canonical_occurrences_present": study_pipeline.snapshot_artifact(snapshot, "occurrences.json").is_file(),
        })
    raw_dir = destination / "raw"
    raw_dir.mkdir(exist_ok=True)
    write_csv(raw_dir / "raw-output-index.csv", raw_index)
    (raw_dir / "README.md").write_text(
        "# Raw outputs\n\nRaw provider outputs, per-repository execution metadata, and stdout/stderr logs are retained under `../repositories/` and `../logs/` to avoid duplicating large evidence files. `raw-output-index.csv` maps every frozen repository to those immutable snapshot paths.\n",
        encoding="utf-8",
    )
    table_data = _tables(destination, config)
    charts = _charts(destination, table_data, config)
    _sanity(destination, config, table_data, charts)
    report = destination / "FULL_RUN_REPORT.md"
    aggregate = study_pipeline.load_json(destination / "aggregate" / "aggregate-summary.json", {})
    validation = study_pipeline.load_json(destination / "status" / "validation-report.json", {})
    status_counts = validation.get("repository_status_counts", {})
    incomplete_rows = table_data["failures-and-partials.csv"]
    incomplete_table = "\n".join([
        "| Repository | Status | Provider state | Error |",
        "|---|---|---|---|",
        *[
            "| " + " | ".join(str(row.get(key, "")).replace("|", "\\|").replace("\n", " ")
                               for key in ("repository", "overall_status", "provider_state", "error_message")) + " |"
            for row in incomplete_rows
        ],
    ]) if incomplete_rows else "No incomplete repository scans."
    report.write_text(
        f"# AnsibleGuard v{config['tool']['version']} full reproducible run\n\n"
        f"Run identity: `{config['run']['id']}`.  The canonical command uses exactly {WORKERS} concurrent repository jobs.\n\n"
        "## Reproducibility identity\n\n"
        "See `run-manifest.json`, `environment/`, `inputs/`, and `checksums/outputs.sha256`.\n\n"
        "## Execution health\n\n"
        f"Targeted repositories: {aggregate.get('repositories', 0)}. Complete: {status_counts.get('complete', 0)}; partial: {status_counts.get('partial', 0)}; failed: {status_counts.get('failed', 0)}. Provider and repository state are in `tables/repository-execution-status.csv`.\n\n"
        "## Main result totals\n\n"
        f"Raw findings: {aggregate.get('raw_findings', 0)}.  Canonical occurrences: {aggregate.get('canonical_occurrences', 0)}.  Internal and external-provider totals remain separate in `tables/findings-by-provider.csv`.\n\n"
        "## Results and caveats\n\n"
        "Rule, repository, provider, severity, confidence, uncertainty, runtime, and failure tables are in `tables/`; all chart source data is in `charts/data/`. Incomplete scans are explicit missing observations, never zero findings.\n\n"
        "### Incomplete scans\n\n"
        + incomplete_table + "\n\n"
        "## What these results do not prove\n\n"
        "This execution alone does **not** establish precision, recall, F1, human agreement, correctness of candidate thresholds, or generalization beyond the selected frozen population. No threshold-validation conclusion is made here.\n",
        encoding="utf-8",
    )
    run_manifest = study_pipeline.load_json(destination / "run-manifest.json", {})
    run_manifest.update({
        "state": "reported-with-incomplete-scans" if incomplete_rows else "reported",
        "completed_at_utc": _now(),
        "report": str(report),
        "validation_status": validation.get("status", "missing"),
        "repository_status_counts": status_counts,
        "aggregate_summary": aggregate,
        "package_builder_commit": _command(["git", "rev-parse", "HEAD"], cwd=Path(config["_root"])),
    })
    _json(destination / "run-manifest.json", run_manifest)
    shutil.copy2(destination / "run-manifest.json", destination / "RUN_MANIFEST.json")
    (destination / "README.md").write_text(
        "# v0.0.7 full reproducibility package\n\n"
        "`FULL_RUN_REPORT.md` is the execution summary and `report/FULL_STUDY_REPORT.md` contains the detailed analysis report. `raw/` indexes preserved per-repository evidence; `normalized/`, `tables/`, and `charts/data/` are deterministic analytical artifacts. Validate the package with `sanity-checks.json`, `DETERMINISM_REPORT.md`, and `checksums/outputs.sha256`.\n",
        encoding="utf-8",
    )
    _determinism(destination, config)
    _checksums(destination)
    return package(destination)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("study/configs/v007-207.yaml"))
    parser.add_argument("--clean", action="store_true", help="remove only the exact generated run directory before running")
    parser.add_argument("--skip-tests", action="store_true", help="do not run pytest; intended only after a recorded clean test run")
    parser.add_argument(
        "--skip-benchmark-validation",
        action="store_true",
        help=(
            "do not run scripts/validate_threshold_benchmark.py. That check validates "
            "study/threshold-benchmark-v007/ (a separate, unrelated human/LLM labeling-"
            "agreement pilot for threshold calibration) and has no bearing on this scan's "
            "detector output. Use this flag only when that pilot's own data is independently "
            "known to be stale/incomplete in the current checkout (e.g. a stale manifest hash "
            "after a deliberate codebook revision, or a missing generated artifact) and fixing "
            "it is tracked as separate work."
        ),
    )
    parser.add_argument("--postprocess-only", action="store_true", help="package an already completed scan without acquisition or analysis")
    parser.add_argument("--minimum-free-gib", type=int, default=MINIMUM_FREE_GIB, help="fail before acquisition unless this much free disk is available")
    parser.add_argument(
        "--max-acquisition-failures", type=int, default=0,
        help=(
            "tolerate up to this many repository-acquisition failures instead of aborting "
            "the run. Default 0 preserves the original all-or-nothing behavior. See "
            "acquire()'s docstring for when a non-zero tolerance is appropriate (a known, "
            "structural, non-retriable git failure class, not transient errors)."
        ),
    )
    args = parser.parse_args(argv)
    config = study_pipeline.load_config(args.config)
    run_id = str(config["run"].get("id") or "")
    if not run_id:
        raise RuntimeError("config run.id is required")
    if run_id == RUN_ID and str(config["tool"].get("version")) != "0.0.7":
        raise RuntimeError(f"run ID {RUN_ID} is reserved for tool version 0.0.7; use a new run ID")
    if int(config["run"].get("workers", 0)) != WORKERS:
        raise RuntimeError(f"canonical run must use exactly {WORKERS} workers")
    destination = study_pipeline.run_dir(config)
    if args.clean:
        if destination.name != run_id:
            raise RuntimeError("refusing to remove a directory that is not the configured run")
        shutil.rmtree(destination, ignore_errors=True)
    if args.postprocess_only:
        print(package_path := postprocess(config))
        print(f"archive_sha256={_sha256(package_path)}")
        return 0
    verify_disk_budget(config, args.minimum_free_gib)
    study_pipeline.prepare(config)
    if not args.skip_tests:
        result = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=config["_root"], text=True, capture_output=True)
        logs = destination / "logs"
        logs.mkdir(exist_ok=True)
        (logs / "test-results.txt").write_text(result.stdout + result.stderr, encoding="utf-8")
        _json(logs / "test-environment.json", {"python": sys.executable, "returncode": result.returncode, "recorded_at_utc": _now()})
        if result.returncode:
            raise RuntimeError("pytest failed; full run was not started")
    if not args.skip_benchmark_validation:
        benchmark = subprocess.run(
            [sys.executable, "scripts/validate_threshold_benchmark.py"],
            cwd=config["_root"], text=True, capture_output=True,
        )
        logs = destination / "logs"
        logs.mkdir(exist_ok=True)
        (logs / "threshold-benchmark-validation.txt").write_text(
            benchmark.stdout + benchmark.stderr, encoding="utf-8"
        )
        if benchmark.returncode:
            raise RuntimeError("threshold benchmark integrity validation failed")
    acquire(config, max_failures=args.max_acquisition_failures)
    study_pipeline.run_all(config)
    archive = postprocess(config)
    print(f"archive={archive}\narchive_sha256={_sha256(archive)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
