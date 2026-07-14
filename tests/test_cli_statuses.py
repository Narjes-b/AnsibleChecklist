import json

from ansibleguard.cli import analyze_path
from ansibleguard.external.gitleaks import ToolResult


def test_parse_failure_still_emits_gitleaks_finding(tmp_path, monkeypatch):
    target = tmp_path / "project"
    target.mkdir()
    broken = target / "vars.yaml"
    broken.write_text('password: "AKIAIOSFODNN7EXAMPLE"\nbroken: [yaml\n')

    fake = ToolResult(
        "completed",
        [{"File": "vars.yaml", "StartLine": 1, "Description": "AWS key"}],
    )
    monkeypatch.setattr(
        "ansibleguard.external.gitleaks.scan_with_gitleaks", lambda *a, **k: fake
    )
    monkeypatch.setattr(
        "ansibleguard.external.ansible_lint.scan_with_ansible_lint",
        lambda *a, **k: ToolResult("completed"),
    )

    output = tmp_path / "output"
    run = analyze_path(target, output)

    assert run["discovered"] == 1
    assert run["structurally_analyzed"] == 0
    findings = json.loads((output / "findings.json").read_text())
    assert findings[0]["rule_id"] == "hardcoded-credentials"
    summary = (output / "summary.csv").read_text()
    assert "invalid,unknown,skipped,completed,completed" in summary


def test_tool_failure_is_not_reported_as_clean_scan(tmp_path, monkeypatch):
    target = tmp_path / "vars.yml"
    target.write_text("safe_value: true\n")
    monkeypatch.setattr(
        "ansibleguard.external.gitleaks.scan_with_gitleaks",
        lambda *a, **k: ToolResult("tool-error", message="binary missing"),
    )
    monkeypatch.setattr(
        "ansibleguard.external.ansible_lint.scan_with_ansible_lint",
        lambda *a, **k: ToolResult("completed"),
    )
    output = tmp_path / "output"
    run = analyze_path(target, output)
    assert run["tool_errors"] == 1
    diagnostics = json.loads((output / "diagnostics.json").read_text())
    assert diagnostics[-1]["status"] == "tool-error"


def test_repository_without_yaml_still_keeps_gitleaks_findings(tmp_path, monkeypatch):
    target = tmp_path / "project"
    target.mkdir()
    (target / ".env").write_text("TOKEN=secret\n")
    monkeypatch.setattr(
        "ansibleguard.external.gitleaks.scan_with_gitleaks",
        lambda *a, **k: ToolResult(
            "completed",
            [{"File": ".env", "StartLine": 1, "Description": "Token"}],
        ),
    )
    monkeypatch.setattr(
        "ansibleguard.external.ansible_lint.scan_with_ansible_lint",
        lambda *a, **k: ToolResult("completed"),
    )
    output = tmp_path / "output"
    run = analyze_path(target, output)
    assert run["discovered"] == 0
    findings = json.loads((output / "findings.json").read_text())
    assert findings[0]["file"].endswith(".env")


def test_empty_yaml_keeps_source_detector_finding_without_structural_analysis(
    tmp_path, monkeypatch
):
    target = tmp_path / "empty.yml"
    target.write_text("")
    monkeypatch.setattr(
        "ansibleguard.external.gitleaks.scan_with_gitleaks",
        lambda *a, **k: ToolResult("completed"),
    )
    monkeypatch.setattr(
        "ansibleguard.external.ansible_lint.scan_with_ansible_lint",
        lambda *a, **k: ToolResult("completed"),
    )

    output = tmp_path / "output"
    run = analyze_path(target, output)

    assert run["structurally_analyzed"] == 0
    findings = json.loads((output / "findings.json").read_text())
    assert {finding["rule_id"] for finding in findings} == {"empty-abstraction"}
    assert ",empty,skipped," in (output / "summary.csv").read_text()
