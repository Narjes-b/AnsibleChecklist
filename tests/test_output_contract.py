import csv
import json
from pathlib import Path

import pytest

from ansibleguard.cli import analyze_path
from ansibleguard.external.gitleaks import ToolResult
from ansibleguard.file_manifest import classify_repository, write_file_manifest
from ansibleguard.report.output_contract import (
    CONTRACT_URI,
    SCHEMA_ARTIFACT,
    SCHEMA_VERSION,
    _finding_category,
    load_contract_schema,
    validate_contract_payload,
)
from ansibleguard.report.occurrences import build_occurrences


def test_canonical_alias_uses_native_rule_category():
    occurrence = {
        "concept_id": "credential-log-exposure",
        "detectors": [{"rule_id": "credentials-leaking-in-log"}],
        "native_rules": ["ansibleguard/credentials-leaking-in-log"],
    }
    assert _finding_category(occurrence) == "security"


def test_output_contract_validator_rejects_unknown_schema_and_kind():
    payload = {
        "schema_version": SCHEMA_VERSION,
        "contract": CONTRACT_URI,
        "kind": "canonical-occurrences",
        "items": [],
    }
    assert validate_contract_payload(
        payload, expected_kind="canonical-occurrences"
    )["items"] == []

    invalid_version = dict(payload, schema_version=999)
    try:
        validate_contract_payload(invalid_version)
    except ValueError as exc:
        assert "unsupported output schema" in str(exc)
    else:
        raise AssertionError("unknown schema version was accepted")

    invalid_kind = dict(payload, kind="raw-findings")
    try:
        validate_contract_payload(
            invalid_kind, expected_kind="canonical-occurrences"
        )
    except ValueError as exc:
        assert "expected output kind" in str(exc)
    else:
        raise AssertionError("wrong output kind was accepted")

    with pytest.raises(ValueError, match="unsupported output kind"):
        validate_contract_payload(dict(payload, kind="banana"))


def test_v3_contract_rejects_structurally_invalid_occurrences():
    import jsonschema

    payload = {
        "schema_version": SCHEMA_VERSION,
        "contract": CONTRACT_URI,
        "kind": "canonical-occurrences",
        "items": [{"banana": 42}],
    }

    with pytest.raises(ValueError, match="missing required fields"):
        validate_contract_payload(payload)

    schema = load_contract_schema()
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(payload, schema)


@pytest.mark.parametrize(
    "field,value,match",
    (
        ("line", "banana", "positive integer"),
        ("severity", "critical", "invalid severity"),
        ("detectors", 42, "must be an array"),
    ),
)
def test_runtime_v3_validator_enforces_critical_occurrence_types(
    field, value, match
):
    occurrence = {
        "occurrence_id": "occurrence",
        "concept_id": "concept",
        "file": "tasks.yml",
        "line": 1,
        "scan_mode": "source",
        "severity": "warning",
        "message": "Review this finding",
        "semantic_key": "semantic",
        "content_semantic_key": "content",
        "semantic_subject": "task:configure",
        "provider_evidence_fingerprint": "evidence",
        "detectors": [{"provider": "ansibleguard"}],
    }
    occurrence[field] = value
    payload = {
        "schema_version": SCHEMA_VERSION,
        "contract": CONTRACT_URI,
        "kind": "canonical-occurrences",
        "items": [occurrence],
    }

    with pytest.raises(ValueError, match=match):
        validate_contract_payload(payload)


def test_every_rule_has_developer_guidance_and_confidence():
    from ansibleguard.report.findings import RULE_CATALOG

    assert len(RULE_CATALOG) == 76
    assert all(metadata.get("remediation") for metadata in RULE_CATALOG.values())
    assert {
        metadata.get("confidence") for metadata in RULE_CATALOG.values()
    } <= {"low", "medium", "high"}
    assert all(
        isinstance(metadata.get("known_limitations"), list)
        and isinstance(metadata.get("uncertainty_sources"), list)
        for metadata in RULE_CATALOG.values()
    )
    assert "dynamic_inventory_is_not_executed" in RULE_CATALOG[
        "unguarded-variable"
    ]["known_limitations"]


