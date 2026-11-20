import re

import yaml


def check_missing_bool_filter(condition_str):
    warnings = []

    # Quoted boolean comparisons are definitely suspicious. Bare variables,
    # comparisons, tests and function calls are valid when their runtime value
    # is Boolean, so this detector does not guess their type.
    string_bool_pattern = r"\b\w+\s*(?:==|!=)\s*(['\"])(?:true|false)\1"
    if re.search(string_bool_pattern, condition_str, re.IGNORECASE):
        warnings.append(
            "Warning: Comparing boolean to string literal instead of boolean value or filter."
        )

    return warnings


def get_when_conditions(yaml_file_path, parsed_document=None):
    if parsed_document is not None:
        playbook = parsed_document.document
    else:
        with open(yaml_file_path, "r", encoding="utf-8") as f:
            playbook = yaml.safe_load(f)

    when_conditions = []

    def extract_when_from_tasks(tasks):
        if not isinstance(tasks, list):
            return
        for task in tasks:
            if isinstance(task, dict):
                if "when" in task:
                    when = task["when"]
                    if isinstance(when, list):
                        when_conditions.extend(when)
                    else:
                        when_conditions.append(when)
                # Handle block/rescue/always recursively
                for section in ("block", "rescue", "always"):
                    if section in task and isinstance(task[section], list):
                        extract_when_from_tasks(task[section])

    if isinstance(playbook, list):
        for entry in playbook:
            found_play_section = False
            if isinstance(entry, dict):
                for section in ("pre_tasks", "tasks", "post_tasks", "handlers"):
                    if isinstance(entry.get(section), list):
                        extract_when_from_tasks(entry[section])
                        found_play_section = True
            if not found_play_section:
                extract_when_from_tasks([entry])  # top-level task
    # print("when_conditions:", when_conditions)
    nbWhens = 0
    for cond in when_conditions:
        result = check_missing_bool_filter(str(cond))
        if result:
            nbWhens += 1
    return nbWhens


# Tester la fonction
file_path = "/Users/narjes/Documents/Research/Contrib_AnsibleSmells/data/projects/adriagalin/ansible.motd/tasks/main.yml"  # Remplacez par le chemin de votre playbook
# whensCond = get_when_conditions(file_path)
# nbWhens=0
# for cond in whensCond:
#   result = check_missing_bool_filter(cond)
#  if result:
#     nbWhens += 1
# print(f"[!] Found potential issues in condition: '{nbWhens}'")
# Print the condition and its warnings
# print(f"[!] In condition '{cond}':")
# for warning in result:
# print("   -", warning)


""" 1. Scan for conditionals using variables or expressions without | bool filter
Parse all when: statements.
For each variable or expression involving a variable, check if there is a | bool or equivalent filter.
If not, flag it as potentially missing a boolean filter.
2. Detect comparisons against strings "true" or "false"
Find when: conditions that compare variables to quoted strings "true"/"false".
Suggest replacing with unquoted booleans or adding | bool.
 """
