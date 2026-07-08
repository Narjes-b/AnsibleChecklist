"""Regression tests for findings.py's build_findings_list() -- the function
that flattens one file's analysis into the {file, line, rule_id, severity,
message} shape both findings.json and findings.sarif are built from.
Previously only verified manually, one-off, this session -- never locked
in as a real test until now."""

from ansibleguard.report.findings import build_findings_list, RULE_CATALOG


def _base_result(playbook_metrics_overrides=None, plays=None):
    """Minimal result shape matching what assess_code_smells() actually
    returns, with everything defaulted to a clean/zero state."""
    pm = {
        "large_playbook": 0,
        "complex_playbook": 0,
        "insufficient_modularization": 0,
        "high_coupling": 0,
        "duplicated_code": 0,
        "unecessary_set_fact": 0,
        "overriding_facts": 0,
        "unecessary_abstraction": 0,
        "missing_files_extension": 0,
        "duplicate_task_names": 0,
        "missing_bool_filters": 0,
        "similarityPlays": 0,
        "incohesive_playbook": 0,
        "WarningUnusedIncludeVars": [],
    }
    if playbook_metrics_overrides:
        pm.update(playbook_metrics_overrides)
    return {"playbook": {"metrics": pm, "plays": plays or []}}


def _base_metrics(overrides=None):
    metrics = {
        "credentials_leaking_in_log_details": [],
        "overriden_keys": [],
        "unnamed_play_details": [],
        "unnamed_tasks_details": [],
        "plays": [],
    }
    if overrides:
        metrics.update(overrides)
    return metrics


# --- empty/missing input handling ---


def test_returns_empty_list_when_metrics_is_none():
    result = _base_result()
    assert build_findings_list(None, result, [], [], "f.yml") == []


def test_returns_empty_list_when_result_is_none():
    metrics = _base_metrics()
    assert build_findings_list(metrics, None, [], [], "f.yml") == []


def test_returns_empty_list_for_clean_file_with_no_issues():
    metrics = _base_metrics()
    result = _base_result()
    assert build_findings_list(metrics, result, [], [], "f.yml") == []


# --- GitLeaks findings: real line data already present in GitLeaks' own output ---


def test_gitleaks_finding_uses_real_line_and_error_severity():
    metrics = _base_metrics()
    result = _base_result()
    gitleaks_findings = [{"StartLine": 42, "Description": "AWS Access Key"}]

    out = build_findings_list(metrics, result, gitleaks_findings, [], "f.yml")

    assert len(out) == 1
    assert out[0]["rule_id"] == "hardcoded-credentials"
    assert out[0]["line"] == 42
    assert out[0]["severity"] == "error"
    assert out[0]["message"] == "AWS Access Key"


def test_gitleaks_finding_falls_back_to_line_1_when_no_line_data():
    metrics = _base_metrics()
    result = _base_result()
    gitleaks_findings = [{"Description": "Something found"}]

    out = build_findings_list(metrics, result, gitleaks_findings, [], "f.yml")
    assert out[0]["line"] == 1


# --- ansible-lint findings: real line data from the tool's own output ---


def test_ansible_lint_finding_uses_real_line_and_warning_severity():
    metrics = _base_metrics()
    result = _base_result()
    lint_results = [{"message": "Use FQCN", "location": {"path": "f.yml", "line": 5}}]

    out = build_findings_list(metrics, result, [], lint_results, "f.yml")

    assert len(out) == 1
    assert out[0]["rule_id"] == "ansible-lint-issue"
    assert out[0]["line"] == 5
    assert out[0]["severity"] == "warning"
    assert out[0]["message"] == "Use FQCN"


# --- credentials_leaking_in_log: uses the new *_details list, real line, error severity ---


def test_credentials_leaking_finding_uses_real_line_from_details():
    metrics = _base_metrics(
        {
            "credentials_leaking_in_log_details": [
                {
                    "task_name": "Set password",
                    "line": 7,
                    "message": "Task 'Set password' leaks a secret",
                }
            ]
        }
    )
    result = _base_result()

    out = build_findings_list(metrics, result, [], [], "f.yml")

    assert len(out) == 1
    assert out[0]["rule_id"] == "credentials-leaking-in-log"
    assert out[0]["line"] == 7
    assert out[0]["severity"] == "error"
    assert out[0]["message"] == "Task 'Set password' leaks a secret"


# --- overriden_keys: uses the raw duplicate-key list, real line, error severity ---


