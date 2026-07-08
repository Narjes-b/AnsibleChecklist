import yaml


def _count_unnecessary_blocks(tasks):
    """Recursively count blocks that wrap exactly one task, at any nesting depth."""
    count = 0
    for task in tasks:
        if not isinstance(task, dict):
            continue
        if "block" in task and isinstance(task["block"], list):
            if len(task["block"]) == 1:
                count += 1
            # Recurse regardless of the parent block's own size — a 3-task
            # outer block can still contain a 1-task inner block.
            count += _count_unnecessary_blocks(task["block"])
        # Ansible also allows rescue/always sections shaped like tasks lists.
        for section in ("rescue", "always"):
            if section in task and isinstance(task[section], list):
                count += _count_unnecessary_blocks(task[section])
    return count


def unecessary_abs(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            playbook = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print("Erreur lors de l'analyse du fichier YAML:", e)
        return None
    except FileNotFoundError as e:
        print(f"Fichier {file_path} non trouvé:", e)
        return None

    if not playbook or not isinstance(playbook, list):
        return 0

    unnecessary_abstraction_detected = 0

    for play in playbook:
        if not isinstance(play, dict):
            continue

        # Case 1: Play with 'tasks'
        if "tasks" in play and isinstance(play["tasks"], list):
            unnecessary_abstraction_detected += _count_unnecessary_blocks(play["tasks"])

        # Case 2: Top-level task (as in a role's main.yml or playbook without 'tasks' key)
        elif "block" in play and isinstance(play["block"], list):
            if len(play["block"]) == 1:
                unnecessary_abstraction_detected += 1
            unnecessary_abstraction_detected += _count_unnecessary_blocks(play["block"])

    return unnecessary_abstraction_detected


# Tester la fonction
if __name__ == "__main__":
    from ..config import TEST_PLAYBOOK

    result = unecessary_abs(str(TEST_PLAYBOOK))

    if result is not None:
        print(result)
