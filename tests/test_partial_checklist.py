from ansibleguard.detectors.partial_checklist import (
    detect_partial_checklist_smells,
    detect_invalid_numeric_values,
    detect_invalid_task_attribute_types,
    detect_unscoped_shell_variables,
    detect_unused_registered_variables,
)
from ansibleguard.symbol_index import build_repository_symbol_index
from ansibleguard.analysis_context import build_repository_analysis_context


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


def test_complex_templated_boolean_has_unknown_runtime_type(tmp_path):
    playbook = _write(
        tmp_path / "templated.yml",
        "- name: Protect selected values\n"
        "  debug:\n"
        "    msg: safe\n"
        "  no_log: \"{{ option in protected_options | default([]) }}\"\n",
    )

    assert detect_invalid_task_attribute_types(playbook) == (0, [])


def test_pure_jinja_literals_are_checked_by_the_bounded_evaluator(tmp_path):
    playbook = _write(
        tmp_path / "literal-types.yml",
        "- name: Static expressions\n"
        "  debug: {msg: safe}\n"
        "  no_log: '{{ true }}'\n"
        "  retries: '{{ 3 }}'\n"
        "- name: Wrong static expression\n"
        "  debug: {msg: unsafe}\n"
        "  check_mode: '{{ 1 }}'\n",
    )

    count, details = detect_invalid_task_attribute_types(playbook)
    assert count == 1
    assert details[0]["attribute"] == "check_mode"


def test_static_variable_through_default_filter_has_its_real_attribute_type(tmp_path):
    playbook = _write(
        tmp_path / "default-filter.yml",
        "- hosts: all\n"
        "  vars:\n"
        "    safe_check_mode: false\n"
        "  tasks:\n"
        "    - name: Preserve known bool\n"
        "      debug: {msg: safe}\n"
        "      check_mode: '{{ safe_check_mode | default(true) }}'\n",
    )

    assert detect_invalid_task_attribute_types(playbook) == (0, [])


def test_excluded_role_default_does_not_affect_attribute_type(tmp_path):
    defaults = tmp_path / "roles" / "web" / "defaults" / "main.yml"
    defaults.parent.mkdir(parents=True)
    defaults.write_text("retry_delay: slow\n")
    tasks = tmp_path / "roles" / "web" / "tasks" / "main.yml"
    tasks.parent.mkdir(parents=True)
    tasks.write_text(
        "- name: Runtime value\n"
        "  command: /bin/true\n"
        "  delay: '{{ retry_delay }}'\n"
    )
    graph = build_repository_symbol_index(tmp_path, files=[tasks])

    assert detect_invalid_task_attribute_types(
        tasks, symbol_index=graph
    ) == (0, [])


def test_profile_selection_skips_repository_wide_unused_register_scan(
    tmp_path, monkeypatch
):
    playbook = _write(
        tmp_path / "selected.yml",
        "- name: Invalid retry\n  debug: {msg: ok}\n  retries: -1\n",
    )

    def should_not_run(path):
        raise AssertionError("disabled repository-wide detector executed")

    monkeypatch.setattr(
        "ansibleguard.detectors.partial_checklist.detect_unused_registered_variables",
        should_not_run,
    )
    result = detect_partial_checklist_smells(
        playbook, enabled_rules={"invalid-numeric-value"}
    )

    assert result["unused_registered_variables"] == 0
    assert result["invalid_numeric_values"] == 1


def test_connected_register_analysis_reuses_repository_documents(
    tmp_path, monkeypatch
):
    parent = tmp_path / "main.yml"
    child = tmp_path / "child.yml"
    parent.write_text(
        "- command: /bin/true\n  register: command_result\n"
        "- include_tasks: child.yml\n",
        encoding="utf-8",
    )
    child.write_text(
        "- debug: {msg: '{{ command_result.stdout }}'}\n", encoding="utf-8"
    )
    files = [parent, child]
    context = build_repository_analysis_context(tmp_path, files)
    graph = build_repository_symbol_index(
        tmp_path, files=files, parsed_documents=context.parsed_documents
    )
    original_load = __import__(
        "ansibleguard.detectors.partial_checklist", fromlist=["_load"]
    )._load

    def parse_once_only(path, parsed_document=None):
        if parsed_document is None:
            raise AssertionError(f"unexpected YAML reload: {path}")
        return original_load(path, parsed_document)

    monkeypatch.setattr(
        "ansibleguard.detectors.partial_checklist._load", parse_once_only
    )

    assert detect_unused_registered_variables(
        parent, symbol_index=graph,
        parsed_document=context.document_for(parent),
        repository_context=context,
    ) == (0, [])


def test_quoted_heredoc_body_is_not_shell_expanded(tmp_path):
    playbook = _write(tmp_path / "heredoc.yml", """---
- hosts: all
  tasks:
    - name: Write a script literally
      ansible.builtin.shell: |
        cat > /tmp/run.sh <<'EOF'
        echo "$UNDEFINED_BY_ANSIBLE"
        EOF
    - name: Expanded heredoc
      ansible.builtin.shell: |
        cat > /tmp/run2.sh <<EOF
        echo "$UNDEFINED_VALUE"
        EOF
""")
    count, details = detect_unscoped_shell_variables(playbook)
    assert count == 1
    assert details[0]["task_name"] == "Expanded heredoc"
