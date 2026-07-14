from ansibleguard.detectors.partial_checklist import (
    detect_invalid_numeric_values,
    detect_invalid_task_attribute_types,
    detect_unscoped_shell_variables,
    detect_unused_registered_variables,
)


def _write(path, content):
    path.write_text(content, encoding="utf-8")
    return path


def test_unused_register_and_shell_environment_scope(tmp_path):
    playbook = _write(
        tmp_path / "variables.yml",
        """- name: Variable checks
  hosts: all
  environment:
    SHARED_TOKEN: safe
  tasks:
    - name: Unused result
      command: /bin/true
      register: forgotten_result
    - name: Used result
      command: /bin/true
      register: checked_result
    - name: Inspect result
      debug:
        var: checked_result
    - name: Missing shell environment
      shell: echo $CUSTOM_TOKEN $SHARED_TOKEN $HOME
""",
    )

    count, details = detect_unused_registered_variables(playbook)
    assert count == 1
    assert details[0]["variable"] == "forgotten_result"

    count, details = detect_unscoped_shell_variables(playbook)
    assert count == 1
    assert details[0]["variables"] == ["CUSTOM_TOKEN"]


def test_task_attribute_types_and_numeric_ranges(tmp_path):
    playbook = _write(
        tmp_path / "values.yml",
        """- name: Value checks
  hosts: all
  tasks:
    - name: Invalid types
      command: /bin/true
      become: "sometimes"
      retries: "three"
      environment: NOT_A_MAPPING
      tags: 123
    - name: Invalid ranges
      debug:
        msg: bad values
      delay: -1
      vars:
        service_port: 70000
""",
    )

    type_count, type_details = detect_invalid_task_attribute_types(playbook)
    assert type_count == 4
    assert {detail["attribute"] for detail in type_details} == {
        "become",
        "retries",
        "environment",
        "tags",
    }

    value_count, value_details = detect_invalid_numeric_values(playbook)
    assert value_count == 2
    assert {detail["attribute"] for detail in value_details} == {
        "delay",
        "service_port",
    }
