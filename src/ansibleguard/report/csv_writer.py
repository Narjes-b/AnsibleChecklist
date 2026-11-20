import csv
import json

from .llm_explain import STRUCTURED_FIELDS, ASSESSMENT_FIELDS


FINDING_FIELDS = (
    "file",
    "line",
    "rule_id",
    "severity",
    "message",
    "provider",
    "native_rule_id",
    "concept_id",
    "variable_classification",
    "legacy_concept_id",
    "native_severity",
    "confidence",
    "analysis_population",
    "source_population",
    "classification_confidence",
    "secret_population",
    "taxonomy",
    "actionability",
    "rule_maturity",
    "remediation",
    "help_url",
    "finding_id",
    "llm_status",
    *ASSESSMENT_FIELDS,
    "llm_explanation",
    "llm_why_in_this_context",
    "llm_suggested_fix",
    "llm_fixed_code_snippet",
    "llm_confidence",
    "llm_limitations",
    "llm_disclaimer",
)


def write_findings_to_csv(findings, file_path, include_schema_version=False):
    """Write the normalized finding contract, including project-level rules."""
    fieldnames = (
        ("schema_version", *FINDING_FIELDS)
        if include_schema_version
        else FINDING_FIELDS
    )
    with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for finding in findings:
            row = {field: finding.get(field, "") for field in FINDING_FIELDS}
            for field in STRUCTURED_FIELDS:
                if field in finding:
                    row[field] = json.dumps(finding[field], ensure_ascii=False)
            if include_schema_version:
                row["schema_version"] = 2
            writer.writerow(row)


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
            "Complex Expressions",
            "Incomplete Tasks",
            "Long Statements",
            "Unstructured Modules",
            "Empty Abstractions",
            "Excessive Nesting",
            "Missing Abstractions",
            "Broken Role Dependencies",
            "Unguarded Variables",
            "Insecure Permissions",
            "Default Credentials",
            "Non-idempotent Commands",
            "Silent Error Suppressions",
            "Redundant Default Values",
            "Shell Environment Exports",
            "Undocumented Complex Tasks",
            "Unused Registered Variables",
            "Unscoped Shell Variables",
            "Invalid Task Attribute Types",
            "Invalid Numeric Values",
            "Variable Use Before Definition",
            "Unexpected Task Locations",
            "Deprecated Module Options",
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
                    "Incohesive Playbook": (
                        incohesive_playbook_value
                        if incohesive_playbook_value is not None
                        else ""
                    ),
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
                    "Missing Validate Certs": metrics.get("missing_validate_certs", ""),
                    "Deprecated Modules": metrics.get("deprecated_modules", ""),
                    "Missing Tags": metrics.get("missing_tags", ""),
                    "Shell Instead of Module": metrics.get(
                        "shell_instead_of_module", ""
                    ),
                    "Missing Handlers": metrics.get("missing_handlers", ""),
                    "Unused Handlers": metrics.get("unused_handlers", ""),
                    "Complex Expressions": metrics.get("complex_expressions", ""),
                    "Incomplete Tasks": metrics.get("incomplete_tasks", ""),
                    "Long Statements": metrics.get("long_statements", ""),
                    "Unstructured Modules": metrics.get("unstructured_modules", ""),
                    "Empty Abstractions": metrics.get("empty_abstractions", ""),
                    "Excessive Nesting": metrics.get("excessive_nesting", ""),
                    "Missing Abstractions": metrics.get("missing_abstractions", ""),
                    "Broken Role Dependencies": metrics.get(
                        "broken_role_dependencies", ""
                    ),
                    "Unguarded Variables": metrics.get("unguarded_variables", ""),
                    "Insecure Permissions": metrics.get("insecure_permissions", ""),
                    "Default Credentials": metrics.get("default_credentials", ""),
                    "Non-idempotent Commands": metrics.get(
                        "non_idempotent_commands", ""
                    ),
                    "Silent Error Suppressions": metrics.get(
                        "silent_error_suppressions", ""
                    ),
                    "Redundant Default Values": metrics.get(
                        "redundant_default_values", ""
                    ),
                    "Shell Environment Exports": metrics.get(
                        "shell_environment_exports", ""
                    ),
                    "Undocumented Complex Tasks": metrics.get(
                        "undocumented_complex_tasks", ""
                    ),
                    "Unused Registered Variables": metrics.get(
                        "unused_registered_variables", ""
                    ),
                    "Unscoped Shell Variables": metrics.get(
                        "unscoped_shell_variables", ""
                    ),
                    "Invalid Task Attribute Types": metrics.get(
                        "invalid_task_attribute_types", ""
                    ),
                    "Invalid Numeric Values": metrics.get("invalid_numeric_values", ""),
                    "Variable Use Before Definition": metrics.get(
                        "variable_use_before_definition", ""
                    ),
                    "Unexpected Task Locations": metrics.get(
                        "unexpected_task_locations", ""
                    ),
                    "Deprecated Module Options": metrics.get(
                        "deprecated_module_options", ""
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
