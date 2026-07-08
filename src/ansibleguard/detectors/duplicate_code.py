import yaml
from collections import Counter


def _collect_task_signatures(tasks, task_list):
    """Recursively collect a comparable signature for every real task,
    named or not, including those nested in block/rescue/always.

    The 'name' field is deliberately excluded from the signature — two
    tasks with different names but otherwise identical parameters are
    exactly the copy-paste duplication this detector exists to catch."""
    for task in tasks:
        if not isinstance(task, dict):
            continue

        task_params = task.copy()
        task_params.pop("name", None)  # safe even if the task has no name

        for section in ("block", "rescue", "always"):
            if section in task and isinstance(task[section], list):
                _collect_task_signatures(task[section], task_list)
                task_params.pop(section, None)

        # Only record a signature if something besides 'name' and the
        # recursed-into sections remains — an empty leftover dict (a pure
        # block/rescue/always wrapper with nothing else) isn't itself a
        # comparable task body.
        if task_params:
            task_list.append(str(sorted(task_params.items())))


def duplicate_code(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except (yaml.YAMLError, FileNotFoundError) as e:
        print("Error while analyzing the YAML or the file:", e)
        return None

    task_list = []

    if isinstance(data, list):
        for play_or_task in data:
            if not isinstance(play_or_task, dict):
                continue

            if "tasks" in play_or_task and isinstance(play_or_task["tasks"], list):
                _collect_task_signatures(play_or_task["tasks"], task_list)
            elif "block" in play_or_task and isinstance(play_or_task["block"], list):
                _collect_task_signatures(play_or_task["block"], task_list)
            elif "hosts" not in play_or_task:
                # A bare top-level task (role tasks/main.yml style) — treat
                # this single entry itself as a task to compare.
                _collect_task_signatures([play_or_task], task_list)

    task_counter = Counter(task_list)
    duplicates = {task: count for task, count in task_counter.items() if count > 1}
    return len(duplicates)


# Tester la fonction
if __name__ == "__main__":
    from ..config import TEST_PLAYBOOK

    result = duplicate_code(str(TEST_PLAYBOOK))
    if result is not None:
        print("Code dupliqué détecté" if result > 0 else "Aucun code dupliqué trouvé")
        print(result)

