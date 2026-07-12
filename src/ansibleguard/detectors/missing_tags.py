"""
Detects tasks that lack a `tags:` attribute.

In Ansible, tags allow selective execution of specific tasks or groups
of tasks. Tasks without tags cannot be targeted with `--tags` or skipped
with `--skip-tags`, reducing operational flexibility in large playbooks.

Ansible best practice: every task should have at least one tag, and
tags should follow a consistent naming convention (e.g., 'install',
'configure', 'restart', 'never' for dangerous tasks).

Reference:
  - Ansible tags documentation:
    https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_tags.html
  - Red Hat best practices: tag all tasks for operational control.

Detection strategy:
  Walk all leaf tasks (recurse into block/rescue/always).
  For each task without a `tags:` key, flag it.
  Tasks that inherit tags from a `block:` wrapper are NOT flagged
  (the block's tags propagate to all children automatically).

Complexity: O(n) where n = number of tasks.
False positives: tasks in simple playbooks that don't need selective
  execution (rare in production environments).
Limitations: does not check tag naming conventions; does not detect
  when a block provides tags to its children.
"""

import yaml


def _collect_all_tasks(playbook):
    """Recursively collect all leaf tasks. Returns list of (task_dict, inherited_tags)."""
    all_tasks = []

    def recurse(tasks, parent_has_tags=False):
        for task in tasks:
            if not isinstance(task, dict):
                continue
            has_nested = False
            for section in ("block", "rescue", "always"):
                if section in task and isinstance(task[section], list):
                    # Children inherit tags from their block/rescue/always wrapper
                    wrapper_has_tags = parent_has_tags or "tags" in task
                    recurse(task[section], wrapper_has_tags)
                    has_nested = True
            if not has_nested:
                # Leaf task — check if it has tags or inherits from parent
                all_tasks.append((task, parent_has_tags))

    if isinstance(playbook, list):
        for entry in playbook:
            if not isinstance(entry, dict):
                continue
            if "tasks" in entry and isinstance(entry["tasks"], list):
                recurse(entry["tasks"])
            elif "block" in entry and isinstance(entry["block"], list):
                recurse(entry["block"])
            elif "hosts" not in entry:
                recurse([entry])
    return all_tasks


def detect_missing_tags(yaml_file_path):
    """
    Detect tasks that lack a tags: attribute.

    Tasks inside a block/rescue/always that has its own tags inherit
    them, so they are not flagged.

    Args:
        yaml_file_path: Path to an Ansible playbook YAML file.

    Returns:
        (count, details) where:
          count:   int — number of tasks without tags
          details: list[dict] — {"task_name", "issue"} per flagged task
    """
    try:
        with open(yaml_file_path, "r", encoding="utf-8") as f:
            playbook = yaml.safe_load(f)
    except (yaml.YAMLError, FileNotFoundError) as e:
        print(f"Could not parse {yaml_file_path}: {e}")
        return 0, []

    all_tasks = _collect_all_tasks(playbook)
    details = []

    for task, parent_has_tags in all_tasks:
        task_name = task.get("name", "Unnamed task")
        has_own_tags = "tags" in task

        if not has_own_tags and not parent_has_tags:
            details.append({
                "task_name": task_name,
                "issue": "Task has no tags — cannot be targeted with --tags or --skip-tags.",
                "line": None,
            })

    return len(details), details


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        count, details = detect_missing_tags(sys.argv[1])
        print(f"Found {count} task(s) without tags:")
        for d in details:
            print(f"  - {d['task_name']}")
    else:
        print("Usage: python missing_tags.py <playbook.yml>")
