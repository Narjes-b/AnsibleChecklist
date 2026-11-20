import pytest

from ansibleguard.analysis_context import build_repository_analysis_context
from ansibleguard.detectors.paper_candidates import detect_unguarded_variables
from ansibleguard.symbol_index import build_repository_symbol_index


def test_repository_symbol_index_collects_provenance_and_resolves_uses(tmp_path):
    (tmp_path / "group_vars").mkdir()
    (tmp_path / "group_vars" / "all.yml").write_text(
        "inventory_value: available\n", encoding="utf-8"
    )
    playbook = tmp_path / "site.yml"
    playbook.write_text(
        """- name: Index
  hosts: all
  vars:
    play_value: yes
  tasks:
    - set_fact:
        fact_value: true
    - debug:
        msg: "{{ inventory_value }} {{ play_value }} {{ fact_value }} {{ missing_value }}"
""",
        encoding="utf-8",
    )

    index = build_repository_symbol_index(tmp_path, known_variables=["runtime_value"])
    assert {"inventory_value", "play_value", "fact_value", "runtime_value"} <= index.names
    assert index.metadata()["definition_count"] >= 4
    assert len(index.metadata()["sha256"]) == 64
    assert len(index.metadata()["graph_input_sha256"]) == 64
    assert {"files", "roles", "names", "kinds", "plays", "tasks", "host_scopes"} <= set(
        index.metadata()["indexes"]
    )

    count, details = detect_unguarded_variables(playbook, symbol_index=index)
    assert count == 1
    assert details[0]["variable"] == "missing_value"


def test_visibility_candidate_lookup_does_not_scan_all_definitions(tmp_path):
    consumer = tmp_path / "roles" / "consumer" / "tasks" / "main.yml"
    consumer.parent.mkdir(parents=True)
    consumer.write_text("- debug: {msg: '{{ local_value }}'}\n", encoding="utf-8")
    defaults = tmp_path / "roles" / "consumer" / "defaults" / "main.yml"
    defaults.parent.mkdir(parents=True)
    defaults.write_text("local_value: ready\n", encoding="utf-8")
    for index in range(100):
        unrelated = tmp_path / "roles" / f"unrelated-{index}" / "defaults" / "main.yml"
        unrelated.parent.mkdir(parents=True)
        unrelated.write_text(f"unrelated_{index}: true\n", encoding="utf-8")

    graph = build_repository_symbol_index(tmp_path)
    # Replacing the all-definitions tuple after index construction makes an
    # accidental full scan observable while leaving the immutable indexes
    # used by the query intact.
    object.__setattr__(graph, "definitions", None)

    assert graph.names_for(consumer) == frozenset({"local_value"})


def test_symbol_index_collects_register_loop_and_included_vars(tmp_path):
    (tmp_path / "extra.yml").write_text("included_value: yes\n", encoding="utf-8")
    playbook = tmp_path / "tasks.yml"
    playbook.write_text(
        """- include_vars: extra.yml
- command: echo ok
  register: command_result
- debug:
    msg: "{{ custom_item }}"
  loop: []
  loop_control:
    loop_var: custom_item
""",
        encoding="utf-8",
    )
    index = build_repository_symbol_index(tmp_path)
    assert {"included_value", "command_result", "custom_item"} <= index.names


def test_symbol_index_ignores_malformed_roles_and_vars_files(tmp_path):
    (tmp_path / "malformed.yml").write_text(
        """- name: Malformed fixture
  hosts: localhost
  roles: 123
  vars_files: 456
  vars:
    valid_value: present
""",
        encoding="utf-8",
    )

    index = build_repository_symbol_index(tmp_path)

    assert "valid_value" in index.names


def test_symbol_visibility_is_role_scoped_but_inventory_is_global(tmp_path):
    (tmp_path / "group_vars").mkdir()
    (tmp_path / "group_vars" / "all.yml").write_text("global_value: yes\n")
    role_a = tmp_path / "roles" / "a"
    role_b = tmp_path / "roles" / "b"
    for role in (role_a, role_b):
        (role / "tasks").mkdir(parents=True)
    (role_a / "defaults").mkdir()
    (role_a / "defaults" / "main.yml").write_text("a_value: yes\n")
    a_tasks = role_a / "tasks" / "main.yml"
    b_tasks = role_b / "tasks" / "main.yml"
    a_tasks.write_text("- debug: {msg: '{{ a_value }}'}\n")
    b_tasks.write_text("- debug: {msg: '{{ global_value }}'}\n")

    index = build_repository_symbol_index(tmp_path)

    assert {"a_value", "global_value"} <= index.names_for(a_tasks)
    assert "global_value" in index.names_for(b_tasks)
    assert "a_value" not in index.names_for(b_tasks)


def test_nested_role_collection_resolves_actual_role_root(tmp_path):
    role_a = tmp_path / "roles" / "custom" / "matrix-base"
    role_b = tmp_path / "roles" / "custom" / "matrix-service"
    defaults = role_a / "defaults" / "main.yml"
    producer_tasks = role_a / "tasks" / "main.yml"
    consumer_tasks = role_b / "tasks" / "main.yml"
    defaults.parent.mkdir(parents=True)
    producer_tasks.parent.mkdir(parents=True)
    consumer_tasks.parent.mkdir(parents=True)
    defaults.write_text("matrix_user_name: matrix\n", encoding="utf-8")
    producer_tasks.write_text(
        "- debug: {msg: '{{ matrix_user_name }}'}\n", encoding="utf-8"
    )
    consumer_tasks.write_text(
        "- debug: {msg: '{{ matrix_user_name }}'}\n", encoding="utf-8"
    )

    index = build_repository_symbol_index(tmp_path)

    assert "matrix_user_name" in index.names_for(producer_tasks)
    assert "matrix_user_name" not in index.names_for(consumer_tasks)


def test_prior_nested_role_defaults_reach_literal_role_path_include(tmp_path):
    playbook = tmp_path / "setup.yml"
    base = tmp_path / "roles" / "custom" / "matrix-base"
    service = tmp_path / "roles" / "custom" / "matrix-service"
    defaults = base / "defaults" / "main.yml"
    base_tasks = base / "tasks" / "main.yml"
    service_main = service / "tasks" / "main.yml"
    service_install = service / "tasks" / "install.yml"
    for path in (defaults, base_tasks, service_main, service_install):
        path.parent.mkdir(parents=True, exist_ok=True)
    playbook.write_text(
        "- hosts: all\n"
        "  roles:\n"
        "    - custom/matrix-base\n"
        "    - custom/matrix-service\n",
        encoding="utf-8",
    )
    defaults.write_text("matrix_user_name: matrix\n", encoding="utf-8")
    base_tasks.write_text("- debug: {msg: ready}\n", encoding="utf-8")
    service_main.write_text(
        "- include_tasks: '{{ role_path }}/tasks/install.yml'\n",
        encoding="utf-8",
    )
    service_install.write_text(
        "- debug: {msg: '{{ matrix_user_name }}'}\n", encoding="utf-8"
    )
    files = [playbook, defaults, base_tasks, service_main, service_install]
    context = build_repository_analysis_context(tmp_path, files)
    index = build_repository_symbol_index(
        tmp_path, files=files, parsed_documents=context.parsed_documents
    )

    assert detect_unguarded_variables(
        service_install,
        symbol_index=index,
        parsed_document=context.document_for(service_install),
        repository_context=context.with_symbol_graph(index),
    ) == (0, [])


def test_dynamic_include_candidates_receive_call_vars_as_may_only(tmp_path):
    caller = tmp_path / "roles" / "cloud" / "tasks" / "main.yml"
    candidate = caller.parent / "provision_ec2.yml"
    disconnected = caller.parent / "teardown_ec2.yml"
    caller.parent.mkdir(parents=True)
    caller.write_text(
        "- include_tasks: 'provision_{{ res_def.role }}.yml'\n"
        "  vars:\n"
        "    res_def: '{{ resource }}'\n",
        encoding="utf-8",
    )
    candidate.write_text(
        "- debug: {msg: '{{ res_def.name }}'}\n", encoding="utf-8"
    )
    disconnected.write_text(
        "- debug: {msg: '{{ res_def.name }}'}\n", encoding="utf-8"
    )
    files = [caller, candidate, disconnected]
    context = build_repository_analysis_context(tmp_path, files)
    graph = build_repository_symbol_index(
        tmp_path, files=files, parsed_documents=context.parsed_documents
    )

    assert graph.definition_visibility("res_def", candidate, 0, 0) == "may"
    assert "dynamic_include" in graph.definition_uncertainty_sources(
        "res_def", candidate, 0, 0
    )
    assert graph.definition_visibility("res_def", disconnected, 0, 0) == "none"


