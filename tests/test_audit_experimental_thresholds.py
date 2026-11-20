"""Tests for the extended threshold-sensitivity audit.

This is a candidate-rate audit, not a precision estimator (see the
script's own module docstring) -- these tests only verify that each
newly-added metric family is wired to the right underlying metric
function and produces a monotonically non-increasing candidate rate as
the threshold rises, not that any particular threshold is "correct".
"""
from pathlib import Path

from scripts.audit_experimental_thresholds import audit_paths


def _write(tmp_path, name, content):
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return path


def test_large_task_and_long_task_name_candidate_rates(tmp_path):
    path = _write(
        tmp_path,
        "tasks.yml",
        "- name: " + ("x" * 90) + "\n"
        "  debug:\n"
        "    msg: line one\n"
        "    another: line two\n"
        "    more: line three\n"
        "    extra: line four\n"
        "    padding: line five\n"
        "    filler: line six\n"
        "    stuffing: line seven\n"
        "    tail: line eight\n"
        "    end: line nine\n"
        "    last: line ten\n"
        "    more1: eleven\n"
        "    more2: twelve\n"
        "    more3: thirteen\n"
        "    more4: fourteen\n"
        "    more5: fifteen\n"
        "    more6: sixteen\n"
        "    more7: seventeen\n"
        "    more8: eighteen\n"
        "    more9: nineteen\n"
        "    more10: twenty\n"
        "    more11: twentyone\n",
    )
    result = audit_paths([path])
    # A 90-character task name exceeds 75 but not necessarily other bounds.
    assert result["long_task_name_candidate_rates"]["50"] == 1.0
    assert result["long_task_name_candidate_rates"]["75"] == 1.0
    # Rate must never increase as the threshold rises.
    rates = result["long_task_name_candidate_rates"]
    assert rates["50"] >= rates["75"] >= rates["100"]


def test_large_playbook_candidate_rates_are_monotonic(tmp_path):
    plays = "\n".join(
        f"- hosts: all\n  tasks:\n    - name: task {i}\n      debug:\n        msg: hi\n"
        for i in range(6)
    )
    path = _write(tmp_path, "playbook.yml", plays)
    result = audit_paths([path])
    for family in (
        "large_playbook_loc", "large_playbook_num_plays",
        "large_playbook_avg_play_size", "large_playbook_num_tasks",
        "large_playbook_avg_task_size",
    ):
        rates = list(result[f"{family}_candidate_rates"].values())
        assert rates == sorted(rates, reverse=True)


def test_missing_abstraction_candidate_rate_reflects_leaf_task_count(tmp_path):
    many_tasks = "\n".join(
        f"- name: task {i}\n  debug:\n    msg: hi\n" for i in range(12)
    )
    path = _write(tmp_path, "tasks.yml", many_tasks)
    result = audit_paths([path])
    # 12 leaf tasks, no include/role abstraction: candidate at 7 and 10, not at 13.
    assert result["missing_abstraction_candidate_rates"]["7"] == 1.0
    assert result["missing_abstraction_candidate_rates"]["10"] == 1.0
    assert result["missing_abstraction_candidate_rates"]["13"] == 0.0


def test_audit_paths_still_reports_original_families(tmp_path):
    path = _write(tmp_path, "tasks.yml", "- name: hi\n  debug:\n    msg: hi\n")
    result = audit_paths([path])
    assert "high_coupling_candidate_rates" in result
    assert "undocumented_complex_task_candidate_rates" in result
    assert result["files"] == 1
