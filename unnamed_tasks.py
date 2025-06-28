import yaml
from detect_large_task import calculate_metrics_task
def unnamed_tasks(file_path):
    """ try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except (yaml.YAMLError, FileNotFoundError) as e:
        print("Erreur lors de l'analyse du fichier YAML ou fichier non trouvé :", e)
        return None """

    unnamed_tasks = []
    tasks=[]
    all_metrics,tasks = calculate_metrics_task(file_path)
    #print("tasks:", tasks)
    if not tasks:
        print("No tasks found in the file.")
        return 0
    for task in tasks:
            #print("task:", task)
            #for key, value in task.items():
                #print(f"{key}: {value}")
            task_name = task.get("task_name")
                #print(f"Task: {task_name}")
            if task_name== "Unknown":
                unnamed_tasks.append(task)
                #print(f"Unnamed task found: {task}")
    ##counts only tasks under -tasks:
    """ if isinstance(data, list):
        for play_index, play in enumerate(data):
            if isinstance(play, dict) and "tasks" in play:
                for task_index, task in enumerate(play["tasks"]):
                    task_name = task.get("name")
                    print(f"Play {play_index}, Task {task_index}: {task_name}")
                    if not isinstance(task_name, str) or not task_name.strip():
                        unnamed_tasks.append((play_index, task_index, task)) """
   
    #print("Unnamed tasks found:", len(unnamed_tasks))
    return len(unnamed_tasks)
    if unnamed_tasks:
        return 1
    else:
        return 0

# Tester la fonction
file_path = "/Users/narjes/Documents/Research/Contrib_AnsibleSmells/data/projects/adriagalin/ansible.motd/tasks/main.yml"
result = unnamed_tasks(file_path)
#if __name__ == "__main__":
    #if result is not None:
       # print(result) 