def test_vars_file_names_are_visible_from_referring_playbook(tmp_path):
    (tmp_path / "vars").mkdir()
    (tmp_path / "vars" / "production.yml").write_text("release_channel: stable\n")
    playbook = tmp_path / "site.yml"
    playbook.write_text(
        "- hosts: all\n  vars_files: [vars/production.yml]\n"
        "  tasks:\n    - debug: {msg: '{{ release_channel }}'}\n"
    )

    assert "release_channel" in build_repository_symbol_index(tmp_path).names_for(playbook)


def test_role_parameters_are_visible_only_to_destination_role(tmp_path):
    playbook = tmp_path / "site.yml"
    playbook.write_text(
        "- hosts: all\n  roles:\n"
        "    - role: web\n      web_port: 8080\n",
        encoding="utf-8",
    )
    web = tmp_path / "roles" / "web" / "tasks" / "main.yml"
    db = tmp_path / "roles" / "db" / "tasks" / "main.yml"
    for path in (web, db):
        path.parent.mkdir(parents=True)
        path.write_text("- debug: {msg: ok}\n", encoding="utf-8")

    index = build_repository_symbol_index(tmp_path)

    assert "web_port" in index.names_for(web)
    assert "web_port" not in index.names_for(db)


def test_unrelated_role_definition_does_not_satisfy_unguarded_input(tmp_path):
    role_a = tmp_path / "roles" / "producer" / "defaults" / "main.yml"
    role_a.parent.mkdir(parents=True)
    role_a.write_text("shared_endpoint: https://example.invalid\n", encoding="utf-8")
    consumer = tmp_path / "roles" / "consumer" / "tasks" / "main.yml"
    consumer.parent.mkdir(parents=True)
    consumer.write_text("- debug: {msg: '{{ shared_endpoint }}'}\n", encoding="utf-8")

    index = build_repository_symbol_index(tmp_path)

    assert "shared_endpoint" not in index.names_for(consumer)
    count, details = detect_unguarded_variables(consumer, symbol_index=index)
    assert count == 1
    assert details[0]["variable"] == "shared_endpoint"


def test_explicit_graph_population_excludes_fixture_definitions(tmp_path):
    production = tmp_path / "roles" / "web" / "tasks" / "main.yml"
    production.parent.mkdir(parents=True)
    production.write_text("- debug: {msg: '{{ fixture_only }}'}\n", encoding="utf-8")
    fixture = tmp_path / "group_vars" / "fixture.yml"
    fixture.parent.mkdir()
    fixture.write_text("fixture_only: yes\n", encoding="utf-8")

    index = build_repository_symbol_index(tmp_path, files=[production])

    assert "fixture_only" not in index.names
    assert index.metadata()["graph_input_count"] == 1
    assert detect_unguarded_variables(production, symbol_index=index)[0] == 1


def test_static_names_exclude_task_created_values(tmp_path):
    tasks = tmp_path / "roles" / "web" / "tasks" / "main.yml"
    tasks.parent.mkdir(parents=True)
    tasks.write_text(
        "- command: /bin/true\n  register: command_result\n"
        "- set_fact:\n    computed_value: ready\n",
        encoding="utf-8",
    )
    index = build_repository_symbol_index(tmp_path)

    assert {"command_result", "computed_value"} <= index.names_for(tasks)
    assert "command_result" not in index.static_names_for(tasks)
    assert "computed_value" not in index.static_names_for(tasks)


def test_disconnected_role_task_runtime_value_does_not_hide_unguarded_use(tmp_path):
    producer = tmp_path / "roles" / "web" / "tasks" / "producer.yml"
    consumer = tmp_path / "roles" / "web" / "tasks" / "consumer.yml"
    producer.parent.mkdir(parents=True)
    producer.write_text("- set_fact:\n    runtime_value: ready\n")
    consumer.write_text("- debug: {msg: '{{ runtime_value }}'}\n")

    graph = build_repository_symbol_index(tmp_path)

    assert "runtime_value" in graph.names_for(consumer)
    assert "runtime_value" not in graph.static_names_for(consumer)
    assert detect_unguarded_variables(consumer, symbol_index=graph)[0] == 1


@pytest.mark.parametrize("action", ("include_tasks", "import_tasks"))
def test_runtime_definition_reaches_statically_included_task_file(
    tmp_path, action
):
    parent = tmp_path / "roles" / "web" / "tasks" / "main.yml"
    child = tmp_path / "roles" / "web" / "tasks" / "configure.yml"
    parent.parent.mkdir(parents=True)
    parent.write_text(
        "- set_fact:\n"
        "    app_port: 8080\n"
        f"- {action}: configure.yml\n",
        encoding="utf-8",
    )
    child.write_text(
        "- debug:\n"
        "    msg: '{{ app_port }}'\n",
        encoding="utf-8",
    )
    context = build_repository_analysis_context(tmp_path, [parent, child])
    graph = build_repository_symbol_index(
        tmp_path,
        files=[parent, child],
        parsed_documents=context.parsed_documents,
    )

    assert detect_unguarded_variables(
        child,
        symbol_index=graph,
        parsed_document=context.document_for(child),
        repository_context=context,
    ) == (0, [])


def test_play_vars_reach_statically_included_file(tmp_path):
    parent = tmp_path / "site.yml"
    child = tmp_path / "configure.yml"
    parent.write_text(
        "- hosts: all\n"
        "  vars:\n"
        "    app_port: 8080\n"
        "  tasks:\n"
        "    - include_tasks: configure.yml\n",
        encoding="utf-8",
    )
    child.write_text("- debug: {msg: '{{ app_port }}'}\n", encoding="utf-8")
    context = build_repository_analysis_context(tmp_path, [parent, child])
    graph = build_repository_symbol_index(
        tmp_path, files=[parent, child],
        parsed_documents=context.parsed_documents,
    )

    assert detect_unguarded_variables(
        child, symbol_index=graph,
        parsed_document=context.document_for(child),
        repository_context=context,
    ) == (0, [])


def test_include_task_vars_and_custom_loop_var_reach_included_file(tmp_path):
    parent = tmp_path / "main.yml"
    child = tmp_path / "configure.yml"
    parent.write_text(
        "- include_tasks: configure.yml\n"
        "  vars:\n"
        "    app_port: 8080\n"
        "  loop: [one]\n"
        "  loop_control:\n"
        "    loop_var: selected_app\n",
        encoding="utf-8",
    )
    child.write_text(
        "- debug: {msg: '{{ app_port }} {{ selected_app }}'}\n",
        encoding="utf-8",
    )
    context = build_repository_analysis_context(tmp_path, [parent, child])
    graph = build_repository_symbol_index(
        tmp_path, files=[parent, child],
        parsed_documents=context.parsed_documents,
    )

    assert detect_unguarded_variables(
        child, symbol_index=graph,
        parsed_document=context.document_for(child),
        repository_context=context,
    ) == (0, [])


@pytest.mark.parametrize("action", ("include_tasks", "import_tasks"))
def test_child_set_fact_reaches_caller_continuation(tmp_path, action):
    parent = tmp_path / "main.yml"
    child = tmp_path / "prepare.yml"
    parent.write_text(
        f"- {action}: prepare.yml\n"
        "- debug: {msg: '{{ generated_port }}'}\n",
        encoding="utf-8",
    )
    child.write_text(
        "- set_fact:\n    generated_port: 8080\n", encoding="utf-8"
    )
    context = build_repository_analysis_context(tmp_path, [parent, child])
    graph = build_repository_symbol_index(
        tmp_path, files=[parent, child],
        parsed_documents=context.parsed_documents,
    )

    assert detect_unguarded_variables(
        parent, symbol_index=graph,
        parsed_document=context.document_for(parent),
        repository_context=context,
    ) == (0, [])


@pytest.mark.parametrize("action", ("include_tasks", "import_tasks"))
def test_child_register_reaches_caller_continuation(tmp_path, action):
    parent = tmp_path / "main.yml"
    child = tmp_path / "prepare.yml"
    parent.write_text(
        f"- {action}: prepare.yml\n"
        "- debug: {msg: '{{ generated_result.stdout }}'}\n",
        encoding="utf-8",
    )
    child.write_text(
        "- command: /bin/echo ready\n"
        "  register: generated_result\n",
        encoding="utf-8",
    )
    files = [parent, child]
    context = build_repository_analysis_context(tmp_path, files)
    graph = build_repository_symbol_index(
        tmp_path, files=files, parsed_documents=context.parsed_documents
    )

    assert graph.definition_visibility(
        "generated_result", parent, 1, 0
    ) == "must"
    assert detect_unguarded_variables(
        parent,
        symbol_index=graph,
        parsed_document=context.document_for(parent),
        repository_context=context,
    ) == (0, [])


