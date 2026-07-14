from ansibleguard.detector_config import filter_findings, load_detector_config
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
