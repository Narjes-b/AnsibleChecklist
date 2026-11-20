"""Build developer-facing summaries grouped by playbook and shared role."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import yaml

from ..document import inspect_document
from ..task_traversal import PLAY_TASK_SECTIONS, iter_leaf_tasks


TASK_KEYS = PLAY_TASK_SECTIONS
INCLUDE_KEYS = ("import_tasks", "include_tasks", "include_vars", "import_playbook")


def _clean_reference(value):
    if isinstance(value, str) and "{{" not in value:
        return value
    if isinstance(value, dict):
        candidate = value.get("file") or value.get("name")
        if isinstance(candidate, str) and "{{" not in candidate:
            return candidate
    return None


def _relative(path, root):
    try:
        return Path(path).resolve().relative_to(Path(root).resolve()).as_posix()
    except ValueError:
        return Path(path).as_posix().removeprefix("./")


def _task_count(value):
    return sum(1 for _ in iter_leaf_tasks(value))


def _node_map(node):
    if not isinstance(node, yaml.MappingNode):
        return {}
    return {
        key.value: value
        for key, value in node.value
        if isinstance(key, yaml.ScalarNode)
    }


def _changed_task_nodes(sequence, changed, source_lines=()):
    count = 0
    for task in iter_leaf_tasks(sequence):
        start = task.start_mark.line + 1
        mark = task.end_mark
        # Block node ends can point into the indentation of the next task.
        # Include the final line only when it contains content before the
        # end mark (e.g. a closing flow bracket), not just indentation.
        end = mark.line
        if mark.line < len(source_lines) and source_lines[mark.line][:mark.column].strip():
            end += 1
        end = max(start, end)
        if any(start <= line <= end for line in changed):
            count += 1
    return count


def _changed_tasks(path, document_type, changed):
    if not changed:
        return 0
    try:
        text = Path(path).read_text(encoding="utf-8")
        node = yaml.compose(text)
    except (OSError, yaml.YAMLError):
        return 0
    if document_type == "tasks":
        return _changed_task_nodes(node, changed, text.splitlines())
    count = 0
    if isinstance(node, yaml.SequenceNode):
        for play in node.value:
            mapping = _node_map(play)
            for key in TASK_KEYS:
                count += _changed_task_nodes(mapping.get(key), changed, text.splitlines())
    return count


def _references(value, current, root):
    result = set()
    if isinstance(value, list):
        for item in value:
            result.update(_references(item, current, root))
    elif isinstance(value, dict):
        for key, child in value.items():
            if key in INCLUDE_KEYS:
                reference = _clean_reference(child)
                if reference:
                    candidate = (current.parent / reference).resolve()
                    if candidate.suffix.lower() not in {".yml", ".yaml"}:
                        for suffix in (".yml", ".yaml"):
                            with_suffix = candidate.with_suffix(suffix)
                            if with_suffix.is_file():
                                candidate = with_suffix
                                break
                    if candidate.is_file():
                        result.add(candidate)
            result.update(_references(child, current, root))
    return result


def _role_paths(document, root, playbook_path=None):
    roles = set()
    plays = document if isinstance(document, list) else [document]
    for play in plays:
        if not isinstance(play, dict):
            continue
        for role in play.get("roles", []) or []:
            name = role if isinstance(role, str) else role.get("role") or role.get("name")
            if not isinstance(name, str) or "{{" in name:
                continue
            candidates = []
            if playbook_path is not None:
                candidates.append(Path(playbook_path).parent / "roles" / name)
            candidates.append(Path(root) / "roles" / name)
            for role_root in candidates:
                if role_root.is_dir():
                    roles.add(role_root.resolve())
                    break
    return roles


def discover_playbooks(repo_root):
    """Return playbooks with conservative static dependency information."""
    root = Path(repo_root).resolve()
    playbooks = []
    for path in sorted((*root.rglob("*.yml"), *root.rglob("*.yaml"))):
        if any(part in {".git", ".github", ".venv", "venv", "ansibleguard-output"} for part in path.parts):
            continue
        info = inspect_document(path)
        if info.document_type != "playbook":
            continue
        dependencies = {path.resolve()}
        queue = [path.resolve()]
        roles = _role_paths(info.document, root, path)
        for role_root in roles:
            dependencies.update(
                child.resolve()
                for pattern in ("*.yml", "*.yaml")
                for child in role_root.rglob(pattern)
            )
        while queue:
            current = queue.pop()
            current_info = inspect_document(current)
            for reference in _references(current_info.document, current, root):
                if reference not in dependencies:
                    dependencies.add(reference)
                    queue.append(reference)
        plays = info.document if isinstance(info.document, list) else [info.document]
        playbooks.append(
            {
                "path": _relative(path, root),
                "plays_analyzed": sum(isinstance(play, dict) for play in plays),
                "tasks_analyzed": sum(
                    _task_count(play.get(key))
                    for play in plays if isinstance(play, dict)
                    for key in TASK_KEYS
                ),
                "dependencies": sorted(_relative(item, root) for item in dependencies),
                "roles": sorted(_relative(item, root) for item in roles),
            }
        )
    return playbooks


def build_playbook_summary(repo_root, comparison, changed_files=(), diagnostics=()):
    introduced = comparison.get("introduced", [])
    fixed = comparison.get("fixed", [])
    unchanged = comparison.get("unchanged", [])
    changed_line_map = changed_files if isinstance(changed_files, dict) else {}
    changed_files = set(changed_files)
    result = []
    occurrence_usage = Counter()
    discovered = discover_playbooks(repo_root)
    for playbook in discovered:
        dependencies = set(playbook["dependencies"])
        new = [item for item in introduced if item.get("file") in dependencies]
        removed = [item for item in fixed if item.get("file") in dependencies]
        existing = [
            pair["head"] for pair in unchanged
            if pair.get("head", {}).get("file") in dependencies
        ]
        for item in new:
            occurrence_usage[item["occurrence_id"]] += 1
        errors = sum(item.get("severity") == "error" for item in new)
        warnings = sum(item.get("severity") == "warning" for item in new)
        relevant_diagnostics = [
            item for item in diagnostics if item.get("file") in dependencies
        ]
        affected = bool(dependencies & changed_files or new or removed)
        changed_tasks = 0
        for dependency in dependencies & changed_files:
            path = Path(repo_root) / dependency
            changed_tasks += _changed_tasks(
                path,
                inspect_document(path).document_type,
                changed_line_map.get(dependency, set()),
            )
        status = (
            "partial" if relevant_diagnostics
            else "failed" if errors
            else "warning" if warnings
            else "passed"
        )
        result.append(
            {
                **playbook,
                "status": status,
                "affected": affected,
                "changed_files": sorted(dependencies & changed_files),
                "changed_tasks": changed_tasks,
                "findings": {
                    "introduced": len(new),
                    "introduced_by_severity": dict(sorted(Counter(item.get("severity", "warning") for item in new).items())),
                    "fixed": len(removed),
                    "unchanged": len(existing),
                },
                "introduced_occurrence_ids": [item["occurrence_id"] for item in new],
                "fixed_occurrence_ids": [item["occurrence_id"] for item in removed],
                "diagnostics": relevant_diagnostics,
            }
        )
    for playbook in result:
        playbook["shared_introduced_occurrence_ids"] = [
            item for item in playbook["introduced_occurrence_ids"] if occurrence_usage[item] > 1
        ]
    return result
