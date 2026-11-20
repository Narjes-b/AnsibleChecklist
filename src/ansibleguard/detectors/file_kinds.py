"""Checks that apply to variable, metadata, and dependency YAML kinds."""

from __future__ import annotations

from pathlib import Path
import re

import yaml

from ansibleguard.document import inspect_document
from ansibleguard.compat import StrEnum


VARIABLE_DIRECTORIES = {"defaults", "vars", "group_vars", "host_vars", "env_vars"}
SENSITIVE_PARTS = {
    "pass",
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
    "backend",
    "count",
    "dir",
    "enabled",
    "expire",
    "expiration",
    "file",
    "format",
    "hash",
    "header",
    "length",
    "limit",
    "lock",
    "max",
    "min",
    "mode",
    "path",
    "policy",
    "prefix",
    "required",
    "provider",
    "reset",
    "link",
    "size",
    "suffix",
    "timeout",
    "ttl",
    "type",
    "url",
    "uri",
    "name",
    "map",
    "maps",
    "id",
    "keyname",
}
DEPENDENCY_FILENAMES = {
    "requirements.yml",
    "requirements.yaml",
    "ansible-role-requirements.yml",
    "ansible-role-requirements.yaml",
    "ansible-collection-requirements.yml",
    "ansible-collection-requirements.yaml",
}


class SensitiveValueClass(StrEnum):
    SECRET_VALUE = "SECRET_VALUE"
    SECRET_CONFIGURATION = "SECRET_CONFIGURATION"
    SECRET_METADATA = "SECRET_METADATA"
    SECRET_MESSAGE = "SECRET_MESSAGE"
    SECRET_PATH = "SECRET_PATH"
    UNKNOWN = "UNKNOWN"


def _normalized_key_parts(key):
    normalized = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", str(key))
    normalized = normalized.lower().replace("-", "_")
    return normalized, [part for part in normalized.split("_") if part]


def _has_sensitive_token(normalized, parts):
    joined_pairs = {"_".join(parts[index : index + 2]) for index in range(len(parts))}
    legacy_suffix = re.fullmatch(
        r"(?:(?:db|user|admin|root|mysql|registry|ptv|api|store|key)[a-z0-9_]*)?"
        r"(?:password|passwd|pwd|pass)",
        normalized,
    )
    return bool(
        SENSITIVE_PARTS.intersection(parts)
        or SENSITIVE_PARTS.intersection(joined_pairs)
        or legacy_suffix
    )


def classify_sensitive_entry(key, value) -> SensitiveValueClass:
    """Classify secret-bearing intent using key shape, value, and context."""
    normalized, parts = _normalized_key_parts(key)
    if not _has_sensitive_token(normalized, parts):
        return SensitiveValueClass.UNKNOWN
    suffix = parts[-1] if parts else ""
    if suffix in {"msg", "message", "warning", "error"} or "fail" in parts:
        return SensitiveValueClass.SECRET_MESSAGE
    if suffix in {"path", "dir", "file", "url", "uri", "endpoint", "socket"} or (
        {"link", "url", "uri", "endpoint"} & set(parts)
    ):
        return SensitiveValueClass.SECRET_PATH
    if suffix in {"name", "id", "keyname", "label", "description"}:
        return SensitiveValueClass.SECRET_METADATA
    if suffix in {
        "option", "mode", "backend", "provider", "store", "configuration",
        "config", "algorithm", "algo", "hash", "ttl", "timeout", "policy",
        "map", "maps",
    } or {"map", "maps"} & set(parts):
        return SensitiveValueClass.SECRET_CONFIGURATION
    if _plaintext_literal(value):
        return SensitiveValueClass.SECRET_VALUE
    return SensitiveValueClass.UNKNOWN


def _line_for_key(text: str, key: str) -> int:
    pattern = re.compile(rf"^\s*{re.escape(key)}\s*:", re.MULTILINE)
    match = pattern.search(text)
    return text.count("\n", 0, match.start()) + 1 if match else 1


def _sensitive_key(key) -> bool:
    normalized, parts = _normalized_key_parts(key)
    if NON_SECRET_SUFFIXES.intersection(parts):
        return False
    joined_pairs = {"_".join(parts[index : index + 2]) for index in range(len(parts))}
    legacy_suffix = re.fullmatch(
        r"(?:(?:db|user|admin|root|mysql|registry|ptv|api|store|key)[a-z0-9_]*)?"
        r"(?:password|passwd|pwd|pass)",
        normalized,
    )
    return bool(
        SENSITIVE_PARTS.intersection(parts)
        or SENSITIVE_PARTS.intersection(joined_pairs)
        or legacy_suffix
    )


_SOPS_CIPHER_RE = re.compile(r"^ENC\[AES256_GCM,")
_PLACEHOLDER_RE = re.compile(
    r"^(?:PLACEHOLDER|CHANGEME|CHANGE[_-]ME|YOUR[_-]|your[_-]|"
    r"some[_-]|example[_-]|<[^>]+>|TODO|FIXME|\*{3,}|xxx|XXX|none|null|empty|"
    r"default|changeit|insert|enter|fill|provide|replace)",
    re.IGNORECASE,
)


