"""Detect role variables not prefixed with the role name (C5)."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

_VAR_DEF_RE = re.compile(r"^\s{0,4}([a-z][a-zA-Z0-9_]*)(?:\s*:)", re.MULTILINE)
_ROLE_BOUNDARY_DIRS = frozenset({"tasks", "defaults", "vars", "handlers", "meta", "templates", "files"})


def _role_name_for(yaml_file_path):
    """Derive the role name from the file's location, or None if not in a role."""
    path = Path(yaml_file_path).resolve()
    for parent in (path.parent, *path.parent.parents):
        if parent.name in _ROLE_BOUNDARY_DIRS:
            role_root = parent.parent
            return role_root.name
        if (parent / ".git").is_dir():
            break
    return None


def _is_defaults_or_vars_file(yaml_file_path):
    path = Path(yaml_file_path)
    return path.parent.name in ("defaults", "vars") and path.suffix in (".yml", ".yaml")


def detect_variable_naming_convention(yaml_file_path, parsed_document=None):
    """Flag top-level role variables that lack the role-name prefix.

    Only runs on defaults/ and vars/ YAML files inside a recognised role.
    Skips variables whose names start with an underscore (internal/private).

    Returns:
        (count, details)
    """
    if not _is_defaults_or_vars_file(yaml_file_path):
        return 0, []

    role_name = _role_name_for(yaml_file_path)
    if not role_name:
        return 0, []

    # Ansible variable identifiers cannot contain role-name punctuation.
    # Accept the underscore-normalized form used by ansible-lint and the
    # compact form used by established roles such as RHEL8-CIS.
    normalized_role = re.sub(r"[^a-z0-9]+", "_", role_name.lower()).strip("_")
    compact_role = re.sub(r"[^a-z0-9]", "", role_name.lower())
    prefixes = tuple(
        dict.fromkeys(
            prefix + "_"
            for prefix in (normalized_role, compact_role)
            if prefix
        )
    )
    expected_prefix = prefixes[0] if prefixes else role_name + "_"

    if parsed_document is not None:
        content = parsed_document.source_text
        loaded = parsed_document.document or {}
    else:
        try:
            content = Path(yaml_file_path).read_text(encoding="utf-8")
            loaded = yaml.safe_load(content) or {}
        except Exception:
            return 0, []

    if not isinstance(loaded, dict):
        return 0, []

    details = []
    for key in loaded:
        name = str(key)
        if name.startswith("_") or any(
            name.lower().startswith(prefix) for prefix in prefixes
        ):
            continue
        # Heuristic line location: find first occurrence in source
        line = 1
        for i, src_line in enumerate(content.splitlines(), 1):
            if re.match(rf"^{re.escape(name)}\s*:", src_line):
                line = i
                break
        details.append(
            {
                "task_name": name,
                "line": line,
                "message": (
                    f"Variable '{name}' is not prefixed with the role name "
                    f"(expected a '{expected_prefix}' role prefix)."
                ),
            }
        )

    return len(details), details