@pytest.mark.parametrize("action", ("include_tasks", "import_tasks"))
def test_child_include_vars_reaches_caller_continuation(tmp_path, action):
    parent = tmp_path / "main.yml"
    child = tmp_path / "prepare.yml"
    variables = tmp_path / "runtime-vars.yml"
    parent.write_text(
        f"- {action}: prepare.yml\n"
        "- debug: {msg: '{{ generated_port }}'}\n",
        encoding="utf-8",
    )
    child.write_text(
        "- include_vars: runtime-vars.yml\n", encoding="utf-8"
    )
    variables.write_text("generated_port: 8080\n", encoding="utf-8")
    files = [parent, child, variables]
    context = build_repository_analysis_context(tmp_path, files)
    graph = build_repository_symbol_index(
        tmp_path, files=files, parsed_documents=context.parsed_documents
    )

    assert graph.definition_visibility(
        "generated_port", parent, 1, 0
    ) == "must"
    assert detect_unguarded_variables(
        parent,
        symbol_index=graph,
        parsed_document=context.document_for(parent),
        repository_context=context,
    ) == (0, [])


def test_nested_child_definition_reaches_outer_caller_continuation(tmp_path):
    parent = tmp_path / "main.yml"
    middle = tmp_path / "middle.yml"
    child = tmp_path / "prepare.yml"
    parent.write_text(
        "- include_tasks: middle.yml\n"
        "- debug: {msg: '{{ generated_port }}'}\n",
        encoding="utf-8",
    )
    middle.write_text(
        "- import_tasks: prepare.yml\n", encoding="utf-8"
    )
    child.write_text(
        "- set_fact: {generated_port: 8080}\n", encoding="utf-8"
    )
    files = [parent, middle, child]
    context = build_repository_analysis_context(tmp_path, files)
    graph = build_repository_symbol_index(
        tmp_path, files=files, parsed_documents=context.parsed_documents
    )

    assert graph.definition_visibility(
        "generated_port", parent, 1, 0
    ) == "must"
    assert detect_unguarded_variables(
        parent,
        symbol_index=graph,
        parsed_document=context.document_for(parent),
        repository_context=context,
    ) == (0, [])


@pytest.mark.parametrize("action", ("include_tasks", "import_tasks"))
def test_conditional_child_output_is_uncertain_in_caller(tmp_path, action):
    parent = tmp_path / "main.yml"
    child = tmp_path / "prepare.yml"
    parent.write_text(
        f"- {action}: prepare.yml\n"
        "  when: prepare_enabled\n"
        "- debug: {msg: '{{ generated_port }}'}\n",
        encoding="utf-8",
    )
    child.write_text(
        "- set_fact: {generated_port: 8080}\n", encoding="utf-8"
    )
    files = [parent, child]
    context = build_repository_analysis_context(tmp_path, files)
    graph = build_repository_symbol_index(
        tmp_path, files=files, parsed_documents=context.parsed_documents
    )

    count, details = detect_unguarded_variables(
        parent,
        known_variables={"prepare_enabled"},
        symbol_index=graph,
        parsed_document=context.document_for(parent),
        repository_context=context,
    )

    assert graph.definition_visibility(
        "generated_port", parent, 1, 0
    ) == "may"
    assert count == 1
    assert details[0]["semantic_status"] == "UNCERTAIN"


def test_dynamic_include_output_is_uncertain_not_repo_visible(tmp_path):
    parent = tmp_path / "main.yml"
    disconnected = tmp_path / "prepare.yml"
    parent.write_text(
        "- include_tasks: '{{ selected_task_file }}'\n"
        "- debug: {msg: '{{ generated_port }}'}\n",
        encoding="utf-8",
    )
    disconnected.write_text(
        "- set_fact: {generated_port: 8080}\n", encoding="utf-8"
    )
    files = [parent, disconnected]
    context = build_repository_analysis_context(tmp_path, files)
    graph = build_repository_symbol_index(
        tmp_path, files=files, parsed_documents=context.parsed_documents
    )

    count, details = detect_unguarded_variables(
        parent,
        known_variables={"selected_task_file"},
        symbol_index=graph,
        parsed_document=context.document_for(parent),
        repository_context=context,
    )

    assert graph.definition_visibility(
        "generated_port", parent, 1, 0
    ) == "none"
    assert count == 1
    assert details[0]["semantic_status"] == "UNCERTAIN"
    assert "dynamic_include" in details[0]["uncertainty_sources"]


def test_conditional_child_definition_is_only_maybe_visible_to_caller(tmp_path):
    parent = tmp_path / "main.yml"
    child = tmp_path / "prepare.yml"
    parent.write_text(
        "- include_tasks: prepare.yml\n"
        "  when: prepare_enabled\n"
        "- debug: {msg: '{{ generated_port }}'}\n",
        encoding="utf-8",
    )
    child.write_text(
        "- set_fact: {generated_port: 8080}\n", encoding="utf-8"
    )
    context = build_repository_analysis_context(tmp_path, [parent, child])
    graph = build_repository_symbol_index(
        tmp_path, files=[parent, child],
        parsed_documents=context.parsed_documents,
    )

    count, details = detect_unguarded_variables(
        parent, known_variables={"prepare_enabled"}, symbol_index=graph,
        parsed_document=context.document_for(parent),
        repository_context=context,
    )

    assert count == 1
    assert details[0]["variable"] == "generated_port"
    assert details[0]["semantic_status"] == "UNCERTAIN"


def test_conditional_set_fact_is_may_defined_for_later_same_file_use(tmp_path):
    tasks = tmp_path / "main.yml"
    tasks.write_text(
        "- set_fact: {app_port: 8080}\n"
        "  when: detect_port\n"
        "- debug: {msg: '{{ app_port }}'}\n",
        encoding="utf-8",
    )
    context = build_repository_analysis_context(tmp_path, [tasks])
    graph = build_repository_symbol_index(
        tmp_path, files=[tasks], parsed_documents=context.parsed_documents
    )

    count, details = detect_unguarded_variables(
        tasks, known_variables={"detect_port"}, symbol_index=graph,
        parsed_document=context.document_for(tasks),
        repository_context=context,
    )

    assert graph.definition_visibility("app_port", tasks, 1, 0) == "may"
    assert count == 1
    assert details[0]["semantic_status"] == "UNCERTAIN"


def test_conditional_set_fact_is_may_defined_in_statically_included_child(
    tmp_path,
):
    parent = tmp_path / "main.yml"
    child = tmp_path / "configure.yml"
    parent.write_text(
        "- set_fact: {app_port: 8080}\n"
        "  when: detect_port\n"
        "- include_tasks: configure.yml\n",
        encoding="utf-8",
    )
    child.write_text("- debug: {msg: '{{ app_port }}'}\n", encoding="utf-8")
    files = [parent, child]
    context = build_repository_analysis_context(tmp_path, files)
    graph = build_repository_symbol_index(
        tmp_path, files=files, parsed_documents=context.parsed_documents
    )

    count, details = detect_unguarded_variables(
        child, symbol_index=graph,
        parsed_document=context.document_for(child),
        repository_context=context,
    )

    assert graph.definition_visibility("app_port", child, 0, 0) == "may"
    assert count == 1
    assert details[0]["semantic_status"] == "UNCERTAIN"


def test_conditional_child_set_fact_is_may_defined_in_caller_continuation(
    tmp_path,
):
    parent = tmp_path / "main.yml"
    child = tmp_path / "prepare.yml"
    parent.write_text(
        "- include_tasks: prepare.yml\n"
        "- debug: {msg: '{{ generated_port }}'}\n",
        encoding="utf-8",
    )
    child.write_text(
        "- set_fact: {generated_port: 8080}\n"
        "  when: calculate_port\n",
        encoding="utf-8",
    )
    files = [parent, child]
    context = build_repository_analysis_context(tmp_path, files)
    graph = build_repository_symbol_index(
        tmp_path, files=files, parsed_documents=context.parsed_documents
    )

    count, details = detect_unguarded_variables(
        parent, symbol_index=graph,
        parsed_document=context.document_for(parent),
        repository_context=context,
    )

    assert graph.definition_visibility("generated_port", parent, 1, 0) == "may"
    assert count == 1
    assert details[0]["semantic_status"] == "UNCERTAIN"


