import csv
import json

from ansibleguard.cli import analyze_path
from ansibleguard.external.gitleaks import ToolResult


def test_normalized_findings_are_consistent_in_every_format(tmp_path, monkeypatch):
    target = tmp_path / "project"
    target.mkdir()
    playbook = target / "site.yml"
    playbook.write_text(
        """---
- name: Configure service
  hosts: all
  vars:
    admin_password: admin
  tasks:
    - name: Show configuration
      debug:
        msg: configured
      tags: configuration
""",
        encoding="utf-8",
    )
    output = tmp_path / "output"
    monkeypatch.setattr(
        "ansibleguard.external.gitleaks.scan_with_gitleaks",
        lambda *args, **kwargs: ToolResult("completed"),
    )
    monkeypatch.setattr(
        "ansibleguard.external.ansible_lint.scan_with_ansible_lint",
        lambda *args, **kwargs: ToolResult("completed"),
    )

    analyze_path(target, output)

    findings = json.loads((output / "findings.json").read_text())
    with (output / "findings.csv").open(newline="", encoding="utf-8") as stream:
        csv_findings = list(csv.DictReader(stream))
    sarif = json.loads((output / "findings.sarif").read_text())
    sarif_findings = sarif["runs"][0]["results"]
    text = (output / "findings.txt").read_text()
    file_text = (output / "site" / "Play_Level_Analysis.txt").read_text()

    rule_id = "default-credentials"
    json_count = sum(item["rule_id"] == rule_id for item in findings)
    assert json_count == 1
    assert sum(item["rule_id"] == rule_id for item in csv_findings) == json_count
    assert sum(item["ruleId"] == rule_id for item in sarif_findings) == json_count
    assert text.count(rule_id) == json_count
    assert file_text.count(rule_id) == json_count
    assert (output / "review_metrics.json").is_file()


def test_all_normalized_output_files_are_created_for_an_empty_scan(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "ansibleguard.external.gitleaks.scan_with_gitleaks",
        lambda *args, **kwargs: ToolResult("completed"),
    )
    monkeypatch.setattr(
        "ansibleguard.external.ansible_lint.scan_with_ansible_lint",
        lambda *args, **kwargs: ToolResult("completed"),
    )
    target = tmp_path / "empty"
    target.mkdir()
    output = tmp_path / "output"
    analyze_path(target, output)
    for name in (
        "summary.csv",
        "findings.json",
        "findings.csv",
        "findings.txt",
        "findings.sarif",
        "diagnostics.json",
        "review_metrics.json",
        "file_selection.json",
        "run_metadata.json",
    ):
        assert (output / name).is_file()
