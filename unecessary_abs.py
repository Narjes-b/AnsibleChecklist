import yaml

def unecessary_abs(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            playbook = yaml.load(f, Loader=yaml.Loader)
    except yaml.YAMLError as e:
        print("Erreur lors de l'analyse du fichier YAML:", e)
        return None
    except FileNotFoundError as e:
        print(f"Fichier {file_path} non trouvé:", e)
        return None

    unnecessary_abstraction_detected = 0
    
    for play in playbook:
        # Case 1: Play with 'tasks'
        if isinstance(play, dict) and 'tasks' in play:
            for task in play.get('tasks', []):
                if isinstance(task, dict) and 'block' in task:
                    if isinstance(task['block'], list) and len(task['block']) == 1:
                        unnecessary_abstraction_detected += 1

        # Case 2: Top-level task (as in a role's main.yml or playbook without 'tasks' key)
        elif isinstance(play, dict) and 'block' in play:
            if isinstance(play['block'], list) and len(play['block']) == 1:
                unnecessary_abstraction_detected += 1
                    
        #if unnecessary_abstraction_detected:
         #   break

    return unnecessary_abstraction_detected

# Tester la fonction
if __name__ == "__main__":
    file_path = "/Users/narjes/Documents/Research/Contrib_AnsibleSmells/data/projects/adriagalin/ansible.motd/tasks/main.yml"
    result = unecessary_abs(file_path)
    
    if result is not None:
        print(result)
