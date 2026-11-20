from ansibleguard.detectors.missing_checklist import (
    detect_deprecated_module_options,
    detect_unexpected_task_locations,
    detect_variable_use_before_definition,
)
from ansibleguard.parser import mainn
from ansibleguard.report.findings import build_findings_list
from ansibleguard.symbol_index import build_repository_symbol_index
from ansibleguard.analysis_context import build_repository_analysis_context
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


def test_reused_register_is_not_use_before_definition(tmp_path):
    playbook = _write(
        tmp_path / "reuse.yml",
        """- name: First producer
  command: /bin/true
  register: command_result
- name: First use
  debug:
    var: command_result
- name: Second producer
  command: /bin/true
  register: command_result
""",
    )
    assert detect_variable_use_before_definition(playbook) == (0, [])


def test_not_defined_guard_is_not_use_before_definition(tmp_path):
    playbook = _write(
        tmp_path / "guard.yml",
        """- name: Conditionally obtain value
  command: /bin/true
  register: command_result
  when: final_value is not defined
- name: Define final value
  set_fact:
    final_value: "{{ command_result.stdout }}"
""",
    )

    assert detect_variable_use_before_definition(playbook) == (0, [])


def test_repository_definition_prevents_false_ordering_finding(tmp_path):
    _write(tmp_path / "roles" / "web" / "defaults" / "main.yml", "deploy_result: preset\n")
    playbook = _write(
        tmp_path / "roles" / "web" / "tasks" / "main.yml",
        "- name: Use visible default\n"
        "  debug:\n    msg: '{{ deploy_result }}'\n"
        "- name: Optionally refresh value\n"
        "  set_fact:\n    deploy_result: refreshed\n",
    )
    index = build_repository_symbol_index(tmp_path)

    assert detect_variable_use_before_definition(playbook, symbol_index=index) == (0, [])


def test_symbol_index_does_not_hide_later_runtime_definition(tmp_path):
    playbook = _write(
        tmp_path / "roles" / "web" / "tasks" / "main.yml",
        "- name: Premature use\n  debug:\n    msg: '{{ command_result.stdout }}'\n"
        "- name: Later producer\n  command: /bin/true\n  register: command_result\n",
    )
    index = build_repository_symbol_index(tmp_path)

    count, details = detect_variable_use_before_definition(playbook, symbol_index=index)

    assert count == 1
    assert details[0]["variable"] == "command_result"


def test_excluded_vars_file_does_not_affect_use_before_definition(tmp_path):
    playbook = _write(
        tmp_path / "site.yml",
        "- name: Premature use\n  debug: {msg: '{{ staged_value }}'}\n"
        "- name: Later definition\n  set_fact: {staged_value: ready}\n",
    )
    _write(tmp_path / "group_vars" / "all.yml", "staged_value: excluded\n")
    graph = build_repository_symbol_index(tmp_path, files=[playbook])

    count, details = detect_variable_use_before_definition(
        playbook, symbol_index=graph
    )

    assert count == 1
    assert details[0]["variable"] == "staged_value"


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


def test_custom_role_meta_list_is_not_treated_as_meta_main(tmp_path):
    variants = _write(
        tmp_path / "roles" / "web" / "meta" / "variants.yml",
        "- services:\n    cache: true\n- services:\n    cache: false\n",
    )

    assert detect_unexpected_task_locations(variants) == (0, [])


def test_handler_imported_task_file_is_not_misclassified(tmp_path):
    role = tmp_path / "roles" / "web"
    handler = _write(
        role / "handlers" / "main.yml",
        "- name: Dispatch restart\n"
        "  listen: Restart web\n"
        "  import_tasks: ../tasks/restart.yml\n",
    )
    imported = _write(
        role / "tasks" / "restart.yml",
        "- name: Restart service\n"
        "  listen: Restart web\n"
        "  service: {name: nginx, state: restarted}\n",
    )
    context = build_repository_analysis_context(tmp_path, [handler, imported])

    assert detect_unexpected_task_locations(
        imported, repository_context=context
    ) == (0, [])


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


def test_installed_metadata_deprecated_option_is_detected(tmp_path):
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
    metadata = {
        "example_module": {
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
        }
    }

    count, details = detect_deprecated_module_options(
        playbook, module_metadata=metadata
    )
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


def test_undefined_guard_before_later_definition_is_safe(tmp_path):
    tasks = _write(
        tmp_path / "tasks.yml",
        "- name: Check whether address is needed\n"
        "  debug:\n"
        "    msg: resolving\n"
        "  when: host_address is undefined or host_address is none\n"
        "- name: Resolve address\n"
        "  set_fact:\n"
        "    host_address: 2001:db8::1\n",
    )

    assert detect_variable_use_before_definition(tasks) == (0, [])


def test_same_task_defined_guard_prevents_use_before_definition(tmp_path):
    tasks = _write(
        tmp_path / "tasks.yml",
        "- name: Conditionally display result\n"
        "  debug:\n"
        "    msg: '{{ command_result.stdout }}'\n"
        "  when: command_result is defined\n"
        "- name: Produce result\n"
        "  command: /bin/true\n"
        "  register: command_result\n",
    )

    assert detect_variable_use_before_definition(tasks) == (0, [])


def test_disjunctive_defined_guard_does_not_hide_use_before_definition(tmp_path):
    tasks = _write(
        tmp_path / "tasks.yml",
        "- name: May display missing result\n"
        "  debug:\n    msg: '{{ command_result.stdout }}'\n"
        "  when: command_result is defined or fallback_enabled\n"
        "- name: Produce result\n"
        "  command: /bin/true\n"
        "  register: command_result\n",
    )

    count, details = detect_variable_use_before_definition(tasks)

    assert count == 1
    assert details[0]["variable"] == "command_result"


def test_missing_checklist_detectors_reuse_dispatcher_document(tmp_path, monkeypatch):
    tasks = _write(
        tmp_path / "roles" / "web" / "defaults" / "main.yml",
        "- name: Task-shaped defaults\n  debug: {msg: ready}\n",
    )
    context = build_repository_analysis_context(tmp_path, [tasks])
    parsed = context.document_for(tasks)
    original = missing_checklist._load

    def require_parsed(path, parsed_document=None):
        assert parsed_document is parsed
        return original(path, parsed_document)

    monkeypatch.setattr(missing_checklist, "_load", require_parsed)

    result = missing_checklist.detect_missing_checklist_smells(
        tasks,
        repository_context=context,
        parsed_document=parsed,
        enabled_rules={"unexpected-task-location", "deprecated-module-option"},
    )

    assert "unexpected_task_locations" in result
    assert "deprecated_module_options" in result


def test_dynamic_include_marks_use_before_definition_as_uncertain(tmp_path):
    from ansibleguard.analysis_context import build_repository_analysis_context

    tasks = _write(
        tmp_path / "tasks.yml",
        "- include_vars: '{{ platform }}.yml'\n"
        "- debug:\n    msg: '{{ staged_value }}'\n"
        "- set_fact:\n    staged_value: ready\n",
    )
    context = build_repository_analysis_context(tmp_path, [tasks])

    count, details = detect_variable_use_before_definition(
        tasks,
        repository_context=context,
        parsed_document=context.document_for(tasks),
    )

    assert count == 1
    assert details[0]["semantic_status"] == "UNCERTAIN"
    assert details[0]["resolution_status"] == "RUNTIME_CONTEXT_UNCERTAIN"
    assert details[0]["resolution_evidence"]["blockers"] == ["dynamic_include"]
    assert details[0]["uncertainty_sources"] == ["dynamic_include"]
    assert details[0]["confidence"] == "low"
