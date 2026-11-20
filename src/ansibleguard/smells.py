from .parser import mainn
import json
import csv
import pandas as pd
from ansibleguard.report.text_writer import write_results_to_txt
from ansibleguard.report.text_writer import write_AnsibleLint_results_to_txt
from ansibleguard.report.text_writer import write_unused_vars_to_txt
from ansibleguard.report.text_writer import write_duplicates_to_txt

from ansibleguard.report.csv_writer import write_results_to_csv

from ansibleguard.report.text_writer import write_GitLeaks_results_to_txt

from ansibleguard.external.ansible_lint import run_ansible_lint

from .external.gitleaks import scan_with_gitleaks_file_output
from .config import (
    csvfile,
    textfile,
    Ansiblelintfile,
    Gitleaksfile,
    JSONfile,
    varsfiles_folder,
    yaml_files_folder,
    RESULTS_DIR,
)

from .config import THRESHOLDS_FILE
from .external.install_gitleaks import GITLEAKS_PATH
from .detector_config import load_detector_config


class FileAnalysisError(RuntimeError):
    """Structured failure raised to the scan orchestrator."""

    def __init__(self, path, stage, cause, partial=False):
        super().__init__(f"{stage} failed for {path}: {cause}")
        self.path = str(path)
        self.stage = stage
        self.cause = cause
        self.partial = bool(partial)


def read_thresholds(path=None):
    thresholds = {}
    with open(THRESHOLDS_FILE, "r") as f:
        reader = csv.reader(f)
        next(reader)  # sauter l'en-tête
        for row in reader:
            if len(row) < 2:
                print(f"Ignored line : {row}")
                continue
            key, value = row[0], float(row[1])
            thresholds[key] = value
    if path is not None:
        for key, value in load_detector_config(path).get("thresholds", {}).items():
            if key in thresholds:
                thresholds[key] = float(value)
    return thresholds


