from ansibleguard.detectors.unnecessary_abs import unecessary_abs


def test_empty_file_returns_zero_not_crash(fixtures_dir):
    """Regression test: an empty YAML file parses to None via
    yaml.safe_load(). The old code had no None guard before iterating
    'for play in playbook', crashing with
    TypeError: 'NoneType' object is not iterable."""
    fixture = fixtures_dir / "unecessary_abs_empty.yml"
    assert unecessary_abs(str(fixture)) == 0


def test_rescue_nested_block_counted(fixtures_dir):
    """v0.0.4: outer block has rescue: so it is NOT unnecessary (rescue provides
    error-boundary semantics that cannot be expressed on the single task directly).
    Only the inner 'fallback wrapper' block (no justifying keys, single task) is
    flagged — count is 1, not 2."""
    fixture = fixtures_dir / "unecessary_abs_rescue_nested.yml"
    assert unecessary_abs(str(fixture)) == 1
