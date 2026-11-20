from ansibleguard.analysis_context import build_repository_analysis_context
from ansibleguard.detectors.paper_candidates import (
    _file_role_threshold_multiplier,
    detect_broken_role_dependencies,
    detect_complex_expressions,
    detect_empty_abstractions,
    detect_excessive_nesting,
    detect_incomplete_tasks,
    detect_long_statements,
    detect_missing_abstraction,
    detect_paper_candidates,
    detect_unguarded_variables,
    detect_unstructured_module,
)
from ansibleguard.parser import mainn
from ansibleguard.report.findings import build_findings_list
from ansibleguard.symbol_index import build_repository_symbol_index


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
    - name: "TODO: replace this temporary task"
      debug:
        msg: placeholder
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
    nesting_count, nesting_details = detect_excessive_nesting(playbook)
    assert nesting_count == 1
    assert nesting_details[0]["line"] > 1
    assert detect_missing_abstraction(playbook)[0] == 1

    count, details = detect_unguarded_variables(playbook)
    assert count >= 1
    assert "missing_value" in {detail["variable"] for detail in details}
    assert "optional_value" not in {detail["variable"] for detail in details}


def test_long_statement_ignores_comment_only_lines(tmp_path):
    playbook = _write(
        tmp_path / "long-lines.yml",
        "# " + "comment " * 30 + "\nvalue: " + "x" * 130 + "\n",
    )

    count, details = detect_long_statements(playbook)

    assert count == 1
    assert details[0]["line"] == 2


def test_dependency_metadata_is_not_a_missing_task_abstraction(tmp_path):
    requirements = _write(
        tmp_path / "requirements.yml",
        "".join(f"- src: example.role_{index}\n" for index in range(20)),
    )

    assert detect_missing_abstraction(requirements) == (0, [])


def test_unguarded_variables_ignore_identifiers_inside_string_literals(tmp_path):
    playbook = _write(
        tmp_path / "literal.yml",
        "repo_matches: \"{{ repository == 'https://github.com/adfinis/project' }}\"\n",
    )

    count, details = detect_unguarded_variables(
        playbook, known_variables=("repository",)
    )

    assert count == 0
    assert details == []


def test_jinja_if_guard_protects_later_interpolation_in_same_value(tmp_path):
    variables = _write(
        tmp_path / "roles" / "app" / "defaults" / "main.yml",
        "endpoint: >-\n"
        "  {% if registry.url is defined %}"
        "https://{{ registry.url }}/api{% endif %}\n",
    )

    assert detect_unguarded_variables(variables) == (0, [])


def test_multiline_complex_expression_reports_opening_jinja_line(tmp_path):
    playbook = _write(
        tmp_path / "multiline.yml",
        """---
result: >-
  {{
    first_value | default(
      (second_value == 'yes') | ternary(third_value, fourth_value))
  }}
""",
    )

    count, details = detect_complex_expressions(playbook)

    assert count == 1
    assert details[0]["line"] == 3


def test_unguarded_expression_with_yaml_escape_reports_source_line(tmp_path):
    playbook = _write(
        tmp_path / "escaped-expression.yml",
        "---\n"
        "- name: Show audit results\n"
        "  ansible.builtin.debug:\n"
        '    msg: "{{ audit_results.split(\'\\n\') }}"\n',
    )

    count, details = detect_unguarded_variables(playbook)

    assert count == 1
    assert details[0]["variable"] == "audit_results"
    assert details[0]["line"] == 4


def test_parenthesized_unguarded_expression_with_escape_reports_source_line(
    tmp_path,
):
    playbook = _write(
        tmp_path / "parenthesized-escaped-expression.yml",
        "---\n"
        "- name: Show decoded results\n"
        "  ansible.builtin.debug:\n"
        '    msg: "{{ (audit_results | string).split(\'\\n\') }}"\n',
    )

    count, details = detect_unguarded_variables(playbook)

    assert count == 1
    assert details[0]["variable"] == "audit_results"
    assert details[0]["line"] == 4


