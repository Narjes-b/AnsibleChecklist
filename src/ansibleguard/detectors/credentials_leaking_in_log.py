# To prevent credentials from leaking in logs when running Ansible playbooks, you must ensure that any task dealing with sensitive data uses the no_log: true directive.
# Your anomaly parser should issue a warning whenever a credential-handling task does not use no_log: true, as this omission can lead to password leaks in:


import re
from collections.abc import Mapping
from pathlib import Path
from ruamel.yaml import YAML

from .source_lines import source_line

_ruamel_yaml = YAML(typ="rt")
_ruamel_yaml.allow_duplicate_keys = True

import yaml as _stdlib_yaml


SENSITIVE_KEY_RE = re.compile(
    r"(?:^|[_-])(?:password|passwd|pwd|pass|secret|token|api[_-]?key|"
    r"access[_-]?key|client[_-]?secret|credential|private[_-]?key)"
    r"(?:$|[_-])",
    re.IGNORECASE,
)
NON_SECRET_KEY_RE = re.compile(
    r"(?:expire|expiration|length|lock|policy|algorithm|file|format|path|"
    r"enabled|provider|reset|link|url|uri)$",
    re.IGNORECASE,
)
NON_SECRET_KEYS = {
    "update_password",
    "password_lock",
    "password_expire_min",
    "password_expire_max",
    "password_expire_warn",
}
LOCKED_PASSWORD_VALUES = {"!", "!!", "*", "!*", "LK", "NP"}
LEGACY_SENSITIVE_SUFFIX_RE = re.compile(
    r"(?:(?:db|user|admin|root|mysql|registry|ptv|api|store|key)[a-z0-9_]*)?"
    r"(?:password|passwd|pwd|pass)$",
    re.IGNORECASE,
)
JINJA_VARIABLE_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")
JINJA_EXPRESSION_RE = re.compile(r"{{.*?}}|{%.*?%}", re.DOTALL)
DISPLAY_MODULES = {
    "debug",
    "ansible.builtin.debug",
    "fail",
    "ansible.builtin.fail",
}
TASK_META_KEYS = {
    "name",
    "when",
    "tags",
    "block",
    "rescue",
    "always",
    "register",
    "ignore_errors",
    "no_log",
    "become",
    "delegate_to",
    "run_once",
    "vars",
    "environment",
    "notify",
    "changed_when",
    "failed_when",
    "loop",
    "loop_control",
}


def _is_sensitive_key(key):
    value = str(key)
    # POSIX PWD is the current working directory, not an abbreviation for a
    # password. Keep lowercase/project-specific `pwd` conservative while
    # avoiding false positives for lookup('env', 'PWD').
    if value == "PWD":
        return False
    normalized = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", value)
    normalized = normalized.lower().replace("-", "_")
    return bool(
        normalized not in NON_SECRET_KEYS
        and (
            SENSITIVE_KEY_RE.search(normalized)
            or LEGACY_SENSITIVE_SUFFIX_RE.fullmatch(normalized)
        )
        and not NON_SECRET_KEY_RE.search(normalized)
    )


def _is_non_secret_sentinel(key, value):
    normalized = str(key).lower().replace("-", "_")
    return normalized == "password" and str(value).strip() in LOCKED_PASSWORD_VALUES


