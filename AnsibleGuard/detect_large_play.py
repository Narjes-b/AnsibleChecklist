import yaml
import pandas as pd
import re


def compter_caracteres_speciaux(chaine):
    return len(re.findall(r"[^\w\s]", chaine))


def _collect_real_tasks(tasks):
    """
    Recursively walk a tasks list the same way detect_large_task.py's
    analyser_tasks does: a 'block:' wrapper is never itself counted as a
    task (it has no module, it never executes) — only its children are.
    This must stay in sync with analyser_tasks/analyser_play so play-level
    and task-level metrics describe the same set of tasks for a given play.
    """
    names = []
    count = 0
    for task in tasks:
        if not isinstance(task, dict):
            continue
        for section in ("block", "rescue", "always"):
            if section in task and isinstance(task[section], list):
                sub_count, sub_names = _collect_real_tasks(task[section])
                count += sub_count
                names.extend(sub_names)
                break
        else:
            count += 1
            if "name" in task:
                names.append(task["name"])
    return count, names


def compter_tasks_dans_play(play):
    tasks = play.get("tasks", [])
    nombre_tasks, tasks_names = _collect_real_tasks(tasks)

    # Top-level 'block' directly under a play (rare, but detect_large_task.py
    # handles this shape too via analyser_play's first branch)
    if "block" in play and isinstance(play["block"], list):
        block_count, block_names = _collect_real_tasks(play["block"])
        nombre_tasks += block_count
        tasks_names += block_names

    return nombre_tasks, tasks_names


def est_un_play(element):
    return "hosts" in element or "tasks" in element


def calculate_metrics_play(yaml_file_path):
    metrics = {}
    plays_metrics = []

    with open(yaml_file_path, "r", encoding="utf-8") as f:
        playbook = yaml.safe_load(f)

    if not playbook or not isinstance(playbook, list):
        print(f"Error : File {yaml_file_path} is not a valid Playbook!.")
        return None

    play_id = 0
    for element in playbook:
        if est_un_play(element):
            nom_play = element.get("name")
            if not nom_play:
                nom_play = "unknown"
            nombre_tasks, tasks_names = compter_tasks_dans_play(element)

            lignes_play = yaml.dump([element]).count("\n")
            avg_task_size = lignes_play / nombre_tasks if nombre_tasks > 0 else 0
            special_chars_count = (
                compter_caracteres_speciaux(nom_play) if nom_play else 0
            )

            plays_metrics.append(
                {
                    "play_id": play_id,
                    "Play_name": nom_play,
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
    from config import TEST_PLAYBOOK

    metrics = calculate_metrics_play(str(TEST_PLAYBOOK))

    if metrics:
        for i, play_metrics in enumerate(metrics["Plays"]):
            df = pd.DataFrame([play_metrics])
            print(f"DataFrame pour le Play {i + 1}:")
            print(df)
    else:
        print("Pas de métriques disponibles.")

