"""Static detectors derived from the configuration-smell paper mapping.

The functions in this module deliberately share one parse and traversal
implementation.  They remain independently callable so each smell has a
stable metric and finding rule without nine slightly different YAML walkers.
"""

from __future__ import annotations

from collections import defaultdict
from functools import lru_cache
from pathlib import Path
import re

import yaml

from ansibleguard.detector_config import load_detector_config
from ansibleguard.document import AnsibleSafeLoader, inspect_document
from ansibleguard.role_context import (
    automatic_role_variable_files,
    resolve_role_context,
)
from ansibleguard.analysis_context import IncludeResolution
from ansibleguard.jinja_semantics import conjunctive_defined_guards
from ansibleguard.task_semantics import task_action
from ansibleguard.detectors.source_lines import source_line

NESTED_SECTIONS = ("block", "rescue", "always")
TASK_SECTIONS = ("pre_tasks", "tasks", "post_tasks", "handlers")
ROLE_DIRS = ("tasks", "handlers", "defaults", "vars", "meta")
# A marker joined to an identifier ("containerd-hack", "todo_list") is a name,
# not an unresolved-work marker.
TODO_RE = re.compile(r"(?<![\w./-])(TODO|FIXME|HACK|XXX)(?![\w./-])", re.IGNORECASE)
JINJA_RE = re.compile(r"{{.*?}}|{%.*?%}", re.DOTALL)
VAR_RE = re.compile(r"(?<![\w.])([A-Za-z_][\w]*)(?:\.[A-Za-z_][\w]*)?")
JINJA_STRING_RE = re.compile(r"'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\"")

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
    "ansible_collection_name",
    "ansible_config_file",
    "ansible_dependent_role_names",
    "ansible_diff_mode",
    "ansible_facts",
    "ansible_forks",
    "ansible_inventory_sources",
    "ansible_limit",
    "ansible_loop",
    "ansible_loop_var",
    "ansible_parent_role_names",
    "ansible_parent_role_paths",
    "ansible_play_batch",
    "ansible_play_hosts",
    "ansible_play_hosts_all",
    "ansible_play_name",
    "ansible_play_role_names",
    "ansible_role_name",
    "ansible_role_names",
    "ansible_run_tags",
    "ansible_search_path",
    "ansible_skip_tags",
    "ansible_verbosity",
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
    "role_names",
    "role_path",
    "vars",
    "item",
    "result",
    "true",
    "false",
    "none",
    "null",
}

BUILTIN_FACT_ACTIONS = frozenset({"package_facts", "service_facts"})

INPUT_CONTRACT_UNCERTAINTY = frozenset({
    "possible_required_role_input",
    "possible_playbook_input",
    "possible_task_fragment_input",
})


def _variable_classification(uncertainty_sources):
    """Map definition evidence to the v0.0.6.1 three-way concept model."""
    sources = frozenset(uncertainty_sources)
    if not sources:
        return "missing-internal-variable"
    if sources <= INPUT_CONTRACT_UNCERTAINTY:
        return "undeclared-input-contract"
    return "unresolved-runtime-input"


def _conjunctive_condition_atoms(value):
    """Return normalized safe conjuncts, or an empty set when implication is unknown.

    This deliberately proves only the small monotonic subset needed for an
    identical-or-stronger consumer condition. Disjunctions and templated
    conditions remain MAY rather than being guessed into certainty.
    """
    values = value if isinstance(value, list) else [value]
    atoms = set()
    for condition in values:
        if not isinstance(condition, str) or re.search(r"\bor\b", condition):
            return frozenset()
        parts = re.split(r"\band\b", condition)
        for part in parts:
            normalized = re.sub(r"\s+", " ", part.strip().strip("() "))
            if not normalized or "{{" in normalized or "{%" in normalized:
                return frozenset()
            atoms.add(normalized)
    return frozenset(atoms)

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
    "null",
    "if",
    "elif",
    "else",
    "endif",
    "for",
    "endfor",
    "block",
    "endblock",
    "macro",
    "endmacro",
    "call",
    "endcall",
    "filter",
    "endfilter",
    "raw",
    "endraw",
    "set",
    "endset",
    "include",
    "import",
    "from",
    "as",
    "with",
    "without",
    "recursive",
}


def _load(path, parsed_document=None):
    if parsed_document is not None:
        return parsed_document.document, parsed_document.source_text
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8")
        return yaml.load(text, Loader=AnsibleSafeLoader), text
    except (OSError, yaml.YAMLError):
        return None, ""


def _line_for(text, needle, start=0):
    if not needle:
        return 1
    for number, line in enumerate(text.splitlines(), 1):
        if number >= start and str(needle) in line:
            return number
    return 1


def _line_for_expression(text, expression):
    """Locate an expression even when YAML folds it across source lines."""
    normalized = re.sub(r"\s+", " ", str(expression).strip())
    if not normalized:
        return 1

    flattened = []
    source_lines = []
    previous_was_space = False
    for line_number, line in enumerate(text.splitlines(), 1):
        for character in line:
            if character.isspace():
                if not previous_was_space:
                    flattened.append(" ")
                    source_lines.append(line_number)
                previous_was_space = True
            else:
                flattened.append(character)
                source_lines.append(line_number)
                previous_was_space = False
        if not previous_was_space:
            flattened.append(" ")
            source_lines.append(line_number)
            previous_was_space = True

    position = "".join(flattened).find(normalized)
    if position >= 0:
        return source_lines[position]

    # Keep a useful fallback for parser-normalized values that cannot be
    # matched byte-for-byte, but never assume line 1 merely because a
    # multiline prefix was searched on a single physical line.
    prefix = normalized[:80]
    position = "".join(flattened).find(prefix)
    return source_lines[position] if position >= 0 else 1