def assess_code_smells(
    metrics,
    thresholds,
    txt_output_files,
    yaml_file_path,
    gitleaks_findings=None,
    provided_lint_results=None,
    run_external=True,
):
    result = {"playbook": {"metrics": {}, "plays": []}}

    # print("metrics", metrics.get('plays', {}))

    playbook_metrics = metrics.get("playbook_metrics")
    if playbook_metrics is None:
        playbook_metrics = {}

    high_coupling_metrics = metrics.get("high_coupling_metrics")
    if high_coupling_metrics is None:
        high_coupling_metrics = {}
    # print("playbook_metrics", playbook_metrics)
    ##missing_files_extension

    result["playbook"]["metrics"]["credentials_leaking_in_log"] = metrics.get(
        "credentials_leaking_in_log", 0
    )

    result["playbook"]["metrics"]["num_plays"] = playbook_metrics.get("num_plays", 0)
    result["playbook"]["metrics"]["num_global_tasks_playbook"] = playbook_metrics.get(
        "num_global_tasks_playbook", 0
    )
    result["playbook"]["metrics"]["num_nested_tasks_playbook"] = playbook_metrics.get(
        "num_nested_tasks_playbook", 0
    )

    result["playbook"]["metrics"]["missing_files_extension"] = metrics.get(
        "missing_files_extension", 0
    )

    result["playbook"]["metrics"]["missing_validate_certs"] = metrics.get(
        "missing_validate_certs", 0
    )

    result["playbook"]["metrics"]["deprecated_modules"] = metrics.get(
        "deprecated_modules", 0
    )
    result["playbook"]["metrics"]["redirected_modules"] = metrics.get(
        "redirected_modules", 0
    )

    result["playbook"]["metrics"]["missing_tags"] = metrics.get("missing_tags", 0)

    result["playbook"]["metrics"]["shell_instead_of_module"] = metrics.get(
        "shell_instead_of_module", 0
    )

    result["playbook"]["metrics"]["missing_handlers"] = metrics.get(
        "missing_handlers", 0
    )

    result["playbook"]["metrics"]["unused_handlers"] = metrics.get("unused_handlers", 0)

    for metric_name in (
        "complex_expressions",
        "incomplete_tasks",
        "long_statements",
        "unstructured_modules",
        "empty_abstractions",
        "excessive_nesting",
        "missing_abstractions",
        "broken_role_dependencies",
        "unguarded_variables",
        "insecure_permissions",
        "unsafe_file_writes",
        "default_credentials",
        "non_idempotent_commands",
        "silent_error_suppressions",
        "redundant_default_values",
        "shell_environment_exports",
        "undocumented_complex_tasks",
        "unused_registered_variables",
        "unscoped_shell_variables",
        "invalid_task_attribute_types",
        "invalid_numeric_values",
        "variable_use_before_definition",
        "unexpected_task_locations",
        "deprecated_module_options",
    ):
        result["playbook"]["metrics"][metric_name] = metrics.get(metric_name, 0)

    result["playbook"]["metrics"]["similarityPlays"] = metrics.get("similarityPlays", 0)
    ##overriden_keys

    result["playbook"]["metrics"]["unused_include_vars"] = metrics.get(
        "unused_include_vars", 0
    )
    warnings = result["playbook"]["metrics"]["WarningUnusedIncludeVars"] = metrics.get(
        "WarningUnusedIncludeVars", []
    )
    # result['playbook']['metrics']['unused_include_vars']= result
    write_unused_vars_to_txt(warnings, txt_output_files)

    result["playbook"]["metrics"]["overriden_keys"] = metrics.get("overriden_keys", 0)
    # print("overriden_keys", result['playbook']['metrics']['overriden_keys'])

    dupes = result["playbook"]["metrics"]["overriden_keys"]
    nbKeys = 0
    # print(f"Found {len(dupes)} tasks with duplicate keys:")
    if dupes:
        for task in dupes:
            # print(f"Task '{task['task_name']}' (starting line {task['start_line']}) has duplicate keys:")
            for key, lines in task["duplicates"].items():
                # print(f"  - Key '{key}' duplicated on lines {lines}")
                nbKeys += 1
        # print(f"Total number of duplicate keys detected: {nbKeys}")
    write_duplicates_to_txt(dupes, txt_output_files)
    result["playbook"]["metrics"]["overriden_keys"] = nbKeys
    # print("overriden_keys", result['playbook']['metrics']['overriden_keys'])
    ##unnamed_play

    result["playbook"]["metrics"]["unnamed_play"] = metrics.get("unnamed_play", 0)
    # print("unnamed_play", result['playbook']['metrics']['unnamed_play'])

    ##unnamed_tasks

    result["playbook"]["metrics"]["unnamed_tasks"] = metrics.get("unnamed_tasks", 0)
    # print("unnamed_tasks", result['playbook']['metrics']['unnamed_tasks'])

    result["playbook"]["metrics"]["duplicate_task_names"] = metrics.get(
        "duplicate_task_names", 0
    )

    result["playbook"]["metrics"]["missing_bool_filters"] = metrics.get(
        "missing_bool_filters", 0
    )

    ####

    #######large_playbook

    if any(
        playbook_metrics.get(key, 0) > thresholds.get(threshold_key, 0)
        for key, threshold_key in [
            ("LOC_playbook", "LOC_playbook"),
            ("num_plays", "num_plays"),
            ("avg_play_size", "avg_play_size"),
            ("num_nested_tasks_playbook", "num_tasks_playbook"),
        ]
    ):
        result["playbook"]["metrics"]["large_playbook"] = 1
    else:
        result["playbook"]["metrics"]["large_playbook"] = 0

    #######complex_playbook — H6: complexity budget formula
    # A playbook is complex when multiple dimensions compound.  Each dimension
    # is normalized by its threshold (contribution 1.0 = exactly at threshold).
    # Firing threshold: budget > 2.0 (at least two dimensions over threshold,
    # or one dimension at 2× threshold).
    _t_loc = thresholds.get("LOC_playbook") or 0
    _t_plays = thresholds.get("num_plays") or 0
    _t_tasks = thresholds.get("num_tasks_playbook") or 0
    _t_imports = thresholds.get("Num_Imports") or 0
    _t_roles = thresholds.get("Num_Roles") or 0

    if _t_loc and _t_plays and _t_tasks and _t_imports and _t_roles:
        _complexity_budget = (
            playbook_metrics.get("LOC_playbook", 0) / _t_loc
            + playbook_metrics.get("num_plays", 0) / _t_plays
            + playbook_metrics.get("num_nested_tasks_playbook", 0) / _t_tasks
            + high_coupling_metrics.get("Num_Imports", 0) / _t_imports
            + high_coupling_metrics.get("Num_Roles", 0) / _t_roles
        )
        result["playbook"]["metrics"]["complex_playbook"] = (
            1 if _complexity_budget > 2.0 else 0
        )
    else:
        # Legacy fallback when thresholds are incomplete
        _legacy_complex = (
            (
                playbook_metrics.get("LOC_playbook", 0) > _t_loc
                and playbook_metrics.get("num_plays", 0) > _t_plays
            )
            or (
                playbook_metrics.get("LOC_playbook", 0) > _t_loc
                and playbook_metrics.get("num_nested_tasks_playbook", 0) > _t_tasks
            )
            or high_coupling_metrics.get("Num_Imports", 0) > _t_imports
            or high_coupling_metrics.get("Num_Roles", 0) > _t_roles
        )
        result["playbook"]["metrics"]["complex_playbook"] = 1 if _legacy_complex else 0

    #########insufficient_modularization
    if playbook_metrics.get("LOC_playbook", 0) > thresholds.get(
        "LOC_playbook", 0
    ) and playbook_metrics.get("num_plays", 0) > thresholds.get("num_plays", 0):
        result["playbook"]["metrics"]["insufficient_modularization"] = 1
    else:
        result["playbook"]["metrics"]["insufficient_modularization"] = 0

    #########high_coupling
    if any(
        high_coupling_metrics.get(key, 0) > thresholds.get(key, 0)
        for key in ["Num_Imports", "Num_Roles"]
    ):
        result["playbook"]["metrics"]["high_coupling"] = 1
    else:
        result["playbook"]["metrics"]["high_coupling"] = 0

    ############incohesive_playbook
    similarity_value = metrics.get("similarity")
    if similarity_value is None:
        # Cohesion couldn't be measured (e.g. no play/task names had a usable
        # word vector — likely non-English or otherwise out-of-vocabulary
        # names). Don't guess; don't crash comparing None < float.
        result["playbook"]["metrics"]["incohesive_playbook"] = None
    elif similarity_value < thresholds.get("similarity", 0):
        result["playbook"]["metrics"]["incohesive_playbook"] = 1
    else:
        result["playbook"]["metrics"]["incohesive_playbook"] = 0

    # print("playbook_metrics", result['playbook']['metrics']['incohesive_playbook'])

    #######duplicated_code
    if metrics.get("duplicated_code", 0) > 0:
        result["playbook"]["metrics"]["duplicated_code"] = metrics.get(
            "duplicated_code", 0
        )
    else:
        result["playbook"]["metrics"]["duplicated_code"] = 0

    #######unecessary_set_fact
    if metrics.get("unecessary_set_fact", 0) > 0:
        result["playbook"]["metrics"]["unecessary_set_fact"] = metrics.get(
            "unecessary_set_fact", 0
        )
    else:
        result["playbook"]["metrics"]["unecessary_set_fact"] = 0

    #######overriding_facts
    if metrics.get("overriding_facts", 0) > 0:
        result["playbook"]["metrics"]["overriding_facts"] = metrics.get(
            "overriding_facts", 0
        )
    else:
        result["playbook"]["metrics"]["overriding_facts"] = 0

    #######unecessary_abstraction
    if metrics.get("unecessary_abstraction", 0) > 0:
        result["playbook"]["metrics"]["unecessary_abstraction"] = metrics.get(
            "unecessary_abstraction", 0
        )
    else:
        result["playbook"]["metrics"]["unecessary_abstraction"] = 0

    findings = (
        scan_with_gitleaks_file_output(yaml_file_path, GITLEAKS_PATH)
        if run_external and gitleaks_findings is None
        else (gitleaks_findings or [])
    )
    result["playbook"]["metrics"]["hardcoded_credentials"] = len(findings)

    lint_results = (
        run_ansible_lint(yaml_file_path)
        if run_external and provided_lint_results is None
        else (provided_lint_results or [])
    )
    result["playbook"]["metrics"]["ansible_lint_issues"] = (
        len(lint_results) if lint_results else 0
    )

    # Suppress internal overriden_keys when ansible-lint covers yaml[key-duplicates]
    # (overlap policy: ansible-lint is canonical for duplicate YAML mapping keys;
    #  the internal detector is an internal-shadow that fires only as fallback).
    if any(
        (r.get("check_name") or r.get("rule_id") or "") == "yaml[key-duplicates]"
        for r in lint_results
    ):
        metrics["overriden_keys"] = []
        result["playbook"]["metrics"]["overriden_keys"] = 0

    # Niveau Play
    if "plays" in metrics:
        # print(metrics)
        num_large_plays = 0
        num_unnamed_plays = 0
        result["playbook"]["metrics"]["large_play"] = 0
        result["playbook"]["metrics"]["unnamed_play"] = 0
        num_large_task = 0
        task_name = 0
        naming_convention = 0
        for play in metrics["plays"]:
            # print("play", play)
            # Case 1: Structured Play (has play_metrics)
            if play.get("play_metrics", {}) != None:
                play_metrics_dict = play.get("play_metrics", {})
                play_result = {
                    "exist_play": 1,
                    "play_name": play_metrics_dict.get("Play_name", "Unknown"),
                    "metrics": {},
                    "tasks": [],
                }

                is_large_play = any(
                    play_metrics_dict.get(metric_key, 0)
                    > thresholds.get(threshold_key, 0)
                    for metric_key, threshold_key in [
                        ("LOC_play", "LOC_play"),
                        ("num_tasks_in_play", "num_tasks_play"),
                        ("avg_task_play", "avg_task_play"),
                    ]
                )
                play_result["metrics"]["large_play"] = int(is_large_play)
                if is_large_play:
                    num_large_plays += 1
                result["playbook"]["metrics"]["large_play"] = num_large_plays

                is_unnamed = play.get("unnamed_play", 0) == 1
                play_result["metrics"]["unnamed_play"] = int(is_unnamed)
                if is_unnamed:
                    num_unnamed_plays += 1
                result["playbook"]["metrics"]["unnamed_play"] = num_unnamed_plays
                # Case 2: Global tasks not in a defined play (play_metrics is None)
            else:
                play_result = {
                    "exist_play": 0,
                    "play_name": "Global",
                    "metrics": {},
                    "tasks": [],
                }
                # NOTE: do NOT touch result["playbook"]["metrics"]["large_play"] or
                # ["unnamed_play"] here — this branch is for top-level "Global" tasks
                # that aren't part of any play, so it must not reset the running counts
                # accumulated from real plays above.
            if "task_metrics" in play:
                for task in play["task_metrics"]:
                    # print("task", task)
                    task_result = {
                        "task_name": task.get("task_name", "Unknown"),
                        "metrics": {},
                    }

                    if task.get("LOC_task", 0) > thresholds.get("LOC_task", 0):
                        num_large_task += 1
                        task_result["metrics"]["large_task"] = 1

                    # else:
                    #   task_result['metrics']['large_task'] = 0

                    if task.get("task_name_len", 0) > thresholds.get(
                        "task_name_len", 0
                    ):
                        task_name += 1
                        task_result["metrics"]["long_task_name"] = 1
                    # else:
                    #   task_result['metrics']['long_task_name'] = 0

                    play_special_chars = (play.get("play_metrics") or {}).get(
                        "special_chars", 0
                    )
                    if task.get("special_chars", 0) > thresholds.get(
                        "special_chars", 0
                    ) or play_special_chars > thresholds.get("special_chars", 0):
                        naming_convention += 1
                        task_result["metrics"]["inconsistent_naming_convention"] = 1
                        #
                    # else:
                    #   result['playbook']['metrics']['inconsistent_naming_convention'] = 0

                    play_result["tasks"].append(task_result)

            result["playbook"]["plays"].append(play_result)

        result["playbook"]["metrics"]["large_task"] = num_large_task
        result["playbook"]["metrics"][
            "inconsistent_naming_convention"
        ] = naming_convention
        result["playbook"]["metrics"]["long_task_name"] = task_name

    return result, findings, lint_results


