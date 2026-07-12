import csv


def write_results_to_csv(all_results, file_path):
    with open(file_path, "w", newline="") as csvfile:
        fieldnames = [
            "Playbook Path",
            "Number Play",
            "Number Global Task",
            "Number Nested Task",
            "Duplicated Code",
            "Complex Playbook",
            "High Playbook Coupling",
            "Large Playbook",
            "Unnecessary set_fact",
            "Overriding Facts",
            "Incohesive Playbook",
            "Unecessary Abstraction",
            "Insufficient Modularization",
            "Inconsistent Naming Convention",
            "Large Play",
            "Unnamed Play",
            "Incohesive Play",
            "Large Task",
            "Long Task Name",
            "Unnamed Task",
            "Duplicated Task Names",
            "Overriden keys",
            "Missing Bool Filter",
            "Credentials Leaking In Log",
            "Unecessary Dependency",
            "Hardcoded Credentials",
            "Missing File Extension",
            "Missing Validate Certs",
            "Deprecated Modules",
            "Missing Tags",
            "Shell Instead of Module",
            "Missing Handlers",
            "Unused Handlers",
            "Design Smells",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        for playbook_path, playbook_data in all_results.items():
            metrics = playbook_data["playbook"]["metrics"]
            incohesive_playbook_value = metrics.get("incohesive_playbook")
            writer.writerow(
                {
                    "Playbook Path": playbook_path,
                    "Number Play": metrics.get("num_plays", ""),
                    "Number Global Task": metrics.get("num_global_tasks_playbook", ""),
                    "Number Nested Task": metrics.get("num_nested_tasks_playbook", ""),
                    "Duplicated Code": metrics.get("duplicated_code", ""),
                    "Complex Playbook": metrics.get("complex_playbook", ""),
                    "High Playbook Coupling": metrics.get("high_coupling", ""),
                    "Large Playbook": metrics.get("large_playbook", ""),
                    "Unnecessary set_fact": metrics.get("unecessary_set_fact", ""),
                    "Overriding Facts": metrics.get("overriding_facts", ""),
                    "Incohesive Playbook": incohesive_playbook_value
                    if incohesive_playbook_value is not None
                    else "",
                    "Unecessary Abstraction": metrics.get("unecessary_abstraction", ""),
                    "Insufficient Modularization": metrics.get(
                        "insufficient_modularization", ""
                    ),
                    "Inconsistent Naming Convention": metrics.get(
                        "inconsistent_naming_convention", ""
                    ),
                    "Large Play": metrics.get("large_play", ""),
                    "Unnamed Play": metrics.get("unnamed_play", ""),
                    "Incohesive Play": metrics.get("similarityPlays", ""),
                    "Large Task": metrics.get("large_task", ""),
                    "Long Task Name": metrics.get("long_task_name", ""),
                    "Unnamed Task": metrics.get("unnamed_tasks", ""),
                    "Duplicated Task Names": metrics.get("duplicate_task_names", ""),
                    "Overriden keys": metrics.get("overriden_keys", ""),
                    "Missing Bool Filter": metrics.get("missing_bool_filters", ""),
                    "Credentials Leaking In Log": metrics.get(
                        "credentials_leaking_in_log", 0
                    ),
                    "Unecessary Dependency": metrics.get("unused_include_vars", 0),
                    "Hardcoded Credentials": metrics.get("hardcoded_credentials", 0),
                    "Missing File Extension": metrics.get(
                        "missing_files_extension", ""
                    ),
                    "Missing Validate Certs": metrics.get(
                        "missing_validate_certs", ""
                    ),
                    "Deprecated Modules": metrics.get(
                        "deprecated_modules", ""
                    ),
                    "Missing Tags": metrics.get(
                        "missing_tags", ""
                    ),
                    "Shell Instead of Module": metrics.get(
                        "shell_instead_of_module", ""
                    ),
                    "Missing Handlers": metrics.get(
                        "missing_handlers", ""
                    ),
                    "Unused Handlers": metrics.get(
                        "unused_handlers", ""
                    ),
                    "Design Smells": metrics.get("ansible_lint_issues", ""),
                }
            )

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
