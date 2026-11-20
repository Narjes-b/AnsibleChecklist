from ansibleguard.detectors.duplicate_task_names import repeated_task_names


def test_duplicate_names_detected(fixtures_dir):
    """Regression test for the tuple-unpacking bug: calculate_metrics_task()
    returns (all_metrics, top_level_tasks); the buggy version assigned the
    whole tuple to one variable, so this always silently returned 0."""
    fixture = fixtures_dir / "duplicate_task_names.yml"
    assert repeated_task_names(str(fixture)) == 1


def test_no_duplicates_returns_zero(fixtures_dir):
    """Negative case — confirms the detector isn't just hardcoded to '1'."""
    fixture = fixtures_dir / "no_duplicate_task_names.yml"
    assert repeated_task_names(str(fixture)) == 0


def test_same_name_in_different_plays_is_not_a_duplicate(tmp_path):
    playbook = tmp_path / "different-plays.yml"
    playbook.write_text(
        "- name: Debian\n  hosts: debian\n  tasks:\n"
        "    - name: Install packages\n      apt: {name: nginx}\n"
        "- name: Red Hat\n  hosts: redhat\n  tasks:\n"
        "    - name: Install packages\n      dnf: {name: nginx}\n",
        encoding="utf-8",
    )
    assert repeated_task_names(playbook) == 0
