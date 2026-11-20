"""Canonical extraction of Ansible task actions and control keywords."""

from __future__ import annotations

from collections.abc import Mapping


TASK_META_KEYS = frozenset({
    "name", "when", "tags", "register", "vars", "environment", "no_log",
    "loop", "loop_control", "with_items", "with_list", "with_together",
    "with_nested", "with_dict", "with_subelements", "with_sequence",
    "with_first_found", "with_indexed_items", "with_ini", "with_fileglob",
    "with_lines", "with_flattened", "with_random_choice", "with_csvfile",
    "with_pipe", "with_cartesian", "become", "become_user", "become_method",
    "become_flags", "changed_when", "failed_when", "notify", "block",
    "rescue", "always", "delegate_to", "delegate_facts", "ignore_errors",
    "ignore_unreachable", "run_once", "any_errors_fatal", "until", "retries",
    "delay", "async", "poll", "check_mode", "diff", "throttle", "connection",
    "collections", "listen", "module_defaults", "remote_user", "port", "args",
    "action", "local_action", "timeout", "debugger",
})


def task_has_name(task: Mapping | None) -> bool:
    """Presence is independent of any display placeholder such as 'Unknown'."""
    return isinstance(task, Mapping) and isinstance(task.get("name"), str) and bool(task["name"].strip())


def task_action(task: Mapping | None) -> str | None:
    """Return the module/action name without mistaking task keywords for it."""
    if not isinstance(task, Mapping):
        return None
    for action_key in ("action", "local_action"):
        action = task.get(action_key)
        if isinstance(action, str):
            return action.split()[0] if action.split() else None
        if isinstance(action, Mapping):
            module = action.get("module")
            if isinstance(module, str):
                return module
    return next(
        (str(key) for key in task if str(key) not in TASK_META_KEYS),
        None,
    )
