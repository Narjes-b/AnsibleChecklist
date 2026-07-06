# To prevent credentials from leaking in logs when running Ansible playbooks, you must ensure that any task dealing with sensitive data uses the no_log: true directive.
# Your anomaly parser should issue a warning whenever a credential-handling task does not use no_log: true, as this omission can lead to password leaks in:


import pandas as pd
import yaml
from ruamel.yaml import YAML

_ruamel_yaml = YAML(typ="rt")
_ruamel_yaml.allow_duplicate_keys = True


def _to_plain(obj):
    """
    Strip ruamel's CommentedMap/CommentedSeq wrappers down to plain
    dict/list before handing a task to PyYAML's yaml.dump() (used here to
    flatten a task into text for the sensitive-keyword search). PyYAML has
    no representer for ruamel's types -- it doesn't raise, it silently
    dumps their internal implementation details instead of the actual
    content (confirmed this failure mode earlier this session on the same
    class of bug in detect_large_task.py/detect_large_play.py). Without
    this conversion, the keyword search would still often "work" by
    accident (the real key/value text is buried in the noise), but
    unreliably so -- not something a security-relevant detector should
    depend on.
    """
    if isinstance(obj, dict):
        return {k: _to_plain(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_to_plain(v) for v in obj]
    return obj


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

    def recurse(tasks):
        for task in tasks:
            if not isinstance(task, dict):
                continue
            has_nested = False
            for section in ("block", "rescue", "always"):
                if section in task and isinstance(task[section], list):
                    recurse(task[section])
                    has_nested = True
            if not has_nested:
                all_tasks.append(task)

    if isinstance(playbook, list):
        for entry in playbook:
            if not isinstance(entry, dict):
                continue
            if "tasks" in entry and isinstance(entry["tasks"], list):
                recurse(entry["tasks"])
            elif "block" in entry and isinstance(entry["block"], list):
                recurse(entry["block"])
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
    sensitive_keys = [
        "password",
        "secret",
        "api_key",
        "token",
        "access_key",
        "client_secret",
    ]

    for task in all_tasks:
        try:
            yaml_str = yaml.dump(_to_plain(task), default_flow_style=False)
            content = yaml_str.strip().splitlines()
            # print(f"Content of task: {content}")

            # Check if any sensitive keyword appears in the YAML string
            lower_content = yaml_str.lower()

            # Check for 'no_log' in the task dictionary directly
            no_log_set = task.get("no_log", False)

            if not no_log_set and any(key in lower_content for key in sensitive_keys):
                message = (
                    f"Task '{task.get('name', 'Unnamed task')}' handles a sensitive "
                    f"value but does not use no_log: true — secrets may leak in logs."
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
        except yaml.YAMLError as e:
            message = f"Error processing task '{task.get('name', 'Unknown')}': {str(e)}"
            warnings.append(message)
            details.append(
                {
                    "task_name": task.get("name", "Unknown"),
                    "line": _line_of(task),
                    "message": message,
                }
            )
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
    from config import TEST_PLAYBOOK

    warnings, nbLeaks, details = detect_credentials_leaking_in_log(TEST_PLAYBOOK)
    if warnings:
        df = pd.DataFrame(warnings, columns=["Warning"])
        print(df)
    else:
        print("Pas de métriques disponibles.")
