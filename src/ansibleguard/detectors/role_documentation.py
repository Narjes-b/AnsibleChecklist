"""Detect Ansible roles that have no README.md file (C1)."""

from __future__ import annotations

from pathlib import Path


def _find_role_root(yaml_file_path):
    """Return the role root directory if the file lives inside a role, else None."""
    path = Path(yaml_file_path).resolve()
    for parent in (path.parent, *path.parent.parents):
        if (parent / "tasks").is_dir() and (parent / "tasks" / "main.yml").is_file():
            return parent
        if (parent / ".git").is_dir():
            break
    return None


def detect_role_readme_absent(yaml_file_path):
    """Flag a role that has no README.md at its root.

    Only fires once per role, anchored to tasks/main.yml so the finding
    has a stable, unique location.

    Returns:
        (count, details) where count is 0 or 1.
    """
    path = Path(yaml_file_path)
    if path.name != "main.yml" or path.parent.name != "tasks":
        return 0, []

    role_root = _find_role_root(yaml_file_path)
    if role_root is None:
        return 0, []

    for candidate in ("README.md", "README.rst", "README.txt", "README"):
        if (role_root / candidate).is_file():
            return 0, []

    return 1, [
        {
            "task_name": f"role:{role_root.name}",
            "line": 1,
            "message": (
                f"Role '{role_root.name}' has no README.md. "
                "Add documentation covering inputs, outputs, and example usage."
            ),
        }
    ]
