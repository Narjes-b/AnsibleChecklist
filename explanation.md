# Project Explanation

This document explains the purpose of each folder and file in the repository. It is designed to help you understand what has been implemented and how the main components fit together.

---

## Root Files

- `README.md`
  - Existing main project documentation.
  - Includes installation instructions, a demo video link, and usage notes for `ansible-lint`, `GitLeaks`, and the analyzer.

- `requirements.txt`
  - Lists Python dependencies required by the project.
  - Includes tools such as `ansible`, `ansible-lint`, `ansiblemetrics`, `PyYAML`, `pandas`, `typer`, `requests`, and many helper libraries.

- `thresholds.csv`
  - Defines numeric thresholds for metrics used by the analyzer.
  - Example keys: `LOC_playbook`, `num_plays`, `avg_play_size`, `num_tasks_playbook`, `Num_Imports`, `Num_Roles`, `similarity`, `LOC_play`, `num_tasks_play`, `avg_task_play`, `special_chars`, `LOC_task`, `task_name_len`.

- `IaC_smells_definition.pdf`
  - Likely a document defining the infrastructure-as-code smells targeted by the project.

---

## `AnsibleGuard/`

This is the main analysis engine of the project. It contains the code that reads Ansible playbooks, computes metrics, detects smells, and exports results.

### Core orchestrators

- `parser_playbook.py`
  - Main analysis orchestrator for a single YAML playbook file.
  - Imports detector functions and computes aggregated metrics such as playbook size, coupling, duplicate code, unused `set_fact`, overriding facts, missing extensions, unnamed plays/tasks, duplicate task names, missing boolean filters, and GitLeaks results.
  - Returns a `main_metrics` dictionary with nested metrics for the playbook, plays, and tasks.

- `parser_playbook_mod.py`
  - A variant parser with CSV writing support.
  - Reads playbook file paths from CSV and computes the same kinds of metrics as `parser_playbook.py`.
  - Includes helper functions to create CSV rows for playbook, play, and task metrics.
  - Appears intended for batch processing multiple playbooks and exporting results.

- `smellsDetector.py`
  - Evaluates raw metrics against thresholds.
  - Combines results from multiple detectors and produces higher-level smell decisions like `large_playbook`, `complex_playbook`, `insufficient_modularization`, `high_coupling`, `incohesive_playbook`, and alerts for duplicate keys or unused vars.
  - Also coordinates `ansible-lint` and GitLeaks scans and writes results to text output files.

### Security and external tool integration

- `Ansible_Lint.py`
  - Wrapper for running the external `ansible-lint` command.
  - Can return JSON-formatted lint results or plain text.

- `Install_Gitleaks.py`
  - Downloads and installs the `gitleaks` binary into `AnsibleGuard/gitleaks-bin/`.
  - Supports Linux, macOS, and Windows download URLs.
  - Sets executable permissions on the downloaded binary.

- `GitLeaks_hardcoded_credentials.py`
  - Runs `gitleaks detect` against a playbook file.
  - Produces JSON findings of hardcoded secrets and credentials.
  - Uses a temporary file to capture the report.

### Metrics and smell detectors

- `detect_large_playbook.py`
  - Computes playbook-level metrics such as line count, number of plays, average play size, nested task counts, and global task counts.
  - Uses `ansiblemetrics` helpers and play/task metric functions.

- `detect_large_play.py`
  - Computes metrics at the play level.
  - Likely measures size and task count per individual play.

- `detect_large_task.py`
  - Computes metrics at the task level.
  - Probably extracts LOC and task length statistics for each task.

- `high_coupling.py`
  - Detects coupling in the playbook by analyzing role and import usage.
  - Used to determine whether the playbook is tightly coupled.

- `duplicate_code.py`
  - Detects repeated tasks by comparing task structures and parameters.
  - Ignores task names and counts how many duplicate task definitions exist.

- `duplicate_task_Name.py`
  - Detects tasks that share the same `name` field within a playbook.
  - Helps find repeated or ambiguous task naming.

- `overriden_keys.py`
  - Detects duplicate keys inside task dictionaries.
  - Returns tasks where the same key is defined multiple times within a single task, which can mask values.

- `overriding_facts.py`
  - Detects facts that are overwritten by later tasks.
  - Helps find redundant or conflicting `set_fact` usage.

- `set_fact.py`
  - Detects unnecessary `set_fact` usage.
  - Part of the analysis for redundant variable assignment smells.

- `unecessary_abs.py`
  - Detects unnecessary abstraction patterns in playbooks.
  - Likely flags abstraction or indirection that does not add value.

- `sem_cohesion.py`
  - Computes similarity or cohesion metrics for the playbook.
  - Used to assess how cohesive or incohesive the playbook is.

- `incohesive_plays.py`
  - Computes similarity across plays.
  - Helps detect whether plays are too different or not grouped logically.