def test_conditional_register_root_remains_must_defined(tmp_path):
    tasks = tmp_path / "main.yml"
    tasks.write_text(
        "- command: /bin/true\n"
        "  when: run_command\n"
        "  register: command_result\n"
        "- debug: {msg: '{{ command_result }}'}\n",
        encoding="utf-8",
    )
    graph = build_repository_symbol_index(tmp_path)

    assert graph.definition_visibility("command_result", tasks, 1, 0) == "must"


def test_static_include_cycle_downgrades_cross_cycle_definition_to_may(tmp_path):
    first = tmp_path / "a.yml"
    second = tmp_path / "b.yml"
    first.write_text(
        "- set_fact: {cycle_value: ready}\n"
        "- include_tasks: b.yml\n",
        encoding="utf-8",
    )
    second.write_text(
        "- debug: {msg: '{{ cycle_value }}'}\n"
        "- include_tasks: a.yml\n",
        encoding="utf-8",
    )
    files = [first, second]
    context = build_repository_analysis_context(tmp_path, files)
    graph = build_repository_symbol_index(
        tmp_path, files=files, parsed_documents=context.parsed_documents
    )

    count, details = detect_unguarded_variables(
        second, symbol_index=graph,
        parsed_document=context.document_for(second),
        repository_context=context,
    )

    assert graph.metadata()["cyclic_execution_edge_count"] == 2
    assert graph.definition_visibility("cycle_value", second, 0, 0) == "may"
    assert count == 1
    assert details[0]["semantic_status"] == "UNCERTAIN"


def test_conditional_block_include_vars_and_custom_facts_remain_may(tmp_path):
    tasks = tmp_path / "main.yml"
    variables = tmp_path / "vars.yml"
    variables.write_text("imported_port: 8080\n", encoding="utf-8")
    tasks.write_text(
        "- block:\n"
        "    - set_fact: {block_port: 8081}\n"
        "  when: block_enabled\n"
        "- include_vars:\n"
        "    file: vars.yml\n"
        "    name: imported\n"
        "  when: vars_enabled\n"
        "- vendor.device_facts: {}\n"
        "  when: facts_enabled\n"
        "- debug:\n"
        "    msg: '{{ block_port }} {{ imported }} {{ device_model }}'\n",
        encoding="utf-8",
    )
    files = [tasks, variables]
    context = build_repository_analysis_context(tmp_path, files)
    graph = build_repository_symbol_index(
        tmp_path,
        files=files,
        parsed_documents=context.parsed_documents,
        custom_module_facts_by_file={
            tasks: {"vendor.device_facts": ["device_model"]}
        },
    )

    assert graph.definition_visibility("block_port", tasks, 4, 0) == "may"
    assert graph.definition_visibility("imported", tasks, 4, 0) == "may"
    assert graph.definition_visibility("device_model", tasks, 4, 0) == "may"
    conditional_kinds = {
        item.kind for item in graph.definitions if item.conditional
    }
    assert {
        "set-fact", "included-vars-namespace",
        "custom-module-fact",
    } <= conditional_kinds
    assert "included-vars" not in conditional_kinds


def test_multiple_static_callers_do_not_union_definitions_as_certain(tmp_path):
    caller_a = tmp_path / "caller-a.yml"
    caller_b = tmp_path / "caller-b.yml"
    child = tmp_path / "child.yml"
    caller_a.write_text(
        "- set_fact: {x: ready}\n- include_tasks: child.yml\n",
        encoding="utf-8",
    )
    caller_b.write_text("- include_tasks: child.yml\n", encoding="utf-8")
    child.write_text("- debug: {msg: '{{ x }}'}\n", encoding="utf-8")
    files = [caller_a, caller_b, child]
    context = build_repository_analysis_context(tmp_path, files)
    graph = build_repository_symbol_index(
        tmp_path, files=files, parsed_documents=context.parsed_documents
    )

    count, details = detect_unguarded_variables(
        child, symbol_index=graph,
        parsed_document=context.document_for(child),
        repository_context=context,
    )

    assert count == 1
    assert details[0]["semantic_status"] == "UNCERTAIN"
    assert details[0]["uncertainty_sources"] == [
        "multiple_include_call_sites",
        "static_include_execution_context",
    ]


def test_symbol_graph_exposes_edges_and_location_apis(tmp_path):
    included = tmp_path / "included.yml"
    included.write_text("- debug: {msg: ok}\n")
    tasks = tmp_path / "tasks.yml"
    tasks.write_text(
        "- import_tasks: included.yml\n"
        "- command: /bin/true\n  register: command_result\n"
    )

    graph = build_repository_symbol_index(tmp_path)

    assert any(edge.kind == "import_tasks" for edge in graph.edges)
    assert graph.possible_definitions_of("command_result", tasks)
    assert "command_result" not in graph.visible_names_at(tasks, task_index=1)
    assert "command_result" in graph.visible_names_at(tasks, task_index=2)


def test_standalone_role_defaults_are_visible(tmp_path):
    defaults = tmp_path / "defaults" / "main.yml"
    defaults.parent.mkdir()
    defaults.write_text("standalone_port: 8080\n")
    tasks = tmp_path / "tasks" / "main.yml"
    tasks.parent.mkdir()
    tasks.write_text("- debug: {msg: '{{ standalone_port }}'}\n")

    graph = build_repository_symbol_index(tmp_path)

    assert "standalone_port" in graph.names_for(tasks)
    assert detect_unguarded_variables(tasks, symbol_index=graph) == (0, [])


def test_nested_group_vars_are_visible(tmp_path):
    variables = tmp_path / "group_vars" / "production" / "database.yml"
    variables.parent.mkdir(parents=True)
    variables.write_text("database_endpoint: db.internal\n")
    tasks = tmp_path / "site.yml"
    tasks.write_text("- debug: {msg: '{{ database_endpoint }}'}\n")

    graph = build_repository_symbol_index(tmp_path)

    assert "database_endpoint" in graph.names_for(tasks)


def test_nested_host_vars_are_visible(tmp_path):
    variables = tmp_path / "host_vars" / "server01" / "network.yml"
    variables.parent.mkdir(parents=True)
    variables.write_text("network_interface: eth0\n")
    tasks = tmp_path / "site.yml"
    tasks.write_text("- debug: {msg: '{{ network_interface }}'}\n")

    graph = build_repository_symbol_index(tmp_path)

    assert "network_interface" in graph.names_for(tasks)


def test_split_role_main_variable_directories_are_visible(tmp_path):
    defaults = tmp_path / "roles" / "web" / "defaults" / "main" / "ports.yml"
    defaults.parent.mkdir(parents=True)
    defaults.write_text("web_port: 8080\n")
    role_vars = tmp_path / "roles" / "web" / "vars" / "main" / "tls.yml"
    role_vars.parent.mkdir(parents=True)
    role_vars.write_text("tls_enabled: true\n")
    tasks = tmp_path / "roles" / "web" / "tasks" / "main.yml"
    tasks.parent.mkdir(parents=True)
    tasks.write_text("- debug: {msg: '{{ web_port }} {{ tls_enabled }}'}\n")

    graph = build_repository_symbol_index(tmp_path)

    assert {"web_port", "tls_enabled"} <= graph.names_for(tasks)


def test_arbitrary_role_variable_files_are_not_automatically_loaded(tmp_path):
    variables = tmp_path / "roles" / "web" / "defaults" / "optional.yml"
    variables.parent.mkdir(parents=True)
    variables.write_text("optional_value: true\n")
    tasks = tmp_path / "roles" / "web" / "tasks" / "main.yml"
    tasks.parent.mkdir(parents=True)
    tasks.write_text("- debug: {msg: '{{ optional_value }}'}\n")

    graph = build_repository_symbol_index(tmp_path)

    assert "optional_value" not in graph.names_for(tasks)


def test_task_vars_do_not_leak(tmp_path):
    tasks = tmp_path / "tasks.yml"
    tasks.write_text(
        "- name: First\n  debug: {msg: '{{ x }}'}\n"
        "- name: Second\n  vars: {x: hello}\n  debug: {msg: '{{ x }}'}\n"
    )
    graph = build_repository_symbol_index(tmp_path)

    count, details = detect_unguarded_variables(tasks, symbol_index=graph)

    assert count == 1
    assert details[0]["variable"] == "x"


def test_later_task_vars_do_not_fix_earlier_use(tmp_path):
    tasks = tmp_path / "tasks.yml"
    tasks.write_text(
        "- debug: {msg: '{{ later_value }}'}\n"
        "- vars: {later_value: ready}\n  debug: {msg: '{{ later_value }}'}\n"
    )
    graph = build_repository_symbol_index(tmp_path)

    assert detect_unguarded_variables(tasks, symbol_index=graph)[0] == 1


