from ansibleguard.detectors.detect_large_play import calculate_metrics_play


def test_block_recursion_matches_detect_large_task(fixtures_dir):
    """The core bug this session: detect_large_play.py counted a block
    wrapper as one task using its own name, while detect_large_task.py
    recursed into the block and only recorded the children. For the same
    play, num_tasks_in_play/tasks_names must now describe the same set of
    tasks calculate_metrics_task() does — real leaf tasks, not wrapper
    labels."""
    fixture = fixtures_dir / "large_task_block_consistency.yml"
    result = calculate_metrics_play(str(fixture))
    play = result["Plays"][0]
    assert play["num_tasks_in_play"] == 2
    assert play["tasks_names"] == ["task4", "task5"]


def test_non_list_yaml_returns_none(fixtures_dir):
    """A vault-encrypted (string-shaped) file must not crash — should
    return None, matching the already-correct guard this file had before
    the block-recursion fix was even needed."""
    fixture = fixtures_dir / "vault_encrypted_full.yml"
    result = calculate_metrics_play(str(fixture))
    assert result is None
