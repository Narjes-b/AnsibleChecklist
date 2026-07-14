"""Additional static coverage for partially automated review criteria."""

from __future__ import annotations

import re

from ansibleguard.detectors.paper_candidates import _iter_tasks, _line_for, _load
from ansibleguard.detectors.review_checklist import (
    COMMAND_MODULES,
    _command_text,
    _module_value,
)

JINJA_REFERENCE_RE = re.compile(r"{{.*?}}|{%.*?%}", re.DOTALL)
SHELL_VARIABLE_RE = re.compile(
    r"(?<!\\)\$(?:{([A-Za-z_][A-Za-z0-9_]*)}|([A-Za-z_][A-Za-z0-9_]*))"
)
INLINE_ASSIGNMENT_RE = re.compile(r"(?:^|[;&]\s*)([A-Za-z_][A-Za-z0-9_]*)=")
COMMON_ENVIRONMENT = {
    "HOME",
    "PATH",
    "PWD",
    "SHELL",
    "USER",
    "LOGNAME",
    "LANG",
    "LC_ALL",
    "TERM",
    "TMP",
    "TMPDIR",
    "HOSTNAME",
    "SHLVL",
}
BOOLEAN_ATTRIBUTES = {
    "any_errors_fatal",
    "become",
    "check_mode",
    "diff",
    "force_handlers",
    "gather_facts",
    "ignore_errors",
    "ignore_unreachable",
    "no_log",
    "run_once",
}
INTEGER_ATTRIBUTES = {"async", "delay", "poll", "retries", "throttle", "timeout"}


def _walk_strings(value, parent_key=None):
    if isinstance(value, dict):
        for key, child in value.items():
            yield from _walk_strings(child, key)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_strings(child, parent_key)
    elif isinstance(value, str):
        yield parent_key, value


def detect_unused_registered_variables(path):
    document, text = _load(path)
    registered = {}
    for task, _ in _iter_tasks(document):
        if task.get("register"):
            registered[str(task["register"])] = task

    used = set()
    for key, value in _walk_strings(document):
        if key == "register":
            continue
        for variable in registered:
            if re.search(rf"\b{re.escape(variable)}\b", value):
                used.add(variable)

    details = []
    for variable, task in registered.items():
        if variable not in used:
            details.append(
                {
                    "line": _line_for(text, task.get("name")),
                    "task_name": task.get("name", "Unnamed task"),
                    "variable": variable,
                    "issue": f"Registered result '{variable}' is never referenced in this file.",
                }
            )
    return len(details), details


def detect_unscoped_shell_variables(path):
    document, text = _load(path)
    play_environment = set()
    if isinstance(document, list):
        for entry in document:
            if isinstance(entry, dict) and isinstance(entry.get("environment"), dict):
                play_environment.update(map(str, entry["environment"]))

    details = []
    for task, _ in _iter_tasks(document):
        _, value = _module_value(task, COMMAND_MODULES)
        if value is None:
            continue
        command = _command_text(value)
        references = {
            left or right for left, right in SHELL_VARIABLE_RE.findall(command)
        }
        task_environment = (
            task.get("environment") if isinstance(task.get("environment"), dict) else {}
        )
        defined = (
            COMMON_ENVIRONMENT | play_environment | set(map(str, task_environment))
        )
        defined.update(INLINE_ASSIGNMENT_RE.findall(command))
        missing = sorted(references - defined)
        if missing:
            details.append(
                {
                    "line": _line_for(text, task.get("name")),
                    "task_name": task.get("name", "Unnamed task"),
                    "variables": missing,
                    "issue": f"Shell variable(s) {', '.join(missing)} are not declared in the task/play environment mapping.",
                }
            )
    return len(details), details


def detect_invalid_task_attribute_types(path):
    document, text = _load(path)
    details = []
    for task, _ in _iter_tasks(document):
        for attribute in BOOLEAN_ATTRIBUTES:
            if attribute in task and not isinstance(task[attribute], bool):
                details.append(
                    {
                        "line": _line_for(text, task.get("name")),
                        "task_name": task.get("name", "Unnamed task"),
                        "attribute": attribute,
                        "issue": f"Task attribute '{attribute}' expects a boolean, got {type(task[attribute]).__name__}.",
                    }
                )
        for attribute in INTEGER_ATTRIBUTES:
            value = task.get(attribute)
            if attribute in task and (
                isinstance(value, bool) or not isinstance(value, int)
            ):
                details.append(
                    {
                        "line": _line_for(text, task.get("name")),
                        "task_name": task.get("name", "Unnamed task"),
                        "attribute": attribute,
                        "issue": f"Task attribute '{attribute}' expects an integer, got {type(value).__name__}.",
                    }
                )
        for attribute in ("environment", "vars"):
            if attribute in task and not isinstance(task[attribute], dict):
                details.append(
                    {
                        "line": _line_for(text, task.get("name")),
                        "task_name": task.get("name", "Unnamed task"),
                        "attribute": attribute,
                        "issue": f"Task attribute '{attribute}' expects a mapping.",
                    }
                )
        if "tags" in task and not isinstance(task["tags"], (str, list)):
            details.append(
                {
                    "line": _line_for(text, task.get("name")),
                    "task_name": task.get("name", "Unnamed task"),
                    "attribute": "tags",
                    "issue": "Task attribute 'tags' expects a string or list.",
                }
            )
    return len(details), details


def _walk_key_values(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield str(key), child
            yield from _walk_key_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_key_values(child)


def detect_invalid_numeric_values(path):
    document, text = _load(path)
    details = []
    seen = set()
    for task, _ in _iter_tasks(document):
        for key, value in _walk_key_values(task):
            if isinstance(value, bool) or not isinstance(value, int):
                continue
            issue = None
            if (key == "port" or key.endswith("_port")) and not 1 <= value <= 65535:
                issue = f"Port value {value} is outside the valid range 1..65535."
            elif key in INTEGER_ATTRIBUTES and value < 0:
                issue = f"Task control value '{key}' cannot be negative ({value})."
            identity = (key, value, task.get("name"))
            if issue and identity not in seen:
                seen.add(identity)
                details.append(
                    {
                        "line": _line_for(text, task.get("name")),
                        "task_name": task.get("name", "Unnamed task"),
                        "attribute": key,
                        "value": value,
                        "issue": issue,
                    }
                )
    return len(details), details


def detect_partial_checklist_smells(path):
    detectors = {
        "unused_registered_variables": detect_unused_registered_variables,
        "unscoped_shell_variables": detect_unscoped_shell_variables,
        "invalid_task_attribute_types": detect_invalid_task_attribute_types,
        "invalid_numeric_values": detect_invalid_numeric_values,
    }
    result = {}
    for metric, detector in detectors.items():
        count, details = detector(path)
        result[metric] = count
        result[f"{metric}_details"] = details
    return result