- `unnamed_play.py`
  - Detects plays that do not have meaningful `name` values.

- `is_unamed.py`
  - Helper function to decide if a play or task name is considered unnamed.

- `unnamed_tasks.py`
  - Detects tasks without names.
  - Useful for finding anonymous tasks that make playbooks harder to understand.

- `include_vars.py`
  - Detects unused variables loaded via `include_vars`.
  - Parses playbooks and included var files, then checks whether those vars are actually referenced.

- `files_extensions.py`
  - Scans tasks for file references like `src`, `file`, `cmd`, `path`.
  - Flags file references that are missing file extensions.

- `filters_for_comparison.py`
  - Analyzes `when:` conditions.
  - Detects missing `| bool` filters and comparisons against string literals like `"true"` or `"false"`.

- `credentials_leaking_in_log.py`
  - Detects credentials that may be leaked in logs.
  - Likely searches tasks or strings for credential patterns.

- `exceptions.py`
  - Contains custom exception classes used by the analyzer.
  - Provides structured error handling across the system.

### Output and export helpers

- `write_to_csv.py`
  - Writes analyzed metrics into CSV format.
  - Used by batch processing or export flows.

- `write_to_text.py`
  - Writes human-readable text reports.
  - Includes functions for writing `ansible-lint` results, GitLeaks results, unused vars warnings, duplicate key reports, and play-level smell reports.

### Data and configuration files

- `thresholds.csv`
  - Defines the numeric thresholds used by the analyzer to mark a playbook, play, or task as problematic.
  - These thresholds drive the decision logic in `smellsDetector.py`.

- `gitleaks-bin/`
  - Stores the downloaded `gitleaks` executable.
  - Includes the binary and license info.

- `parser_playbook.ipynb`
  - Jupyter notebook version of the playbook parser.
  - Likely used for experimentation or interactive analysis.

---

## `GitLeaks_Smells/`

This folder contains output data from GitLeaks scans.

- `gitleaks_full_smells.csv`
  - CSV export of full GitLeaks findings.

- `gitleaks_full_smells.json`
  - JSON export of full GitLeaks findings.

These files are used as examples or historical results for hardcoded credentials analysis.

---

## `Literature_review/`

Contains research material, notes, or references used to design the Ansible IaC smell detection.

- Likely includes papers, checklists, and background documents supporting the implemented smell logic.

---

## `TestData/`

Contains sample playbook data, sample projects, and results for testing and validation.

- `Paths.csv`
  - Probably a list of playbook paths used for batch analysis.

- `projects/`
  - Example Ansible project directories used for testing the analyzer.
  - Includes at least `adriagalin/ansible.motd/` with sample roles, tasks, templates, and test data.

- `Results/`
  - Stored result files from previous analysis runs.
  - Subfolders such as `main/`, `main-2/`, and `main3/` include `ansiblelint.txt`, `gitleaks.txt`, `IaC_Smells.csv`, `Play_Level_Analysis.txt`, and `Technical_Analysis.json`.

- `tasks/`
  - YAML files like `main.yml`, `main-2.yml`, and `main3.yml` used as test playbooks.

---

## How the project works together

1. `parser_playbook.py` or `parser_playbook_mod.py` is used to analyze one or more playbooks.
2. These parser files call detector modules in `AnsibleGuard/` to compute metrics and identify smells.
3. `smellsDetector.py` evaluates those metrics against `thresholds.csv` and formats the final smell results.
4. `Ansible_Lint.py` and `GitLeaks_hardcoded_credentials.py` integrate external security tools.
5. `write_to_text.py` and `write_to_csv.py` export the results to human-readable reports and CSV files.

---

## Important implementation notes

- Many modules currently use hardcoded local paths in `config.py` and in scanner code.
- `config.py` points to user-specific directories like `/Users/narjes/Documents/Research/Contrib_AnsibleSmells/...`.
- To run the project on another machine, update those paths to your own workspace locations.

---

## Recommended next steps

- Update `config.py` to use relative paths or CLI arguments instead of absolute local paths.
- Use `requirements.txt` to install dependencies in a virtual environment.
- Run `Install_Gitleaks.py` once to ensure `gitleaks` is available.
- Start analysis with `parser_playbook.py` or `parser_playbook_mod.py` and inspect outputs in `TestData/Results/`.

---

## Summary

This repository is a time-series analyzer for Ansible playbooks and roles with these main focuses:

- Playbook complexity and size metrics
- Task-level smell detection
- Duplicate and overridden code detection
- Unused included variables
- Missing file extensions and boolean filter issues
- Security scanning via `ansible-lint` and GitLeaks

The `AnsibleGuard` folder contains the actual analysis implementation, while `TestData` and `GitLeaks_Smells` store sample input and output data.
