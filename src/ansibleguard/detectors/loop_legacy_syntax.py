"""Detects deprecated with_* loop syntax that should be replaced with loop:.

Ansible 2.5 introduced the unified loop: keyword and deprecated all with_*
loop plugins (with_items, with_dict, with_list, with_sequence, with_fileglob,
with_together, with_nested, with_subelements, with_indexed_items, etc.).

Using loop: instead of with_* is more readable, consistent, and forward-
compatible as the with_* plugins may eventually be removed.

Detection strategy:
  Walk all leaf tasks. If any task key starts with "with_" (and is not a
  non-loop key like "with_timeout", which doesn't exist), flag it with the
  recommended migration path.
"""

from ansibleguard.detectors.paper_candidates import _iter_tasks, _line_for, _load

# Keys that start with "with_" but are not loop constructs
_NON_LOOP_WITH_KEYS = frozenset()

# Recommended migration for common with_* patterns
_MIGRATION_HINTS = {
    "with_items": "Use loop: with a list value.",
    "with_list": "Use loop: with a list value.",
    "with_dict": "Use loop: over (my_dict | dict2items).",
    "with_sequence": "Use loop: over (range(n) | list) or the sequence plugin.",
    "with_fileglob": "Use loop: over (query('fileglob', pattern)).",
    "with_together": "Use loop: over (list_a | zip(list_b) | list).",
    "with_nested": "Use loop: over (list_a | product(list_b) | list).",
    "with_subelements": "Use loop: over (list | subelements('key')).",
    "with_indexed_items": "Use loop: over (list | indexed_items).",
    "with_first_found": "Use loop: with the first_found lookup.",
    "with_lines": "Use loop: over (query('lines', command)).",
    "with_inventory_hostnames": "Use loop: over groups['all'] or similar.",
    "with_flattened": "Use loop: over (list | flatten).",
    "with_cartesian": "Use loop: over (list_a | product(list_b) | list).",
    "with_random_choice": "Use loop: over [item] with randomize logic.",
}
_DEFAULT_MIGRATION = "Replace with loop: using the equivalent Jinja2 filter or lookup."


def detect_loop_legacy_syntax(path, parsed_document=None):
    """Detect tasks using deprecated with_* loop syntax.

    Returns:
        (count, details) where each detail has line, task_name, legacy_key, issue.
    """
    document, text = _load(path, parsed_document=parsed_document)
    details = []
    for task, _ in _iter_tasks(document):
        for key in task:
            key_str = str(key)
            if not key_str.startswith("with_"):
                continue
            if key_str in _NON_LOOP_WITH_KEYS:
                continue
            hint = _MIGRATION_HINTS.get(key_str, _DEFAULT_MIGRATION)
            task_name = task.get("name", "Unnamed task")
            details.append(
                {
                    "line": _line_for(text, task_name),
                    "task_name": task_name,
                    "legacy_key": key_str,
                    "issue": (
                        f"Task uses deprecated '{key_str}' loop syntax. "
                        f"{hint} (Introduced in Ansible 2.5.)"
                    ),
                }
            )
            break  # one finding per task
    return len(details), details
