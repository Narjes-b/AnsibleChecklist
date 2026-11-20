"""Shared Ansible role-layout and automatically loaded variable resolution."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ROLE_SECTIONS = frozenset(
    {"defaults", "vars", "tasks", "handlers", "meta", "files", "templates"}
)


@dataclass(frozen=True)
class RoleContext:
    root: Path
    identifier: str
    section: str | None
    standalone: bool


def _has_main(directory: Path) -> bool:
    return any((directory / f"main.{suffix}").is_file() for suffix in ("yml", "yaml"))


def is_standalone_role_root(root: Path) -> bool:
    """Return whether *root* has the conventional shape of one Galaxy role."""
    root = Path(root).resolve()
    return any(_has_main(root / section) for section in ("tasks", "meta"))


def resolve_role_context(path, repository_root=None) -> RoleContext | None:
    """Resolve collection-style and repository-root standalone role layouts."""
    resolved = Path(path).resolve()
    root = Path(repository_root).resolve() if repository_root is not None else None
    if root is not None:
        try:
            relative = resolved.relative_to(root)
        except ValueError:
            relative = None
        if relative is not None:
            parts = relative.parts
            if "roles" in parts:
                index = parts.index("roles")
                section_index = next(
                    (
                        candidate
                        for candidate in range(index + 2, len(parts))
                        if parts[candidate] in ROLE_SECTIONS
                    ),
                    None,
                )
                if section_index is not None:
                    role_root = root.joinpath(*parts[:section_index])
                    return RoleContext(
                        role_root,
                        role_root.relative_to(root).as_posix(),
                        parts[section_index],
                        False,
                    )
                if index + 1 < len(parts):
                    role_root = root.joinpath(*parts[: index + 2])
                    return RoleContext(
                        role_root,
                        role_root.relative_to(root).as_posix(),
                        None,
                        False,
                    )
            if parts and parts[0] in ROLE_SECTIONS and is_standalone_role_root(root):
                return RoleContext(root, ".", parts[0], True)

    parts = resolved.parts
    indexes = [index for index, part in enumerate(parts) if part == "roles"]
    if indexes:
        index = indexes[-1]
        section_index = next(
            (
                candidate
                for candidate in range(index + 2, len(parts))
                if parts[candidate] in ROLE_SECTIONS
            ),
            None,
        )
        if section_index is not None:
            role_root = Path(*parts[:section_index])
            role_suffix = Path(*parts[index:section_index]).as_posix()
            return RoleContext(
                role_root, role_suffix, parts[section_index], False
            )
        if index + 1 < len(parts):
            role_root = Path(*parts[: index + 2])
            return RoleContext(role_root, f"roles/{parts[index + 1]}", None, False)

    for parent in resolved.parents:
        if parent.name not in ROLE_SECTIONS:
            continue
        candidate = parent.parent
        if is_standalone_role_root(candidate):
            return RoleContext(candidate, ".", parent.name, True)
    return None


def is_automatically_loaded_role_vars(path, repository_root=None) -> tuple[str, RoleContext] | None:
    """Classify defaults/vars files Ansible loads through the role entry point.

    Ansible loads ``defaults/main.yml`` and ``vars/main.yml``. It also supports
    split entry-point directories such as ``defaults/main/*.yml``. Other YAML
    files below defaults/vars require an explicit reference and are not treated
    as automatically visible.
    """
    resolved = Path(path).resolve()
    context = resolve_role_context(resolved, repository_root)
    if context is None or context.section not in {"defaults", "vars"}:
        return None
    try:
        relative = resolved.relative_to(context.root / context.section)
    except ValueError:
        return None
    parts = relative.parts
    direct_main = len(parts) == 1 and relative.name in {"main.yml", "main.yaml"}
    split_main = len(parts) >= 2 and parts[0] == "main"
    if not (direct_main or split_main):
        return None
    kind = "defaults-file" if context.section == "defaults" else "role-vars-file"
    return kind, context


def automatic_role_variable_files(role_root, section):
    """Yield conventional main files/directories for a role variable section."""
    directory = Path(role_root) / section
    candidates = [directory / "main.yml", directory / "main.yaml"]
    main_directory = directory / "main"
    if main_directory.is_dir():
        candidates.extend(
            path
            for pattern in ("*.yml", "*.yaml")
            for path in main_directory.rglob(pattern)
        )
    return tuple(sorted({path for path in candidates if path.is_file()}))
