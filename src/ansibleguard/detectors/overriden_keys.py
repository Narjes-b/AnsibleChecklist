from collections import defaultdict

from ruamel.yaml import YAML
from ruamel.yaml.nodes import MappingNode, ScalarNode, SequenceNode


def _mapping_label(node, inherited):
    for key_node, value_node in node.value:
        if (
            isinstance(key_node, ScalarNode)
            and key_node.value == "name"
            and isinstance(value_node, ScalarNode)
        ):
            return value_node.value
    return inherited


def _collect_mapping_duplicates(node, inherited_label, report):
    """Inspect each YAML mapping independently.

    A prior line/indentation heuristic used task boundaries and accidentally
    merged mappings in ``pre_tasks``, ``post_tasks``, roles, and loop items.
    Composer nodes retain every duplicate key and its source mark, allowing us
    to test the YAML scope directly instead of guessing it from indentation.
    """
    if isinstance(node, MappingNode):
        label = _mapping_label(node, inherited_label)
        keys = defaultdict(list)
        for key_node, value_node in node.value:
            if isinstance(key_node, ScalarNode):
                keys[key_node.value].append(key_node.start_mark.line + 1)
            _collect_mapping_duplicates(value_node, label, report)
        duplicates = {
            key: sorted(lines) for key, lines in keys.items() if len(lines) > 1
        }
        if duplicates:
            report.append(
                {
                    "task_name": label or "Unknown",
                    "start_line": node.start_mark.line + 1,
                    "duplicates": duplicates,
                }
            )
    elif isinstance(node, SequenceNode):
        for child in node.value:
            _collect_mapping_duplicates(child, inherited_label, report)


def detect_duplicate_keys_per_task(yaml_file_path, parsed_document=None):
    if parsed_document is not None:
        # The shared Ansible-aware loader records duplicate keys without a
        # second YAML composition pass. Preserve the canonical report shape;
        # task labels are unavailable from the safe loader and remain generic.
        if not parsed_document.duplicate_keys:
            return []
        grouped = defaultdict(list)
        for duplicate in parsed_document.duplicate_keys:
            grouped[str(duplicate.get("key", "<unknown>"))].append(
                int(duplicate.get("line", 1))
            )
        return [{
            "task_name": "Unknown",
            "start_line": min(line for lines in grouped.values() for line in lines),
            "duplicates": {key: sorted(lines) for key, lines in grouped.items()},
        }]
    yaml = YAML(typ="base")
    yaml.allow_duplicate_keys = True
    try:
        with open(yaml_file_path, "r", encoding="utf-8") as stream:
            document = yaml.compose(stream)
    except Exception as exc:
        print(f"Could not parse {yaml_file_path} for structural analysis: {exc}")
        return []
    if document is None:
        return []

    report = []
    _collect_mapping_duplicates(document, "Unknown", report)
    return sorted(report, key=lambda item: item["start_line"])


if __name__ == "__main__":
    from ..config import TEST_PLAYBOOK

    print(detect_duplicate_keys_per_task(str(TEST_PLAYBOOK)))
