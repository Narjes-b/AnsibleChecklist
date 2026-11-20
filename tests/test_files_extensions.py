from ansibleguard.detectors.files_extensions import extract_tasks_from_playbook


def test_missing_extension_nested_in_rescue_detected_once(fixtures_dir):
    """Regression test: the old version was missing rescue/always
    recursion and had a separate triple-count bug. Here an extensionless
    include_tasks reference sits inside a rescue: block. Expect exactly 1
    missing-extension finding — found once
    (recursion works), not zero (recursion missing) and not 3
    (triple-count bug)."""
    fixture = fixtures_dir / "files_ext_rescue.yml"
    assert extract_tasks_from_playbook(str(fixture)) == 1


def test_all_extensions_present_returns_zero(fixtures_dir):
    fixture = fixtures_dir / "files_ext_all_present.yml"
    assert extract_tasks_from_playbook(str(fixture)) == 0


def test_null_tasks_is_a_valid_empty_task_section(tmp_path):
    playbook = tmp_path / "null-tasks.yml"
    playbook.write_text(
        "---\n- name: Empty test play\n  hosts: localhost\n  tasks:\n",
        encoding="utf-8",
    )

    assert extract_tasks_from_playbook(str(playbook)) == 0