def execute_for_single_file(
    yaml_file_path,
    csvfile,
    textfile,
    output_dir,
    gitleaks_findings=None,
    lint_results=None,
    run_external=True,
    symbol_index=None,
    raise_on_error=False,
    enabled_rules=None,
    parsed_document=None,
    repository_context=None,
    fail_on_detector_error=False,
):
    all_metrics = {}
    all_results = {}
    findings = list(gitleaks_findings or [])
    lint_results = list(lint_results or [])
    result = None
    metrics = None

    thresholds = read_thresholds(yaml_file_path)

    stage = "internal-detectors"
    try:
        print(f"Analyzing file {yaml_file_path}...")

        include_cohesion = enabled_rules is None or bool(
            {"incohesive-play", "incohesive-playbook"} & set(enabled_rules)
        )
        metrics = mainn(
            yaml_file_path,
            symbol_index=symbol_index,
            include_cohesion=include_cohesion,
            enabled_rules=enabled_rules,
            parsed_document=parsed_document,
            repository_context=repository_context,
            fail_on_detector_error=fail_on_detector_error,
        )
        if metrics is None:
            print(
                f"Skipping {yaml_file_path}: could not be parsed as a valid YAML/Ansible file."
            )
            return findings, lint_results, result, metrics

        stage = "raw-metrics-write"
        JSON_output_file = output_dir / "Technical_Analysis.json"
        with open(JSON_output_file, "w") as f:
            json.dump(metrics, f, indent=4)

        all_metrics[yaml_file_path] = metrics
        csv_output_file = output_dir / "IaC_Smells.csv"
        txt_output_file = output_dir / "Play_Level_Analysis.txt"
        stage = "threshold-evaluation"
        result, findings, lint_results = assess_code_smells(
            metrics,
            thresholds,
            txt_output_file,
            yaml_file_path,
            gitleaks_findings=gitleaks_findings,
            provided_lint_results=lint_results,
            run_external=run_external,
        )

        all_results[yaml_file_path] = result

        stage = "legacy-report-write"
        write_results_to_csv(all_results, csv_output_file)
        write_results_to_txt(all_results, txt_output_file)

        print(f"[ok] Results are saved to {csv_output_file}")
    except Exception as e:
        error = FileAnalysisError(
            yaml_file_path,
            stage,
            e,
            partial=metrics is not None,
        )
        if raise_on_error:
            raise error from e
        print(f"Error while analyzing file {yaml_file_path}: {e}")

    return findings, lint_results, result, metrics


