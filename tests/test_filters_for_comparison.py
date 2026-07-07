from ansibleguard.detectors.filters_for_comparison import get_when_conditions


def test_bare_boolean_when_does_not_crash(fixtures_dir):
    """Regression test: when: true is a literal Python bool once parsed
    by PyYAML, not a string. The old code called re.split() directly on
    condition_str, raising TypeError: expected string or bytes-like
    object. A bare boolean is never itself a 'missing | bool filter'
    issue, so the correct result is 0 findings, not a crash."""
    fixture = fixtures_dir / "filters_bare_bool_when.yml"
    assert get_when_conditions(str(fixture)) == 0


def test_missing_bool_filter_nested_in_rescue_detected(fixtures_dir):
    """Regression test for missing rescue/always recursion: 'when:
    some_var' with no comparison and no | bool filter, sitting inside a
    rescue: block, must still be flagged."""
    fixture = fixtures_dir / "filters_missing_bool_rescue.yml"
    assert get_when_conditions(str(fixture)) == 1
