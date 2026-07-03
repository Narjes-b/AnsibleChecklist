import re
import yaml
import re

import re


def check_missing_bool_filter(condition_str):
    warnings = []

    # Detect string comparisons to "true"/"false"
    string_bool_pattern = r'\b\w+\s*==\s*"?(true|false)"?'
    if re.search(string_bool_pattern, condition_str, re.IGNORECASE):
        warnings.append(
            "Warning: Comparing boolean to string literal instead of boolean value or filter."
        )

    # Split on logical operators: and, or
    parts = re.split(r"\s+and\s+|\s+or\s+|\(|\)", condition_str)

    for part in parts:
        part = part.strip()
        if not part:
            continue
        # Skip comparisons (e.g., foo == bar)
        if "==" in part or "!=" in part or "<" in part or ">" in part:
            continue
        # If it doesn't contain '| bool', and is not a literal (true/false), it's suspicious
        if "| bool" not in part and not re.match(
            r"^(true|false|not\s+true|not\s+false)$", part, re.IGNORECASE
        ):
            warnings.append(f"Warning: Possible missing '| bool' in: '{part}'")

    return warnings


def get_when_conditions(yaml_file_path):
    with open(yaml_file_path, "r", encoding="utf-8") as f:
        playbook = yaml.safe_load(f)

    when_conditions = []

    def extract_when_from_tasks(tasks):
        for task in tasks:
            if isinstance(task, dict):
                if "when" in task:
                    when = task["when"]
                    if isinstance(when, list):
                        when_conditions.extend(when)
                    else:
                        when_conditions.append(when)
                # Handle blocks recursively
                if "block" in task:
                    extract_when_from_tasks(task["block"])

    if isinstance(playbook, list):
        for entry in playbook:
            if isinstance(entry, dict) and "tasks" in entry:
                extract_when_from_tasks(entry["tasks"])
            else:
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
