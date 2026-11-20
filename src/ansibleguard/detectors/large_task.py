import yaml
import regex as re
from ruamel.yaml import YAML

from .source_lines import source_line
from ..task_traversal import is_play, iter_leaf_tasks, iter_play_leaf_tasks
from ..task_semantics import task_has_name

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
    # Jinja expressions and ordinary technical punctuation are normal in
    # descriptive Ansible task names. Count only genuinely unusual symbols.
    rendered = re.sub(r"{{.*?}}|{%.*?%}", "", str(chaine))
    allowed = set("-_./:()[]'\"&|,+")
    return sum(
        not character.isalnum()
        and not character.isspace()
        and character not in allowed
        for character in rendered
    )


def _line_of(task):
    """
    Real 1-indexed source line for this task, or None if unavailable.
    Tries the map's own start line first; falls back to the first key's
    tracked line (ruamel also records per-key line/col in .lc.data) in
    case the map-level line isn't populated for some construct/ruamel
    version but per-key data still is.
    """
    return source_line(task, fallback=None)


def analyser_tasks(tasks, metrics, play_id):
    for task in iter_leaf_tasks(tasks):
        # Handle standard task (with or without a name)
        has_name = task_has_name(task)
        task_name = task["name"] if has_name else "Unknown"

        lignes = compter_lignes_dans_task(task)
        metrics.append(
            {
                "play_id": play_id,
                "task_name": task_name,
                "has_name": has_name,
                "line": _line_of(task),
                "LOC_task": lignes,
                "task_name_len": len(task_name) if has_name else 0,
                "special_chars": compter_caracteres_speciaux(task_name)
                if has_name
                else 0,
            }
        )


def analyser_play(play, metrics, play_id):
    analyser_tasks(list(iter_play_leaf_tasks(play)), metrics, play_id)


def count_nested_tasks(tasks):
    return sum(1 for _ in iter_leaf_tasks(tasks))


def count_tasks_in_playbook(yaml_data):
    if not isinstance(yaml_data, list):
        return 0
    total_tasks = 0
    global_tasks = []
    for play in yaml_data:
        if is_play(play):
            total_tasks += sum(1 for _ in iter_play_leaf_tasks(play))
        else:
            global_tasks.append(play)
    total_tasks += count_nested_tasks(global_tasks)
    return total_tasks


def calculate_metrics_task(yaml_file_path, parsed_document=None):
    if parsed_document is not None:
        playbook = parsed_document.document
    else:
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
            if is_play(entry):
                analyser_play(entry, all_metrics, play_id)
                play_id += 1
            else:
                top_level_tasks.append(entry)

        if top_level_tasks:
            analyser_tasks(
                top_level_tasks,
                all_metrics,
                play_id=-1,
            )  # -1 means "global" tasks
    # print(top_level_tasks)
    # print(all_metrics)
    return all_metrics, top_level_tasks


if __name__ == "__main__":
    import pandas as pd

    from ..config import TEST_PLAYBOOK

    metrics, top_level_tasks = calculate_metrics_task(TEST_PLAYBOOK)
    if metrics:
        df = pd.DataFrame(metrics)
        print(df)
    else:
        print("Pas de métriques disponibles.")
