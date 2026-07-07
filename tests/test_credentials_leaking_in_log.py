from credentials_leaking_in_log import detect_credentials_leaking_in_log


def test_credential_in_normal_play_detected(fixtures_dir):
    """Regression test for the highest-severity bug this session: the old
    code read top_level_tasks (only tasks outside any play — rare) instead
    of the full recursive task list, so it was silently blind to
    credentials sitting in ordinary hosts:/tasks: plays, the vast majority
    of real playbooks."""
    fixture = fixtures_dir / "credentials_nested_in_play.yml"
    warnings, count, _details = detect_credentials_leaking_in_log(str(fixture))
    assert count == 1


def test_no_log_true_suppresses_warning(fixtures_dir):
    """Confirms the detector isn't just flagging every set_fact — a task
    that correctly uses no_log: true must NOT be flagged."""
    fixture = fixtures_dir / "credentials_with_no_log.yml"
    warnings, count, _details = detect_credentials_leaking_in_log(str(fixture))
    assert count == 0


def test_credential_nested_in_block_detected(fixtures_dir):
    """Confirms detection still works when the sensitive task is nested
    inside a block:, not just a direct child of tasks:."""
    fixture = fixtures_dir / "credentials_nested_in_block.yml"
    warnings, count, _details = detect_credentials_leaking_in_log(str(fixture))
    assert count == 1
