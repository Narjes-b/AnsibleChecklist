"""Compare canonical base/head occurrences for pull-request ratcheting."""

from __future__ import annotations

import re
from collections import Counter

from .findings import finding_category, finding_policy, is_optional_finding

_DEFAULTS_VARS_FILE_RE = re.compile(r"(?:defaults|vars)/[^/]+\.ya?ml$")
_TOP_LEVEL_KEY_RE = re.compile(r"^([a-z][a-zA-Z0-9_]*):")
_TASK_NAME_RE = re.compile(r"^-?\s*name\s*:\s*(.*)$")
_HUNK_HEADER_RE = re.compile(r"@@\s+-(\d+)(?:,\d+)?\s+\+(\d+)(?:,\d+)?\s+@@")


def detect_breaking_changes_from_diff(diff_text):
    """F3: Scan a git diff for potential breaking changes.

    Detects:
    - Task name changes (breaks --start-at-task and task-level --tags)
    - Top-level variable removals from defaults/ or vars/ (breaks role API)

    Returns a list of {type, file, line, message} dicts.
    """
    if not diff_text:
        return []

    breaking = []
    current_file = None
    is_defaults_file = False
    old_line = 1
    new_line = 1
    pending_removed_names = []

    for raw_line in diff_text.splitlines():
        if raw_line.startswith("+++ "):
            current_file = raw_line[4:].strip().removeprefix("b/")
            is_defaults_file = bool(
                _DEFAULTS_VARS_FILE_RE.search(current_file or "")
            )
            pending_removed_names = []
        elif raw_line.startswith("@@ "):
            pending_removed_names = []
            match = _HUNK_HEADER_RE.search(raw_line)
            old_line = int(match.group(1)) if match else 1
            new_line = int(match.group(2)) if match else 1
        elif raw_line.startswith("-") and not raw_line.startswith("---"):
            content = raw_line[1:]
            stripped = content.lstrip()
            name_match = _TASK_NAME_RE.match(stripped)
            if name_match:
                name_val = name_match.group(1).strip().strip("\"'")
                pending_removed_names.append((name_val, old_line))
            elif is_defaults_file and not content.startswith(" "):
                m = _TOP_LEVEL_KEY_RE.match(content)
                if m:
                    breaking.append({
                        "type": "defaults-variable-removed",
                        "file": current_file,
                        "line": new_line,
                        "message": (
                            f"Variable '{m.group(1)}' removed from '{current_file}' — "
                            "potential breaking change for role consumers."
                        ),
                    })
            # F4: Idempotency guard removals in task files
            elif not is_defaults_file and stripped.startswith((
                "changed_when: false",
                "changed_when: 'false'",
                "changed_when: \"false\"",
                "creates:",
                "removes:",
            )):
                key = stripped.split(":")[0].strip()
                breaking.append({
                    "type": "idempotency-guard-removed",
                    "file": current_file,
                    "line": new_line,
                    "message": (
                        f"Idempotency guard '{key}:' removed from '{current_file}' — "
                        "task may now report changed on every run."
                    ),
                })
            old_line += 1
        elif raw_line.startswith("+") and not raw_line.startswith("+++"):
            content = raw_line[1:]
            stripped = content.lstrip()
            name_match = _TASK_NAME_RE.match(stripped)
            if name_match and pending_removed_names:
                new_name = name_match.group(1).strip().strip("\"'")
                old_name, removed_line = pending_removed_names.pop(0)
                if old_name and new_name and old_name != new_name:
                    breaking.append({
                        "type": "task-renamed",
                        "file": current_file,
                        "line": new_line,
                        "message": (
                            f"Task renamed from '{old_name}' to '{new_name}' — "
                            "potential breaking change for --start-at-task and --tags."
                        ),
                    })
            # F4: ignore_errors: true addition (reliability regression)
            elif not is_defaults_file and stripped.startswith((
                "ignore_errors: true",
                "ignore_errors: yes",
                "ignore_errors: 'true'",
                "ignore_errors: \"true\"",
            )):
                breaking.append({
                    "type": "error-suppression-added",
                    "file": current_file,
                    "line": new_line,
                    "message": (
                        f"'ignore_errors: true' added in '{current_file}' — "
                        "task failures will be silently ignored; consider handling "
                        "the error explicitly with register + failed_when."
                    ),
                })
            new_line += 1
        elif raw_line.startswith(" "):
            old_line += 1
            new_line += 1

    return breaking

# F1: per-concept-id weight for precision-weighted ratchet scoring.
# High-precision security rules have weight > 1; low-precision style rules < 1.
RATCHET_WEIGHTS = {
    "hardcoded-secret": 10.0,
    "credential-log-exposure": 5.0,
    "credentials-leaking-in-log": 5.0,
    "insecure-permissions": 3.0,
    "missing-validate-certs": 3.0,
    "become-scope-too-broad": 2.0,
    "missing-handler": 2.0,
    "overriden-keys": 2.0,
    "incohesive-play": 0.5,
    "incohesive-playbook": 0.5,
    "yaml-formatting": 0.2,
    "fqcn-migration": 0.2,
    "missing-tags": 0.0,
}


