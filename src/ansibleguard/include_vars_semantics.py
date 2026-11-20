"""Shared static semantics for Ansible ``include_vars`` targets."""

from __future__ import annotations

from pathlib import Path
from typing import Mapping


def static_include_vars_target(value, source: Path):
    """Return ``(target, namespace)`` for a literal file/directory import."""
    namespace = None
    if isinstance(value, Mapping):
        namespace = value.get("name") if isinstance(value.get("name"), str) else None
        value = value.get("file") or value.get("dir") or value.get("_raw_params")
    if not isinstance(value, str) or "{{" in value or "{%" in value:
        return None
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = Path(source).parent / candidate
    return candidate.resolve(), namespace


def expand_include_vars_target(path, selected_files=None):
    """Expand a literal directory import within an optional selected population."""
    path = Path(path).resolve()
    try:
        is_dir = path.is_dir()
    except OSError:
        # An include_vars target can be a literal absolute path (e.g.
        # "/root/pull_variables.yml") that is meaningful only on the target
        # inventory host at playbook-run time, not on the machine doing this
        # static analysis. Stat-ing it here can raise PermissionError (or
        # other OSError) for paths this process has no access to; treat that
        # the same as "not a directory" rather than letting it crash the
        # whole repository's analysis.
        is_dir = False
    if not is_dir:
        return (path,)
    if selected_files is not None:
        return tuple(sorted(
            candidate
            for candidate in {Path(item).resolve() for item in selected_files}
            if path in candidate.parents
            and candidate.suffix.lower() in {".yml", ".yaml"}
        ))
    try:
        return tuple(sorted(
            candidate.resolve()
            for pattern in ("*.yml", "*.yaml")
            for candidate in path.rglob(pattern)
            if candidate.is_file()
        ))
    except OSError:
        return ()