class _ExpressionLocator:
    """Map repeated normalized expressions to their next physical location."""

    def __init__(self, text):
        flattened = []
        source_lines = []
        previous_was_space = False
        for line_number, line in enumerate(text.splitlines(), 1):
            for character in line:
                if character.isspace():
                    if not previous_was_space:
                        flattened.append(" ")
                        source_lines.append(line_number)
                    previous_was_space = True
                else:
                    flattened.append(character)
                    source_lines.append(line_number)
                    previous_was_space = False
            if not previous_was_space:
                flattened.append(" ")
                source_lines.append(line_number)
                previous_was_space = True
        self._text = "".join(flattened)
        self._source_lines = source_lines
        self._cursors = {}

    def line_for(self, expression):
        normalized = re.sub(r"\s+", " ", str(expression).strip())
        if not normalized:
            return 1
        start = self._cursors.get(normalized, 0)
        position = self._text.find(normalized, start)
        if position < 0:
            prefix = normalized[:80]
            position = self._text.find(prefix, start)
        if position < 0 and start:
            # Wrap once so a caller can make a fresh pass while repeated
            # expressions within that pass still advance in source order.
            position = self._text.find(normalized)
            if position < 0:
                position = self._text.find(normalized[:80])
        if position < 0:
            # YAML double-quoted scalars decode escapes before the detector
            # sees them.  Consequently a parsed expression containing an
            # actual newline or tab may not match its source spelling (for
            # example ``'\n'``).  The Jinja opener plus leading identifier is
            # still stable and points to the correct expression node.
            leading = re.match(
                r"(?:\{\{|\{%)\s*(?:\(\s*)*([A-Za-z_][\w]*)", normalized,
            )
            if leading:
                pattern = re.compile(
                    rf"(?:\{{\{{|\{{%)\s*(?:\(\s*)*"
                    rf"{re.escape(leading.group(1))}\b"
                )
                match = pattern.search(self._text, start)
                if match is None and start:
                    match = pattern.search(self._text)
                if match is not None:
                    position = match.start()
        if position < 0:
            return 1
        self._cursors[normalized] = position + max(1, len(normalized))
        return self._source_lines[position]


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


def detect_complex_expressions(
    path, threshold=6, length_threshold=100, parsed_document=None,
    expression_locator=None,
):
    document, text = _load(path, parsed_document)
    details = []
    seen = set()
    expression_locator = expression_locator or _ExpressionLocator(text)
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
            if len(normalized) > length_threshold:
                score += 2
            if score >= threshold:
                details.append(
                    {
                        "line": expression_locator.line_for(normalized),
                        "score": score,
                        "expression": normalized,
                        "issue": f"Jinja/conditional expression complexity is {score} (threshold {threshold}).",
                    }
                )
    return len(details), details


def detect_incomplete_tasks(path, parsed_document=None):
    # v0.0.4: scan only parsed task-level fields, never raw YAML lines/comments.
    # The previous line-scan approach fired on legitimate YAML comments (e.g.
    # "# TODO: upstream bug") which are not incomplete task logic, causing ~9%
    # precision. We now only flag the task name and module argument strings.
    document, text = _load(path, parsed_document)
    details = []
    for task, _ in _iter_tasks(document):
        task_name = task.get("name", "")
        # Check task name
        for field_value in (task_name,):
            match = TODO_RE.search(str(field_value)) if field_value else None
            if match:
                line = _line_for(text, task_name) if task_name else 1
                details.append(
                    {
                        "line": line,
                        "marker": match.group(1).upper(),
                        "issue": f"Unresolved {match.group(1).upper()} marker in task name.",
                    }
                )
                break
        else:
            # Check module argument strings (but not task name again)
            for key, value in task.items():
                if key in ("name", "when", "register", "tags", "notify", "become",
                           "become_user", "no_log", "ignore_errors", "vars",
                           "loop", "with_items", "block", "rescue", "always"):
                    continue
                if isinstance(value, str):
                    match = TODO_RE.search(value)
                    if match:
                        line = _line_for(text, task_name) if task_name else 1
                        details.append(
                            {
                                "line": line,
                                "marker": match.group(1).upper(),
                                "issue": (
                                    f"Unresolved {match.group(1).upper()} marker "
                                    f"in task argument '{key}'."
                                ),
                            }
                        )
                        break
    return len(details), details


_URL_RE = re.compile(r"https?://\S{40,}")
_BASE64_BLOB_RE = re.compile(r"^\s*(?:[\w.=+/]{60,})\s*$")


def detect_long_statements(path, threshold=120, parsed_document=None):
    _, text = _load(path, parsed_document)
    details = []
    for line_number, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        length = len(line.expandtabs(2))
        if length <= threshold:
            continue
        stripped = line.strip()
        # Skip unavoidable long lines: long URLs
        if _URL_RE.search(stripped):
            continue
        # Skip base64 blobs (certificates, keys, encoded content)
        if _BASE64_BLOB_RE.match(stripped):
            continue
        details.append(
            {
                "line": line_number,
                "length": length,
                "issue": f"Line has {length} characters (threshold {threshold}).",
            }
        )
    return len(details), details


def detect_excessive_nesting(path, threshold=3, parsed_document=None):
    document, text = _load(path, parsed_document)
    details = []
    for task, depth in _iter_tasks(document):
        if depth > threshold:
            name = task.get("name", "Unnamed task")
            details.append(
                {
                    "line": source_line(task, fallback=_line_for(text, name)),
                    "task_name": name,
                    "depth": depth,
                    "issue": f"Task nesting depth is {depth} (threshold {threshold}).",
                }
            )
    return len(details), details


def detect_missing_abstraction(path, threshold=10, parsed_document=None):
    document_info = parsed_document or inspect_document(path)
    if document_info.document_type not in {"playbook", "tasks", "handlers"}:
        return 0, []
    document, _ = _load(path, parsed_document)
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


