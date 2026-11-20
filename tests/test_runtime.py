from ansibleguard.cli import collect_yaml_files
from ansibleguard.runtime import (
    RunResult,
    build_repository_context_stage,
    build_symbol_index_stage,
    prepare_scan_context,
    run_external_providers,
    classify_fault,
    _annotate_lint_environment,
)
import ansibleguard.runtime as runtime
from ansibleguard import __version__
from ansibleguard.external.gitleaks import ToolResult


def test_runtime_provenance_uses_current_source_identity(monkeypatch):
    monkeypatch.setenv("ANSIBLE_COLLECTIONS_PATH", "/controlled/collections")
    runtime._environment_metadata.cache_clear()
    try:
        metadata = runtime._environment_metadata()
        assert metadata["ansibleguard_version"] == __version__ == "0.0.7.1"
        assert metadata["structural_metrics_version"] == "declared-leaf-tasks-v3"
        assert metadata["ansible_collections_paths"] == "/controlled/collections"
    finally:
        runtime._environment_metadata.cache_clear()


def test_typed_runtime_stages_prepare_index_and_skip_unrequested_providers(tmp_path):
    target = tmp_path / "project"
    target.mkdir()
    (target / "group_vars").mkdir()
    (target / "group_vars" / "all.yml").write_text("visible_value: yes\n")
    (target / "site.yml").write_text(
        '- name: use\n  debug:\n    msg: "{{ visible_value }}"\n'
    )
    context = prepare_scan_context(
        target, tmp_path / "output", "quality", None, collect_yaml_files
    )
    assert len(context.selected_files) == 2

    index = build_symbol_index_stage(context)
    assert "visible_value" in index.names
    providers = run_external_providers(context)
    assert providers.gitleaks.status == "not-requested"
    assert providers.ansible_lint.status == "not-requested"


def test_run_result_keeps_dictionary_api():
    result = RunResult(1, 1, 1, [], 0, "quality", 0, 0, {"analyzed": 1})
    assert result.as_dict()["file_states"] == {"analyzed": 1}
    assert result.as_dict()["status"] == "completed"


def test_fault_taxonomy_classifies_representative_failures():
    assert classify_fault("invalid", "yaml-parse") == (
        "PARSER_ERROR", "DETERMINISTIC_INPUT"
    )
    assert classify_fault("analysis-error", "report-write") == (
        "OUTPUT_SERIALIZATION_ERROR", "BUG"
    )
    assert classify_fault("tool-error", "ansible-lint") == (
        "PROVIDER_ERROR", "ENVIRONMENT"
    )
    assert classify_fault("analysis-error", "detector", MemoryError()) == (
        "MEMORY_ERROR", "ENVIRONMENT"
    )


def test_syntax_findings_receive_declared_dependency_environment_evidence(
    tmp_path, monkeypatch
):
    from ansibleguard.analysis_context import build_repository_analysis_context

    requirements = tmp_path / "requirements.yml"
    requirements.write_text(
        "collections:\n  - name: community.general\n", encoding="utf-8"
    )
    context = build_repository_analysis_context(tmp_path, [requirements])
    monkeypatch.setattr(
        runtime,
        "_environment_metadata",
        lambda: {"collections": {"items": {}}},
    )
    findings = [
        {"check_name": "syntax-check[unknown-module]", "message": "unknown"},
        {"check_name": "yaml[truthy]", "message": "style"},
    ]

    _annotate_lint_environment(findings, context.project_model)

    assert findings[0]["environment_interpretation"] == (
        "declared_dependency_not_installed"
    )
    assert findings[0]["environment_evidence"][
        "declared_but_not_installed_collections"
    ] == ["community.general"]
    assert "environment_evidence" not in findings[1]


def test_runtime_symbol_index_uses_only_selected_manifest_files(tmp_path):
    target = tmp_path / "project"
    target.mkdir()
    selected = target / "site.yml"
    selected.write_text('- debug: {msg: "{{ fixture_value }}"}\n')
    fixture = target / "group_vars" / "fixture.yml"
    fixture.parent.mkdir()
    fixture.write_text("fixture_value: yes\n")
    manifest = tmp_path / "manifest.txt"
    manifest.write_text("site.yml\n")

    context = prepare_scan_context(
        target,
        tmp_path / "output",
        "research-core",
        manifest,
        lambda _target, _manifest: [selected],
    )
    index = build_symbol_index_stage(context)

    assert index.input_files == ("site.yml",)
    assert "fixture_value" not in index.names


