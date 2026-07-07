from ansibleguard.detectors.files_extensions import extract_tasks_from_playbook


def test_missing_extension_nested_in_rescue_detected_once(fixtures_dir):
    """Regression test: the old version was missing rescue/always
    recursion and had a separate triple-count bug. Here 'src: myfile'
    (no extension) sits inside a rescue: block; 'dest' already has a real
    extension. Expect exactly 1 missing-extension finding — found once
    (recursion works), not zero (recursion missing) and not 3
    (triple-count bug)."""
    fixture = fixtures_dir / "files_ext_rescue.yml"
    assert extract_tasks_from_playbook(str(fixture)) == 1


def test_all_extensions_present_returns_zero(fixtures_dir):
    fixture = fixtures_dir / "files_ext_all_present.yml"
    assert extract_tasks_from_playbook(str(fixture)) == 0
