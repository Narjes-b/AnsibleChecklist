"""Project-level detector configuration and finding suppressions."""

from __future__ import annotations

from copy import deepcopy
from datetime import date
from pathlib import Path
import re

import yaml


class DetectorConfigError(ValueError):
    """Raised when .ansibleguard.yml cannot be trusted."""


DEFAULT_CONFIG = {
    "thresholds": {
        "complex_expression_score": 6,
        "complex_expression_length": 100,
        "long_statement_length": 160,
        "excessive_nesting_depth": 3,
        "missing_abstraction_tasks": 10,
        "undocumented_complex_boolean_ops": 4,
        "undocumented_complex_jinja_filters": 4,
        "undocumented_complex_nesting_depth": 5,
    },
    "rules": {
        "default_credentials": [
            "admin", "admin123", "changeme", "default", "guest",
            "password", "root", "secret", "test", "123456",
        ],
        "additional_mutating_command_patterns": [],
        "known_variables": [],
        "custom_module_facts": {},
        "deprecated_module_options": {},
    },
    "suppressions": {
        "disabled_rules": [],  # legacy AnsibleGuard rule IDs
        "concepts": [],
        "rules": [],
        "native_rules": [],
        "fingerprints": [],  # stable semantic/native fingerprints with reasons
    },
}

LEGACY_THRESHOLD_KEYS = {
    "LOC_playbook", "num_plays", "avg_play_size", "num_tasks_playbook",
    "avg_task_playbook", "Num_Imports", "Num_Roles", "similarity",
    "similarityPlays", "LOC_play", "num_tasks_play", "avg_task_play",
    "special_chars", "LOC_task", "task_name_len",
}
ALLOWED_ROOT_KEYS = frozenset(DEFAULT_CONFIG)
ALLOWED_THRESHOLD_KEYS = frozenset(DEFAULT_CONFIG["thresholds"]) | LEGACY_THRESHOLD_KEYS
ALLOWED_RULE_KEYS = frozenset(DEFAULT_CONFIG["rules"])
ALLOWED_SUPPRESSION_KEYS = frozenset(DEFAULT_CONFIG["suppressions"])


def _unknown_keys(value, allowed, location, config_path):
    unknown = sorted(set(value) - set(allowed))
    if unknown:
        raise DetectorConfigError(
            f"{config_path}: unknown {location} key(s): {', '.join(unknown)}"
        )


def _string_list(value, location, config_path):
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise DetectorConfigError(f"{config_path}: {location} must be a list of strings")