def _ratchet_weight(item):
    return RATCHET_WEIGHTS.get(item.get("concept_id", ""), 1.0)


_SECURITY_CONCEPT_IDS = frozenset({
    "hardcoded-secret",
    "credential-log-exposure",
    "credentials-leaking-in-log",
    "insecure-permissions",
    "missing-validate-certs",
    "become-scope-too-broad",
})


def detect_security_regressions(comparison):
    """Return security-level findings introduced in HEAD that represent regressions.

    Complements evaluate_policy() by listing only security-category findings so
    callers can surface them in PR comments without scanning the full finding list.
    """
    return [
        item
        for item in comparison.get("introduced", [])
        if item.get("concept_id") in _SECURITY_CONCEPT_IDS
        or item.get("finding_category") == "security"
    ]


def _shared_fingerprint(left, right):
    return bool(
        set(left.get("evidence_fingerprints", ()))
        & set(right.get("evidence_fingerprints", ()))
    )


def _same_semantics(left, right):
    return (
        left.get("concept_id") == right.get("concept_id")
        and left.get("scan_mode", "source") == right.get("scan_mode", "source")
        and left.get("semantic_key") == right.get("semantic_key")
    )


def _same_content_semantics(left, right):
    left_subject = left.get("semantic_subject")
    right_subject = right.get("semantic_subject")
    weak_subjects = {None, "", "location", "semantic_subject:location"}
    if left_subject in weak_subjects or right_subject in weak_subjects:
        return False
    left_structure = left.get("task_fingerprint")
    right_structure = right.get("task_fingerprint")
    if not left_structure or left_structure != right_structure:
        return False
    return (
        left.get("concept_id") == right.get("concept_id")
        and left.get("scan_mode", "source") == right.get("scan_mode", "source")
        and bool(left.get("content_semantic_key"))
        and left.get("content_semantic_key") == right.get("content_semantic_key")
    )


def _same_renamed_subject(left, right, renamed_files):
    subject = left.get("semantic_subject")
    return (
        renamed_files.get(left.get("file")) == right.get("file")
        and left.get("concept_id") == right.get("concept_id")
        and left.get("scan_mode", "source") == right.get("scan_mode", "source")
        and bool(subject)
        and subject != "location"
        and subject == right.get("semantic_subject")
        and set(left.get("native_rules", ()))
        == set(right.get("native_rules", ()))
    )


def _same_detector_shape(left, right):
    return (
        left.get("concept_id") != "hardcoded-secret"
        and right.get("concept_id") != "hardcoded-secret"
        and left.get("concept_id") == right.get("concept_id")
        and left.get("scan_mode", "source") == right.get("scan_mode", "source")
        and left.get("file") == right.get("file")
        and set(left.get("native_rules", ())) == set(right.get("native_rules", ()))
    )


def _decorate_head(item, changed_lines=None, changed_files=None):
    item = dict(item)
    item["finding_category"] = finding_category(item)
    item["policy"] = finding_policy(item)
    if changed_lines is None and changed_files is None:
        return item
    changed_lines = changed_lines or {}
    changed_files = set(changed_files or changed_lines)
    lines = changed_lines.get(item.get("file", ""), set())
    item["on_changed_line"] = int(item.get("line", 1)) in lines
    # Base/head comparison proves that the occurrence was introduced by the
    # branch. It does not claim that its own source line was edited.
    item["caused_by_diff"] = True
    item["in_changed_file"] = item.get("file") in changed_files
    return item


def map_base_line(line_maps, file, line):
    """Map a base line through ``git diff -U0`` hunks to its head line.

    ``line_maps`` is ``{path: [(old_start, old_count, new_start, new_count)]}``.
    Returns None when the base line lies in a deleted or rewritten range.
    Files absent from the map are unchanged, so the line is unchanged.
    """
    hunks = (line_maps or {}).get(file)
    if not hunks:
        return line
    offset = 0
    for old_start, old_count, new_start, new_count in hunks:
        if old_count and old_start <= line < old_start + old_count:
            return None
        # With a zero count, git names the line *before* the empty range, so
        # the first line after each range is start + 1.
        old_next = old_start + old_count if old_count else old_start + 1
        new_next = new_start + new_count if new_count else new_start + 1
        if line < old_next:
            break
        offset = new_next - old_next
    return line + offset


