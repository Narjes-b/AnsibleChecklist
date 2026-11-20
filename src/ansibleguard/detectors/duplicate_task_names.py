import yaml
from collections import Counter

from .large_task import calculate_metrics_task


def repeated_task_names(file_path, parsed_document=None):
    # v0.0.4: scope the duplicate check to per-play instead of file-global.
    # The previous global Counter flagged identical names in different plays
    # (e.g. "Install packages" in pre_tasks and tasks), which is intentional
    # and not a defect, causing ~59% of findings to be FPs.
    all_metrics, top_level_tasks = calculate_metrics_task(
        file_path, parsed_document=parsed_document
    )
    if not all_metrics:
        return 0

    # Group task names by play_id
    plays = {}
    for task in all_metrics:
        if not task["has_name"]:
            continue
        name = task.get("task_name", "").strip()
        play_id = task.get("play_id", -1)
        plays.setdefault(play_id, []).append(name)

    repeated_total = 0
    for names in plays.values():
        counts = Counter(names)
        repeated_total += sum(1 for name, count in counts.items() if count > 1)

    return repeated_total


if __name__ == "__main__":
    from ..config import TEST_PLAYBOOK

    result = repeated_task_names(TEST_PLAYBOOK)
    print(result)
