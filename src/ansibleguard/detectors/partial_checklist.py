"""Additional static coverage for partially automated review criteria."""

from __future__ import annotations

from pathlib import Path
import re

from ansibleguard.detectors.paper_candidates import _iter_tasks, _line_for, _load
from ansibleguard.detectors.review_checklist import (
    COMMAND_MODULES,
    _command_text,
    _module_value,
)
from ansibleguard.role_context import (
    automatic_role_variable_files,
    resolve_role_context,
)
from ansibleguard.jinja_semantics import EvaluationState, evaluate_pure_template

JINJA_REFERENCE_RE = re.compile(r"{{.*?}}|{%.*?%}", re.DOTALL)
SHELL_VARIABLE_RE = re.compile(
    r"(?<!\\)\$(?:{([A-Za-z_][A-Za-z0-9_]*)}|([A-Za-z_][A-Za-z0-9_]*))"
)
INLINE_ASSIGNMENT_RE = re.compile(
    r"(?:^|[;&]\s*|\n\s*)([A-Za-z_][A-Za-z0-9_]*)=", re.MULTILINE
)
# Captures loop-scoped variables: `for VAR in ...` and `while ... read VAR`
FOR_LOOP_VAR_RE = re.compile(
    r"\bfor\s+([A-Za-z_][A-Za-z0-9_]*)\s+in\b"
    r"|\bwhile\s+(?:IFS=\S*\s+)?read\s+(?:-[a-zA-Z]\s+)*([A-Za-z_][A-Za-z0-9_]*)\b",
    re.MULTILINE,
)
SINGLE_QUOTED_SHELL_RE = re.compile(r"'(?:\\.|[^'\\])*'")
# A heredoc with a quoted delimiter (<<'EOF' / <<"EOF") is not expanded by the shell.
QUOTED_HEREDOC_RE = re.compile(r"<<-?\s*(['\"])(\w+)\1[^\n]*\n.*?\n\s*\2\b", re.DOTALL)
COMMON_ENVIRONMENT = {
    # Core POSIX / bash
    "HOME",
    "PATH",
    "PWD",
    "OLDPWD",
    "SHELL",
    "USER",
    "LOGNAME",
    "EUID",
    "UID",
    "GID",
    # Locale / internationalisation
    "LANG",
    "LANGUAGE",
    "LC_ALL",
    "LC_CTYPE",
    "LC_MESSAGES",
    # Terminal
    "TERM",
    "COLUMNS",
    "LINES",
    # Temp directories
    "TMP",
    "TMPDIR",
    "TEMP",
    # Host identity
    "HOSTNAME",
    "HOSTTYPE",
    "MACHTYPE",
    "OSTYPE",
    # Session / process
    "SHLVL",
    "PPID",
    "BASH_VERSION",
    "IFS",
    # Privilege escalation
    "SUDO_USER",
    "SUDO_UID",
    "SUDO_GID",
    "SUDO_COMMAND",
    # Package managers and runtimes (commonly set in CI and automation)
    "DEBIAN_FRONTEND",
    "PYTHONPATH",
    "PYTHONDONTWRITEBYTECODE",
    "VIRTUAL_ENV",
    "GOPATH",
    "GOROOT",
    "JAVA_HOME",
    "JAVA_OPTS",
    "MAVEN_HOME",
    "NODE_PATH",
    "NVM_DIR",
    "RBENV_ROOT",
    "GEM_HOME",
    "GEM_PATH",
    # CI / automation
    "CI",
    "BUILD_ID",
    "WORKSPACE",
    "ANSIBLE_FORCE_COLOR",
    "ANSIBLE_NOCOLOR",
    "ANSIBLE_HOST_KEY_CHECKING",
    "http_proxy",
    "https_proxy",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "no_proxy",
    "NO_PROXY",
    "SSL_CERT_FILE",
    "REQUESTS_CA_BUNDLE",
    "CURL_CA_BUNDLE",
    # XDG
    "XDG_CONFIG_HOME",
    "XDG_DATA_HOME",
    "XDG_CACHE_HOME",
    "XDG_RUNTIME_DIR",
}
# PowerShell syntax patterns — $env:, $true/$false/$null, cmdlet verbs
_POWERSHELL_SYNTAX_RE = re.compile(
    r"\$env:|(?:\$(?:true|false|null|PSVersionTable|ProgressPreference|ErrorActionPreference))\b"
    r"|(?:New|Get|Set|Remove|Import|Export|Add|Clear|Copy|Move|Rename|Test|Write|Read|"
    r"Invoke|Start|Stop|Restart|Enable|Disable|Register|Unregister|Format|Select|"
    r"Where|Sort|Group|Measure|Compare|ConvertTo|ConvertFrom|Out|Send|Receive)-\w+",
    re.IGNORECASE,
)
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
PURE_TEMPLATE_RE = re.compile(
    r"^\s*{{\s*([A-Za-z_][\w]*)\s*}}\s*$", re.DOTALL
)
FULL_TEMPLATE_RE = re.compile(r"^\s*(?:{{.*}}|{%.*%})\s*$", re.DOTALL)
_UNRESOLVED = object()


