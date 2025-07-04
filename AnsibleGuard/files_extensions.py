import re
import pandas as pd
import yaml

def extract_tasks_from_playbook(yaml_file_path):
    
    """Extracts all tasks from an Ansible playbook (including inside blocks)."""
    with open(yaml_file_path, 'r', encoding='utf-8') as f:
        playbook = yaml.safe_load(f)

    all_tasks = []

    def recurse_extract(tasks):
        for task in tasks:
            if isinstance(task, dict):
                if 'block' in task:
                    recurse_extract(task['block'])
                else:
                    all_tasks.append(task)

    if isinstance(playbook, list):
        for play in playbook:
            if isinstance(play, dict):
                if 'tasks' in play:
                    recurse_extract(play['tasks'])
                else:
                    recurse_extract([play])  # Could be a list of tasks (not a play)
    total_missing = 0
    for task in all_tasks:  
        missing_ext_count = check_missing_extension(task)
        
        total_missing += missing_ext_count
    return total_missing




def check_missing_extension(task):
    file_attrs = ['src', 'file', 'cmd', 'path']
    warnings = []
    missing_ext_count = 0

    # Check top-level attributes
    for attr in file_attrs:
        if attr in task:
            filename = task[attr]
            if isinstance(filename, str) and not re.search(r'\.\w+$', filename):
                warnings.append(f"Warning: File reference '{filename}' in '{attr}' lacks a file extension.")
                missing_ext_count +=1
            

    # Check inside module blocks like 'template', 'copy', etc.
    for key, value in task.items():
        if isinstance(value, dict):
            for attr in file_attrs:
                if attr in value:
                    filename = value[attr]
                    if isinstance(filename, str) and not re.search(r'\.\w+$', filename):
                        warnings.append(
                            f"Warning: File reference '{filename}' in module '{key}', attribute '{attr}' lacks a file extension."
                        )
                        missing_ext_count += 1
                    

    #return warnings, missing_ext_count
    return missing_ext_count

# MAIN SCRIPT
# if __name__ == '__main__':
#     file_path = "/Users/narjes/Documents/Research/Contrib_AnsibleSmells/data/projects/adriagalin/ansible.motd/tasks/main.yml"  
#     tasks = extract_tasks_from_playbook(file_path)

#     results = []
#     """ for task in tasks:
#         if isinstance(task, dict):  # Safety check
#             warnings, has_ext = check_missing_extension(task)
#             results.append({
#                 'task_name': task.get('name', 'Unnamed task'),
#                 'warnings': warnings,
#                 'has_extension': has_ext
#             }) """
#     for task in tasks:
#         if isinstance(task, dict):  # Safety check
#             has_ext = check_missing_extension(task)
#             results.append({
#                 'task_name': task.get('name', 'Unnamed task'),
#                 'has_extension': has_ext
#             })
#     # Output as DataFrame
#     if results:
#         df = pd.DataFrame(results)
#         print(df.to_string(index=False))
#     else:
#         print("No tasks found or no metrics to display.")
