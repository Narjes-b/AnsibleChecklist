from collections import defaultdict
from write_to_text import write_duplicates_to_txt
def detect_duplicate_keys_per_task(yaml_file_path):
    duplicates_report = []

    with open(yaml_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    current_task_keys = defaultdict(list)  # key -> list of line numbers in current task
    in_task = False
    task_indent = None
    task_name = None
    task_start_line = None

    for i, line in enumerate(lines, start=1):
        stripped = line.lstrip()
        indent = len(line) - len(stripped)

        # Detect task start: line starting with '- name:' (basic heuristic)
        if stripped.startswith('- name:'):
            # If already in a task, report duplicates found so far
            if in_task:
                duplicates = {k: v for k, v in current_task_keys.items() if len(v) > 1}
                if duplicates:
                    duplicates_report.append({
                        'task_name': task_name or 'Unknown',
                        'start_line': task_start_line,
                        'duplicates': duplicates
                    })
                current_task_keys.clear()

            in_task = True
            task_indent = indent
            task_start_line = i
            # Get task name
            task_name = stripped[len('- name:'):].strip() or 'Unknown'

        elif in_task:
            # Check if indent is less or equal task indent → task ended
            if indent <= task_indent and stripped.startswith('- '):
                # report duplicates for previous task
                duplicates = {k: v for k, v in current_task_keys.items() if len(v) > 1}
                if duplicates:
                    duplicates_report.append({
                        'task_name': task_name or 'Unknown',
                        'start_line': task_start_line,
                        'duplicates': duplicates
                    })
                # Reset for next task
                current_task_keys.clear()
                in_task = False
                task_name = None
                task_start_line = None
            else:
                # Track keys in current task
                # Detect keys in "key: value" format (simple)
                if ':' in stripped:
                    key = stripped.split(':', 1)[0].strip()
                    current_task_keys[key].append(i)

    # Final task duplicates check if file ends inside a task
    if in_task:
        duplicates = {k: v for k, v in current_task_keys.items() if len(v) > 1}
        if duplicates:
            duplicates_report.append({
                'task_name': task_name or 'Unknown',
                'start_line': task_start_line,
                'duplicates': duplicates
            })

    return duplicates_report


# Usage example:
 
if __name__ == '__main__':
    file_path = '/Users/narjes/Documents/Research/Contrib_AnsibleSmells/data/projects/adriagalin/ansible.motd/tasks/main.yml'
    dupes = detect_duplicate_keys_per_task(file_path)
    write_duplicates_to_txt(dupes, '/Users/narjes/Documents/Research/Contrib_AnsibleSmells/data/Play_Level_Analysis.txt')

