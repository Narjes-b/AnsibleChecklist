from ansibleguard.external.ansible_lint import run_ansible_lint


def test_clean_playbook_returns_no_findings(fixtures_dir):
    fixture = fixtures_dir / "ansible_lint_clean.yml"
    result = run_ansible_lint(str(fixture))
    assert result == []


def test_playbook_with_issues_returns_findings(fixtures_dir):
    fixture = fixtures_dir / "ansible_lint_with_issues.yml"
    result = run_ansible_lint(str(fixture))
    assert len(result) >= 1


def test_nonexistent_target_does_not_crash(fixtures_dir):
    """Confirmed clean: ansible-lint reports a missing target as
    structured load-failure findings rather than raising — this test just
    locks in 'never crashes, always returns a list'."""
    fixture = fixtures_dir / "does_not_exist.yml"
    result = run_ansible_lint(str(fixture))
    assert isinstance(result, list)


def test_missing_binary_degrades_to_empty_list(fixtures_dir, monkeypatch):
    """Simulates ansible-lint not being installed at all — the subprocess
    call raises FileNotFoundError, and run_ansible_lint's broad
    except Exception must catch it and return [] rather than crashing the
    whole pipeline."""
    import subprocess

    def fake_run(cmd, **kwargs):
        if cmd[0] == "ansible-lint":
            raise FileNotFoundError("No such file or directory: ansible-lint")
        return subprocess.run(cmd, **kwargs)

    monkeypatch.setattr(subprocess, "run", fake_run)

    fixture = fixtures_dir / "ansible_lint_clean.yml"
    result = run_ansible_lint(str(fixture))
    assert result == []
