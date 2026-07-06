import yaml
import pandas as pd
import re
import regex as re
from ruamel.yaml import YAML

# Round-trip loader gives every parsed dict a real .lc.line -- the actual
# line the parser saw it start at -- the same approach overriden_keys.py
# already uses. allow_duplicate_keys mirrors that file too, so a task with
# a genuine duplicate key doesn't hard-crash this detector; the duplicate
# itself is overriden_keys.py's job to report, not this file's.
_ruamel_yaml = YAML(typ="rt")
_ruamel_yaml.allow_duplicate_keys = True


def _to_plain(obj):
    """
    Strip ruamel's CommentedMap/CommentedSeq wrappers down to plain
    dict/list before handing a task to PyYAML's yaml.dump() in
    compter_lignes_dans_task(). PyYAML has no representer for ruamel's
    types -- it doesn't raise on them, it silently serializes their
    internal implementation details (_yaml_line_col, state, etc.) instead
    of the actual YAML content, which would corrupt every LOC_task count.
    Confirmed this failure mode directly before adding this conversion;
    with it, output is byte-for-byte identical to the pre-ruamel behavior.
    """
    if isinstance(obj, dict):
        return {k: _to_plain(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_to_plain(v) for v in obj]
    return obj


def compter_lignes_dans_task(task):
    try:
        yaml_str = yaml.dump(_to_plain(task), default_flow_style=False)
        return len(yaml_str.strip().splitlines())
    except Exception:
        return 0


def compter_caracteres_speciaux(chaine):
    return len(re.findall(r"[^\p{L}\p{N}\s]", chaine))


def _line_of(task):
    """
    Real 1-indexed source line for this task, or None if unavailable.
    Tries the map's own start line first; falls back to the first key's
    tracked line (ruamel also records per-key line/col in .lc.data) in
    case the map-level line isn't populated for some construct/ruamel
    version but per-key data still is.
    """
    lc = getattr(task, "lc", None)
    if lc is None:
        return None
    if lc.line is not None:
        return lc.line + 1
    data = getattr(lc, "data", None)
    if data:
        try:
            first_key = next(iter(task.keys()))
            return data[first_key][0] + 1
        except Exception:
            pass
    return None


def analyser_tasks(tasks, metrics, play_id):
    for task in tasks:
        # Check for 'block' tasks first
        if "block" in task:
            analyser_tasks(task["block"], metrics, play_id)

        # Handle standard task (with or without a name)
        task_name = task.get("name")
        if not isinstance(task_name, str) or not task_name.strip():
            task_name = "Unknown"

        lignes = compter_lignes_dans_task(task)
        metrics.append(
            {
                "play_id": play_id,
                "task_name": task_name,
                "line": _line_of(task),
                "LOC_task": lignes,
                "task_name_len": 0 if task_name == "Unknown" else len(task_name),
                "special_chars": compter_caracteres_speciaux(task_name)
                if task_name != "Unknown"
                else 0,
            }
        )


def analyser_play(play, metrics, play_id):
    if "block" in play:
        analyser_tasks(play["block"], metrics, play_id)

    elif "tasks" in play:
        for task in play["tasks"]:
            if "block" in task:  # Si c'est un block, analyser les tasks à l'intérieur
                analyser_tasks(task["block"], metrics, play_id)
            else:  # Sinon, c'est une tâche standard
                analyser_tasks([task], metrics, play_id)


def count_nested_tasks(tasks):
    count = 0
    for task in tasks:
        # Count this task itself
        count += 1

        # Recursively count nested structures
        if isinstance(task, dict):
            for section in ["block", "rescue", "always"]:
                if section in task and isinstance(task[section], list):
                    count += count_nested_tasks(task[section])
    return count


def count_tasks_in_playbook(yaml_data):
    total_tasks = 0
    for play in yaml_data:
        if (
            isinstance(play, dict)
            and "tasks" in play
            and isinstance(play["tasks"], list)
        ):
            total_tasks += count_nested_tasks(play["tasks"])
        # else:
        #   # Optionally warn about malformed plays
        #  if not isinstance(play, dict) or 'tasks' not in play:
        #     print(f"⚠️ Skipping malformed or taskless play: {play}")
    return total_tasks


def calculate_metrics_task(yaml_file_path):
    with open(yaml_file_path, "r", encoding="utf-8") as f:
        try:
            playbook = _ruamel_yaml.load(f)
        except Exception as e:
            print(f"Could not parse {yaml_file_path} for line-level analysis: {e}")
            return [], []

    all_metrics = []
    top_level_tasks = []

    if isinstance(playbook, list):
        play_id = 0

        for entry in playbook:
            # print(f"Processing entry: {entry}")
            if isinstance(entry, dict) and ("hosts" in entry or "tasks" in entry):
                analyser_play(entry, all_metrics, play_id)
                play_id += 1
            else:
                top_level_tasks.append(entry)

        if top_level_tasks:
            analyser_tasks(
                top_level_tasks, all_metrics, play_id=-1
            )  # -1 means "global" tasks
    # print(top_level_tasks)
    # print(all_metrics)
    return all_metrics, top_level_tasks


if __name__ == "__main__":
    from config import TEST_PLAYBOOK

    metrics, top_level_tasks = calculate_metrics_task(TEST_PLAYBOOK)
    if metrics:
        df = pd.DataFrame(metrics)
        print(df)
    else:
        print("Pas de métriques disponibles.")

