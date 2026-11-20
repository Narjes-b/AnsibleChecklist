from ansibleguard.analysis_context import (
    IncludeResolution,
    build_repository_analysis_context,
)


def test_repository_context_retains_immutable_module_metadata(tmp_path):
    task_file = tmp_path / "tasks.yml"
    task_file.write_text("- name: noop\n  debug:\n    msg: ok\n", encoding="utf-8")
    source = {"user": {"options": {"password": {"no_log": True}}}}

    context = build_repository_analysis_context(
        tmp_path, [task_file], module_metadata=source
    )

    assert context.module_metadata["user"]["options"]["password"]["no_log"] is True
    source["copy"] = {}
    assert "copy" not in context.module_metadata
    source["user"]["options"]["password"]["no_log"] = False
    assert context.module_metadata["user"]["options"]["password"]["no_log"] is True


def test_repository_context_parse_cache_reuses_same_content(tmp_path):
    task_file = tmp_path / "tasks.yml"
    task_file.write_text("- name: noop\n  debug:\n    msg: ok\n", encoding="utf-8")
    cache = tmp_path / ".cache" / "parsed"

    first = build_repository_analysis_context(tmp_path, [task_file], cache_dir=cache)
    second = build_repository_analysis_context(tmp_path, [task_file], cache_dir=cache)

    assert first.performance["cache_misses"] == 1
    assert second.performance["cache_hits"] == 1
    assert second.document_for(task_file).content_sha256 == first.document_for(task_file).content_sha256

    task_file.write_text("- name: changed\n  debug:\n    msg: changed\n", encoding="utf-8")
    third = build_repository_analysis_context(tmp_path, [task_file], cache_dir=cache)
    assert third.performance["cache_misses"] == 1
    assert third.document_for(task_file).document[0]["name"] == "changed"
from ansibleguard.symbol_index import build_repository_symbol_index
from ansibleguard.detectors.paper_candidates import detect_paper_candidates
from ansibleguard.cli import _annotate_finding_populations


def test_repository_context_parses_and_extracts_shared_task_metadata_once(tmp_path):
    variables = tmp_path / "vars.yml"
    variables.write_text("port: 8080\n")
    tasks = tmp_path / "tasks.yml"
    tasks.write_text(
        "- name: Configure\n"
        "  include_vars: vars.yml\n"
        "- debug:\n"
        "    msg: '{{ port }}'\n"
        "  when: port is defined\n"
    )

    context = build_repository_analysis_context(tmp_path, [tasks, variables])

    assert context.performance["yaml_files_parsed"] == 2
    assert context.performance["yaml_parse_operations"] == 2
    assert context.tasks_for(tasks)[1].jinja_references == ("port",)
    assert context.include_relationships[0].resolution == IncludeResolution.STATIC_RESOLVED
    assert context.file_context_for(tasks).classification == "production_ansible"


def test_repository_context_preindexes_usage_and_runtime_uncertainty(tmp_path):
    tasks = tmp_path / "tasks.yml"
    tasks.write_text(
        "- set_fact: {selected_port: 8080}\n"
        "- include_tasks: '{{ platform }}.yml'\n"
        "- debug: {msg: '{{ selected_port }} {{ runtime_value }}'}\n",
        encoding="utf-8",
    )

    context = build_repository_analysis_context(tmp_path, [tasks])

    assert context.variable_usage["selected_port"] == ("tasks.yml",)
    assert context.uncertainty_for(tasks, 0) == ()
    assert "dynamic_include" in context.uncertainty_for(tasks, 2)


def test_literal_role_path_include_is_statically_resolved(tmp_path):
    main = tmp_path / "roles" / "custom" / "service" / "tasks" / "main.yml"
    included = main.parent / "install.yml"
    main.parent.mkdir(parents=True)
    main.write_text(
        "- include_tasks: '{{ role_path }}/tasks/install.yml'\n",
        encoding="utf-8",
    )
    included.write_text("- debug: {msg: ready}\n", encoding="utf-8")

    relationship = build_repository_analysis_context(
        tmp_path, [main, included]
    ).include_relationships[0]

    assert relationship.resolution == IncludeResolution.STATIC_RESOLVED
    assert relationship.resolved_target == (
        "roles/custom/service/tasks/install.yml"
    )


