from unnamed_play import unnamed_play


def test_hosts_only_play_with_no_tasks_key_counted(fixtures_dir):
    """Regression test: the old condition was
    'hosts' in item AND 'tasks' in item — every other play-detection
    function in the codebase uses OR. A play with only hosts: (no tasks:)
    was invisible to this specific check. Fixed to OR."""
    fixture = fixtures_dir / "unnamed_play_hosts_only.yml"
    assert unnamed_play(str(fixture)) == 1
