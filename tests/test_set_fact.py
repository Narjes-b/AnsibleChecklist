from ansibleguard.detectors.set_fact import set_fact, unnecessary_set_fact_details
from ansibleguard.analysis_context import build_repository_analysis_context
from ansibleguard.symbol_index import build_repository_symbol_index


def test_unused_fact_detected(fixtures_dir):
    fixture = fixtures_dir / "set_fact_unused.yml"
    assert set_fact(str(fixture)) == 1


def test_used_fact_not_flagged(fixtures_dir):
    fixture = fixtures_dir / "set_fact_used.yml"
    assert set_fact(str(fixture)) == 0


def test_fact_name_in_plain_text_is_not_a_variable_use(fixtures_dir):
    fixture = fixtures_dir / "set_fact_not_jinja2.yml"
    assert set_fact(str(fixture)) == 1


def test_fact_used_as_bare_when_expression_is_a_variable_use(fixtures_dir):
    fixture = fixtures_dir / "set_fact_used_when.yml"
    assert set_fact(str(fixture)) == 0


def test_shared_context_keeps_fact_used_by_later_bare_condition(tmp_path):
    playbook = tmp_path / "tasks.yml"
    playbook.write_text(
        "- set_fact:\n    probe_value: true\n"
        "- debug: {msg: ready}\n  when: probe_value\n",
        encoding="utf-8",
    )
    context = build_repository_analysis_context(tmp_path, [playbook])

    assert unnecessary_set_fact_details(
        playbook,
        repository_context=context,
        parsed_document=context.document_for(playbook),
    ) == []


def test_shared_context_finds_nonleading_jinja_reference_in_later_task(tmp_path):
    playbook = tmp_path / "tasks.yml"
    playbook.write_text(
        "- set_fact:\n    selected_user: operator\n"
        "- debug:\n    msg: \"prefix {{ enabled and selected_user | length > 0 }}\"\n",
        encoding="utf-8",
    )
    context = build_repository_analysis_context(tmp_path, [playbook])

    assert unnecessary_set_fact_details(
        playbook,
        repository_context=context,
        parsed_document=context.document_for(playbook),
    ) == []


def test_shared_context_handles_nested_reference_after_ansible_filter(tmp_path):
    playbook = tmp_path / "tasks.yml"
    playbook.write_text(
        "- set_fact:\n    backend_config: ready\n"
        "- set_fact:\n"
        "    combined: \"{{ current | default({}) | "
        "combine({backend: backend_config}) }}\"\n",
        encoding="utf-8",
    )
    context = build_repository_analysis_context(tmp_path, [playbook])

    details = unnecessary_set_fact_details(
        playbook,
        repository_context=context,
        parsed_document=context.document_for(playbook),
    )

    assert {detail["variable"] for detail in details} == {"combined"}


def test_reassigned_fact_reports_only_the_final_dead_assignment(tmp_path):
    playbook = tmp_path / "tasks.yml"
    playbook.write_text(
        "- set_fact:\n    accumulated: [first]\n"
        "- set_fact:\n"
        "    accumulated: '{{ accumulated + [second] }}'\n",
        encoding="utf-8",
    )
    context = build_repository_analysis_context(tmp_path, [playbook])

    details = unnecessary_set_fact_details(
        playbook,
        repository_context=context,
        parsed_document=context.document_for(playbook),
    )

    assert len(details) == 1
    assert details[0]["variable"] == "accumulated"
    assert details[0]["line"] == 4


def test_shared_context_keeps_fact_consumed_by_same_role_template(tmp_path):
    tasks = tmp_path / "roles" / "web" / "tasks" / "main.yml"
    template = tmp_path / "roles" / "web" / "templates" / "config.j2"
    tasks.parent.mkdir(parents=True)
    template.parent.mkdir(parents=True)
    tasks.write_text(
        "- set_fact:\n    selected_port: 8080\n"
        "- template:\n    src: config.j2\n    dest: /tmp/config\n",
        encoding="utf-8",
    )
    template.write_text("port={{ selected_port }}\n", encoding="utf-8")
    context = build_repository_analysis_context(tmp_path, [tasks])

    assert unnecessary_set_fact_details(
        tasks,
        repository_context=context,
        parsed_document=context.document_for(tasks),
    ) == []


def test_fact_used_in_another_repository_file_is_not_flagged(tmp_path):
    tasks = tmp_path / "roles" / "web" / "tasks"
    tasks.mkdir(parents=True)
    producer = tasks / "prepare.yml"
    producer.write_text(
        "- name: Compute port\n  set_fact:\n    selected_port: 8080\n",
        encoding="utf-8",
    )
    (tasks / "consume.yml").write_text(
        "- name: Use port\n  debug:\n    msg: '{{ selected_port }}'\n",
        encoding="utf-8",
    )
    index = build_repository_symbol_index(tmp_path)

    assert set_fact(producer) == 1
    assert set_fact(producer, symbol_index=index) == 0


def test_fact_used_through_explicit_vars_lookup_is_not_flagged(tmp_path):
    playbook = tmp_path / "tasks.yml"
    playbook.write_text(
        "- name: Compute value\n  set_fact:\n    selected_value: ready\n"
        "- name: Resolve indirectly\n  debug:\n"
        "    msg: '{{ vars[\"selected_value\"] }}'\n",
        encoding="utf-8",
    )

    assert set_fact(playbook) == 0


def test_facts_used_through_lookup_and_hostvars_are_not_flagged(tmp_path):
    playbook = tmp_path / "indirect.yml"
    playbook.write_text(
        "- set_fact:\n"
        "    lookup_value: ready\n"
        "    host_value: ready\n"
        "- debug:\n"
        "    msg: \"{{ lookup('vars', 'lookup_value') }} "
        "{{ hostvars[inventory_hostname]['host_value'] }}\"\n",
        encoding="utf-8",
    )

    assert set_fact(playbook) == 0

    context = build_repository_analysis_context(tmp_path, [playbook])
    assert unnecessary_set_fact_details(
        playbook,
        repository_context=context,
        parsed_document=context.document_for(playbook),
    ) == []