def test_manifest_and_repository_context_share_fixture_classification(tmp_path):
    from ansibleguard.file_manifest import classify_repository

    source = tmp_path / "roles" / "web" / "fixtures" / "tasks.yml"
    source.parent.mkdir(parents=True)
    source.write_text("- debug: {msg: fixture}\n", encoding="utf-8")

    manifest_row = classify_repository(tmp_path)[0]
    context = build_repository_analysis_context(tmp_path, [source])

    assert manifest_row["file_class"] == "fixture_or_generated"
    assert context.file_context_for(source).classification == "fixture_or_generated"


def test_task_action_ignores_args_and_other_task_keywords(tmp_path):
    tasks = tmp_path / "tasks.yml"
    tasks.write_text(
        "- name: Collect facts\n"
        "  args: {target: switch}\n"
        "  ignore_errors: true\n"
        "  vendor.device_facts: {}\n",
        encoding="utf-8",
    )

    task = build_repository_analysis_context(tmp_path, [tasks]).tasks_for(tasks)[0]

    assert task.action == "vendor.device_facts"


def test_task_level_role_relationships_record_static_and_dynamic_roles(tmp_path):
    tasks = tmp_path / "tasks.yml"
    tasks.write_text(
        "- include_role: {name: vendor.web}\n"
        "- import_role:\n    name: '{{ selected_role }}'\n",
        encoding="utf-8",
    )

    relationships = build_repository_analysis_context(
        tmp_path, [tasks]
    ).include_relationships

    assert [edge.resolution for edge in relationships] == [
        IncludeResolution.STATIC_ROLE,
        IncludeResolution.DYNAMIC_ROLE,
    ]
    assert relationships[0].raw_target == "vendor.web"


def test_dynamic_external_missing_and_runtime_includes_are_nonfatal(tmp_path):
    tasks = tmp_path / "tasks.yml"
    tasks.write_text(
        "- include_vars: '{{ ansible_os_family }}.yml'\n"
        "- include_vars: missing.yml\n"
        "- include_vars: /root/pull_variables.yml\n"
        "- include_vars: /tmp/generated-vars.yml\n"
    )

    context = build_repository_analysis_context(tmp_path, [tasks])

    assert [edge.resolution for edge in context.include_relationships] == [
        IncludeResolution.DYNAMIC,
        IncludeResolution.STATIC_MISSING,
        IncludeResolution.EXTERNAL,
        IncludeResolution.RUNTIME_GENERATED,
    ]


def test_symbol_index_reuses_repository_documents(tmp_path, monkeypatch):
    tasks = tmp_path / "tasks.yml"
    tasks.write_text("- set_fact: {shared_value: ready}\n")
    context = build_repository_analysis_context(tmp_path, [tasks])

    monkeypatch.setattr(
        "ansibleguard.symbol_index.yaml.load",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("reparsed")),
    )
    graph = build_repository_symbol_index(
        tmp_path,
        files=[tasks],
        parsed_documents=context.parsed_documents,
    )

    assert "shared_value" in graph.names


def test_paper_detector_family_reuses_one_parsed_document(tmp_path, monkeypatch):
    tasks = tmp_path / "tasks.yml"
    tasks.write_text("- name: Display\n  debug: {msg: ok}\n")
    context = build_repository_analysis_context(tmp_path, [tasks])
    parsed = context.document_for(tasks)

    monkeypatch.setattr(
        "ansibleguard.detectors.paper_candidates.yaml.load",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("reparsed")),
    )

    metrics = detect_paper_candidates(tasks, parsed_document=parsed)

    assert "unguarded_variables" in metrics


