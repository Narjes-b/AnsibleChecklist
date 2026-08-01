from ansibleguard.external.ansible_lint import (
    lint_issue_line,
    run_ansible_lint,
    scan_with_ansible_lint,
)


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
    monkeypatch.setattr(
        "ansibleguard.external.ansible_lint._ansible_lint_executable",
        lambda: "ansible-lint",
    )

    fixture = fixtures_dir / "ansible_lint_clean.yml"
    result = run_ansible_lint(str(fixture))
    assert result == []


def test_real_nested_position_schema_produces_line_number():
    issue = {
        "location": {
            "path": "tasks/main.yml",
            "positions": {"begin": {"line": 23, "column": 3}},
        }
    }
    assert lint_issue_line(issue) == 23


def test_real_nested_lines_schema_produces_line_number():
    issue = {"location": {"path": "tasks/main.yml", "lines": {"begin": 7}}}
    assert lint_issue_line(issue) == 7


def test_structured_lint_result_distinguishes_missing_binary(monkeypatch):
    def missing(*args, **kwargs):
        raise FileNotFoundError("ansible-lint missing")

    monkeypatch.setattr("subprocess.run", missing)
    result = scan_with_ansible_lint("playbook.yml")
    assert result.status == "tool-error"
    assert "missing" in result.message


def test_ansible_lint_runs_from_scanned_project_root(tmp_path, monkeypatch):
    import json
    import subprocess

    target = tmp_path / "project"
    target.mkdir()
    (target / "site.yml").write_text("- debug:\n    msg: ok\n", encoding="utf-8")
    captured = {}

    def fake_run(command, **kwargs):
        captured["command"] = command
        captured["cwd"] = kwargs["cwd"]
        return subprocess.CompletedProcess(command, 0, json.dumps([]), "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = scan_with_ansible_lint(target)
    assert result.status == "completed"
    assert captured["cwd"] == target.resolve()
    assert captured["command"][1] == "."
    assert "--offline" in captured["command"]
    assert result.metadata["cwd"] == str(target.resolve())
    assert result.metadata["dependency_mode"] == "offline-no-auto-install"


def test_ansible_lint_identity_is_stable_outside_checkout_root(tmp_path, monkeypatch):
    import hashlib
    import json
    import subprocess

    target = tmp_path / "base-worktree"
    target.mkdir()
    source = target / "molecule" / "default" / "converge.yml"
    message = f"Role not found in {target}/molecule/default/roles"
    payload = [
        {
            "location": {
                "path": str(source),
                "positions": {"begin": {"line": 6, "column": 1}},
            },
            "check_name": "syntax-check[specific]",
            "message": message,
            "fingerprint": "checkout-specific-native-value",
        }
    ]

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda command, **kwargs: subprocess.CompletedProcess(
            command, 2, json.dumps(payload), ""
        ),
    )
    issue = scan_with_ansible_lint(target).findings[0]
    expected_identity = (
        "syntax-check[specific]|molecule/default/converge.yml|6|"
        "Role not found in <repo>/molecule/default/roles"
    )

    assert issue["location"]["path"] == "molecule/default/converge.yml"
    assert issue["message"] == "Role not found in <repo>/molecule/default/roles"
    assert issue["fingerprint"] == hashlib.sha256(
        expected_identity.encode("utf-8")
    ).hexdigest()
