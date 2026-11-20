import pytest

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


def test_ansible_lint_timeout_is_not_clean(monkeypatch):
    import subprocess

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            subprocess.TimeoutExpired(args[0], kwargs.get("timeout"))
        ),
    )

    result = scan_with_ansible_lint("playbook.yml", timeout=0.01)

    assert result.status == "timeout"
    assert result.findings == []
    assert result.metadata["failure_category"] == "TIMEOUT"


def test_ansible_lint_output_limit_is_not_clean(monkeypatch):
    import json
    import subprocess

    monkeypatch.setenv("ANSIBLEGUARD_PROVIDER_MAX_OUTPUT_BYTES", "10")
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda command, **kwargs: subprocess.CompletedProcess(
            command, 0, json.dumps([{"check_name": "yaml[truthy]"}]), ""
        ),
    )

    result = scan_with_ansible_lint("playbook.yml")

    assert result.status == "tool-error"
    assert result.metadata["failure_category"] == "OUTPUT_LIMIT"


def test_mixed_schema_payload_is_partial_and_does_not_crash(tmp_path, monkeypatch):
    import json
    import subprocess

    target = tmp_path / "project"
    target.mkdir()
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda command, **kwargs: subprocess.CompletedProcess(
            command,
            0,
            json.dumps(["adapter noise", {"check_name": "yaml[truthy]", "path": "site.yml"}]),
            "",
        ),
    )

    result = scan_with_ansible_lint(target)

    assert result.status == "partial"
    assert len(result.findings) == 1
    assert result.metadata["provider_diagnostics"][0]["category"] == "PROVIDER_SCHEMA_ERROR"


@pytest.mark.parametrize(
    "malformed",
    (
        {"location": "broken"},
        {"location": []},
        {"location": {"positions": "broken"}},
        {"location": {"positions": {"begin": "broken"}}},
        {"line": "banana"},
        {"path": {"unexpected": "object"}},
    ),
)
def test_nested_malformed_schema_is_partial_diagnostic(
    tmp_path, monkeypatch, malformed
):
    import json
    import subprocess

    target = tmp_path / "project"
    target.mkdir()
    payload = [
        {"check_name": "yaml[truthy]", "path": "valid.yml"},
        {"check_name": "yaml[truthy]", **malformed},
    ]
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda command, **kwargs: subprocess.CompletedProcess(
            command, 0, json.dumps(payload), ""
        ),
    )

    result = scan_with_ansible_lint(target)

    assert result.status == "partial"
    assert len(result.findings) == 1
    assert len(result.metadata["provider_diagnostics"]) == 1
    assert result.metadata["provider_diagnostics"][0]["category"] == (
        "PROVIDER_SCHEMA_ERROR"
    )
    diagnostic = result.metadata["provider_diagnostics"][0]
    assert diagnostic["index"] == 1
    assert diagnostic["json_root_type"] == "list"
    assert diagnostic["provider_root"] == str(target.resolve())
    assert "item_preview" in diagnostic


def test_nonzero_environment_failure_with_invalid_json_has_one_primary_cause(
    tmp_path, monkeypatch
):
    import subprocess

    target = tmp_path / "project"
    target.mkdir()
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda command, **kwargs: subprocess.CompletedProcess(
            command, 3, "not json", "log directory is not writeable"
        ),
    )

    result = scan_with_ansible_lint(target)

    assert result.status == "tool-error"
    assert len(result.metadata["provider_diagnostics"]) == 1
    diagnostic = result.metadata["provider_diagnostics"][0]
    assert diagnostic["category"] == "PROVIDER_ERROR"
    assert diagnostic["returncode"] == 3
    assert diagnostic["exception_type"] == "JSONDecodeError"
    assert "not writeable" in diagnostic["message"]


def test_internal_error_is_provider_diagnostic_not_smell(tmp_path, monkeypatch):
    import json
    import subprocess

    target = tmp_path / "project"
    target.mkdir()
    payload = [{"check_name": "internal-error", "message": "provider exploded"}]
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda command, **kwargs: subprocess.CompletedProcess(
            command, 0, json.dumps(payload), ""
        ),
    )

    result = scan_with_ansible_lint(target)

    assert result.status == "partial"
    assert result.findings == []
    assert result.metadata["provider_diagnostics"][0]["category"] == "PROVIDER_ERROR"


def test_syntax_check_keeps_environment_provenance(tmp_path, monkeypatch):
    import json
    import subprocess

    target = tmp_path / "project"
    target.mkdir()
    payload = [{"check_name": "syntax-check[unknown-module]", "path": "site.yml"}]
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda command, **kwargs: subprocess.CompletedProcess(
            command, 2, json.dumps(payload), ""
        ),
    )

    result = scan_with_ansible_lint(target)

    assert result.findings[0]["analysis_population"] == (
        "environment_dependent_provider_finding"
    )


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
    assert captured["command"][1] == "--offline"
    assert "--offline" in captured["command"]
    assert result.metadata["cwd"] == str(target.resolve())
    assert result.metadata["target"] == "<project-discovery>"
    assert result.metadata["dependency_mode"] == "offline-no-auto-install"