def _plaintext_literal(value) -> bool:
    if isinstance(value, dict) and value.get("__ansible_tag__") == "!vault":
        return False
    # v0.0.4: integers and floats are configuration values (timeouts, port numbers,
    # counts) — they are never plaintext secrets. This was a major FP source
    # (e.g. token_ttl: 3600, api_timeout: 30).
    if isinstance(value, bool) or isinstance(value, (int, float)):
        return False
    if not isinstance(value, str):
        return False
    rendered = value.strip()
    if not rendered or "{{" in rendered or "$ANSIBLE_VAULT" in rendered:
        return False
    # SOPS-encrypted ciphertext is not plaintext
    if _SOPS_CIPHER_RE.match(rendered):
        return False
    # Role defaults with placeholder values are documentation patterns, not real secrets
    if _PLACEHOLDER_RE.match(rendered):
        return False
    return True


def _walk_sensitive(mapping, prefix=()):
    if not isinstance(mapping, dict):
        return
    for key, value in mapping.items():
        path = (*prefix, str(key))
        sensitive_class = classify_sensitive_entry(key, value)
        if sensitive_class == SensitiveValueClass.SECRET_VALUE:
            yield path, sensitive_class
        if isinstance(value, dict):
            yield from _walk_sensitive(value, path)


def detect_plaintext_sensitive_variables(path, parsed_document=None):
    path = Path(path)
    # Skip SOPS-encrypted files by naming convention
    if path.stem.endswith(".sops") or ".sops." in path.name:
        return 0, []
    info = parsed_document or inspect_document(path)
    # Skip files with a top-level sops: key (SOPS metadata marker)
    if isinstance(info.document, dict) and "sops" in info.document:
        return 0, []
    stem = path.stem.lower()
    variable_location = bool(
        VARIABLE_DIRECTORIES.intersection(part.lower() for part in path.parts)
        or stem in {"vars", "defaults", "variables"}
        or stem.endswith(("-vars", "_vars"))
    )
    if (
        info.parse_status != "parsed"
        or info.document_type != "vars"
        or not variable_location
    ):
        return 0, []
    text = info.source_text
    details = []
    for variable_path, sensitive_class in _walk_sensitive(info.document):
        key = variable_path[-1]
        details.append(
            {
                "file": str(path),
                "line": _line_for_key(text, key),
                "variable": ".".join(variable_path),
                "sensitive_class": str(sensitive_class),
                "evidence_level": "KEY_VALUE_CONTEXT",
                "confidence": "high",
                "confidence_factors": {
                    "positive": [
                        "secret_bearing_key",
                        "plaintext_literal_value",
                        "variable_file_context",
                    ],
                    "negative": [],
                },
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


def detect_unpinned_ansible_dependencies(path, parsed_document=None):
    path = Path(path)
    is_requirements = path.name.lower() in DEPENDENCY_FILENAMES
    is_role_meta = (
        path.parent.name.lower() == "meta"
        and path.stem.lower() == "main"
        and path.suffix.lower() in {".yml", ".yaml"}
    )
    if not (is_requirements or is_role_meta):
        return 0, []
    info = parsed_document or inspect_document(path)
    if info.parse_status != "parsed":
        return 0, []
    text = info.source_text
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


def detect_file_kind_smells(path, parsed_document=None):
    detectors = {
        "plaintext_sensitive_variables": detect_plaintext_sensitive_variables,
        "unpinned_ansible_dependencies": detect_unpinned_ansible_dependencies,
    }
    result = {}
    for metric, detector in detectors.items():
        count, details = detector(path, parsed_document=parsed_document)
        result[metric] = count
        result[f"{metric}_details"] = details
    return result


def _load_mapping(path):
    try:
        loaded = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return {}
    return loaded if isinstance(loaded, dict) else {}


def detect_role_variable_precedence_collisions(
    root, symbol_index=None, files=None, repository_context=None
):
    root = Path(root)
    details = []
    if symbol_index is not None:
        by_role = {}
        for definition in symbol_index.definitions:
            if not definition.role or definition.kind not in {
                "defaults-file", "role-vars-file"
            }:
                continue
            role = by_role.setdefault(
                definition.role, {"defaults-file": {}, "role-vars-file": {}}
            )
            role[definition.kind].setdefault(definition.name, definition)
        for role_name in sorted(by_role):
            role = by_role[role_name]
            collisions = sorted(
                set(role["defaults-file"]).intersection(role["role-vars-file"])
            )
            for key in collisions:
                definition = role["role-vars-file"][key]
                vars_path = root / definition.file
                shared = (
                    repository_context.parsed_documents.get(vars_path.resolve())
                    if repository_context is not None else None
                )
                text = (
                    shared.source_text
                    if shared is not None
                    else vars_path.read_text(encoding="utf-8")
                )
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

    allowed = (
        {Path(path).resolve() for path in files}
        if files is not None else None
    )
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
        if allowed is not None and not {
            defaults_path.resolve(), vars_path.resolve()
        } <= allowed:
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
