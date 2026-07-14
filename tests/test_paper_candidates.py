from ansibleguard.detectors.paper_candidates import (
    detect_broken_role_dependencies,
    detect_complex_expressions,
    detect_empty_abstractions,
    detect_excessive_nesting,
    detect_incomplete_tasks,
    detect_long_statements,
    detect_missing_abstraction,
    detect_unguarded_variables,
    detect_unstructured_module,
)
from ansibleguard.parser import mainn
from ansibleguard.report.findings import build_findings_list


def _write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_source_and_task_level_paper_detectors(tmp_path):
    repeated_tasks = "\n".join(
        f"    - name: Ordinary task {index}\n      debug:\n        msg: ok"
        for index in range(11)
    )
    playbook = _write(
        tmp_path / "playbook.yml",
        """---
- name: Detector exercise
  hosts: all
  tasks:
    # TODO: replace this temporary task
    - name: Complex condition
      debug:
        msg: "{{ missing_value }}"
      when: "(enabled and installed) or (forced and not skipped) or version >= 2"
    - name: Guarded value
      debug:
        msg: "{{ optional_value | default('safe') }}"
    - name: Empty wrapper
      block: []
    - name: Level one
      block:
        - name: Level two
          block:
            - name: Level three
              block:
                - name: Level four
                  block:
                    - name: Too deep
                      debug:
                        msg: nested
    - name: Long source line
      debug:
        msg: """ + "x" * 140 + "\n" + repeated_tasks + "\n",
    )

    assert detect_complex_expressions(playbook)[0] == 1
    assert detect_incomplete_tasks(playbook)[0] == 1
    assert detect_long_statements(playbook)[0] >= 1
    assert detect_empty_abstractions(playbook)[0] == 1
    assert detect_excessive_nesting(playbook)[0] == 1
    assert detect_missing_abstraction(playbook)[0] == 1

    count, details = detect_unguarded_variables(playbook)
    assert count >= 1
    assert "missing_value" in {detail["variable"] for detail in details}
    assert "optional_value" not in {detail["variable"] for detail in details}


def test_role_structure_and_dependency_detectors(tmp_path):
    role_a = tmp_path / "roles" / "role_a"
    role_b = tmp_path / "roles" / "role_b"
    anchor = _write(
        role_a / "handlers" / "main.yml",
        "- name: Existing handler\n  debug:\n    msg: ok\n",
    )
    _write(
        role_a / "meta" / "main.yml",
        "dependencies:\n  - role_b\n  - missing_role\n",
    )
    _write(
        role_b / "tasks" / "main.yml",
        "- name: Role B task\n  debug:\n    msg: ok\n",
    )
    _write(role_b / "meta" / "main.yml", "dependencies:\n  - role_a\n")

    structure_count, structure_details = detect_unstructured_module(anchor)
    assert structure_count == 1
    assert "tasks/main" in structure_details[0]["issue"]

    dependency_count, dependency_details = detect_broken_role_dependencies(anchor)
    messages = " ".join(detail["issue"] for detail in dependency_details)
    assert dependency_count >= 2
    assert "missing_role" in messages
    assert "cycle" in messages.lower()


def test_new_metrics_flow_through_parser_and_findings(tmp_path):
    playbook = _write(
        tmp_path / "flow.yml",
        """- name: Flow
  hosts: all
  tasks:
    # FIXME: unfinished
    - name: Unsafe reference
      debug:
        msg: "{{ undefined_setting }}"
""",
    )
    metrics = mainn(playbook)
    assert metrics["incomplete_tasks"] == 1
    assert metrics["unguarded_variables"] >= 1

    result = {
        "playbook": {
            "metrics": {"WarningUnusedIncludeVars": []},
            "plays": [],
        }
    }
    findings = build_findings_list(metrics, result, [], [], playbook)
    rule_ids = {finding["rule_id"] for finding in findings}
    assert "incomplete-task" in rule_ids
    assert "unguarded-variable" in rule_ids
