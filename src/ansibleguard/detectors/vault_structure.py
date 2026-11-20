"""Detect roles with too many inline vault values (H4)."""

from __future__ import annotations

import re
from pathlib import Path


_VAULT_TAG_RE = re.compile(r"!\s*vault\s*\|", re.IGNORECASE)

INLINE_VAULT_THRESHOLD = 3


def _find_role_root(yaml_file_path):
    path = Path(yaml_file_path).resolve()
    for parent in (path.parent, *path.parent.parents):
        if (parent / "tasks").is_dir():
            return parent
        if (parent / ".git").is_dir():
            break
    return None


def _role_anchor(yaml_file_path):
    """Return True only when the file is tasks/main.yml — the role anchor."""
    path = Path(yaml_file_path)
    return path.name == "main.yml" and path.parent.name == "tasks"


def _count_inline_vault_values(role_root, repository_context=None):
    """Count !vault | occurrences across all YAML files in the role."""
    if repository_context is not None:
        try:
            role_root = Path(role_root).resolve()
            return sum(
                len(_VAULT_TAG_RE.findall(document.source_text))
                for path, document in repository_context.parsed_documents.items()
                if path.is_relative_to(role_root)
            )
        except (AttributeError, OSError):
            # Keep the standalone filesystem fallback for partial contexts.
            pass
    count = 0
    for yaml_file in role_root.rglob("*.yml"):
        try:
            text = yaml_file.read_text(encoding="utf-8")
            count += len(_VAULT_TAG_RE.findall(text))
        except Exception:
            continue
    return count


def detect_vault_inline_overload(yaml_file_path, repository_context=None):
    """Flag roles that have more than INLINE_VAULT_THRESHOLD inline vault variables.

    Fires once per role, anchored to tasks/main.yml.

    Returns:
        (count, details)
    """
    if not _role_anchor(yaml_file_path):
        return 0, []

    role_root = _find_role_root(yaml_file_path)
    if role_root is None:
        return 0, []

    vault_count = _count_inline_vault_values(role_root, repository_context)
    if vault_count <= INLINE_VAULT_THRESHOLD:
        return 0, []

    return 1, [
        {
            "task_name": f"role:{role_root.name}",
            "line": 1,
            "message": (
                f"Role '{role_root.name}' has {vault_count} inline !vault | values "
                f"(threshold: {INLINE_VAULT_THRESHOLD}). "
                "Consider consolidating encrypted values into a dedicated "
                "vars/vault.yml or defaults/vault.yml file."
            ),
        }
    ]
