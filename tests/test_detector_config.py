import pytest

from ansibleguard.detector_config import (
    DetectorConfigError,
    filter_findings,
    load_detector_config,
)
from ansibleguard.detectors.paper_candidates import detect_paper_candidates
from ansibleguard.detectors.review_checklist import detect_review_checklist_smells
from ansibleguard.smells import read_thresholds


def test_project_config_controls_thresholds_options_and_suppressions(tmp_path):
    config = tmp_path / ".ansibleguard.yml"
    config.write_text(
"""thresholds:
  long_statement_length: 20
  LOC_playbook: 999
rules:
  default_credentials: [company-default]
  additional_mutating_command_patterns:
    - '\\bcustomctl\\s+apply\\b'
suppressions:
  disabled_rules: [long-statement]
""",
        encoding="utf-8",
    )
    playbook = tmp_path / "site.yml"
    playbook.write_text(
        """---
- hosts: all
  vars:
    api_token: company-default
  tasks:
    - name: A deliberately long task name for the configured threshold
      command: customctl apply service
""",
        encoding="utf-8",
    )

    assert load_detector_config(playbook)["thresholds"]["long_statement_length"] == 20
    assert read_thresholds(playbook)["LOC_playbook"] == 999
    assert detect_paper_candidates(playbook)["long_statements"] > 0
    review = detect_review_checklist_smells(playbook)
    assert review["default_credentials"] == 1
    assert review["non_idempotent_commands"] == 1
    findings = [
        {"rule_id": "long-statement"},
        {"rule_id": "default-credentials"},
    ]
    assert filter_findings(findings, playbook) == [
        {"rule_id": "default-credentials"}
    ]


@pytest.mark.parametrize(
    "content, message",
    [
        ("thresholds:\n  long_statment_length: 10\n", "unknown threshold"),
        ("thresholds:\n  long_statement_length: fast\n", "must be numeric"),
        ("rules:\n  additional_mutating_command_patterns: ['[']\n", "invalid rules"),
        ("suppressions:\n  disabled_rules: [not-a-real-rule]\n", "unknown disabled rule"),
        ("rules: [invalid]\n", "rules must be a mapping"),
    ],
)
def test_invalid_configuration_fails_closed(tmp_path, content, message):
    (tmp_path / ".ansibleguard.yml").write_text(content, encoding="utf-8")
    target = tmp_path / "site.yml"
    target.write_text("- debug: {msg: ok}\n", encoding="utf-8")

    with pytest.raises(DetectorConfigError, match=message):
        load_detector_config(target)


def test_undocumented_complexity_thresholds_are_project_configurable(tmp_path):
    (tmp_path / ".ansibleguard.yml").write_text(
        "thresholds:\n"
        "  undocumented_complex_boolean_ops: 5\n"
        "  undocumented_complex_jinja_filters: 5\n"
        "  undocumented_complex_nesting_depth: 6\n",
        encoding="utf-8",
    )
    playbook = tmp_path / "site.yml"
    playbook.write_text(
        "- name: Locally acceptable condition\n  debug: {msg: ok}\n"
        "  when: a and b or c and d\n",
        encoding="utf-8",
    )

    assert detect_review_checklist_smells(playbook)["undocumented_complex_tasks"] == 0


def test_suppressions_distinguish_concept_normalized_and_native_rules(tmp_path):
    (tmp_path / ".ansibleguard.yml").write_text(
        "suppressions:\n"
        "  concepts: [fqcn-migration, unresolved-runtime-input]\n"
        "  rules: [ansibleguard/missing-tags]\n"
        "  native_rules: ['ansible-lint/yaml[truthy]']\n"
    )
    target = tmp_path / "site.yml"
    target.write_text("- debug: {msg: ok}\n")
    findings = [
        {"rule_id": "ansible-lint-issue", "concept_id": "fqcn-migration",
         "provider": "ansible-lint", "native_rule_id": "fqcn[action]"},
        {"rule_id": "missing-tags", "concept_id": "missing-tags",
         "provider": "ansibleguard", "native_rule_id": "missing-tags"},
        {"rule_id": "ansible-lint-issue", "concept_id": "yaml-truthy-value",
         "provider": "ansible-lint", "native_rule_id": "yaml[truthy]"},
        {"rule_id": "unguarded-variable", "concept_id": "unresolved-runtime-input",
         "provider": "ansibleguard", "native_rule_id": "unguarded-variable"},
        {"rule_id": "unnamed-task", "concept_id": "unnamed-task",
         "provider": "ansibleguard", "native_rule_id": "unnamed-task"},
    ]

    assert filter_findings(findings, target) == [findings[-1]]


def test_fingerprint_suppression_requires_reason_and_honors_expiry(tmp_path):
    config = tmp_path / ".ansibleguard.yml"
    config.write_text(
        "suppressions:\n"
        "  fingerprints:\n"
        "    - fingerprint: stable-accepted-risk\n"
        "      reason: accepted bootstrap exception\n"
        "      expires: 2999-01-01\n"
        "    - fingerprint: expired-risk\n"
        "      reason: old exception\n"
        "      expires: 2000-01-01\n",
        encoding="utf-8",
    )
    target = tmp_path / "site.yml"
    target.write_text("- debug: {msg: ok}\n", encoding="utf-8")
    findings = [
        {"rule_id": "x", "semantic_key": "stable-accepted-risk"},
        {"rule_id": "y", "semantic_key": "expired-risk"},
    ]

    assert filter_findings(findings, target) == [findings[1]]


def test_fingerprint_suppression_reason_is_required(tmp_path):
    (tmp_path / ".ansibleguard.yml").write_text(
        "suppressions:\n  fingerprints:\n    - fingerprint: stable\n",
        encoding="utf-8",
    )
    target = tmp_path / "site.yml"
    target.write_text("- debug: {msg: ok}\n", encoding="utf-8")

    with pytest.raises(DetectorConfigError, match="reason is required"):
        load_detector_config(target)


def test_custom_module_facts_must_map_modules_to_fact_name_lists(tmp_path):
    target = tmp_path / "site.yml"
    target.write_text("- debug: {msg: ok}\n", encoding="utf-8")
    (tmp_path / ".ansibleguard.yml").write_text(
        "rules:\n  custom_module_facts:\n    vendor.widget_facts: widget_state\n",
        encoding="utf-8",
    )

    with pytest.raises(DetectorConfigError, match="custom_module_facts"):
        load_detector_config(target)
