"""Automatable source-level checks from the 2025 IaC review checklist."""

from __future__ import annotations

from pathlib import Path
import re
import stat
from functools import lru_cache

import yaml

from ansibleguard.detector_config import (
    load_detector_config,
    mutating_command_pattern,
)
from ansibleguard.detectors.paper_candidates import (
    NESTED_SECTIONS,
    _iter_tasks,
    _line_for,
    _load,
)
from ansibleguard.detectors.credentials_leaking_in_log import _is_sensitive_key
from ansibleguard.detectors.source_lines import source_line

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
    r"umount|mount|kill|pkill|sed\s+-i)\b",
    re.IGNORECASE,
)
READ_ONLY_COMMAND_RE = re.compile(
    r"(?:^|[;&|]\s*)(?:"
    r"systemctl\s+(?:status|is-active|is-enabled|is-failed|show)|"
    r"(?:yum|dnf)\s+module\s+(?:list|info)|"
    r"(?:yum|dnf|rpm)\s+(?:list|repolist|info|check|verify|query)|"
    r"(?:apt|apt-get)\s+(?:list|show|search)|"
    r"kubectl\s+(?:get|describe|logs|explain|version|config)|"
    r"docker\s+(?:ps|inspect|logs|stats|info|version|images)|"
    r"cat\b|head\b|tail\b|less\b|more\b|"
    r"grep\b|find\b|locate\b|which\b|whereis\b|"
    r"ls\b|stat\b|df\b|du\b|free\b|top\b|ps\b|"
    r"id\b|whoami\b|hostname\b|uname\b|uptime\b"
    r")\b",
    re.IGNORECASE,
)
CURL_COMMAND_RE = re.compile(r"(?:^|[;&|]\s*)curl\b", re.IGNORECASE)
CURL_MUTATING_OPTION_RE = re.compile(
    r"(?:^|\s)(?:"
    r"(?:-X(?:\s+|=)?|--request(?:\s+|=))"
    r"(?!(?:GET|HEAD|OPTIONS)(?:\s|$))\S+|"
    r"-d(?:\s|=|[^\s-])|--data(?:-[a-z-]+)?(?:\s|=)|--json(?:\s|=)|"
    r"-F(?:\s|=|[^\s-])|--form(?:-string)?(?:\s|=)|"
    r"-T(?:\s|=|[^\s-])|--upload-file(?:\s|=)"
    r")",
    re.IGNORECASE,
)
# ``-o``/``--output`` writes a file only for curl (and ``-O`` for curl/wget);
# for kubectl, docker, and similar tools it selects an output *format*.
CURL_WRITES_FILE_RE = re.compile(
    r"(?:^|\s)(?:-o|--output|-O|--remote-name)(?:\s|=)",
)
PIPE_TO_SHELL_RE = re.compile(r"\|\s*(?:sh|bash)\b", re.IGNORECASE)
DOWNLOAD_COMMAND_RE = re.compile(r"(?:^|[;&|]\s*)wget\b", re.IGNORECASE)
EXPORT_RE = re.compile(
    r"(?:^|[;&]\s*)export\s+([A-Za-z_][A-Za-z0-9_]*)\s*=", re.MULTILINE
)
EXPORT_STATEMENT_RE = re.compile(
    r"(?:^|[;&]\s*|\n\s*)export\s+[A-Za-z_][A-Za-z0-9_]*\s*="
    r"[^;\n]*(?:;|$)",
    re.MULTILINE,
)


def _task_line(text, task):
    # Parsed mappings carry their real source position.  Name searching maps
    # every repeated task name to its first occurrence, which can suppress or
    # report the wrong task when a preceding comment is inspected.
    return source_line(task, fallback=_line_for(text, task.get("name")))


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