def validate_detector_config_data(loaded, config_path=".ansibleguard.yml"):
    """Validate configuration types, keys, rule IDs, and regular expressions."""
    config_path = Path(config_path)
    if not isinstance(loaded, dict):
        raise DetectorConfigError(f"{config_path}: configuration root must be a mapping")
    _unknown_keys(loaded, ALLOWED_ROOT_KEYS, "top-level", config_path)

    thresholds = loaded.get("thresholds", {})
    if not isinstance(thresholds, dict):
        raise DetectorConfigError(f"{config_path}: thresholds must be a mapping")
    _unknown_keys(thresholds, ALLOWED_THRESHOLD_KEYS, "threshold", config_path)
    for key, value in thresholds.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise DetectorConfigError(f"{config_path}: threshold {key!r} must be numeric")

    rules = loaded.get("rules", {})
    if not isinstance(rules, dict):
        raise DetectorConfigError(f"{config_path}: rules must be a mapping")
    _unknown_keys(rules, ALLOWED_RULE_KEYS, "rules", config_path)
    for key in ("default_credentials", "additional_mutating_command_patterns", "known_variables"):
        if key in rules:
            _string_list(rules[key], f"rules.{key}", config_path)
    for pattern in rules.get("additional_mutating_command_patterns", []):
        try:
            re.compile(pattern)
        except re.error as exc:
            raise DetectorConfigError(
                f"{config_path}: invalid rules.additional_mutating_command_patterns "
                f"entry {pattern!r}: {exc}"
            ) from exc
    custom_facts = rules.get("custom_module_facts", {})
    if not isinstance(custom_facts, dict) or any(
        not isinstance(module, str)
        or not isinstance(facts, list)
        or any(not isinstance(fact, str) for fact in facts)
        for module, facts in custom_facts.items()
    ):
        raise DetectorConfigError(
            f"{config_path}: rules.custom_module_facts must map module names to lists of fact names"
        )
    deprecations = rules.get("deprecated_module_options", {})
    if not isinstance(deprecations, dict) or any(
        not isinstance(module, str) or not isinstance(options, dict)
        for module, options in deprecations.items()
    ):
        raise DetectorConfigError(
            f"{config_path}: rules.deprecated_module_options must map module names to option mappings"
        )
    for module, options in deprecations.items():
        if any(
            not isinstance(option, str) or not isinstance(specification, (dict, str))
            for option, specification in options.items()
        ):
            raise DetectorConfigError(
                f"{config_path}: deprecated options for {module!r} must map "
                "option names to mappings or explanatory strings"
            )

    suppressions = loaded.get("suppressions", {})
    if not isinstance(suppressions, dict):
        raise DetectorConfigError(f"{config_path}: suppressions must be a mapping")
    _unknown_keys(suppressions, ALLOWED_SUPPRESSION_KEYS, "suppressions", config_path)
    disabled = suppressions.get("disabled_rules", [])
    _string_list(disabled, "suppressions.disabled_rules", config_path)
    if disabled:
        from .report.findings import RULE_CATALOG

        unknown_rules = sorted(set(disabled) - set(RULE_CATALOG))
        if unknown_rules:
            raise DetectorConfigError(
                f"{config_path}: unknown disabled rule ID(s): {', '.join(unknown_rules)}"
            )
    for key in ("concepts", "rules", "native_rules"):
        _string_list(suppressions.get(key, []), f"suppressions.{key}", config_path)
    fingerprints = suppressions.get("fingerprints", [])
    if not isinstance(fingerprints, list):
        raise DetectorConfigError(
            f"{config_path}: suppressions.fingerprints must be a list of mappings"
        )
    for index, entry in enumerate(fingerprints):
        if not isinstance(entry, dict):
            raise DetectorConfigError(
                f"{config_path}: suppressions.fingerprints[{index}] must be a mapping"
            )
        if not isinstance(entry.get("fingerprint"), str) or not entry["fingerprint"].strip():
            raise DetectorConfigError(
                f"{config_path}: suppressions.fingerprints[{index}].fingerprint must be a non-empty string"
            )
        if not isinstance(entry.get("reason"), str) or not entry["reason"].strip():
            raise DetectorConfigError(
                f"{config_path}: suppressions.fingerprints[{index}].reason is required"
            )
        expires = entry.get("expires")
        if expires is not None:
            if not isinstance(expires, (str, date)):
                raise DetectorConfigError(
                    f"{config_path}: suppressions.fingerprints[{index}].expires must be YYYY-MM-DD"
                )
            try:
                if isinstance(expires, str):
                    date.fromisoformat(expires)
            except ValueError as exc:
                raise DetectorConfigError(
                    f"{config_path}: suppressions.fingerprints[{index}].expires must be YYYY-MM-DD"
                ) from exc
    if suppressions.get("concepts"):
        from .report.findings import (
            CONCEPT_IDS,
            EXTERNAL_CONCEPT_IDS,
            RULE_CATALOG,
            VARIABLE_CLASSIFICATION_CATALOG,
        )

        known_concepts = set(RULE_CATALOG) | set(CONCEPT_IDS.values()) | set(
            EXTERNAL_CONCEPT_IDS.values()
        ) | set(VARIABLE_CLASSIFICATION_CATALOG)
        unknown = sorted(set(suppressions["concepts"]) - known_concepts)
        if unknown:
            raise DetectorConfigError(
                f"{config_path}: unknown suppressed concept ID(s): {', '.join(unknown)}"
            )
    if suppressions.get("rules"):
        from .report.findings import RULE_CATALOG

        unknown = sorted(
            value
            for value in suppressions["rules"]
            if not value.startswith("ansibleguard/")
            or value.split("/", 1)[1] not in RULE_CATALOG
        )
        if unknown:
            raise DetectorConfigError(
                f"{config_path}: invalid suppressed normalized rule(s): {', '.join(unknown)}"
            )
    invalid_native = sorted(
        value
        for value in suppressions.get("native_rules", [])
        if "/" not in value or value.split("/", 1)[0] not in {
            "ansibleguard", "ansible-lint", "gitleaks"
        }
    )
    if invalid_native:
        raise DetectorConfigError(
            f"{config_path}: invalid suppressed native rule(s): {', '.join(invalid_native)}"
        )
    return loaded


