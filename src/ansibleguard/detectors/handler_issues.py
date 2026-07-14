"""
Detects handler-related issues in Ansible playbooks:

1. notify referencing a handler that doesn't exist — the notification
   silently fails at runtime, leaving the playbook in an unexpected state.

2. Handler defined but never notified — dead code that suggests an
   incomplete refactoring or a missed notify.

Reference:
  - Ansible handlers documentation:
    https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_handlers.html
  - Ansible best practices: handlers should be notified explicitly;
    an un-notified handler is dead code.

Detection strategy:
  Collect every handler name from 'handlers:' sections across all plays.
  Collect every 'notify:' value (string or list) from tasks.
  Cross-reference:
    - notify value not in handlers → missing handler
    - handler name not in notify values → handler never notified

  Handler names can be a simple string or a list of strings in notify.
  The built-in handler names 'Restart service' etc. are treated as
  valid since they may exist in included files not in the current file.

Complexity: O(n + h) where n = tasks, h = handlers.
False positives: handlers defined in imported files (import_playbook,
  include_tasks) are invisible to single-file analysis.
Limitations: single-file analysis cannot see handlers from included
  task files or imported playbooks.
"""

from ansibleguard.detectors.source_lines import load_with_lines, source_line


def _collect_handlers(playbook):
    """Collect all handler names from every play in the playbook."""
    handlers = {}
    if isinstance(playbook, list):
        for entry in playbook:
            if not isinstance(entry, dict):
                continue
            if "handlers" in entry and isinstance(entry["handlers"], list):
                for handler in entry["handlers"]:
                    if isinstance(handler, dict) and "name" in handler:
                        handlers[handler["name"]] = source_line(handler)
    return handlers


def _collect_notifies(playbook):
    """Collect all notify values from every task in the playbook."""
    notifies = {}

    def recurse(tasks):
        for task in tasks:
            if not isinstance(task, dict):
                continue
            if "notify" in task:
                val = task["notify"]
                if isinstance(val, str):
                    notifies[val] = source_line(task, "notify")
                elif isinstance(val, list):
                    for item in val:
                        if isinstance(item, str):
                            notifies[item] = source_line(task, "notify")
            for section in ("block", "rescue", "always"):
                if section in task and isinstance(task[section], list):
                    recurse(task[section])

    if isinstance(playbook, list):
        for entry in playbook:
            if not isinstance(entry, dict):
                continue
            if "tasks" in entry and isinstance(entry["tasks"], list):
                recurse(entry["tasks"])
            if "handlers" in entry and isinstance(entry["handlers"], list):
                recurse(entry["handlers"])  # handlers can also notify!
    return notifies


def _is_builtin_handler(name):
    """Check if a handler name matches a common 'Restart X' / 'Reload X'
    pattern that likely comes from included roles rather than being
    truly missing. Only match the most common verb prefixes with a
    following word (service name), not bare verbs."""
    common_verbs = (
        "restart ", "reload ", "start ", "stop ", "enable ",
        "disable ", "flush ", "rebuild ",
    )
    lower = name.lower()
    return any(lower.startswith(v) for v in common_verbs)


def detect_handler_issues(yaml_file_path):
    """
    Detect handlers that are never notified AND notifies referencing
    missing handlers.

    Args:
        yaml_file_path: Path to an Ansible playbook YAML file.

    Returns:
        (missing_count, missing_details, unused_count, unused_details) where:
          missing_count:   int — notifies with no matching handler
          missing_details: list[dict] — {"handler_name", "issue"}
          unused_count:    int — handlers never notified
          unused_details:  list[dict] — {"handler_name", "issue"}
    """
    playbook = load_with_lines(yaml_file_path)
    if playbook is None:
        return 0, [], 0, []

    handlers = _collect_handlers(playbook)
    notifies = _collect_notifies(playbook)

    # Missing handlers: notify references not in handlers
    missing_details = []
    for n in sorted(notifies):
        if n not in handlers and not _is_builtin_handler(n):
            missing_details.append({
                "handler_name": n,
                "issue": (
                    f"Notify references handler '{n}' which is not defined "
                    f"in this playbook. The notification will silently fail."
                ),
                "line": notifies[n],
            })

    # Unused handlers: defined but never notified
    unused_details = []
    for h in sorted(handlers):
        if h not in notifies:
            unused_details.append({
                "handler_name": h,
                "issue": (
                    f"Handler '{h}' is defined but never notified. "
                    f"It will never execute."
                ),
                "line": handlers[h],
            })

    return len(missing_details), missing_details, len(unused_details), unused_details


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        mc, md, uc, ud = detect_handler_issues(sys.argv[1])
        print(f"Missing handlers ({mc}):")
        for d in md:
            print(f"  - {d['handler_name']}: {d['issue']}")
        print(f"Unused handlers ({uc}):")
        for d in ud:
            print(f"  - {d['handler_name']}: {d['issue']}")
    else:
        print("Usage: python handler_issues.py <playbook.yml>")
