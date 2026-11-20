#!/usr/bin/env python3
"""Build the calibration-only V007 independent agreement-pilot forms.

Heldout occurrence contexts are never opened. Static candidates are filtered
against the frozen repository split before selection/context extraction. Review
history uses exact target commits; an actual first parent is required only for
rules whose evidence depends on the commit diff.
The script writes blank reviewer forms and never creates human labels.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import os
import re
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


PILOT_SEED = "v007-human-pilot-v1"
TARGET_PER_FAMILY = 50
IDENTITY_SHA256 = "2b70672c1f89039386f6cfb4bb73460059f05014a6b7248e4865f951150c7d6b"
SPLIT_SHA256 = "c6f50da3bd52130cd0a32ab48e322dfa666419d12bccdb1e7a4796d885260f65"
FAMILY_MAP_SHA256 = "914215d3c2ca0c9443ddd424ad0b8a8d9d9f317f2abc1fa27bb6ba7f842d4317"
EXPECTED_REVIEW_CALIBRATION_COUNTS = {
    "ansibleguard/commit-message-format": 98,
    "ansibleguard/missing-bug-reference": 19,
    "ansibleguard/missing-release-note": 133,
    "ansibleguard/missing-test-update": 47,
    "ansibleguard/untested-override-change": 38,
}

FAMILY_ORDER = [
    "objective_correctness",
    "variable_reference_reasoning",
    "security",
    "style_policy",
    "maintainability_complexity",
    "structure_reuse",
    "review_history",
]
FAMILY_NAMES = {
    "objective_correctness": "Objective correctness",
    "variable_reference_reasoning": "Variable/reference reasoning",
    "security": "Security",
    "style_policy": "Style/policy",
    "maintainability_complexity": "Maintainability/complexity",
    "structure_reuse": "Structure/reuse",
    "review_history": "Review/history",
}
FAMILY_QUESTIONS = {
    "objective_correctness": "Does the frozen source violate the documented correctness, reliability, dependency, or compatibility condition in the stated Ansible context?",
    "variable_reference_reasoning": "Given the available frozen repository evidence, what is the strongest supported conclusion about the reported variable, reference, scope, precedence, or runtime-input condition?",
    "security": "Is the documented security exposure or unsafe configuration actually present in the frozen source, and what remediation is justified in this repository context?",
    "style_policy": "Is the stated style/policy predicate true in the frozen source, and separately, is following it useful or actionable for this repository?",
    "maintainability_complexity": "Does the frozen source unit genuinely exhibit the described maintainability/complexity condition independently of the detector cutoff?",
    "structure_reuse": "Does the frozen repository/task organization exhibit the reported structure, placement, abstraction, or reuse condition?",
    "review_history": "Does the exact target commit message or actual first-parent change satisfy the documented review/history rule condition?",
}
FAMILY_CODEBOOKS = {
    "objective_correctness": "codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md",
    "variable_reference_reasoning": "codebooks/FAMILY_VARIABLES.md",
    "security": "codebooks/FAMILY_SECURITY.md",
    "style_policy": "codebooks/FAMILY_STYLE_POLICY.md",
    "maintainability_complexity": "codebooks/FAMILY_MAINTAINABILITY.md",
    "structure_reuse": "codebooks/FAMILY_STRUCTURE.md",
    "review_history": "codebooks/FAMILY_REVIEW_HISTORY.md",
}
PILOT_CODEBOOK_INPUTS = sorted({
    *FAMILY_CODEBOOKS.values(),
    "codebooks/RULE_OVERRIDES.md",
    "codebooks/REVIEWER_INSTRUCTIONS.md",
    "reviewers/HUMAN_REVIEWER_A_INSTRUCTIONS.md",
    "reviewers/HUMAN_REVIEWER_B_INSTRUCTIONS.md",
    "samples/agreement-pilot/PILOT_PROTOCOL.md",
})
REVIEW_RULE_IDS = {
    "ansibleguard/commit-message-format",
    "ansibleguard/missing-bug-reference",
    "ansibleguard/missing-release-note",
    "ansibleguard/missing-test-update",
    "ansibleguard/untested-override-change",
}
REVIEW_MESSAGE_ONLY_RULE_IDS = {
    "ansibleguard/commit-message-format",
    "ansibleguard/missing-bug-reference",
}
REVIEWER_DECISION_COLUMNS = [
    "semantic_label",
    "actionability_label",
    "context_sufficient",
    "requires_external_context",
    "external_context_type",
    "reason_code",
    "evidence_notes",
    "reviewer_notes",
]
REVIEWER_VISIBLE_COLUMNS = [
    "sample_id",
    "occurrence_id",
    "panel",
    "rule_id",
    "concept_id",
    "review_family",
    "codebook_path",
    "review_question",
    "repository",
    "commit_sha",
    "path",
    "line_start",
    "line_end",
    "object_kind",
    "object_id",
    "source_context",
    "context_bundle_path",
]
MASTER_COLUMNS = [
    *REVIEWER_VISIBLE_COLUMNS,
    "source_occurrence_id",
    "selection_rank_sha256",
    "is_agreement_pilot",
    "eligible_for_performance_scoring",
    *REVIEWER_DECISION_COLUMNS,
]
REVIEWER_COLUMNS = [*REVIEWER_VISIBLE_COLUMNS, *REVIEWER_DECISION_COLUMNS]
AI_DECISION_COLUMNS = [
    "ai_semantic_label",
    "ai_actionability_label",
    "ai_context_sufficient",
    "ai_requires_external_context",
    "ai_external_context_type",
    "ai_reason_code",
    "ai_notes",
    "ai_confidence",
    "ai_model_identity",
    "ai_review_protocol_version",
]
AI_SHADOW_COLUMNS = [*REVIEWER_VISIBLE_COLUMNS, *AI_DECISION_COLUMNS]

_SENSITIVE_ASSIGNMENT = re.compile(
    r"(?i)([\"']?[\w.-]*(?:password|passwd|passphrase|pass|pwd|token|secret|"
    r"credential|api[_-]?key|private[_-]?key|access[_-]?key|client[_-]?secret|"
    r"authorization|bearer)[\w.-]*[\"']?\s*[:=]\s*)(.*)$"
)
_BLOCK_SCALAR = re.compile(
    r"^(?:(?:[|>][+-]?\d?|!vault\s+[|>][+-]?\d?)(?:\s+#.*)?|[\[{])\s*$"
)
_TOKEN_PATTERNS = [
    re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{24,}\b"),
]
_PUBLIC_DEFAULTS = {
    "admin", "admin123", "changeme", "default", "guest", "password",
    "root", "secret", "test", "123456",
}
_TEMPLATE_PREFIXES = ("{{", "{%", "${", "$env:", "lookup(", "!vault")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_review_occurrence_id(
    repository: str, commit_sha: str, provider: str, rule_id: str, source_occurrence_id: str
) -> str:
    value = "|".join(
        ("v007-human-review-v1", repository, commit_sha, provider, rule_id, source_occurrence_id)
    )
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def pilot_rank(family_id: str, rule_id: str, occurrence_id: str) -> str:
    value = f"{PILOT_SEED}|{family_id}|{rule_id}|{occurrence_id}"
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def select_family(
    candidates: list[dict[str, str]],
    population_count_by_rule: dict[str, int],
    target: int = TARGET_PER_FAMILY,
) -> tuple[list[dict[str, str]], list[str]]:
    """Round-robin across non-rare rules; prefer one item per repo first."""
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for candidate in candidates:
        grouped[candidate["rule_id"]].append(candidate)
    for rule_id in grouped:
        grouped[rule_id].sort(
            key=lambda row: (row["selection_rank_sha256"], row["occurrence_id"])
        )

    all_rules = sorted(grouped)
    rules = [rule for rule in all_rules if population_count_by_rule.get(rule, 0) >= 5]
    rare_rules = [rule for rule in all_rules if population_count_by_rule.get(rule, 0) < 5]
    selected: list[dict[str, str]] = []
    selected_ids: set[str] = set()
    selected_repositories: set[str] = set()

    for one_per_repository in (True, False):
        while len(selected) < target:
            progress = False
            for rule_id in rules:
                bucket = grouped[rule_id]
                candidate = next(
                    (
                        row
                        for row in bucket
                        if row["occurrence_id"] not in selected_ids
                        and (
                            not one_per_repository
                            or row["repository"] not in selected_repositories
                        )
                    ),
                    None,
                )
                if candidate is not None:
                    selected.append(candidate)
                    selected_ids.add(candidate["occurrence_id"])
                    selected_repositories.add(candidate["repository"])
                    progress = True
                if len(selected) >= target:
                    break
            if not progress:
                break
    return selected, rare_rules


def redact_sensitive_text(text: str) -> str:
    """Redact key-associated credentials and recognizable provider tokens."""
    output: list[str] = []
    in_private_key = False
    in_vault_block_indent: int | None = None
    for line in text.split("\n"):
        if in_private_key:
            if "-----END " in line and "PRIVATE KEY-----" in line:
                output.append("[REDACTED PRIVATE KEY END]")
                in_private_key = False
            else:
                output.append("[REDACTED PRIVATE KEY CONTENT]")
            continue
        if "-----BEGIN " in line and "PRIVATE KEY-----" in line:
            output.append("[REDACTED PRIVATE KEY BLOCK]")
            in_private_key = True
            continue

        content_line = line[1:] if line.startswith(("+", "-")) else line
        indent = len(content_line) - len(content_line.lstrip())
        if in_vault_block_indent is not None:
            if line.strip() and indent > in_vault_block_indent:
                diff_marker = line[:1] if line.startswith(("+", "-")) else ""
                output.append(diff_marker + " " * indent + "[REDACTED ENCRYPTED VALUE]")
                continue
            in_vault_block_indent = None

        assignment = _SENSITIVE_ASSIGNMENT.search(line)
        if assignment:
            raw_value = assignment.group(2).strip()
            value = raw_value.strip().strip("\"'")
            prefix = line[: assignment.start(1)]
            folded = value.casefold()
            if value.startswith("[REDACTED"):
                output.append(line)
            elif value.startswith(_TEMPLATE_PREFIXES):
                output.append(line)
            elif folded in _PUBLIC_DEFAULTS:
                output.append(line)
            elif not value or _BLOCK_SCALAR.fullmatch(value):
                output.append(prefix + assignment.group(1) + "[REDACTED VALUE BLOCK]")
                in_vault_block_indent = indent
            else:
                output.append(prefix + assignment.group(1) + "[REDACTED_LITERAL]")
            continue

        redacted = line
        for pattern in _TOKEN_PATTERNS:
            redacted = pattern.sub("[REDACTED_TOKEN]", redacted)
        output.append(redacted)
    return "\n".join(output)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def _write_csv_bytes(rows: list[dict[str, str]], columns: list[str]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def _git(repo_path: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", "-C", str(repo_path), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if check and result.returncode:
        raise RuntimeError(f"git {' '.join(args)} failed in {repo_path}: {result.stderr[:500]}")
    return result


def _repo_path(root: Path, acquisition_row: dict[str, str]) -> Path:
    path = Path(acquisition_row["repository_path"])
    return path if path.is_absolute() else (root / path).resolve()


def load_review_candidates(
    root: Path,
    split_rows: dict[str, dict[str, str]],
    acquisition: dict[str, dict[str, str]],
    snapshot_index: dict[str, str],
) -> tuple[
    list[dict[str, str]],
    Counter[str],
    Counter[str],
    Counter[str],
    Counter[tuple[str, str]],
    Counter[tuple[str, str]],
    Counter[tuple[str, str]],
    Counter[str],
    Counter[str],
    Counter[str],
]:
    """Read review occurrence snapshots only for calibration repositories."""
    run_dir = root / "study/runs/v007-full-repro-2026"
    candidates: list[dict[str, str]] = []
    source_count_by_rule: Counter[str] = Counter()
    missing_parent_by_rule: Counter[str] = Counter()
    missing_required_parent_by_rule: Counter[str] = Counter()
    source_count_by_rule_repository: Counter[tuple[str, str]] = Counter()
    missing_parent_by_rule_repository: Counter[tuple[str, str]] = Counter()
    missing_required_parent_by_rule_repository: Counter[tuple[str, str]] = Counter()
    source_count_by_repository: Counter[str] = Counter()
    missing_parent_by_repository: Counter[str] = Counter()
    missing_required_parent_by_repository: Counter[str] = Counter()
    seen: set[str] = set()
    for repository in sorted(split_rows):
        split_row = split_rows[repository]
        if split_row["split"] != "calibration":
            continue
        indexed_path = snapshot_index.get(repository)
        acquired = acquisition.get(repository)
        if not indexed_path or not acquired:
            raise RuntimeError(f"calibration review inputs missing for {repository}")
        snapshot_path = run_dir / indexed_path
        if not snapshot_path.is_file():
            raise RuntimeError(f"calibration occurrence snapshot missing: {snapshot_path}")
        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
        items = snapshot if isinstance(snapshot, list) else snapshot.get("items", [])
        repo_path = _repo_path(root, acquired)
        commit_sha = split_row["commit_sha"]
        commit_check = _git(repo_path, "rev-parse", "--verify", f"{commit_sha}^{{commit}}", check=False)
        if commit_check.returncode or commit_check.stdout.strip() != commit_sha:
            raise RuntimeError(f"frozen target commit unavailable/mismatched for {repository}")
        parent_result = _git(repo_path, "rev-parse", "--verify", f"{commit_sha}^1", check=False)
        parent_sha = parent_result.stdout.strip() if parent_result.returncode == 0 else ""

        for item in items:
            rule_hits = sorted(REVIEW_RULE_IDS.intersection(item.get("native_rules", [])))
            if not rule_hits:
                continue
            if len(rule_hits) != 1:
                raise RuntimeError(
                    f"ambiguous review-rule membership in calibration snapshot {repository}: {rule_hits}"
                )
            rule_id = rule_hits[0]
            source_count_by_rule[rule_id] += 1
            source_count_by_rule_repository[(rule_id, repository)] += 1
            source_count_by_repository[repository] += 1
            if not parent_sha:
                missing_parent_by_rule[rule_id] += 1
                missing_parent_by_rule_repository[(rule_id, repository)] += 1
                missing_parent_by_repository[repository] += 1
                if rule_id not in REVIEW_MESSAGE_ONLY_RULE_IDS:
                    missing_required_parent_by_rule[rule_id] += 1
                    missing_required_parent_by_rule_repository[(rule_id, repository)] += 1
                    missing_required_parent_by_repository[repository] += 1
                    continue
            provider = str(item.get("canonical_provider", ""))
            if provider != "ansibleguard":
                raise RuntimeError(f"unexpected provider for review panel: {provider}")
            raw_id = str(item.get("occurrence_id", ""))
            occurrence_id = stable_review_occurrence_id(
                repository, commit_sha, provider, rule_id, raw_id
            )
            if occurrence_id in seen:
                raise RuntimeError(f"duplicate namespaced review identity: {occurrence_id}")
            seen.add(occurrence_id)
            path = str(item.get("file", "."))
            line = str(item.get("line", "1"))
            candidates.append(
                {
                    "occurrence_id": occurrence_id,
                    "source_occurrence_id": raw_id,
                    "identity_scheme": "v007-human-review-v1",
                    "repository": repository,
                    "commit_sha": commit_sha,
                    "provider": provider,
                    "rule_id": rule_id,
                    "concept_id": str(item.get("concept_id", "")),
                    "panel": "review-history",
                    "family_id": "review_history",
                    "path": path,
                    "line_start": line,
                    "line_end": line,
                    "object_kind": "git_commit",
                    "object_id": commit_sha,
                    "semantic_subject": "",
                    "source_context_ref": (
                        f"{repository}@{parent_sha}..{commit_sha}"
                        if parent_sha
                        else f"{repository}@{commit_sha}:commit-message"
                    ),
                    "_repository_path": str(repo_path),
                    "_parent_sha": parent_sha,
                    "_rule_population_count": "",
                }
            )

    if dict(sorted(source_count_by_rule.items())) != dict(sorted(EXPECTED_REVIEW_CALIBRATION_COUNTS.items())):
        raise RuntimeError(
            "calibration review snapshot counts changed; stop and reconcile against the frozen run: "
            f"{dict(source_count_by_rule)}"
        )
    return (
        candidates,
        source_count_by_rule,
        missing_parent_by_rule,
        missing_required_parent_by_rule,
        source_count_by_rule_repository,
        missing_parent_by_rule_repository,
        missing_required_parent_by_rule_repository,
        source_count_by_repository,
        missing_parent_by_repository,
        missing_required_parent_by_repository,
    )


def _safe_source_path(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or value in {"", "."}:
        raise ValueError(f"invalid static source path: {value!r}")
    return path


def _numbered_excerpt(lines: list[str], start: int, end: int) -> str:
    if not lines:
        return "[empty source file]"
    start = max(1, start)
    end = min(len(lines), end)
    excerpt = redact_sensitive_text("\n".join(lines[start - 1 : end])).split("\n")
    return "\n".join(
        f"{number:5d} | {excerpt[index]}"
        for index, number in enumerate(range(start, end + 1))
    )


ROLE_SUBDIRECTORIES = {
    "tasks", "handlers", "defaults", "vars", "meta", "templates", "files", "library",
    "module_utils", "filter_plugins", "molecule", "tests",
}
TREE_LISTING_LIMIT = 120


def _role_root(source_path: str) -> str | None:
    """Return the cited role directory, not an intermediate grouping directory.

    ``roles/device_roles/xrt_caproto/tasks/main.yml`` belongs to the role
    ``roles/device_roles/xrt_caproto``: the role root is the directory that
    directly contains a standard role subdirectory below a ``roles`` segment.
    """
    parts = PurePosixPath(source_path).parts
    try:
        start = next(i for i, part in enumerate(parts[:-1]) if part in {"roles", "collections"})
    except StopIteration:
        return None
    for index in range(start + 2, len(parts) - 1):
        if parts[index] in ROLE_SUBDIRECTORIES:
            return "/".join(parts[:index])
    return "/".join(parts[: start + 2]) if len(parts) > start + 2 else None


def _source_tree_context(repo_path: Path, commit_sha: str, source_path: str) -> str:
    role_root = _role_root(source_path)
    target = role_root or "."
    result = _git(repo_path, "ls-tree", "-r", "--name-only", commit_sha, "--", target, check=False)
    if result.returncode:
        return "[tracked-path listing unavailable]"
    paths = result.stdout.splitlines()
    # Paths next to the cited file come first so a long listing never hides the
    # evidence the rule is about.
    anchor = str(PurePosixPath(source_path).parent)
    nearby = [p for p in paths if anchor == "." or p.startswith(anchor + "/")]
    ordered = nearby + [p for p in paths if p not in set(nearby)]
    shown = ordered[:TREE_LISTING_LIMIT]
    suffix = (
        f"\n[listing truncated: {len(shown)} of {len(paths)} paths shown; paths beside the cited file first]"
        if len(paths) > TREE_LISTING_LIMIT else ""
    )
    return "\n".join(shown) + suffix if shown else "[no tracked paths under this scope]"


def _variable_reference_context(
    repo_path: Path, commit_sha: str, semantic_subject: str
) -> str:
    if not semantic_subject.startswith("variable:"):
        return ""
    symbol = semantic_subject.split(":", 1)[1].strip()
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,127}", symbol):
        return "[symbol not a simple variable identifier; inspect supplied repository context]"
    result = _git(
        repo_path,
        "grep",
        "-n",
        "-I",
        "-F",
        "-e",
        symbol,
        commit_sha,
        "--",
        "*.yml",
        "*.yaml",
        "*.j2",
        check=False,
    )
    if result.returncode not in (0, 1):
        return "[frozen-commit reference search unavailable]"
    matches = result.stdout.splitlines()
    truncated = len(matches) > 50
    output = matches[:50]
    if truncated:
        output.append("[reference search truncated after 50 matches]")
    return "\n".join(output) if output else "[no visible matching references in searched YAML/Jinja files]"


def _static_context(
    candidate: dict[str, str],
    family_name: str,
    codebook_path: str,
    repo_path: Path,
) -> tuple[str, str]:
    relative = _safe_source_path(candidate["path"])
    blob = _git(repo_path, "show", f"{candidate['commit_sha']}:{relative.as_posix()}").stdout
    if "\x00" in blob:
        raise RuntimeError(f"binary source cannot be reviewed: {candidate['source_context_ref']}")
    lines = blob.splitlines()
    anchor = max(1, int(candidate["line_start"] or "1"))
    # Include complete ordinary files and an explicit bounded window for very large files.
    if len(lines) <= 500 and len(blob) <= 120_000:
        first, last = 1, len(lines)
    else:
        first, last = max(1, anchor - 35), min(len(lines), anchor + 35)
    source_excerpt = _numbered_excerpt(lines, first, last)
    parts = [
        f"# Frozen source context: {candidate['sample_id']}",
        "",
        f"- Repository: `{candidate['repository']}`",
        f"- Commit: `{candidate['commit_sha']}`",
        f"- Family: {family_name}",
        f"- Rule: `{candidate['rule_id']}`",
        f"- Codebook: `{codebook_path}`",
        f"- Source: `{candidate['path']}` (reported anchor line {anchor})",
        f"- Object: `{candidate['object_kind']}` `{candidate['object_id']}`",
        "- Evidence source: Git blob at the frozen commit; no current worktree content was used.",
        "- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.",
        "",
        "## Source excerpt",
        "",
        f"Lines {first}–{last} of {len(lines)}:",
        "",
        "```text",
        source_excerpt,
        "```",
    ]
    inline = source_excerpt
    if candidate["family_id"] == "structure_reuse":
        tree = redact_sensitive_text(
            _source_tree_context(repo_path, candidate["commit_sha"], candidate["path"])
        )
        parts.extend(["", "## Frozen tracked paths in the relevant role/scope", "", "```text", tree, "```"])
    if candidate["family_id"] == "variable_reference_reasoning":
        references = _variable_reference_context(
            repo_path, candidate["commit_sha"], candidate.get("semantic_subject", "")
        )
        if references:
            parts.extend(["", "## Visible variable references", "", "```text", redact_sensitive_text(references), "```"])
    if first != 1 or last != len(lines):
        parts.extend([
            "",
            "The file is larger than the inline-context limit; only the stated anchor window is included. If that prevents a defensible decision, use `uncertain` or `unreviewable` as defined in the codebook.",
        ])
    return "\n".join(parts) + "\n", inline


def _changed_file_rows(repo_path: Path, parent_sha: str, commit_sha: str) -> list[tuple[str, str]]:
    result = _git(
        repo_path,
        "diff",
        "--no-ext-diff",
        "--no-color",
        "--name-status",
        parent_sha,
        commit_sha,
    )
    rows = []
    for line in result.stdout.splitlines():
        columns = line.split("\t")
        if len(columns) >= 2:
            rows.append((columns[0], columns[-1]))
    return rows


def _is_test_path(path: str) -> bool:
    parts = set(path.lower().replace("\\", "/").split("/"))
    return bool(parts & {"test", "tests", "molecule", "spec"})


def _is_config_path(path: str) -> bool:
    lower = path.lower()
    return lower.endswith((".yml", ".yaml")) and not _is_test_path(path)


def _review_diff_paths(rule_id: str, changed: list[tuple[str, str]]) -> list[str]:
    paths = [path for _status, path in changed]
    if rule_id == "ansibleguard/missing-release-note":
        # Use the detector's own release-note definition so reviewer evidence
        # and detection cannot disagree about what counts as a release note.
        from ansibleguard.detectors.review_metadata import _is_release_note

        return [p for p in paths if _is_config_path(p) or _is_release_note(p)]
    if rule_id == "ansibleguard/missing-test-update":
        return [p for p in paths if _is_config_path(p) or _is_test_path(p)]
    if rule_id == "ansibleguard/untested-override-change":
        return [
            p for p in paths
            if _is_test_path(p)
            or any(segment in {"defaults", "vars"} for segment in p.lower().split("/"))
        ]
    return []


def _review_context(
    candidate: dict[str, str],
    family_name: str,
    codebook_path: str,
    repo_path: Path,
) -> tuple[str, str]:
    parent_sha = candidate["_parent_sha"]
    commit_sha = candidate["commit_sha"]
    rule_id = candidate["rule_id"]
    message_only = rule_id in REVIEW_MESSAGE_ONLY_RULE_IDS
    message = _git(repo_path, "show", "-s", "--format=%B", commit_sha).stdout.rstrip()
    if message_only:
        changed: list[tuple[str, str]] = []
        relevant: list[str] = []
    else:
        if not parent_sha:
            raise RuntimeError(f"diff-dependent review item lacks its actual first parent: {candidate['sample_id']}")
        changed = _changed_file_rows(repo_path, parent_sha, commit_sha)
        relevant = _review_diff_paths(rule_id, changed)
    parent_evidence = (
        f"`{parent_sha}` (available; diff not required by this message-only rule)"
        if message_only and parent_sha
        else "unavailable locally and not required for this message-only rule"
        if message_only
        else f"`{parent_sha}`"
    )
    parts = [
        f"# Frozen Git review context: {candidate['sample_id']}",
        "",
        f"- Repository: `{candidate['repository']}`",
        f"- Target commit: `{commit_sha}`",
        f"- Actual first parent: {parent_evidence}",
        f"- Evidence type: {'exact target commit message only' if message_only else 'actual first-parent diff'}",
        f"- Family: {family_name}",
        f"- Rule: `{rule_id}`",
        f"- Codebook: `{codebook_path}`",
        f"- Diff range: {'not used for this message-only rule' if message_only else f'`{parent_sha}..{commit_sha}` (from frozen Git objects)'}",
        "- No detector message or scan-time `base: null` fallback is used as review evidence.",
        "",
        "## Exact target commit message",
        "",
        "```text",
        redact_sensitive_text(message) or "[empty commit message]",
        "```",
        "",
        f"## Changed paths {'(not required for message-only evidence)' if message_only else f'({len(changed)})'}",
        "",
    ]
    parts.extend(f"- `{status}` `{path}`" for status, path in changed)
    if message_only:
        parts.append("- [not used; this rule is evaluated on the exact target commit message]")
    elif not changed:
        parts.append("- [no changed paths in this first-parent diff]")
    if message_only:
        parts.extend(["", "The rule is evaluated only on the exact target commit message above. No parent/diff fallback or AI/detector label is used."])
    elif relevant:
        diff = _git(
            repo_path,
            "diff",
            "--no-ext-diff",
            "--no-color",
            "--unified=5",
            parent_sha,
            commit_sha,
            "--",
            *relevant,
        ).stdout
        parts.extend(["", "## Relevant first-parent diff", "", "```diff", redact_sensitive_text(diff), "```"])
    elif rule_id in {
        "ansibleguard/missing-release-note",
        "ansibleguard/missing-test-update",
        "ansibleguard/untested-override-change",
    }:
        parts.extend(["", "## Relevant first-parent diff", "", "No paths relevant to this rule’s evidence class changed in the actual first-parent diff."])
    else:
        parts.extend(["", "No paths relevant to this rule's evidence class changed in the actual first-parent diff."])
    inline = (
        f"Commit `{commit_sha}`. "
        f"{'Message-only evidence; first parent not required. ' if message_only and not parent_sha else ''}"
        f"Message:\n{redact_sensitive_text(message)}\n"
        f"{'See the exact target-message context bundle.' if message_only else f'First-parent diff changes {len(changed)} paths; see the linked frozen context bundle.'}"
    )
    return "\n".join(parts) + "\n", inline


def _immutable_write(path: Path, content: bytes) -> None:
    if path.exists():
        if path.read_bytes() == content:
            return
        raise RuntimeError(f"refusing to overwrite existing validation artifact: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(content)
    os.replace(temporary, path)


def build_agreement_pilot(root: Path, validation_dir: Path, dry_run: bool = False) -> dict[str, Any]:
    identity_path = validation_dir / "identities/static-source-candidates.csv.gz"
    identity_manifest_path = validation_dir / "identities/static-source-candidates.manifest.json"
    split_path = validation_dir / "splits/repository-split.csv"
    mapping_path = validation_dir / "mappings/rule-family-map.csv"
    for path, expected in (
        (identity_path, IDENTITY_SHA256),
        (split_path, SPLIT_SHA256),
        (mapping_path, FAMILY_MAP_SHA256),
    ):
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(f"frozen input SHA changed for {path}: {actual}")
    identity_manifest = json.loads(identity_manifest_path.read_text(encoding="utf-8"))
    if identity_manifest.get("candidate_file_sha256") != IDENTITY_SHA256:
        raise RuntimeError("identity manifest does not match the frozen candidate table")

    split_rows = {row["repository"]: row for row in _read_csv(split_path)}
    if len(split_rows) != 206 or Counter(row["split"] for row in split_rows.values()) != {"calibration": 144, "heldout": 62}:
        raise RuntimeError("frozen 144/62 repository split does not reconcile")
    mapping_rows = _read_csv(mapping_path)
    family_for_rule = {row["rule_id"]: row["family_id"] for row in mapping_rows}
    if len(mapping_rows) != 65 or set(family_for_rule.values()) != set(FAMILY_ORDER):
        raise RuntimeError("frozen rule-family mapping is incomplete")

    static_candidates: dict[str, list[dict[str, str]]] = defaultdict(list)
    static_population_by_rule: Counter[str] = Counter()
    with gzip.open(identity_path, "rt", newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            # Reject heldout rows immediately; no heldout context is opened or retained.
            if split_rows.get(row["repository"], {}).get("split") != "calibration":
                continue
            rule_id = row["canonical_rule_id"]
            family_id = family_for_rule.get(rule_id)
            if not family_id or family_id == "review_history":
                raise RuntimeError(f"static identity has no static family mapping: {rule_id}")
            static_population_by_rule[rule_id] += 1
            static_candidates[family_id].append(
                {
                    "occurrence_id": row["occurrence_id"],
                    "source_occurrence_id": row["source_occurrence_id"],
                    "identity_scheme": row["identity_scheme"],
                    "repository": row["repository"],
                    "commit_sha": row["commit_sha"],
                    "provider": row["provider"],
                    "rule_id": rule_id,
                    "concept_id": row["concept_id"],
                    "panel": "static-source",
                    "family_id": family_id,
                    "path": row["path"],
                    "line_start": row["line_start"],
                    "line_end": row["line_end"],
                    "object_kind": row["object_kind"],
                    "object_id": row["object_id"],
                    "semantic_subject": row["semantic_subject"],
                    "source_context_ref": row["source_context_ref"],
                    "_repository_path": "",
                    "_parent_sha": "",
                }
            )

    run_dir = root / "study/runs/v007-full-repro-2026"
    acquisition = {row["project"]: row for row in _read_csv(run_dir / "status/acquisition.csv")}
    snapshot_index = {
        row["repository"]: row["canonical_occurrences"]
        for row in _read_csv(run_dir / "raw/raw-output-index.csv")
    }
    (
        review_candidates,
        review_population_by_rule,
        missing_parent_by_rule,
        missing_required_parent_by_rule,
        review_source_count_by_rule_repository,
        review_missing_parent_by_rule_repository,
        review_missing_required_parent_by_rule_repository,
        review_source_count_by_repository,
        review_missing_parent_by_repository,
        review_missing_required_parent_by_repository,
    ) = load_review_candidates(root, split_rows, acquisition, snapshot_index)
    review_context_eligible_by_rule = Counter(row["rule_id"] for row in review_candidates)
    for candidate in review_candidates:
        candidate["_rule_population_count"] = str(review_context_eligible_by_rule[candidate["rule_id"]])

    all_candidates_by_family: dict[str, list[dict[str, str]]] = defaultdict(list)
    population_by_family_rule: dict[str, Counter[str]] = defaultdict(Counter)
    for family_id, rows in static_candidates.items():
        for row in rows:
            row["selection_rank_sha256"] = pilot_rank(family_id, row["rule_id"], row["occurrence_id"])
            population_by_family_rule[family_id][row["rule_id"]] += 1
            all_candidates_by_family[family_id].append(row)
    for row in review_candidates:
        family_id = "review_history"
        row["selection_rank_sha256"] = pilot_rank(family_id, row["rule_id"], row["occurrence_id"])
        all_candidates_by_family[family_id].append(row)
        population_by_family_rule[family_id][row["rule_id"]] = review_context_eligible_by_rule[row["rule_id"]]

    selected_by_family: dict[str, list[dict[str, str]]] = {}
    rare_exclusions: dict[str, list[str]] = {}
    candidate_counts: dict[str, dict[str, int]] = {}
    for family_id in FAMILY_ORDER:
        rows = all_candidates_by_family.get(family_id, [])
        selected, rare = select_family(rows, population_by_family_rule[family_id])
        selected_by_family[family_id] = selected
        rare_exclusions[family_id] = rare
        candidate_counts[family_id] = dict(
            sorted(Counter(row["rule_id"] for row in rows).items())
        )

    eligible_by_family_repository: dict[str, dict[str, int]] = {}
    selected_by_family_repository: dict[str, dict[str, int]] = {}
    excluded_by_family_repository: dict[str, dict[str, int]] = {}
    eligible_by_family_rule_repository: dict[str, dict[str, dict[str, int]]] = {}
    selected_by_family_rule_repository: dict[str, dict[str, dict[str, int]]] = {}
    excluded_by_family_rule_repository: dict[str, dict[str, dict[str, int]]] = {}
    for family_id in FAMILY_ORDER:
        eligible_repo_counts = Counter(
            row["repository"] for row in all_candidates_by_family.get(family_id, [])
        )
        selected_repo_counts = Counter(
            row["repository"] for row in selected_by_family[family_id]
        )
        eligible_by_family_repository[family_id] = dict(sorted(eligible_repo_counts.items()))
        selected_by_family_repository[family_id] = dict(sorted(selected_repo_counts.items()))
        excluded_by_family_repository[family_id] = dict(
            sorted((eligible_repo_counts - selected_repo_counts).items())
        )

        eligible_rule_repo_counts: dict[str, Counter[str]] = defaultdict(Counter)
        selected_rule_repo_counts: dict[str, Counter[str]] = defaultdict(Counter)
        for row in all_candidates_by_family.get(family_id, []):
            eligible_rule_repo_counts[row["rule_id"]][row["repository"]] += 1
        for row in selected_by_family[family_id]:
            selected_rule_repo_counts[row["rule_id"]][row["repository"]] += 1
        eligible_by_family_rule_repository[family_id] = {
            rule: dict(sorted(counts.items()))
            for rule, counts in sorted(eligible_rule_repo_counts.items())
        }
        selected_by_family_rule_repository[family_id] = {
            rule: dict(sorted(counts.items()))
            for rule, counts in sorted(selected_rule_repo_counts.items())
        }
        excluded_by_family_rule_repository[family_id] = {
            rule: dict(sorted((counts - selected_rule_repo_counts[rule]).items()))
            for rule, counts in sorted(eligible_rule_repo_counts.items())
        }

    def nested_pair_counts(counts: Counter[tuple[str, str]]) -> dict[str, dict[str, int]]:
        nested: dict[str, dict[str, int]] = defaultdict(dict)
        for (rule_id, repository), count in sorted(counts.items()):
            nested[rule_id][repository] = count
        return {rule: dict(repositories) for rule, repositories in sorted(nested.items())}

    review_source_by_rule_repository = nested_pair_counts(review_source_count_by_rule_repository)
    review_missing_by_rule_repository = nested_pair_counts(review_missing_parent_by_rule_repository)
    review_required_missing_by_rule_repository = nested_pair_counts(
        review_missing_required_parent_by_rule_repository
    )
    selection_audit_columns = [
        "family_id",
        "rule_id",
        "repository",
        "source_candidate_count",
        "context_eligible_count",
        "missing_first_parent_count",
        "parent_required_but_missing_count",
        "selected_count",
        "excluded_context_eligible_count",
        "selection_note",
    ]
    selection_audit_rows: list[dict[str, str]] = []
    for family_id in FAMILY_ORDER:
        if family_id == "review_history":
            all_pairs = set(review_source_count_by_rule_repository) | {
                (rule, repository)
                for rule, repositories in eligible_by_family_rule_repository[family_id].items()
                for repository in repositories
            }
            for rule_id, repository in sorted(all_pairs):
                source_count = review_source_count_by_rule_repository[(rule_id, repository)]
                missing_count = review_missing_parent_by_rule_repository[(rule_id, repository)]
                required_missing_count = review_missing_required_parent_by_rule_repository[(rule_id, repository)]
                eligible_count = source_count - required_missing_count
                recorded_eligible = eligible_by_family_rule_repository[family_id].get(rule_id, {}).get(repository, 0)
                if eligible_count != recorded_eligible:
                    raise RuntimeError(
                        f"review-history context-eligibility audit mismatch for {rule_id} in {repository}"
                    )
                selected_count = selected_by_family_rule_repository[family_id].get(rule_id, {}).get(repository, 0)
                selection_audit_rows.append(
                    {
                        "family_id": family_id,
                        "rule_id": rule_id,
                        "repository": repository,
                        "source_candidate_count": str(source_count),
                        "context_eligible_count": str(eligible_count),
                        "missing_first_parent_count": str(missing_count),
                        "parent_required_but_missing_count": str(required_missing_count),
                        "selected_count": str(selected_count),
                        "excluded_context_eligible_count": str(eligible_count - selected_count),
                        "selection_note": (
                            "exact target commit message is sufficient"
                            if rule_id in REVIEW_MESSAGE_ONLY_RULE_IDS
                            else "actual first-parent diff required"
                        ),
                    }
                )
        else:
            for rule_id, repositories in sorted(eligible_by_family_rule_repository[family_id].items()):
                for repository, eligible_count in sorted(repositories.items()):
                    selected_count = selected_by_family_rule_repository[family_id].get(rule_id, {}).get(repository, 0)
                    note = "rare rule protected" if rule_id in rare_exclusions[family_id] else "deterministic family/rule/repository selection"
                    selection_audit_rows.append(
                        {
                            "family_id": family_id,
                            "rule_id": rule_id,
                            "repository": repository,
                            "source_candidate_count": str(eligible_count),
                            "context_eligible_count": str(eligible_count),
                            "missing_first_parent_count": "0",
                            "parent_required_but_missing_count": "0",
                            "selected_count": str(selected_count),
                            "excluded_context_eligible_count": str(eligible_count - selected_count),
                            "selection_note": note,
                        }
                    )
    selection_audit_bytes = _write_csv_bytes(selection_audit_rows, selection_audit_columns)

    acquisition_cache: dict[str, Path] = {}
    for repo, row in acquisition.items():
        acquisition_cache[repo] = _repo_path(root, row)

    master_rows: list[dict[str, str]] = []
    reviewer_rows: list[dict[str, str]] = []
    ai_shadow_rows: list[dict[str, str]] = []
    context_payloads: dict[str, bytes] = {}
    family_rule_counts: dict[str, dict[str, int]] = {}
    family_repo_counts: dict[str, int] = {}
    family_selected_counts: dict[str, int] = {}
    selected_identities: set[str] = set()
    serial_by_family = Counter()
    for family_id in FAMILY_ORDER:
        family_rule_counts[family_id] = dict(
            sorted(Counter(row["rule_id"] for row in selected_by_family[family_id]).items())
        )
        family_repo_counts[family_id] = len(
            {row["repository"] for row in selected_by_family[family_id]}
        )
        family_selected_counts[family_id] = len(selected_by_family[family_id])
        for candidate in selected_by_family[family_id]:
            if candidate["repository"] not in split_rows or split_rows[candidate["repository"]]["split"] != "calibration":
                raise RuntimeError("pilot selection contains a non-calibration repository")
            if candidate["occurrence_id"] in selected_identities:
                raise RuntimeError("pilot occurrence was selected more than once")
            selected_identities.add(candidate["occurrence_id"])
            serial_by_family[family_id] += 1
            sample_id = f"V007PILOT-{family_id.upper()}-{serial_by_family[family_id]:03d}"
            candidate["sample_id"] = sample_id
            codebook_path = FAMILY_CODEBOOKS[family_id]
            repo_path = acquisition_cache[candidate["repository"]]
            if family_id == "review_history":
                context_text, inline_context = _review_context(
                    candidate, FAMILY_NAMES[family_id], codebook_path, repo_path
                )
            else:
                context_text, inline_context = _static_context(
                    candidate, FAMILY_NAMES[family_id], codebook_path, repo_path
                )
            context_rel = f"samples/agreement-pilot/context/{sample_id}.md"
            context_payloads[context_rel] = context_text.encode("utf-8")
            visible = {
                "sample_id": sample_id,
                "occurrence_id": candidate["occurrence_id"],
                "panel": candidate["panel"],
                "rule_id": candidate["rule_id"],
                "concept_id": candidate["concept_id"],
                "review_family": FAMILY_NAMES[family_id],
                "codebook_path": codebook_path,
                "review_question": FAMILY_QUESTIONS[family_id],
                "repository": candidate["repository"],
                "commit_sha": candidate["commit_sha"],
                "path": candidate["path"],
                "line_start": candidate["line_start"],
                "line_end": candidate["line_end"],
                "object_kind": candidate["object_kind"],
                "object_id": candidate["object_id"],
                "source_context": inline_context,
                "context_bundle_path": context_rel,
            }
            reviewer_row = {**visible, **{column: "" for column in REVIEWER_DECISION_COLUMNS}}
            reviewer_rows.append(reviewer_row)
            ai_shadow_rows.append({**visible, **{column: "" for column in AI_DECISION_COLUMNS}})
            master_rows.append(
                {
                    **visible,
                    "source_occurrence_id": candidate["source_occurrence_id"],
                    "selection_rank_sha256": candidate["selection_rank_sha256"],
                    "is_agreement_pilot": "true",
                    "eligible_for_performance_scoring": "false",
                    **{column: "" for column in REVIEWER_DECISION_COLUMNS},
                }
            )

    master_bytes = _write_csv_bytes(master_rows, MASTER_COLUMNS)
    reviewer_a_bytes = _write_csv_bytes(
        [dict(row) for row in reviewer_rows], REVIEWER_COLUMNS
    )
    reviewer_b_bytes = _write_csv_bytes(
        [dict(row) for row in reviewer_rows], REVIEWER_COLUMNS
    )
    ai_shadow_bytes = _write_csv_bytes(ai_shadow_rows, AI_SHADOW_COLUMNS)
    if reviewer_a_bytes != reviewer_b_bytes:
        raise RuntimeError("independent reviewer forms do not have identical visible rows")
    for context_rel, payload in context_payloads.items():
        context_text = payload.decode("utf-8")
        reprocessed_context = redact_sensitive_text(context_text)
        if reprocessed_context != context_text:
            changed_lines = [
                index
                for index, (before, after) in enumerate(
                    zip(context_text.split("\n"), reprocessed_context.split("\n")), start=1
                )
                if before != after
            ]
            raise RuntimeError(
                f"context redaction audit failed for {context_rel}; changed line numbers: {changed_lines[:20]}"
            )
    for row in reviewer_rows:
        if redact_sensitive_text(row["source_context"]) != row["source_context"]:
            raise RuntimeError(f"inline context redaction audit failed for {row['sample_id']}")
    static_rare_candidates = {
        family: rare_exclusions[family]
        for family in FAMILY_ORDER
        if rare_exclusions[family]
    }
    manifest: dict[str, Any] = {
        "schema_version": 1,
        "created_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source_commit": _git(root, "rev-parse", "HEAD").stdout.strip(),
        "script_commit": _git(root, "rev-parse", "HEAD").stdout.strip(),
        "script_sha256": sha256_file(Path(__file__).resolve()),
        "row_count": len(master_rows),
        "unique_repository_count": len({row["repository"] for row in master_rows}),
        "pilot_seed": PILOT_SEED,
        "target_per_family": TARGET_PER_FAMILY,
        "purpose": "codebook calibration and independent human agreement only; not performance scoring",
        "inputs": {
            "identity_index_sha256": IDENTITY_SHA256,
            "repository_split_sha256": SPLIT_SHA256,
            "rule_family_map_sha256": FAMILY_MAP_SHA256,
            "source_run": "v007-full-repro-2026",
            "pilot_codebooks_sha256": {
                relative: sha256_file(validation_dir / relative)
                for relative in PILOT_CODEBOOK_INPUTS
            },
            "pilot_codebook_bundle_sha256": sha256_bytes(json.dumps(
                {
                    relative: sha256_file(validation_dir / relative)
                    for relative in PILOT_CODEBOOK_INPUTS
                },
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")),
        },
        "selection": {
            "family_order": FAMILY_ORDER,
            "rank_formula": "SHA256('v007-human-pilot-v1|<family_id>|<rule_id>|<occurrence_id>')",
            "round_robin_rule_order": "lexical rule_id order; first pass one item/repository across a family; second pass permits another item/repository if needed",
            "rare_rule_policy": "rules with fewer than five calibration candidates are excluded from the pilot and listed; they remain available for later census/special handling",
            "eligible_candidate_counts_by_family_rule": candidate_counts,
            "eligible_candidate_counts_by_family_repository": eligible_by_family_repository,
            "selected_counts_by_family_repository": selected_by_family_repository,
            "excluded_eligible_counts_by_family_repository": excluded_by_family_repository,
            "eligible_candidate_counts_by_family_rule_repository": eligible_by_family_rule_repository,
            "selected_counts_by_family_rule_repository": selected_by_family_rule_repository,
            "excluded_eligible_counts_by_family_rule_repository": excluded_by_family_rule_repository,
            "selected_counts_by_family": family_selected_counts,
            "selected_counts_by_family_rule": family_rule_counts,
            "distinct_repositories_by_family": family_repo_counts,
            "rare_rule_exclusions": static_rare_candidates,
            "review_history_source_candidate_counts_by_rule": dict(sorted(review_population_by_rule.items())),
            "review_history_source_candidate_counts_by_repository": dict(
                sorted(review_source_count_by_repository.items())
            ),
            "review_history_source_candidate_counts_by_rule_repository": review_source_by_rule_repository,
            "review_history_missing_first_parent_by_rule": dict(sorted(missing_parent_by_rule.items())),
            "review_history_missing_first_parent_by_repository": dict(
                sorted(review_missing_parent_by_repository.items())
            ),
            "review_history_missing_first_parent_by_rule_repository": review_missing_by_rule_repository,
            "review_history_missing_required_first_parent_by_rule": dict(
                sorted(missing_required_parent_by_rule.items())
            ),
            "review_history_missing_required_first_parent_by_repository": dict(
                sorted(review_missing_required_parent_by_repository.items())
            ),
            "review_history_missing_required_first_parent_by_rule_repository": review_required_missing_by_rule_repository,
            "review_history_message_only_without_parent_by_rule": {
                rule: max(0, missing_parent_by_rule[rule] - missing_required_parent_by_rule[rule])
                for rule in sorted(missing_parent_by_rule)
            },
            "review_history_context_eligible_by_rule": dict(sorted(review_context_eligible_by_rule.items())),
            "review_history_context_eligible_by_repository": dict(
                sorted(Counter(row["repository"] for row in review_candidates).items())
            ),
            "review_history_first_parent_available_by_rule": {
                rule: review_population_by_rule[rule] - missing_parent_by_rule[rule]
                for rule in sorted(review_population_by_rule)
            },
            "review_history_limit": "All calibration target commits must exist. The actual first parent/diff is required only for diff-dependent rules; commit-message-format and missing-bug-reference use the exact target commit message and remain eligible without a parent. Detector base=null/root-diff fallbacks are never used. This is a context-availability-limited pool, not a claim that other findings are semantically false.",
        },
        "heldout_protection": {
            "heldout_contexts_opened": 0,
            "heldout_occurrence_rows_emitted": 0,
            "selected_rows_from_heldout": 0,
            "heldout_split_rows_used_only_for_repository_exclusion": True,
        },
        "reviewer_blinding": {
            "forms_have_identical_bytes": reviewer_a_bytes == reviewer_b_bytes,
            "decision_columns_blank": True,
            "detector_confidence_or_severity_in_forms": False,
            "other_reviewer_or_ai_labels_in_forms": False,
            "sampling_weights_or_prevalence_in_forms": False,
            "ai_shadow_template_is_blank": not any(
                row.get(column, "") for row in ai_shadow_rows for column in AI_DECISION_COLUMNS
            ),
            "source_excerpt_secret_redaction": "sensitive-key literals, PEM private keys, and recognizable provider tokens redacted; public default credential strings may remain for rule assessment",
        },
        "human_labels_created": False,
        "ai_labels_created": False,
        "eligible_for_performance_scoring": False,
        "selection_audit_row_count": len(selection_audit_rows),
    }
    if dry_run:
        return manifest

    output_files = {
        validation_dir / "samples/agreement-pilot/agreement-pilot-master.csv": master_bytes,
        validation_dir / "samples/agreement-pilot/pilot-selection-audit.csv": selection_audit_bytes,
        validation_dir / "reviewers/reviewer-a/agreement-pilot.csv": reviewer_a_bytes,
        validation_dir / "reviewers/reviewer-b/agreement-pilot.csv": reviewer_b_bytes,
        validation_dir / "reviewers/ai-shadow/agreement-pilot.csv": ai_shadow_bytes,
        **{validation_dir / path: content for path, content in context_payloads.items()},
    }
    manifest["files"] = {
        str(path.relative_to(validation_dir)): {
            "sha256": sha256_bytes(content),
            "bytes": len(content),
            "rows": (
                len(selection_audit_rows)
                if path.name == "pilot-selection-audit.csv"
                else len(master_rows) if path.name.endswith(".csv") else None
            ),
        }
        for path, content in sorted(output_files.items(), key=lambda pair: str(pair[0]))
    }
    manifest["reviewer_forms_identical_sha256"] = sha256_bytes(reviewer_a_bytes)
    manifest["ai_shadow_template_sha256"] = sha256_bytes(ai_shadow_bytes)
    manifest_bytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    # Preflight every target before writing any output. Existing human edits are never overwritten.
    for path, content in output_files.items():
        if path.exists() and path.read_bytes() != content:
            raise RuntimeError(f"refusing to overwrite existing pilot/context artifact: {path}")
    manifest_path = validation_dir / "samples/agreement-pilot/agreement-pilot-manifest.json"
    if manifest_path.exists() and manifest_path.read_bytes() != manifest_bytes:
        raise RuntimeError(f"refusing to overwrite existing pilot manifest: {manifest_path}")
    for path, content in output_files.items():
        _immutable_write(path, content)
    _immutable_write(manifest_path, manifest_bytes)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--validation-dir", type=Path, default=Path("study/validation-v007-human"))
    parser.add_argument("--dry-run", action="store_true", help="select and audit candidates without writing reviewer artifacts")
    args = parser.parse_args()
    root = args.root.resolve()
    validation_dir = args.validation_dir
    if not validation_dir.is_absolute():
        validation_dir = root / validation_dir
    manifest = build_agreement_pilot(root, validation_dir, dry_run=args.dry_run)
    summary = {
        "pilot_seed": manifest["pilot_seed"],
        "dry_run": args.dry_run,
        "target_per_family": manifest["target_per_family"],
        "selected_counts_by_family": manifest["selection"]["selected_counts_by_family"],
        "distinct_repositories_by_family": manifest["selection"]["distinct_repositories_by_family"],
        "review_history_missing_first_parent_by_rule": manifest["selection"]["review_history_missing_first_parent_by_rule"],
        "review_history_missing_required_first_parent_by_rule": manifest["selection"]["review_history_missing_required_first_parent_by_rule"],
        "heldout_protection": manifest["heldout_protection"],
        "human_labels_created": manifest["human_labels_created"],
        "ai_labels_created": manifest["ai_labels_created"],
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
