from ansibleguard.detectors.detect_large_playbook import calculate_metrics_playbook


def test_task_only_file_does_not_crash(fixtures_dir):
    """Regression test: calculate_metrics_play() returns None for a
    task-only file (no hosts:/tasks: wrapper anywhere). The old code did
    `for play in plays['Plays']` with no None guard, crashing with
    TypeError: 'NoneType' object is not subscriptable on exactly this
    file shape — which is also the shape of a typical role's
    tasks/main.yml, the most common real-world fixture type."""
    fixture = fixtures_dir / "large_task_only_no_play.yml"
    result = calculate_metrics_playbook(str(fixture))
    assert result is not None
    assert result["num_plays"] == 0
