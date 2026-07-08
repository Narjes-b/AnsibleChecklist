from ansibleguard.external.gitleaks import scan_with_gitleaks_file_output


def test_missing_gitleaks_binary_degrades_gracefully(fixtures_dir):
    """Regression test: a missing/misconfigured gitleaks binary path used
    to raise an unguarded FileNotFoundError from subprocess.run(). Matters
    specifically for a CI/PR-bot context — a runner without gitleaks
    pre-installed must not crash the whole check, just skip this one
    finding gracefully."""
    fixture = fixtures_dir / "gitleaks_dummy_playbook.yml"
    result = scan_with_gitleaks_file_output(
        str(fixture), "/nonexistent/path/to/gitleaks"
    )
    assert result == []


def test_nonexistent_target_path_does_not_crash(fixtures_dir):
    """A bad --source path was already handled before this session's fixes
    (gitleaks itself exits non-zero, existing 'else' branch returns []) —
    locking that in so a future edit can't silently regress it."""
    import shutil

    gitleaks_path = shutil.which("gitleaks") or "./gitleaks-bin/gitleaks"
    result = scan_with_gitleaks_file_output("/nonexistent/playbook.yml", gitleaks_path)
    assert result == []
