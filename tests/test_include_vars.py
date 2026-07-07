from include_vars import detect_unused_include_vars


def test_non_list_yaml_returns_tuple_not_bare_int(fixtures_dir):
    """Regression test: the dict-not-list early-return path returned a
    bare 0 instead of (0, []) like every other path in the function.
    parser_playbook.py always unpacks two values
    (unused_include_vars, WarningUnusedIncludeVars = ...), so this crashed
    with TypeError: cannot unpack non-iterable int object on any non-list
    top-level YAML (dict-shaped vars files, vault-encrypted files)."""
    fixture = fixtures_dir / "include_vars_not_a_list.yml"
    result = detect_unused_include_vars(str(fixture))
    count, warnings = result
    assert count == 0
    assert warnings == []