def test_complex_expression_pass_does_not_consume_unguarded_location(tmp_path):
    playbook = _write(
        tmp_path / "shared-expression.yml",
        "---\n"
        "- name: Evaluate an expression\n"
        "  ansible.builtin.debug:\n"
        '    msg: "{{ missing_value | select(\'equalto\', 1) | list }}"\n',
    )

    metrics = detect_paper_candidates(playbook)
    details = metrics["unguarded_variables_details"]

    assert any(
        detail["variable"] == "missing_value" and detail["line"] == 4
        for detail in details
    )


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

    # A role with handlers but no task files is not structurally broken.
    assert detect_unstructured_module(anchor) == (0, [])

    dependency_count, dependency_details = detect_broken_role_dependencies(anchor)
    messages = " ".join(detail["issue"] for detail in dependency_details)
    # v0.0.4: "missing local role" check removed (0% precision — Galaxy roles are
    # not under roles/ by default). Only cycle detection is reliable.
    assert dependency_count >= 1
    assert "cycle" in messages.lower()


def test_standalone_role_structure_and_self_dependency_are_detected(tmp_path):
    role = tmp_path / "standalone_role"
    anchor = _write(
        role / "handlers" / "main.yml",
        "- name: Existing handler\n  debug:\n    msg: ok\n",
    )
    _write(role / "meta" / "main.yml", "dependencies:\n  - standalone_role\n")

    structure_count, structure_details = detect_unstructured_module(anchor)
    dependency_count, dependency_details = detect_broken_role_dependencies(anchor)

    assert structure_count == 0
    assert structure_details == []
    assert dependency_count == 1
    assert "depends on itself" in dependency_details[0]["issue"]


def test_standalone_external_dependency_is_not_assumed_broken(tmp_path):
    role = tmp_path / "standalone_role"
    anchor = _write(
        role / "tasks" / "main.yml",
        "- name: Existing task\n  debug:\n    msg: ok\n",
    )
    _write(role / "meta" / "main.yml", "dependencies:\n  - external_galaxy_role\n")

    assert detect_broken_role_dependencies(anchor) == (0, [])


def test_role_task_files_without_main_entry_point_are_unstructured(tmp_path):
    role = tmp_path / "roles" / "worker"
    anchor = _write(
        role / "tasks" / "install.yml",
        "- name: Install worker\n  debug:\n    msg: installed\n",
    )

    count, details = detect_unstructured_module(anchor)

    assert count == 1
    assert "tasks/main" in details[0]["issue"]


