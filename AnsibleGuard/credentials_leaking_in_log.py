# To prevent credentials from leaking in logs when running Ansible playbooks, you must ensure that any task dealing with sensitive data uses the no_log: true directive.
# Your anomaly parser should issue a warning whenever a credential-handling task does not use no_log: true, as this omission can lead to password leaks in:


import pandas as pd
import yaml


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
        list: List of warnings for tasks that may leak credentials in logs.
    """
    with open(yaml_file_path, "r", encoding="utf-8") as f:
        playbook = yaml.safe_load(f)

    all_tasks = _collect_all_raw_tasks(playbook)
    warnings = []
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
            yaml_str = yaml.dump(task, default_flow_style=False)
            content = yaml_str.strip().splitlines()
            # print(f"Content of task: {content}")

            # Check if any sensitive keyword appears in the YAML string
            lower_content = yaml_str.lower()

            # Check for 'no_log' in the task dictionary directly
            no_log_set = task.get("no_log", False)

            if not no_log_set and any(key in lower_content for key in sensitive_keys):
                warnings.append(
                    f"Task '{task.get('name', 'Unnamed task')}' handles a sensitive value but does not use no_log: true — secrets may leak in logs."
                )
                nbLeaks += 1
        except yaml.YAMLError as e:
            warnings.append(
                f"Error processing task '{task.get('name', 'Unknown')}': {str(e)}"
            )
        except Exception as e:
            warnings.append(
                f"Unexpected error in task '{task.get('name', 'Unknown')}': {str(e)}"
            )

    return warnings, nbLeaks


# Tester la fonction
# file_path = "/Users/narjes/Documents/Research/Contrib_AnsibleSmells/data/projects/adriagalin/ansible.motd/tasks/main.yml"
if __name__ == "__main__":
    from config import TEST_PLAYBOOK

    warnings, nbLeaks = detect_credentials_leaking_in_log(TEST_PLAYBOOK)
    if warnings:
        df = pd.DataFrame(warnings, columns=["Warning"])
        print(df)
    else:
        print("Pas de métriques disponibles.")

