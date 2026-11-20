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
Limitations: does not check tag naming conventions or resolve tags inherited
  from an importing file/role call site.
"""

from ansibleguard.detectors.source_lines import load_with_lines, source_line


def _collect_all_tasks(playbook):
    """Recursively collect all leaf tasks. Returns list of (task_dict, inherited_tags).
    Processes ALL nested sections (block, rescue, always), not just the first."""
    all_tasks = []

    def recurse(tasks, parent_has_tags=False):
        for task in tasks:
            if not isinstance(task, dict):
                continue
            has_nested = False
            for section in ("block", "rescue", "always"):
                if section in task and isinstance(task[section], list):
                    # Children inherit tags from their wrapper
                    wrapper_has_tags = parent_has_tags or "tags" in task
                    recurse(task[section], wrapper_has_tags)
                    has_nested = True
            if not has_nested:
                # Leaf task — check if it has tags or inherits
                all_tasks.append((task, parent_has_tags))

    if isinstance(playbook, list):
        for entry in playbook:
            if not isinstance(entry, dict):
                continue
            found_play_section = False
            play_has_tags = "tags" in entry
            for section in ("pre_tasks", "tasks", "post_tasks", "handlers"):
                if isinstance(entry.get(section), list):
                    recurse(entry[section], play_has_tags)
                    found_play_section = True
            if "block" in entry and isinstance(entry["block"], list):
                recurse(entry["block"], play_has_tags)
            elif not found_play_section and "hosts" not in entry:
                recurse([entry])
    return all_tasks


def detect_missing_tags(yaml_file_path, parsed_document=None):
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
    playbook = (
        parsed_document.document
        if parsed_document is not None
        else load_with_lines(yaml_file_path)
    )
    if playbook is None:
        return 0, []

    all_tasks = _collect_all_tasks(playbook)
    details = []

    for task, parent_has_tags in all_tasks:
        task_name = task.get("name", "Unnamed task")
        has_own_tags = "tags" in task

        if not has_own_tags and not parent_has_tags:
            details.append({
                "task_name": task_name,
                "issue": (
                    "Optional style policy: task has no explicit or inherited tags, "
                    "so it cannot be selected directly with --tags/--skip-tags."
                ),
                "line": source_line(task),
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