def test_ansible_lint_uses_explicit_disjoint_population_with_project_cwd(
    tmp_path, monkeypatch
):
    import json
    import subprocess

    target = tmp_path / "project"
    selected = target / "site.yml"
    excluded = target / "nested" / "tasks.yml"
    excluded.parent.mkdir(parents=True)
    selected.write_text("- debug: {msg: ok}\n", encoding="utf-8")
    excluded.write_text("- debug: {msg: nested}\n", encoding="utf-8")
    captured = {}

    def fake_run(command, **kwargs):
        captured["command"] = command
        captured["cwd"] = kwargs["cwd"]
        return subprocess.CompletedProcess(command, 0, json.dumps([]), "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = scan_with_ansible_lint(target, files=[selected])

    assert result.status == "completed"
    assert captured["cwd"] == target.resolve()
    assert "site.yml" in captured["command"]
    assert "nested/tasks.yml" not in captured["command"]
    assert result.metadata["target"] == ["site.yml"]
    assert result.metadata["explicit_population"] is True


def test_nested_provider_root_uses_nearest_ancestor_ansible_lint_config(
    tmp_path, monkeypatch
):
    import json
    import subprocess

    checkout = tmp_path / "project"
    provider_root = checkout / "ansible"
    selected = provider_root / "site.yml"
    selected.parent.mkdir(parents=True)
    (checkout / ".git").mkdir()
    config = checkout / ".ansible-lint"
    config.write_text("skip_list: [yaml]\n", encoding="utf-8")
    selected.write_text("- hosts: all\n  tasks: []\n", encoding="utf-8")
    captured = {}

    def fake_run(command, **kwargs):
        captured["command"] = command
        captured["cwd"] = kwargs["cwd"]
        return subprocess.CompletedProcess(command, 0, json.dumps([]), "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = scan_with_ansible_lint(provider_root, files=[selected])

    assert result.status == "completed"
    assert captured["cwd"] == provider_root.resolve()
    assert captured["command"][captured["command"].index("-c") + 1] == str(config)
    assert result.metadata["config"] == str(config)


def test_nested_provider_root_prefers_its_independent_config(tmp_path, monkeypatch):
    import json
    import subprocess

    checkout = tmp_path / "project"
    provider_root = checkout / "ansible"
    provider_root.mkdir(parents=True)
    (checkout / ".git").mkdir()
    (checkout / ".ansible-lint").write_text("skip_list: [yaml]\n")
    nested_config = provider_root / ".ansible-lint"
    nested_config.write_text("warn_list: [yaml]\n")
    captured = {}

    def fake_run(command, **kwargs):
        captured["command"] = command
        return subprocess.CompletedProcess(command, 0, json.dumps([]), "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = scan_with_ansible_lint(provider_root)

    assert result.status == "completed"
    assert captured["command"][captured["command"].index("-c") + 1] == str(
        nested_config
    )


def test_directory_scan_discovers_playbooks_instead_of_linting_dot(tmp_path):
    target = tmp_path / "project"
    target.mkdir()
    (target / ".git").mkdir()
    (target / ".ansible-lint").write_text(
        "---\nenable_list:\n  - no-log-password\n",
        encoding="utf-8",
    )
    (target / "site.yml").write_text(
        "---\n"
        "- name: Discovery regression\n"
        "  hosts: localhost\n"
        "  gather_facts: false\n"
        "  tasks:\n"
        "    - name: Configure loop accounts\n"
        "      ansible.builtin.user:\n"
        "        name: '{{ item.name }}'\n"
        "        password: '{{ item.password }}'\n"
        "      loop:\n"
        "        - name: example\n"
        "          password: '{{ example_password }}'\n"
        "      no_log: false\n",
        encoding="utf-8",
    )

    result = scan_with_ansible_lint(target)

    assert result.status == "completed"
    assert any(
        issue.get("check_name") == "no-log-password"
        for issue in result.findings
    )


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


def test_read_only_command_instead_of_module_is_suppressed_with_evidence(
    tmp_path, monkeypatch
):
    import json
    import subprocess

    target = tmp_path / "project"
    target.mkdir()
    (target / "site.yml").write_text(
        "- name: Inspect host name\n  command: hostname\n",
        encoding="utf-8",
    )
    payload = [{
        "check_name": "command-instead-of-module",
        "location": {"path": "site.yml", "line": 1},
        "message": "hostname used in place of module",
    }]
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda command, **kwargs: subprocess.CompletedProcess(
            command, 2, json.dumps(payload), ""
        ),
    )

    result = scan_with_ansible_lint(target)

    assert result.findings == []
    assert result.metadata["suppressed_read_only_command_findings"] == 1
    assert result.suppressed_findings[0]["reason"] == (
        "read-only-command-has-no-state-module-migration"
    )


def test_mutating_command_instead_of_module_is_retained(tmp_path, monkeypatch):
    import json
    import subprocess

    target = tmp_path / "project"
    target.mkdir()
    (target / "site.yml").write_text(
        "- name: Restart service\n  command: systemctl restart nginx\n",
        encoding="utf-8",
    )
    payload = [{
        "check_name": "command-instead-of-module",
        "location": {"path": "site.yml", "line": 1},
        "message": "systemctl used in place of module",
    }]
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda command, **kwargs: subprocess.CompletedProcess(
            command, 2, json.dumps(payload), ""
        ),
    )

    result = scan_with_ansible_lint(target)

    assert len(result.findings) == 1
    assert result.suppressed_findings == []