def _visible_variable_values(
    path, document, symbol_index=None, repository_context=None
):
    """Collect statically visible values without attempting Jinja execution."""
    values = {}
    if isinstance(document, list):
        for entry in document:
            if isinstance(entry, dict) and isinstance(entry.get("vars"), dict):
                values.update(entry["vars"])

    candidates = []
    context = resolve_role_context(
        path, symbol_index.root if symbol_index is not None else None
    )
    if context is not None:
        for directory in ("defaults", "vars"):
            candidates.extend(
                automatic_role_variable_files(context.root, directory)
            )
    allowed = None
    if symbol_index is not None:
        root = symbol_index.root.resolve()
        allowed = {(root / relative).resolve() for relative in symbol_index.input_files}
    for candidate in candidates:
        if allowed is not None and candidate.resolve() not in allowed:
            continue
        if repository_context is not None and candidate.resolve() in (
            repository_context.parsed_documents
        ):
            variables = repository_context.document_for(candidate).document
        else:
            variables, _ = _load(candidate)
        if isinstance(variables, dict):
            values.update(variables)
    return values


def _resolved_attribute_value(value, visible_values):
    result = evaluate_pure_template(value, visible_values)
    if result.state == EvaluationState.RUNTIME_UNKNOWN:
        return _UNRESOLVED
    return result.value


def _walk_strings(value, parent_key=None):
    if isinstance(value, dict):
        for key, child in value.items():
            yield from _walk_strings(child, key)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_strings(child, parent_key)
    elif isinstance(value, str):
        yield parent_key, value


def _symbol_graph_documents(path, symbol_index, repository_context=None):
    if symbol_index is None:
        return ()
    root = symbol_index.root.resolve()
    source = Path(path).resolve()
    connected = {
        (root / relative).resolve()
        for relative in symbol_index.connected_task_files(source)
    }
    documents = []
    for candidate in sorted(connected):
        if repository_context is not None and candidate.resolve() in (
            repository_context.parsed_documents
        ):
            document = repository_context.document_for(candidate).document
        else:
            document, _ = _load(candidate)
        if document is not None:
            documents.append((candidate, document))
    return tuple(documents)


def detect_unused_registered_variables(
    path, symbol_index=None, parsed_document=None, repository_context=None
):
    document, text = _load(path, parsed_document=parsed_document)
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

    resolved = Path(path).resolve()
    if symbol_index is not None:
        # A raw same-name occurrence elsewhere in the repository is not a
        # data-flow edge. Only statically connected include/import task files
        # can consume this registered result.
        for candidate, candidate_document in _symbol_graph_documents(
            resolved, symbol_index, repository_context
        ):
            if candidate == resolved:
                continue
            for key, value in _walk_strings(candidate_document):
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


