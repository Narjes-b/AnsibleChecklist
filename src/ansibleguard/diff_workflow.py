"""Base/head and staged comparison orchestration for local and CI use."""

from __future__ import annotations

import json
import re
import subprocess
import csv
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .report.comparison import (
    compare_occurrences,
    detect_breaking_changes_from_diff,
    evaluate_policy,
)
from .report.diff_report import write_diff_report
from .report.playbook_summary import build_playbook_summary
from .report.findings import finding_category, is_optional_finding
from .report.llm_explain import DEFAULT_HOST, DEFAULT_MODEL, enrich_occurrences_with_explanations
from .report.output_contract import validate_contract_payload
from .profiles import INCREMENTAL_FILE_LOCAL_RULES


class DiffWorkflowError(RuntimeError):
    pass


def incremental_analysis_scope(changed_files, enabled_rules=None):
    """Describe the correctness-safe incremental subset for a PR.

    Cross-file graph rules and providers intentionally remain full-repository
    work. This helper lets a caller accelerate only explicitly file-local
    rules while recording why the rest must not be skipped.
    """
    changed = tuple(sorted(str(path).replace("\\", "/") for path in changed_files))
    selected = set(enabled_rules) if enabled_rules is not None else set()
    local_rules = sorted(INCREMENTAL_FILE_LOCAL_RULES & selected) if selected else sorted(INCREMENTAL_FILE_LOCAL_RULES)
    deferred = sorted(selected - INCREMENTAL_FILE_LOCAL_RULES) if selected else ["repository-semantic-and-provider-rules"]
    return {
        "mode": "safe-file-local-subset",
        "changed_files": list(changed),
        "file_local_rules": local_rules,
        "deferred_rules": deferred,
        "requires_full_repository_analysis": bool(deferred),
    }


def analyze_snapshot_jobs(snapshot_jobs, analyzer, *, parallel=False):
    """Run independent immutable snapshot analyses and return stable results.

    The caller owns snapshot creation and cleanup.  Parallel execution is
    intentionally limited to independent base/head trees; it never shares a
    repository analysis context or output directory between jobs.  Returning
    results in sorted job-name order makes completion order unobservable to
    later comparison/canonicalization stages.
    """
    jobs = tuple(sorted(snapshot_jobs.items()))
    if not parallel:
        return {name: analyzer(*arguments) for name, arguments in jobs}
    with ThreadPoolExecutor(max_workers=len(jobs) or 1) as executor:
        futures = {
            name: executor.submit(analyzer, *arguments)
            for name, arguments in jobs
        }
        return {name: futures[name].result() for name, _arguments in jobs}


def mark_incremental_output_partial(output_root, *, changed_file):
    """Prevent a changed-file artifact from being treated as a full snapshot."""
    root = Path(output_root)
    health = {
        "status": "partial",
        "complete": False,
        "scope": "changed-files-only",
        "changed_file": str(changed_file).replace("\\", "/"),
    }
    for relative in ("run_metadata.json", "metadata/run.json"):
        path = root / relative
        if not path.is_file():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            payload["analysis_health"] = {
                **payload.get("analysis_health", {}),
                **health,
            }
            payload["incremental_analysis"] = {
                "mode": "file-local-only",
                "comparison_eligible": False,
            }
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    report_path = root / "summary/report.json"
    if report_path.is_file():
        report = json.loads(report_path.read_text(encoding="utf-8"))
        if isinstance(report, dict):
            report["status"] = "partial"
            report["analysis_health"] = {
                **report.get("analysis_health", {}),
                **health,
            }
            report["incremental_analysis"] = {
                "mode": "file-local-only",
                "comparison_eligible": False,
            }
            report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    summary_path = root / "summary/run-summary.md"
    if summary_path.is_file():
        summary = summary_path.read_text(encoding="utf-8")
        summary = re.sub(
            r"(?m)^- Run status: \*\*[^*]+\*\*$",
            "- Run status: **partial**",
            summary,
            count=1,
        )
        warning = (
            "\n> Incremental file-local feedback only; this artifact is not "
            "eligible for repository comparison.\n"
        )
        if warning.strip() not in summary:
            summary += warning
        summary_path.write_text(summary, encoding="utf-8")


def _artifact(root, relative):
    root = Path(root)
    return root / relative if root.is_dir() else root


