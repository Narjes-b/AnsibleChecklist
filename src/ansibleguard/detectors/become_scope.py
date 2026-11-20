"""Detects plays that apply become: true at play level across many tasks.

Setting become: true at the play level means every task in the play runs
with elevated privileges (typically root). When most tasks are read-only
queries, assertions, or low-risk operations, this unnecessarily broadens the
privilege escalation surface.

The rule flags plays that:
  - Set become: true at the play level (not at individual task level)
  - Contain at least MIN_TASKS_FOR_BROAD_BECOME tasks

This is a style/security issue: privilege should be requested at the narrowest
scope possible. Tasks that genuinely need elevation can set their own become: true.

Detection strategy:
  Parse the top-level YAML list for play entries (have "hosts:").
  For each play with become: true, count leaf tasks.
  Flag if task count >= MIN_TASKS_FOR_BROAD_BECOME.

Limitations:
  Cannot determine at static analysis time which tasks actually need root.
  The threshold is a heuristic — adjust via .ansibleguard.yml thresholds.
"""

from __future__ import annotations

from ansibleguard.detectors.paper_candidates import _iter_tasks, _line_for, _load

MIN_TASKS_FOR_BROAD_BECOME = 5


def _count_leaf_tasks(play):
    """Count leaf tasks in a play (tasks/pre_tasks/post_tasks sections)."""
    count = 0
    for section in ("pre_tasks", "tasks", "post_tasks"):
        task_list = play.get(section)
        if not isinstance(task_list, list):
            continue
        count += sum(1 for _ in _iter_tasks_in_list(task_list))
    return count


def _iter_tasks_in_list(task_list):
    """Yield leaf tasks from a task list (recurse into block/rescue/always)."""
    for task in task_list:
        if not isinstance(task, dict):
            continue
        has_nested = False
        for section in ("block", "rescue", "always"):
            if isinstance(task.get(section), list):
                yield from _iter_tasks_in_list(task[section])
                has_nested = True
        if not has_nested:
            yield task


def detect_become_scope_too_broad(path, parsed_document=None):
    """Detect plays with become: true at play level across many tasks.

    Returns:
        (count, details) where each detail has line, play_name, task_count, issue.
    """
    document, text = _load(path, parsed_document=parsed_document)
    if not isinstance(document, list):
        return 0, []
    details = []
    for entry in document:
        if not isinstance(entry, dict) or "hosts" not in entry:
            continue
        # Only flag become: true set at the PLAY level (not inherited)
        become = entry.get("become")
        if become is not True and str(become).lower() not in ("true", "yes"):
            continue
        task_count = _count_leaf_tasks(entry)
        if task_count < MIN_TASKS_FOR_BROAD_BECOME:
            continue
        play_name = entry.get("name") or entry.get("hosts", "Unnamed play")
        details.append(
            {
                "line": _line_for(text, play_name),
                "play_name": play_name,
                "task_count": task_count,
                "issue": (
                    f"Play '{play_name}' sets become: true at play level for all "
                    f"{task_count} tasks. Move become: true to specific tasks that "
                    "require privilege escalation to limit the attack surface."
                ),
            }
        )
    return len(details), details