def test_dot_directory_is_preserved_in_canonical_path(tmp_path):
    repository = tmp_path / "repository"
    source = repository / ".github" / "workflows" / "ci.yml"
    source.parent.mkdir(parents=True)
    source.write_text("name: CI\n", encoding="utf-8")

    occurrence = build_occurrences(
        [
            {
                "file": str(source),
                "line": 1,
                "rule_id": "hardcoded-credentials",
                "concept_id": "hardcoded-secret",
                "severity": "error",
                "message": "secret",
            }
        ],
        repo_root=repository,
    )[0]

    assert occurrence["file"] == ".github/workflows/ci.yml"


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
    normalized = next(item for item in findings if item["rule_id"] == rule_id)
    assert normalized["confidence"] in {"low", "medium", "high"}
    assert normalized["remediation"]
    sarif_result = next(item for item in sarif_findings if item["ruleId"] == rule_id)
    assert sarif_result["properties"]["confidence"] == normalized["confidence"]
    assert sarif_result["properties"]["remediation"] == normalized["remediation"]
    assert text.count(rule_id) == json_count
    assert file_text.count(rule_id) == json_count
    assert (output / "review_metrics.json").is_file()
    contract = json.loads((output / "contract.json").read_text())
    assert contract["kind"] == "contract-manifest"
    assert contract["supported_schema_versions"] == [SCHEMA_VERSION]
    schema_path = output / SCHEMA_ARTIFACT
    assert json.loads(schema_path.read_text())["$id"] == CONTRACT_URI
    assert json.loads(schema_path.read_text()) == load_contract_schema()


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
        "gitleaks-suppressed.json",
    ):
        assert (output / name).is_file()


def test_cached_and_uncached_scans_have_identical_canonical_occurrences(
    tmp_path, monkeypatch
):
    target = tmp_path / "project"
    target.mkdir()
    (target / "tasks.yml").write_text(
        "- name: A deliberately overlong task name that is stable across the "
        "parse cache boundary and therefore suitable for equivalence testing\n"
        "  debug: {msg: ready}\n",
        encoding="utf-8",
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

    analyze_path(target, output, profile="developer-fast")
    uncached = json.loads((output / "canonical/occurrences.json").read_text())
    first_metadata = json.loads((output / "metadata/run.json").read_text())

    analyze_path(target, output, profile="developer-fast")
    cached = json.loads((output / "canonical/occurrences.json").read_text())
    second_metadata = json.loads((output / "metadata/run.json").read_text())

    assert first_metadata["performance"]["cache_misses"] == 1
    assert second_metadata["performance"]["cache_hits"] == 1
    assert cached == uncached


def test_sequential_and_concurrent_providers_have_identical_canonical_output(
    tmp_path, monkeypatch
):
    target = tmp_path / "project"
    target.mkdir()
    (target / "tasks.yml").write_text(
        "- name: Run command\n  command: echo ready\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "ansibleguard.external.gitleaks.scan_with_gitleaks",
        lambda *args, **kwargs: ToolResult("completed"),
    )
    monkeypatch.setattr(
        "ansibleguard.external.ansible_lint.scan_with_ansible_lint",
        lambda *args, **kwargs: ToolResult(
            "completed",
            [{
                "check_name": "command-instead-of-module",
                "description": "use a module",
                "location": {
                    "path": "tasks.yml",
                    "positions": {"begin": {"line": 2}},
                },
            }],
        ),
    )
    sequential_root = tmp_path / "sequential"
    concurrent_root = tmp_path / "concurrent"

    analyze_path(
        target, sequential_root, provider_concurrent=False
    )
    analyze_path(
        target, concurrent_root, provider_concurrent=True
    )

    sequential = json.loads(
        (sequential_root / "canonical/occurrences.json").read_text()
    )
    concurrent = json.loads(
        (concurrent_root / "canonical/occurrences.json").read_text()
    )
    assert concurrent == sequential


def test_suppressed_gitleaks_evidence_is_auditable_output(tmp_path, monkeypatch):
    target = tmp_path / "project"
    target.mkdir()
    (target / "site.yml").write_text("- debug: {msg: ok}\n", encoding="utf-8")
    evidence = {
        "provider": "gitleaks", "native_rule_id": "generic-api-key",
        "file": "guide.md", "line": 1, "scan_mode": "dir",
        "native_fingerprint": "safe", "reason": "documentation-placeholder",
        "policy_version": 1,
    }
    monkeypatch.setattr(
        "ansibleguard.external.gitleaks.scan_with_gitleaks",
        lambda *args, **kwargs: ToolResult(
            "completed", suppressed_findings=[evidence]
        ),
    )
    monkeypatch.setattr(
        "ansibleguard.external.ansible_lint.scan_with_ansible_lint",
        lambda *args, **kwargs: ToolResult("completed"),
    )
    output = tmp_path / "output"
    analyze_path(target, output)

    payload = json.loads(
        (output / "raw/suppressed-external-findings.json").read_text()
    )
    assert payload["items"] == [evidence]
    report = json.loads((output / "summary/report.json").read_text())
    assert report["counts"]["suppressed_external_findings"] == 1


def test_v3_output_is_organized_versioned_and_compatible(tmp_path, monkeypatch):
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
        "summary/run-summary.md",
        "summary/summary.csv",
        "summary/diagnostics.json",
        "raw/findings.json",
        "raw/suppressed-external-findings.json",
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
        "schemas/output-v3.json",
        "files/site.yml/report.json",
        "files/site.yml/findings.json",
        "files/site.yml/occurrences.json",
        "files/site.yml/diagnostics.json",
        "files/site.yml/metrics.json",
    )
    assert all((output / path).is_file() for path in expected)

    schema = json.loads(
        files("ansibleguard.report")
        .joinpath("schemas/output-v3.json")
        .read_text(encoding="utf-8")
    )
    v3_documents = (
        output / "summary/report.json",
        output / "summary/diagnostics.json",
        output / "raw/findings.json",
        output / "raw/suppressed-external-findings.json",
        output / "canonical/occurrences.json",
        output / "metadata/run.json",
        output / "metadata/file-selection.json",
        output / "metadata/review-metrics.json",
        output / "legacy/layout.json",
        output / "files/site.yml/report.json",
        output / "files/site.yml/findings.json",
        output / "files/site.yml/occurrences.json",
        output / "files/site.yml/diagnostics.json",
        output / "files/site.yml/metrics.json",
    )
    for path in v3_documents:
        jsonschema.validate(json.loads(path.read_text()), schema)

    raw_legacy = json.loads((output / "findings.json").read_text())
    raw_v3 = json.loads((output / "raw/findings.json").read_text())
    canonical_legacy = json.loads((output / "occurrences.json").read_text())
    canonical_v3 = json.loads((output / "canonical/occurrences.json").read_text())
    assert raw_v3["items"] == raw_legacy
    assert canonical_v3["items"] == canonical_legacy
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
    assert report["schema_version"] == SCHEMA_VERSION
    assert report["counts"]["raw_findings"] == len(
        json.loads((output / "findings.json").read_text())
    )
    assert report["counts"]["canonical_occurrences"] == len(
        json.loads((output / "occurrences.json").read_text())
    )
    assert report["artifacts"]["canonical_csv"] == "canonical/occurrences.csv"
    assert report["artifacts"]["trust_summary"] == "summary/run-summary.md"
    assert report["counts"]["suppressed_external_findings"] == 0
    assert report["analysis_scope"]["internal"]["selected_files"] == 1
    assert report["reproducibility"]["rule_count"] == 76
    assert report["reproducibility"]["rule_catalog_sha256"]
    trust_summary = (output / "summary/run-summary.md").read_text(encoding="utf-8")
    assert "scan trust summary" in trust_summary
    assert "Structurally analyzed files" in trust_summary
    counts = report["counts"]
    assert sum(counts["files_by_class"].values()) == counts["files"]
    assert sum(counts["files_by_artifact_kind"].values()) == counts["files"]
    assert sum(counts["canonical_by_finding_category"].values()) == counts["canonical_occurrences"]
    assert sum(counts["canonical_by_file_class"].values()) == counts["canonical_occurrences"]
    assert sum(counts["canonical_by_artifact_kind"].values()) == counts["canonical_occurrences"]
    file_report = json.loads((output / "files/site.yml/report.json").read_text())
    assert file_report["file_class"] == "unclassified"
    assert file_report["ansible_artifact_kind"] in {"tasks", "playbook"}
    assert "canonical_by_finding_category" in file_report["counts"]


