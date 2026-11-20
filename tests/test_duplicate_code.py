from ansibleguard.detectors.duplicate_code import duplicate_code


def test_duplicate_named_tasks_detected(fixtures_dir):
    """Two tasks with identical module parameters (name field excluded
    from the comparison on purpose) — this is the real smell: copy-pasted
    task bodies under different names."""
    fixture = fixtures_dir / "duplicate_code_named.yml"
    assert duplicate_code(str(fixture)) == 1


def test_duplicate_unnamed_tasks_now_detected(fixtures_dir):
    """Regression test — this used to be an xfail documenting a known
    limitation: duplicate_code() only scanned tasks with a 'name' key,
    so two unnamed tasks with identical content were invisible. Fixed by
    removing the 'name' requirement entirely (task.pop('name', None) is
    safe whether or not the key exists)."""
    fixture = fixtures_dir / "duplicate_code_unnamed.yml"
    assert duplicate_code(str(fixture)) == 1


def test_duplicate_tasks_nested_in_separate_blocks_detected(fixtures_dir):
    """New coverage: the rewrite added block/rescue/always recursion,
    which the original version never had at all."""
    fixture = fixtures_dir / "duplicate_code_block_nested.yml"
    assert duplicate_code(str(fixture)) == 1


def test_no_duplicates_returns_zero(fixtures_dir):
    fixture = fixtures_dir / "duplicate_code_no_dup.yml"
    assert duplicate_code(str(fixture)) == 0
