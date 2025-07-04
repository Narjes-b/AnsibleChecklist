import yaml
import pandas as pd
import re
import regex as re

def compter_lignes_dans_task(task):
    try:
        yaml_str = yaml.dump(task, default_flow_style=False)
        return len(yaml_str.strip().splitlines())
    except Exception:
        return 0

def compter_caracteres_speciaux(chaine):
    return len(re.findall(r'[^\p{L}\p{N}\s]', chaine))

def analyser_tasks(tasks, metrics, play_id):
    for task in tasks:
        # Check for 'block' tasks first
        if 'block' in task:
            analyser_tasks(task['block'], metrics, play_id)

        # Handle standard task (with or without a name)
        task_name = task.get('name')
        if not isinstance(task_name, str) or not task_name.strip():
            task_name = 'Unknown'
        
        lignes = compter_lignes_dans_task(task)
        metrics.append({
            'play_id': play_id,
            'task_name': task_name,
            'LOC_task': lignes,
            'task_name_len': 0 if task_name == 'Unknown' else len(task_name),
            'special_chars': compter_caracteres_speciaux(task_name) if task_name != 'Unknown' else 0
        })

def analyser_play(play, metrics, play_id):
    if 'block' in play:
        analyser_tasks(play['block'], metrics, play_id)

    elif 'tasks' in play:
        for task in play['tasks']:
            if 'block' in task:  # Si c'est un block, analyser les tasks à l'intérieur
                analyser_tasks(task['block'], metrics, play_id)
            else:  # Sinon, c'est une tâche standard
                analyser_tasks([task], metrics, play_id)
def count_nested_tasks(tasks):
    count = 0
    for task in tasks:
        # Count this task itself
        count += 1
        
        # Recursively count nested structures
        if isinstance(task, dict):
            for section in ['block', 'rescue', 'always']:
                if section in task and isinstance(task[section], list):
                    count += count_nested_tasks(task[section])
    return count

def count_tasks_in_playbook(yaml_data):
    total_tasks = 0
    for play in yaml_data:
        if isinstance(play, dict) and 'tasks' in play and isinstance(play['tasks'], list):
            total_tasks += count_nested_tasks(play['tasks'])
        #else:
         #   # Optionally warn about malformed plays
          #  if not isinstance(play, dict) or 'tasks' not in play:
           #     print(f"⚠️ Skipping malformed or taskless play: {play}")
    return total_tasks

def calculate_metrics_task(yaml_file_path):
    with open(yaml_file_path, 'r', encoding='utf-8') as f:
        playbook = yaml.safe_load(f)

    all_metrics = []

    if isinstance(playbook, list):
        play_id = 0
        top_level_tasks = []

        for entry in playbook:
            #print(f"Processing entry: {entry}")
            if isinstance(entry, dict) and ("hosts" in entry or "tasks" in entry or "block" in entry):
                analyser_play(entry, all_metrics, play_id)
                play_id += 1
            else:
                
                top_level_tasks.append(entry)
   
        if top_level_tasks:
            analyser_tasks(top_level_tasks, all_metrics, play_id=-1)  # -1 means "global" tasks
    #print(top_level_tasks)
    #print(all_metrics)
    return all_metrics,top_level_tasks

# Tester la fonction
file_path = "/Users/narjes/Documents/Research/Contrib_AnsibleSmells/data/projects/adoptium/infrastructure/ansible/playbooks/nagios/roles/Nagios_Server/tasks/restart_nagios_server.yml"  # Remplacez par le chemin de votre playbook
metrics = calculate_metrics_task(file_path)

if __name__ == '__main__':
    if metrics:
        df = pd.DataFrame(metrics)
        print(df)
    else:
        print('Pas de métriques disponibles.')