def test_block_vars_are_visible_only_inside_the_block(tmp_path):
    tasks = tmp_path / "tasks.yml"
    tasks.write_text(
        "- name: Scoped block\n"
        "  vars: {block_value: ready}\n"
        "  block:\n"
        "    - debug: {msg: '{{ block_value }}'}\n"
        "- name: Outside\n"
        "  debug: {msg: '{{ block_value }}'}\n"
    )
    graph = build_repository_symbol_index(tmp_path)

    count, details = detect_unguarded_variables(tasks, symbol_index=graph)

    assert count == 1
    assert details[0]["variable"] == "block_value"


def test_block_defined_guard_protects_nested_variable_reference(tmp_path):
    tasks = tmp_path / "tasks.yml"
    tasks.write_text(
        "- name: Guard optional result\n"
        "  when: optional_result is defined\n"
        "  block:\n"
        "    - debug: {msg: '{{ optional_result.stdout }}'}\n",
        encoding="utf-8",
    )
    graph = build_repository_symbol_index(tmp_path)

    assert detect_unguarded_variables(tasks, symbol_index=graph) == (0, [])


def test_unguarded_variable_has_reasoned_confidence_factors(tmp_path):
    tasks = tmp_path / "tasks.yml"
    tasks.write_text("- debug: {msg: '{{ missing_value }}'}\n", encoding="utf-8")

    count, details = detect_unguarded_variables(tasks)

    assert count == 1
    assert details[0]["confidence"] == "medium"
    assert "no_visible_static_definition" in details[0]["confidence_factors"]["positive"]
    assert details[0]["confidence_factors"]["negative"] == []


def test_disjunctive_defined_check_is_not_a_safe_task_guard(tmp_path):
    tasks = tmp_path / "tasks.yml"
    tasks.write_text(
        "- name: May run without optional result\n"
        "  when: optional_result is defined or fallback_enabled\n"
        "  debug: {msg: '{{ optional_result.stdout }}'}\n",
        encoding="utf-8",
    )
    graph = build_repository_symbol_index(tmp_path)

    count, details = detect_unguarded_variables(tasks, symbol_index=graph)
    assert count == 1
    assert details[0]["variable"] == "optional_result"


def test_play_vars_do_not_leak_to_another_play(tmp_path):
    playbook = tmp_path / "site.yml"
    playbook.write_text(
        "- hosts: first\n"
        "  tasks:\n"
        "    - debug: {msg: '{{ second_play_value }}'}\n"
        "- hosts: second\n"
        "  vars: {second_play_value: ready}\n"
        "  tasks:\n"
        "    - debug: {msg: '{{ second_play_value }}'}\n"
    )
    graph = build_repository_symbol_index(tmp_path)

    count, details = detect_unguarded_variables(playbook, symbol_index=graph)

    assert count == 1
    assert details[0]["variable"] == "second_play_value"


def test_indexed_visibility_matches_definition_wide_reference(tmp_path):
    (tmp_path / "group_vars").mkdir()
    (tmp_path / "group_vars" / "all.yml").write_text("global_value: yes\n")
    tasks = tmp_path / "roles" / "web" / "tasks" / "main.yml"
    tasks.parent.mkdir(parents=True)
    tasks.write_text(
        "- set_fact: {runtime_value: ready}\n"
        "- debug: {msg: '{{ runtime_value }}'}\n"
    )
    defaults = tmp_path / "roles" / "web" / "defaults" / "main.yml"
    defaults.parent.mkdir(parents=True)
    defaults.write_text("role_value: ready\n")
    graph = build_repository_symbol_index(tmp_path)

    for task_index in (None, 0, 1, 2):
        reference = frozenset(
            item.name
            for item in graph.definitions
            if graph._visible_definition(item, tasks, task_index, 0, None)
        )
        assert graph.visible_names_at(tasks, task_index, 0) == reference


def test_visibility_index_avoids_unrelated_role_definitions(tmp_path, monkeypatch):
    queried = None
    for index in range(20):
        defaults = tmp_path / "roles" / f"role_{index}" / "defaults" / "main.yml"
        defaults.parent.mkdir(parents=True)
        defaults.write_text(f"role_{index}_value: ready\n")
        tasks = tmp_path / "roles" / f"role_{index}" / "tasks" / "main.yml"
        tasks.parent.mkdir(parents=True)
        tasks.write_text("- debug: {msg: ok}\n")
        if index == 7:
            queried = tasks
    graph = build_repository_symbol_index(tmp_path)
    calls = 0
    original = type(graph)._visible_definition

    def counted(self, *args, **kwargs):
        nonlocal calls
        calls += 1
        return original(self, *args, **kwargs)

    monkeypatch.setattr(type(graph), "_visible_definition", counted)
    assert "role_7_value" in graph.visible_names_at(queried)
    assert calls < len(graph.definitions) / 2
    assert graph.metadata()["indexes"]["roles"] == 20


def test_configured_custom_module_fact_is_visible_after_its_task(tmp_path):
    tasks = tmp_path / "tasks.yml"
    tasks.write_text(
        "- vendor.widget_facts: {}\n"
        "- debug: {msg: '{{ widget_state }}'}\n",
        encoding="utf-8",
    )
    graph = build_repository_symbol_index(
        tmp_path,
        files=[tasks],
        custom_module_facts_by_file={
            tasks: {"vendor.widget_facts": ["widget_state"]}
        },
    )

    assert "widget_state" not in graph.visible_names_at(tasks, task_index=0)
    assert "widget_state" in graph.visible_names_at(tasks, task_index=1)
    assert any(
        item.name == "widget_state" and item.kind == "custom-module-fact"
        for item in graph.definitions
    )
    assert "widget_state" not in graph.static_names_for(tasks)
    assert graph.has_visible_static_definition("widget_state", tasks) is False


def test_configured_custom_facts_support_unambiguous_short_module_alias(tmp_path):
    tasks = tmp_path / "tasks.yml"
    tasks.write_text("- widget_facts: {}\n", encoding="utf-8")
    graph = build_repository_symbol_index(
        tmp_path,
        files=[tasks],
        custom_module_facts_by_file={
            tasks: {"vendor.widget_facts": ["widget_state"]}
        },
    )

    assert any(item.name == "widget_state" for item in graph.definitions)


def test_literal_play_hosts_limit_host_and_group_var_visibility(tmp_path):
    (tmp_path / "host_vars").mkdir()
    (tmp_path / "host_vars" / "server01.yml").write_text("host_only: yes\n")
    (tmp_path / "group_vars").mkdir()
    (tmp_path / "group_vars" / "web.yml").write_text("web_only: yes\n")
    playbook = tmp_path / "site.yml"
    playbook.write_text(
        "- hosts: server02\n  tasks:\n    - debug: {msg: ok}\n"
        "- hosts: web\n  tasks:\n    - debug: {msg: ok}\n",
        encoding="utf-8",
    )
    graph = build_repository_symbol_index(tmp_path)

    first = graph.visible_names_at(playbook, play_index=0)
    second = graph.visible_names_at(playbook, play_index=1)
    assert "host_only" not in first
    assert "web_only" not in first
    assert "web_only" in second


def test_literal_child_group_inherits_static_ini_parent_group_vars(tmp_path):
    inventory = tmp_path / "inventory.ini"
    inventory.write_text(
        "[production:children]\nweb\n[web:children]\napi\n",
        encoding="utf-8",
    )
    group_vars = tmp_path / "group_vars"
    group_vars.mkdir()
    (group_vars / "production.yml").write_text("parent_value: yes\n")
    playbook = tmp_path / "site.yml"
    playbook.write_text(
        "- hosts: api\n  tasks:\n    - debug: {msg: '{{ parent_value }}'}\n",
        encoding="utf-8",
    )

    graph = build_repository_symbol_index(tmp_path)

    assert "parent_value" in graph.visible_names_at(playbook, play_index=0)


def test_declared_extensionless_inventory_variables_are_indexed_and_scoped(
    tmp_path,
):
    inventory = tmp_path / "inventories" / "production"
    inventory.parent.mkdir()
    inventory.write_text(
        "[all:vars]\ndata_dir=/data\n"
        "[web:vars]\nweb_port=8080\n"
        "[web]\nserver01 host_token=secret\n",
        encoding="utf-8",
    )
    web = tmp_path / "web.yml"
    database = tmp_path / "database.yml"
    web.write_text(
        "- hosts: web\n  tasks:\n"
        "    - debug: {msg: '{{ data_dir }} {{ web_port }}'}\n",
        encoding="utf-8",
    )
    database.write_text(
        "- hosts: database\n  tasks:\n"
        "    - debug: {msg: '{{ web_port }}'}\n",
        encoding="utf-8",
    )
    files = [web, database]

    graph = build_repository_symbol_index(
        tmp_path,
        files=files,
        inventory_sources=("inventories",),
    )

    assert graph.definition_visibility("data_dir", web, 0, 0) == "must"
    assert graph.definition_visibility("web_port", web, 0, 0) == "must"
    assert graph.definition_visibility("web_port", database, 0, 0) == "none"
    assert graph.definition_visibility("host_token", database, 0, 0) == "none"