def test_overriden_keys_finding_uses_first_duplicate_line():
    metrics = _base_metrics(
        {
            "overriden_keys": [
                {"task_name": "task4", "start_line": 4, "duplicates": {"name": [4, 6]}}
            ]
        }
    )
    result = _base_result()

    out = build_findings_list(metrics, result, [], [], "f.yml")

    assert len(out) == 1
    assert out[0]["rule_id"] == "overriden-keys"
    assert out[0]["line"] == 4  # first entry in duplicates["name"] == [4, 6]
    assert out[0]["severity"] == "error"
    assert "task4" in out[0]["message"]
    assert "name" in out[0]["message"]


def test_overriden_keys_multiple_duplicate_keys_produce_multiple_findings():
    metrics = _base_metrics(
        {
            "overriden_keys": [
                {
                    "task_name": "task8",
                    "start_line": 83,
                    "duplicates": {"src": [85, 90], "dest": [86, 91]},
                }
            ]
        }
    )
    result = _base_result()

    out = build_findings_list(metrics, result, [], [], "f.yml")
    assert len(out) == 2
    rule_ids = {f["rule_id"] for f in out}
    assert rule_ids == {"overriden-keys"}


# --- unused_include_vars warnings: file-level, line 1 ---


def test_unused_include_vars_warning_produces_a_finding():
    result = _base_result(
        playbook_metrics_overrides={
            "WarningUnusedIncludeVars": ["Warning: unused var 'foo'"]
        }
    )
    metrics = _base_metrics()

    out = build_findings_list(metrics, result, [], [], "f.yml")

    assert len(out) == 1
    assert out[0]["rule_id"] == "unused-include-vars"
    assert out[0]["line"] == 1
    assert out[0]["message"] == "Warning: unused var 'foo'"


# --- playbook-level simple counts: only fire when truthy, correct severity per rule ---


def test_playbook_level_counts_only_fire_when_nonzero():
    metrics = _base_metrics()
    result = _base_result(
        playbook_metrics_overrides={
            "large_playbook": 1,
            "complex_playbook": 0,  # must NOT produce a finding
            "duplicated_code": 3,
        }
    )

    out = build_findings_list(metrics, result, [], [], "f.yml")
    rule_ids = {f["rule_id"] for f in out}

    assert "large-playbook" in rule_ids
    assert "complex-playbook" not in rule_ids
    assert "duplicated-code" in rule_ids


def test_playbook_level_count_includes_the_real_count_in_message():
    metrics = _base_metrics()
    result = _base_result(playbook_metrics_overrides={"duplicated_code": 3})

    out = build_findings_list(metrics, result, [], [], "f.yml")
    dup_finding = next(f for f in out if f["rule_id"] == "duplicated-code")
    assert "count=3" in dup_finding["message"]


def test_playbook_level_counts_use_warning_severity():
    metrics = _base_metrics()
    result = _base_result(playbook_metrics_overrides={"large_playbook": 1})

    out = build_findings_list(metrics, result, [], [], "f.yml")
    assert out[0]["severity"] == "warning"


# --- incohesive_playbook: special-cased, only fires on exactly 1, not 0 or None ---


def test_incohesive_playbook_equal_one_produces_finding():
    metrics = _base_metrics()
    result = _base_result(playbook_metrics_overrides={"incohesive_playbook": 1})

    out = build_findings_list(metrics, result, [], [], "f.yml")
    assert len(out) == 1
    assert out[0]["rule_id"] == "incohesive-playbook"
    assert out[0]["severity"] == "note"


def test_incohesive_playbook_none_does_not_produce_finding():
    """None means 'unmeasurable' (e.g. all-OOV task names) -- must not be
    treated as a truthy count the way the simple playbook-level counts are."""
    metrics = _base_metrics()
    result = _base_result(playbook_metrics_overrides={"incohesive_playbook": None})

    out = build_findings_list(metrics, result, [], [], "f.yml")
    assert out == []


def test_incohesive_playbook_zero_does_not_produce_finding():
    metrics = _base_metrics()
    result = _base_result(playbook_metrics_overrides={"incohesive_playbook": 0})

    out = build_findings_list(metrics, result, [], [], "f.yml")
    assert out == []


# --- unnamed_play / unnamed_tasks: use the *_details lists, real line, note severity ---


def test_unnamed_play_detail_produces_finding_with_real_line():
    metrics = _base_metrics({"unnamed_play_details": [{"line": 15}]})
    result = _base_result()

    out = build_findings_list(metrics, result, [], [], "f.yml")

    assert len(out) == 1
    assert out[0]["rule_id"] == "unnamed-play"
    assert out[0]["line"] == 15
    assert out[0]["severity"] == "note"


def test_unnamed_task_detail_produces_finding_with_real_line():
    metrics = _base_metrics(
        {"unnamed_tasks_details": [{"task_name": "Unknown", "line": 4}]}
    )
    result = _base_result()

    out = build_findings_list(metrics, result, [], [], "f.yml")

    assert len(out) == 1
    assert out[0]["rule_id"] == "unnamed-task"
    assert out[0]["line"] == 4


