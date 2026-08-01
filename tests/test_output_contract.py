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


def test_v2_output_is_organized_versioned_and_compatible(tmp_path, monkeypatch):
    from importlib.resources import files

    import jsonschema

    target = tmp_path / "project"
    target.mkdir()
    (target / "site.yml").write_text(
        "- name: Show value\n  debug:\n    msg: ok\n", encoding="utf-8"
    )
    monkeypatch.setattr(
        "ansibleguard.external.gitleaks.scan_with_gitleaks",
        lambda *args, **kwargs: ToolResult("completed"),
    )
    monkeypatch.setattr(
        "ansibleguard.external.ansible_lint.scan_with_ansible_lint",
        lambda *args, **kwargs: ToolResult("completed"),
    )
    output = tmp_path / "output"
    analyze_path(target, output)

    expected = (
        "summary/report.json",
        "summary/summary.csv",
        "summary/diagnostics.json",
        "raw/findings.json",
        "raw/findings.csv",
        "raw/findings.txt",
        "canonical/occurrences.json",
        "canonical/occurrences.csv",
        "canonical/occurrences.txt",
        "canonical/findings.sarif",
        "metadata/run.json",
        "metadata/file-selection.json",
        "metadata/review-metrics.json",
        "legacy/layout.json",
    )
    assert all((output / path).is_file() for path in expected)

    schema = json.loads(
        files("ansibleguard.report")
        .joinpath("schemas/output-v2.json")
        .read_text(encoding="utf-8")
    )
    v2_documents = (
        output / "summary/report.json",
        output / "summary/diagnostics.json",
        output / "raw/findings.json",
        output / "canonical/occurrences.json",
        output / "metadata/run.json",
        output / "metadata/file-selection.json",
        output / "metadata/review-metrics.json",
        output / "legacy/layout.json",
    )
    for path in v2_documents:
        jsonschema.validate(json.loads(path.read_text()), schema)

    raw_legacy = json.loads((output / "findings.json").read_text())
    raw_v2 = json.loads((output / "raw/findings.json").read_text())
    canonical_legacy = json.loads((output / "occurrences.json").read_text())
    canonical_v2 = json.loads((output / "canonical/occurrences.json").read_text())
    assert raw_v2["items"] == raw_legacy
    assert canonical_v2["items"] == canonical_legacy
    assert (output / "findings.sarif").read_text() == (
        output / "canonical/findings.sarif"
    ).read_text()


def test_enriched_summary_and_report_explain_raw_and_canonical_counts(
    tmp_path, monkeypatch
):
    target = tmp_path / "project"
    target.mkdir()
    (target / "site.yml").write_text(
        "- name: Show value\n  debug:\n    msg: ok\n", encoding="utf-8"
    )
    monkeypatch.setattr(
        "ansibleguard.external.gitleaks.scan_with_gitleaks",
        lambda *args, **kwargs: ToolResult("completed"),
    )
    monkeypatch.setattr(
        "ansibleguard.external.ansible_lint.scan_with_ansible_lint",
        lambda *args, **kwargs: ToolResult(
            "completed",
            [
                {
                    "check_name": "name[casing]",
                    "description": "Name casing",
                    "location": {
                        "path": "site.yml",
                        "positions": {"begin": {"line": 1}},
                    },
                }
            ],
        ),
    )
    output = tmp_path / "output"
    analyze_path(target, output)

    with (output / "summary/summary.csv").open(
        newline="", encoding="utf-8"
    ) as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 1
    row = rows[0]
    assert int(row["raw_findings"]) >= int(row["canonical_occurrences"])
    assert int(row["ansibleguard_findings"]) > 0
    assert int(row["ansible_lint_findings"]) == 1
    assert row["pr_comparison_status"] == "not-compared"

    report = json.loads((output / "summary/report.json").read_text())
    assert report["schema_version"] == 2
    assert report["counts"]["raw_findings"] == len(
        json.loads((output / "findings.json").read_text())
    )
    assert report["counts"]["canonical_occurrences"] == len(
        json.loads((output / "occurrences.json").read_text())
    )
    assert report["artifacts"]["canonical_csv"] == "canonical/occurrences.csv"
