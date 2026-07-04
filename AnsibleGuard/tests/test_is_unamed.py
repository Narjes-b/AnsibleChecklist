from is_unamed import is_unnamed


def test_none_is_unnamed():
    assert is_unnamed(None) == 1


def test_empty_string_is_unnamed():
    """Regression test: the old version only checked 'is None', missing
    empty/whitespace strings — inconsistent with unnamed_play.py's own
    (correct) check."""
    assert is_unnamed("") == 1


def test_whitespace_only_is_unnamed():
    assert is_unnamed("   ") == 1


def test_real_name_is_not_unnamed():
    assert is_unnamed("Real name") == 0
