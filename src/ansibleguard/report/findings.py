"""
Flattens one file's analysis output (the raw `metrics` dict from
parser_playbook.mainn(), the post-threshold `result` dict from
smellsDetector.assess_code_smells(), plus the raw GitLeaks `findings` and
ansible-lint `lint_results`) into one flat list of findings:

    {"file": str, "line": int, "rule_id": str, "severity": str, "message": str}

This is the single shape both the plain-JSON output and the SARIF writer
consume -- keeping the flattening logic in one place means both stay in
sync automatically.

Severity/rule-id catalog lives in RULE_CATALOG below rather than scattered
through this file's logic, so it's a data change, not a code change, to
retune later (e.g. once thresholds.csv gets an empirical calibration pass,
or against the project's own Literature_review/ sources).
"""

# level: SARIF's three practical severities -- "error", "warning", "note".
# category: informal grouping, not part of SARIF itself, just useful when
# eyeballing findings.json directly.
RULE_CATALOG = {
    "hardcoded-credentials": {
        "level": "error",
        "category": "security",
        "description": "A hardcoded secret was detected by GitLeaks.",
    },
    "credentials-leaking-in-log": {
        "level": "error",
        "category": "security",
        "description": "A task handles a sensitive value without no_log: true.",
    },
    "overriden-keys": {
        "level": "error",
        "category": "correctness",
        "description": "A duplicate mapping key silently discards a value.",
    },
    "missing-bool-filters": {
        "level": "warning",
        "category": "correctness",
        "description": "A when: condition may be missing a | bool filter.",
    },
    "overriding-facts": {
        "level": "warning",
        "category": "correctness",
        "description": "A set_fact variable is reassigned with a different value.",
    },
    "duplicated-code": {
        "level": "warning",
        "category": "maintainability",
        "description": "Duplicate task blocks detected.",
    },
    "high-coupling": {
        "level": "warning",
        "category": "maintainability",
        "description": "High number of imports/roles.",
    },
    "large-playbook": {
        "level": "warning",
        "category": "maintainability",
        "description": "Playbook exceeds size thresholds.",
    },
    "complex-playbook": {
        "level": "warning",
        "category": "maintainability",
        "description": "Playbook exceeds complexity thresholds.",
    },
    "insufficient-modularization": {
        "level": "warning",
        "category": "maintainability",
        "description": "Playbook is large with many plays -- consider splitting.",
    },
    "large-play": {
        "level": "warning",
        "category": "maintainability",
        "description": "A play exceeds size thresholds.",
    },
    "large-task": {
        "level": "warning",
        "category": "maintainability",
        "description": "A task exceeds size thresholds.",
    },
    "ansible-lint-issue": {
        "level": "warning",
        "category": "lint",
        "description": "ansible-lint reported an issue.",
    },
    "unnamed-play": {
        "level": "note",
        "category": "style",
        "description": "A play has no name:.",
    },
    "unnamed-task": {
        "level": "note",
        "category": "style",
        "description": "A task has no name:.",
    },
    "long-task-name": {
        "level": "note",
        "category": "style",
        "description": "A task name exceeds the length threshold.",
    },
    "inconsistent-naming-convention": {
        "level": "note",
        "category": "style",
        "description": "A task or play name has excessive special characters.",
    },
    "missing-file-extension": {
        "level": "note",
        "category": "style",
        "description": "A file reference is missing a file extension.",
    },
    "unnecessary-abstraction": {
        "level": "note",
        "category": "style",
        "description": "A block: wraps exactly one task.",
    },
    "unnecessary-set-fact": {
        "level": "note",
        "category": "style",
        "description": "A set_fact variable is never used.",
    },
    "unused-include-vars": {
        "level": "note",
        "category": "style",
        "description": "An include_vars file's variables are never used.",
    },
    "duplicate-task-names": {
        "level": "note",
        "category": "style",
        "description": "Multiple tasks share the same name.",
    },
    "incohesive-playbook": {
        "level": "note",
        "category": "cohesion",
        "description": "Play/task names in this playbook are semantically dissimilar.",
    },
    "incohesive-play": {
        "level": "note",
        "category": "cohesion",
        "description": "A play's task names are semantically dissimilar.",
    },
    "missing-validate-certs": {
        "level": "warning",
        "category": "security",
        "description": "TLS certificate validation is disabled on an HTTPS module (uri/get_url).",
    },
    "deprecated-modules": {
        "level": "warning",
        "category": "maintainability",
        "description": "A deprecated Ansible module is in use and may break in future versions.",
    },
    "missing-tags": {
        "level": "note",
        "category": "style",
        "description": "A task has no tags and cannot be targeted with --tags or --skip-tags.",
    },
    "shell-instead-of-module": {
        "level": "warning",
        "category": "maintainability",
        "description": "A shell/command task could be replaced by a native Ansible module.",
    },
    "missing-handler": {
        "level": "error",
        "category": "correctness",
        "description": "A notify references a handler that does not exist.",
    },
    "unused-handler": {
        "level": "warning",
        "category": "maintainability",
        "description": "A handler is defined but never notified.",
    },
}


