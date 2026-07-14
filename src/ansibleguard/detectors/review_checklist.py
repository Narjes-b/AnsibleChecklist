"""Automatable source-level checks from the 2025 IaC review checklist."""

from __future__ import annotations

from pathlib import Path
import re
import stat

from ansibleguard.detectors.paper_candidates import (
    NESTED_SECTIONS,
    _iter_tasks,
    _line_for,
    _load,
)

SENSITIVE_KEY_RE = re.compile(
    r"(?:password|passwd|pwd|secret|token|api[_-]?key|credential)", re.IGNORECASE
)
DEFAULT_CREDENTIALS = {
    "admin",
    "admin123",
    "changeme",
    "default",
    "guest",
    "password",
    "root",
    "secret",
    "test",
    "123456",
}
MODE_MODULES = {
    "assemble",
    "blockinfile",
    "copy",
    "file",
    "get_url",
    "ini_file",
    "lineinfile",
    "replace",
    "template",
    "unarchive",
}
COMMAND_MODULES = {
    "ansible.builtin.command",
    "ansible.builtin.raw",
    "ansible.builtin.shell",
    "command",
    "raw",
    "shell",
}
MUTATING_COMMAND_RE = re.compile(
    r"(?:^|[;&|]\s*)(?:apt(?:-get)?|yum|dnf|rpm|pip|npm|systemctl|service|"
    r"rm|cp|mv|mkdir|touch|chmod|chown|useradd|usermod|groupadd|git\s+clone|"
    r"curl|wget|sed\s+-i)\b",
    re.IGNORECASE,
)
EXPORT_RE = re.compile(
    r"(?:^|[;&]\s*)export\s+([A-Za-z_][A-Za-z0-9_]*)\s*=", re.MULTILINE
)


def _task_line(text, task):
    return _line_for(text, task.get("name"))


def _module_value(task, names):
    for name in names:
        if name in task:
            return name, task[name]
    return None, None