def test_manifest_categories_flow_to_repository_and_file_reports(tmp_path, monkeypatch):
    target = tmp_path / "project"
    tasks = target / "roles" / "web" / "tasks" / "main.yml"
    tasks.parent.mkdir(parents=True)
    tasks.write_text(
        "- name: Untagged task\n  debug:\n    msg: hello\n", encoding="utf-8"
    )
    manifest = write_file_manifest(
        classify_repository(target, "example/project", "a" * 40),
        tmp_path / "files.csv",
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
    analyze_path(
        target,
        output,
        file_manifest=manifest,
        profile="snapshot-source",
    )

    report = json.loads((output / "summary/report.json").read_text())
    assert report["counts"]["files_by_class"] == {"production_ansible": 1}
    assert report["counts"]["files_by_artifact_kind"] == {"tasks": 1}
    assert report["counts"]["canonical_by_artifact_kind"] == {
        "tasks": report["counts"]["canonical_occurrences"]
    }
    nested = report["counts"][
        "canonical_by_artifact_kind_and_finding_category"
    ]
    assert nested["tasks"]["style"] >= 1
    file_report = json.loads(
        (output / "files/roles/web/tasks/main.yml/report.json").read_text()
    )
    assert file_report["file_class"] == "production_ansible"
    assert file_report["ansible_artifact_kind"] == "tasks"