def test_new_metrics_flow_through_parser_and_findings(tmp_path):
    playbook = _write(
        tmp_path / "flow.yml",
        """- name: Flow
  hosts: all
  tasks:
    - name: "FIXME: unfinished placeholder task"
      debug:
        msg: placeholder
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


def test_a3_file_role_multiplier_returns_expected_values(tmp_path):
    handlers_file = tmp_path / "roles" / "myrole" / "handlers" / "main.yml"
    tasks_file = tmp_path / "roles" / "myrole" / "tasks" / "main.yml"
    playbook_file = tmp_path / "site.yml"
    assert _file_role_threshold_multiplier(handlers_file) == 0.5
    assert _file_role_threshold_multiplier(tasks_file) == 1.0
    assert _file_role_threshold_multiplier(playbook_file) == 1.5


def test_a3_handlers_file_fires_at_half_threshold(tmp_path):
    """A handler file with >5 tasks (0.5× of default 10) should fire missing-abstraction."""
    six_handlers = "\n".join(
        f"  - name: Restart service {i}\n    service:\n      name: svc{i}\n      state: restarted"
        for i in range(6)
    )
    handlers = tmp_path / "roles" / "myrole" / "handlers" / "main.yml"
    handlers.parent.mkdir(parents=True)
    handlers.write_text(f"---\n{six_handlers}\n", encoding="utf-8")
    count, _ = detect_missing_abstraction(handlers, threshold=10)
    assert count == 0  # raw function ignores path-based multiplier
    # detect_paper_candidates applies the multiplier; threshold becomes max(3, 10*0.5)=5
    from ansibleguard.detectors.paper_candidates import detect_paper_candidates
    result = detect_paper_candidates(handlers)
    assert result["missing_abstractions"] == 1


def test_same_task_when_defined_guard_protects_reference(tmp_path):
    playbook = _write(
        tmp_path / "same-task-guard.yml",
        "- name: Conditionally display result\n"
        "  debug:\n"
        "    msg: '{{ command_result.stdout }}'\n"
        "  when: command_result is defined\n",
    )

    assert detect_unguarded_variables(playbook) == (0, [])


def test_default_filter_only_guards_its_own_expression(tmp_path):
    playbook = _write(
        tmp_path / "mixed-expression-guards.yml",
        "- debug:\n"
        "    msg: \"{{ foo | default('safe') }} {{ foo }}\"\n",
    )

    count, details = detect_unguarded_variables(playbook)

    assert count == 1
    assert details[0]["variable"] == "foo"


def test_jinja_defined_region_does_not_guard_reference_after_endif(tmp_path):
    playbook = _write(
        tmp_path / "region-guards.yml",
        "- debug:\n"
        "    msg: >-\n"
        "      {% if foo is defined %}{{ foo }}{% endif %}\n"
        "      {{ foo }}\n",
    )

    count, details = detect_unguarded_variables(playbook)

    assert count == 1
    assert details[0]["variable"] == "foo"


def test_jinja_for_local_does_not_escape_endfor_region(tmp_path):
    playbook = _write(
        tmp_path / "loop-region.yml",
        "- debug:\n"
        "    msg: >-\n"
        "      {% for server in servers %}\n"
        "      {{ server.name }}\n"
        "      {% endfor %}\n"
        "      {{ server.name }}\n",
    )

    count, details = detect_unguarded_variables(
        playbook, known_variables={"servers"}
    )

    assert count == 1
    assert details[0]["variable"] == "server"


def test_jinja_raw_region_is_not_interpreted_as_ansible_variables(tmp_path):
    playbook = _write(
        tmp_path / "raw-template.yml",
        "- debug:\n"
        "    msg: >-\n"
        "      {% raw %}\n"
        "      {{ if .Alert.Status }}{{ end }}\n"
        "      {% endraw %}\n"
        "      {{ real_ansible_variable }}\n",
    )

    count, details = detect_unguarded_variables(playbook)

    assert count == 1
    assert details[0]["variable"] == "real_ansible_variable"


def test_declared_external_role_variable_is_uncertain_not_unresolved(tmp_path):
    tasks = tmp_path / "roles" / "app" / "tasks" / "main.yml"
    tasks.parent.mkdir(parents=True)
    tasks.write_text(
        "- debug: {msg: '{{ devture_systemd_docker_base_systemd_path }}'}\n",
        encoding="utf-8",
    )
    (tmp_path / "requirements.yml").write_text(
        "- name: systemd_docker_base\n"
        "  src: git+https://github.com/devture/"
        "com.devture.ansible.role.systemd_docker_base.git\n",
        encoding="utf-8",
    )
    context = build_repository_analysis_context(tmp_path, [tasks])
    graph = build_repository_symbol_index(
        tmp_path, files=[tasks], parsed_documents=context.parsed_documents
    )

    count, details = detect_unguarded_variables(
        tasks,
        symbol_index=graph,
        parsed_document=context.document_for(tasks),
        repository_context=context,
    )

    assert count == 1
    assert details[0]["semantic_status"] == "UNCERTAIN"
    assert details[0]["uncertainty_sources"] == [
        "declared_external_dependency"
    ]


def test_jinja_for_else_does_not_expose_loop_target(tmp_path):
    playbook = _write(
        tmp_path / "loop-else.yml",
        "- debug:\n"
        "    msg: >-\n"
        "      {% for server in servers %}\n"
        "      {{ server.name }}\n"
        "      {% else %}\n"
        "      {{ server.name }}\n"
        "      {% endfor %}\n",
    )

    count, details = detect_unguarded_variables(
        playbook, known_variables={"servers"}
    )

    assert count == 1
    assert details[0]["variable"] == "server"
    assert details[0]["line"] == 6


def test_jinja_set_inside_loop_does_not_escape_loop_scope(tmp_path):
    playbook = _write(
        tmp_path / "loop-set.yml",
        "- debug:\n"
        "    msg: >-\n"
        "      {% for server in servers %}\n"
        "      {% set hostname = server.name %}\n"
        "      {{ hostname }}\n"
        "      {% endfor %}\n"
        "      {{ hostname }}\n",
    )

    count, details = detect_unguarded_variables(
        playbook, known_variables={"servers"}
    )

    assert count == 1
    assert details[0]["variable"] == "hostname"
    assert details[0]["line"] == 7


def test_jinja_set_target_is_not_visible_in_its_own_rhs(tmp_path):
    playbook = tmp_path / "tasks.yml"
    playbook.write_text(
        "- debug:\n"
        "    msg: >-\n"
        "      {% set counter = counter + 1 %}\n"
        "      {{ counter }}\n",
        encoding="utf-8",
    )

    count, details = detect_unguarded_variables(playbook)

    assert count == 1
    assert details[0]["variable"] == "counter"


def test_jinja_block_set_becomes_visible_only_after_endset(tmp_path):
    playbook = tmp_path / "tasks.yml"
    playbook.write_text(
        "- debug:\n"
        "    msg: >-\n"
        "      {% set message %}{{ missing_value }}{% endset %}\n"
        "      {{ message }}\n",
        encoding="utf-8",
    )

    count, details = detect_unguarded_variables(playbook)

    assert count == 1
    assert details[0]["variable"] == "missing_value"


def test_identical_unguarded_references_are_distinct_occurrences(tmp_path):
    playbook = _write(
        tmp_path / "repeated.yml",
        "- name: First\n"
        "  debug:\n"
        "    msg: '{{ missing_value }}'\n"
        "- name: Second\n"
        "  debug:\n"
        "    msg: '{{ missing_value }}'\n",
    )

    count, details = detect_unguarded_variables(playbook)

    assert count == 2
    assert {detail["line"] for detail in details} == {3, 6}


def test_required_public_role_input_is_uncertain_not_unresolved(tmp_path):
    tasks = _write(
        tmp_path / "roles" / "database" / "tasks" / "main.yml",
        "- debug:\n    msg: '{{ database_admin_password }}'\n",
    )
    context = build_repository_analysis_context(tmp_path, [tasks])
    graph = build_repository_symbol_index(tmp_path)

    count, details = detect_unguarded_variables(
        tasks,
        symbol_index=graph,
        parsed_document=context.document_for(tasks),
        repository_context=context,
    )

    assert count == 1
    assert details[0]["semantic_status"] == "UNCERTAIN"
    assert details[0]["uncertainty_sources"] == [
        "possible_required_role_input"
    ]


def test_required_public_role_input_in_vars_file_is_uncertain(tmp_path):
    variables = _write(
        tmp_path / "roles" / "database" / "vars" / "main.yml",
        "database_url: 'postgres://{{ database_host }}/app'\n",
    )
    context = build_repository_analysis_context(tmp_path, [variables])
    graph = build_repository_symbol_index(tmp_path)

    count, details = detect_unguarded_variables(
        variables,
        symbol_index=graph,
        parsed_document=context.document_for(variables),
        repository_context=context,
    )

    assert count == 1
    assert details[0]["semantic_status"] == "UNCERTAIN"
    assert details[0]["uncertainty_sources"] == [
        "possible_required_role_input"
    ]


def test_role_argument_spec_is_first_class_external_input_evidence(tmp_path):
    tasks = _write(
        tmp_path / "roles" / "database" / "tasks" / "main.yml",
        "- debug:\n    msg: '{{ database_admin_password }}'\n",
    )
    _write(
        tmp_path / "roles" / "database" / "meta" / "argument_specs.yml",
        "argument_specs:\n"
        "  main:\n"
        "    options:\n"
        "      database_admin_password:\n"
        "        type: str\n"
        "        required: true\n",
    )
    context = build_repository_analysis_context(tmp_path, [tasks])
    graph = build_repository_symbol_index(tmp_path)

    count, details = detect_unguarded_variables(
        tasks,
        symbol_index=graph,
        parsed_document=context.document_for(tasks),
        repository_context=context,
    )

    assert count == 0
    assert details == []


def test_optional_role_argument_without_definition_remains_uncertain(tmp_path):
    tasks = _write(
        tmp_path / "roles" / "database" / "tasks" / "main.yml",
        "- debug:\n    msg: '{{ database_port }}'\n",
    )
    _write(
        tmp_path / "roles" / "database" / "meta" / "argument_specs.yml",
        "argument_specs:\n"
        "  main:\n"
        "    options:\n"
        "      database_port:\n"
        "        type: int\n",
    )
    context = build_repository_analysis_context(tmp_path, [tasks])
    graph = build_repository_symbol_index(tmp_path)

    count, details = detect_unguarded_variables(
        tasks,
        symbol_index=graph,
        parsed_document=context.document_for(tasks),
        repository_context=context,
    )

    assert count == 1
    assert details[0]["semantic_status"] == "UNCERTAIN"
    assert details[0]["resolution_status"] == "RUNTIME_CONTEXT_UNCERTAIN"
    assert details[0]["uncertainty_sources"] == [
        "declared_optional_role_argument"
    ]


def test_required_argument_from_other_role_entrypoint_does_not_suppress(tmp_path):
    tasks = _write(
        tmp_path / "roles" / "database" / "tasks" / "main.yml",
        "- debug:\n    msg: '{{ restore_archive }}'\n",
    )
    _write(
        tmp_path / "roles" / "database" / "meta" / "argument_specs.yml",
        "argument_specs:\n"
        "  restore:\n"
        "    options:\n"
        "      restore_archive:\n"
        "        required: true\n",
    )
    context = build_repository_analysis_context(tmp_path, [tasks])
    graph = build_repository_symbol_index(tmp_path)

    count, details = detect_unguarded_variables(
        tasks,
        symbol_index=graph,
        parsed_document=context.document_for(tasks),
        repository_context=context,
    )

    assert count == 1
    assert details[0]["resolution_status"] == "EXTERNAL_INPUT_UNCERTAIN"


def test_required_entrypoint_argument_does_not_suppress_imported_subtask(tmp_path):
    tasks = _write(
        tmp_path / "roles" / "database" / "tasks" / "configure.yml",
        "- debug:\n    msg: '{{ database_password }}'\n",
    )
    _write(
        tmp_path / "roles" / "database" / "meta" / "argument_specs.yml",
        "argument_specs:\n"
        "  main:\n"
        "    options:\n"
        "      database_password:\n"
        "        required: true\n",
    )
    context = build_repository_analysis_context(tmp_path, [tasks])
    graph = build_repository_symbol_index(tmp_path)

    count, details = detect_unguarded_variables(
        tasks,
        symbol_index=graph,
        parsed_document=context.document_for(tasks),
        repository_context=context,
    )

    assert count == 1
    assert details[0]["resolution_status"] == "EXTERNAL_INPUT_UNCERTAIN"


def test_inventory_precedence_input_is_uncertain_but_private_name_is_strict(
    tmp_path,
):
    variables = _write(
        tmp_path / "group_vars" / "production.yml",
        "public_url: 'https://{{ inventory_domain }}'\n"
        "private_url: 'https://{{ __internal_domain }}'\n",
    )
    context = build_repository_analysis_context(tmp_path, [variables])
    graph = build_repository_symbol_index(tmp_path)

    count, details = detect_unguarded_variables(
        variables,
        symbol_index=graph,
        parsed_document=context.document_for(variables),
        repository_context=context,
    )

    assert count == 2
    by_variable = {detail["variable"]: detail for detail in details}
    assert by_variable["inventory_domain"]["semantic_status"] == "UNCERTAIN"
    assert by_variable["inventory_domain"]["uncertainty_sources"] == [
        "possible_inventory_precedence_input"
    ]
    assert by_variable["__internal_domain"]["semantic_status"] == "UNRESOLVED"


def test_playbook_extra_var_input_includes_underscore_prefixed_names(
    tmp_path,
):
    playbook = _write(
        tmp_path / "deploy.yml",
        "- hosts: all\n"
        "  tasks:\n"
        "    - debug:\n"
        "        msg: '{{ deployment_region }} {{ _internal_region }}'\n",
    )
    context = build_repository_analysis_context(tmp_path, [playbook])
    graph = build_repository_symbol_index(tmp_path)

    count, details = detect_unguarded_variables(
        playbook,
        symbol_index=graph,
        parsed_document=context.document_for(playbook),
        repository_context=context,
    )

    assert count == 2
    by_variable = {detail["variable"]: detail for detail in details}
    assert by_variable["deployment_region"]["uncertainty_sources"] == [
        "possible_playbook_input"
    ]
    assert by_variable["_internal_region"]["semantic_status"] == "UNCERTAIN"
    assert by_variable["_internal_region"]["uncertainty_sources"] == [
        "possible_playbook_input"
    ]
    assert by_variable["_internal_region"]["variable_classification"] == (
        "undeclared-input-contract"
    )


def test_reusable_task_fragment_input_is_uncertain(tmp_path):
    tasks = _write(
        tmp_path / "common_tasks" / "configure.yml",
        "- debug:\n    msg: '{{ caller_supplied_value }}'\n",
    )
    context = build_repository_analysis_context(tmp_path, [tasks])
    graph = build_repository_symbol_index(tmp_path)

    count, details = detect_unguarded_variables(
        tasks,
        symbol_index=graph,
        parsed_document=context.document_for(tasks),
        repository_context=context,
    )

    assert count == 1
    assert details[0]["uncertainty_sources"] == [
        "possible_task_fragment_input"
    ]


def test_fail_if_undefined_guards_later_reachable_use(tmp_path):
    playbook = _write(
        tmp_path / "tasks.yml",
        "- fail:\n    msg: required\n"
        "  when: database_password is undefined\n"
        "- debug:\n    msg: '{{ database_password }}'\n",
    )

    assert detect_unguarded_variables(playbook) == (0, [])


def test_assert_defined_guards_later_reachable_use(tmp_path):
    playbook = _write(
        tmp_path / "tasks.yml",
        "- assert:\n    that:\n      - database_password is defined\n"
        "- debug:\n    msg: '{{ database_password }}'\n",
    )

    assert detect_unguarded_variables(playbook) == (0, [])


def test_variable_mapping_forward_reference_is_visible(tmp_path):
    variables = _write(
        tmp_path / "roles" / "web" / "vars" / "main.yml",
        "selected_package: '{{ package_v3 }}'\npackage_v3: nginx\n",
    )

    assert detect_unguarded_variables(variables) == (0, [])


def test_conditional_set_fact_is_uncertain_without_repository_graph(tmp_path):
    playbook = _write(
        tmp_path / "conditional-fact.yml",
        "- set_fact: {app_port: 8080}\n"
        "  when: detect_port\n"
        "- debug: {msg: '{{ app_port }}'}\n",
    )

    count, details = detect_unguarded_variables(
        playbook, known_variables={"detect_port"}
    )

    assert count == 1
    assert details[0]["semantic_status"] == "UNCERTAIN"
    assert details[0]["uncertainty_sources"] == [
        "conditional_runtime_definition"
    ]


def test_ansible_vars_magic_mapping_is_not_unguarded(tmp_path):
    playbook = _write(
        tmp_path / "vars-magic.yml",
        "- debug: {msg: \"{{ vars['database_port'] }}\"}\n",
    )

    assert detect_unguarded_variables(playbook) == (0, [])


def test_dynamic_vars_files_downgrades_unresolved_reference(tmp_path):
    playbook = _write(
        tmp_path / "site.yml",
        "- hosts: all\n"
        "  vars_files:\n"
        "    - vars/{{ deployment_environment }}.yml\n"
        "  tasks:\n"
        "    - debug: {msg: '{{ database_endpoint }}'}\n",
    )
    context = build_repository_analysis_context(tmp_path, [playbook])

    count, details = detect_unguarded_variables(
        playbook,
        known_variables={"deployment_environment"},
        parsed_document=context.document_for(playbook),
        repository_context=context,
    )

    assert count == 1
    assert details[0]["semantic_status"] == "UNCERTAIN"
    assert "dynamic_vars_files" in details[0]["uncertainty_sources"]


def test_dynamic_inventory_plugin_is_uncertainty_evidence(tmp_path):
    playbook = _write(
        tmp_path / "site.yml",
        "- hosts: all\n  tasks:\n"
        "    - debug: {msg: '{{ cloud_database_endpoint }}'}\n",
    )
    inventory = _write(
        tmp_path / "inventory" / "cloud.yml",
        "plugin: amazon.aws.aws_ec2\nregions: [eu-west-1]\n",
    )
    context = build_repository_analysis_context(
        tmp_path, [playbook, inventory]
    )

    count, details = detect_unguarded_variables(
        playbook,
        parsed_document=context.document_for(playbook),
        repository_context=context,
    )

    assert count == 1
    assert details[0]["semantic_status"] == "UNCERTAIN"
    assert "possible_dynamic_inventory_definition" in (
        details[0]["uncertainty_sources"]
    )


def test_qualified_default_filter_protects_reference(tmp_path):
    variables = _write(
        tmp_path / "qualified-default.yml",
        "selected_value: '{{ optional_value | arista.avd.default(fallback_value | default(\"safe\")) }}'\n",
    )

    assert detect_unguarded_variables(variables) == (0, [])


def test_dynamic_include_before_reference_marks_unguarded_result_uncertain(
    tmp_path
):
    from ansibleguard.analysis_context import build_repository_analysis_context

    tasks = tmp_path / "tasks.yml"
    tasks.write_text(
        "- include_vars: '{{ ansible_os_family }}.yml'\n"
        "- debug:\n    msg: '{{ runtime_value }}'\n",
        encoding="utf-8",
    )
    context = build_repository_analysis_context(tmp_path, [tasks])

    count, details = detect_unguarded_variables(
        tasks,
        parsed_document=context.document_for(tasks),
        repository_context=context,
    )

    assert count == 1
    assert details[0]["semantic_status"] == "UNCERTAIN"
    assert details[0]["confidence"] == "low"
    assert details[0]["uncertainty_sources"] == ["dynamic_include"]


def test_dynamic_include_after_reference_does_not_retroactively_add_uncertainty(
    tmp_path
):
    from ansibleguard.analysis_context import build_repository_analysis_context

    tasks = tmp_path / "tasks.yml"
    tasks.write_text(
        "- debug:\n    msg: '{{ runtime_value }}'\n"
        "- include_vars: '{{ ansible_os_family }}.yml'\n",
        encoding="utf-8",
    )
    context = build_repository_analysis_context(tmp_path, [tasks])

    _count, details = detect_unguarded_variables(
        tasks,
        parsed_document=context.document_for(tasks),
        repository_context=context,
    )

    assert details[0]["semantic_status"] == "UNRESOLVED"
    assert "uncertainty_sources" not in details[0]


def test_shared_expression_locator_wraps_for_each_detector_family(tmp_path):
    from ansibleguard.analysis_context import build_repository_analysis_context

    variables = tmp_path / "defaults.yml"
    variables.write_text(
        "computed_value: >-\n"
        "  {{ external_input | map(attribute='name') | select('equalto', 'x') | list }}\n",
        encoding="utf-8",
    )
    context = build_repository_analysis_context(tmp_path, [variables])

    metrics = detect_paper_candidates(
        variables,
        parsed_document=context.document_for(variables),
        repository_context=context,
    )

    detail = next(
        item for item in metrics["unguarded_variables_details"]
        if item["variable"] == "external_input"
    )
    assert detail["line"] == 2


def test_preceding_custom_facts_module_makes_reference_uncertain(tmp_path):
    from ansibleguard.analysis_context import build_repository_analysis_context

    playbook = tmp_path / "custom-facts.yml"
    playbook.write_text(
        "- name: Collect vendor facts\n"
        "  vendor.device_facts:\n"
        "    target: switch\n"
        "- name: Use discovered value\n"
        "  debug:\n"
        "    msg: '{{ device_serial_number }}'\n",
        encoding="utf-8",
    )
    context = build_repository_analysis_context(tmp_path, [playbook])

    metrics = detect_paper_candidates(
        playbook,
        parsed_document=context.document_for(playbook),
        repository_context=context,
    )
    detail = next(
        item for item in metrics["unguarded_variables_details"]
        if item["variable"] == "device_serial_number"
    )

    assert detail["semantic_status"] == "UNCERTAIN"
    assert "custom_module_fact" in detail["uncertainty_sources"]
