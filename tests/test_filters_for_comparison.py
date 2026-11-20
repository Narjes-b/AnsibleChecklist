from ansibleguard.detectors.filters_for_comparison import get_when_conditions


def test_bare_boolean_when_does_not_crash(fixtures_dir):
    """Regression test: when: true is a literal Python bool once parsed
    by PyYAML, not a string. The old code called re.split() directly on
    condition_str, raising TypeError: expected string or bytes-like
    object. A bare boolean is never itself a 'missing | bool filter'
    issue, so the correct result is 0 findings, not a crash."""
    fixture = fixtures_dir / "filters_bare_bool_when.yml"
    assert get_when_conditions(str(fixture)) == 0


def test_quoted_boolean_comparison_nested_in_rescue_detected(fixtures_dir):
    """Regression test for rescue/always recursion: a quoted Boolean
    comparison inside rescue must still be flagged without guessing the type
    of valid bare-variable conditions."""
    fixture = fixtures_dir / "filters_missing_bool_rescue.yml"
    assert get_when_conditions(str(fixture)) == 1


def test_null_tasks_is_a_valid_empty_task_section(tmp_path):
    playbook = tmp_path / "null-tasks.yml"
    playbook.write_text(
        "---\n- name: Empty test play\n  hosts: localhost\n  tasks:\n",
        encoding="utf-8",
    )

    assert get_when_conditions(str(playbook)) == 0