def test_explicit_inventory_population_prevents_ini_context_leakage(tmp_path):
    documentation_inventory = tmp_path / "docs" / "example" / "inventory.ini"
    documentation_inventory.parent.mkdir(parents=True)
    documentation_inventory.write_text(
        "[production:children]\nweb\n", encoding="utf-8"
    )
    group_vars = tmp_path / "group_vars"
    group_vars.mkdir()
    variables = group_vars / "production.yml"
    variables.write_text("parent_value: yes\n", encoding="utf-8")
    playbook = tmp_path / "site.yml"
    playbook.write_text(
        "- hosts: web\n  tasks:\n    - debug: {msg: '{{ parent_value }}'}\n",
        encoding="utf-8",
    )
    files = [playbook, variables]

    isolated = build_repository_symbol_index(
        tmp_path, files=files, inventory_sources=()
    )
    declared = build_repository_symbol_index(
        tmp_path,
        files=files,
        inventory_sources=("docs/example/inventory.ini",),
    )

    assert "parent_value" not in isolated.visible_names_at(playbook, play_index=0)
    assert "parent_value" in declared.visible_names_at(playbook, play_index=0)


def test_literal_host_inherits_static_ini_group_vars(tmp_path):
    (tmp_path / "inventory.ini").write_text(
        "[web]\nserver01 ansible_host=192.0.2.10\n", encoding="utf-8"
    )
    group_vars = tmp_path / "group_vars"
    group_vars.mkdir()
    (group_vars / "web.yml").write_text("web_value: yes\n")
    playbook = tmp_path / "site.yml"
    playbook.write_text(
        "- hosts: server01\n  tasks:\n    - debug: {msg: '{{ web_value }}'}\n",
        encoding="utf-8",
    )

    graph = build_repository_symbol_index(tmp_path)

    assert "web_value" in graph.visible_names_at(playbook, play_index=0)


def test_literal_host_inherits_static_yaml_inventory_group_vars(tmp_path):
    (tmp_path / "inventory.yml").write_text(
        """all:
  children:
    production:
      children:
        web:
          hosts:
            server01: {}
""",
        encoding="utf-8",
    )
    group_vars = tmp_path / "group_vars"
    group_vars.mkdir()
    (group_vars / "production.yml").write_text("parent_value: yes\n")
    playbook = tmp_path / "site.yml"
    playbook.write_text(
        "- hosts: server01\n  tasks:\n    - debug: {msg: '{{ parent_value }}'}\n",
        encoding="utf-8",
    )

    graph = build_repository_symbol_index(tmp_path)

    assert "parent_value" in graph.visible_names_at(playbook, play_index=0)


def test_set_fact_cacheable_option_is_not_a_runtime_definition(tmp_path):
    tasks = tmp_path / "tasks.yml"
    tasks.write_text(
        "- set_fact: {cacheable: true, actual_fact: ready}\n"
        "- debug: {msg: '{{ cacheable }} {{ actual_fact }}'}\n",
        encoding="utf-8",
    )

    graph = build_repository_symbol_index(tmp_path)
    count, details = detect_unguarded_variables(tasks, symbol_index=graph)

    assert "cacheable" not in graph.names
    assert "actual_fact" in graph.names
    assert count == 1
    assert details[0]["variable"] == "cacheable"


@pytest.mark.parametrize(
    "role_entry",
    ("    - web\n", "    - role: web\n"),
)
def test_play_vars_reach_invoked_role_tasks(tmp_path, role_entry):
    playbook = tmp_path / "site.yml"
    role_tasks = tmp_path / "roles" / "web" / "tasks" / "main.yml"
    role_tasks.parent.mkdir(parents=True)
    playbook.write_text(
        "- hosts: all\n  vars:\n    web_port: 8080\n  roles:\n"
        + role_entry,
        encoding="utf-8",
    )
    role_tasks.write_text(
        "- debug: {msg: '{{ web_port }}'}\n", encoding="utf-8"
    )
    files = [playbook, role_tasks]
    context = build_repository_analysis_context(tmp_path, files)
    graph = build_repository_symbol_index(
        tmp_path, files=files, parsed_documents=context.parsed_documents
    )

    assert graph.definition_visibility("web_port", role_tasks, 0, 0) == "must"
    assert detect_unguarded_variables(
        role_tasks, symbol_index=graph,
        parsed_document=context.document_for(role_tasks),
        repository_context=context,
    ) == (0, [])


def test_pre_task_fact_and_role_invocation_vars_reach_role(tmp_path):
    playbook = tmp_path / "site.yml"
    role_tasks = tmp_path / "roles" / "web" / "tasks" / "main.yml"
    role_tasks.parent.mkdir(parents=True)
    playbook.write_text(
        "- hosts: all\n"
        "  pre_tasks:\n"
        "    - set_fact: {app_port: 8080}\n"
        "  roles:\n"
        "    - role: web\n"
        "      vars: {role_mode: production}\n",
        encoding="utf-8",
    )
    role_tasks.write_text(
        "- debug: {msg: '{{ app_port }} {{ role_mode }}'}\n",
        encoding="utf-8",
    )
    files = [playbook, role_tasks]
    context = build_repository_analysis_context(tmp_path, files)
    graph = build_repository_symbol_index(
        tmp_path, files=files, parsed_documents=context.parsed_documents
    )

    assert detect_unguarded_variables(
        role_tasks, symbol_index=graph,
        parsed_document=context.document_for(role_tasks),
        repository_context=context,
    ) == (0, [])


@pytest.mark.parametrize("action", ("include_role", "import_role"))
def test_prior_fact_and_task_vars_reach_task_invoked_role(tmp_path, action):
    playbook = tmp_path / "site.yml"
    role_tasks = tmp_path / "roles" / "web" / "tasks" / "main.yml"
    role_tasks.parent.mkdir(parents=True)
    playbook.write_text(
        "- hosts: all\n  tasks:\n"
        "    - set_fact: {app_port: 8080}\n"
        f"    - {action}: {{name: web}}\n"
        "      vars: {role_mode: production}\n",
        encoding="utf-8",
    )
    role_tasks.write_text(
        "- debug: {msg: '{{ app_port }} {{ role_mode }}'}\n",
        encoding="utf-8",
    )
    files = [playbook, role_tasks]
    context = build_repository_analysis_context(tmp_path, files)
    graph = build_repository_symbol_index(
        tmp_path, files=files, parsed_documents=context.parsed_documents
    )

    assert detect_unguarded_variables(
        role_tasks, symbol_index=graph,
        parsed_document=context.document_for(role_tasks),
        repository_context=context,
    ) == (0, [])


def test_multiple_role_callers_intersect_execution_context(tmp_path):
    caller_a = tmp_path / "a.yml"
    caller_b = tmp_path / "b.yml"
    role_tasks = tmp_path / "roles" / "web" / "tasks" / "main.yml"
    role_tasks.parent.mkdir(parents=True)
    caller_a.write_text(
        "- hosts: all\n  vars: {only_a: yes}\n  roles: [web]\n",
        encoding="utf-8",
    )
    caller_b.write_text(
        "- hosts: all\n  vars: {only_b: yes}\n  roles: [web]\n",
        encoding="utf-8",
    )
    role_tasks.write_text(
        "- debug: {msg: '{{ only_a }} {{ only_b }}'}\n", encoding="utf-8"
    )
    files = [caller_a, caller_b, role_tasks]
    context = build_repository_analysis_context(tmp_path, files)
    graph = build_repository_symbol_index(
        tmp_path, files=files, parsed_documents=context.parsed_documents
    )

    assert graph.definition_visibility("only_a", role_tasks, 0, 0) == "may"
    assert graph.definition_visibility("only_b", role_tasks, 0, 0) == "may"


