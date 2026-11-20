import re

import pandas as pd
import yaml


FILE_REFERENCE_MODULES = {
    "import_playbook",
    "import_tasks",
    "include_tasks",
    "include_vars",
}


COLLECTION_PLAYBOOK_RE = re.compile(r"^[A-Za-z0-9_]+\.[A-Za-z0-9_]+\.[A-Za-z0-9_.]+$")


def extract_tasks_from_playbook(yaml_file_path, parsed_document=None):
    """Extracts all tasks from an Ansible playbook (including inside blocks)."""
    if parsed_document is not None:
        playbook = parsed_document.document
    else:
        with open(yaml_file_path, "r", encoding="utf-8") as f:
            playbook = yaml.safe_load(f)

    all_tasks = []

    def recurse_extract(tasks):
        if not isinstance(tasks, list):
            return
        for task in tasks:
            if not isinstance(task, dict):
                continue
            has_nested = False
            for section in ("block", "rescue", "always"):
                if isinstance(task.get(section), list):
                    recurse_extract(task[section])
                    has_nested = True
            if not has_nested:
                all_tasks.append(task)

    if isinstance(playbook, list):
        for play in playbook:
            if isinstance(play, dict):
                if "tasks" in play:
                    recurse_extract(play["tasks"])
                else:
                    recurse_extract([play])  # Could be a list of tasks (not a play)
    total_missing = 0
    for task in all_tasks:
        missing_ext_count = check_missing_extension(task)

        total_missing += missing_ext_count
    return total_missing


def check_missing_extension(task):
    """Count extensionless static include/import references only."""
    for key, value in task.items():
        if str(key).split(".")[-1] not in FILE_REFERENCE_MODULES:
            continue
        reference = value.get("file") if isinstance(value, dict) else value
        if not isinstance(reference, str) or "{{" in reference or "{%" in reference:
            continue
        module = str(key).split(".")[-1]
        reference = reference.strip()
        if not reference:
            return 0
        if " " in reference:  # free-form arguments after the file name
            reference = reference.split()[0]
        if reference.endswith("/"):  # include_vars accepts a directory
            return 0
        if module == "import_playbook" and COLLECTION_PLAYBOOK_RE.match(reference):
            return 0  # namespace.collection.playbook, resolved by the collection loader
        extensions = (".yml", ".yaml", ".json") if module == "include_vars" else (".yml", ".yaml")
        return int(not reference.lower().endswith(extensions))
    return 0


# MAIN SCRIPT
# if __name__ == '__main__':
#     file_path = "/Users/narjes/Documents/Research/Contrib_AnsibleSmells/data/projects/adriagalin/ansible.motd/tasks/main.yml"
#     tasks = extract_tasks_from_playbook(file_path)

#     results = []
#     """ for task in tasks:
#         if isinstance(task, dict):  # Safety check
#             warnings, has_ext = check_missing_extension(task)
#             results.append({
#                 'task_name': task.get('name', 'Unnamed task'),
#                 'warnings': warnings,
#                 'has_extension': has_ext
#             }) """
#     for task in tasks:
#         if isinstance(task, dict):  # Safety check
#             has_ext = check_missing_extension(task)
#             results.append({
#                 'task_name': task.get('name', 'Unnamed task'),
#                 'has_extension': has_ext
#             })
#     # Output as DataFrame
#     if results:
#         df = pd.DataFrame(results)
#         print(df.to_string(index=False))
#     else:
#         print("No tasks found or no metrics to display.")
