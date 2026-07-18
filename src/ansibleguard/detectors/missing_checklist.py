"""Conservative detectors for previously missing review-checklist criteria."""

from __future__ import annotations

from functools import lru_cache
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

from ansibleguard.detector_config import load_detector_config
from ansibleguard.detectors.paper_candidates import (
    COMMON_VARIABLES,
    JINJA_RE,
    JINJA_WORDS,
    META_KEYS,
    VAR_RE,
    _collect_defined_variables,
    _line_for,
    _load,
    _module_keys,
)


CONDITION_KEYS = {"changed_when", "failed_when", "until", "when"}
SET_FACT_MODULES = {"ansible.builtin.set_fact", "set_fact"}


def _task_sequences(document):
    """Yield linear task sequences whose order is statically meaningful."""
    if not isinstance(document, list):
        return
    for entry in document:
        if not isinstance(entry, dict):
            continue
        found_play_section = False
        for section in ("pre_tasks", "tasks", "post_tasks", "handlers"):
            tasks = entry.get(section)
            if isinstance(tasks, list):
                found_play_section = True
                yield [task for task in tasks if isinstance(task, dict)]
        if not found_play_section and "hosts" not in entry:
            yield [task for task in document if isinstance(task, dict)]
            return


def _task_definitions(task):
    definitions = set()
    if task.get("register"):
        definitions.add(str(task["register"]))
    for module in SET_FACT_MODULES:
        if isinstance(task.get(module), dict):
            definitions.update(str(key) for key in task[module])
    return definitions


def _expression_references(expression):
    body = expression[2:-2] if expression.startswith(("{{", "{%")) else expression
    guarded = set(
        re.findall(
            r"([A-Za-z_][\w]*)\s*(?:\|\s*(?:default|d)\b|\bis\s+defined\b)",
            body,
        )
    )
    references = set()
    for variable in VAR_RE.findall(body):
        if (
            variable in COMMON_VARIABLES
            or variable in JINJA_WORDS
            or variable in guarded
            or variable.startswith("ansible_")
        ):
            continue
        if re.search(
            rf"\|\s*{re.escape(variable)}\b|\b{re.escape(variable)}\s*\(", body
        ):
            continue
        references.add(variable)
    return references


def _task_references(task):
    references = set()

    def walk(value, key=None):
        if isinstance(value, dict):
            for child_key, child in value.items():
                if child_key in {"register", "name"}:
                    continue
                walk(child, child_key)
        elif isinstance(value, list):
            for child in value:
                walk(child, key)
        elif isinstance(value, str):
            expressions = JINJA_RE.findall(value)
            if key in CONDITION_KEYS:
                expressions.append(value)
            for expression in expressions:
                references.update(_expression_references(expression))

    walk(task)
    return references


def detect_variable_use_before_definition(path):
    """Report references to a result/fact that is only created by a later task.

    The rule intentionally ignores variables that have any visible static
    definition (play/task vars, role vars/defaults, inventory, or configured
    runtime variables). It also limits itself to linear task sections and does
    not guess across block/rescue/always control flow.
    """
    document, text = _load(path)
    known = load_detector_config(path)["rules"].get("known_variables", [])
    static_definitions = _collect_defined_variables(
        document, path, known, include_task_definitions=False
    )
    details = []
    seen = set()
    for sequence in _task_sequences(document) or []:
        definitions_by_index = [_task_definitions(task) for task in sequence]
        for index, task in enumerate(sequence):
            later = {}
            for later_index in range(index + 1, len(sequence)):
                for variable in definitions_by_index[later_index]:
                    later.setdefault(variable, later_index)
            task_static = set(task.get("vars", {})) if isinstance(task.get("vars"), dict) else set()
            for variable in sorted(_task_references(task)):
                if variable in static_definitions or variable in task_static or variable not in later:
                    continue
                identity = (id(task), variable)
                if identity in seen:
                    continue
                seen.add(identity)
                definition_task = sequence[later[variable]]
                details.append(
                    {
                        "line": _line_for(text, task.get("name")),
                        "task_name": task.get("name", "Unnamed task"),
                        "variable": variable,
                        "definition_line": _line_for(text, definition_task.get("name")),
                        "issue": (
                            f"Variable '{variable}' is used before the later task "
                            f"'{definition_task.get('name', 'Unnamed task')}' defines it."
                        ),
                    }
                )
    return len(details), details


def _role_location(path):
    resolved = Path(path).resolve()
    parts = resolved.parts
    indexes = [index for index, part in enumerate(parts) if part == "roles"]
    if not indexes or indexes[-1] + 2 >= len(parts):
        return None, None
    index = indexes[-1]
    return Path(*parts[: index + 2]), parts[index + 2]