def _finding(file, line, rule_id, message):
    catalog_entry = RULE_CATALOG.get(rule_id, {"level": "warning"})
    return {
        "file": str(file),
        "line": int(line) if line else 1,
        "rule_id": rule_id,
        "severity": catalog_entry["level"],
        "message": message,
    }


def build_findings_list(
    metrics, result, gitleaks_findings, lint_results, yaml_file_path
):
    """
    metrics: the raw dict from parser_playbook.mainn() (has real line data
             for overriden_keys, and the real per-task warning strings for
             credentials_leaking_in_log, before assess_code_smells()
             collapses both down to bare counts).
    result:  the post-threshold dict from assess_code_smells() (has the
             per-play/per-task pass/fail breakdown).
    gitleaks_findings / lint_results: the raw external-tool outputs,
             already returned by execute_for_single_file() today.
    """
    out = []
    file = yaml_file_path

    # --- GitLeaks: real file+line data already present in its own output ---
    for f in gitleaks_findings or []:
        line = f.get("StartLine") or f.get("startLine") or 1
        desc = f.get("Description") or f.get("RuleID") or "Hardcoded secret detected"
        out.append(_finding(file, line, "hardcoded-credentials", desc))

    # ansible-lint is also target-level and may produce useful load/syntax
    # findings for documents our structural detector cannot analyze.
    from ansibleguard.external.ansible_lint import lint_issue_line

    for issue in lint_results or []:
        line = lint_issue_line(issue)
        message = (
            issue.get("message") or issue.get("description") or "ansible-lint issue"
        )
        out.append(_finding(file, line, "ansible-lint-issue", message))

    if not metrics or not result:
        return out

    pm = result["playbook"]["metrics"]

    # --- credentials_leaking_in_log: use the new details list (real line
    # per task, from credentials_leaking_in_log.py's own ruamel-based
    # rewrite) -- this makes the pipeline's single most security-relevant
    # finding point at the actual task instead of just "somewhere in this
    # file". credentials_leaking_in_log_warnings (plain strings, no line
    # data) stays available for backward-compatible consumers but is no
    # longer what findings.py builds from.
    for detail in metrics.get("credentials_leaking_in_log_details", []) or []:
        out.append(
            _finding(
                file,
                detail.get("line", 1),
                "credentials-leaking-in-log",
                detail.get("message", ""),
            )
        )

    # --- overriden_keys: use the RAW list from metrics (real start_line
    # per task), not result's collapsed count.
    for dup_task in metrics.get("overriden_keys", []) or []:
        task_name = dup_task.get("task_name", "Unknown")
        start_line = dup_task.get("start_line", 1)
        for key, lines in dup_task.get("duplicates", {}).items():
            out.append(
                _finding(
                    file,
                    lines[0] if lines else start_line,
                    "overriden-keys",
                    f"Task '{task_name}': key '{key}' duplicated on lines {lines}",
                )
            )

    # --- unused_include_vars warnings: file-level, no line data available ---
    for warning in pm.get("WarningUnusedIncludeVars", []) or []:
        out.append(_finding(file, 1, "unused-include-vars", warning))

    # --- missing_validate_certs: per-task details ---
    for detail in metrics.get("missing_validate_certs_details", []) or []:
        out.append(
            _finding(
                file,
                detail.get("line", 1),
                "missing-validate-certs",
                f"Task '{detail.get('task_name', 'Unknown')}': "
                f"{detail.get('issue', 'validate_certs disabled')} "
                f"(module={detail.get('module', '?')})",
            )
        )

    # --- deprecated_modules: per-task details ---
    for detail in metrics.get("deprecated_modules_details", []) or []:
        out.append(
            _finding(
                file,
                detail.get("line", 1),
                "deprecated-modules",
                f"Task '{detail.get('task_name', 'Unknown')}': "
                f"{detail.get('issue', 'deprecated module')}",
            )
        )

    # --- missing_tags: per-task details ---
    for detail in metrics.get("missing_tags_details", []) or []:
        out.append(
            _finding(
                file,
                detail.get("line", 1),
                "missing-tags",
                f"Task '{detail.get('task_name', 'Unknown')}': "
                f"{detail.get('issue', 'no tags')}",
            )
        )

    # --- shell_instead_of_module: per-task details ---
    for detail in metrics.get("shell_instead_of_module_details", []) or []:
        out.append(
            _finding(
                file,
                detail.get("line", 1),
                "shell-instead-of-module",
                f"Task '{detail.get('task_name', 'Unknown')}': "
                f"{detail.get('issue', 'shell instead of module')} "
                f"(module: {detail.get('module', '?')}, "
                f"command: {detail.get('command', '?')})",
            )
        )

    # --- handler_issues: per-handler details ---
    for detail in metrics.get("missing_handlers_details", []) or []:
        out.append(
            _finding(
                file,
                detail.get("line", 1),
                "missing-handler",
                f"Notify '{detail.get('handler_name', '?')}': "
                f"{detail.get('issue', 'missing handler')}",
            )
        )
    for detail in metrics.get("unused_handlers_details", []) or []:
        out.append(
            _finding(
                file,
                detail.get("line", 1),
                "unused-handler",
                f"Handler '{detail.get('handler_name', '?')}': "
                f"{detail.get('issue', 'unused handler')}",
            )
        )

    # --- playbook-level boolean/count smells: file-level (line 1) ---
    playbook_level_simple = [
        ("large_playbook", "large-playbook", "Playbook exceeds size thresholds"),
        (
            "complex_playbook",
            "complex-playbook",
            "Playbook exceeds complexity thresholds",
        ),
        (
            "insufficient_modularization",
            "insufficient-modularization",
            "Large playbook with many plays",
        ),
        ("high_coupling", "high-coupling", "High number of imports/roles"),
        ("duplicated_code", "duplicated-code", "Duplicate task blocks detected"),
        (
            "unecessary_set_fact",
            "unnecessary-set-fact",
            "Unused set_fact variable(s) detected",
        ),
        (
            "overriding_facts",
            "overriding-facts",
            "A set_fact variable is reassigned with a different value",
        ),
        (
            "unecessary_abstraction",
            "unnecessary-abstraction",
            "block: wraps exactly one task",
        ),
        (
            "missing_files_extension",
            "missing-file-extension",
            "File reference missing an extension",
        ),
        (
            "duplicate_task_names",
            "duplicate-task-names",
            "Multiple tasks share the same name",
        ),
        (
            "missing_bool_filters",
            "missing-bool-filters",
            "when: condition may be missing | bool",
        ),
        (
            "similarityPlays",
            "incohesive-play",
            "A play's task names are semantically dissimilar",
        ),
    ]
    for key, rule_id, label in playbook_level_simple:
        count = pm.get(key, 0)
        if count:
            out.append(_finding(file, 1, rule_id, f"{label} (count={count})"))

    if pm.get("incohesive_playbook") == 1:
        out.append(
            _finding(
                file,
                1,
                "incohesive-playbook",
                "Play/task names in this playbook are semantically dissimilar",
            )
        )

    # --- unnamed_play / unnamed_tasks: use the dedicated *_details lists
    # from metrics (real line numbers, from unnamed_play.py's/
    # unnamed_tasks.py's own ruamel-based checks) rather than trying to
    # infer this while walking result's play/task structure, where the
    # line field doesn't survive assess_code_smells()'s play_result/
    # task_result construction anyway (see the zip below for why that
    # matters for large-play/large-task instead).
    for detail in metrics.get("unnamed_play_details", []) or []:
        out.append(
            _finding(file, detail.get("line", 1), "unnamed-play", "A play has no name:")
        )
    for detail in metrics.get("unnamed_tasks_details", []) or []:
        out.append(
            _finding(file, detail.get("line", 1), "unnamed-task", "A task has no name:")
        )

    # --- play-level and task-level size/naming findings: result's
    # play_result/task_result dicts don't carry the real "line" field
    # through (assess_code_smells() drops it when building them), even
    # though the raw metrics["plays"] entries do. Zip the two structures
    # by index -- they're built one-to-one, in the same order, by
    # assess_code_smells()'s own loop over metrics["plays"] -- so real
    # line numbers can still be recovered instead of falling back to
    # line 1 for these two finding types now.
    result_plays = result["playbook"].get("plays", [])
    raw_plays = metrics.get("plays", [])
    for result_play, raw_play in zip(result_plays, raw_plays):
        play_name = result_play.get("play_name", "Unknown")
        raw_play_metrics = raw_play.get("play_metrics") or {}
        play_line = raw_play_metrics.get("line", 1)

        if result_play.get("metrics", {}).get("large_play"):
            out.append(
                _finding(
                    file,
                    play_line,
                    "large-play",
                    f"Play '{play_name}' exceeds size thresholds",
                )
            )

        result_tasks = result_play.get("tasks", [])
        raw_tasks = raw_play.get("task_metrics", [])
        for result_task, raw_task in zip(result_tasks, raw_tasks):
            task_name = result_task.get("task_name", "Unknown")
            task_line = raw_task.get("line", 1)
            tm = result_task.get("metrics", {})
            if tm.get("large_task"):
                out.append(
                    _finding(
                        file,
                        task_line,
                        "large-task",
                        f"Task '{task_name}' exceeds size thresholds",
                    )
                )
            if tm.get("long_task_name"):
                out.append(
                    _finding(
                        file,
                        task_line,
                        "long-task-name",
                        f"Task '{task_name}' name is too long",
                    )
                )
            if tm.get("inconsistent_naming_convention"):
                out.append(
                    _finding(
                        file,
                        task_line,
                        "inconsistent-naming-convention",
                        f"Task '{task_name}' or its play has excessive special characters",
                    )
                )

    return out