def load_occurrences(root):
    path = _artifact(root, "canonical/occurrences.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict) and payload.get("kind") == "canonical-occurrences":
        if payload.get("contract") or "schema_version" in payload:
            try:
                validate_contract_payload(payload, expected_kind="canonical-occurrences")
            except ValueError as exc:
                raise DiffWorkflowError(f"invalid occurrence contract: {exc}") from exc
        return payload.get("items", [])
    if isinstance(payload, list):
        return payload
    raise DiffWorkflowError(f"unsupported occurrence document: {path}")


def load_diagnostics(root):
    root = Path(root)
    candidates = (
        root / "summary" / "diagnostics.json",
        root / "diagnostics.json",
    ) if root.is_dir() else ()
    for path in candidates:
        if not path.is_file():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            if payload.get("kind") == "diagnostics" and (
                payload.get("contract") or "schema_version" in payload
            ):
                try:
                    validate_contract_payload(payload, expected_kind="diagnostics")
                except ValueError as exc:
                    raise DiffWorkflowError(
                        f"invalid diagnostics contract: {exc}"
                    ) from exc
            return payload.get("items", [])
        return payload
    return []


def load_run_metadata(root):
    root = Path(root)
    if not root.is_dir():
        return None
    for path in (root / "metadata" / "run.json", root / "run_metadata.json"):
        if path.is_file():
            payload = json.loads(path.read_text(encoding="utf-8"))
            # Metadata written by v0.0.5 is validated. Older snapshots do not
            # carry a contract URI and remain readable for legacy comparison.
            if isinstance(payload, dict) and payload.get("contract"):
                try:
                    validate_contract_payload(payload, expected_kind="run-metadata")
                except ValueError as exc:
                    raise DiffWorkflowError(
                        f"invalid run metadata contract: {exc}"
                    ) from exc
            return payload
    return None


_SEMANTIC_PROVENANCE_PATHS = (
    ("schema_version",),
    ("profile", "name"),
    ("profile", "rules_sha256"),
    ("profile", "providers"),
    ("profile", "ansible_lint_rules"),
    ("reproducibility", "ansibleguard_version"),
    ("reproducibility", "ansibleguard_git_sha"),
    ("reproducibility", "structural_metrics_version"),
    ("reproducibility", "rule_catalog_sha256"),
    ("reproducibility", "ansible_core_version"),
    ("reproducibility", "ansible_lint_version"),
    ("reproducibility", "gitleaks_version"),
    ("reproducibility", "config", "sha256"),
)


def _nested(payload, path):
    value = payload
    for key in path:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def snapshot_compatibility(base_output, head_output):
    """Compare semantic inputs while allowing revision identity to differ."""
    base = load_run_metadata(base_output)
    head = load_run_metadata(head_output)
    if base is None and head is None:
        return {"status": "legacy-unverified", "compatible": True, "mismatches": []}
    if base is None or head is None:
        return {
            "status": "incompatible",
            "compatible": False,
            "mismatches": [{
                "field": "run_metadata",
                "base": "present" if base is not None else "missing",
                "head": "present" if head is not None else "missing",
            }],
        }
    mismatches = []
    for path in _SEMANTIC_PROVENANCE_PATHS:
        base_value = _nested(base, path)
        head_value = _nested(head, path)
        if base_value != head_value:
            mismatches.append(
                {
                    "field": ".".join(path),
                    "base": base_value,
                    "head": head_value,
                }
            )
    excluded_providers = set()
    for label, payload in (("base", base), ("head", head)):
        health = payload.get("analysis_health")
        if isinstance(health, dict) and health.get("complete") is True:
            continue
        incomplete = _provider_only_incompleteness(health)
        if incomplete is None:
            mismatches.append(
                {
                    "field": f"{label}.analysis_health.complete",
                    "base": _nested(base, ("analysis_health", "complete")),
                    "head": _nested(head, ("analysis_health", "complete")),
                }
            )
        else:
            excluded_providers.update(incomplete)
    # Files that failed to parse on either side are compared on neither side;
    # their findings cannot appear as fixed or introduced.
    parse_failed = {
        label: sorted({
            str(item.get("file"))
            for item in load_diagnostics(output)
            if item.get("category") == "PARSER_ERROR" and item.get("file")
        })
        for label, output in (("base", base_output), ("head", head_output))
    }
    excluded_files = sorted(set(parse_failed["base"]) | set(parse_failed["head"]))
    return {
        "status": (
            "incompatible" if mismatches
            else "partial" if excluded_providers or excluded_files
            else "compatible"
        ),
        "compatible": not mismatches,
        "mismatches": mismatches,
        "excluded_providers": sorted(excluded_providers),
        "excluded_files": excluded_files,
        "head_parse_failures": parse_failed["head"],
        "base_parse_failures": parse_failed["base"],
    }


def _provider_only_incompleteness(health):
    """Return the external providers to exclude, or None if the scan is unusable.

    A snapshot is still comparable when AnsibleGuard's own analysis completed
    and every fault is either an external-provider fault or a YAML parse
    failure of an individual file (deterministic input). The incomplete
    provider's findings, and every file that failed to parse, are then removed
    from *both* sides, so missing evidence can never appear as a fixed or
    introduced finding.
    """
    if not isinstance(health, dict) or health.get("internal_status") != "completed":
        return None
    faults = health.get("faults_by_category") or {}
    if any(
        not str(category).startswith("PROVIDER_") and category != "PARSER_ERROR"
        for category in faults
    ):
        return None
    providers = health.get("providers") or {}
    return {
        name.replace("_", "-") for name, status in providers.items() if status != "completed"
    }


def _enrich_head_output(head_output, comparison, policy):
    """Keep the normal head report aware of its associated comparison."""
    root = Path(head_output)
    if not root.is_dir():
        return
    introduced_by_file = Counter(
        item.get("file", ".") for item in comparison.get("introduced", [])
    )
    actionable_by_file = Counter(
        item.get("file", ".")
        for item in comparison.get("introduced", [])
        if not is_optional_finding(item)
    )
    optional_by_file = Counter(
        item.get("file", ".")
        for item in comparison.get("introduced", [])
        if is_optional_finding(item)
    )
    categories_by_file = defaultdict(Counter)
    for item in comparison.get("introduced", []):
        categories_by_file[item.get("file", ".")][finding_category(item)] += 1
    known_files = set()
    for path in (root / "summary.csv", root / "summary" / "summary.csv"):
        if not path.is_file():
            continue
        with path.open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            rows = list(reader)
            fields = list(reader.fieldnames or [])
        known_files.update(row["file"] for row in rows)
        for field in (
            "new_pr_findings",
            "new_pr_actionable_findings",
            "new_pr_optional_findings",
            "new_pr_findings_by_category",
            "pr_comparison_status",
        ):
            if field not in fields:
                fields.append(field)
        for row in rows:
            row["new_pr_findings"] = str(introduced_by_file.get(row["file"], 0))
            row["new_pr_actionable_findings"] = str(
                actionable_by_file.get(row["file"], 0)
            )
            row["new_pr_optional_findings"] = str(
                optional_by_file.get(row["file"], 0)
            )
            row["new_pr_findings_by_category"] = json.dumps(
                dict(sorted(categories_by_file.get(row["file"], {}).items())),
                separators=(",", ":"),
            )
            row["pr_comparison_status"] = "compared"
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
    report_path = root / "summary" / "report.json"
    if report_path.is_file():
        report = json.loads(report_path.read_text(encoding="utf-8"))
        report["pr_comparison"] = {
            "status": "compared",
            **policy.get("counts", {}),
            "actionable": policy.get("counts", {}).get(
                "introduced_actionable", 0
            ),
            "optional": policy.get("counts", {}).get(
                "introduced_optional", 0
            ),
            "policy_mode": policy["mode"],
            "policy_conclusion": policy["conclusion"],
            "introduced_by_severity": policy.get("introduced_by_severity", {}),
            "introduced_by_category": policy.get("introduced_by_category", {}),
            "optional_by_category": policy.get("optional_by_category", {}),
        }
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    for file in known_files:
        total = introduced_by_file.get(file, 0)
        comparison_payload = {
            "status": "compared",
            "introduced": total,
            "actionable": actionable_by_file.get(file, 0),
            "optional": optional_by_file.get(file, 0),
            "introduced_by_category": dict(
                sorted(categories_by_file.get(file, {}).items())
            ),
        }
        for name in ("report.json", "metrics.json"):
            path = root / "files" / file / name
            if not path.is_file():
                continue
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["pr_comparison"] = comparison_payload
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def parse_changed_lines(diff_text):
    """Parse a zero-context git diff into head-side changed line numbers."""
    result = {}
    current = None
    for line in diff_text.splitlines():
        if line.startswith("+++ "):
            value = line[4:].strip()
            current = None if value == "/dev/null" else value.removeprefix("b/")
            if current:
                result.setdefault(current, set())
            continue
        if current and line.startswith("@@"):
            match = re.search(r"\+(\d+)(?:,(\d+))?", line)
            if not match:
                continue
            start = int(match.group(1))
            count = int(match.group(2) or 1)
            result[current].update(range(start, start + count))
    return result


def parse_line_maps(diff_text):
    """Parse ``git diff -U0`` hunks per head path for base-to-head line mapping."""
    maps = {}
    current = None
    for line in (diff_text or "").splitlines():
        if line.startswith("+++ "):
            value = line[4:].strip()
            current = None if value == "/dev/null" else value.removeprefix("b/")
            if current:
                maps.setdefault(current, [])
            continue
        if current and line.startswith("@@"):
            match = re.match(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", line)
            if match:
                old_start, old_count, new_start, new_count = match.groups()
                maps[current].append((
                    int(old_start), int(old_count if old_count is not None else 1),
                    int(new_start), int(new_count if new_count is not None else 1),
                ))
    return maps


def parse_renamed_files(diff_text):
    """Return explicit old-to-new paths from Git rename metadata."""
    result = {}
    old_path = None
    for line in (diff_text or "").splitlines():
        if line.startswith("rename from "):
            old_path = line.removeprefix("rename from ").strip()
        elif line.startswith("rename to ") and old_path is not None:
            result[old_path] = line.removeprefix("rename to ").strip()
            old_path = None
    return result


def git_changed_lines(repo_root, base, head=None, *, staged=False, return_diff_text=False):
    command = ["git", "diff", "--unified=0", "--no-ext-diff"]
    if staged:
        command.append("--cached")
    else:
        command.append(str(base))
        if head:
            command.append(str(head))
    command.extend(["--", "*.yml", "*.yaml"])
    try:
        completed = subprocess.run(
            command,
            cwd=repo_root,
            text=True,
            capture_output=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = getattr(exc, "stderr", "") or str(exc)
        raise DiffWorkflowError(f"could not calculate git diff: {detail.strip()}") from exc
    changed = parse_changed_lines(completed.stdout)
    if return_diff_text:
        return changed, completed.stdout
    return changed


_DEFAULTS_FILE_RE = re.compile(r"(?:defaults|vars)/[^/]+\.ya?ml$")
_TOP_LEVEL_VAR_RE = re.compile(r"^([a-z][a-zA-Z0-9_]*):")
_README_NAMES = ("README.md", "README.rst", "README.txt", "README")


def detect_variable_documentation_gaps(diff_text, repo_root):
    """F5: Check if newly added defaults/ variables are documented in README.

    Returns a list of {type, file, variable, message} dicts for variables that
    were added in the PR but are not mentioned in the role's README.
    """
    if not diff_text:
        return []

    repo_root = Path(repo_root)
    added_vars = []
    current_file = None
    is_defaults = False

    for raw_line in diff_text.splitlines():
        if raw_line.startswith("+++ "):
            current_file = raw_line[4:].strip().removeprefix("b/")
            is_defaults = bool(_DEFAULTS_FILE_RE.search(current_file or ""))
        elif raw_line.startswith("+") and not raw_line.startswith("+++"):
            if is_defaults and not raw_line[1:].startswith(" "):
                m = _TOP_LEVEL_VAR_RE.match(raw_line[1:])
                if m:
                    added_vars.append((m.group(1), current_file))

    if not added_vars:
        return []

    readme_cache: dict[str, str] = {}
    gaps = []
    for var_name, defaults_path in added_vars:
        # Role root is parent.parent of defaults/main.yml
        defaults_rel = Path(defaults_path)
        if defaults_rel.parent.name not in ("defaults", "vars"):
            continue
        role_root = repo_root / defaults_rel.parent.parent
        cache_key = str(role_root)
        if cache_key not in readme_cache:
            readme_content = ""
            for name in _README_NAMES:
                candidate = role_root / name
                if candidate.is_file():
                    try:
                        readme_content = candidate.read_text(encoding="utf-8", errors="replace")
                    except OSError:
                        pass
                    break
            readme_cache[cache_key] = readme_content
        readme = readme_cache[cache_key]
        if readme and var_name not in readme:
            gaps.append({
                "type": "variable-undocumented",
                "file": defaults_path,
                "variable": var_name,
                "message": (
                    f"Variable '{var_name}' added to '{defaults_path}' "
                    "but not mentioned in the role README."
                ),
            })
    return gaps


_SOURCE_FROM_REPO = object()


def compare_outputs(
    base_output,
    head_output,
    output_root,
    repo_root,
    *,
    policy_mode="ratchet",
    changed_lines=None,
    summary_mode="changed",
    diff_text=None,
    allow_incompatible_snapshots=False,
    explain=False,
    explain_model=DEFAULT_MODEL,
    explain_host=DEFAULT_HOST,
    explain_max_items=None,
    explain_timeout=120.0,
    explain_budget=600.0,
    explain_checkpoint_dir=None,
    explain_style="free",
    head_source_root=_SOURCE_FROM_REPO,
):
    # API callers traditionally supply their live head snapshot as repo_root.
    # The CLI can keep report links rooted in the user's repository while
    # supplying the actual head/index tree separately. Explicit None means
    # precomputed results have no verified source available; never substitute
    # the current checkout for them.
    source_root = repo_root if head_source_root is _SOURCE_FROM_REPO else head_source_root
    changed_lines = changed_lines or {}
    compatibility = snapshot_compatibility(base_output, head_output)
    if not compatibility["compatible"] and not allow_incompatible_snapshots:
        fields = ", ".join(item["field"] for item in compatibility["mismatches"])
        raise DiffWorkflowError(
            "base/head snapshots use incompatible analysis semantics: " + fields
        )
    compatibility["override_applied"] = bool(
        allow_incompatible_snapshots and not compatibility["compatible"]
    )
    excluded = set(compatibility.get("excluded_providers", []))
    excluded_files = set(compatibility.get("excluded_files", []))

    def comparable(occurrences):
        return [
            item for item in occurrences
            if str(item.get("canonical_provider", "ansibleguard")) not in excluded
            and str(item.get("file")) not in excluded_files
        ]

    comparison = compare_occurrences(
        comparable(load_occurrences(base_output)),
        comparable(load_occurrences(head_output)),
        changed_lines=changed_lines,
        changed_files=changed_lines,
        renamed_files=parse_renamed_files(diff_text),
        line_maps=parse_line_maps(diff_text) if diff_text is not None else None,
    )
    comparison["snapshot_compatibility"] = compatibility
    # F3: Breaking-change detection from raw diff text
    comparison["breaking_changes"] = detect_breaking_changes_from_diff(diff_text)
    # F5: Variable documentation gaps
    comparison["source_context"] = {"status": "available" if source_root is not None else "unavailable",
                                    "uses_separate_head_tree": source_root is not None and Path(source_root) != Path(repo_root)}
    comparison["variable_doc_gaps"] = (
        detect_variable_documentation_gaps(diff_text, source_root) if source_root is not None else []
    )
    if explain:
        # Opt-in only (ansibleguard diff --explain): enriches comparison["introduced"]
        # in place with llm_* fields, which occurrences.py/csv_writer.py/
        # sarif_writer.py/pr_annotations.py already know how to carry
        # through to every output format. Never raises -- a missing/slow
        # model degrades to no enrichment, not a failed scan.
        comparison["llm_explain"] = enrich_occurrences_with_explanations(
            comparison.get("introduced", []),
            source_root,
            model=explain_model,
            host=explain_host,
            max_items=explain_max_items,
            timeout=explain_timeout,
            budget=explain_budget,
            checkpoint_dir=explain_checkpoint_dir,
            explanation_style=explain_style,
        )
    policy = evaluate_policy(comparison, policy_mode)
    diagnostics = [*load_diagnostics(base_output), *load_diagnostics(head_output)]
    execution_errors = [
        item for item in diagnostics
        if item.get("status") in {"tool-error", "analysis-error"}
    ]
    policy["execution_errors"] = len(execution_errors)
    if execution_errors:
        policy["conclusion"] = "failure"
    # A pull request that makes a file it changes unparseable is a regression.
    broken_by_change = sorted(
        path for path in compatibility.get("head_parse_failures", [])
        if path in changed_lines and path not in set(compatibility.get("base_parse_failures", []))
    )
    policy["introduced_parse_failures"] = broken_by_change
    if broken_by_change:
        policy["conclusion"] = "failure"
    _enrich_head_output(head_output, comparison, policy)
    playbooks = build_playbook_summary(
        source_root,
        comparison,
        changed_files=changed_lines,
        diagnostics=diagnostics,
    ) if source_root is not None else []
    return write_diff_report(
        output_root,
        comparison,
        policy,
        playbooks,
        repo_root=repo_root,
        changed_lines=changed_lines,
        summary_mode=summary_mode,
    )
