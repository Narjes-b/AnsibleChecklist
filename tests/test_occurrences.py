from ansibleguard.report.occurrences import build_occurrences


def test_overlapping_detectors_are_grouped_without_losing_evidence(tmp_path):
    source = tmp_path / "tasks.yml"
    findings = [
        {
            "file": str(source),
            "line": 7,
            "rule_id": "overriden-keys",
            "severity": "error",
            "message": "duplicate key",
            "provider": "ansibleguard",
            "native_rule_id": "overriden-keys",
            "concept_id": "duplicate-mapping-key",
            "finding_id": "internal",
        },
        {
            "file": str(source),
            "line": 7,
            "rule_id": "ansible-lint-issue",
            "severity": "warning",
            "message": "key-duplicates",
            "provider": "ansible-lint",
            "native_rule_id": "yaml[key-duplicates]",
            "concept_id": "duplicate-mapping-key",
            "finding_id": "lint",
        },
    ]
    occurrences = build_occurrences(findings, repo_root=tmp_path)
    assert len(occurrences) == 1
    assert occurrences[0]["detector_count"] == 2
    assert occurrences[0]["canonical_provider"] == "ansible-lint"
    assert {item["finding_id"] for item in occurrences[0]["detectors"]} == {
        "internal",
        "lint",
    }


def test_occurrence_identity_changes_when_native_evidence_changes(tmp_path):
    base = {
        "file": str(tmp_path / "vars.yml"),
        "line": 2,
        "rule_id": "hardcoded-credentials",
        "severity": "error",
        "message": "secret",
        "provider": "gitleaks",
        "native_rule_id": "generic-api-key",
        "concept_id": "hardcoded-secret",
        "finding_id": "raw",
        "native_fingerprint": "old",
        "scan_mode": "dir",
    }
    old = build_occurrences([base], repo_root=tmp_path)[0]
    new = build_occurrences(
        [{**base, "native_fingerprint": "new"}], repo_root=tmp_path
    )[0]
    assert old["occurrence_id"] != new["occurrence_id"]