def _deep_merge(base, override):
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value
    return base


def find_config(path):
    candidate = Path(path).resolve()
    directory = candidate if candidate.is_dir() else candidate.parent
    for parent in (directory, *directory.parents):
        config_path = parent / ".ansibleguard.yml"
        if config_path.is_file():
            return config_path
    return None


def load_detector_config(path):
    config = deepcopy(DEFAULT_CONFIG)
    config_path = find_config(path)
    if config_path is None:
        return config
    try:
        loaded = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise DetectorConfigError(f"{config_path}: cannot read configuration: {exc}") from exc
    except yaml.YAMLError as exc:
        raise DetectorConfigError(f"{config_path}: invalid YAML: {exc}") from exc
    loaded = {} if loaded is None else loaded
    validate_detector_config_data(loaded, config_path)
    _deep_merge(config, loaded)
    # A1: Auto-discover long_statement_length from ansible-lint project config
    # Only override the default (160); explicit .ansibleguard.yml values take priority
    ansible_lint_len = _discover_ansible_lint_line_length(path)
    if ansible_lint_len is not None:
        # Only apply if not explicitly set in .ansibleguard.yml
        if not (loaded and "thresholds" in loaded and "long_statement_length" in loaded.get("thresholds", {})):
            config["thresholds"]["long_statement_length"] = ansible_lint_len
    return config


def _discover_ansible_lint_line_length(path):
    """Read max-line-length from the project's .ansible-lint config if present."""
    candidate = Path(path).resolve()
    directory = candidate if candidate.is_dir() else candidate.parent
    for parent in (directory, *directory.parents):
        for name in (".ansible-lint", ".ansible-lint.yml", ".ansible-lint.yaml"):
            cfg = parent / name
            if not cfg.is_file():
                continue
            try:
                loaded = yaml.safe_load(cfg.read_text(encoding="utf-8")) or {}
                val = loaded.get("max-line-length") or loaded.get("max_line_length")
                if isinstance(val, int) and val > 0:
                    return val
            except Exception:
                pass
    return None


def validate_detector_configs(paths):
    """Validate each distinct nearest configuration used by a scan."""
    validated = set()
    for path in paths:
        config_path = find_config(path)
        if config_path is None or config_path in validated:
            continue
        load_detector_config(path)
        validated.add(config_path)
    return tuple(sorted(validated))


def filter_findings(findings, path):
    suppressions = load_detector_config(path).get("suppressions", {})
    legacy_rules = set(suppressions.get("disabled_rules", []))
    concepts = set(suppressions.get("concepts", []))
    rules = set(suppressions.get("rules", []))
    native_rules = set(suppressions.get("native_rules", []))
    active_fingerprints = set()
    for entry in suppressions.get("fingerprints", []):
        expires = entry.get("expires")
        if expires:
            expiry = expires if isinstance(expires, date) else date.fromisoformat(expires)
            if expiry < date.today():
                continue
        active_fingerprints.add(entry["fingerprint"])

    def suppressed(finding):
        rule_id = str(finding.get("rule_id") or "")
        provider = str(finding.get("provider") or "ansibleguard")
        native_rule = str(finding.get("native_rule_id") or rule_id)
        finding_fingerprints = {
            str(finding.get(key))
            for key in ("occurrence_id", "semantic_key", "content_semantic_key", "native_fingerprint")
            if finding.get(key)
        }
        return (
            rule_id in legacy_rules
            or finding.get("concept_id") in concepts
            or f"ansibleguard/{rule_id}" in rules
            or f"{provider}/{native_rule}" in native_rules
            or bool(finding_fingerprints & active_fingerprints)
        )

    return [finding for finding in findings if not suppressed(finding)]


def mutating_command_pattern(config, base_pattern):
    additions = config.get("rules", {}).get(
        "additional_mutating_command_patterns", []
    )
    valid = []
    for pattern in additions:
        valid.append(f"(?:{pattern})")
    if not valid:
        return base_pattern
    return re.compile(
        f"(?:{base_pattern.pattern})|(?:{'|'.join(valid)})",
        base_pattern.flags,
    )