def test_nested_known_variables_do_not_leak(tmp_path):
    target = tmp_path / "project"
    target.mkdir()
    root_file = target / "root.yml"
    root_file.write_text("- debug: {msg: '{{ root_only }}'}\n")
    nested_file = target / "nested" / "tasks.yml"
    nested_file.parent.mkdir()
    nested_file.write_text("- debug: {msg: '{{ nested_only }}'}\n")
    (target / ".ansibleguard.yml").write_text(
        "rules:\n  known_variables: [root_only]\n"
    )
    (target / "nested" / ".ansibleguard.yml").write_text(
        "rules:\n  known_variables: [nested_only]\n"
    )
    context = prepare_scan_context(
        target,
        tmp_path / "output",
        "quality",
        None,
        lambda _target, _manifest: [root_file, nested_file],
    )

    graph = build_symbol_index_stage(context)

    assert "root_only" in graph.names_for(root_file)
    assert "nested_only" not in graph.names_for(root_file)
    assert "nested_only" in graph.names_for(nested_file)
    assert "root_only" not in graph.names_for(nested_file)


def test_research_container_fingerprint_is_recorded(monkeypatch):
    monkeypatch.setenv("ANSIBLEGUARD_RESEARCH_IMAGE_DIGEST", "sha256:frozen")
    monkeypatch.setenv("ANSIBLEGUARD_BUILD_GIT_SHA", "a" * 40)
    monkeypatch.setattr(runtime, "_git_sha", lambda _path: None)
    runtime._environment_metadata.cache_clear()
    try:
        metadata = runtime._environment_metadata()
    finally:
        runtime._environment_metadata.cache_clear()

    assert metadata["execution_environment"] == "research-container"
    assert metadata["research_image_digest"] == "sha256:frozen"
    assert metadata["ansibleguard_git_sha"] == "a" * 40
    assert "ansible_doc_executable" in metadata
    assert "ansible_doc_version" in metadata
    assert "ansible_collections_paths" in metadata
    assert set(metadata["environment_files"]) == {
        "requirements.txt", "Dockerfile.research", "collections.lock.yml"
    }


def test_ansible_lint_runs_once_per_detected_project_root_and_rebases_paths(
    tmp_path, monkeypatch
):
    target = tmp_path / "monorepo"
    files = []
    for project in ("service_a", "service_b"):
        tasks = target / project / "roles" / "web" / "tasks" / "main.yml"
        tasks.parent.mkdir(parents=True)
        tasks.write_text("- debug: {msg: ok}\n")
        files.append(tasks)
    context = prepare_scan_context(
        target, tmp_path / "output", "lint", None,
        lambda _target, _manifest: files,
    )
    repository_context = build_repository_context_stage(context)
    calls = []

    def scan(root, files=None):
        calls.append(root)
        return ToolResult(
            "completed",
            [{"check_name": "yaml[truthy]", "path": "roles/web/tasks/main.yml"}],
            metadata={"provider": "ansible-lint"},
        )

    monkeypatch.setattr(
        "ansibleguard.external.ansible_lint.scan_with_ansible_lint", scan
    )
    providers = run_external_providers(
        context, repository_context=repository_context
    )

    assert calls == [target / "service_a", target / "service_b"]
    assert providers.ansible_lint.status == "completed"
    assert [item["path"] for item in providers.ansible_lint.findings] == [
        "service_a/roles/web/tasks/main.yml",
        "service_b/roles/web/tasks/main.yml",
    ]
    assert providers.ansible_lint.metadata["provider_roots"] == [
        "service_a", "service_b"
    ]


