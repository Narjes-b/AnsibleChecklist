from smellsDetector import assess_code_smells, read_thresholds


def test_assess_code_smells_uses_the_correct_file_path_for_external_tools(
    tmp_path, monkeypatch
):
    """Regression test for a severe, previously undiscovered bug:
    assess_code_smells() called scan_with_gitleaks_file_output() and
    run_ansible_lint() using a bare 'yaml_file_path' name that was never
    a parameter of this function — Python silently resolved it to the
    module-level global imported from config.py, so EVERY file this
    pipeline ever processed had its hardcoded_credentials and
    ansible_lint_issues ('Design Smells' column) computed against
    whatever config.yaml_file_path happened to be, not the actual file
    being analyzed. Confirmed the bug affected the real production call
    path (execute_for_single_file never passed the path through either).
    Fixed by making yaml_file_path an explicit required 4th parameter.
    """
    calls = {"gitleaks": [], "lint": []}

    def fake_gitleaks(path, gitleaks_path):
        calls["gitleaks"].append(path)
        return []

    def fake_lint(path, **kwargs):
        calls["lint"].append(path)
        return []

    monkeypatch.setattr("smellsDetector.scan_with_gitleaks_file_output", fake_gitleaks)
    monkeypatch.setattr("smellsDetector.run_ansible_lint", fake_lint)

    thresholds = read_thresholds()

    assess_code_smells({}, thresholds, str(tmp_path / "out1.txt"), "FILE_A.yml")
    assess_code_smells({}, thresholds, str(tmp_path / "out2.txt"), "FILE_B.yml")

    assert calls["gitleaks"] == ["FILE_A.yml", "FILE_B.yml"], (
        f"BUG REGRESSED — same path reused across files: {calls['gitleaks']}"
    )
    assert calls["lint"] == ["FILE_A.yml", "FILE_B.yml"], (
        f"BUG REGRESSED — same path reused across files: {calls['lint']}"
    )
