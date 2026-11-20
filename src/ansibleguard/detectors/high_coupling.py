import os
import yaml


IMPORT_KEYS = {
    "import_playbook",
    "import_tasks",
    "include_tasks",
    "import_role",
    "include_role",
    "ansible.builtin.import_tasks",
    "ansible.builtin.import_playbook",
    "ansible.builtin.include_tasks",
    "ansible.builtin.import_role",
    "ansible.builtin.include_role",
}


def _count_task_level_imports(tasks):
    count = 0
    for task in tasks:
        if not isinstance(task, dict):
            continue
        if any(key in task for key in IMPORT_KEYS):
            count += 1
        for section in ("block", "rescue", "always"):
            if section in task and isinstance(task[section], list):
                count += _count_task_level_imports(task[section])
    return count


def _count_functional_tasks(tasks):
    count = 0
    for task in tasks:
        if not isinstance(task, dict):
            continue
        nested = False
        for section in ("block", "rescue", "always"):
            if isinstance(task.get(section), list):
                count += _count_functional_tasks(task[section])
                nested = True
        if not nested and not any(key in task for key in IMPORT_KEYS):
            count += 1
    return count


def high_coupling(file_path, parsed_document=None):
    if parsed_document is None and not os.path.exists(file_path):
        print(f"File {file_path} does not exist.")
        return None

    try:
        if parsed_document is not None:
            playbook = parsed_document.document
        else:
            with open(file_path, "r") as f:
                playbook = yaml.safe_load(f)

        if not playbook or not isinstance(playbook, list):
            print(f"File {file_path} is not a valid playbook (not a list).")
            return None

        num_imports = 0
        num_roles = 0
        functional_tasks = 0

        for play in playbook:
            if not isinstance(play, dict):
                # A malformed/blank list item (e.g. a stray "- " or "- null"
                # in hand-edited YAML) shouldn't discard every other real
                # play's coupling data via the outer except below. Confirmed
                # this was a real, live gap: a single null entry caused the
                # whole file to silently return None, losing all coupling
                # data for the rest of the file.
                continue

            if any(key in play for key in IMPORT_KEYS):
                num_imports += 1

            if isinstance(play.get("tasks"), list):
                num_imports += _count_task_level_imports(play["tasks"])
                functional_tasks += _count_functional_tasks(play["tasks"])

            if "roles" in play:
                roles = play["roles"]
                num_roles += len(roles) if isinstance(roles, list) else 1

        # Any import-only document is an orchestration/dispatch entry point,
        # not evidence of problematic coupling. Imports are the modularization
        # mechanism this rule should encourage. Mixed documents retain counts.
        is_dispatcher = num_imports > 0 and functional_tasks == 0
        metrics = {
            "Num_Imports": 0 if is_dispatcher else num_imports,
            "Num_Roles": num_roles,
            "Raw_Num_Imports": num_imports,
            "Import_Only_Dispatcher": is_dispatcher,
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
