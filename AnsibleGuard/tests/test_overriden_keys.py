from overriden_keys import detect_duplicate_keys_per_task


def test_cross_depth_name_not_a_false_positive(fixtures_dir):
    """Regression test: a task's own 'name:' (e.g. '- name: task4') and an
    unrelated nested module parameter also called 'name:' (e.g.
    apt: {name: nginx}) sit at different structural depths and must NOT be
    reported as the same duplicated key. The buggy version tracked
    (depth, key) correctly during collection but discarded depth right
    before the duplicate check, re-merging them."""
    fixture = fixtures_dir / "overriden_keys_cross_depth.yml"
    result = detect_duplicate_keys_per_task(str(fixture))
    assert result == []


def test_real_same_depth_duplicate_still_caught(fixtures_dir):
    """A genuine duplicate at the same structural depth must still be
    detected — confirms the depth-fix didn't overcorrect into blindness."""
    fixture = fixtures_dir / "overriden_keys_same_depth.yml"
    result = detect_duplicate_keys_per_task(str(fixture))
    assert len(result) == 1
    assert "name" in result[0]["duplicates"]


def test_multiple_keys_each_duplicated(fixtures_dir):
    """Mirrors main3.yml's real task8: several different keys, each
    duplicated, all within one task — confirms multi-key detection still
    works correctly after the depth-bucket rewrite."""
    fixture = fixtures_dir / "overriden_keys_multi_key.yml"
    result = detect_duplicate_keys_per_task(str(fixture))
    assert len(result) == 1
    assert "src" in result[0]["duplicates"]
    assert "dest" in result[0]["duplicates"]