def detect_insecure_permissions(path, parsed_document=None):
    document, text = _load(path, parsed_document=parsed_document)
    details = []
    for task, _ in _iter_tasks(document):
        candidates = []
        if "mode" in task:
            candidates.append(("task", task["mode"], task))
        for module_name, value in task.items():
            short_name = str(module_name).split(".")[-1]
            if (
                short_name in MODE_MODULES
                and isinstance(value, dict)
                and "mode" in value
            ):
                candidates.append((module_name, value["mode"], value))
        for module_name, mode, module_args in candidates:
            parsed = _mode_to_int(mode)
            destination = str(
                module_args.get("path")
                or module_args.get("dest")
                or module_args.get("name")
                or ""
            ).lower()
            persisted_material = " ".join(
                str(module_args.get(key) or "")
                for key in ("path", "dest", "src", "content", "name")
            ).lower()
            sensitive = bool(SENSITIVE_KEY_RE.search(persisted_material))
            private_material = bool(
                "private_key" in persisted_material
                or "id_rsa" in destination
                or "id_ed25519" in destination
                or destination.endswith((".pem", ".key"))
            )
            is_directory = module_args.get("state") == "directory"
            issue = None
            intentional_shared_directory = bool(
                is_directory
                and parsed is not None
                and parsed & stat.S_ISGID
                and module_args.get("group")
                and not parsed & stat.S_IWOTH
            )
            if (
                parsed is not None
                and parsed & stat.S_ISUID
                and not is_directory
            ):
                issue = "Managed permissions unexpectedly set setuid or setgid bits."
            elif (
                parsed is not None
                and parsed & stat.S_ISGID
                and not intentional_shared_directory
            ):
                issue = "Managed permissions unexpectedly set setgid bits."
            elif (
                parsed is not None
                and is_directory
                and parsed & stat.S_IWOTH
                and not parsed & stat.S_ISVTX
            ):
                issue = (
                    "World-writable directory has no sticky bit, allowing users "
                    "to remove or replace each other's entries."
                )
            elif parsed is not None and parsed & stat.S_IWOTH:
                issue = "World-writable permissions grant write access to other users."
            elif (
                parsed is not None
                and private_material
                and parsed & (stat.S_IRGRP | stat.S_IROTH)
            ):
                issue = "Private key material is readable by group or other users."
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
        # H5: Sensitive file written without any explicit mode (umask default ≈ 0644,
        # world-readable). Only flag file-writing modules; query modules are harmless.
        _FILE_WRITE_MODULES = {"template", "copy", "assemble", "ini_file",
                               "lineinfile", "blockinfile", "replace"}
        task_has_mode = "mode" in task
        for module_name, value in task.items():
            short_name = str(module_name).split(".")[-1]
            if short_name not in _FILE_WRITE_MODULES:
                continue
            if not isinstance(value, dict):
                continue
            if "mode" in value or task_has_mode:
                continue
            persisted = " ".join(
                str(value.get(key) or "")
                for key in ("dest", "src", "path", "content", "name")
            ).lower()
            if not (SENSITIVE_KEY_RE.search(persisted)
                    or persisted.endswith((".pem", ".key", ".p12"))
                    or "private_key" in persisted
                    or "id_rsa" in persisted
                    or "id_ed25519" in persisted):
                continue
            details.append(
                {
                    "line": _task_line(text, task),
                    "task_name": task.get("name", "Unnamed task"),
                    "module": module_name,
                    "mode": "(unset)",
                    "issue": (
                        "Sensitive file written without explicit mode; "
                        "defaults to system umask (typically 0644, world-readable)."
                    ),
                }
            )
    return len(details), details


