from detect_large_task import calculate_metrics_task


def test_vault_encrypted_file_does_not_crash(fixtures_dir):
    """Regression test: a fully vault-encrypted file parses via
    yaml.safe_load() as a plain string, not a list. The old code's
    isinstance(playbook, list) guard skipped the whole function body
    without ever defining top_level_tasks, so the return statement raised
    UnboundLocalError."""
    fixture = fixtures_dir / "vault_encrypted_full.yml"
    metrics, top_level_tasks = calculate_metrics_task(str(fixture))
    assert metrics == []
    assert top_level_tasks == []


def test_block_wrapper_not_counted_as_its_own_task(fixtures_dir):
    """The block wrapper ('Notconsideredtask3') has no module of its own —
    it never executes — so only its real children (task4, task5) should
    appear in the task metrics."""
    fixture = fixtures_dir / "large_task_block_consistency.yml"
    metrics, _ = calculate_metrics_task(str(fixture))
    names = [t["task_name"] for t in metrics]
    assert names == ["task4", "task5"]


def test_bare_tasks_with_no_play_are_global(fixtures_dir):
    """Tasks with no hosts:/tasks: wrapper around them are 'global' —
    play_id should be -1 for each."""
    fixture = fixtures_dir / "large_task_only_no_play.yml"
    metrics, _ = calculate_metrics_task(str(fixture))
    assert all(t["play_id"] == -1 for t in metrics)
    assert len(metrics) == 2
