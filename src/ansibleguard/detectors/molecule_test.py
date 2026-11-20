"""Detects Ansible roles that lack a Molecule test scenario.

Molecule is the de-facto standard testing framework for Ansible roles.
A role without a molecule/ directory (or molecule/default/molecule.yml)
has no automated test coverage for its behavior.

Detection strategy:
  Determine if the scanned file is within an Ansible role (has meta/main.yml
  at the role root). If so, check whether molecule/ exists at the role root.
  Only fire once per role — use the role anchor file (tasks/main.yml).

Limitations:
  Cannot determine if tests are in a sibling repository or external CI.
  The rule is most useful in standalone role repositories.
"""

from __future__ import annotations

from pathlib import Path


def _find_role_root(path):
    """Return the role root Path if path is inside an Ansible role, else None.

    An Ansible role root is identified by having a meta/ directory with
    main.yml and at least a tasks/ directory.
    """
    path = Path(path).resolve()
    # Walk up looking for the role root (containing meta/main.yml)
    for parent in (path.parent, *path.parent.parents):
        if parent.name == "roles":
            break
        meta_main = next(
            (
                parent / "meta" / f"main.{suffix}"
                for suffix in ("yml", "yaml")
                if (parent / "meta" / f"main.{suffix}").is_file()
            ),
            None,
        )
        if meta_main is not None:
            return parent
    return None


def _role_anchor(role_root):
    """Return the canonical anchor file for the role (tasks/main.yml)."""
    for suffix in ("yml", "yaml"):
        candidate = role_root / "tasks" / f"main.{suffix}"
        if candidate.exists():
            return candidate
    return None


def detect_molecule_test_absent(path):
    """Detect Ansible roles without a molecule/ test directory.

    Only fires when path is the role's canonical anchor (tasks/main.yml),
    to emit one finding per role rather than per file.

    Returns:
        (count, details) where each detail has line, role, issue.
    """
    path = Path(path).resolve()
    role_root = _find_role_root(path)
    if role_root is None:
        return 0, []
    anchor = _role_anchor(role_root)
    if anchor is None or path != anchor:
        return 0, []

    molecule_dir = role_root / "molecule"
    if molecule_dir.is_dir():
        return 0, []

    return 1, [
        {
            "file": str(path),
            "line": 1,
            "role": role_root.name,
            "issue": (
                f"Role '{role_root.name}' has no molecule/ directory. "
                "Add a Molecule scenario to enable automated integration testing."
            ),
        }
    ]