def test_public_role_vars_reach_later_role_without_becoming_repository_global(
    tmp_path,
):
    playbook = tmp_path / "site.yml"
    base_vars = tmp_path / "roles" / "matrix-base" / "defaults" / "main.yml"
    base_tasks = tmp_path / "roles" / "matrix-base" / "tasks" / "main.yml"
    consumer = tmp_path / "roles" / "matrix-consumer" / "tasks" / "main.yml"
    disconnected = tmp_path / "roles" / "other" / "tasks" / "main.yml"
    for path in (base_vars, base_tasks, consumer, disconnected):
        path.parent.mkdir(parents=True, exist_ok=True)
    playbook.write_text(
        "- hosts: all\n  roles:\n    - matrix-base\n    - matrix-consumer\n",
        encoding="utf-8",
    )
    base_vars.write_text("matrix_user_name: matrix\n", encoding="utf-8")
    base_tasks.write_text("- debug: {msg: base}\n", encoding="utf-8")
    consumer.write_text(
        "- debug: {msg: '{{ matrix_user_name }}'}\n", encoding="utf-8"
    )
    disconnected.write_text(
        "- debug: {msg: '{{ matrix_user_name }}'}\n", encoding="utf-8"
    )
    files = [playbook, base_vars, base_tasks, consumer, disconnected]
    context = build_repository_analysis_context(tmp_path, files)
    graph = build_repository_symbol_index(
        tmp_path, files=files, parsed_documents=context.parsed_documents
    )

    assert graph.definition_visibility("matrix_user_name", consumer, 0, 0) == "must"
    assert graph.definition_visibility("matrix_user_name", disconnected, 0, 0) == "none"


def test_private_role_vars_do_not_leak_to_later_role(tmp_path):
    (tmp_path / "ansible.cfg").write_text(
        "[defaults]\nprivate_role_vars = true\n", encoding="utf-8"
    )
    playbook = tmp_path / "site.yml"
    base_vars = tmp_path / "roles" / "base" / "vars" / "main.yml"
    base_tasks = tmp_path / "roles" / "base" / "tasks" / "main.yml"
    consumer = tmp_path / "roles" / "consumer" / "tasks" / "main.yml"
    for path in (base_vars, base_tasks, consumer):
        path.parent.mkdir(parents=True, exist_ok=True)
    playbook.write_text(
        "- hosts: all\n  roles: [base, consumer]\n", encoding="utf-8"
    )
    base_vars.write_text("private_value: secret\n", encoding="utf-8")
    base_tasks.write_text("- debug: {msg: base}\n", encoding="utf-8")
    consumer.write_text(
        "- debug: {msg: '{{ private_value }}'}\n", encoding="utf-8"
    )
    files = [playbook, base_vars, base_tasks, consumer]
    context = build_repository_analysis_context(tmp_path, files)
    graph = build_repository_symbol_index(
        tmp_path, files=files, parsed_documents=context.parsed_documents
    )

    assert graph.definition_visibility("private_value", consumer, 0, 0) == "none"


def test_role_dependency_context_reaches_depending_role(tmp_path):
    playbook = tmp_path / "site.yml"
    meta = tmp_path / "roles" / "app" / "meta" / "main.yml"
    app_tasks = tmp_path / "roles" / "app" / "tasks" / "main.yml"
    base_tasks = tmp_path / "roles" / "base" / "tasks" / "main.yml"
    for path in (meta, app_tasks, base_tasks):
        path.parent.mkdir(parents=True, exist_ok=True)
    playbook.write_text("- hosts: all\n  roles: [app]\n", encoding="utf-8")
    meta.write_text("dependencies: [base]\n", encoding="utf-8")
    base_tasks.write_text(
        "- set_fact: {dependency_value: ready}\n", encoding="utf-8"
    )
    app_tasks.write_text(
        "- debug: {msg: '{{ dependency_value }}'}\n", encoding="utf-8"
    )
    files = [playbook, meta, app_tasks, base_tasks]
    context = build_repository_analysis_context(tmp_path, files)
    graph = build_repository_symbol_index(
        tmp_path, files=files, parsed_documents=context.parsed_documents
    )

    assert graph.definition_visibility("dependency_value", app_tasks, 0, 0) == "must"


def test_conditional_role_output_is_may_in_caller_continuation(tmp_path):
    playbook = tmp_path / "site.yml"
    role_tasks = tmp_path / "roles" / "web" / "tasks" / "main.yml"
    role_tasks.parent.mkdir(parents=True)
    playbook.write_text(
        "- hosts: all\n  tasks:\n"
        "    - include_role: {name: web}\n"
        "      when: use_web\n"
        "    - debug: {msg: '{{ role_result }}'}\n",
        encoding="utf-8",
    )
    role_tasks.write_text(
        "- set_fact: {role_result: ready}\n", encoding="utf-8"
    )
    files = [playbook, role_tasks]
    context = build_repository_analysis_context(tmp_path, files)
    graph = build_repository_symbol_index(
        tmp_path, files=files, parsed_documents=context.parsed_documents
    )

    assert graph.definition_visibility("role_result", playbook, 1, 0) == "may"


def test_rescue_register_is_may_but_when_skipped_register_is_must(tmp_path):
    tasks = tmp_path / "main.yml"
    tasks.write_text(
        "- block:\n"
        "    - debug: {msg: ok}\n"
        "  rescue:\n"
        "    - command: recover\n"
        "      register: recovery_result\n"
        "- command: /bin/true\n"
        "  when: run_command\n"
        "  register: command_result\n"
        "- debug: {msg: '{{ recovery_result }} {{ command_result }}'}\n",
        encoding="utf-8",
    )
    context = build_repository_analysis_context(tmp_path, [tasks])
    graph = build_repository_symbol_index(
        tmp_path, files=[tasks], parsed_documents=context.parsed_documents
    )

    assert graph.definition_visibility("recovery_result", tasks, 4, 0) == "may"
    assert graph.definition_visibility("command_result", tasks, 4, 0) == "must"
    count, details = detect_unguarded_variables(
        tasks, known_variables={"run_command"}, symbol_index=graph,
        parsed_document=context.document_for(tasks),
        repository_context=context,
    )
    assert count == 1
    assert details[0]["variable"] == "recovery_result"
    assert details[0]["semantic_status"] == "UNCERTAIN"


def test_static_include_vars_directory_defines_selected_variables(tmp_path):
    tasks = tmp_path / "tasks.yml"
    variables = tmp_path / "vars" / "common" / "database.yml"
    variables.parent.mkdir(parents=True)
    variables.write_text("database_port: 5432\n", encoding="utf-8")
    tasks.write_text(
        "- include_vars: {dir: vars/common}\n"
        "- debug: {msg: '{{ database_port }}'}\n",
        encoding="utf-8",
    )
    files = [tasks, variables]
    context = build_repository_analysis_context(tmp_path, files)
    graph = build_repository_symbol_index(
        tmp_path, files=files, parsed_documents=context.parsed_documents
    )

    assert graph.definition_visibility("database_port", tasks, 1, 0) == "must"
    assert detect_unguarded_variables(
        tasks, symbol_index=graph,
        parsed_document=context.document_for(tasks),
        repository_context=context,
    ) == (0, [])


def test_namespaced_include_vars_does_not_define_bare_mapping_keys(tmp_path):
    tasks = tmp_path / "tasks.yml"
    variables = tmp_path / "vars.yml"
    variables.write_text("database_port: 5432\n", encoding="utf-8")
    tasks.write_text(
        "- include_vars: {file: vars.yml, name: database}\n"
        "- debug: {msg: '{{ database.database_port }} {{ database_port }}'}\n",
        encoding="utf-8",
    )
    files = [tasks, variables]
    context = build_repository_analysis_context(tmp_path, files)
    graph = build_repository_symbol_index(
        tmp_path, files=files, parsed_documents=context.parsed_documents
    )

    assert graph.definition_visibility("database", tasks, 1, 0) == "must"
    assert graph.definition_visibility("database_port", tasks, 1, 0) == "none"
    count, details = detect_unguarded_variables(
        tasks,
        symbol_index=graph,
        parsed_document=context.document_for(tasks),
        repository_context=context,
    )
    assert count == 1
    assert details[0]["variable"] == "database_port"