def format_ansible_lint_results(lint_results):
    from .external.ansible_lint import lint_issue_line, lint_issue_path

    formatted = []

    for issue in lint_results:
        rule = issue.get("rule_id") or issue.get("check_name") or "unknown-rule"
        message = (
            issue.get("message") or issue.get("description") or "No message provided"
        )
        path = lint_issue_path(issue) or "unknown-path"
        line = lint_issue_line(issue)
        formatted.append(f"warning: {rule} - {message} at {path}:{line}")

    return formatted


if __name__ == "__main__":
    import os
    from pathlib import Path

    yaml_folder = Path(yaml_files_folder)
    yaml_files = list(yaml_folder.glob("*.yml")) + list(yaml_folder.glob("*.yaml"))

    for yaml_file_path in yaml_files:
        print(f"Processing file: {yaml_file_path}")
        file_stem = yaml_file_path.stem
        output_dir = RESULTS_DIR / file_stem
        output_dir.mkdir(parents=True, exist_ok=True)

        findings, lint_results, result, metrics = execute_for_single_file(
            yaml_file_path, csvfile, textfile, output_dir
        )

        lint_output_file = output_dir / "ansiblelint.txt"
        gitleaks_output_file = output_dir / "gitleaks.txt"

        formatted = format_ansible_lint_results(lint_results)
        write_AnsibleLint_results_to_txt(formatted, lint_output_file, yaml_file_path)
        write_GitLeaks_results_to_txt(findings, gitleaks_output_file)