def test_project_discovery_prefers_nested_ansible_root_over_git_root(tmp_path):
    ansible = tmp_path / "infrastructure" / "ansible"
    tasks = ansible / "roles" / "web" / "tasks" / "main.yml"
    tasks.parent.mkdir(parents=True)
    tasks.write_text("- debug: {msg: ok}\n")
    chart = tmp_path / "charts" / "values.yml"
    chart.parent.mkdir()
    chart.write_text("replicas: 2\n")

    context = build_repository_analysis_context(tmp_path, [tasks, chart])

    assert context.project_model.ansible_roots == ("infrastructure/ansible",)
    assert context.file_context_for(chart).classification == "project_yaml"


def test_project_discovery_supports_multiple_ansible_roots(tmp_path):
    files = []
    for project in ("service_a", "service_b"):
        tasks = tmp_path / project / "roles" / "web" / "tasks" / "main.yml"
        tasks.parent.mkdir(parents=True)
        tasks.write_text("- debug: {msg: ok}\n")
        files.append(tasks)

    context = build_repository_analysis_context(tmp_path, files)

    assert context.project_model.ansible_roots == ("service_a", "service_b")


def test_root_playbook_prevents_overlapping_unconfigured_nested_provider_root(
    tmp_path,
):
    site = tmp_path / "site.yml"
    site.write_text("- hosts: all\n  tasks: []\n", encoding="utf-8")
    nested = tmp_path / "service" / "roles" / "web" / "tasks" / "main.yml"
    nested.parent.mkdir(parents=True)
    nested.write_text("- debug: {msg: ready}\n", encoding="utf-8")

    context = build_repository_analysis_context(tmp_path, [site, nested])

    assert context.project_model.ansible_roots == (".",)


def test_nested_provider_root_is_kept_with_independent_configuration(tmp_path):
    site = tmp_path / "site.yml"
    site.write_text("- hosts: all\n  tasks: []\n", encoding="utf-8")
    nested = tmp_path / "service" / "roles" / "web" / "tasks" / "main.yml"
    nested.parent.mkdir(parents=True)
    nested.write_text("- debug: {msg: ready}\n", encoding="utf-8")
    (tmp_path / "service" / "ansible.cfg").write_text(
        "[defaults]\n", encoding="utf-8"
    )

    context = build_repository_analysis_context(tmp_path, [site, nested])

    assert context.project_model.ansible_roots == (".", "service")


def test_project_model_extracts_dependencies_without_installing_them(tmp_path):
    requirements = tmp_path / "requirements.yml"
    requirements.write_text(
        "roles:\n"
        "  - name: geerlingguy.nginx\n"
        "collections:\n"
        "  - name: community.general\n",
        encoding="utf-8",
    )
    galaxy = tmp_path / "galaxy.yml"
    galaxy.write_text("namespace: acme\nname: platform\n", encoding="utf-8")
    execution_environment = tmp_path / "execution-environment.yml"
    execution_environment.write_text(
        "dependencies:\n"
        "  galaxy: requirements.yml\n"
        "  python: requirements.txt\n"
        "  system: bindep.txt\n",
        encoding="utf-8",
    )

    context = build_repository_analysis_context(
        tmp_path, [requirements, galaxy, execution_environment]
    )
    dependencies = context.project_model.dependencies

    assert dependencies.declared_roles == ("geerlingguy.nginx",)
    assert dependencies.declared_collections == ("community.general",)
    assert dependencies.local_collections == ("acme.platform",)
    assert dependencies.execution_environment_dependencies == (
        "galaxy:requirements.yml",
        "python:requirements.txt",
        "system:bindep.txt",
    )
    assert dependencies.source_files == (
        "execution-environment.yml",
        "galaxy.yml",
        "requirements.yml",
    )


def test_dependency_discovery_accepts_role_requirement_filename_variants(tmp_path):
    requirements = tmp_path / "ansible-role-requirements.yml"
    requirements.write_text(
        "- name: geerlingguy.nginx\n  src: geerlingguy.nginx\n",
        encoding="utf-8",
    )

    dependencies = build_repository_analysis_context(
        tmp_path, [requirements]
    ).project_model.dependencies

    assert dependencies.declared_roles == ("geerlingguy.nginx",)
    assert "geerlingguy_nginx_" in dependencies.declared_variable_prefixes
    assert dependencies.source_files == ("ansible-role-requirements.yml",)


