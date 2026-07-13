"""Regression tests for sarif_writer.py. Earlier this session the generated
document was validated against the real, downloaded OASIS SARIF 2.1.0
schema manually, one-off -- these tests don't repeat that live network/
jsonschema-dependent check (deliberately, to keep this suite fast and
offline-safe), but do lock in every structural property that check
actually confirmed, plus the specific repo-relative-URI requirement GitHub
Code Scanning needs to annotate a PR correctly."""

import json

from ansibleguard.report.sarif_writer import build_sarif, write_sarif, _to_repo_relative


def _one_finding(
    file="roles/apache/tasks/main.yml",
    line=7,
    rule_id="credentials-leaking-in-log",
    severity="error",
    message="Task 'Set password' leaks a secret",
):
    return {
        "file": file,
        "line": line,
        "rule_id": rule_id,
        "severity": severity,
        "message": message,
    }


# --- top-level document structure ---


def test_build_sarif_has_required_top_level_keys():
    doc = build_sarif([], repo_root="/tmp")
    assert doc["version"] == "2.1.0"
    assert "$schema" in doc
    assert isinstance(doc["runs"], list) and len(doc["runs"]) == 1


def test_build_sarif_tool_driver_has_name_and_rules():
    doc = build_sarif([], repo_root="/tmp")
    driver = doc["runs"][0]["tool"]["driver"]
    assert driver["name"] == "AnsibleGuard"
    assert isinstance(driver["rules"], list)
    assert len(driver["rules"]) > 0  # RULE_CATALOG should never be empty


def test_build_sarif_empty_findings_produces_empty_but_valid_results():
    doc = build_sarif([], repo_root="/tmp")
    assert doc["runs"][0]["results"] == []


# --- rules array: every entry must have the fields SARIF/GitHub expect ---


def test_every_rule_entry_has_id_and_valid_level():
    doc = build_sarif([], repo_root="/tmp")
    valid_levels = {"error", "warning", "note"}
    for rule in doc["runs"][0]["tool"]["driver"]["rules"]:
        assert "id" in rule
        assert rule["defaultConfiguration"]["level"] in valid_levels
        assert "text" in rule["shortDescription"]


# --- one finding -> one correctly-shaped SARIF result ---


def test_single_finding_maps_to_correct_sarif_result():
    finding = _one_finding(file="/tmp/roles/apache/tasks/main.yml")
    doc = build_sarif([finding], repo_root="/tmp")

    results = doc["runs"][0]["results"]
    assert len(results) == 1
    r = results[0]
    assert r["ruleId"] == "credentials-leaking-in-log"
    assert r["level"] == "error"
    assert r["message"]["text"] == "Task 'Set password' leaks a secret"

    location = r["locations"][0]["physicalLocation"]
    assert location["region"]["startLine"] == 7
    assert location["artifactLocation"]["uri"] == "roles/apache/tasks/main.yml"
    assert len(r["partialFingerprints"]["primaryLocationLineHash"]) == 64


def test_multiple_findings_produce_multiple_results_in_order():
    findings = [
        _one_finding(rule_id="large-task", line=10),
        _one_finding(rule_id="unnamed-play", line=1),
    ]
    doc = build_sarif(findings, repo_root="/tmp")

    results = doc["runs"][0]["results"]
    assert len(results) == 2
    assert results[0]["ruleId"] == "large-task"
    assert results[1]["ruleId"] == "unnamed-play"


# --- the repo-relative URI requirement: this is what makes GitHub Code
# Scanning able to map an annotation back to the right file in a PR diff.
# An absolute path here silently fails to annotate anything on GitHub's side. ---


def test_to_repo_relative_strips_the_repo_root_prefix(tmp_path):
    repo_root = tmp_path / "myproject"
    (repo_root / "roles" / "apache" / "tasks").mkdir(parents=True)
    file_path = repo_root / "roles" / "apache" / "tasks" / "main.yml"
    file_path.write_text("- name: x\n")

    rel = _to_repo_relative(file_path, repo_root)
    assert rel == "roles/apache/tasks/main.yml"
    assert not rel.startswith("/")  # must never be absolute


def test_to_repo_relative_falls_back_to_filename_when_not_under_root(tmp_path):
    unrelated_root = tmp_path / "unrelated"
    unrelated_root.mkdir()
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    file_path = elsewhere / "playbook.yml"
    file_path.write_text("- name: x\n")

    rel = _to_repo_relative(file_path, unrelated_root)
    assert rel == "playbook.yml"
    assert not rel.startswith("/")


def test_build_sarif_never_emits_absolute_uris(tmp_path):
    """A finding whose file path isn't actually under repo_root must still
    degrade to a relative-looking filename, never an absolute path leaking
    through into the SARIF output."""
    finding = _one_finding(file="/some/totally/unrelated/path/main.yml")
    doc = build_sarif([finding], repo_root=str(tmp_path))

    uri = doc["runs"][0]["results"][0]["locations"][0]["physicalLocation"][
        "artifactLocation"
    ]["uri"]
    assert not uri.startswith("/")


# --- write_sarif(): actually writes valid, round-trippable JSON to disk ---


def test_write_sarif_writes_valid_json_that_round_trips(tmp_path):
    finding = _one_finding()
    output_path = tmp_path / "findings.sarif"

    write_sarif([finding], output_path, repo_root=str(tmp_path))

    assert output_path.exists()
    with open(output_path) as f:
        loaded = json.load(f)  # must not raise -- confirms it's valid JSON

    assert loaded["version"] == "2.1.0"
    assert len(loaded["runs"][0]["results"]) == 1
    assert loaded["runs"][0]["results"][0]["ruleId"] == "credentials-leaking-in-log"


def test_write_sarif_with_empty_findings_still_writes_valid_document(tmp_path):
    output_path = tmp_path / "findings.sarif"
    write_sarif([], output_path, repo_root=str(tmp_path))

    with open(output_path) as f:
        loaded = json.load(f)
    assert loaded["runs"][0]["results"] == []
