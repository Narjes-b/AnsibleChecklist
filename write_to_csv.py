import csv
def write_results_to_csv(all_results, file_path):
    with open(file_path, 'w', newline='') as csvfile:
        fieldnames = ['Playbook Path', 'Number Play', 'Number Global Task','Number Nested Task', 'Duplicated Code', 'Complex Playbook', 'High Playbook Coupling', 'Large Playbook', 'Unnecessary set_fact', 'Overriding Facts', 'Incohesive Playbook', 'Unecessary Abstraction', 'Insufficient Modularization', 'Inconsistent Naming Convention', 'Large Play', 'Unnamed Play', 'Incohesive Play','Large Task', 'Long Task Name','Unnamed Task', 'Duplicated Task Names','Overriden keys','Missing Bool Filter','Credentials Leaking In Log','Unecessary Dependency','Missing File Extension']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()  

        for playbook_path, playbook_data in all_results.items():
            writer.writerow({
                'Playbook Path': playbook_path, 
                'Number Play': playbook_data['playbook']['metrics'].get('num_plays', ''), 
                'Number Global Task': playbook_data['playbook']['metrics'].get('num_global_tasks_playbook', ''), 
                'Number Nested Task': playbook_data['playbook']['metrics'].get('num_nested_tasks_playbook', ''), 
                'Duplicated Code':playbook_data['playbook']['metrics'].get('duplicated_code', ''), 
                'Complex Playbook':playbook_data['playbook']['metrics'].get('complex_playbook', ''), 
                'High Playbook Coupling':playbook_data['playbook']['metrics'].get('high_coupling', ''),
                'Large Playbook':playbook_data['playbook']['metrics'].get('large_playbook', ''),
                'Unnecessary set_fact':playbook_data['playbook']['metrics'].get('unecessary_set_fact', ''), 
                'Overriding Facts':playbook_data['playbook']['metrics'].get('overriding_facts', ''), 
                'Incohesive Playbook':playbook_data['playbook']['metrics'].get('incohesive_playbook', ''), 
                'Unecessary Abstraction':playbook_data['playbook']['metrics'].get('unecessary_abstraction', ''), 
                'Insufficient Modularization':playbook_data['playbook']['metrics'].get('insufficient_modularization', ''), 
                'Inconsistent Naming Convention':playbook_data['playbook']['metrics'].get('inconsistent_naming_convention', ''), 
                'Large Play':playbook_data['playbook']['metrics'].get('large_play', ''), 
                'Unnamed Play':playbook_data['playbook']['metrics'].get('unnamed_play', ''), 
                'Incohesive Play':playbook_data['playbook']['metrics'].get('similarityPlays', ''),
                'Large Task':playbook_data['playbook']['metrics'].get('large_task', ''),
                'Long Task Name':playbook_data['playbook']['metrics'].get('long_task_name', ''),
                'Unnamed Task':playbook_data['playbook']['metrics'].get('unnamed_tasks', ''),
                'Duplicated Task Names':playbook_data['playbook']['metrics'].get('duplicate_task_names', ''),
                'Overriden keys':playbook_data['playbook']['metrics'].get('overriden_keys', ''),
                'Missing Bool Filter':playbook_data['playbook']['metrics'].get('missing_bool_filters', ''),
                'Credentials Leaking In Log': playbook_data['playbook']['metrics'].get('credentials_leaking_in_log', 0),
                'Unecessary Dependency': playbook_data['playbook']['metrics'].get('unused_include_vars', 0),
                'Missing File Extension':playbook_data['playbook']['metrics'].get('missing_files_extension', '')})


            """ for play in playbook_data['playbook'].get('plays', []):
                ## tasks with defined play
                #print("play", play)
                if play.get('exist_play', '') == 1:
                    
                    writer.writerow({
                        'Playbook Path': '', 
                        'Play Name': play.get('play_name', 'Unknown'), 
                        'Task Name': '', 
                        'duplicated code':'', 
                        'complex playbook':'', 
                        'high playbook coupling':'', 
                        'Large Playbook':'', 
                        'Unnecessary set_fact':'', 
                        'Overriding facts':'', 
                        'Incohesive Playbook':'', 
                        'Unecessary Abstraction':'', 
                        'Insufficient Modularization':'', 
                        'Inconsistent Naming Convention':'', 
                        'Large Play':play.get('metrics', {}).get('large_play', ''), 
                        'Unnamed Play':play.get('metrics', {}).get('unnamed_play', ''), 
                        'Large Task':'', 
                        'Long Task Name':'',
                        'Unnamed Task':'',
                        'Overriden keys':'',
                        'Missing File Extension':''})

                    for task in play.get('tasks', []):
                        #print("task", task)
                        writer.writerow({
                            'Playbook Path': '', 
                            'Play Name': '', 
                            'Task Name': task.get('task_name', 'Unknown'), 
                            'duplicated code':'', 
                            'complex playbook':'', 
                            'high playbook coupling':'', 
                            'Large Playbook':'', 
                            'Unnecessary set_fact':'', 
                            'Overriding facts':'', 
                            'Incohesive Playbook':'', 
                            'Unecessary Abstraction':'', 
                            'Insufficient Modularization':'', 
                            'Inconsistent Naming Convention':'', 
                            'Large Play':'', 
                            'Unnamed Play':'', 
                            'Large Task':task.get('metrics', {}).get('large_task', ''),  
                            'Long Task Name':task.get('metrics', {}).get('long_task_name', ''),
                            'Unnamed Task':task.get('metrics', {}).get('unnamed_tasks', ''),
                            'Overriden keys':playbook_data['playbook']['metrics'].get('overriden_keys', ''),
                            'Missing File Extension':task.get('metrics', {}).get('missing_files_extension', '')})
                
                #tasks without defined play
                else:
                    
                    for task in play.get('tasks', []):
                        #print("task", task)
                        
                        writer.writerow({
                            'Playbook Path': '', 
                            'Play Name': '', 
                            'Task Name': task.get('task_name', 'Unknown'), 
                            'duplicated code':'', 
                            'complex playbook':'', 
                            'high playbook coupling':'', 
                            'Large Playbook':'', 
                            'Unnecessary set_fact':'', 
                            'Overriding facts':'', 
                            'Incohesive Playbook':'', 
                            'Unecessary Abstraction':'', 
                            'Insufficient Modularization':'', 
                            'Inconsistent Naming Convention':'', 
                            'Large Play':'', 
                            'Unnamed Play':'', 
                            'Large Task':task.get('metrics', {}).get('large_task', ''),  
                            'Long Task Name':task.get('metrics', {}).get('long_task_name', ''),
                            'Unnamed Task':task.get('metrics', {}).get('unnamed_tasks', ''),
                            'Overriden keys':playbook_data['playbook']['metrics'].get('overriden_keys', ''),
                            'Missing File Extension':task.get('metrics', {}).get('missing_files_extension', '')}) """