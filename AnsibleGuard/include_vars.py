### this code will search for unecessary include_vars/ dependencies in an Ansible playbook

import yaml
import os
import re
from config import varsfiles_folder
from write_to_text import write_unused_vars_to_txt


def detect_unused_include_vars(playbook_file, vars_folder=None):
    with open(playbook_file, "r", encoding="utf-8") as f:
        playbook = yaml.safe_load(f)

    if not isinstance(playbook, list):
        print("This does not look like a valid playbook")
        return 0, []

    included_vars_files = {}  # full path → list of vars
    used_vars = set()
    warnings = []
    found_include_vars = False

    def find_include_vars(data):
        nonlocal found_include_vars
        if isinstance(data, dict):
            for key, value in data.items():
                if key == "include_vars":
                    found_include_vars = True
                    # Value can be a filename, or a dict with 'file' key
                    if isinstance(value, str):
                        # Determine if absolute or relative path
                        if os.path.isabs(value):
                            included_vars_files[value] = None
                        else:
                            # If vars_folder given, join; else assume relative to playbook_file
                            base_path = vars_folder or os.path.dirname(playbook_file)
                            full_path = os.path.abspath(os.path.join(base_path, value))
                            included_vars_files[full_path] = None
                    elif isinstance(value, dict) and "file" in value:
                        file_val = value["file"]
                        if os.path.isabs(file_val):
                            included_vars_files[file_val] = None
                        else:
                            base_path = vars_folder or os.path.dirname(playbook_file)
                            full_path = os.path.abspath(
                                os.path.join(base_path, file_val)
                            )
                            included_vars_files[full_path] = None
                    else:
                        warnings.append(
                            f"Warning: include_vars with unsupported format: {value}"
                        )
                elif isinstance(value, (dict, list)):
                    find_include_vars(value)
        elif isinstance(data, list):
            for item in data:
                find_include_vars(item)

    find_include_vars(playbook)

    if not found_include_vars:
        print("No include_vars found, skipping unused vars detection.")
        return 0, []

    # Load included vars files
    for full_path in list(included_vars_files.keys()):
        if os.path.exists(full_path):
            try:
                with open(full_path, "r") as f_vars:
                    vars_data = yaml.safe_load(f_vars) or {}
                    if isinstance(vars_data, dict):
                        included_vars_files[full_path] = list(vars_data.keys())
                    else:
                        warnings.append(
                            f"Warning: Included vars file {full_path} is not a dict"
                        )
            except yaml.YAMLError as e:
                warnings.append(f"YAML error parsing {full_path}: {e}")
        else:
            warnings.append(f"Warning: Included vars file not found: {full_path}")
            included_vars_files[full_path] = []

    # Relaxed regex to detect variable usage inside any string
    # This matches {{ var_name }} with optional spaces and optional filters/pipes
    var_usage_pattern = re.compile(r"{{\s*([a-zA-Z0-9_]+)")

    def find_used_vars(data):
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str):
                    for var_list in included_vars_files.values():
                        for var_name in var_list:
                            # Match Jinja2-style variable usage
                            if re.search(
                                rf"{{{{\s*{re.escape(var_name)}\s*}}}}", value
                            ):
                                used_vars.add(var_name)
                elif isinstance(value, (dict, list)):
                    find_used_vars(value)
        elif isinstance(data, list):
            for item in data:
                find_used_vars(item)

    find_used_vars(playbook)

    # Determine unused vars per file
    unused = {}
    for filename, vars_list in included_vars_files.items():
        unused_vars = set(vars_list) - used_vars
        if unused_vars:
            unused[filename] = list(unused_vars)
    # print(used_vars,unused)

    # Combine declared vars from all included files
    all_declared_vars = set().union(
        *[set(v or []) for v in included_vars_files.values()]
    )

    if warnings:
        return 1, warnings

    # Include_vars exist but no declared vars used
    if included_vars_files and not used_vars:
        return 1, warnings

    # Vars are used, but none of the used vars are from the included files
    if (
        included_vars_files
        and used_vars
        and not used_vars.intersection(all_declared_vars)
    ):
        return 1, warnings

    # Else: included vars used properly
    return 0, warnings


if __name__ == "__main__":
    result, warnings = detect_unused_include_vars(
        playbook_file="/Users/narjes/Documents/Research/Contrib_AnsibleSmells/data/projects/adoptium/infrastructure/ansible/playbooks/nagios/roles/Nagios_Server/tasks/restart_nagios_server.yml",
        vars_folder=varsfiles_folder,
    )
    # print(result,warnings)
    write_unused_vars_to_txt(
        warnings,
        "/Users/narjes/Documents/Research/Contrib_AnsibleSmells/data/Play_Level_Analysis.txt",
    )