def test_one_failed_ansible_root_makes_provider_partial(tmp_path, monkeypatch):
    target = tmp_path / "monorepo"
    files = []
    for project in ("service_a", "service_b"):
        tasks = target / project / "roles" / "web" / "tasks" / "main.yml"
        tasks.parent.mkdir(parents=True)
        tasks.write_text("- debug: {msg: ok}\n")
        files.append(tasks)
    context = prepare_scan_context(
        target, tmp_path / "output", "lint", None,
        lambda _target, _manifest: files,
    )
    repository_context = build_repository_context_stage(context)

    monkeypatch.setattr(
        "ansibleguard.external.ansible_lint.scan_with_ansible_lint",
        lambda root, files=None: ToolResult(
            "tool-error" if root.name == "service_b" else "completed",
            message="provider failed" if root.name == "service_b" else "",
        ),
    )

    result = run_external_providers(
        context, repository_context=repository_context
    ).ansible_lint

    assert result.status == "partial"
    assert "service_b: provider failed" in result.message


def test_ansible_lint_adapter_exception_is_provider_error_not_scan_crash(
    tmp_path, monkeypatch
):
    target = tmp_path / "project"
    target.mkdir()
    playbook = target / "site.yml"
    playbook.write_text("- hosts: all\n  tasks: []\n", encoding="utf-8")
    context = prepare_scan_context(
        target, tmp_path / "output", "technical-full", None,
        lambda _target, _manifest: [playbook],
    )
    repository_context = build_repository_context_stage(context)

    monkeypatch.setattr(
        "ansibleguard.external.ansible_lint.scan_with_ansible_lint",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AttributeError("malformed nested location")
        ),
    )
    monkeypatch.setattr(
        "ansibleguard.external.gitleaks.scan_with_gitleaks",
        lambda *args, **kwargs: ToolResult("completed"),
    )

    result = run_external_providers(
        context, repository_context=repository_context, concurrent=True
    )

    assert result.ansible_lint.status == "tool-error"
    assert result.ansible_lint.metadata["provider_diagnostics"][0][
        "category"
    ] == "PROVIDER_SCHEMA_ERROR"


def test_nested_ansible_lint_roots_receive_disjoint_file_populations(
    tmp_path, monkeypatch
):
    target = tmp_path / "monorepo"
    root_playbook = target / "site.yml"
    nested_tasks = target / "service" / "roles" / "web" / "tasks" / "main.yml"
    nested_tasks.parent.mkdir(parents=True)
    root_playbook.write_text("- hosts: all\n  tasks: []\n", encoding="utf-8")
    nested_tasks.write_text("- debug: {msg: ok}\n", encoding="utf-8")
    (target / "service" / "ansible.cfg").write_text(
        "[defaults]\nroles_path=roles\n", encoding="utf-8"
    )
    selected = [root_playbook, nested_tasks]
    context = prepare_scan_context(
        target, tmp_path / "output", "lint", None,
        lambda _target, _manifest: selected,
    )
    repository_context = build_repository_context_stage(context)
    calls = []

    def scan(root, files=None):
        calls.append(
            (
                root.relative_to(target).as_posix() or ".",
                tuple(
                    path.relative_to(target).as_posix()
                    for path in files or ()
                ),
            )
        )
        return ToolResult("completed", metadata={"provider": "ansible-lint"})

    monkeypatch.setattr(
        "ansibleguard.external.ansible_lint.scan_with_ansible_lint", scan
    )
    result = run_external_providers(
        context, repository_context=repository_context
    ).ansible_lint

    assert repository_context.project_model.ansible_roots == (".", "service")
    assert calls == [
        (".", ("site.yml",)),
        ("service", ("service/roles/web/tasks/main.yml",)),
    ]
    handed_off = [path for _root, files in calls for path in files]
    assert sorted(handed_off) == sorted(
        path.relative_to(target).as_posix() for path in selected
    )
    assert len(handed_off) == len(set(handed_off))
    assert result.metadata["provider_population_files"] == 2
    assert all(
        item["provider_population_files"] == 1
        and len(item["provider_population_sha256"]) == 64
        for item in result.metadata["root_results"]
    )