def compare_occurrences(
    base_occurrences,
    head_occurrences,
    *,
    changed_lines=None,
    changed_files=None,
    renamed_files=None,
    line_maps=None,
):
    """Classify exact, moved, introduced, fixed, and uncertain occurrences."""
    base_remaining = {item["occurrence_id"]: item for item in base_occurrences}
    head_remaining = {item["occurrence_id"]: item for item in head_occurrences}
    renamed_files = dict(renamed_files or {})
    unchanged = []
    for occurrence_id in sorted(set(base_remaining) & set(head_remaining)):
        base_item, head_item = base_remaining[occurrence_id], head_remaining[occurrence_id]
        if line_maps is not None and map_base_line(
            line_maps, base_item.get("file"), int(base_item.get("line") or 1)
        ) != int(head_item.get("line") or 1):
            # Same identity at the same line number, but the diff moved the
            # base line elsewhere: a different task now occupies that line.
            continue
        unchanged.append(
            {
                "base": base_remaining.pop(occurrence_id),
                "head": head_remaining.pop(occurrence_id),
                "match": "exact",
            }
        )

    moved = []
    tiers = [
        ("native-fingerprint", _shared_fingerprint),
        ("semantic", _same_semantics),
        ("semantic-rename", _same_content_semantics),
    ]
    if renamed_files:
        tiers.append(
            ("git-rename-subject", lambda base, head: _same_renamed_subject(base, head, renamed_files))
        )
    for head_id, head in list(head_remaining.items()):
        head_line = int(head.get("line") or 1)

        def image(base):
            if base.get("file") != head.get("file"):
                return None
            return map_base_line(line_maps, base.get("file"), int(base.get("line") or 1))

        chosen, match = [], ""
        for tier_name, predicate in tiers:
            candidates = [
                (base_id, base) for base_id, base in base_remaining.items()
                if predicate(base, head)
            ]
            match = tier_name
            if candidates and line_maps is not None:
                # The diff says where every surviving base line went. Prefer
                # the candidate whose base line maps onto this head line;
                # otherwise only a candidate whose base line was deleted or
                # rewritten can have moved here (a line that survives
                # elsewhere is still there). If the gate empties this tier,
                # weaker tiers are tried.
                exact = [(base_id, base) for base_id, base in candidates if image(base) == head_line]
                if exact:
                    if len(candidates) > 1:
                        match = f"{tier_name}-line-mapped"
                    candidates = exact
                else:
                    candidates = [
                        (base_id, base) for base_id, base in candidates
                        if base.get("file") != head.get("file") or image(base) is None
                    ]
            if candidates:
                chosen = candidates
                break
        if len(chosen) != 1:
            continue
        base_id, base = chosen[0]
        moved.append(
            {
                "base": base_remaining.pop(base_id),
                "head": head_remaining.pop(head_id),
                "match": match,
            }
        )

    uncertain = []
    for head_id, head in list(head_remaining.items()):
        candidates = [
            (base_id, base)
            for base_id, base in base_remaining.items()
            if _same_detector_shape(base, head)
        ]
        if len(candidates) != 1:
            continue
        base_id, _ = candidates[0]
        uncertain.append(
            {
                "base": base_remaining.pop(base_id),
                "head": head_remaining.pop(head_id),
                "match": "uncertain-detector-shape",
            }
        )

    ordering = lambda item: (
        item.get("file", ""),
        item.get("line", 1),
        item.get("concept_id", ""),
    )
    return {
        "schema_version": 1,
        "introduced": sorted(
            (
                _decorate_head(item, changed_lines, changed_files)
                for item in head_remaining.values()
            ),
            key=ordering,
        ),
        "unchanged": unchanged,
        "fixed": sorted(base_remaining.values(), key=ordering),
        "moved": moved,
        "uncertain": uncertain,
    }


def evaluate_policy(comparison, mode="observe"):
    if mode not in {"observe", "ratchet", "strict"}:
        raise ValueError("policy mode must be 'observe', 'ratchet', or 'strict'")
    introduced = comparison.get("introduced", [])
    actionable = [item for item in introduced if not is_optional_finding(item)]
    optional = [item for item in introduced if is_optional_finding(item)]
    # Optional-policy findings are reported but never block; an exposed
    # secret always blocks.
    blocking = [
        item
        for item in introduced
        if item.get("concept_id") == "hardcoded-secret"
        or (
            not is_optional_finding(item)
            and (
                (mode in {"ratchet", "strict"} and item.get("severity") == "error")
                or (mode == "strict" and item.get("severity") == "warning")
            )
        )
    ]
    return {
        "mode": mode,
        "conclusion": "failure" if blocking else "success",
        "blocking_occurrence_ids": [
            item["occurrence_id"] for item in blocking
        ],
        "counts": {
            key: len(comparison.get(key, []))
            for key in ("introduced", "unchanged", "fixed", "moved", "uncertain")
        } | {
            "introduced_actionable": len(actionable),
            "introduced_optional": len(optional),
        },
        "introduced_by_severity": dict(
            sorted(Counter(item.get("severity", "warning") for item in introduced).items())
        ),
        "introduced_by_category": dict(
            sorted(Counter(finding_category(item) for item in introduced).items())
        ),
        "optional_by_category": dict(
            sorted(Counter(finding_category(item) for item in optional).items())
        ),
        "weighted_ratchet_score": sum(
            _ratchet_weight(item)
            for item in actionable
        ),
        "security_regressions": [
            item["occurrence_id"]
            for item in introduced
            if item.get("concept_id") in _SECURITY_CONCEPT_IDS
            or item.get("finding_category") == "security"
        ],
    }