# --- play-level and task-level size/naming findings: real line pulled from
# metrics (which assess_code_smells() drops), zipped against result's flags ---


def _play_and_task(
    large_play=0,
    unnamed_play_flag=0,
    large_task=0,
    long_task_name=0,
    inconsistent_naming=0,
    play_line=1,
    task_line=1,
):
    result_play = {
        "play_name": "p",
        "metrics": {"large_play": large_play, "unnamed_play": unnamed_play_flag},
        "tasks": [
            {
                "task_name": "t",
                "metrics": {
                    "large_task": large_task,
                    "long_task_name": long_task_name,
                    "inconsistent_naming_convention": inconsistent_naming,
                },
            }
        ],
    }
    raw_play = {
        "play_metrics": {"line": play_line},
        "task_metrics": [{"line": task_line}],
    }
    return result_play, raw_play


def test_large_play_finding_uses_real_line_from_metrics_not_result():
    result_play, raw_play = _play_and_task(large_play=1, play_line=9)
    result = _base_result(plays=[result_play])
    metrics = _base_metrics({"plays": [raw_play]})

    out = build_findings_list(metrics, result, [], [], "f.yml")

    large_play_findings = [f for f in out if f["rule_id"] == "large-play"]
    assert len(large_play_findings) == 1
    assert large_play_findings[0]["line"] == 9


def test_large_task_and_long_task_name_and_naming_convention_use_real_task_line():
    result_play, raw_play = _play_and_task(
        large_task=1, long_task_name=1, inconsistent_naming=1, task_line=42
    )
    result = _base_result(plays=[result_play])
    metrics = _base_metrics({"plays": [raw_play]})

    out = build_findings_list(metrics, result, [], [], "f.yml")

    rule_ids = {f["rule_id"] for f in out}
    assert rule_ids == {
        "large-task",
        "long-task-name",
        "inconsistent-naming-convention",
    }
    assert all(f["line"] == 42 for f in out)


def test_play_and_task_findings_absent_when_flags_are_zero():
    result_play, raw_play = _play_and_task()  # everything defaults to 0
    result = _base_result(plays=[result_play])
    metrics = _base_metrics({"plays": [raw_play]})

    out = build_findings_list(metrics, result, [], [], "f.yml")
    assert out == []


def test_multiple_plays_and_tasks_all_produce_findings_not_just_the_last():
    """Regression-shaped test mirroring the exact bug class found earlier
    this session (per-play/per-task counters that only reflected the last
    play processed) -- here at the findings-list level: two plays, each
    with one oversized task, must both appear, not just one."""
    play1, raw1 = _play_and_task(large_task=1, task_line=10)
    play2, raw2 = _play_and_task(large_task=1, task_line=20)
    result = _base_result(plays=[play1, play2])
    metrics = _base_metrics({"plays": [raw1, raw2]})

    out = build_findings_list(metrics, result, [], [], "f.yml")

    large_task_findings = [f for f in out if f["rule_id"] == "large-task"]
    assert len(large_task_findings) == 2
    assert {f["line"] for f in large_task_findings} == {10, 20}


# --- RULE_CATALOG sanity: every rule_id this function can ever emit must
# have a real entry, or _finding()'s .get(rule_id, {"level": "warning"})
# fallback would silently mask a typo in a rule_id string literal ---


def test_every_rule_id_used_in_this_file_exists_in_rule_catalog():
    expected_rule_ids = {
        "hardcoded-credentials",
        "ansible-lint-issue",
        "credentials-leaking-in-log",
        "overriden-keys",
        "unused-include-vars",
        "large-playbook",
        "complex-playbook",
        "insufficient-modularization",
        "high-coupling",
        "duplicated-code",
        "unnecessary-set-fact",
        "overriding-facts",
        "unnecessary-abstraction",
        "missing-file-extension",
        "duplicate-task-names",
        "missing-bool-filters",
        "incohesive-play",
        "incohesive-playbook",
        "unnamed-play",
        "unnamed-task",
        "large-play",
        "large-task",
        "long-task-name",
        "inconsistent-naming-convention",
    }
    missing = expected_rule_ids - set(RULE_CATALOG.keys())
    assert not missing, f"RULE_CATALOG is missing entries for: {missing}"


def test_rule_catalog_every_entry_has_a_valid_sarif_level():
    valid_levels = {"error", "warning", "note"}
    for rule_id, meta in RULE_CATALOG.items():
        assert meta["level"] in valid_levels, (
            f"{rule_id} has invalid level {meta['level']!r} -- SARIF only accepts "
            f"error/warning/note"
        )
