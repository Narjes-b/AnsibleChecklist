import yaml
from collections import Counter

from .large_task import calculate_metrics_task


def repeated_task_names(file_path):
    all_metrics, top_level_tasks = calculate_metrics_task(file_path)
    if not all_metrics:
        print("No tasks found in the file.")
        return 0
    task_names = [
        task.get("task_name", "").strip() for task in all_metrics if "task_name" in task
    ]

    name_counts = Counter(task_names)
    repeated = [name for name, count in name_counts.items() if count > 1]
    return len(repeated)


if __name__ == "__main__":
    from ..config import TEST_PLAYBOOK

    result = repeated_task_names(TEST_PLAYBOOK)
    print(result)
