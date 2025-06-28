#To prevent credentials from leaking in logs when running Ansible playbooks, you must ensure that any task dealing with sensitive data uses the no_log: true directive. 
#Your anomaly parser should issue a warning whenever a credential-handling task does not use no_log: true, as this omission can lead to password leaks in:


import pandas as pd
import yaml
from detect_large_task import calculate_metrics_task

def detect_credentials_leaking_in_log(yaml_file_path):
    """
    Detects tasks that handle sensitive credentials without using no_log: true.
    
    Args:
        yaml_file_path (str): Path to the Ansible playbook YAML file.
    
    Returns:
        list: List of warnings for tasks that may leak credentials in logs.
    """
    metrics, top_level_tasks = calculate_metrics_task(yaml_file_path)
    warnings = []
    nbLeaks=0
    sensitive_keys = ['password', 'secret', 'api_key', 'token', 'access_key', 'client_secret']

    for task in top_level_tasks:
        try:
            yaml_str = yaml.dump(task, default_flow_style=False)
            content = yaml_str.strip().splitlines()
            #print(f"Content of task: {content}")

            # Check if any sensitive keyword appears in the YAML string
            lower_content = yaml_str.lower()

            # Check for 'no_log' in the task dictionary directly
            no_log_set = task.get('no_log', False)

            if not no_log_set and any(key in lower_content for key in sensitive_keys):
                warnings.append(
                    f"Task '{task.get('name', 'Unnamed task')}' handles a sensitive value but does not use no_log: true — secrets may leak in logs."
                )
                nbLeaks+=1
        except yaml.YAMLError as e:
            warnings.append(f"Error processing task '{task.get('name', 'Unknown')}': {str(e)}")
        except Exception as e:
            warnings.append(f"Unexpected error in task '{task.get('name', 'Unknown')}': {str(e)}")

    return warnings,nbLeaks

# Tester la fonction
file_path = "/Users/narjes/Documents/Research/Contrib_AnsibleSmells/data/projects/adriagalin/ansible.motd/tasks/main.yml"  # Remplacez par le chemin de votre playbook
warnings,nbLeaks = detect_credentials_leaking_in_log(file_path)

if __name__ == '__main__':
    if warnings:
        df = pd.DataFrame(warnings, columns=['Warning'])
        print(df)
    else:
        print('Pas de métriques disponibles.')