def _mode_to_int(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    candidate = str(value).strip().strip("'\"")
    if candidate.lower().startswith("0o"):
        candidate = candidate[2:]
    if re.fullmatch(r"0?[0-7]{3,4}", candidate):
        return int(candidate, 8)
    return None


def _symbolic_world_write(value):
    if not isinstance(value, str):
        return False
    for clause in value.replace(" ", "").split(","):
        match = re.fullmatch(r"([ugoa]*)([+=-])([rwxXst]+)", clause)
        if not match or match.group(2) == "-" or "w" not in match.group(3).lower():
            continue
        subjects = match.group(1)
        if not subjects or "a" in subjects or "o" in subjects:
            return True
    return False


def detect_insecure_permissions(path):
    document, text = _load(path)
    details = []
    for task, _ in _iter_tasks(document):
        candidates = []
        if "mode" in task:
            candidates.append(("task", task["mode"]))
        for module_name, value in task.items():
            short_name = str(module_name).split(".")[-1]
            if (
                short_name in MODE_MODULES
                and isinstance(value, dict)
                and "mode" in value
            ):
                candidates.append((module_name, value["mode"]))
        for module_name, mode in candidates:
            parsed = _mode_to_int(mode)
            task_text = str(task).lower()
            sensitive = bool(
                SENSITIVE_KEY_RE.search(task_text) or "private" in task_text
            )
            issue = None
            if parsed is not None and parsed & stat.S_IWOTH:
                issue = "World-writable permissions grant write access to other users."
            elif parsed is not None and sensitive and parsed & stat.S_IROTH:
                issue = "A sensitive resource is readable by other users."
            elif _symbolic_world_write(mode):
                issue = "Symbolic mode grants write access to other users."
            if issue:
                details.append(
                    {
                        "line": _task_line(text, task),
                        "task_name": task.get("name", "Unnamed task"),
                        "module": module_name,
                        "mode": str(mode),
                        "issue": issue,
                    }
                )
    return len(details), details


def _walk_mappings(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk_mappings(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_mappings(child)


def detect_default_credentials(path):
    document, text = _load(path)
    details = []
    seen = set()
    for mapping in _walk_mappings(document):
        for key, value in mapping.items():
            if not SENSITIVE_KEY_RE.search(str(key)) or not isinstance(
                value, (str, int)
            ):
                continue
            normalized = str(value).strip().lower()
            if "{{" in normalized or "$ansible_vault" in normalized:
                continue
            if normalized not in DEFAULT_CREDENTIALS and normalized != str(key).lower():
                continue
            identity = (str(key), normalized)
            if identity in seen:
                continue
            seen.add(identity)
            details.append(
                {
                    "line": _line_for(text, str(key)),
                    "credential_key": str(key),
                    "issue": f"Credential '{key}' uses the well-known default value '{value}'.",
                }
            )
    return len(details), details


def _command_text(value):
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return str(value.get("cmd") or value.get("argv") or "")
    return ""


def detect_non_idempotent_commands(path):
    document, text = _load(path)
    details = []
    for task, _ in _iter_tasks(document):
        module, value = _module_value(task, COMMAND_MODULES)
        if not module:
            continue
        command = _command_text(value)
        args = task.get("args") if isinstance(task.get("args"), dict) else {}
        if isinstance(value, dict):
            args = {**args, **value}
        guarded = any(key in args for key in ("creates", "removes")) or any(
            key in task for key in ("changed_when", "check_mode")
        )
        if MUTATING_COMMAND_RE.search(command) and not guarded:
            details.append(
                {
                    "line": _task_line(text, task),
                    "task_name": task.get("name", "Unnamed task"),
                    "command": command,
                    "issue": "Mutating command has no creates/removes/changed_when idempotency guard.",
                }
            )
    return len(details), details


def detect_silent_error_suppression(path):
    document, text = _load(path)
    details = []
    for task, _ in _iter_tasks(document):
        ignores_errors = task.get("ignore_errors") is True
        disables_failure = task.get("failed_when") is False
        if (ignores_errors or disables_failure) and not task.get("register"):
            details.append(
                {
                    "line": _task_line(text, task),
                    "task_name": task.get("name", "Unnamed task"),
                    "issue": "Task suppresses failure without registering the result for warning or recovery handling.",
                }
            )
    return len(details), details


def _role_root(path):
    path = Path(path).resolve()
    parts = path.parts
    indexes = [index for index, part in enumerate(parts) if part == "roles"]
    if not indexes or indexes[-1] + 1 >= len(parts):
        return None
    index = indexes[-1]
    return Path(*parts[: index + 2])


def detect_redundant_default_values(path):
    document, text = _load(path)
    role_root = _role_root(path)
    if not role_root:
        return 0, []
    defaults = None
    for suffix in ("yml", "yaml"):
        defaults, _ = _load(role_root / "defaults" / f"main.{suffix}")
        if isinstance(defaults, dict):
            break
    if not isinstance(defaults, dict):
        return 0, []

    assignments = []
    if isinstance(document, list):
        for entry in document:
            if isinstance(entry, dict) and isinstance(entry.get("vars"), dict):
                assignments.append((entry.get("name", "play vars"), entry["vars"]))
    for task, _ in _iter_tasks(document):
        if isinstance(task.get("vars"), dict):
            assignments.append((task.get("name", "task vars"), task["vars"]))
        for key in ("set_fact", "ansible.builtin.set_fact"):
            if isinstance(task.get(key), dict):
                assignments.append((task.get("name", "set_fact"), task[key]))

    details = []
    for owner, values in assignments:
        for key, value in values.items():
            if key in defaults and defaults[key] == value:
                details.append(
                    {
                        "line": _line_for(text, str(key)),
                        "task_name": owner,
                        "variable": str(key),
                        "issue": f"'{key}' repeats the same value already supplied by role defaults.",
                    }
                )
    return len(details), details


def detect_shell_environment_exports(path):
    document, text = _load(path)
    details = []
    for task, _ in _iter_tasks(document):
        module, value = _module_value(task, COMMAND_MODULES)
        if not module:
            continue
        command = _command_text(value)
        exported = sorted(set(EXPORT_RE.findall(command)))
        if exported:
            details.append(
                {
                    "line": _task_line(text, task),
                    "task_name": task.get("name", "Unnamed task"),
                    "variables": exported,
                    "issue": "Shell export does not provide durable Ansible variable scoping; use the task environment mapping.",
                }
            )
    return len(details), details


def _has_preceding_comment(lines, line_number):
    index = max(0, line_number - 2)
    while index >= 0 and not lines[index].strip():
        index -= 1
    return index >= 0 and lines[index].lstrip().startswith("#")


def detect_undocumented_complex_tasks(path):
    document, text = _load(path)
    lines = text.splitlines()
    details = []
    for task, depth in _iter_tasks(document):
        condition = str(task.get("when", ""))
        complex_task = (
            any(section in task for section in NESTED_SECTIONS)
            or len(condition) > 80
            or depth > 2
        )
        if not complex_task:
            continue
        line = _task_line(text, task)
        if not _has_preceding_comment(lines, line):
            details.append(
                {
                    "line": line,
                    "task_name": task.get("name", "Unnamed task"),
                    "issue": "Complex task has no immediately preceding explanatory comment.",
                }
            )
    return len(details), details


def detect_review_checklist_smells(path):
    detectors = {
        "insecure_permissions": detect_insecure_permissions,
        "default_credentials": detect_default_credentials,
        "non_idempotent_commands": detect_non_idempotent_commands,
        "silent_error_suppressions": detect_silent_error_suppression,
        "redundant_default_values": detect_redundant_default_values,
        "shell_environment_exports": detect_shell_environment_exports,
        "undocumented_complex_tasks": detect_undocumented_complex_tasks,
    }
    result = {}
    for metric, detector in detectors.items():
        count, details = detector(path)
        result[metric] = count
        result[f"{metric}_details"] = details
    return result
