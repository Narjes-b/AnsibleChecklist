import os
import pandas as pd
import yaml


def _count_task_level_imports(tasks):
    count = 0
    for task in tasks:
        if not isinstance(task, dict):
            continue
        if "import_tasks" in task or "include_tasks" in task:
            count += 1
        for section in ("block", "rescue", "always"):
            if section in task and isinstance(task[section], list):
                count += _count_task_level_imports(task[section])
    return count


def high_coupling(file_path):
    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist.")
        return None

    try:
        with open(file_path, "r") as f:
            playbook = yaml.safe_load(f)

        if not playbook or not isinstance(playbook, list):
            print(f"File {file_path} is not a valid playbook (not a list).")
            return None

        num_imports = 0
        num_roles = 0

        for play in playbook:
            if "import_playbook" in play:
                num_imports += 1

            if "import_tasks" in play or "include_tasks" in play:
                num_imports += 1

            if isinstance(play.get("tasks"), list):
                num_imports += _count_task_level_imports(play["tasks"])

            if "roles" in play:
                roles = play["roles"]
                num_roles += len(roles) if isinstance(roles, list) else 1

        metrics = {
            "Num_Imports": num_imports,
            "Num_Roles": num_roles,
        }

        return metrics

    except Exception as e:
        print(f"Error while analyzing file : {e}")
        return None


# Tester la fonction
""" file_path = "C:/Users/PC/Desktop/mitacs/Projet/ansible/playbooks/parser/expl.yaml"  
metrics = high_coupling(file_path)

if __name__ == '__main__':
    if metrics:
        df = pd.DataFrame([metrics])
        print(df)
    else:
        print('Pas de métriques disponibles.') """

