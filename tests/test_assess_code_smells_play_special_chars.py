from ansibleguard.smells import assess_code_smells, read_thresholds


def _make_metrics(task_special_chars, play_special_chars):
    """Minimal but realistic metrics dict matching parser_playbook.mainn()'s
    real output shape for a single structured play with one task."""
    return {
        "playbook_metrics": {
            "LOC_playbook": 5,
            "num_plays": 1,
            "avg_play_size": 5,
            "num_nested_tasks_playbook": 1,
            "num_global_tasks_playbook": 0,
        },
        "high_coupling_metrics": {"Num_Imports": 0, "Num_Roles": 0},
        "similarity": 1,
        "duplicated_code": 0,
        "unecessary_set_fact": 0,
        "overriding_facts": 0,
        "unecessary_abstraction": 0,
        "missing_files_extension": 0,
        "unnamed_play": 0,
        "unnamed_tasks": 0,
        "overriden_keys": [],
        "duplicate_task_names": 0,
        "missing_bool_filters": 0,
        "similarityPlays": 0,
        "credentials_leaking_in_log": 0,
        "unused_include_vars": 0,
        "WarningUnusedIncludeVars": [],
        "plays": [
            {
                "play_metrics": {
                    "play_id": 0,
                    "Play_name": "p",
                    "LOC_play": 10,
                    "num_tasks_in_play": 1,
                    "tasks_names": ["t"],
                    "avg_task_play": 10,
                    "special_chars": play_special_chars,
                },
                "unnamed_play": 0,
                "task_metrics": [
                    {
                        "play_id": 0,
                        "task_name": "t",
                        "LOC_task": 2,
                        "task_name_len": 14,
                        "special_chars": task_special_chars,
                    }
                ],
            }
        ],
    }


def test_play_level_special_chars_no_longer_crashes(tmp_path, monkeypatch):
    """Regression test for a real AttributeError crash in the naming-
    convention check: play_special_chars = (play.get('play_metrics') or
    {}).get('special_chars', 0) already unwraps to a plain int, but the
    very next line called .get('special_chars', 0) on that int AGAIN
    ('int' object has no attribute 'get'). This only fired when the
    task's own special_chars did NOT exceed threshold (Python's `or`
    short-circuits, so the buggy right-hand side was skipped whenever the
    left-hand side was already True) -- meaning it silently never crashed
    on the project's own tiny fixtures (which never had a real structured
    play with a plain, low-special-char task name reach this branch) but
    reproduced immediately on a realistic synthetic case. Confirmed
    against the real, unmodified assess_code_smells() before fixing."""
    monkeypatch.setattr(
        "ansibleguard.smells.scan_with_gitleaks_file_output", lambda *a, **kw: []
    )
    monkeypatch.setattr("ansibleguard.smells.run_ansible_lint", lambda *a, **kw: [])

    thresholds = read_thresholds()
    txt_output = tmp_path / "Play_Level_Analysis.txt"

    # The exact crash condition: task special_chars below threshold, so
    # evaluation must fall through to the play-level check.
    metrics = _make_metrics(task_special_chars=0, play_special_chars=5)
    result, _, _ = assess_code_smells(metrics, thresholds, txt_output, "fake.yml")
    assert result["playbook"]["metrics"]["inconsistent_naming_convention"] == 1, (
        "Play-level special_chars exceeding threshold should flag "
        "inconsistent_naming_convention even when the task's own "
        "special_chars doesn't -- this is the exact case that used to crash"
    )


def test_play_level_special_chars_short_circuit_path_unaffected(tmp_path, monkeypatch):
    """The path that never crashed before (task's own special_chars already
    exceeds threshold, short-circuiting before the buggy line) must still
    correctly flag the smell after the fix -- no regression."""
    monkeypatch.setattr(
        "ansibleguard.smells.scan_with_gitleaks_file_output", lambda *a, **kw: []
    )
    monkeypatch.setattr("ansibleguard.smells.run_ansible_lint", lambda *a, **kw: [])

    thresholds = read_thresholds()
    txt_output = tmp_path / "Play_Level_Analysis.txt"

    metrics = _make_metrics(task_special_chars=5, play_special_chars=0)
    result, _, _ = assess_code_smells(metrics, thresholds, txt_output, "fake.yml")
    assert result["playbook"]["metrics"]["inconsistent_naming_convention"] == 1


def test_play_level_special_chars_clean_negative_case(tmp_path, monkeypatch):
    """Neither task nor play special_chars exceed threshold -> must not
    flag the smell, and must not crash."""
    monkeypatch.setattr(
        "ansibleguard.smells.scan_with_gitleaks_file_output", lambda *a, **kw: []
    )
    monkeypatch.setattr("ansibleguard.smells.run_ansible_lint", lambda *a, **kw: [])

    thresholds = read_thresholds()
    txt_output = tmp_path / "Play_Level_Analysis.txt"

    metrics = _make_metrics(task_special_chars=0, play_special_chars=0)
    result, _, _ = assess_code_smells(metrics, thresholds, txt_output, "fake.yml")
    assert result["playbook"]["metrics"]["inconsistent_naming_convention"] == 0
