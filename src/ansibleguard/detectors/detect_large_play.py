import pandas as pd
import re
import yaml as _pyyaml
from ruamel.yaml import YAML

from .source_lines import source_line
from ..task_traversal import is_play, iter_leaf_tasks, iter_play_leaf_tasks

_ruamel_yaml = YAML(typ="rt")
_ruamel_yaml.allow_duplicate_keys = True


def _to_plain(obj):
    """
    Strip ruamel's CommentedMap/CommentedSeq wrappers down to plain
    dict/list before handing an element to PyYAML's yaml.dump() for the
    LOC_play count. Confirmed directly that using ruamel's own dumper
    instead (which preserves original comments/blank-lines/flow-style
    formatting) silently produces a DIFFERENT line count than PyYAML's
    canonical re-serialization once comments or flow-style lists are
    involved (11 vs 12 lines on a realistic test case) -- exactly the
    kind of silent drift that would shift "Large Play" threshold
    decisions without anyone noticing. This conversion keeps LOC_play
    byte-identical to pre-ruamel behavior, same fix as
    detect_large_task.py's compter_lignes_dans_task().
    """
    if isinstance(obj, dict):
        return {k: _to_plain(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_to_plain(v) for v in obj]
    return obj


def compter_caracteres_speciaux(chaine):
    rendered = re.sub(r"{{.*?}}|{%.*?%}", "", str(chaine))
    allowed = set("-_./:()[]'\"&|,+")
    return sum(
        not character.isalnum()
        and not character.isspace()
        and character not in allowed
        for character in rendered
    )


def _line_of(node):
    """Real 1-indexed source line for this node, or None if unavailable.
    Falls back to the first key's tracked line if the map-level line
    isn't populated -- see detect_large_task.py's _line_of for why."""
    return source_line(node, fallback=None)


def _collect_real_tasks(tasks):
    """Count the same declared leaf population as task-level metrics."""
    names = []
    count = 0
    for task in iter_leaf_tasks(tasks):
        count += 1
        if isinstance(task.get("name"), str) and task["name"].strip():
            names.append(task["name"])
    return count, names


def compter_tasks_dans_play(play):
    return _collect_real_tasks(list(iter_play_leaf_tasks(play)))


def est_un_play(element):
    return is_play(element)


def calculate_metrics_play(yaml_file_path, parsed_document=None):
    metrics = {}
    plays_metrics = []

    if parsed_document is not None:
        playbook = parsed_document.document
    else:
        with open(yaml_file_path, "r", encoding="utf-8") as f:
            try:
                playbook = _ruamel_yaml.load(f)
            except Exception as e:
                print(
                    f"Error : File {yaml_file_path} could not be parsed for line-level analysis: {e}"
                )
                return None

    if not playbook or not isinstance(playbook, list):
        print(f"Error : File {yaml_file_path} is not a valid Playbook!.")
        return None

    play_id = 0
    for element in playbook:
        if not isinstance(element, dict):
            continue
        if est_un_play(element):
            nom_play = element.get("name")
            if not nom_play:
                nom_play = "unknown"
            nombre_tasks, tasks_names = compter_tasks_dans_play(element)

            lignes_play = _pyyaml.dump([_to_plain(element)]).count("\n")

            avg_task_size = lignes_play / nombre_tasks if nombre_tasks > 0 else 0
            special_chars_count = (
                compter_caracteres_speciaux(nom_play) if nom_play else 0
            )

            plays_metrics.append(
                {
                    "play_id": play_id,
                    "Play_name": nom_play,
                    "line": _line_of(element),
                    "LOC_play": lignes_play,
                    "num_tasks_in_play": nombre_tasks,
                    "tasks_names": tasks_names,
                    "avg_task_play": avg_task_size,
                    "special_chars": special_chars_count,
                }
            )
            play_id += 1

    metrics["Plays"] = plays_metrics

    return metrics


# Tester la fonction
if __name__ == "__main__":
    from ..config import TEST_PLAYBOOK

    metrics = calculate_metrics_play(str(TEST_PLAYBOOK))

    if metrics:
        for i, play_metrics in enumerate(metrics["Plays"]):
            df = pd.DataFrame([play_metrics])
            print(f"DataFrame pour le Play {i + 1}:")
            print(df)
    else:
        print("Pas de métriques disponibles.")
