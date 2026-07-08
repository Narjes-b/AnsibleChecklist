from ansiblemetrics.general.lines_code import LinesCode
from ansiblemetrics.playbook.num_tasks import NumTasks
from ansiblemetrics.playbook.num_plays import NumPlays
from ansiblemetrics.playbook.avg_play_size import AvgPlaySize
from ansiblemetrics.playbook.avg_task_size import AvgTaskSize
from ansiblemetrics.general.lines_comment import LinesComment

from ansibleguard.detectors.large_task import calculate_metrics_task

from ansibleguard.detectors.detect_large_play import calculate_metrics_play
import pandas as pd


def calculate_metrics_playbook(yaml_file_path):
    try:
        tasksmetrics, tasks = calculate_metrics_task(yaml_file_path)
        nb_tasks = 0
        loc_tasks = 0
        for task in tasksmetrics:
            if "task_name" in task:
                nb_tasks += 1
            if "LOC_task" in task:
                loc_tasks += task["LOC_task"]

        plays = calculate_metrics_play(yaml_file_path)
        if not plays:
            plays = {"Plays": []}

        nb_plays = 0
        loc_plays = 0
        nb_global_tasks = 0
        for play in plays["Plays"]:
            if "LOC_play" in play:
                loc_plays += play["LOC_play"]
            if "Play_name" in play:
                nb_plays += 1
            if "num_tasks_in_play" in play:
                nb_global_tasks += play["num_tasks_in_play"]

        with open(yaml_file_path, "r") as f:
            yaml_data = f.read()

        if not yaml_data:
            return None

        metrics = {}
        metrics["LOC_playbook"] = (
            LinesCode(yaml_data).count() + LinesComment(yaml_data).count()
        )
        metrics["num_plays"] = nb_plays
        metrics["avg_play_size"] = loc_plays / nb_plays if nb_plays > 0 else 0
        metrics["num_nested_tasks_playbook"] = nb_tasks
        metrics["avg_nested_task_playbook"] = (
            loc_tasks / nb_tasks if nb_tasks > 0 else 0
        )
        metrics["num_global_tasks_playbook"] = nb_global_tasks

        return metrics
    except FileNotFoundError:
        print(f"File not found: {yaml_file_path}")
    except PermissionError:
        print(f"Refused Permission: {yaml_file_path}")
    except Exception as e:
        print(f"Error while analyzing the file {yaml_file_path}: {str(e)}")


# Tester la fonction

if __name__ == "__main__":
    from ..config import TEST_PLAYBOOK

    metrics = calculate_metrics_playbook(TEST_PLAYBOOK)
    if metrics:
        df = pd.DataFrame([metrics])
        print(df)
    else:
        print("Pas de métriques disponibles.")