def detect_unscoped_shell_variables(path, parsed_document=None):
    document, text = _load(path, parsed_document=parsed_document)
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
        # Fix 7: Skip PowerShell and non-bash shells — their variable syntax differs from bash
        args_dict = task.get("args") if isinstance(task.get("args"), dict) else {}
        if isinstance(value, dict):
            args_dict = {**args_dict, **value}
        executable = str(args_dict.get("executable", "")).lower()
        if "powershell" in executable or "pwsh" in executable:
            continue
        if executable in ("/bin/csh", "/bin/tcsh", "csh", "tcsh"):
            continue
        # Also detect PowerShell syntax heuristically when no explicit executable
        if _POWERSHELL_SYNTAX_RE.search(command):
            continue
        expandable_command = SINGLE_QUOTED_SHELL_RE.sub("", QUOTED_HEREDOC_RE.sub("", command))
        references = {
            left or right
            for left, right in SHELL_VARIABLE_RE.findall(expandable_command)
        }
        task_environment = (
            task.get("environment") if isinstance(task.get("environment"), dict) else {}
        )
        defined = (
            COMMON_ENVIRONMENT | play_environment | set(map(str, task_environment))
        )
        defined.update(INLINE_ASSIGNMENT_RE.findall(expandable_command))
        # Variables bound by `for VAR in ...` or `while read VAR` are shell-scoped
        # and must not be flagged as unscoped — they are not Ansible env vars.
        defined.update(
            v
            for match in FOR_LOOP_VAR_RE.finditer(expandable_command)
            for v in match.groups()
            if v
        )
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


def detect_invalid_task_attribute_types(
    path, symbol_index=None, parsed_document=None, repository_context=None
):
    document, text = _load(path, parsed_document=parsed_document)
    visible_values = _visible_variable_values(
        path, document, symbol_index, repository_context
    )
    details = []
    for task, _ in _iter_tasks(document):
        for attribute in BOOLEAN_ATTRIBUTES:
            value = _resolved_attribute_value(task.get(attribute), visible_values)
            if value is _UNRESOLVED:
                continue
            if attribute in task and not isinstance(value, bool):
                details.append(
                    {
                        "line": _line_for(text, task.get("name")),
                        "task_name": task.get("name", "Unnamed task"),
                        "attribute": attribute,
                        "issue": f"Task attribute '{attribute}' expects a boolean, got {type(value).__name__}.",
                    }
                )
        for attribute in INTEGER_ATTRIBUTES:
            value = _resolved_attribute_value(task.get(attribute), visible_values)
            if value is _UNRESOLVED:
                continue
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
            raw_val = task.get(attribute)
            if raw_val is None:
                continue
            # v0.0.4: skip Jinja template strings — the variable may resolve to a
            # dict at runtime; static type checking has 0% accuracy here.
            if isinstance(raw_val, str) and ("{{" in raw_val or "{%" in raw_val):
                continue
            # Ansible defines ``environment`` as a list attribute: a mapping or
            # a list of mappings (or templates) is valid. ``vars`` must be a
            # mapping (ansible-core raises a parser error for a list).
            if attribute == "environment" and isinstance(raw_val, list) and all(
                isinstance(item, dict)
                or (isinstance(item, str) and ("{{" in item or "{%" in item))
                for item in raw_val
            ):
                continue
            if not isinstance(raw_val, dict):
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


def detect_invalid_numeric_values(path, parsed_document=None):
    document, text = _load(path, parsed_document=parsed_document)
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


def detect_partial_checklist_smells(
    path, enabled_rules=None, symbol_index=None, parsed_document=None,
    repository_context=None,
):
    detectors = {
        "unused_registered_variables": (
            "unused-registered-variable", detect_unused_registered_variables
        ),
        "unscoped_shell_variables": (
            "unscoped-shell-variable", detect_unscoped_shell_variables
        ),
        "invalid_task_attribute_types": (
            "invalid-task-attribute-type", detect_invalid_task_attribute_types
        ),
        "invalid_numeric_values": (
            "invalid-numeric-value", detect_invalid_numeric_values
        ),
    }
    result = {}
    enabled_rules = set(enabled_rules) if enabled_rules is not None else None
    for metric, (rule_id, detector) in detectors.items():
        if enabled_rules is not None and rule_id not in enabled_rules:
            count, details = 0, []
        else:
            graph_aware = {
                "unused-registered-variable",
                "invalid-task-attribute-type",
            }
            count, details = (
                detector(
                    path, symbol_index=symbol_index,
                    parsed_document=parsed_document,
                    repository_context=repository_context,
                )
                if rule_id in graph_aware else detector(path, parsed_document=parsed_document)
            )
        result[metric] = count
        result[f"{metric}_details"] = details
    return result
