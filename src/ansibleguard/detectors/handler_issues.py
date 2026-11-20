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

from pathlib import Path

from ansibleguard.detectors.source_lines import load_with_lines, source_line

_INCLUDE_KEYS = {"import_tasks", "include_tasks", "include"}


def _include_target(task):
    """Return the static file named by an include/import task, or ``""``.

    ``None`` means the task is an include whose target is not static (Jinja),
    so its contents cannot be known.
    """
    for key, value in task.items():
        if str(key).split(".")[-1] not in _INCLUDE_KEYS:
            continue
        if isinstance(value, dict):
            value = value.get("file")
        if not isinstance(value, str) or "{{" in value or "{%" in value:
            return None
        return value
    return ""


def _resolve(base_dir, relative):
    for candidate in (base_dir / relative, base_dir / "tasks" / relative, base_dir / "handlers" / relative):
        if candidate.is_file():
            return candidate
    return None


def _role_names(play):
    names = []
    for role in play.get("roles") or []:
        name = role.get("role") or role.get("name") if isinstance(role, dict) else role
        names.append(name if isinstance(name, str) else None)
    return names


def _external_sources(playbook, playbook_path):
    """Handler names, listen topics, and notifies visible outside this file.

    Returns ``(handler_names, listen_topics, notifies, handlers_complete,
    notifies_complete)``. Handler sources (handler imports, roles) decide
    whether a handler can be called missing; notify sources (task includes,
    roles) decide whether a handler can be called unused. An unresolved source
    makes the corresponding claim unknowable, so it is not made.
    """
    base_dir = Path(playbook_path).resolve().parent
    names, topics, notifies = set(), set(), set()
    state = {"handlers": True, "notifies": True}
    seen = set()

    def load(path):
        if path in seen:
            return None
        seen.add(path)
        return load_with_lines(path)

    def absorb_handlers(entries, origin_dir):
        for handler in entries or []:
            if not isinstance(handler, dict):
                continue
            target = _include_target(handler)
            if target is None:
                state["handlers"] = False
                continue
            if target:
                path = _resolve(origin_dir, target)
                document = load(path) if path else None
                if path is None:
                    state["handlers"] = False
                elif isinstance(document, list):
                    absorb_handlers(document, path.parent)
                continue
            if isinstance(handler.get("name"), str):
                names.add(handler["name"])
            listen = handler.get("listen")
            topics.update([listen] if isinstance(listen, str) else [x for x in listen or [] if isinstance(x, str)])

    def absorb_tasks(entries, origin_dir):
        for task in entries or []:
            if not isinstance(task, dict):
                continue
            notify = task.get("notify")
            notifies.update([notify] if isinstance(notify, str) else [x for x in notify or [] if isinstance(x, str)])
            for section in ("block", "rescue", "always"):
                if isinstance(task.get(section), list):
                    absorb_tasks(task[section], origin_dir)
            target = _include_target(task)
            if target is None:
                state["notifies"] = False
            elif target:
                path = _resolve(origin_dir, target)
                document = load(path) if path else None
                if path is None:
                    state["notifies"] = False
                elif isinstance(document, list):
                    absorb_tasks(document, path.parent)

    if not isinstance(playbook, list):
        return names, topics, notifies, True, True
    for play in playbook:
        if not isinstance(play, dict):
            continue
        absorb_handlers(
            [h for h in play.get("handlers") or [] if isinstance(h, dict) and _include_target(h) != ""],
            base_dir,
        )
        for section in ("pre_tasks", "tasks", "post_tasks"):
            if isinstance(play.get(section), list):
                for task in play[section]:
                    if isinstance(task, dict) and _include_target(task) != "":
                        absorb_tasks([task], base_dir)
        for role in _role_names(play):
            role_dir = next(
                (d for d in (base_dir / "roles" / str(role), base_dir.parent / "roles" / str(role)) if role and d.is_dir()),
                None,
            )
            if role_dir is None:
                state["handlers"] = state["notifies"] = False
                continue
            for name in ("main.yml", "main.yaml"):
                handlers_path = role_dir / "handlers" / name
                if handlers_path.is_file():
                    document = load(handlers_path)
                    if isinstance(document, list):
                        absorb_handlers(document, handlers_path.parent)
                tasks_path = role_dir / "tasks" / name
                if tasks_path.is_file():
                    document = load(tasks_path)
                    if isinstance(document, list):
                        absorb_tasks(document, tasks_path.parent)
    return names, topics, notifies, state["handlers"], state["notifies"]


def _collect_handlers(playbook):
    """Collect all handler names and their listen topics from every play.

    Returns {handler_name: {"line": int, "listen": [str...]}}
    """
    handlers = {}
    if isinstance(playbook, list):
        for entry in playbook:
            if not isinstance(entry, dict):
                continue
            if "handlers" in entry and isinstance(entry["handlers"], list):
                for handler in entry["handlers"]:
                    if not isinstance(handler, dict) or "name" not in handler:
                        continue
                    module_names = {str(key).split(".")[-1] for key in handler}
                    if module_names & {"import_tasks", "include_tasks"}:
                        continue
                    listen_raw = handler.get("listen")
                    if isinstance(listen_raw, str):
                        listen_topics = [listen_raw]
                    elif isinstance(listen_raw, list):
                        listen_topics = [t for t in listen_raw if isinstance(t, str)]
                    else:
                        listen_topics = []
                    handlers[handler["name"]] = {
                        "line": source_line(handler),
                        "listen": listen_topics,
                    }
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
            for section in ("pre_tasks", "tasks", "post_tasks", "handlers"):
                if isinstance(entry.get(section), list):
                    recurse(entry[section])
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


def detect_handler_issues(yaml_file_path, parsed_document=None):
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
    playbook = (
        parsed_document.document
        if parsed_document is not None
        else load_with_lines(yaml_file_path)
    )
    if playbook is None:
        return 0, [], 0, []

    handlers = _collect_handlers(playbook)
    notifies = _collect_notifies(playbook)
    # Handlers imported into the play, role handlers, and notifies from
    # statically included task files are part of the same play.
    (
        external_names, external_topics, external_notifies,
        handlers_complete, notifies_complete,
    ) = _external_sources(playbook, yaml_file_path)

    # Missing handlers: notify references not in handlers and not a listen topic
    all_listen_topics = set(external_topics)
    for h_info in handlers.values():
        all_listen_topics.update(h_info.get("listen", []))

    missing_details = []
    for n in sorted(notifies):
        if not handlers_complete:
            break
        if n in external_names:
            continue
        if n not in handlers and n not in all_listen_topics and not _is_builtin_handler(n):
            missing_details.append({
                "handler_name": n,
                "issue": (
                    f"Notify references handler '{n}' which is not defined "
                    f"in this playbook. The notification will silently fail."
                ),
                "line": notifies[n],
            })

    # Unused handlers: defined but never notified (by name or listen topic)
    unused_details = []
    for h_name in sorted(handlers):
        h_info = handlers[h_name]
        if not notifies_complete:
            break
        notified_by_name = h_name in notifies or h_name in external_notifies
        notified_by_topic = any(
            topic in notifies or topic in external_notifies for topic in h_info.get("listen", [])
        )
        if not notified_by_name and not notified_by_topic:
            unused_details.append({
                "handler_name": h_name,
                "issue": (
                    f"Handler '{h_name}' is defined but never notified. "
                    f"It will never execute."
                ),
                "line": h_info["line"],
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
