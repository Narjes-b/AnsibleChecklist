from .large_task import calculate_metrics_task


def unnamed_tasks(file_path):
    """
    Returns (count, details) where details is a list of
    {"task_name": "Unknown", "line": <real line or None>} dicts, one per
    unnamed task -- mirrors credentials_leaking_in_log.py's (warnings,
    count) pattern so downstream findings/SARIF output can point at the
    real task, not just report a bare count.

    BUG FIXED: this previously iterated `tasks` (== top_level_tasks from
    calculate_metrics_task(), the RAW task dicts with no computed fields
    at all) and checked `task.get("task_name")` -- a key that only exists
    on the *computed* entries in `all_metrics`, never on a raw task dict.
    Confirmed this meant unnamed_tasks() returned 0 for every file,
    always, regardless of real content: a fixture with one genuinely
    unnamed top-level task returned 0, not 1. Fixed by iterating
    `all_metrics` (every task, correctly computed, including ones nested
    inside real plays -- which top_level_tasks never covered anyway) and
    checking the correct field.
    """
    all_metrics, top_level_tasks = calculate_metrics_task(file_path)

    if not all_metrics:
        print("No tasks found in the file.")
        return 0, []

    details = []
    for task in all_metrics:
        if task.get("task_name") == "Unknown":
            details.append({"task_name": "Unknown", "line": task.get("line")})

    return len(details), details


# Tester la fonction
if __name__ == "__main__":
    from ..config import TEST_PLAYBOOK

    result, details = unnamed_tasks(TEST_PLAYBOOK)
    print(result, details)
