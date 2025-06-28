
from parser_playbook import mainn
import json
import csv
import pandas as pd
from write_to_text import write_results_to_txt
from write_to_text import write_AnsibleLint_results_to_txt
from write_to_text import write_unused_vars_to_txt
from write_to_text import write_duplicates_to_txt
from write_to_csv import write_results_to_csv
from Ansible_Lint import run_ansible_lint
from config import yaml_file_path, csvfile, textfile, Ansiblelintfile
def read_thresholds():
    thresholds = {}
    with open('/Users/narjes/Documents/Research/Contrib_AnsibleSmells/AnsibleCodeSmells-master/CodeSmellsTool/thresholds.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)  # sauter l'en-tête
        for row in reader:
            if len(row) < 2:
                print(f"Ignored line : {row}")
                continue
            key, value = row[0], float(row[1])  
            thresholds[key] = value
    return thresholds


def assess_code_smells(metrics, thresholds):
    result = {
        'playbook': {
            'metrics': {},
            'plays': []
        }
    }
    
    #print("metrics", metrics.get('plays', {}))
    
    playbook_metrics = metrics.get('playbook_metrics', {})
    #print("playbook_metrics", playbook_metrics)
    ##missing_files_extension

    result['playbook']['metrics']['credentials_leaking_in_log'] = metrics.get('credentials_leaking_in_log', 0)

    result['playbook']['metrics']['num_plays'] = playbook_metrics.get('num_plays', 0)
    result['playbook']['metrics']['num_global_tasks_playbook'] = playbook_metrics.get('num_global_tasks_playbook', 0)
    result['playbook']['metrics']['num_nested_tasks_playbook'] = playbook_metrics.get('num_nested_tasks_playbook', 0)

    result['playbook']['metrics']['missing_files_extension'] = metrics.get('missing_files_extension', 0)

    result['playbook']['metrics']['similarityPlays'] = metrics.get('similarityPlays', 0)
    ##overriden_keys

    result['playbook']['metrics']['unused_include_vars'] = metrics.get('unused_include_vars', 0)
    warnings = result['playbook']['metrics']['WarningUnusedIncludeVars'] = metrics.get('WarningUnusedIncludeVars', [])
    #result['playbook']['metrics']['unused_include_vars']= result
    write_unused_vars_to_txt(warnings, textfile)

    result['playbook']['metrics']['overriden_keys'] = metrics.get('overriden_keys', 0)
    #print("overriden_keys", result['playbook']['metrics']['overriden_keys'])

    dupes = result['playbook']['metrics']['overriden_keys']
    nbKeys=0
    #print(f"Found {len(dupes)} tasks with duplicate keys:")
    if dupes:
        for task in dupes:
            #print(f"Task '{task['task_name']}' (starting line {task['start_line']}) has duplicate keys:")
            for key, lines in task['duplicates'].items():
                #print(f"  - Key '{key}' duplicated on lines {lines}")
                nbKeys+=1
        #print(f"Total number of duplicate keys detected: {nbKeys}")   
    write_duplicates_to_txt(dupes, textfile)  
    result['playbook']['metrics']['overriden_keys']= nbKeys
    #print("overriden_keys", result['playbook']['metrics']['overriden_keys'])
    ##unnamed_play

    result['playbook']['metrics']['unnamed_play'] = metrics.get('unnamed_play', 0)
    #print("unnamed_play", result['playbook']['metrics']['unnamed_play'])

    ##unnamed_tasks

    result['playbook']['metrics']['unnamed_tasks'] = metrics.get('unnamed_tasks', 0)
    #print("unnamed_tasks", result['playbook']['metrics']['unnamed_tasks'])


    result['playbook']['metrics']['duplicate_task_names']  = metrics.get('duplicate_task_names', 0)

    
    result['playbook']['metrics']['missing_bool_filters']  = metrics.get('missing_bool_filters', 0)

    ####

    #######large_playbook

    if any(playbook_metrics.get(key, 0) > thresholds.get(key, 0) for key in ['LOC_playbook', 'num_plays', 'avg_play_size', 'num_tasks_playbook']):
        result['playbook']['metrics']['large_playbook'] = 1
    else:
        result['playbook']['metrics']['large_playbook'] = 0
      
    

    #######complex_playbook

    if (
    (playbook_metrics.get('LOC_playbook', 0) > thresholds.get('LOC_playbook', 0) and playbook_metrics.get('num_plays', 0) > thresholds.get('num_plays', 0)) or
    (playbook_metrics.get('LOC_playbook', 0) > thresholds.get('LOC_playbook', 0) and playbook_metrics.get('num_tasks_playbook', 0) > thresholds.get('num_tasks_playbook', 0)) or
    playbook_metrics.get('Num_Imports', 0) > thresholds.get('Num_Imports', 0) or
    playbook_metrics.get('Num_Roles', 0) > thresholds.get('num_roles', 0)
    ):
        result['playbook']['metrics']['complex_playbook'] = 1

    else:
        result['playbook']['metrics']['complex_playbook'] = 0


    #########insufficient_modularization
    if (
    (playbook_metrics.get('LOC_playbook', 0) > thresholds.get('LOC_playbook', 0) and playbook_metrics.get('num_plays', 0) > thresholds.get('num_plays', 0)) 
    ):
        result['playbook']['metrics']['insufficient_modularization'] = 1
    else:
        result['playbook']['metrics']['insufficient_modularization'] = 0

    #########high_coupling
    if any(playbook_metrics.get(key, 0) > thresholds.get(key, 0) for key in ['Num_Imports', 'Num_Roles']):
        result['playbook']['metrics']['high_coupling'] = 1
    else:
        result['playbook']['metrics']['high_coupling'] = 0
        

        
    ############incohesive_playbook
    if metrics.get('similarity', 0) < thresholds.get('similarity', 0):
        result['playbook']['metrics']['incohesive_playbook'] = 1
    else:
        result['playbook']['metrics']['incohesive_playbook'] = 0

    #print("playbook_metrics", result['playbook']['metrics']['incohesive_playbook'])      


     #######duplicated_code
    if  metrics.get('duplicated_code', 0) >0:
        result['playbook']['metrics']['duplicated_code'] = metrics.get('duplicated_code', 0)
    else:
        result['playbook']['metrics']['duplicated_code'] = 0  

    #######unecessary_set_fact
    if  metrics.get('unecessary_set_fact', 0) >0:
        result['playbook']['metrics']['unecessary_set_fact'] = metrics.get('unecessary_set_fact', 0)
    else:
        result['playbook']['metrics']['unecessary_set_fact'] = 0  
        
    #######overriding_facts
    if  metrics.get('overriding_facts', 0) >0:
        result['playbook']['metrics']['overriding_facts'] = metrics.get('overriding_facts', 0)
    else:
        result['playbook']['metrics']['overriding_facts'] = 0   

    #######unecessary_abstraction
    if  metrics.get('unecessary_abstraction', 0) >0:
        result['playbook']['metrics']['unecessary_abstraction'] = metrics.get('unecessary_abstraction', 0)
    else:
        result['playbook']['metrics']['unecessary_abstraction'] = 0             

    
    
    # Niveau Play
    if 'plays' in metrics:
        #print(metrics)
        num_large_plays = 0
        num_unnamed_plays = 0
        for play in metrics['plays']:
            #print("play", play)
            # ✅ Case 1: Structured Play (has play_metrics)
            if play.get('play_metrics', {}) != None:
        
                
                play_result = {
                    'exist_play': 1,
                    'play_name': play.get('play_metrics', {}).get('Play_name', 'Unknown'),
                    'metrics': {},
                    'tasks': []
                }
                    
                is_large_play =any(play_result.get(key, 0) > thresholds.get(key, 0) for key in ['LOC_play', 'num_tasks_play', 'avg_task_size'])
                #print("is_large_play", is_large_play)
                play_result['metrics']['large_play'] = int(is_large_play)
                if is_large_play:
                    num_large_plays += 1
                   
                play_result['metrics']['large_play'] = num_large_plays
                #print("play_result", num_large_plays)
                result['playbook']['metrics']['large_play']=num_large_plays
                

                is_unnamed = play.get('unnamed_play', 0) == 1
                play_result['metrics']['unnamed_play'] = int(is_unnamed)
                if is_unnamed:
                    num_unnamed_plays += 1
                play_result['metrics']['unnamed_play'] = num_unnamed_plays

                # ✅ Case 2: Global tasks not in a defined play (play_metrics is None)
            else:
                    
                    play_result = {
                        'exist_play': 0,
                        'play_name': 'Global',
                        'metrics': {},
                        'tasks': []
                    }
                    
                    result['playbook']['metrics']['large_play'] = 0
            if 'task_metrics' in play:
                    num_large_task = 0
                    task_name=0
                    naming_convention=0
                    for task in play['task_metrics']:
                        #print("task", task)
                        task_result = {
                            'task_name': task.get('task_name', 'Unknown'),
                            'metrics': {}
                        }
            
                        if task.get('LOC_task', 0) > thresholds.get('LOC_task', 0):
                            num_large_task=+1
                            task_result['metrics']['large_task'] = 1
                        
                        
                        #else:
                         #   task_result['metrics']['large_task'] = 0

                        if task.get('task_name_len', 0) > thresholds.get('task_name_len', 0):
                            task_name+=1
                            task_result['metrics']['long_task_name'] = 1
                        #else:
                         #   task_result['metrics']['long_task_name'] = 0

                        if task.get('special_chars', 0) > thresholds.get('special_chars', 0) or play.get('special_chars', 0) > thresholds.get('special_chars', 0) :
                            naming_convention+=1
                            task_result['metrics']['inconsistent_naming_convention'] = 1
                            #
                        #else:
                         #   result['playbook']['metrics']['inconsistent_naming_convention'] = 0

                        play_result['tasks'].append(task_result)
                    #print("num_large_task", num_large_task)
                    result['playbook']['metrics']['large_task'] = num_large_task  
                    result['playbook']['metrics']['inconsistent_naming_convention'] = naming_convention
                    result['playbook']['metrics']['long_task_name']= task_name




            result['playbook']['plays'].append(play_result)       
            """ else:
               
                play_result = {
                    'exist_play': 0,
                    'tasks': []
                }
                if 'task_metrics' in play:
                    for task in play['task_metrics']:
                        task_result = {
                            'task_name': task.get('task_name', 'Unknown'),
                            'metrics': {}
                        }
                        
                        if task.get('LOC_task', 0) > thresholds.get('LOC_task', 0):
                            task_result['metrics']['large_task'] = 1
                        else:
                            task_result['metrics']['large_task'] = 0

                        if task.get('task_name_len', 0) > thresholds.get('task_name_len', 0):
                            task_result['metrics']['long_task_name'] = 1
                        else:
                            task_result['metrics']['long_task_name'] = 0

                        if task.get('special_chars', 0) > thresholds.get('special_chars', 0):
                            result['playbook']['metrics']['inconsistent_naming_convention'] = 1
                        else:
                            result['playbook']['metrics']['inconsistent_naming_convention'] = 0  

                        play_result['tasks'].append(task_result)
            result['playbook']['plays'].append(play_result)  """
    return result


                        
def execute_for_single_file(yaml_file_path,csvfile,textfile):
    
    all_metrics = {}
    
    all_results = {}
    
    thresholds = read_thresholds()
    
    try:
        print(f"Analyzing file {yaml_file_path}...")
        
        metrics = mainn(yaml_file_path)
        
       
        all_metrics[yaml_file_path] = metrics
        
        result = assess_code_smells(metrics, thresholds)
        
        all_results[yaml_file_path] = result
        
        write_results_to_csv(all_results, csvfile)
        write_results_to_txt(all_results, textfile)
        
        print(f"[✔] Results are saved to {csvfile}")
    except Exception as e:
        print(f"Error while analyzing file {yaml_file_path}: {e}")

    

def format_ansible_lint_results(lint_results):
    formatted = []

    for issue in lint_results:
        # Use check_name or rule_id as identifier
        rule = issue.get('rule_id') or issue.get('check_name') or 'unknown-rule'

        # Use message or provide fallback
        message = issue.get('message') or issue.get('description') or 'No message provided'

        # Get location if available
        location = issue.get('location', {})
        path = issue.get('path') or location.get('path') or 'unknown-path'
        line = issue.get('line') or location.get('line') or '?'

        formatted.append(f"⚠️ {rule} - {message} at {path}:{line}")

    return formatted


if __name__ == "__main__":
    
    #yaml_file_path = input("Enter your Playbook path : ")
    
    execute_for_single_file(yaml_file_path,csvfile,textfile)

    lint_results = run_ansible_lint(yaml_file_path)

    formatted = format_ansible_lint_results(lint_results)
    write_AnsibleLint_results_to_txt(formatted,Ansiblelintfile,yaml_file_path)
    
    

    


    