def detect_unsafe_file_writes(path, parsed_document=None):
    document, text = _load(path, parsed_document=parsed_document)
    details = []
    for task, _ in _iter_tasks(document):
        for module_name, value in task.items():
            if not isinstance(value, dict) or value.get("unsafe_writes") is not True:
                continue
            details.append(
                {
                    "line": _task_line(text, task),
                    "task_name": task.get("name", "Unnamed task"),
                    "module": str(module_name),
                    "issue": (
                        "unsafe_writes: true disables atomic file replacement "
                        "and can expose partial or corrupted content."
                    ),
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


def detect_default_credentials(path, known_values=None, parsed_document=None):
    path_parts = {part.lower() for part in Path(path).parts}
    if path_parts & {"examples", "example", "molecule", "tests", "test", "fixtures", "demo", "demos"}:
        return 0, []
    document, text = _load(path, parsed_document=parsed_document)
    details = []
    seen = set()
    for mapping in _walk_mappings(document):
        for key, value in mapping.items():
            if not _is_sensitive_key(key) or not isinstance(
                value, (str, int)
            ):
                continue
            normalized = str(value).strip().lower()
            if "{{" in normalized or "$ansible_vault" in normalized:
                continue
            credential_values = {
                str(item).lower()
                for item in (known_values if known_values is not None else DEFAULT_CREDENTIALS)
            }
            if normalized not in credential_values and normalized != str(key).lower():
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


def _curl_writes_file(command):
    return bool(CURL_COMMAND_RE.search(command) and CURL_WRITES_FILE_RE.search(command))


def _ends_in_mutating_segment(command):
    """True when any later pipeline/list segment is a mutating command (e.g. `| xargs umount`)."""
    return bool(re.search(r"(?:^|[;&|]\s*|xargs\s+(?:-\S+\s+)*)(?:umount|mount|kill|pkill|rm)\b", command))


def _is_read_only_command(command):
    return bool(
        (READ_ONLY_COMMAND_RE.search(command) or _is_read_only_curl(command))
        and not PIPE_TO_SHELL_RE.search(command)
        and not _ends_in_mutating_segment(command)
        and not _curl_writes_file(command)
    )


def _is_read_only_curl(command):
    """Classify curl conservatively as read-only GET/HEAD/OPTIONS only."""
    return bool(
        CURL_COMMAND_RE.search(command)
        and not CURL_MUTATING_OPTION_RE.search(command)
    )


def _is_output_writing_download(command):
    return bool(
        DOWNLOAD_COMMAND_RE.search(command)
        or _curl_writes_file(command)
        or (
            (READ_ONLY_COMMAND_RE.search(command) or CURL_COMMAND_RE.search(command))
            and PIPE_TO_SHELL_RE.search(command)
        )
    )


def _explicit_false(value):
    return value is False or (
        isinstance(value, str) and value.strip().lower() in {"false", "no", "0"}
    )


def _has_idempotency_guard(task, args):
    # creates/removes prevent execution once the desired filesystem state is
    # reached. changed_when/check_mode only affect reporting/execution mode;
    # neither proves that the underlying operation is idempotent.
    return any(args.get(key) not in (None, "", False) for key in ("creates", "removes"))


_NOQA_NON_IDEMPOTENT_RE = re.compile(
    r"#\s*noqa:?\s*(?:ansibleguard/)?non-idempotent-command\b", re.IGNORECASE
)


def _build_noqa_lines(text):
    """Return explicit AnsibleGuard non-idempotency suppressions."""
    noqa_lines = set()
    for i, line in enumerate(text.splitlines(), 1):
        if _NOQA_NON_IDEMPOTENT_RE.search(line):
            noqa_lines.add(i)
    return noqa_lines


def detect_non_idempotent_commands(path, command_pattern=None, parsed_document=None):
    document, text = _load(path, parsed_document=parsed_document)
    noqa_lines = _build_noqa_lines(text)
    details = []
    for task, _ in _iter_tasks(document):
        module, value = _module_value(task, COMMAND_MODULES)
        if not module:
            continue
        command = _command_text(value)
        args = task.get("args") if isinstance(task.get("args"), dict) else {}
        if isinstance(value, dict):
            args = {**args, **value}
        guarded = _has_idempotency_guard(task, args)
        if _is_read_only_command(command):
            continue
        task_line = _task_line(text, task)
        # Only an explicit suppression of this detector applies. Ansible-lint
        # command/no-changed-when annotations make no idempotency claim.
        if task_line in noqa_lines:
            continue
        mutating = bool(
            (command_pattern or MUTATING_COMMAND_RE).search(command)
            or _is_output_writing_download(command)
            or (
                CURL_COMMAND_RE.search(command)
                and CURL_MUTATING_OPTION_RE.search(command)
            )
        )
        if mutating and not guarded:
            details.append(
                {
                    "line": task_line,
                    "task_name": task.get("name", "Unnamed task"),
                    "command": command,
                    "issue": "Mutating command has no effective creates/removes execution guard.",
                }
            )
    return len(details), details


def detect_read_only_command_changes(path, parsed_document=None):
    """Report read-only fetch/query commands that would claim task changes."""
    document, text = _load(path, parsed_document=parsed_document)
    details = []
    for task, _ in _iter_tasks(document):
        module, value = _module_value(task, COMMAND_MODULES)
        if not module:
            continue
        command = _command_text(value)
        if not _is_read_only_command(command) or _explicit_false(task.get("changed_when")):
            continue
        details.append(
            {
                "line": _task_line(text, task),
                "task_name": task.get("name", "Unnamed task"),
                "command": command,
                "issue": (
                    "Read-only command has no changed_when: false and "
                    "may report a change on every run."
                ),
            }
        )
    return len(details), details


@lru_cache(maxsize=32)
def _repository_yaml_documents(root_text):
    documents = []
    for pattern in ("*.yml", "*.yaml"):
        for candidate in Path(root_text).rglob(pattern):
            if any(part in {".git", ".venv", "venv", "ansibleguard-output"} for part in candidate.parts):
                continue
            try:
                documents.append(
                    (candidate.resolve(), yaml.safe_load(candidate.read_text(encoding="utf-8")))
                )
            except (OSError, UnicodeError, yaml.YAMLError):
                continue
    return tuple(documents)


def _static_task_includes(document, source):
    includes = set()

    def walk(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key in {
                    "include_tasks", "import_tasks",
                    "ansible.builtin.include_tasks", "ansible.builtin.import_tasks",
                }:
                    reference = child if isinstance(child, str) else (
                        child.get("file") if isinstance(child, dict) else None
                    )
                    if isinstance(reference, str) and "{{" not in reference and "{%" not in reference:
                        includes.add((source.parent / reference).resolve())
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(document)
    return includes


def _connected_task_documents(source, scan_scope, repository_context=None):
    """Return documents statically connected by include/import task edges."""
    scan_scope = Path(scan_scope).resolve()
    if repository_context is not None:
        documents = {
            path: parsed.document
            for path, parsed in repository_context.parsed_documents.items()
            if parsed.structurally_analyzable
            and (path == scan_scope or scan_scope in path.parents)
        }
    else:
        documents = dict(_repository_yaml_documents(str(scan_scope)))
    graph = {path: set() for path in documents}
    for path, document in documents.items():
        for included in _static_task_includes(document, path):
            if included in documents:
                graph[path].add(included)
                graph[included].add(path)
    connected = set()
    pending = [source]
    while pending:
        current = pending.pop()
        if current in connected:
            continue
        connected.add(current)
        pending.extend(graph.get(current, ()))
    return tuple(
        (path, documents[path])
        for path in sorted(connected)
        if path in documents
    )


def detect_silent_error_suppression(
    path, symbol_index=None, parsed_document=None, repository_context=None
):
    document, text = _load(path, parsed_document=parsed_document)
    details = []
    tasks = [task for task, _ in _iter_tasks(document)]
    rescue_only = {}

    def collect_rescue_paths(value):
        if isinstance(value, dict):
            block = value.get("block")
            rescue = value.get("rescue")
            if isinstance(block, list) and isinstance(rescue, list):
                block_ids = {id(task) for task, _ in _iter_tasks(block)}
                rescue_ids = {id(task) for task, _ in _iter_tasks(rescue)}
                for task_id in block_ids:
                    rescue_only.setdefault(task_id, set()).update(rescue_ids)
            for child in value.values():
                collect_rescue_paths(child)
        elif isinstance(value, list):
            for child in value:
                collect_rescue_paths(child)

    collect_rescue_paths(document)
    for index, task in enumerate(tasks):
        ignores_errors = task.get("ignore_errors") is True
        disables_failure = task.get("failed_when") is False
        if not (ignores_errors or disables_failure):
            continue
        registered = task.get("register")
        def references_result(value, parent_key=None):
            if isinstance(value, dict):
                return any(
                    key not in {"name", "register"}
                    and references_result(child, key)
                    for key, child in value.items()
                )
            if isinstance(value, list):
                return any(references_result(child, parent_key) for child in value)
            if not isinstance(value, str) or not registered:
                return False
            name = re.escape(str(registered))
            return bool(
                re.search(rf"{{{{[^}}]*\b{name}\b", value)
                or (
                    parent_key == "var"
                    and value.strip().split(".", 1)[0].split("[", 1)[0]
                    == str(registered)
                )
                or (
                    parent_key in {"when", "failed_when", "changed_when", "until", "that"}
                    and re.search(rf"(?<![\w.]){name}\b", value)
                )
            )

        unreachable_recovery = rescue_only.get(id(task), set())
        result_is_inspected = any(
            id(later) not in unreachable_recovery and references_result(later)
            for later in tasks[index + 1 :]
        )
        if not result_is_inspected and registered and symbol_index is not None:
            source = Path(path).resolve()
            role_root = _role_root(source)
            scan_scope = role_root or source.parent
            result_is_inspected = any(
                candidate != source and references_result(candidate_document)
                for candidate, candidate_document in _connected_task_documents(
                    source, scan_scope, repository_context=repository_context
                )
            )
        if not result_is_inspected:
            mechanism = (
                "ignore_errors: true"
                if ignores_errors
                else "failed_when: false"
            )
            recovery = (
                f" Registered result '{registered}' is never inspected later."
                if registered
                else " No result is registered for later recovery."
            )
            details.append(
                {
                    "line": _task_line(text, task),
                    "task_name": task.get("name", "Unnamed task"),
                    "mechanism": mechanism,
                    "issue": (
                        f"Task uses {mechanism} without observable recovery "
                        f"handling.{recovery}"
                    ),
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


def detect_redundant_default_values(
    path, parsed_document=None, repository_context=None
):
    document, text = _load(path, parsed_document=parsed_document)
    role_root = _role_root(path)
    if not role_root:
        return 0, []
    defaults = None
    for suffix in ("yml", "yaml"):
        defaults_path = (role_root / "defaults" / f"main.{suffix}").resolve()
        shared = (
            repository_context.parsed_documents.get(defaults_path)
            if repository_context is not None else None
        )
        if repository_context is not None and shared is None:
            continue
        defaults, _ = _load(defaults_path, parsed_document=shared)
        if isinstance(defaults, dict):
            break
    if not isinstance(defaults, dict):
        return 0, []

    assignments = []
    assignment_index = 0
    if isinstance(document, list):
        for entry in document:
            if isinstance(entry, dict) and isinstance(entry.get("vars"), dict):
                assignments.append((entry.get("name", "play vars"), entry["vars"], None, assignment_index))
                assignment_index += 1
    for task, _ in _iter_tasks(document):
        if isinstance(task.get("vars"), dict):
            assignments.append((task.get("name", "task vars"), task["vars"], task, assignment_index))
            assignment_index += 1
        for key in ("set_fact", "ansible.builtin.set_fact"):
            if isinstance(task.get(key), dict):
                fact_values = {
                    name: value
                    for name, value in task[key].items()
                    if name != "cacheable"
                }
                assignments.append((task.get("name", "set_fact"), fact_values, task, assignment_index))
                assignment_index += 1

    details = []
    prior_assignments = {}
    for owner, values, task, index in assignments:
        conditional = bool(task and task.get("when"))
        for key, value in values.items():
            # A repeated default after an earlier runtime assignment can be an
            # intentional state transition. Only flag the first unconditional
            # static-equivalent assignment for a variable.
            prior = prior_assignments.get(str(key), False)
            if (
                key in defaults
                and defaults[key] == value
                and not conditional
                and not prior
            ):
                details.append(
                    {
                        "line": _line_for(text, str(key)),
                        "task_name": owner,
                        "variable": str(key),
                        "issue": f"'{key}' repeats the same value already supplied by role defaults.",
                    }
                )
            prior_assignments[str(key)] = True
    return len(details), details


def detect_shell_environment_exports(path, parsed_document=None):
    document, text = _load(path, parsed_document=parsed_document)
    details = []
    for task, _ in _iter_tasks(document):
        module, value = _module_value(task, COMMAND_MODULES)
        if not module:
            continue
        command = _command_text(value)
        exported = sorted(set(EXPORT_RE.findall(command)))
        remainder = EXPORT_STATEMENT_RE.sub("", command)
        remainder = re.sub(r"^[\s;]+|[\s;]+$", "", remainder)
        if exported and not remainder:
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


def detect_undocumented_complex_tasks(path, parsed_document=None):
    document, text = _load(path, parsed_document=parsed_document)
    thresholds = load_detector_config(path)["thresholds"]
    boolean_threshold = int(thresholds["undocumented_complex_boolean_ops"])
    filter_threshold = int(thresholds["undocumented_complex_jinja_filters"])
    nesting_threshold = int(thresholds["undocumented_complex_nesting_depth"])
    lines = text.splitlines()
    details = []
    for task, depth in _iter_tasks(document):
        condition = task.get("when", "")
        if isinstance(condition, list):
            condition = " and ".join(str(item) for item in condition)
        condition = str(condition)
        boolean_ops = len(re.findall(r"\b(?:and|or)\b", condition, re.IGNORECASE))
        jinja_filters = len(re.findall(r"\|\s*[A-Za-z_]\w*", condition))
        complex_task = (
            boolean_ops >= boolean_threshold
            or jinja_filters >= filter_threshold
            or depth > nesting_threshold
        )
        if not complex_task:
            continue
        line = _task_line(text, task)
        if _has_preceding_comment(lines, line):
            continue
        evidence = []
        if boolean_ops >= boolean_threshold:
            evidence.append(f"{boolean_ops} boolean operators")
        if jinja_filters >= filter_threshold:
            evidence.append(f"{jinja_filters} Jinja filters")
        if depth > nesting_threshold:
            evidence.append(f"nesting depth {depth}")
        details.append({
            "line": line,
            "task_name": task.get("name", "Unnamed task"),
            "issue": "Highly complex task lacks a preceding rationale comment (" + ", ".join(evidence) + ").",
        })
    return len(details), details


def detect_review_checklist_smells(
    path, symbol_index=None, parsed_document=None, repository_context=None,
    enabled_rules=None,
):
    config = load_detector_config(path)
    detectors = {
        "insecure_permissions": ("insecure-permissions", detect_insecure_permissions),
        "unsafe_file_writes": ("unsafe-file-write", detect_unsafe_file_writes),
        "default_credentials": ("default-credentials", lambda value, parsed_document=None: detect_default_credentials(
            value, config["rules"]["default_credentials"], parsed_document=parsed_document
        )),
        "non_idempotent_commands": ("non-idempotent-command", lambda value, parsed_document=None: detect_non_idempotent_commands(
            value, mutating_command_pattern(config, MUTATING_COMMAND_RE), parsed_document=parsed_document
        )),
        "read_only_command_changes": ("read-only-command-change", detect_read_only_command_changes),
        "silent_error_suppressions": ("silent-error-suppression", lambda value, parsed_document=None: detect_silent_error_suppression(
            value, symbol_index=symbol_index, parsed_document=parsed_document,
            repository_context=repository_context,
        )),
        "redundant_default_values": ("redundant-default-value", lambda value, parsed_document=None: detect_redundant_default_values(
            value, parsed_document=parsed_document,
            repository_context=repository_context,
        )),
        "shell_environment_exports": ("shell-environment-export", detect_shell_environment_exports),
        "undocumented_complex_tasks": ("undocumented-complex-task", detect_undocumented_complex_tasks),
    }
    result = {}
    selected = set(enabled_rules) if enabled_rules is not None else None
    for metric, (rule_id, detector) in detectors.items():
        count, details = (
            (0, [])
            if selected is not None and rule_id not in selected
            else detector(path, parsed_document=parsed_document)
        )
        result[metric] = count
        result[f"{metric}_details"] = details
    return result