def detect_unexpected_task_locations(path):
    """Detect document shapes or handler-only attributes in the wrong role file."""
    document, text = _load(path)
    role_root, section = _role_location(path)
    if role_root is None:
        return 0, []
    details = []
    if section in {"defaults", "vars", "meta"} and isinstance(document, list):
        details.append(
            {
                "line": 1,
                "section": section,
                "issue": f"Role {section}/ files must contain a mapping, not a task or play list.",
            }
        )
    if section in {"tasks", "handlers"} and isinstance(document, dict):
        details.append(
            {
                "line": 1,
                "section": section,
                "issue": f"Role {section}/ files must contain a task list, not a variable mapping.",
            }
        )
    if section in {"tasks", "handlers"} and isinstance(document, list):
        for entry in document:
            if isinstance(entry, dict) and "hosts" in entry:
                details.append(
                    {
                        "line": _line_for(text, entry.get("name") or "hosts"),
                        "section": section,
                        "issue": f"A play belongs in a playbook, not under a role's {section}/ directory.",
                    }
                )
            if section == "tasks" and isinstance(entry, dict) and "listen" in entry:
                details.append(
                    {
                        "line": _line_for(text, entry.get("name") or "listen"),
                        "section": section,
                        "issue": "A task using the handler-only 'listen' attribute belongs under handlers/.",
                    }
                )
    return len(details), details


def _ansible_doc_executable():
    sibling = Path(sys.executable).with_name("ansible-doc")
    if sibling.is_file():
        return str(sibling)
    return shutil.which("ansible-doc")


@lru_cache(maxsize=256)
def _module_document(module_name):
    executable = _ansible_doc_executable()
    if not executable:
        return {}
    env = os.environ.copy()
    env.setdefault(
        "ANSIBLE_LOCAL_TEMP",
        str(Path(tempfile.gettempdir()) / "ansibleguard-ansible-doc-tmp"),
    )
    candidates = [module_name]
    if "." not in module_name:
        candidates.insert(0, f"ansible.builtin.{module_name}")
    for candidate in candidates:
        try:
            result = subprocess.run(
                [executable, "-j", candidate],
                capture_output=True,
                text=True,
                env=env,
                timeout=10,
            )
            payload = json.loads(result.stdout or "{}") if result.returncode == 0 else {}
        except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError):
            payload = {}
        if payload:
            return next(iter(payload.values()), {})
    return {}


def _configured_option_deprecations(path, module_name):
    configured = load_detector_config(path)["rules"].get(
        "deprecated_module_options", {}
    )
    if not isinstance(configured, dict):
        return {}
    short_name = module_name.rsplit(".", 1)[-1]
    value = configured.get(module_name, configured.get(short_name, {}))
    return value if isinstance(value, dict) else {}


def _option_deprecation(option_spec):
    if not isinstance(option_spec, dict):
        return None
    deprecated = option_spec.get("deprecated")
    if deprecated:
        return deprecated if isinstance(deprecated, dict) else {"why": str(deprecated)}
    removal = (
        option_spec.get("removed_in_version")
        or option_spec.get("removed_in")
        or option_spec.get("removed_at_date")
    )
    return {"removed_in": removal} if removal else None


def _deprecation_message(module_name, option, deprecation):
    replacement = (
        deprecation.get("alternative")
        or deprecation.get("replacement")
        or deprecation.get("use_instead")
    )
    removal = (
        deprecation.get("removed_in")
        or deprecation.get("removed_in_version")
        or deprecation.get("version")
        or deprecation.get("removed_at_date")
    )
    reason = deprecation.get("why") or deprecation.get("description")
    message = f"Option '{option}' of module '{module_name}' is deprecated."
    if replacement:
        message += f" Use '{replacement}' instead."
    if removal:
        message += f" Removal: {removal}."
    if reason:
        message += f" {reason}"
    return message


def detect_deprecated_module_options(path):
    """Use installed Ansible metadata plus project overrides for option deprecations."""
    document, text = _load(path)
    details = []
    for sequence in _task_sequences(document) or []:
        for task in sequence:
            module_keys = _module_keys(task)
            if not module_keys:
                continue
            module_name = str(module_keys[0])
            module_value = task.get(module_name)
            supplied = dict(module_value) if isinstance(module_value, dict) else {}
            if isinstance(task.get("args"), dict):
                supplied.update(task["args"])
            if not supplied:
                continue
            metadata = _module_document(module_name)
            doc = metadata.get("doc", {}) if isinstance(metadata, dict) else {}
            options = doc.get("options", {}) if isinstance(doc, dict) else {}
            configured = _configured_option_deprecations(path, module_name)
            for option in supplied:
                deprecation = _option_deprecation(options.get(option))
                if option in configured:
                    override = configured[option]
                    deprecation = override if isinstance(override, dict) else {"why": str(override)}
                if not deprecation:
                    continue
                details.append(
                    {
                        "line": _line_for(text, task.get("name")),
                        "task_name": task.get("name", "Unnamed task"),
                        "module": module_name,
                        "option": str(option),
                        "issue": _deprecation_message(module_name, option, deprecation),
                    }
                )
    return len(details), details


def detect_missing_checklist_smells(path):
    detectors = {
        "variable_use_before_definition": detect_variable_use_before_definition,
        "unexpected_task_locations": detect_unexpected_task_locations,
        "deprecated_module_options": detect_deprecated_module_options,
    }
    result = {}
    for metric, detector in detectors.items():
        count, details = detector(path)
        result[metric] = count
        result[f"{metric}_details"] = details
    return result
