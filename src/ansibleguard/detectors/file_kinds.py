"""Checks that apply to variable, metadata, and dependency YAML kinds."""

from __future__ import annotations

from pathlib import Path
import re

import yaml

from ansibleguard.document import inspect_document


VARIABLE_DIRECTORIES = {"defaults", "vars", "group_vars", "host_vars", "env_vars"}
SENSITIVE_PARTS = {
    "password",
    "passwd",
    "pwd",
    "secret",
    "token",
    "api_key",
    "apikey",
    "access_key",
    "private_key",
    "client_secret",
    "credential",
}
NON_SECRET_SUFFIXES = {
    "algorithm",
    "enabled",
    "expire",
    "expiration",
    "file",
    "length",
    "lock",
    "path",
    "policy",
    "required",
    "type",
}
DEPENDENCY_FILENAMES = {
    "requirements.yml",
    "requirements.yaml",
    "ansible-role-requirements.yml",
    "ansible-role-requirements.yaml",
    "ansible-collection-requirements.yml",
    "ansible-collection-requirements.yaml",
}


def _line_for_key(text: str, key: str) -> int:
    pattern = re.compile(rf"^\s*{re.escape(key)}\s*:", re.MULTILINE)
    match = pattern.search(text)
    return text.count("\n", 0, match.start()) + 1 if match else 1


def _sensitive_key(key) -> bool:
    normalized = str(key).lower().replace("-", "_")
    parts = [part for part in normalized.split("_") if part]
    if NON_SECRET_SUFFIXES.intersection(parts):
        return False
    joined_pairs = {"_".join(parts[index : index + 2]) for index in range(len(parts))}
    return bool(SENSITIVE_PARTS.intersection(parts) or SENSITIVE_PARTS.intersection(joined_pairs))


def _plaintext_literal(value) -> bool:
    if isinstance(value, dict) and value.get("__ansible_tag__") == "!vault":
        return False
    if not isinstance(value, (str, int, float)):
        return False
    rendered = str(value).strip()
    if not rendered or "{{" in rendered or "$ANSIBLE_VAULT" in rendered:
        return False
    return True


def _walk_sensitive(mapping, prefix=()):
    if not isinstance(mapping, dict):
        return
    for key, value in mapping.items():
        path = (*prefix, str(key))
        if _sensitive_key(key) and _plaintext_literal(value):
            yield path
        if isinstance(value, dict):
            yield from _walk_sensitive(value, path)


def detect_plaintext_sensitive_variables(path):
    path = Path(path)
    info = inspect_document(path)
    if (
        info.parse_status != "parsed"
        or info.document_type != "vars"
        or not VARIABLE_DIRECTORIES.intersection(
            part.lower() for part in path.parts
        )
    ):
        return 0, []
    text = path.read_text(encoding="utf-8")
    details = []
    for variable_path in _walk_sensitive(info.document):
        key = variable_path[-1]
        details.append(
            {
                "file": str(path),
                "line": _line_for_key(text, key),
                "variable": ".".join(variable_path),
                "issue": (
                    f"Sensitive variable '{'.'.join(variable_path)}' is stored "
                    "as a plaintext literal; use Ansible Vault or an external "
                    "secret source."
                ),
            }
        )
    return len(details), details


def _dependency_entries(document, include_meta_dependencies=False):
    if isinstance(document, list):
        yield from document
    elif isinstance(document, dict):
        for section in ("roles", "collections"):
            entries = document.get(section)
            if isinstance(entries, list):
                yield from entries
        if include_meta_dependencies:
            entries = document.get("dependencies")
            if isinstance(entries, list):
                yield from entries


def detect_unpinned_ansible_dependencies(path):
    path = Path(path)
    is_requirements = path.name.lower() in DEPENDENCY_FILENAMES
    is_role_meta = (
        path.parent.name.lower() == "meta"
        and path.stem.lower() == "main"
        and path.suffix.lower() in {".yml", ".yaml"}
    )
    if not (is_requirements or is_role_meta):
        return 0, []
    info = inspect_document(path)
    if info.parse_status != "parsed":
        return 0, []
    text = path.read_text(encoding="utf-8")
    details = []
    for entry in _dependency_entries(
        info.document, include_meta_dependencies=is_role_meta
    ):
        if isinstance(entry, str):
            name = entry
            version = None
        elif isinstance(entry, dict):
            name = entry.get("name") or entry.get("role") or entry.get("src")
            version = entry.get("version")
        else:
            continue
        # Short names in role metadata normally reference local sibling roles;
        # unlike external Galaxy roles, they have no meaningful version pin.
        if is_role_meta and not (
            isinstance(entry, dict) and entry.get("src")
        ) and "." not in str(name):
            continue
        if not name or version:
            continue
        details.append(
            {
                "file": str(path),
                "line": _line_for_key(text, str(name)),
                "dependency": str(name),
                "issue": (
                    f"Ansible dependency '{name}' has no explicit version; "
                    "pin a reviewed tag or commit for reproducible scans."
                ),
            }
        )
    return len(details), details


def detect_file_kind_smells(path):
    detectors = {
        "plaintext_sensitive_variables": detect_plaintext_sensitive_variables,
        "unpinned_ansible_dependencies": detect_unpinned_ansible_dependencies,
    }
    result = {}
    for metric, detector in detectors.items():
        count, details = detector(path)
        result[metric] = count
        result[f"{metric}_details"] = details
    return result


def _load_mapping(path):
    try:
        loaded = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return {}
    return loaded if isinstance(loaded, dict) else {}


def detect_role_variable_precedence_collisions(root):
    root = Path(root)
    details = []
    role_roots = set()
    for defaults_dir in root.rglob("defaults"):
        if defaults_dir.is_dir():
            role_roots.add(defaults_dir.parent)
    if root.name in {"defaults", "vars"}:
        role_roots.add(root.parent)

    for role_root in sorted(role_roots):
        defaults_path = next(
            (
                role_root / "defaults" / f"main.{suffix}"
                for suffix in ("yml", "yaml")
                if (role_root / "defaults" / f"main.{suffix}").is_file()
            ),
            None,
        )
        vars_path = next(
            (
                role_root / "vars" / f"main.{suffix}"
                for suffix in ("yml", "yaml")
                if (role_root / "vars" / f"main.{suffix}").is_file()
            ),
            None,
        )
        if defaults_path is None or vars_path is None:
            continue
        defaults = _load_mapping(defaults_path)
        variables = _load_mapping(vars_path)
        text = vars_path.read_text(encoding="utf-8")
        for key in sorted(set(defaults).intersection(variables)):
            details.append(
                {
                    "file": str(vars_path),
                    "line": _line_for_key(text, str(key)),
                    "variable": str(key),
                    "issue": (
                        f"Role variable '{key}' is defined in both "
                        "defaults/main and vars/main; the higher-precedence "
                        "vars value silently prevents normal overrides."
                    ),
                }
            )
    return {
        "role_variable_precedence_collisions": len(details),
        "role_variable_precedence_collisions_details": details,
    }
