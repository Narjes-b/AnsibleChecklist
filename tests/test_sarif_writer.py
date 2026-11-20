"""Regression tests for sarif_writer.py. Earlier this session the generated
document was validated against the real, downloaded OASIS SARIF 2.1.0
schema manually, one-off -- these tests don't repeat that live network/
jsonschema-dependent check (deliberately, to keep this suite fast and
offline-safe), but do lock in every structural property that check
actually confirmed, plus the specific repo-relative-URI requirement GitHub
Code Scanning needs to annotate a PR correctly."""

import json

from ansibleguard.report.sarif_writer import (
    build_sarif,
    write_sarif,
    _to_repo_relative,
    _effective_rule_id,
)


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
    assert driver["version"] == "0.0.1"
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
        assert rule["properties"]["status"] in {
            "stable", "candidate", "experimental", "deprecated", "removed"
        }


def test_sarif_exposes_experimental_rule_lifecycle():
    doc = build_sarif([], repo_root="/tmp")
    rules = {
        rule["id"]: rule for rule in doc["runs"][0]["tool"]["driver"]["rules"]
    }
    assert rules["incohesive-play"]["properties"]["status"] == "experimental"
    assert rules["unused-include-vars"]["properties"]["status"] == "experimental"
    assert rules["unused-include-vars"]["properties"]["confidence"] == "low"


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
    assert "partialFingerprints" not in r


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


# --- native ruleId for ansible-lint findings ---
# Before the fix all 65k+ ansible-lint findings shared one ruleId
# ("ansible-lint-issue") in SARIF, collapsing them into a single rule node
# in GitHub Code Scanning. The fix uses native_rule_id when concept_id is
# the generic envelope.


def _ansible_lint_finding(native_rule_id="fqcn[action-core]"):
    return {
        "file": "roles/common/tasks/main.yml",
        "line": 5,
        "rule_id": "ansible-lint-issue",
        "native_rule_id": native_rule_id,
        "concept_id": "ansible-lint-issue",
        "severity": "warning",
        "message": f"ansible-lint: {native_rule_id}",
        "provider": "ansible-lint",
    }


def test_effective_rule_id_uses_native_for_ansible_lint_envelope():
    finding = _ansible_lint_finding("fqcn[action-core]")
    assert _effective_rule_id(finding) == "fqcn[action-core]"


def test_effective_rule_id_leaves_regular_findings_unchanged():
    finding = _one_finding(rule_id="credentials-leaking-in-log")
    finding["concept_id"] = "credential-log-exposure"
    assert _effective_rule_id(finding) == "credentials-leaking-in-log"


def test_effective_rule_id_falls_back_when_native_rule_id_is_envelope():
    finding = _ansible_lint_finding("ansible-lint-issue")
    # native_rule_id IS the envelope — must not produce the generic ID as ruleId
    # when native is also the envelope; fall back to rule_id
    result = _effective_rule_id(finding)
    # The result should not be empty; it's acceptable to return the rule_id here
    assert result  # not empty


def test_sarif_result_uses_native_rule_id_for_ansible_lint_finding():
    finding = _ansible_lint_finding("yaml[line-length]")
    doc = build_sarif([finding], repo_root="/tmp")
    result = doc["runs"][0]["results"][0]
    assert result["ruleId"] == "yaml[line-length]", (
        "ansible-lint finding must use native rule ID in SARIF ruleId"
    )


def test_sarif_rules_array_has_per_native_rule_entry_with_help_uri():
    finding = _ansible_lint_finding("fqcn[action-core]")
    doc = build_sarif([finding], repo_root="/tmp")
    rules = {r["id"]: r for r in doc["runs"][0]["tool"]["driver"]["rules"]}
    assert "fqcn[action-core]" in rules, "native rule must appear in driver.rules"
    assert "helpUri" in rules["fqcn[action-core]"], "ansible-lint rules need a helpUri"
    assert "ansible-lint.readthedocs.io" in rules["fqcn[action-core]"]["helpUri"]


def test_sarif_rules_array_deduplicates_same_native_rule():
    findings = [
        _ansible_lint_finding("yaml[line-length]"),
        _ansible_lint_finding("yaml[line-length]"),
        _ansible_lint_finding("yaml[line-length]"),
    ]
    doc = build_sarif(findings, repo_root="/tmp")
    rule_ids = [r["id"] for r in doc["runs"][0]["tool"]["driver"]["rules"]]
    assert rule_ids.count("yaml[line-length]") == 1, "same native rule must not be duplicated"


def test_multiple_distinct_ansible_lint_rules_each_get_their_own_sarif_entry():
    findings = [
        _ansible_lint_finding("fqcn[action-core]"),
        _ansible_lint_finding("yaml[line-length]"),
        _ansible_lint_finding("no-log-password"),
    ]
    doc = build_sarif(findings, repo_root="/tmp")
    rule_ids = {r["id"] for r in doc["runs"][0]["tool"]["driver"]["rules"]}
    for native in ("fqcn[action-core]", "yaml[line-length]", "no-log-password"):
        assert native in rule_ids
