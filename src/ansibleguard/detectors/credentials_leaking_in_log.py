# To prevent credentials from leaking in logs when running Ansible playbooks, you must ensure that any task dealing with sensitive data uses the no_log: true directive.
# Your anomaly parser should issue a warning whenever a credential-handling task does not use no_log: true, as this omission can lead to password leaks in:


import re
from ruamel.yaml import YAML

_ruamel_yaml = YAML(typ="rt")
_ruamel_yaml.allow_duplicate_keys = True


SENSITIVE_KEY_RE = re.compile(
    r"(?:^|[_-])(?:password|passwd|pwd|secret|token|api[_-]?key|"
    r"access[_-]?key|client[_-]?secret|credential|private[_-]?key)"
    r"(?:$|[_-])",
    re.IGNORECASE,
)
NON_SECRET_KEY_RE = re.compile(
    r"(?:expire|expiration|length|lock|policy|algorithm|file|path|enabled)$",
    re.IGNORECASE,
)
JINJA_VARIABLE_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")
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
    return bool(SENSITIVE_KEY_RE.search(value) and not NON_SECRET_KEY_RE.search(value))


def _sensitive_paths(value, prefix=()):
    if isinstance(value, dict):
        for key, child in value.items():
            path = (*prefix, str(key))
            if _is_sensitive_key(key):
                yield ".".join(path)
            yield from _sensitive_paths(child, path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _sensitive_paths(child, (*prefix, str(index)))


def _sensitive_references(value):
    if not isinstance(value, str):
        return []
    return sorted(
        variable
        for variable in set(JINJA_VARIABLE_RE.findall(value))
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
    lc = getattr(task, "lc", None)
    if lc is None:
        return None
    if lc.line is not None:
        return lc.line + 1
    data = getattr(lc, "data", None)
    if data:
        try:
            first_key = next(iter(task.keys()))
            return data[first_key][0] + 1
        except Exception:
            pass
    return None


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
            if "tasks" in entry and isinstance(entry["tasks"], list):
                recurse(entry["tasks"], entry.get("no_log"))
            elif "block" in entry and isinstance(entry["block"], list):
                recurse(entry["block"], entry.get("no_log"))
            elif "hosts" not in entry:
                # bare top-level task, not a play wrapper
                recurse([entry])

    return all_tasks


def detect_credentials_leaking_in_log(yaml_file_path):
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
    with open(yaml_file_path, "r", encoding="utf-8") as f:
        try:
            playbook = _ruamel_yaml.load(f)
        except Exception as e:
            # Defense in depth: this function is called directly by at
            # least one existing test, not only through parser_playbook's
            # mainn(), which has its own top-level guard. A vault-tagged
            # or otherwise malformed file must not crash this function on
            # its own merits, the same principle already applied to
            # mainn() itself earlier this session. Confirmed this was a
            # real, live gap: a plain !vault-tagged file raised an
            # uncaught yaml.constructor.ConstructorError here before this
            # guard was added.
            print(f"Could not parse {yaml_file_path} for credential-leak analysis: {e}")
            return [], 0, []

    all_tasks = _collect_all_raw_tasks(playbook)
    warnings = []
    details = []
    nbLeaks = 0
    for task, inherited_no_log in all_tasks:
        try:
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
                    _sensitive_references(str(module_items[module_name]))
                )
            protection = _effective_no_log(inherited_no_log)
            if (
                sensitive_paths or sensitive_references or display_references
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
                uncertainty = (
                    " The effective no_log value is dynamic and could not be "
                    "proven true."
                    if protection == "unknown"
                    else ""
                )
                message = (
                    f"Task '{task.get('name', 'Unnamed task')}' handles a sensitive "
                    f"value but does not have a proven no_log: true "
                    f"({'; '.join(evidence)}) — secrets may leak in logs."
                    f"{uncertainty}"
                )
                warnings.append(message)
                details.append(
                    {
                        "task_name": task.get("name", "Unnamed task"),
                        "line": _line_of(task),
                        "message": message,
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
