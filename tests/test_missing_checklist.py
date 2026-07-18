from ansibleguard.detectors.missing_checklist import (
    detect_deprecated_module_options,
    detect_unexpected_task_locations,
    detect_variable_use_before_definition,
)
from ansibleguard.parser import mainn
from ansibleguard.report.findings import build_findings_list
import ansibleguard.detectors.missing_checklist as missing_checklist


def _write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_variable_use_before_definition_only_reports_later_task_results(tmp_path):
    playbook = _write(
        tmp_path / "order.yml",
        """- name: Ordering
  hosts: all
  vars:
    externally_defined: ready
  tasks:
    - name: Premature result use
      debug:
        msg: "{{ deploy_result.stdout }}"
    - name: Guarded future result
      debug:
        msg: "{{ optional_result | default('not ready') }}"
    - name: Static value remains valid
      debug:
        msg: "{{ externally_defined }}"
    - name: Define deploy result
      command: /bin/true
      register: deploy_result
    - name: Define optional result
      command: /bin/true
      register: optional_result
    - name: Valid later use
      debug:
        msg: "{{ deploy_result.stdout }}"
""",
    )

    count, details = detect_variable_use_before_definition(playbook)
    assert count == 1
    assert details[0]["variable"] == "deploy_result"
    assert details[0]["line"] == 6
    assert details[0]["definition_line"] == 15


def test_unexpected_role_file_content_and_handler_attribute(tmp_path):
    role = tmp_path / "roles" / "web"
    wrong_defaults = _write(
        role / "defaults" / "main.yml",
        "- name: This is a task, not a default mapping\n  debug:\n    msg: wrong\n",
    )
    wrong_task = _write(
        role / "tasks" / "main.yml",
        "- name: Handler in tasks\n  listen: Restart web\n  service:\n    name: nginx\n    state: restarted\n",
    )
    valid_handler = _write(
        role / "handlers" / "main.yml",
        "- name: Restart web\n  listen: Restart web\n  service:\n    name: nginx\n    state: restarted\n",
    )

    assert detect_unexpected_task_locations(wrong_defaults)[0] == 1
    assert detect_unexpected_task_locations(wrong_task)[0] == 1
    assert detect_unexpected_task_locations(valid_handler)[0] == 0


def test_configured_deprecated_option_flows_through_parser_and_findings(tmp_path):
    _write(
        tmp_path / ".ansibleguard.yml",
        """rules:
  deprecated_module_options:
    debug:
      verbosity:
        replacement: project_verbosity
        removed_in: "3.0"
""",
    )
    playbook = _write(
        tmp_path / "deprecated.yml",
        """- name: Deprecated option
  hosts: all
  tasks:
    - name: Show message
      debug:
        msg: hello
        verbosity: 1
""",
    )

    count, details = detect_deprecated_module_options(playbook)
    assert count == 1
    assert details[0]["option"] == "verbosity"
    assert "project_verbosity" in details[0]["issue"]

    metrics = mainn(playbook)
    assert metrics["deprecated_module_options"] == 1
    result = {
        "playbook": {"metrics": {"WarningUnusedIncludeVars": []}, "plays": []}
    }
    findings = build_findings_list(metrics, result, [], [], playbook)
    assert "deprecated-module-option" in {
        finding["rule_id"] for finding in findings
    }


def test_installed_metadata_deprecated_option_is_detected(tmp_path, monkeypatch):
    playbook = _write(
        tmp_path / "metadata.yml",
        """- name: Metadata
  hosts: all
  tasks:
    - name: Use old option
      example_module:
        old_option: value
""",
    )
    monkeypatch.setattr(
        missing_checklist,
        "_module_document",
        lambda module: {
            "doc": {
                "options": {
                    "old_option": {
                        "deprecated": {
                            "why": "The provider replaced it.",
                            "alternative": "new_option",
                            "version": "4.0",
                        }
                    }
                }
            }
        },
    )

    count, details = detect_deprecated_module_options(playbook)
    assert count == 1
    assert details[0]["module"] == "example_module"
    assert "new_option" in details[0]["issue"]
    assert "4.0" in details[0]["issue"]


def test_new_order_and_location_metrics_flow_to_findings(tmp_path):
    playbook = _write(
        tmp_path / "roles" / "web" / "tasks" / "main.yml",
        """- name: Use result too soon
  debug:
    msg: "{{ command_result.stdout }}"
  listen: Incorrect handler placement
- name: Produce result
  command: /bin/true
  register: command_result
""",
    )
    metrics = mainn(playbook)
    assert metrics["variable_use_before_definition"] == 1
    assert metrics["unexpected_task_locations"] == 1
    result = {
        "playbook": {"metrics": {"WarningUnusedIncludeVars": []}, "plays": []}
    }
    findings = build_findings_list(metrics, result, [], [], playbook)
    rule_ids = {finding["rule_id"] for finding in findings}
    assert "variable-use-before-definition" in rule_ids
    assert "unexpected-task-location" in rule_ids
