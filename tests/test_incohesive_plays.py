from ansibleguard.detectors.incohesive_plays import calculate_similarity


def test_nonenglish_task_names_not_falsely_incohesive(fixtures_dir):
    """Direct coverage for incohesive_plays.py itself (previously only
    exercised indirectly via detect_large_play.py's tests). Confirms the
    all-OOV-names case correctly returns 0 (unmeasurable play skipped,
    counted toward neither cohesive nor incohesive) rather than a false
    positive on either side.

    Note: unlike sem_cohesion.py, this function only ever compares task
    names to each other within one play — it never mixes in a play-name
    vector comparison, so the 'shared counter masks the other group'
    follow-up bug found in sem_cohesion.py cannot occur here structurally.
    Confirmed by reading the function: 'playname' is extracted only for
    the warning message text, never passed through nlp()."""
    fixture = fixtures_dir / "incohesive_plays_nonenglish_tasks.yml"
    result = calculate_similarity(str(fixture))
    assert result == 0


def test_unnamed_task_does_not_crash_cohesion_analysis(tmp_path):
    playbook = tmp_path / "unnamed-task.yml"
    playbook.write_text(
        "---\n"
        "- name: Test play\n"
        "  hosts: localhost\n"
        "  tasks:\n"
        "    - name:\n"
        "      debug:\n"
        "        msg: hello\n",
        encoding="utf-8",
    )

    assert calculate_similarity(str(playbook)) == 0
