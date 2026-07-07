from ansibleguard.detectors.unnecessary_abs import unecessary_abs


def test_empty_file_returns_zero_not_crash(fixtures_dir):
    """Regression test: an empty YAML file parses to None via
    yaml.safe_load(). The old code had no None guard before iterating
    'for play in playbook', crashing with
    TypeError: 'NoneType' object is not iterable."""
    fixture = fixtures_dir / "unecessary_abs_empty.yml"
    assert unecessary_abs(str(fixture)) == 0


def test_rescue_nested_block_counted(fixtures_dir):
    """Two genuine single-task blocks here: 'risky task's own block
    (wraps 1 task: 'do the thing'), and 'fallback wrapper's block nested
    inside rescue: (wraps 1 task: 'only one task'). The old code never
    recursed into a block nested inside another block or inside rescue/
    always at all, so this would previously undercount."""
    fixture = fixtures_dir / "unecessary_abs_rescue_nested.yml"
    assert unecessary_abs(str(fixture)) == 2
