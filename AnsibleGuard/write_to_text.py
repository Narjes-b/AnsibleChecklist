     

def write_AnsibleLint_results_to_txt(all_results, file_path,yaml_file_path):
    with open(file_path, 'w') as txtfile:
        
            txtfile.write(f"AnsibleLint analysis for playbook {yaml_file_path}:\n")
            txtfile.write("\n\n")

            for line in all_results:
              #print(line)
              txtfile.write(f"- {line}\n")
    print(f"[✔] AnsibleLint analysis saved to {file_path}")        
            
import json
from pathlib import Path

def write_GitLeaks_results_to_txt(findings, file_path):
    output_file = Path(file_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)  # Ensure dir exists

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(findings, f, indent=2)

    
    print(f"[✔] GitLeaks analysis saved to {file_path}")        
          


def write_unused_vars_to_txt(warnings, file_path):
    with open(file_path, 'w', newline='\n') as txtfile:
        txtfile.write("### UNECESSARY DEPENDENCIES  ###.\n\n")

        if warnings:
            for warning in warnings:
                #print(warning.strip())
                txtfile.write(warning.strip() + '\n')
        else:
            txtfile.write("No unnecessary dependencies found.\n")        
        txtfile.write("\n")
        txtfile.write("\n")            
        print(f"[✔] Unnecessary dependencies saved to {file_path}")


def write_duplicates_to_txt(dupes, file_path):
    with open(file_path, 'a', newline='\n') as txtfile:
        txtfile.write("### OVERRIDEN KEYS  ###.\n\n")
        if not dupes:
            txtfile.write("No duplicate keys found.\n\n")
            return

        nbKeys = 0
        txtfile.write(f"Found {len(dupes)} tasks with duplicate keys:\n\n")

        for task in dupes:
            txtfile.write(f"Task '{task['task_name']}' (starting line {task['start_line']}) has duplicate keys:\n")
            for key, lines in task['duplicates'].items():
                txtfile.write(f"  - Key '{key}' duplicated on lines {lines}\n")
                nbKeys += 1
            txtfile.write("\n")

        txtfile.write(f"Total number of duplicate keys detected: {nbKeys}\n")
        txtfile.write("\n")
        txtfile.write("\n")
        print(f"[✔] Duplicate key report saved to {file_path}")


def write_results_to_txt(all_results, file_path):
    with open(file_path, 'a') as txtfile:
        txtfile.write("### PLAY LEVEL IAC SMELLS  ###.\n\n")
        for playbook_path, playbook_data in all_results.items():
            """ txtfile.write(f"IaC smells detected for playbook {playbook_path}:\n")
            
            playbook_smells = [k for k, v in playbook_data['playbook']['metrics'].items() if v == 1]
            if playbook_smells:
                for smell in playbook_smells:
                    txtfile.write(f"- {smell}\n")
            else:
                txtfile.write("No IaC smell detected.\n") """

            for play in playbook_data['playbook'].get('plays', []):
                play_smells = [k for k, v in play.get('metrics', {}).items() if v == 1]

                if play.get('exist_play', '') == 1:
                    txtfile.write(f"\nPlay:: {play.get('play_name', 'Unknown')}:\n")

                    if play_smells:
                        for smell in play_smells:
                            txtfile.write(f"- {smell}\n")
                    else:
                        txtfile.write("No IaC smell detected for this play.\n")

                    for task in play.get('tasks', []):
                        task_smells = [k for k, v in task.get('metrics', {}).items() if v == 1]
                        
                        txtfile.write(f"\n\tTask:: {task.get('task_name', 'Unknown')}:\n")
                        if task_smells:
                            for smell in task_smells:
                                txtfile.write(f"\t- {smell}\n")
                        else:
                            txtfile.write("\tNo IaC smell detected for this task.\n")
                else:
                    for task in play.get('tasks', []):
                        task_smells = [k for k, v in task.get('metrics', {}).items() if v == 1]
                        
                        txtfile.write(f"\n\tTask:: {task.get('task_name', 'Unknown')}:\n")
                        if task_smells:
                            for smell in task_smells:
                                txtfile.write(f"\t- {smell}\n")
                        else:
                            txtfile.write("\tNo IaC smell detected for this task.\n")
            
            txtfile.write("\n\n")

    print(f"[✔] Plays level IaC smells analysis saved to {file_path}")  



    