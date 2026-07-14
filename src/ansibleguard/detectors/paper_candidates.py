"""Static detectors derived from the configuration-smell paper mapping.

The functions in this module deliberately share one parse and traversal
implementation.  They remain independently callable so each smell has a
stable metric and finding rule without nine slightly different YAML walkers.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import re

import yaml

from ansibleguard.document import AnsibleSafeLoader

NESTED_SECTIONS = ("block", "rescue", "always")
TASK_SECTIONS = ("pre_tasks", "tasks", "post_tasks", "handlers")
ROLE_DIRS = ("tasks", "handlers", "defaults", "vars", "meta")
TODO_RE = re.compile(r"\b(TODO|FIXME|HACK|XXX)\b", re.IGNORECASE)
JINJA_RE = re.compile(r"{{.*?}}|{%.*?%}", re.DOTALL)
VAR_RE = re.compile(r"(?<![\w.])([A-Za-z_][\w]*)(?:\.[A-Za-z_][\w]*)?")

META_KEYS = {
    "name",
    "when",
    "tags",
    "block",
    "rescue",
    "always",
    "register",
    "ignore_errors",
    "ignore_unreachable",
    "no_log",
    "become",
    "become_user",
    "delegate_to",
    "run_once",
    "any_errors_fatal",
    "vars",
    "environment",
    "notify",
    "changed_when",
    "failed_when",
    "with_items",
    "with_dict",
    "with_fileglob",
    "loop",
    "loop_control",
    "until",
    "retries",
    "delay",
    "async",
    "poll",
    "connection",
    "check_mode",
    "diff",
    "throttle",
    "serial",
    "remote_user",
    "gather_facts",
    "strategy",
    "collections",
    "max_fail_percentage",
    "order",
    "args",
    "listen",
}

COMMON_VARIABLES = {
    "ansible_check_mode",
    "ansible_config_file",
    "ansible_diff_mode",
    "ansible_facts",
    "ansible_forks",
    "ansible_inventory_sources",
    "ansible_play_batch",
    "ansible_play_hosts",
    "ansible_play_hosts_all",
    "ansible_play_name",
    "ansible_version",
    "group_names",
    "groups",
    "hostvars",
    "inventory_dir",
    "inventory_file",
    "inventory_hostname",
    "inventory_hostname_short",
    "omit",
    "playbook_dir",
    "role_name",
    "role_path",
    "item",
    "result",
    "true",
    "false",
    "none",
}

JINJA_WORDS = {
    "and",
    "or",
    "not",
    "in",
    "is",
    "defined",
    "undefined",
    "true",
    "false",
    "none",
    "if",
    "else",
    "for",
    "with",
    "without",
    "recursive",
}


def _load(path):
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8")
        return yaml.load(text, Loader=AnsibleSafeLoader), text
    except OSError, yaml.YAMLError:
        return None, ""


def _line_for(text, needle, start=0):
    if not needle:
        return 1
    for number, line in enumerate(text.splitlines(), 1):
        if number >= start and str(needle) in line:
            return number
    return 1


def _iter_tasks(document):
    """Yield ``(task, nesting_depth)`` for task-like mappings."""

    def walk(items, depth=0):
        if not isinstance(items, list):
            return
        for task in items:
            if not isinstance(task, dict):
                continue
            yield task, depth
            for section in NESTED_SECTIONS:
                yield from walk(task.get(section), depth + 1)

    if not isinstance(document, list):
        return
    for entry in document:
        if not isinstance(entry, dict):
            continue
        found_section = False
        for section in TASK_SECTIONS:
            if isinstance(entry.get(section), list):
                found_section = True
                yield from walk(entry[section])
        if not found_section and "hosts" not in entry:
            yield from walk([entry])


def _module_keys(task):
    return [key for key in task if key not in META_KEYS]


def _walk_values(value, key=None):
    if isinstance(value, dict):
        for child_key, child in value.items():
            yield from _walk_values(child, child_key)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_values(child, key)
    elif isinstance(value, str):
        yield key, value


def detect_complex_expressions(path, threshold=6):
    document, text = _load(path)
    details = []
    seen = set()
    for key, value in _walk_values(document):
        candidates = JINJA_RE.findall(value)
        if key in {"when", "changed_when", "failed_when", "until"}:
            candidates.append(value)
        for expression in candidates:
            normalized = expression.strip()
            if normalized in seen:
                continue
            seen.add(normalized)
            score = (
                len(re.findall(r"\b(?:and|or|not|in|is)\b", normalized))
                + len(re.findall(r"==|!=|>=|<=|>|<", normalized))
                + normalized.count("|")
                + normalized.count("(")
                + normalized.count("[")
                + normalized.count("?")
            )
            if len(normalized) > 100:
                score += 2
            if score >= threshold:
                details.append(
                    {
                        "line": _line_for(text, normalized[:24]),
                        "score": score,
                        "expression": normalized,
                        "issue": f"Jinja/conditional expression complexity is {score} (threshold {threshold}).",
                    }
                )
    return len(details), details


def detect_incomplete_tasks(path):
    _, text = _load(path)
    details = []
    for line_number, line in enumerate(text.splitlines(), 1):
        match = TODO_RE.search(line)
        if match:
            details.append(
                {
                    "line": line_number,
                    "marker": match.group(1).upper(),
                    "issue": f"Unresolved {match.group(1).upper()} marker remains in configuration code.",
                }
            )
    return len(details), details


def detect_long_statements(path, threshold=120):
    _, text = _load(path)
    details = []
    for line_number, line in enumerate(text.splitlines(), 1):
        length = len(line.expandtabs(2))
        if length > threshold:
            details.append(
                {
                    "line": line_number,
                    "length": length,
                    "issue": f"Line has {length} characters (threshold {threshold}).",
                }
            )
    return len(details), details


def detect_excessive_nesting(path, threshold=3):
    document, text = _load(path)
    details = []
    for task, depth in _iter_tasks(document):
        if depth > threshold:
            name = task.get("name", "Unnamed task")
            details.append(
                {
                    "line": _line_for(text, name),
                    "task_name": name,
                    "depth": depth,
                    "issue": f"Task nesting depth is {depth} (threshold {threshold}).",
                }
            )
    return len(details), details


def detect_missing_abstraction(path, threshold=10):
    document, _ = _load(path)
    tasks = list(_iter_tasks(document))
    leaf_tasks = [
        task
        for task, _ in tasks
        if not any(section in task for section in NESTED_SECTIONS)
    ]
    abstraction_keys = {
        "include_tasks",
        "import_tasks",
        "include_role",
        "import_role",
        "ansible.builtin.include_tasks",
        "ansible.builtin.import_tasks",
        "ansible.builtin.include_role",
        "ansible.builtin.import_role",
    }
    has_abstraction = any(abstraction_keys.intersection(task) for task, _ in tasks)
    if isinstance(document, list):
        has_abstraction = has_abstraction or any(
            isinstance(entry, dict) and bool(entry.get("roles")) for entry in document
        )
    if len(leaf_tasks) > threshold and not has_abstraction:
        return 1, [
            {
                "line": 1,
                "task_count": len(leaf_tasks),
                "issue": f"{len(leaf_tasks)} leaf tasks are kept in one file without roles or task includes (threshold {threshold}).",
            }
        ]
    return 0, []


def detect_empty_abstractions(path):
    document, text = _load(path)
    details = []
    if document in (None, [], {}):
        details.append({"line": 1, "issue": "YAML abstraction is empty."})
    for task, _ in _iter_tasks(document):
        for section in NESTED_SECTIONS:
            if section in task and task[section] == []:
                name = task.get("name", "Unnamed task")
                details.append(
                    {
                        "line": _line_for(text, name),
                        "task_name": name,
                        "issue": f"Task contains an empty {section}: abstraction.",
                    }
                )
    return len(details), details


def _role_context(path):
    path = Path(path).resolve()
    parts = path.parts
    indexes = [i for i, part in enumerate(parts) if part == "roles"]
    if not indexes:
        return None, None
    index = indexes[-1]
    if index + 1 >= len(parts):
        return None, None
    roles_dir = Path(*parts[: index + 1])
    return roles_dir, roles_dir / parts[index + 1]


def _role_anchor(role_root):
    for section in ("tasks", "handlers"):
        for suffix in ("yml", "yaml"):
            candidate = role_root / section / f"main.{suffix}"
            if candidate.exists():
                return candidate
    candidates = sorted(
        p for pattern in ("*.yml", "*.yaml") for p in role_root.rglob(pattern)
    )
    return candidates[0] if candidates else None


def detect_unstructured_module(path):
    roles_dir, role_root = _role_context(path)
    if role_root is None or Path(path).resolve() != _role_anchor(role_root):
        return 0, []
    details = []
    tasks_main = [role_root / "tasks" / "main.yml", role_root / "tasks" / "main.yaml"]
    if not any(candidate.exists() for candidate in tasks_main):
        details.append(
            {
                "line": 1,
                "role": role_root.name,
                "issue": f"Role '{role_root.name}' has no tasks/main.yml or tasks/main.yaml entry point.",
            }
        )
    for directory_name in ROLE_DIRS:
        directory = role_root / directory_name
        if not directory.is_dir() or directory_name == "tasks":
            continue
        if not any(
            (directory / f"main.{suffix}").exists() for suffix in ("yml", "yaml")
        ):
            details.append(
                {
                    "line": 1,
                    "role": role_root.name,
                    "issue": f"Role directory '{directory_name}' exists without a main.yml/main.yaml entry point.",
                }
            )
    return len(details), details


def _dependency_names(meta_document):
    dependencies = (
        meta_document.get("dependencies", []) if isinstance(meta_document, dict) else []
    )
    names = []
    for dependency in dependencies or []:
        if isinstance(dependency, str):
            names.append(dependency)
        elif isinstance(dependency, dict):
            name = dependency.get("role") or dependency.get("name")
            if name:
                names.append(name)
    return names


def detect_broken_role_dependencies(path):
    path = Path(path).resolve()
    roles_dir, role_root = _role_context(path)
    if roles_dir is None:
        return 0, []
    project_anchors = sorted(
        anchor
        for candidate_role in roles_dir.iterdir()
        if candidate_role.is_dir()
        for anchor in [_role_anchor(candidate_role)]
        if anchor is not None
    )
    if project_anchors and path != project_anchors[0]:
        return 0, []

    graph = defaultdict(list)
    details = []
    role_names = {
        directory.name for directory in roles_dir.iterdir() if directory.is_dir()
    }
    for role_name in role_names:
        meta = None
        for suffix in ("yml", "yaml"):
            candidate = roles_dir / role_name / "meta" / f"main.{suffix}"
            if candidate.exists():
                meta, _ = _load(candidate)
                break
        for dependency in _dependency_names(meta):
            local_name = dependency.rsplit(".", 1)[-1]
            graph[role_name].append(local_name)
            if local_name == role_name:
                details.append(
                    {
                        "line": 1,
                        "role": role_name,
                        "dependency": dependency,
                        "issue": f"Role '{role_name}' depends on itself.",
                    }
                )
            elif "." not in dependency and local_name not in role_names:
                details.append(
                    {
                        "line": 1,
                        "role": role_name,
                        "dependency": dependency,
                        "issue": f"Local role dependency '{dependency}' does not exist under roles/.",
                    }
                )

    visiting = set()
    visited = set()

    def visit(role, trail):
        if role in visiting:
            cycle = trail[trail.index(role) :] + [role]
            details.append(
                {
                    "line": 1,
                    "role": role,
                    "issue": f"Role dependency cycle detected: {' -> '.join(cycle)}.",
                }
            )
            return
        if role in visited:
            return
        visiting.add(role)
        for dependency in graph[role]:
            if dependency in role_names:
                visit(dependency, trail + [dependency])
        visiting.remove(role)
        visited.add(role)

    for role in sorted(role_names):
        visit(role, [role])
    unique = {detail["issue"]: detail for detail in details}
    return len(unique), list(unique.values())


def _collect_defined_variables(document, path):
    defined = set(COMMON_VARIABLES)
    if isinstance(document, list):
        for entry in document:
            if not isinstance(entry, dict):
                continue
            if isinstance(entry.get("vars"), dict):
                defined.update(entry["vars"])
            for vars_file in entry.get("vars_files", []) or []:
                vars_path = Path(path).parent / str(vars_file)
                vars_document, _ = _load(vars_path)
                if isinstance(vars_document, dict):
                    defined.update(vars_document)
    for task, _ in _iter_tasks(document):
        if isinstance(task.get("vars"), dict):
            defined.update(task["vars"])
        if task.get("register"):
            defined.add(str(task["register"]))
        for key in ("set_fact", "ansible.builtin.set_fact"):
            if isinstance(task.get(key), dict):
                defined.update(task[key])
        loop_control = task.get("loop_control")
        if isinstance(loop_control, dict) and loop_control.get("loop_var"):
            defined.add(str(loop_control["loop_var"]))

    roles_dir, role_root = _role_context(path)
    if role_root:
        for directory_name in ("defaults", "vars"):
            for suffix in ("yml", "yaml"):
                variables, _ = _load(role_root / directory_name / f"main.{suffix}")
                if isinstance(variables, dict):
                    defined.update(variables)
    return defined


def detect_unguarded_variables(path):
    document, text = _load(path)
    defined = _collect_defined_variables(document, path)
    details = []
    seen = set()
    for _, value in _walk_values(document):
        for expression in JINJA_RE.findall(value):
            body = expression[2:-2]
            guarded = set(
                re.findall(
                    r"([A-Za-z_][\w]*)\s*(?:\|\s*(?:default|d)\b|\bis\s+defined\b)",
                    body,
                )
            )
            for variable in VAR_RE.findall(body):
                if (
                    variable in defined
                    or variable in JINJA_WORDS
                    or variable in guarded
                ):
                    continue
                # Filter/function names occur after a pipe or as calls.
                if re.search(
                    rf"\|\s*{re.escape(variable)}\b|\b{re.escape(variable)}\s*\(", body
                ):
                    continue
                key = (variable, expression)
                if key in seen:
                    continue
                seen.add(key)
                details.append(
                    {
                        "line": _line_for(text, expression[:24]),
                        "variable": variable,
                        "expression": expression,
                        "issue": f"Variable '{variable}' is referenced without a visible definition or default/defined guard.",
                    }
                )
    return len(details), details


def detect_paper_candidates(path):
    """Run every detector and return metric/detail pairs."""
    detectors = {
        "complex_expressions": detect_complex_expressions,
        "incomplete_tasks": detect_incomplete_tasks,
        "long_statements": detect_long_statements,
        "unstructured_modules": detect_unstructured_module,
        "empty_abstractions": detect_empty_abstractions,
        "excessive_nesting": detect_excessive_nesting,
        "missing_abstractions": detect_missing_abstraction,
        "broken_role_dependencies": detect_broken_role_dependencies,
        "unguarded_variables": detect_unguarded_variables,
    }
    result = {}
    for metric, detector in detectors.items():
        count, details = detector(path)
        result[metric] = count
        result[f"{metric}_details"] = details
    return result