def detect_empty_abstractions(path, parsed_document=None):
    document, text = _load(path, parsed_document)
    details = []
    variable_directories = {"defaults", "vars", "group_vars", "host_vars"}
    is_variable_file = bool(variable_directories.intersection(Path(path).parts))
    if document in (None, [], {}) and not is_variable_file:
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
    context = resolve_role_context(path)
    if context is None:
        return None, None
    return (None if context.standalone else context.root.parent), context.root


def _role_anchor(role_root, repository_context=None):
    role_root = Path(role_root).resolve()
    selected = (
        set(repository_context.parsed_documents)
        if repository_context is not None else None
    )
    for section in ("tasks", "handlers"):
        for suffix in ("yml", "yaml"):
            candidate = role_root / section / f"main.{suffix}"
            if candidate in selected if selected is not None else candidate.exists():
                return candidate
    candidates = (
        sorted(path for path in selected if path == role_root or role_root in path.parents)
        if selected is not None
        else sorted(
            p for pattern in ("*.yml", "*.yaml") for p in role_root.rglob(pattern)
        )
    )
    return candidates[0] if candidates else None


def detect_unstructured_module(path):
    roles_dir, role_root = _role_context(path)
    if role_root is None or Path(path).resolve() != _role_anchor(role_root):
        return 0, []
    details = []
    tasks_dir = role_root / "tasks"
    tasks_main = [tasks_dir / "main.yml", tasks_dir / "main.yaml"]
    task_files = [
        candidate
        for pattern in ("*.yml", "*.yaml")
        for candidate in tasks_dir.glob(pattern)
    ] if tasks_dir.is_dir() else []
    # A role may intentionally contain only defaults, handlers, files or
    # templates.  Report only the observable structural defect: task files
    # exist but there is no conventional tasks/main entry point.
    if task_files and not any(candidate.exists() for candidate in tasks_main):
        details.append(
            {
                "line": 1,
                "role": role_root.name,
                "issue": f"Role '{role_root.name}' has no tasks/main.yml or tasks/main.yaml entry point.",
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


def detect_broken_role_dependencies(path, repository_context=None):
    path = Path(path).resolve()
    roles_dir, role_root = _role_context(path)
    if role_root is None:
        return 0, []
    standalone = roles_dir is None
    if (
        repository_context is not None
        and not standalone
        and repository_context.role_analysis_anchor is not None
        and path != repository_context.role_analysis_anchor
    ):
        return 0, []
    if standalone:
        anchor = _role_anchor(role_root, repository_context)
        project_anchors = [anchor] if anchor is not None else []
        role_roots = {role_root.name: role_root}
    else:
        if repository_context is not None:
            role_roots = dict(repository_context.role_roots)
        else:
            role_roots = {
                directory.name: directory
                for directory in roles_dir.iterdir()
                if directory.is_dir()
            }
        project_anchors = (
            [repository_context.role_analysis_anchor]
            if repository_context is not None
            and repository_context.role_analysis_anchor is not None
            else sorted(
                anchor
                for candidate_role in role_roots.values()
                for anchor in [_role_anchor(candidate_role, repository_context)]
                if anchor is not None
            )
        )
    if project_anchors and path != project_anchors[0]:
        return 0, []

    graph = defaultdict(list)
    details = []
    role_names = set(role_roots)
    for role_name in role_names:
        meta = None
        for suffix in ("yml", "yaml"):
            candidate = role_roots[role_name] / "meta" / f"main.{suffix}"
            shared = (
                repository_context.parsed_documents.get(candidate.resolve())
                if repository_context is not None else None
            )
            if shared is not None:
                meta, _ = _load(candidate, parsed_document=shared)
                break
            if repository_context is None and candidate.exists():
                meta, _ = _load(candidate)
                break
        for dependency in _dependency_names(meta):
            # "DavidWittman.redis" is a different (Galaxy) role than a local
            # role named "redis"; only an exact name, or a three-part
            # collection FQCN ending in this role, can refer to the role itself.
            parts = dependency.split(".")
            if dependency == role_name or (len(parts) == 3 and parts[-1] == role_name):
                details.append(
                    {
                        "line": 1,
                        "role": role_name,
                        "dependency": dependency,
                        "issue": f"Role '{role_name}' depends on itself.",
                    }
                )
                continue
            local_name = dependency if dependency in role_names else (
                parts[-1] if len(parts) == 3 and parts[-1] in role_names else None
            )
            if local_name is not None:
                graph[role_name].append(local_name)
            # v0.0.4: removed "missing local role" check — it had 0% precision because
            # most dependencies are Galaxy/collection roles installed elsewhere, not
            # under a local roles/ directory. Only self-dependency and cycle detection
            # are reliable static checks.

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


def _collect_defined_variables(
    document, path, known_variables=(), include_task_definitions=True,
    include_external_definitions=True, include_play_definitions=True,
):
    defined = set(COMMON_VARIABLES) | set(known_variables)
    if isinstance(document, list):
        for entry in document:
            if not isinstance(entry, dict):
                continue
            if include_play_definitions and isinstance(entry.get("vars"), dict):
                defined.update(entry["vars"])
            if include_external_definitions:
                for vars_file in entry.get("vars_files", []) or []:
                    vars_path = Path(path).parent / str(vars_file)
                    vars_document, _ = _load(vars_path)
                    if isinstance(vars_document, dict):
                        defined.update(vars_document)
    for task, _ in _iter_tasks(document):
        if include_task_definitions and task.get("register"):
            defined.add(str(task["register"]))
        if include_task_definitions:
            for key in ("set_fact", "ansible.builtin.set_fact"):
                if isinstance(task.get(key), dict):
                    defined.update(name for name in task[key] if name != "cacheable")
            for key in ("include_vars", "ansible.builtin.include_vars"):
                include_vars = task.get(key)
                if isinstance(include_vars, dict) and include_vars.get("name"):
                    defined.add(str(include_vars["name"]))
        loop_control = task.get("loop_control")
        if isinstance(loop_control, dict):
            for variable_key in ("loop_var", "index_var"):
                if loop_control.get(variable_key):
                    defined.add(str(loop_control[variable_key]))

    roles_dir, role_root = _role_context(path)
    if role_root and include_external_definitions:
        for directory_name in ("defaults", "vars"):
            for variable_file in automatic_role_variable_files(
                role_root, directory_name
            ):
                variables, _ = _load(variable_file)
                if isinstance(variables, dict):
                    defined.update(variables)
    # Inventory variables can live beside any project ancestor. Loading these
    # visible repository definitions avoids treating normal group/host vars as
    # unguarded merely because they are not declared in the current playbook.
    if include_external_definitions:
        seen_variable_files = set()
        for parent in (Path(path).resolve().parent, *Path(path).resolve().parents):
            for directory_name in ("group_vars", "host_vars"):
                directory = parent / directory_name
                if not directory.is_dir():
                    continue
                for pattern in ("*.yml", "*.yaml"):
                    for variable_file in directory.rglob(pattern):
                        if variable_file in seen_variable_files:
                            continue
                        seen_variable_files.add(variable_file)
                        variables, _ = _load(variable_file)
                        if isinstance(variables, dict):
                            defined.update(variables)
    return defined


def _task_variable_contexts(document):
    """Yield tasks with stable scope plus inherited vars and defined-guards."""
    ordinal = 0

    def walk(
        items, play_index, prefix=(), inherited=frozenset(),
        inherited_guards=frozenset(),
        inherited_conditional=False,
        inherited_control_optional=False,
    ):
        nonlocal ordinal
        if not isinstance(items, list):
            return
        for position, task in enumerate(items):
            if not isinstance(task, dict):
                continue
            task_path = (*prefix, position)
            task_index = ordinal
            ordinal += 1
            task_conditional = inherited_conditional or bool(task.get("when"))
            own = set(task.get("vars", {})) if isinstance(task.get("vars"), dict) else set()
            visible = set(inherited) | own
            yield (
                task, play_index, task_index, task_path, visible,
                inherited_guards, task_conditional,
                inherited_control_optional,
            )
            block_visible = frozenset(visible)
            block_guards = frozenset(
                set(inherited_guards) | _same_task_defined_guards(task)
            )
            for section_position, section in enumerate(NESTED_SECTIONS):
                yield from walk(
                    task.get(section), play_index,
                    (*task_path, section_position), block_visible, block_guards,
                    task_conditional or section in {"rescue", "always"},
                    inherited_control_optional or section == "rescue",
                ) or []

    if not isinstance(document, list):
        return
    is_playbook = any(
        isinstance(entry, dict)
        and any(key in entry for key in ("hosts", "tasks", "pre_tasks", "post_tasks"))
        for entry in document
    )
    if not is_playbook:
        yield from walk(document, 0) or []
        return
    for play_index, play in enumerate(document):
        if not isinstance(play, dict):
            continue
        play_vars = frozenset(play.get("vars", {})) if isinstance(play.get("vars"), dict) else frozenset()
        for section in TASK_SECTIONS:
            yield from walk(
                play.get(section), play_index, (), play_vars
            ) or []


def _unguarded_details(
    values, defined, text, seen, uncertainty_sources=(), maybe_defined=(),
    expression_locator=None,
):
    details = []
    for _, value in _walk_values(values):
        for expression, control_guards, scoped_locals in _jinja_scoped_regions(
            value
        ):
            expression_line = (
                expression_locator.line_for(expression)
                if expression_locator is not None
                else _line_for_expression(text, expression)
            )
            body = expression[2:-2]
            analysis_body = body
            guarded = set(
                re.findall(
                    r"([A-Za-z_][\w]*)\s*(?:\|\s*(?:(?:[A-Za-z_][\w]*\.)*default|d)\b|"
                    r"\bis\s+(?:defined|not\s+undefined)\b)",
                    body,
                )
            )
            # Identifiers inside quoted literals (URLs are a common case) are
            # data, not Jinja variables. Tokenizing the raw expression used to
            # report words such as ``adfinis`` from an HTTPS URL.
            set_assignment = re.match(
                r"\s*set\s+[A-Za-z_][\w]*\s*=\s*(.*)\Z", body,
                flags=re.DOTALL,
            )
            if set_assignment:
                # Assignment targets are definitions, while references on the
                # right-hand side are evaluated in the old lexical scope.
                analysis_body = set_assignment.group(1)
                variable_body = JINJA_STRING_RE.sub("", analysis_body)
            elif re.fullmatch(r"\s*(?:set\s+[A-Za-z_][\w]*|endset)\s*", body):
                variable_body = ""
            else:
                variable_body = JINJA_STRING_RE.sub("", body)
            # A nested ``{{ ... }}`` inside a quoted default can make the
            # outer non-greedy Jinja match end before the closing quote.  In
            # that partial expression, everything after the unmatched quote
            # is still literal data rather than identifiers.
            for quote in ("'", '"'):
                if variable_body.count(quote) % 2:
                    variable_body = variable_body.split(quote, 1)[0]
            for variable in VAR_RE.findall(variable_body):
                if (
                    variable in defined
                    or variable in scoped_locals
                    or variable.lower() in JINJA_WORDS
                    or variable in guarded
                    or variable in control_guards
                    or variable.startswith("ansible_")
                    or variable.startswith("vault_")
                ):
                    continue
                # Testing absence is itself safe, but it must not guard a
                # separate interpolation elsewhere in the same scalar.
                if re.fullmatch(
                    rf"\s*{re.escape(variable)}(?:\.[A-Za-z_][\w]*)*\s+"
                    r"is\s+(?:not\s+defined|undefined)\s*",
                    analysis_body,
                ):
                    continue
                # Filter/function names occur after a pipe or as calls.
                if re.search(
                    rf"\|\s*{re.escape(variable)}\b"
                    rf"|\b{re.escape(variable)}\s*\("
                    rf"|\b{re.escape(variable)}\s*="
                    rf"|\bis\s+(?:not\s+)?{re.escape(variable)}\b",
                    analysis_body,
                ):
                    continue
                key = (expression_line, variable, expression)
                if key in seen:
                    continue
                seen.add(key)
                variable_uncertainty = set(uncertainty_sources)
                if isinstance(maybe_defined, dict):
                    variable_uncertainty.update(maybe_defined.get(variable, ()))
                elif variable in maybe_defined:
                    variable_uncertainty.add("static_include_execution_context")
                variable_classification = _variable_classification(
                    variable_uncertainty
                )
                issues = {
                    "missing-internal-variable": (
                        f"Internal variable '{variable}' has no visible definition, "
                        "runtime producer, default, or defined guard."
                    ),
                    "undeclared-input-contract": (
                        f"Input variable '{variable}' is consumed without a visible "
                        "default, declared contract, or caller value."
                    ),
                    "unresolved-runtime-input": (
                        f"Runtime input variable '{variable}' may be supplied by "
                        "dynamic execution context that static analysis cannot prove."
                    ),
                }
                detail = {
                        "line": expression_line,
                        "variable": variable,
                        "expression": expression,
                        "issue": issues[variable_classification],
                        "variable_classification": variable_classification,
                        "legacy_concept_id": "unguarded-variable",
                        "confidence": "low" if variable_uncertainty else "medium",
                        "resolution_scope": "repository-static",
                        "confidence_factors": {
                            "positive": [
                                "jinja_reference",
                                "no_visible_static_definition",
                                "no_default_or_defined_guard",
                            ],
                            "negative": sorted(variable_uncertainty),
                        },
                    }
                if variable_uncertainty:
                    resolution_status = (
                        "EXTERNAL_INPUT_UNCERTAIN"
                        if variable_classification == "undeclared-input-contract"
                        else "RUNTIME_CONTEXT_UNCERTAIN"
                    )
                    detail.update(
                        {
                            "semantic_status": "UNCERTAIN",
                            "resolution_status": resolution_status,
                            "confidence": "low",
                            "uncertainty_sources": sorted(variable_uncertainty),
                            "resolution_evidence": {
                                "proved": ["no_visible_static_definition"],
                                "blockers": sorted(variable_uncertainty),
                            },
                            "confidence_factors": {
                                "positive": ["no_visible_static_definition"],
                                "negative": sorted(variable_uncertainty),
                            },
                        }
                    )
                else:
                    detail.update(
                        {
                            "semantic_status": "UNRESOLVED",
                            "resolution_status": "CANDIDATE_MISSING",
                            "resolution_evidence": {
                                "proved": [
                                    "no_visible_static_definition",
                                    "no_runtime_definition_source",
                                    "no_default_or_defined_guard",
                                ],
                                "blockers": [],
                            },
                            "confidence_factors": {
                                "positive": [
                                    "no_visible_static_definition",
                                    "no_runtime_definition_source",
                                ],
                                "negative": [],
                            },
                        }
                    )
                details.append(detail)
    return details


def _jinja_scoped_regions(value):
    """Yield fragments with active conditional guards and lexical locals."""
    stack = []
    persistent_locals = set()
    raw_depth = 0
    for expression in JINJA_RE.findall(value):
        body = expression[2:-2].strip().strip("-").strip()
        keyword = body.partition(" ")[0] if expression.startswith("{%") else ""
        if keyword == "raw":
            raw_depth += 1
            continue
        if keyword == "endraw" and raw_depth:
            raw_depth -= 1
            continue
        if raw_depth:
            continue
        pending_assignment = None
        if expression.startswith("{%"):
            keyword, _, condition = body.partition(" ")
            if keyword == "if":
                stack.append({
                    "kind": "if",
                    "guards": set(conjunctive_defined_guards(condition)),
                    "locals": set(),
                })
            elif keyword == "for":
                target, separator, _iterable = condition.partition(" in ")
                loop_locals = {
                    item.strip()
                    for item in target.split(",")
                    if separator and re.fullmatch(r"[A-Za-z_][\w]*", item.strip())
                }
                if loop_locals:
                    loop_locals.add("loop")
                stack.append({
                    "kind": "for", "guards": set(), "locals": loop_locals,
                })
            elif keyword == "elif" and stack and stack[-1]["kind"] == "if":
                stack[-1]["guards"] = set(
                    conjunctive_defined_guards(condition)
                )
            elif keyword == "else" and stack and stack[-1]["kind"] == "if":
                stack[-1]["guards"] = set()
            elif keyword == "else" and stack and stack[-1]["kind"] == "for":
                # A Jinja for/else branch runs only when no iteration occurred,
                # so neither the loop target nor ``loop`` exists there.
                stack[-1]["locals"] = set()
            elif keyword == "endif" and stack and stack[-1]["kind"] == "if":
                stack.pop()
            elif keyword == "endfor" and stack and stack[-1]["kind"] == "for":
                stack.pop()
            elif keyword == "set":
                match = re.match(r"([A-Za-z_][\w]*)\s*=", condition)
                if match:
                    # The assignment target is not visible while evaluating
                    # its own right-hand side. Commit it after this expression
                    # has been yielded to the reference analyzer.
                    pending_assignment = match.group(1)
                else:
                    block_match = re.fullmatch(r"([A-Za-z_][\w]*)", condition)
                    if block_match:
                        stack.append({
                            "kind": "set-block",
                            "guards": set(),
                            "locals": set(),
                            "target": block_match.group(1),
                        })
            elif keyword == "endset" and stack and stack[-1]["kind"] == "set-block":
                pending_assignment = stack.pop()["target"]
        active_guards = frozenset().union(
            *(frame["guards"] for frame in stack)
        ) if stack else frozenset()
        active_locals = set(persistent_locals)
        for frame in stack:
            active_locals.update(frame["locals"])
        yield expression, active_guards, frozenset(active_locals)
        if pending_assignment:
            loop_frame = next(
                (frame for frame in reversed(stack) if frame["kind"] == "for"),
                None,
            )
            if loop_frame is None:
                persistent_locals.add(pending_assignment)
            else:
                loop_frame["locals"].add(pending_assignment)


def _possible_jinja_roots(values):
    """Collect root identifiers used by Jinja fragments for indexed lookup."""
    return {
        variable
        for _, value in _walk_values(values)
        for expression in JINJA_RE.findall(value)
        for variable in VAR_RE.findall(
            JINJA_STRING_RE.sub("", expression[2:-2])
        )
    }


def _runtime_uncertainty_sources(repository_context, path, task_index):
    if repository_context is None:
        return ()
    if hasattr(repository_context, "uncertainty_for"):
        return repository_context.uncertainty_for(path, task_index)
    relative = repository_context.file_context_for(path).relative_path
    labels = {
        IncludeResolution.DYNAMIC: "dynamic_include",
        IncludeResolution.RUNTIME_GENERATED: "runtime_generated_include",
        IncludeResolution.EXTERNAL: "external_include",
        IncludeResolution.INACCESSIBLE: "inaccessible_include",
        IncludeResolution.DYNAMIC_ROLE: "dynamic_role",
    }
    sources = {
        labels[edge.resolution]
        for edge in repository_context.include_relationships
        if edge.source == relative
        and edge.resolution in labels
        and (edge.task_ordinal is None or edge.task_ordinal <= task_index)
    }
    selected_documents = set(repository_context.parsed_documents)
    for edge in repository_context.include_relationships:
        if (
            edge.source != relative
            or edge.action.rsplit(".", 1)[-1] != "include_vars"
            or edge.resolution != IncludeResolution.STATIC_RESOLVED
            or not edge.resolved_target
            or (
                edge.task_ordinal is not None
                and edge.task_ordinal > task_index
            )
        ):
            continue
        target = (repository_context.root / edge.resolved_target).resolve()
        represented = target in selected_documents or any(
            target in candidate.parents for candidate in selected_documents
        )
        if not represented:
            sources.add("static_include_vars_outside_population")
    parsed = repository_context.document_for(path).document
    entries = parsed if isinstance(parsed, list) else ()

    def dynamic_vars_files(entry):
        if not isinstance(entry, dict):
            return False
        references = entry.get("vars_files") or ()
        if isinstance(references, str):
            references = (references,)
        return any(
            isinstance(reference, str)
            and ("{{" in reference or "{%" in reference)
            for reference in references
        )

    if any(dynamic_vars_files(entry) for entry in entries):
        sources.add("dynamic_vars_files")

    inventory_roots = tuple(
        repository_context.root / relative
        for relative in repository_context.project_model.inventory_sources
    )
    for inventory_path, inventory_document in (
        repository_context.parsed_documents.items()
    ):
        if not any(
            inventory_path == root or root in inventory_path.parents
            for root in inventory_roots
        ):
            continue
        inventory_value = inventory_document.document
        if isinstance(inventory_value, dict) and isinstance(
            inventory_value.get("plugin"), str
        ):
            sources.add("possible_dynamic_inventory_definition")
            break
    builtin_prefixes = ("ansible.builtin.", "ansible.legacy.")
    for task in repository_context.tasks_for(path):
        if task.ordinal > task_index or not task.action:
            continue
        action = task.action.lower()
        short_action = action.rsplit(".", 1)[-1]
        if (
            short_action not in BUILTIN_FACT_ACTIONS
            and not action.startswith(builtin_prefixes)
            and (action.endswith("_facts") or action.endswith(".facts"))
        ):
            sources.add("custom_module_fact")
    return tuple(sorted(sources))


def _same_task_defined_guards(task):
    """Compatibility wrapper around the shared safe guard semantics."""
    return set(conjunctive_defined_guards(
        task.get("when") if isinstance(task, dict) else None
    ))


def _post_task_defined_guards(task):
    """Return variables proven defined when execution continues past a task."""
    if not isinstance(task, dict) or task.get("ignore_errors") is True:
        return set()
    action = task_action(task)
    action = (action or "").rsplit(".", 1)[-1]
    if action == "assert":
        payload = task.get("assert") or task.get("ansible.builtin.assert") or {}
        return set(conjunctive_defined_guards(
            payload.get("that") if isinstance(payload, dict) else None
        ))
    if action != "fail":
        return set()
    conditions = task.get("when")
    conditions = conditions if isinstance(conditions, list) else [conditions]
    proven = set()
    for condition in conditions:
        if not isinstance(condition, str) or re.search(r"\bor\b", condition):
            continue
        proven.update(re.findall(
            r"([A-Za-z_][\w]*)(?:\.[A-Za-z_][\w]*)*\s+"
            r"is\s+(?:undefined|not\s+defined)\b",
            condition,
        ))
    return proven


@lru_cache(maxsize=512)
def _role_argument_contracts(role_root, entrypoint):
    """Return required and optional inputs from a role argument specification.

    A required role argument is a proof that the role task cannot execute with
    the root name undefined: Ansible validates the contract before running the
    role. Optional arguments remain MAY-defined unless another source supplies
    a definition. We deliberately do not treat schema ``default`` metadata as
    a runtime assignment without stronger execution evidence.
    """
    root = Path(role_root)
    paths = (
        root / "meta" / "argument_specs.yml",
        root / "meta" / "argument_specs.yaml",
    )
    for candidate in paths:
        try:
            payload = yaml.load(
                candidate.read_text(encoding="utf-8"), Loader=AnsibleSafeLoader
            )
        except (OSError, UnicodeError, yaml.YAMLError):
            continue
        specs = payload.get("argument_specs") if isinstance(payload, dict) else None
        if not isinstance(specs, dict):
            continue
        entry = specs.get(entrypoint)
        options = (
            entry.get("options", {}) if isinstance(entry, dict) else {}
        )
        if not isinstance(options, dict):
            return frozenset(), frozenset()
        options = {str(name): definition for name, definition in options.items()}
        required = frozenset(
            name for name, definition in options.items()
            if isinstance(definition, dict) and definition.get("required") is True
        )
        return required, frozenset(options) - required
    return frozenset(), frozenset()


def _role_argument_contracts_for_path(path, role_context):
    """Return contracts only for the directly validated role task entry point."""
    if role_context is None or role_context.section != "tasks":
        return frozenset(), frozenset()
    task_path = Path(path).resolve()
    tasks_root = (role_context.root / "tasks").resolve()
    if task_path.parent != tasks_root or task_path.suffix.lower() not in {
        ".yml", ".yaml"
    }:
        return frozenset(), frozenset()
    return _role_argument_contracts(
        str(role_context.root), task_path.stem
    )


def detect_unguarded_variables(
    path, known_variables=(), symbol_index=None, parsed_document=None,
    repository_context=None, expression_locator=None,
):
    document, text = _load(path, parsed_document)
    base_defined = _collect_defined_variables(
        document,
        path,
        known_variables,
        include_task_definitions=False,
        include_external_definitions=symbol_index is None,
        include_play_definitions=False,
    )
    details = []
    seen = set()
    runtime_before = set()
    runtime_maybe_before = set()
    conditional_runtime_atoms = {}
    current_play_index = None
    expression_locator = expression_locator or _ExpressionLocator(text)
    for (
        task, play_index, task_index, task_path, lexical_names,
        inherited_guards, task_conditional, task_control_optional,
    ) in (
        _task_variable_contexts(document) or []
    ):
        if current_play_index is not None and play_index != current_play_index:
            # Runtime task definitions are scoped to the modeled play. Cross-
            # play host overlap is not guaranteed by a repository-only scan.
            runtime_before.clear()
            runtime_maybe_before.clear()
            conditional_runtime_atoms.clear()
        current_play_index = play_index
        defined = (
            set(base_defined) | set(lexical_names) | set(inherited_guards)
            | runtime_before
        )
        defined.update(_same_task_defined_guards(task))
        consumer_atoms = _conjunctive_condition_atoms(task.get("when"))
        for variable, producer_atoms in conditional_runtime_atoms.items():
            if producer_atoms and producer_atoms <= consumer_atoms:
                defined.add(variable)
        task_values = {
            key: value for key, value in task.items() if key not in NESTED_SECTIONS
        }
        maybe_defined = {
            variable: {"conditional_runtime_definition"}
            for variable in runtime_maybe_before
            if variable not in defined
        }
        if symbol_index is not None:
            possible_roots = _possible_jinja_roots(task_values)
            role_context = (
                resolve_role_context(Path(path), repository_context.root)
                if repository_context is not None else None
            )
            required_role_arguments, optional_role_arguments = (
                _role_argument_contracts_for_path(path, role_context)
            )
            for variable in possible_roots:
                if variable in defined:
                    continue
                visibility = symbol_index.definition_visibility(
                    variable, path, task_index, play_index, task_path
                )
                if visibility == "must":
                    defined.add(variable)
                elif variable in required_role_arguments:
                    defined.add(variable)
                elif visibility == "may":
                    sources = symbol_index.definition_uncertainty_sources(
                        variable, path, task_index, play_index, task_path
                    )
                    maybe_defined.setdefault(variable, set()).update(sources)
                elif (
                    repository_context is not None
                    and repository_context.external_dependency_may_define(variable)
                ):
                    maybe_defined.setdefault(variable, set()).add(
                        "declared_external_dependency"
                    )
                elif role_context is not None:
                    source = (
                        "declared_optional_role_argument"
                        if variable in optional_role_arguments
                        else "possible_required_role_input"
                    )
                    maybe_defined.setdefault(variable, set()).add(source)
                elif (
                    repository_context is not None
                ):
                    source = (
                        "possible_playbook_input"
                        if parsed_document is not None
                        and parsed_document.document_type == "playbook"
                        else "possible_task_fragment_input"
                    )
                    maybe_defined.setdefault(variable, set()).add(source)
        details.extend(
            _unguarded_details(
                task_values,
                defined,
                text,
                seen,
                _runtime_uncertainty_sources(
                    repository_context, path, task_index
                ),
                maybe_defined,
                expression_locator,
            )
        )
        if task.get("register"):
            target = (
                runtime_maybe_before
                if task_control_optional else runtime_before
            )
            target.add(str(task["register"]))
            if task_control_optional:
                producer_atoms = _conjunctive_condition_atoms(task.get("when"))
                if producer_atoms:
                    conditional_runtime_atoms[str(task["register"])] = producer_atoms
            else:
                conditional_runtime_atoms.pop(str(task["register"]), None)
        for module in ("set_fact", "ansible.builtin.set_fact"):
            if isinstance(task.get(module), dict):
                target = runtime_maybe_before if task_conditional else runtime_before
                names = {
                    str(name) for name in task[module] if name != "cacheable"
                }
                target.update(names)
                producer_atoms = _conjunctive_condition_atoms(task.get("when"))
                for name in names:
                    if task_conditional and producer_atoms:
                        conditional_runtime_atoms[name] = producer_atoms
                    elif not task_conditional:
                        conditional_runtime_atoms.pop(name, None)
        for module in ("include_vars", "ansible.builtin.include_vars"):
            included = task.get(module)
            if isinstance(included, dict) and isinstance(included.get("name"), str):
                target = runtime_maybe_before if task_conditional else runtime_before
                target.add(included["name"])
                producer_atoms = _conjunctive_condition_atoms(task.get("when"))
                if task_conditional and producer_atoms:
                    conditional_runtime_atoms[included["name"]] = producer_atoms
                elif not task_conditional:
                    conditional_runtime_atoms.pop(included["name"], None)
        if not task_control_optional:
            runtime_before.update(_post_task_defined_guards(task))

    # Variable-only YAML has no tasks but can still contain templated values.
    if not list(_task_variable_contexts(document) or []):
        defined = set(base_defined)
        maybe_defined = {}
        if isinstance(document, dict):
            # Ansible variable mappings are lazily evaluated; a later key is a
            # visible definition, not an ordered runtime assignment.
            defined.update(str(name) for name in document)
        if symbol_index is not None:
            defined.update(symbol_index.static_names_for(path))
            role_context = (
                resolve_role_context(Path(path), repository_context.root)
                if repository_context is not None else None
            )
            required_role_arguments, optional_role_arguments = (
                _role_argument_contracts_for_path(path, role_context)
            )
            inventory_variable_file = any(
                part in {"group_vars", "host_vars"}
                for part in Path(path).parts
            )
            for variable in _possible_jinja_roots(document):
                if variable in defined or variable.startswith("__"):
                    continue
                visibility = symbol_index.definition_visibility(
                    variable, path, 0, 0, ()
                )
                if visibility == "must":
                    defined.add(variable)
                elif variable in required_role_arguments:
                    defined.add(variable)
                elif visibility == "may":
                    maybe_defined.setdefault(variable, set()).update(
                        symbol_index.definition_uncertainty_sources(
                            variable, path, 0, 0, ()
                        )
                    )
                elif (
                    repository_context is not None
                    and repository_context.external_dependency_may_define(variable)
                ):
                    maybe_defined.setdefault(variable, set()).add(
                        "declared_external_dependency"
                    )
                elif role_context is not None:
                    source = (
                        "declared_optional_role_argument"
                        if variable in optional_role_arguments
                        else "possible_required_role_input"
                    )
                    maybe_defined.setdefault(variable, set()).add(source)
                elif inventory_variable_file:
                    maybe_defined.setdefault(variable, set()).add(
                        "possible_inventory_precedence_input"
                    )
        details.extend(_unguarded_details(
            document, defined, text, seen,
            maybe_defined=maybe_defined,
            expression_locator=expression_locator,
        ))
    return len(details), details


def _file_role_threshold_multiplier(path: Path) -> float:
    """A3: Return a threshold multiplier based on the file's role directory.

    Handler files should fire sooner (0.5×) because they should be small.
    Top-level playbooks are allowed more tasks (1.5×) before abstraction fires.
    tasks/ files use the baseline (1.0×).
    """
    parent = Path(path).parent.name.lower()
    if parent == "handlers":
        return 0.5
    if parent in {"tasks", "pre_tasks", "post_tasks"}:
        return 1.0
    # Playbook files at project root or in a dedicated playbooks/ directory
    return 1.5


def detect_paper_candidates(
    path, symbol_index=None, parsed_document=None, repository_context=None,
    enabled_rules=None,
):
    """Run every detector and return metric/detail pairs."""
    detector_config = load_detector_config(path)
    thresholds = dict(detector_config["thresholds"])
    source_text = (
        parsed_document.source_text
        if parsed_document is not None else _load(path)[1]
    )
    # A3: Adjust size-sensitive thresholds by file role
    multiplier = _file_role_threshold_multiplier(path)
    if multiplier != 1.0:
        thresholds["missing_abstraction_tasks"] = max(
            3, int(thresholds.get("missing_abstraction_tasks", 10) * multiplier)
        )
    detectors = {
        "complex_expressions": ("complex-expression", lambda value: detect_complex_expressions(
            value,
            thresholds["complex_expression_score"],
            thresholds["complex_expression_length"],
            parsed_document,
            _ExpressionLocator(source_text),
        )),
        "incomplete_tasks": ("incomplete-task", lambda value: detect_incomplete_tasks(
            value, parsed_document
        )),
        "long_statements": ("long-statement", lambda value: detect_long_statements(
            value, thresholds["long_statement_length"], parsed_document
        )),
        "unstructured_modules": ("unstructured-module", detect_unstructured_module),
        "empty_abstractions": ("empty-abstraction", lambda value: detect_empty_abstractions(
            value, parsed_document
        )),
        "excessive_nesting": ("excessive-nesting", lambda value: detect_excessive_nesting(
            value, thresholds["excessive_nesting_depth"], parsed_document
        )),
        "missing_abstractions": ("missing-abstraction", lambda value: detect_missing_abstraction(
            value, thresholds["missing_abstraction_tasks"], parsed_document
        )),
        "broken_role_dependencies": ("broken-role-dependency", lambda value: detect_broken_role_dependencies(
            value, repository_context=repository_context
        )),
        "unguarded_variables": ("unguarded-variable", lambda value: detect_unguarded_variables(
            value,
            detector_config["rules"]["known_variables"],
            symbol_index=symbol_index,
            parsed_document=parsed_document,
            repository_context=repository_context,
            expression_locator=_ExpressionLocator(source_text),
        )),
    }
    result = {}
    selected = set(enabled_rules) if enabled_rules is not None else None
    for metric, (rule_id, detector) in detectors.items():
        count, details = (
            (0, [])
            if selected is not None and rule_id not in selected
            else detector(path)
        )
        result[metric] = count
        result[f"{metric}_details"] = details
    return result
