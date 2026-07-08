from collections import defaultdict
from ruamel.yaml import YAML
from ansibleguard.report.text_writer import write_duplicates_to_txt


def _collect_task_markers(node, markers):
    """
    Recursively walk the parsed structure and record the starting line of
    every dict that represents a play, a task, or a block/rescue/always
    wrapper — anything that can carry its own top-level keys.

    This replaces the old '- name:' text heuristic entirely: instead of
    guessing where a task starts by looking for a literal 'name:' key,
    we use ruamel.yaml's real parse tree, so key order inside a task
    (e.g. 'become:' before 'name:') can no longer break boundary detection.
    """
    if isinstance(node, dict):
        if hasattr(node, "lc"):
            label = node.get("name", "Unknown")
            markers.append((node.lc.line, label))
        for section in ("tasks", "block", "rescue", "always"):
            if section in node and isinstance(node[section], list):
                for child in node[section]:
                    _collect_task_markers(child, markers)
    elif isinstance(node, list):
        for item in node:
            _collect_task_markers(item, markers)


def detect_duplicate_keys_per_task(yaml_file_path):
    with open(yaml_file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    yaml = YAML(typ="rt")
    yaml.allow_duplicate_keys = True  # don't crash — we detect duplicates ourselves
    with open(yaml_file_path, "r", encoding="utf-8") as f:
        try:
            data = yaml.load(f)
        except Exception as e:
            print(f"Could not parse {yaml_file_path} for structural analysis: {e}")
            return []

    if not data:
        return []

    markers = []
    _collect_task_markers(data, markers)
    markers.sort(key=lambda m: m[0])

    duplicates_report = []

    for i, (start_line, task_name) in enumerate(markers):
        end_line = markers[i + 1][0] if i + 1 < len(markers) else len(lines)

        current_keys = defaultdict(list)
        # start_line is 0-indexed from ruamel; lines[] is also 0-indexed,
        # so this range is exactly this task's own text span, up to (but
        # not including) the next marker's starting line.
        for line_no in range(start_line, end_line):
            if line_no >= len(lines):
                break
            raw_line = lines[line_no]
            stripped = raw_line.lstrip()
            if not stripped or stripped.startswith("#"):
                continue
            if ":" not in stripped:
                continue

            indent = len(raw_line) - len(stripped)
            # A '- ' prefixed line is the first key of a mapping — its
            # sibling keys (same dict, no dash) sit 2 columns further right.
            # Normalize so both register at the same structural depth,
            # instead of 2 apart, which would hide a real same-task duplicate.
            if stripped.startswith("- "):
                depth = indent + 2
            else:
                depth = indent

            key = stripped.split(":", 1)[0].lstrip("- ").strip()
            if key:
                current_keys[(depth, key)].append(line_no + 1)  # report as 1-indexed

        # Decide duplication WITHIN each (depth, key) bucket first — a key
        # only counts as duplicated if it repeats at the same structural
        # depth. Only after that check passes do we collapse the surviving
        # entries down to a plain key name for the report, so a task's own
        # 'name:' can never be merged with an unrelated nested module
        # parameter also called 'name' (e.g. apt: {name: nginx}).
        task_duplicates = defaultdict(list)
        for (depth, key), line_numbers in current_keys.items():
            if len(line_numbers) > 1:
                task_duplicates[key].extend(line_numbers)

        task_duplicates = {k: sorted(v) for k, v in task_duplicates.items()}
        if task_duplicates:
            duplicates_report.append(
                {
                    "task_name": task_name or "Unknown",
                    "start_line": start_line + 1,  # report as 1-indexed
                    "duplicates": task_duplicates,
                }
            )

    return duplicates_report


# Usage example:
if __name__ == "__main__":
    from ..config import TEST_PLAYBOOK

    dupes = detect_duplicate_keys_per_task(str(TEST_PLAYBOOK))
    print(dupes)
