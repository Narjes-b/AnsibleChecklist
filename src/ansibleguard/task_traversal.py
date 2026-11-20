"""Shared declared-task population for structural metrics and summaries.

Counts source declarations, not runtime executions or expanded imports. Block
wrappers never count as leaf tasks; all block/rescue/always branches are visited.
Aliases at distinct positions count separately; cycles fail explicitly.
"""

from collections.abc import Mapping

from yaml.nodes import MappingNode, ScalarNode, SequenceNode


STRUCTURAL_METRICS_VERSION = "declared-leaf-tasks-v3"
PLAY_TASK_SECTIONS = ("pre_tasks", "tasks", "post_tasks", "handlers")
BLOCK_SECTIONS = ("block", "rescue", "always")


def is_play(value):
    return isinstance(value, Mapping) and (
        "hosts" in value or any(key in value for key in PLAY_TASK_SECTIONS)
    )


def _sequence(value):
    return value if isinstance(value, list) else value.value if isinstance(value, SequenceNode) else None


def _mapping(value):
    if isinstance(value, Mapping):
        return list(value.items())
    if isinstance(value, MappingNode):
        return [(key.value, child) for key, child in value.value if isinstance(key, ScalarNode)]
    return None


def iter_leaf_tasks(tasks):
    """Yield mapping objects/nodes in declaration order without recursion.

    A block section's presence identifies a wrapper, including an empty or
    malformed section. Non-list sections and non-mapping task entries are
    ignored here; YAML/Ansible validity is a separate analysis responsibility.
    """
    stack = [("sequence", tasks)]
    active = set()
    while stack:
        action, value = stack.pop()
        if action == "leaf":
            yield value
            continue
        if action == "leave":
            active.remove(value)
            continue
        values = _sequence(value)
        if values is None:
            continue
        identity = id(value)
        if identity in active:
            raise ValueError("cyclic task container cannot be measured")
        active.add(identity)
        stack.append(("leave", identity))
        # One sequence frame per task preserves depth-first source order and
        # keeps a repeated alias separate from an active ancestor cycle.
        for task in reversed(values):
            pairs = _mapping(task)
            if pairs is None:
                continue
            branches = [child for key, child in pairs if key in BLOCK_SECTIONS]
            if branches:
                stack.extend(("sequence", branch) for branch in reversed(branches))
            else:
                stack.append(("leaf", task))


def iter_play_leaf_tasks(play):
    if not isinstance(play, Mapping):
        return
    for section in (*PLAY_TASK_SECTIONS, *BLOCK_SECTIONS):
        yield from iter_leaf_tasks(play.get(section))
