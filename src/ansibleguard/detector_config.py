"""Project-level detector configuration and finding suppressions."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import re

import yaml


DEFAULT_CONFIG = {
    "thresholds": {
        "complex_expression_score": 6,
        "complex_expression_length": 100,
        "long_statement_length": 120,
        "excessive_nesting_depth": 3,
        "missing_abstraction_tasks": 10,
    },
    "rules": {
        "default_credentials": [
            "admin", "admin123", "changeme", "default", "guest",
            "password", "root", "secret", "test", "123456",
        ],
        "additional_mutating_command_patterns": [],
        "known_variables": [],
        "deprecated_module_options": {},
    },
    "suppressions": {"disabled_rules": []},
}


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
        loaded = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return config
    return _deep_merge(config, loaded) if isinstance(loaded, dict) else config


def filter_findings(findings, path):
    disabled = set(
        load_detector_config(path).get("suppressions", {}).get("disabled_rules", [])
    )
    return [finding for finding in findings if finding.get("rule_id") not in disabled]


def mutating_command_pattern(config, base_pattern):
    additions = config.get("rules", {}).get(
        "additional_mutating_command_patterns", []
    )
    valid = []
    for pattern in additions:
        try:
            re.compile(str(pattern))
        except re.error:
            continue
        valid.append(f"(?:{pattern})")
    if not valid:
        return base_pattern
    return re.compile(
        f"(?:{base_pattern.pattern})|(?:{'|'.join(valid)})",
        base_pattern.flags,
    )