@pytest.mark.parametrize("producer_when", (None, "produce_value"))
def test_repeated_include_call_sites_keep_pre_definition_use_uncertain(
    tmp_path, producer_when
):
    parent = tmp_path / "main.yml"
    child = tmp_path / "repeated.yml"
    parent.write_text(
        "- include_tasks: repeated.yml\n"
        "- include_tasks: repeated.yml\n",
        encoding="utf-8",
    )
    conditional = (
        f"  when: {producer_when}\n" if producer_when is not None else ""
    )
    child.write_text(
        "- debug: {msg: '{{ repeated_value }}'}\n"
        "- set_fact: {repeated_value: ready}\n"
        + conditional,
        encoding="utf-8",
    )
    files = [parent, child]
    context = build_repository_analysis_context(tmp_path, files)
    graph = build_repository_symbol_index(
        tmp_path, files=files, parsed_documents=context.parsed_documents
    )

    count, details = detect_unguarded_variables(
        child,
        known_variables={"produce_value"},
        symbol_index=graph,
        parsed_document=context.document_for(child),
        repository_context=context,
    )

    assert graph.definition_visibility(
        "repeated_value", child, 0, 0
    ) == "may"
    assert count == 1
    assert details[0]["semantic_status"] == "UNCERTAIN"
    assert "multiple_include_call_sites" in details[0]["uncertainty_sources"]


def test_mixed_include_call_sites_do_not_promote_conditional_definition(
    tmp_path,
):
    caller_a = tmp_path / "caller-a.yml"
    caller_b = tmp_path / "caller-b.yml"
    child = tmp_path / "child.yml"
    caller_a.write_text(
        "- set_fact: {shared_value: ready}\n"
        "  when: define_shared_value\n"
        "- include_tasks: child.yml\n",
        encoding="utf-8",
    )
    caller_b.write_text(
        "- include_tasks: child.yml\n", encoding="utf-8"
    )
    child.write_text(
        "- debug: {msg: '{{ shared_value }}'}\n", encoding="utf-8"
    )
    files = [caller_a, caller_b, child]
    context = build_repository_analysis_context(tmp_path, files)
    graph = build_repository_symbol_index(
        tmp_path, files=files, parsed_documents=context.parsed_documents
    )

    count, details = detect_unguarded_variables(
        child,
        known_variables={"define_shared_value"},
        symbol_index=graph,
        parsed_document=context.document_for(child),
        repository_context=context,
    )

    assert graph.definition_visibility(
        "shared_value", child, 0, 0
    ) == "may"
    assert count == 1
    assert details[0]["semantic_status"] == "UNCERTAIN"
    assert "multiple_include_call_sites" in details[0]["uncertainty_sources"]
    assert "conditional_runtime_definition" in details[0][
        "uncertainty_sources"
    ]


def test_conditional_include_vars_call_site_changes_may_to_must_by_position(
    tmp_path,
):
    tasks = tmp_path / "main.yml"
    variables = tmp_path / "vars.yml"
    variables.write_text("database_port: 5432\n", encoding="utf-8")
    tasks.write_text(
        "- include_vars: vars.yml\n"
        "  when: load_database_vars\n"
        "- debug: {msg: '{{ database_port }}'}\n"
        "- include_vars: vars.yml\n"
        "- debug: {msg: '{{ database_port }}'}\n",
        encoding="utf-8",
    )
    files = [tasks, variables]
    context = build_repository_analysis_context(tmp_path, files)
    graph = build_repository_symbol_index(
        tmp_path, files=files, parsed_documents=context.parsed_documents
    )

    assert graph.definition_visibility("database_port", tasks, 1, 0) == "may"
    assert graph.definition_visibility("database_port", tasks, 3, 0) == "must"
    assert "conditional_runtime_definition" in (
        graph.definition_uncertainty_sources(
            "database_port", tasks, 1, 0
        )
    )


def test_same_condition_makes_conditional_set_fact_certain(tmp_path):
    tasks = tmp_path / "main.yml"
    tasks.write_text(
        "- set_fact: {database_port: 5432}\n"
        "  when: database_enabled\n"
        "- debug: {msg: '{{ database_port }}'}\n"
        "  when:\n"
        "    - database_enabled\n"
        "    - configure_database\n",
        encoding="utf-8",
    )
    graph = build_repository_symbol_index(tmp_path)

    assert detect_unguarded_variables(
        tasks,
        known_variables={"database_enabled", "configure_database"},
        symbol_index=graph,
    ) == (0, [])


def test_different_condition_keeps_conditional_set_fact_uncertain(tmp_path):
    tasks = tmp_path / "main.yml"
    tasks.write_text(
        "- set_fact: {database_port: 5432}\n"
        "  when: database_enabled\n"
        "- debug: {msg: '{{ database_port }}'}\n"
        "  when: configure_database\n",
        encoding="utf-8",
    )
    graph = build_repository_symbol_index(tmp_path)

    count, details = detect_unguarded_variables(
        tasks,
        known_variables={"database_enabled", "configure_database"},
        symbol_index=graph,
    )

    assert count == 1
    assert details[0]["variable_classification"] == "unresolved-runtime-input"
    assert details[0]["semantic_status"] == "UNCERTAIN"


def test_underscore_prefixed_role_value_is_an_input_contract(tmp_path):
    tasks = tmp_path / "roles" / "database" / "tasks" / "main.yml"
    tasks.parent.mkdir(parents=True)
    tasks.write_text(
        "- debug: {msg: '{{ __database_private_input }}'}\n",
        encoding="utf-8",
    )
    context = build_repository_analysis_context(tmp_path, [tasks])
    graph = build_repository_symbol_index(
        tmp_path,
        files=[tasks],
        parsed_documents=context.parsed_documents,
    )

    count, details = detect_unguarded_variables(
        tasks,
        symbol_index=graph,
        parsed_document=context.document_for(tasks),
        repository_context=context,
    )

    assert count == 1
    assert details[0]["variable_classification"] == "undeclared-input-contract"
    assert details[0]["uncertainty_sources"] == [
        "possible_required_role_input"
    ]


@pytest.mark.parametrize("action", ("package_facts", "service_facts"))
def test_bare_builtin_fact_action_does_not_add_custom_fact_uncertainty(
    tmp_path, action
):
    playbook = tmp_path / "site.yml"
    playbook.write_text(
        "- hosts: all\n"
        "  tasks:\n"
        f"    - {action}: {{}}\n"
        "    - debug: {msg: '{{ deployment_input }}'}\n",
        encoding="utf-8",
    )
    context = build_repository_analysis_context(tmp_path, [playbook])
    graph = build_repository_symbol_index(
        tmp_path,
        files=[playbook],
        parsed_documents=context.parsed_documents,
    )

    count, details = detect_unguarded_variables(
        playbook,
        symbol_index=graph,
        parsed_document=context.document_for(playbook),
        repository_context=context,
    )

    assert count == 1
    assert "custom_module_fact" not in details[0]["uncertainty_sources"]
    assert details[0]["variable_classification"] == "undeclared-input-contract"


def test_ansible_collection_fact_module_is_not_treated_as_builtin(tmp_path):
    tasks = tmp_path / "tasks.yml"
    tasks.write_text(
        "- ansible.posix.mount_facts: {}\n"
        "- debug: {msg: '{{ vendor_mount_state }}'}\n",
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
    assert "custom_module_fact" in details[0]["uncertainty_sources"]
    assert details[0]["variable_classification"] == "unresolved-runtime-input"


def test_same_file_set_fact_does_not_become_must_across_plays(tmp_path):
    playbook = tmp_path / "site.yml"
    playbook.write_text(
        "- hosts: first\n"
        "  tasks:\n"
        "    - set_fact: {first_play_value: ready}\n"
        "- hosts: second\n"
        "  tasks:\n"
        "    - debug: {msg: '{{ first_play_value }}'}\n",
        encoding="utf-8",
    )
    context = build_repository_analysis_context(tmp_path, [playbook])
    graph = build_repository_symbol_index(
        tmp_path,
        files=[playbook],
        parsed_documents=context.parsed_documents,
    )

    count, details = detect_unguarded_variables(
        playbook,
        symbol_index=graph,
        parsed_document=context.document_for(playbook),
        repository_context=context,
    )

    assert count == 1
    assert details[0]["variable"] == "first_play_value"
    assert details[0]["variable_classification"] == "undeclared-input-contract"


def test_dynamic_include_glob_survives_notimplementederror(tmp_path, monkeypatch):
    # A dynamic include's pattern is task-controlled content, not a trusted
    # glob. pathlib (3.13+) raises NotImplementedError for some patterns it
    # considers "non-relative" -- confirmed in practice crashing an entire
    # repository scan (novateams/nova.core) because only OSError/ValueError
    # were caught around base.glob(pattern).
    from pathlib import Path

    from ansibleguard.symbol_index import _dynamic_task_include_targets

    def raise_not_implemented(self, pattern):
        raise NotImplementedError("Non-relative patterns are unsupported")

    monkeypatch.setattr(Path, "glob", raise_not_implemented)

    source = tmp_path / "tasks" / "main.yml"
    result = _dynamic_task_include_targets(
        "{{ item }}_task.yml", source, tmp_path, allowed_files=set()
    )

    assert result == ()