def test_dynamically_named_set_fact_is_not_classified_as_unused(tmp_path):
    playbook = tmp_path / "tasks.yml"
    playbook.write_text(
        "- name: Runtime fact name\n  set_fact:\n    '{{ fact_name }}': ready\n",
        encoding="utf-8",
    )

    assert set_fact(playbook) == 0


def test_dynamic_vars_lookup_abstains_from_unused_fact_warning(tmp_path):
    playbook = tmp_path / "dynamic-use.yml"
    playbook.write_text(
        "- name: Define candidate\n"
        "  set_fact:\n"
        "    selected_value: ready\n"
        "- name: Read dynamic fact\n"
        "  debug:\n"
        "    msg: '{{ vars[fact_name] }}'\n",
        encoding="utf-8",
    )

    assert set_fact(playbook) == 0


def test_fact_used_as_bare_assert_expression_is_not_flagged(tmp_path):
    playbook = tmp_path / "tasks.yml"
    playbook.write_text(
        "- set_fact:\n    probe_value: ready\n"
        "- assert:\n    that: probe_value == 'ready'\n",
        encoding="utf-8",
    )

    assert set_fact(playbook) == 0


def test_fqcn_set_fact_is_detected_and_usage_is_respected(tmp_path):
    playbook = tmp_path / "tasks.yml"
    playbook.write_text(
        "- ansible.builtin.set_fact:\n    selected_value: ready\n"
        "- debug:\n    msg: '{{ selected_value }}'\n",
        encoding="utf-8",
    )

    assert set_fact(playbook) == 0


def test_set_fact_cacheable_option_is_not_an_unused_fact(tmp_path):
    playbook = tmp_path / "tasks.yml"
    playbook.write_text(
        "- ansible.builtin.set_fact:\n    cacheable: true\n    selected_value: ready\n"
        "- debug:\n    msg: '{{ selected_value }}'\n",
        encoding="utf-8",
    )

    assert set_fact(playbook) == 0


def test_cacheable_fact_without_static_consumer_is_preserved(tmp_path):
    playbook = tmp_path / "tasks.yml"
    playbook.write_text(
        "- ansible.builtin.set_fact:\n"
        "    cacheable: true\n"
        "    cached_platform_state: ready\n",
        encoding="utf-8",
    )
    context = build_repository_analysis_context(tmp_path, [playbook])

    assert unnecessary_set_fact_details(
        playbook,
        repository_context=context,
        parsed_document=context.document_for(playbook),
    ) == []


def test_disconnected_role_usage_does_not_keep_fact_alive(tmp_path):
    producer = tmp_path / "roles" / "a" / "tasks" / "main.yml"
    consumer = tmp_path / "roles" / "b" / "tasks" / "main.yml"
    producer.parent.mkdir(parents=True)
    consumer.parent.mkdir(parents=True)
    producer.write_text("- set_fact:\n    state: ready\n", encoding="utf-8")
    consumer.write_text("- debug: {msg: '{{ state }}'}\n", encoding="utf-8")
    context = build_repository_analysis_context(tmp_path, [producer, consumer])

    details = unnecessary_set_fact_details(
        producer,
        repository_context=context,
        parsed_document=context.document_for(producer),
    )
    assert details and details[0]["variable"] == "state"


def test_unused_fact_details_identify_variable_and_line(tmp_path):
    playbook = tmp_path / "tasks.yml"
    playbook.write_text(
        "- name: Define value\n  set_fact:\n    unused_value: ready\n",
        encoding="utf-8",
    )

    assert unnecessary_set_fact_details(playbook) == [
        {
            "line": 3,
            "variable": "unused_value",
            "issue": "set_fact variable 'unused_value' is never used.",
            "semantic_status": "UNCERTAIN",
            "resolution_status": "BOUNDED_GRAPH_UNKNOWN",
            "resolution_scope": "repository-static",
            "uncertainty_sources": [
                "bounded_execution_graph_cannot_prove_dead_assignment"
            ],
            "resolution_evidence": {
                "proved": ["no_use_in_bounded_execution_graph"],
                "blockers": [
                    "bounded_execution_graph_cannot_prove_dead_assignment"
                ],
            },
            "confidence": "low",
        }
    ]


def test_ansible_unsafe_tag_does_not_skip_set_fact_analysis(tmp_path):
    playbook = tmp_path / "tasks.yml"
    playbook.write_text(
        "- set_fact:\n    unused_value: !unsafe '{{ runtime_value }}'\n",
        encoding="utf-8",
    )

    assert set_fact(playbook) == 1


def test_shared_context_reuses_documents_for_cross_file_fact_use(
    tmp_path, monkeypatch
):
    producer = tmp_path / "prepare.yml"
    producer.write_text(
        "- set_fact:\n    selected_port: 8080\n"
        "- include_tasks: consume.yml\n",
        encoding="utf-8",
    )
    consumer = tmp_path / "consume.yml"
    consumer.write_text("- debug:\n    msg: '{{ selected_port }}'\n", encoding="utf-8")
    context = build_repository_analysis_context(tmp_path, [producer, consumer])

    monkeypatch.setattr(
        "ansibleguard.detectors.set_fact._repository_documents",
        lambda *_: (_ for _ in ()).throw(AssertionError("repository reparsed")),
    )
    assert set_fact(
        producer,
        repository_context=context,
        parsed_document=context.document_for(producer),
    ) == 0
