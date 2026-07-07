from detect_large_playbook import calculate_metrics_playbook
from detect_large_play import calculate_metrics_play
from detect_large_task import calculate_metrics_task
from high_coupling import high_coupling
from duplicate_code import duplicate_code

# from include_vars import detect_unnecessary_include_vars
from set_fact import set_fact
from overriding_facts import overriding_facts
from unecessary_abs import unecessary_abs

from ansibleguard.detectors.unnamed_play import unnamed_play
from ansibleguard.detectors.is_unnamed import is_unnamed

from unnamed_tasks import unnamed_tasks
from overriden_keys import detect_duplicate_keys_per_task
from itertools import zip_longest
from sem_cohesion import calculate_similarity

from ansibleguard.detectors.duplicate_task_names import repeated_task_names
from incohesive_plays import calculate_similarity as calculate_similarity_plays

# new
from pathlib import Path
from files_extensions import extract_tasks_from_playbook
from filters_for_comparison import get_when_conditions
from credentials_leaking_in_log import detect_credentials_leaking_in_log
from include_vars import detect_unused_include_vars
import pandas as pd
import csv
import json
import yaml


##def read_specific_values():
##  specific_values = {}
# with open(
#   "/Users/narjes/Documents/Research/Contrib_AnsibleSmells/AnsibleCodeSmells-master/CodeSmellsTool/thresholds.csv",
#  "r",
# ) as f:
#   csvreader = csv.reader(f)
#  next(csvreader)
# for row in csvreader:
#    key, value = row[0], int(row[1])
#   specific_values[key] = value
#  return specific_values


def mainn(yaml_file_path):
    try:
        with open(yaml_file_path, "r", encoding="utf-8") as f:
            playbook = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"Could not parse {yaml_file_path} as YAML: {e}")
        return None

    is_task_only_playbook = isinstance(playbook, list) and all(
        isinstance(task, dict) and "hosts" not in task and "tasks" not in task
        for task in playbook
    )

    metrics_playbook = calculate_metrics_playbook(yaml_file_path)
    # print("metrics_playbook:", metrics_playbook)
    metrics_play = None

    if not is_task_only_playbook:
        metrics_play = calculate_metrics_play(yaml_file_path)
        # print("metrics_play:", metrics_play)
    metrics_task, taskss = calculate_metrics_task(yaml_file_path)
    # print("metrics_task:", metrics_task)
    metrics_high_coupling = high_coupling(yaml_file_path)
    duplicated_code = duplicate_code(yaml_file_path)
    unecessary_set_fact = set_fact(yaml_file_path)
    overriding_fact = overriding_facts(yaml_file_path)
    unecessary_abst = unecessary_abs(yaml_file_path)
    similarityPlaybook = calculate_similarity(yaml_file_path)
    extension = extract_tasks_from_playbook(yaml_file_path)
    unnamedPlay, unnamedPlayDetails = unnamed_play(yaml_file_path)
    unnamedTasks, unnamedTasksDetails = unnamed_tasks(yaml_file_path)
    overridenKeys = detect_duplicate_keys_per_task(yaml_file_path)
    duplicate_task_names = repeated_task_names(yaml_file_path)
    missing_bool_filters = get_when_conditions(yaml_file_path)
    similarityPlays = calculate_similarity_plays(yaml_file_path)
    warnings, nbLeaks, credentialsLeakDetails = detect_credentials_leaking_in_log(
        yaml_file_path
    )
    unused_include_vars, WarningUnusedIncludeVars = detect_unused_include_vars(
        yaml_file_path, vars_folder=None
    )

    main_metrics = {
        "playbook_metrics": metrics_playbook,
        "high_coupling_metrics": metrics_high_coupling,
        "similarity": similarityPlaybook,
        "duplicated_code": duplicated_code,
        "unecessary_set_fact": unecessary_set_fact,
        "overriding_facts": overriding_fact,
        "unecessary_abstraction": unecessary_abst,
        "missing_files_extension": extension,
        "unnamed_play": unnamedPlay,
        "unnamed_play_details": unnamedPlayDetails,
        "unnamed_tasks": unnamedTasks,
        "unnamed_tasks_details": unnamedTasksDetails,
        "overriden_keys": overridenKeys,
        "duplicate_task_names": duplicate_task_names,
        "missing_bool_filters": missing_bool_filters,
        "similarityPlays": similarityPlays,
        "credentials_leaking_in_log": nbLeaks,
        "credentials_leaking_in_log_warnings": warnings,
        "credentials_leaking_in_log_details": credentialsLeakDetails,
        "unused_include_vars": unused_include_vars,
        "WarningUnusedIncludeVars": WarningUnusedIncludeVars,
        "plays": [],
    }

    if metrics_play:
        # task_counts = [count_tasks_in_playbook(play) for play in playbook]

        tasks_by_play_id = {}
        for task in metrics_task:
            play_id = task.get("play_id")
            if play_id not in tasks_by_play_id:
                tasks_by_play_id[play_id] = []
            tasks_by_play_id[play_id].append(task)

        # detect_large_play.py substitutes the placeholder string "unknown"
        # for Play_name when a play has no real name (so downstream display
        # code always has something to show). Calling is_unnamed() on that
        # already-substituted placeholder is wrong -- "unknown" is a
        # non-empty string, so is_unnamed("unknown") always returns 0,
        # silently masking every genuinely unnamed play. Confirmed this
        # directly: a real hosts:-only play with no name: reported
        # unnamed_play == 0. Use unnamedPlayDetails instead (built by
        # unnamed_play.py from a fresh, correct check against the raw
        # YAML, unaffected by this placeholder), matched by real line
        # number, which unnamed_play.py's ruamel-based rewrite now provides.
        unnamed_play_lines = {
            d["line"] for d in unnamedPlayDetails if d.get("line") is not None
        }

        for play in metrics_play["Plays"]:
            play_id = play.get("play_id")
            tasks_for_this_play = tasks_by_play_id.get(play_id, [])

            is_unnamed_Play = int(play.get("line") in unnamed_play_lines)

            play_entry = {
                "play_metrics": play,
                "unnamed_play": is_unnamed_Play,
                "task_metrics": tasks_for_this_play,
            }
            main_metrics["plays"].append(play_entry)
        # 🔁 handle top-level tasks without plays
        if -1 in tasks_by_play_id:
            main_metrics["plays"].append(
                {
                    "play_metrics": None,
                    "unnamed_play": None,
                    "task_metrics": tasks_by_play_id[-1],
                }
            )
    else:
        play_entry = {
            "play_metrics": None,
            "unnamed_play": None,
            "task_metrics": metrics_task,
        }
        main_metrics["plays"].append(play_entry)
    # print("main_metrics:", main_metrics)

    return main_metrics


if __name__ == "__main__":
    from config import TEST_PLAYBOOK

    metrics_playbook = mainn(TEST_PLAYBOOK)
    if metrics_playbook:
        print(metrics_playbook)