def test_dependency_model_discovers_unselected_root_manifest_prefixes(tmp_path):
    tasks = tmp_path / "roles" / "app" / "tasks" / "main.yml"
    tasks.parent.mkdir(parents=True)
    tasks.write_text("- debug: {msg: ok}\n", encoding="utf-8")
    (tmp_path / "requirements.yml").write_text(
        "- name: systemd_docker_base\n"
        "  src: git+https://github.com/devture/"
        "com.devture.ansible.role.systemd_docker_base.git\n",
        encoding="utf-8",
    )

    context = build_repository_analysis_context(tmp_path, [tasks])

    assert context.external_dependency_may_define(
        "devture_systemd_docker_base_systemd_path"
    )


def test_project_model_records_configs_per_detected_ansible_root(tmp_path):
    files = []
    for project in ("service_a", "service_b"):
        root = tmp_path / project
        tasks = root / "roles" / "web" / "tasks" / "main.yml"
        tasks.parent.mkdir(parents=True)
        tasks.write_text("- debug: {msg: ok}\n", encoding="utf-8")
        (root / "ansible.cfg").write_text("[defaults]\n", encoding="utf-8")
        if project == "service_b":
            (root / ".ansible-lint").write_text("profile: basic\n", encoding="utf-8")
        files.append(tasks)

    context = build_repository_analysis_context(tmp_path, files)

    assert dict(context.project_model.configs_by_root["service_a"]) == {
        "ansible_cfg": "service_a/ansible.cfg"
    }
    assert dict(context.project_model.configs_by_root["service_b"]) == {
        "ansible_cfg": "service_b/ansible.cfg",
        "ansible_lint_config": "service_b/.ansible-lint",
    }


def test_findings_receive_explicit_source_and_analysis_populations(tmp_path):
    production = tmp_path / "roles" / "web" / "tasks" / "main.yml"
    production.parent.mkdir(parents=True)
    production.write_text("- debug: {msg: ok}\n")
    example = tmp_path / "examples" / "example.yml"
    example.parent.mkdir()
    example.write_text("- debug: {msg: ok}\n")
    context = build_repository_analysis_context(tmp_path, [production, example])
    findings = [
        {"file": "roles/web/tasks/main.yml", "provider": "ansibleguard"},
        {"file": "examples/example.yml", "provider": "gitleaks"},
        {
            "file": "roles/web/tasks/main.yml",
            "provider": "ansible-lint",
            "analysis_population": "environment_dependent_provider_finding",
        },
    ]

    _annotate_finding_populations(findings, context, tmp_path)

    assert findings[0]["analysis_population"] == "production_valid"
    assert findings[0]["classification_confidence"] == "high"
    assert findings[1]["analysis_population"] == "test_or_example"
    assert findings[1]["secret_population"] == "example_secret"
    assert findings[1]["secret_context"] == "likely_dummy_secret"
    assert "test_example_or_fixture" in findings[1]["secret_context_factors"][
        "negative"
    ]
    assert findings[2]["analysis_population"] == (
        "environment_dependent_provider_finding"
    )


def test_inventory_sources_are_explicitly_discovered_from_config(tmp_path):
    playbook = tmp_path / "site.yml"
    inventory = tmp_path / "environments" / "production" / "hosts.ini"
    inventory.parent.mkdir(parents=True)
    playbook.write_text("- hosts: all\n  tasks: []\n", encoding="utf-8")
    inventory.write_text("[web]\nserver.example.test\n", encoding="utf-8")
    (tmp_path / "ansible.cfg").write_text(
        "[defaults]\ninventory = environments/production/hosts.ini\n",
        encoding="utf-8",
    )

    context = build_repository_analysis_context(tmp_path, [playbook])

    assert context.project_model.inventory_sources == (
        "environments/production/hosts.ini",
    )
