import yaml


# v0.0.4: attributes that give a single-task block a legitimate reason to exist.
# Blocks with any of these are NOT unnecessary — they carry block-level semantics
# that cannot be expressed by moving the attribute directly onto the single task.
_BLOCK_JUSTIFYING_KEYS = frozenset({
    "rescue", "always",       # error handling — can only exist at block level
    "when",                   # block-level condition applied to all (even 1) task
    "tags",                   # block-level tag inheritance
    "become", "become_user",  # privilege escalation applied to the group
    "no_log",                 # secrets guard at group level
    "environment",            # environment mapping for all tasks
    "loop", "with_items",     # loop over the block (edge case but valid)
    "vars",                   # block-scoped variables
})


def _count_unnecessary_blocks(tasks):
    """Recursively count blocks that wrap exactly one task and carry no block semantics."""
    count = 0
    for task in tasks:
        if not isinstance(task, dict):
            continue
        if "block" in task and isinstance(task["block"], list):
            # A block is only "unnecessary" if it has exactly one task AND none of
            # the keys that make a block semantically meaningful exist on this task.
            has_justifying_key = bool(_BLOCK_JUSTIFYING_KEYS.intersection(task))
            if len(task["block"]) == 1 and not has_justifying_key:
                count += 1
            # Recurse regardless of the parent block's own size.
            count += _count_unnecessary_blocks(task["block"])
        for section in ("rescue", "always"):
            if section in task and isinstance(task[section], list):
                count += _count_unnecessary_blocks(task[section])
    return count


def unecessary_abs(file_path, parsed_document=None):
    if parsed_document is not None:
        playbook = parsed_document.document
    else:
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
