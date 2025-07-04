import yaml
from collections import Counter

from detect_large_task import calculate_metrics_task
def repeated_task_names(file_path):
    
    repeated = []
    repeated_task_names = []
    tasks=[]
    tasks = calculate_metrics_task(file_path)
    #print("tasks:", tasks)
    if not tasks:
        print("No tasks found in the file.")
        return 0
    task_names = [task.get("task_name", "").strip() for task in tasks if "task_name" in task]

    # Count occurrences
    name_counts = Counter(task_names)

    # Identify names that occur more than once
    repeated = [name for name, count in name_counts.items() if count > 1]
    #print("repeated:", repeated)
    return len(repeated)
    if repeated_task_names:
        return 1
    else:
        return 0

# Tester la fonction
file_path = "/Users/narjes/Documents/Research/Contrib_AnsibleSmells/data/projects/adriagalin/ansible.motd/tasks/main.yml"
result = repeated_task_names(file_path)
#if __name__ == "__main__":
    #if result is not None:
       # print(result) 