def _sensitive_paths(value, prefix=()):
    if isinstance(value, dict):
        for key, child in value.items():
            path = (*prefix, str(key))
            if _is_sensitive_key(key) and not _is_non_secret_sentinel(key, child):
                yield ".".join(path)
            yield from _sensitive_paths(child, path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _sensitive_paths(child, (*prefix, str(index)))


def _sensitive_references(value):
    if not isinstance(value, str):
        return []
    expressions = JINJA_EXPRESSION_RE.findall(value)
    if not expressions:
        return []
    return sorted(
        variable
        for variable in set(JINJA_VARIABLE_RE.findall(" ".join(expressions)))
        if _is_sensitive_key(variable)
    )


def _walk_sensitive_references(value):
    if isinstance(value, dict):
        for child in value.values():
            yield from _walk_sensitive_references(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_sensitive_references(child)
    else:
        yield from _sensitive_references(value)


def _display_sensitive_references(value):
    """Find secrets displayed via debug/fail, including debug's raw var syntax."""
    if not isinstance(value, dict):
        return _sensitive_references(str(value))
    references = set(_walk_sensitive_references(value))
    raw_var = value.get("var")
    if isinstance(raw_var, str):
        references.update(
            token
            for token in JINJA_VARIABLE_RE.findall(raw_var)
            if _is_sensitive_key(token)
        )
    return sorted(references)


def _effective_no_log(value):
    if value is True:
        return "protected"
    if value is False or value is None:
        return "exposed"
    normalized = str(value).strip().lower()
    if "{{" in normalized:
        return "unknown"
    if normalized in {"true", "yes", "on", "1"}:
        return "protected"
    if normalized in {"false", "no", "off", "0", ""}:
        return "exposed"
    return "unknown"


def _line_of(task):
    """Real 1-indexed source line for this task, or None if unavailable.
    Falls back to the first key's tracked line -- see
    detect_large_task.py's _line_of for why."""
    return source_line(task, fallback=None)


def _collect_all_raw_tasks(playbook):
    """
    Recursively collect the raw dict for every real task in the playbook,
    whether it's nested inside a play's 'tasks:' list, inside a
    block/rescue/always wrapper, or sitting as a bare top-level entry
    (a role's tasks/main.yml style file). A 'block:' wrapper itself is
    never counted as a task — only its children are — matching the same
    semantics as detect_large_task.py / files_extensions.py so this
    detector sees the exact same set of tasks the rest of the pipeline does.
    """
    all_tasks = []

    def recurse(tasks, inherited_no_log=None):
        for task in tasks:
            if not isinstance(task, dict):
                continue
            effective_no_log = task.get("no_log", inherited_no_log)
            has_nested = False
            for section in ("block", "rescue", "always"):
                if section in task and isinstance(task[section], list):
                    recurse(task[section], effective_no_log)
                    has_nested = True
            if not has_nested:
                all_tasks.append((task, effective_no_log))

    if isinstance(playbook, list):
        for entry in playbook:
            if not isinstance(entry, dict):
                continue
            found_play_section = False
            for section in ("pre_tasks", "tasks", "post_tasks", "handlers"):
                if isinstance(entry.get(section), list):
                    recurse(entry[section], entry.get("no_log"))
                    found_play_section = True
            if "block" in entry and isinstance(entry["block"], list):
                recurse(entry["block"], entry.get("no_log"))
            elif not found_play_section and "hosts" not in entry:
                # bare top-level task, not a play wrapper
                recurse([entry])

    return all_tasks


_SET_FACT_MODULES = frozenset({"set_fact", "ansible.builtin.set_fact"})


def _registered_sensitive_vars(all_tasks):
    """Return {var_name: source_task_name} for variables that carry credential data
    under a non-sensitive name, covering two patterns:

    1. register + sensitive-module chain: a task with sensitive module args
       registers its result under an innocuous name (e.g. 'result'), then a
       later debug task exposes it.

    2. set_fact name-laundering: a set_fact task assigns a Jinja expression
       containing a sensitive variable to a non-sensitive-named variable
       (e.g. ``my_config: "{{ vault_password }}"``), then a debug task logs it.
    """
    sensitive_register = {}
    for task, _inherited in all_tasks:
        module_items = {
            str(k): v for k, v in task.items() if k not in TASK_META_KEYS
        }
        # Skip display modules themselves — we only want source tasks.
        if DISPLAY_MODULES & set(module_items.keys()):
            continue

        # Pattern 1: register on a task with sensitive module args.
        register_var = task.get("register")
        if isinstance(register_var, str) and register_var.strip():
            if sorted(set(_sensitive_paths(module_items))):
                sensitive_register[register_var.strip()] = task.get("name") or "Unnamed task"

        # Pattern 2: set_fact name-laundering.
        # A set_fact that assigns {{ sensitive_var }} to a non-sensitive-named key.
        for sf_key in _SET_FACT_MODULES:
            if sf_key not in module_items:
                continue
            fact_args = module_items[sf_key]
            if not isinstance(fact_args, dict):
                continue
            task_name = task.get("name") or "Unnamed task"
            for fact_name, fact_value in fact_args.items():
                if _is_sensitive_key(str(fact_name)):
                    continue  # Already covered by the sensitive_paths branch.
                refs = _sensitive_references(str(fact_value)) if isinstance(fact_value, str) else []
                if refs:
                    sensitive_register[str(fact_name)] = task_name
    return sensitive_register


def _display_references_registered_var(task_module_value, sensitive_vars):
    """Return registered var names that are exposed by this debug/fail task value."""
    exposed = []
    if isinstance(task_module_value, dict):
        raw_var = task_module_value.get("var")
        if isinstance(raw_var, str):
            # debug: var: result  or  debug: var: result.stdout
            base = raw_var.strip().split(".")[0].split("[")[0]
            if base in sensitive_vars:
                exposed.append(base)
        # Check msg/other string values for {{ result }} or {{ result.stdout }}
        for child_val in task_module_value.values():
            if isinstance(child_val, str):
                for token in JINJA_VARIABLE_RE.findall(child_val):
                    if token in sensitive_vars:
                        exposed.append(token)
    elif isinstance(task_module_value, str):
        for token in JINJA_VARIABLE_RE.findall(task_module_value):
            if token in sensitive_vars:
                exposed.append(token)
    return sorted(set(exposed))


def _load_role_defaults(yaml_file_path, repository_context=None):
    """Load defaults/main.yml if the YAML file is inside a role."""
    path = Path(yaml_file_path)
    for parent in (path.parent, *path.parent.parents):
        for suffix in ("yml", "yaml"):
            defaults = (parent / "defaults" / f"main.{suffix}").resolve()
            shared = (
                repository_context.parsed_documents.get(defaults)
                if repository_context is not None else None
            )
            if shared is not None:
                loaded = shared.document
                return loaded if isinstance(loaded, dict) else {}
            if repository_context is not None or not defaults.is_file():
                continue
            try:
                loaded = _stdlib_yaml.safe_load(defaults.read_text(encoding="utf-8"))
                return loaded if isinstance(loaded, dict) else {}
            except Exception:
                return {}
        # Stop at likely role/repo root boundaries
        if (parent / "meta").is_dir() or (parent / ".git").is_dir():
            break
    return {}


def _resolve_no_log_jinja(value, defaults):
    """If no_log is a bare {{ var }} template, resolve it from role defaults."""
    if not isinstance(value, str):
        return None
    m = re.fullmatch(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}", value.strip())
    if not m:
        return None
    return defaults.get(m.group(1))


def _module_redacts_sensitive_paths(module_items, sensitive_paths, module_metadata):
    """Return true only when metadata marks every sensitive argument no_log."""
    if not sensitive_paths or not module_metadata:
        return False
    for path in sensitive_paths:
        module_name, _, argument_path = path.partition(".")
        argument = argument_path.split(".", 1)[0]
        metadata = module_metadata.get(module_name) or {}
        doc = metadata.get("doc") if isinstance(metadata, Mapping) else None
        options = (
            metadata.get("options")
            or metadata.get("argument_spec")
            or (doc.get("options") if isinstance(doc, Mapping) else None)
            or {}
        )
        option = options.get(argument) if isinstance(options, Mapping) else None
        if not isinstance(option, Mapping) or option.get("no_log") is not True:
            return False
    return True


def detect_credentials_leaking_in_log(
    yaml_file_path, module_metadata=None, parsed_document=None,
    repository_context=None,
):
    """
    Detects tasks that handle sensitive credentials without using no_log: true.

    Args:
        yaml_file_path (str): Path to the Ansible playbook YAML file.

    Returns:
        (warnings, nbLeaks, details):
          warnings: list[str] -- unchanged in type and wording from before,
                    for full backward compatibility with existing callers
                    (parser_playbook.py, this file's own __main__, and any
                    existing tests that check warning text directly).
          nbLeaks:  int -- unchanged.
          details:  list[dict] -- NEW. {"task_name", "line", "message"}
                    per flagged task, with a real source line number, for
                    callers (findings.py) that need precise location data
                    rather than just a message string.
    """
    if parsed_document is not None:
        playbook = parsed_document.document
    else:
        with open(yaml_file_path, "r", encoding="utf-8") as f:
            try:
                playbook = _ruamel_yaml.load(f)
            except Exception as e:
                # Standalone callers retain the defensive round-trip fallback.
                print(f"Could not parse {yaml_file_path} for credential-leak analysis: {e}")
                return [], 0, []

    all_tasks = _collect_all_raw_tasks(playbook)
    if module_metadata is None:
        # Module metadata is a repository preparation service. Detectors never
        # launch ansible-doc; standalone calls conservatively use no metadata.
        module_metadata = {}
    role_defaults = _load_role_defaults(
        yaml_file_path, repository_context=repository_context
    )

    # Build the register+debug chain index before the main scan loop so that
    # display tasks can be checked against it in a single pass.
    sensitive_register_vars = _registered_sensitive_vars(all_tasks)

    warnings = []
    details = []
    nbLeaks = 0
    for task, inherited_no_log in all_tasks:
        try:
            task_name = task.get("name")
            if not isinstance(task_name, str) or not task_name.strip():
                task_name = "Unnamed task"
            module_items = {
                str(key): value
                for key, value in task.items()
                if key not in TASK_META_KEYS
            }
            sensitive_paths = sorted(set(_sensitive_paths(module_items)))
            sensitive_references = sorted(
                set(_walk_sensitive_references(module_items))
            )
            display_references = []
            for module_name in DISPLAY_MODULES.intersection(module_items):
                display_references.extend(
                    _display_sensitive_references(module_items[module_name])
                )

            # Register+debug chain: debug/fail task exposes a registered var
            # that originated from a task with sensitive module args.
            chain_references = []
            if DISPLAY_MODULES & set(module_items.keys()):
                for module_name in DISPLAY_MODULES.intersection(module_items):
                    chain_references.extend(
                        _display_references_registered_var(
                            module_items[module_name], sensitive_register_vars
                        )
                    )

            plugin_redacted = _module_redacts_sensitive_paths(
                module_items, sensitive_paths, module_metadata
            )

            # B5: Resolve {{ var }} no_log references via role defaults
            effective_no_log_val = inherited_no_log
            if isinstance(effective_no_log_val, str) and "{{" in effective_no_log_val:
                resolved = _resolve_no_log_jinja(effective_no_log_val, role_defaults)
                if resolved is not None:
                    effective_no_log_val = resolved
            protection = _effective_no_log(effective_no_log_val)
            if plugin_redacted and not display_references and not chain_references:
                continue
            if (
                sensitive_paths or sensitive_references or display_references or chain_references
            ) and protection != "protected":
                evidence = []
                if sensitive_paths:
                    evidence.append(
                        "sensitive argument(s): " + ", ".join(sensitive_paths[:4])
                    )
                if display_references:
                    evidence.append(
                        "displayed sensitive variable(s): "
                        + ", ".join(sorted(set(display_references))[:4])
                    )
                elif sensitive_references:
                    evidence.append(
                        "sensitive variable reference(s): "
                        + ", ".join(sensitive_references[:4])
                    )
                if chain_references:
                    sources = ", ".join(
                        f"'{v}' (registered from '{sensitive_register_vars[v]}')"
                        for v in chain_references[:4]
                    )
                    evidence.append(
                        "registered variable(s) from sensitive task exposed via display: "
                        + sources
                    )
                uncertainty = (
                    " The effective no_log value is dynamic and could not be "
                    "proven true."
                    if protection == "unknown"
                    else ""
                )
                message = (
                    f"Task '{task_name}' handles a sensitive "
                    f"value but does not have a proven no_log: true "
                    f"({'; '.join(evidence)}) — secrets may leak in logs."
                    f"{uncertainty}"
                )
                warnings.append(message)
                if display_references:
                    evidence_level = "DIRECT_DISPLAY"
                    confidence = "high"
                elif chain_references:
                    evidence_level = "REGISTERED_RESULT_DISPLAY"
                    confidence = "high"
                else:
                    evidence_level = "SENSITIVE_ARGUMENT_POSSIBLE_LOG"
                    confidence = "medium"
                semantic_status = (
                    "UNCERTAIN" if protection == "unknown" else "EXPOSED"
                )
                if semantic_status == "UNCERTAIN":
                    confidence = "low"
                details.append(
                    {
                        "task_name": task_name,
                        "line": _line_of(task),
                        "message": message,
                        "evidence_level": evidence_level,
                        "semantic_status": semantic_status,
                        "resolution_status": (
                            "DYNAMIC_PROTECTION_UNKNOWN"
                            if protection == "unknown" else "PROVEN_EXPOSED"
                        ),
                        "resolution_scope": "task-static",
                        "uncertainty_sources": (
                            ["dynamic_no_log"]
                            if protection == "unknown" else []
                        ),
                        "resolution_evidence": {
                            "proved": [evidence_level.lower()],
                            "blockers": (
                                ["dynamic_no_log"]
                                if protection == "unknown" else []
                            ),
                        },
                        "confidence": confidence,
                        "confidence_factors": {
                            "positive": [evidence_level.lower()],
                            "negative": (
                                ["dynamic_no_log"]
                                if protection == "unknown" else []
                            ),
                        },
                    }
                )
                nbLeaks += 1
        except Exception as e:
            message = (
                f"Unexpected error in task '{task.get('name', 'Unknown')}': {str(e)}"
            )
            warnings.append(message)
            details.append(
                {
                    "task_name": task.get("name", "Unknown"),
                    "line": _line_of(task),
                    "message": message,
                }
            )

    return warnings, nbLeaks, details


# Tester la fonction
# file_path = "/Users/narjes/Documents/Research/Contrib_AnsibleSmells/data/projects/adriagalin/ansible.motd/tasks/main.yml"
if __name__ == "__main__":
    from ..config import TEST_PLAYBOOK

    warnings, nbLeaks, details = detect_credentials_leaking_in_log(TEST_PLAYBOOK)
    if warnings:
        print("\n".join(warnings))
    else:
        print("Pas de métriques disponibles.")
