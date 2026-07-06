"""Regression tests for two bugs found via real-world CLI testing against
a downloaded third-party Ansible project (large-ansible/small-ansible,
group_vars/tomcat.yml specifically) -- neither was caught by any hand-built
fixture all session, because our own fixtures never happened to combine
"a non-playbook file" with "real, nonzero high_coupling data" at once."""

import pytest
from smellsDetector import assess_code_smells


def _base_metrics(playbook_metrics=None, high_coupling_metrics=None, **overrides):
    """Minimal shape matching what parser_playbook.mainn() actually returns."""
    metrics = {
        "playbook_metrics": playbook_metrics,
        "high_coupling_metrics": high_coupling_metrics,
        "similarity": None,
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
        "plays": [{"play_metrics": None, "unnamed_play": None, "task_metrics": []}],
    }
    metrics.update(overrides)
    return metrics


def test_none_playbook_metrics_does_not_crash(tmp_path, monkeypatch):
    """Bug 1: metrics.get('playbook_metrics', {}) doesn't substitute the
    default when the key exists with value None -- exactly what mainn()
    returns for any non-playbook file (vars files, meta files, etc). This
    crashed on the very first playbook_metrics.get(...) call afterward."""
    monkeypatch.setattr(
        "smellsDetector.scan_with_gitleaks_file_output", lambda *a, **k: []
    )
    monkeypatch.setattr("smellsDetector.run_ansible_lint", lambda *a, **k: [])

    metrics = _base_metrics(playbook_metrics=None, high_coupling_metrics=None)
    thresholds = {"LOC_playbook": 110, "num_plays": 4, "similarity": 0.4}
    txt_file = tmp_path / "out.txt"

    result, findings, lint_results = assess_code_smells(
        metrics, thresholds, txt_file, str(tmp_path / "fake.yml")
    )
    assert result["playbook"]["metrics"]["large_playbook"] == 0
    assert result["playbook"]["metrics"]["complex_playbook"] == 0
    assert result["playbook"]["metrics"]["high_coupling"] == 0


def test_high_coupling_reads_from_correct_dict(tmp_path, monkeypatch):
    """Bug 2: Num_Imports/Num_Roles were being read from playbook_metrics,
    which never contains those keys at all -- they live in the separate
    high_coupling_metrics dict. This meant High Playbook Coupling (and half
    of Complex Playbook's conditions) could never fire, for any file,
    regardless of real coupling data, for the whole session -- invisible
    because our main fixture happened to genuinely have zero imports/roles."""
    monkeypatch.setattr(
        "smellsDetector.scan_with_gitleaks_file_output", lambda *a, **k: []
    )
    monkeypatch.setattr("smellsDetector.run_ansible_lint", lambda *a, **k: [])

    metrics = _base_metrics(
        playbook_metrics={
            "LOC_playbook": 10, "num_plays": 1, "avg_play_size": 10,
            "num_nested_tasks_playbook": 1, "avg_nested_task_playbook": 1,
            "num_global_tasks_playbook": 0,
        },
        high_coupling_metrics={"Num_Imports": 10, "Num_Roles": 10},
    )
    thresholds = {
        "LOC_playbook": 110, "num_plays": 4, "avg_play_size": 50,
        "num_tasks_playbook": 15, "Num_Imports": 4, "Num_Roles": 5,
        "similarity": 0.4,
    }
    txt_file = tmp_path / "out.txt"

    result, findings, lint_results = assess_code_smells(
        metrics, thresholds, txt_file, str(tmp_path / "fake.yml")
    )
    assert result["playbook"]["metrics"]["high_coupling"] == 1
    assert result["playbook"]["metrics"]["complex_playbook"] == 1