def test_ansible_lint_v004_target_scope_runs_once_without_explicit_files(
    tmp_path, monkeypatch
):
    target = tmp_path / "project"
    nested = target / "service" / "tasks.yml"
    nested.parent.mkdir(parents=True)
    root = target / "site.yml"
    root.write_text("- hosts: all\n  tasks: []\n", encoding="utf-8")
    nested.write_text("- debug: {msg: ok}\n", encoding="utf-8")
    context = prepare_scan_context(
        target, tmp_path / "output", "lint", None,
        lambda _target, _manifest: [root, nested],
        ansible_lint_scope="v004-target",
    )
    repository_context = build_repository_context_stage(context)
    calls = []

    def scan(scan_target, files=None):
        calls.append((scan_target, files))
        return ToolResult("completed", metadata={"provider": "ansible-lint"})

    monkeypatch.setattr(
        "ansibleguard.external.ansible_lint.scan_with_ansible_lint", scan
    )
    result = run_external_providers(
        context, repository_context=repository_context
    ).ansible_lint

    assert calls == [(target.resolve(), None)]
    assert result.metadata["provider_scope"] == "v004-target"
    assert result.metadata["explicit_population"] is False


def test_ansible_lint_dependency_evidence_is_scoped_to_provider_root(
    tmp_path, monkeypatch
):
    target = tmp_path / "monorepo"
    root_playbook = target / "site.yml"
    nested_tasks = target / "service" / "roles" / "web" / "tasks" / "main.yml"
    requirements = target / "service" / "requirements.yml"
    nested_tasks.parent.mkdir(parents=True)
    root_playbook.write_text("- hosts: all\n  tasks: []\n", encoding="utf-8")
    nested_tasks.write_text("- debug: {msg: ok}\n", encoding="utf-8")
    requirements.write_text(
        "collections:\n  - name: community.general\n", encoding="utf-8"
    )
    (target / "service" / "ansible.cfg").write_text(
        "[defaults]\nroles_path=roles\n", encoding="utf-8"
    )
    selected = [root_playbook, nested_tasks, requirements]
    context = prepare_scan_context(
        target, tmp_path / "output", "lint", None,
        lambda _target, _manifest: selected,
    )
    repository_context = build_repository_context_stage(context)
    monkeypatch.setattr(
        runtime, "_environment_metadata",
        lambda: {"collections": {"items": {}}},
    )

    def scan(root, files=None):
        return ToolResult(
            "completed",
            findings=[{
                "check_name": "syntax-check[unknown-module]",
                "path": "site.yml",
            }],
            metadata={"provider": "ansible-lint"},
        )

    monkeypatch.setattr(
        "ansibleguard.external.ansible_lint.scan_with_ansible_lint", scan
    )
    result = run_external_providers(
        context, repository_context=repository_context
    ).ansible_lint
    evidence_by_root = {
        finding["provider_root"]: finding["environment_evidence"]
        for finding in result.findings
    }

    assert evidence_by_root["."]["declared_collections"] == []
    assert evidence_by_root["service"]["declared_collections"] == [
        "community.general"
    ]


def test_concurrent_and_sequential_provider_results_are_semantically_equal(
    tmp_path, monkeypatch
):
    target = tmp_path / "project"
    target.mkdir()
    tasks = target / "tasks.yml"
    tasks.write_text("- debug: {msg: ok}\n")
    context = prepare_scan_context(
        target, tmp_path / "output", "technical-full", None,
        lambda _target, _manifest: [tasks],
    )
    monkeypatch.setattr(
        "ansibleguard.external.gitleaks.scan_with_gitleaks",
        lambda *args, **kwargs: ToolResult(
            "completed", [{"File": "tasks.yml", "StartLine": 1}]
        ),
    )
    monkeypatch.setattr(
        "ansibleguard.external.ansible_lint.scan_with_ansible_lint",
        lambda *args, **kwargs: ToolResult(
            "completed", [{"path": "tasks.yml", "line": 1}]
        ),
    )

    sequential = run_external_providers(context, concurrent=False)
    parallel = run_external_providers(context, concurrent=True)

    assert sequential.gitleaks.status == parallel.gitleaks.status == "completed"
    assert sequential.gitleaks.findings == parallel.gitleaks.findings
    assert sequential.ansible_lint.status == parallel.ansible_lint.status == "completed"
    assert sequential.ansible_lint.findings == parallel.ansible_lint.findings
    assert sequential.gitleaks.metadata["provider_execution_mode"] == "sequential"
    assert parallel.gitleaks.metadata["provider_execution_mode"] == "concurrent"
