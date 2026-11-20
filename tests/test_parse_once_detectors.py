import builtins
from pathlib import Path

from ansibleguard.document import inspect_document
from ansibleguard.detectors.duplicate_code import duplicate_code
from ansibleguard.detectors.files_extensions import extract_tasks_from_playbook
from ansibleguard.detectors.filters_for_comparison import get_when_conditions
from ansibleguard.detectors.high_coupling import high_coupling
from ansibleguard.detectors.incohesive_plays import calculate_similarity as play_cohesion
from ansibleguard.detectors.sem_cohesion import calculate_similarity as playbook_cohesion
from ansibleguard.detectors.overriding_facts import overriding_facts
from ansibleguard.detectors.unnecessary_abs import unecessary_abs
from ansibleguard.detectors.file_kinds import detect_file_kind_smells
from ansibleguard.detectors.galaxy_meta import detect_galaxy_meta_incomplete
from ansibleguard.detectors.variable_naming import detect_variable_naming_convention
from ansibleguard.detectors.deprecated_modules import (
    detect_deprecated_modules,
    detect_redirected_modules,
)
from ansibleguard.detectors.handler_issues import detect_handler_issues
from ansibleguard.detectors.loop_legacy_syntax import detect_loop_legacy_syntax
from ansibleguard.detectors.missing_tags import detect_missing_tags
from ansibleguard.detectors.missing_validate_certs import detect_missing_validate_certs
from ansibleguard.detectors.shell_instead_of_module import detect_shell_instead_of_module
from ansibleguard.detectors.review_checklist import (
    detect_redundant_default_values,
    detect_review_checklist_smells,
    detect_silent_error_suppression,
)
from ansibleguard.detectors.paper_candidates import (
    detect_broken_role_dependencies,
    detect_paper_candidates,
)
from ansibleguard.detectors.missing_checklist import detect_missing_checklist_smells
from ansibleguard.detectors.partial_checklist import detect_partial_checklist_smells
from ansibleguard.detectors.become_scope import detect_become_scope_too_broad
from ansibleguard.detectors.overriden_keys import detect_duplicate_keys_per_task
from ansibleguard.detectors.unnamed_play import unnamed_play
from ansibleguard.detectors.unnamed_tasks import unnamed_tasks
from ansibleguard.detectors.duplicate_task_names import repeated_task_names
from ansibleguard.detectors.credentials_leaking_in_log import (
    detect_credentials_leaking_in_log,
)
from ansibleguard.detectors.detect_large_play import calculate_metrics_play
from ansibleguard.detectors.detect_large_playbook import calculate_metrics_playbook
from ansibleguard.detectors.large_task import calculate_metrics_task
from ansibleguard.detectors.vault_structure import detect_vault_inline_overload
from ansibleguard.analysis_context import build_repository_analysis_context


def test_file_local_detector_group_reuses_parsed_document(tmp_path, monkeypatch):
    playbook = tmp_path / "site.yml"
    playbook.write_text(
        "- hosts: all\n"
        "  roles: [web]\n"
        "  tasks:\n"
        "    - import_tasks: setup\n"
        "    - debug: {msg: repeated}\n"
        "    - debug: {msg: repeated}\n"
        "    - block:\n"
        "        - debug: {msg: wrapped}\n"
        "    - set_fact: {mode: one}\n"
        "    - set_fact: {mode: two}\n"
        "    - debug: {msg: ok}\n"
        "      when: enabled == 'true'\n",
        encoding="utf-8",
    )
    parsed = inspect_document(playbook)

    def forbidden_open(*_args, **_kwargs):
        raise AssertionError("detector reopened an already parsed YAML file")

    monkeypatch.setattr(builtins, "open", forbidden_open)

    assert duplicate_code(playbook, parsed_document=parsed) == 1
    assert extract_tasks_from_playbook(playbook, parsed_document=parsed) == 1
    assert get_when_conditions(playbook, parsed_document=parsed) == 1
    assert high_coupling(playbook, parsed_document=parsed) == {
        "Num_Imports": 1,
        "Num_Roles": 1,
        "Raw_Num_Imports": 1,
        "Import_Only_Dispatcher": False,
    }
    assert overriding_facts(playbook, parsed_document=parsed) == 1
    assert unecessary_abs(playbook, parsed_document=parsed) == 1
    assert play_cohesion(playbook, parsed_document=parsed) == 0
    assert playbook_cohesion(playbook, parsed_document=parsed) >= 0.5


def test_variable_and_metadata_detectors_reuse_parsed_document(
    tmp_path, monkeypatch
):
    defaults = tmp_path / "roles" / "web" / "defaults" / "main.yml"
    defaults.parent.mkdir(parents=True)
    defaults.write_text("port: 80\ndb_password: real-secret\n", encoding="utf-8")
    meta = tmp_path / "roles" / "web" / "meta" / "main.yml"
    meta.parent.mkdir(parents=True)
    meta.write_text("galaxy_info:\n  author: Example\n", encoding="utf-8")
    defaults_document = inspect_document(defaults)
    meta_document = inspect_document(meta)

    monkeypatch.setattr(
        "ansibleguard.detectors.file_kinds.inspect_document",
        lambda *_: (_ for _ in ()).throw(AssertionError("file reparsed")),
    )
    monkeypatch.setattr(
        "ansibleguard.detectors.variable_naming.yaml.safe_load",
        lambda *_: (_ for _ in ()).throw(AssertionError("file reparsed")),
    )
    monkeypatch.setattr(
        "ansibleguard.detectors.galaxy_meta.yaml.safe_load",
        lambda *_: (_ for _ in ()).throw(AssertionError("file reparsed")),
    )

    metrics = detect_file_kind_smells(
        defaults, parsed_document=defaults_document
    )
    assert metrics["plaintext_sensitive_variables"] == 1
    assert detect_variable_naming_convention(
        defaults, parsed_document=defaults_document
    )[0] == 2
    assert detect_galaxy_meta_incomplete(
        meta, parsed_document=meta_document
    )[0] == 1


def test_legacy_detector_group_reuses_parsed_document(tmp_path, monkeypatch):
    playbook = tmp_path / "site.yml"
    playbook.write_text(
        "- hosts: all\n"
        "  handlers:\n"
        "    - name: restart app\n"
        "      service: {name: app, state: restarted}\n"
        "  tasks:\n"
        "    - name: install package\n"
        "      yum: {name: vim}\n"
        "      notify: missing handler\n"
        "    - name: old loop\n"
        "      debug: {msg: '{{ item }}'}\n"
        "      with_items: [one]\n"
        "    - name: unsafe request\n"
        "      uri:\n"
        "        url: https://example.test\n"
        "        validate_certs: false\n"
        "    - name: shell package\n"
        "      shell: apt-get install vim\n",
        encoding="utf-8",
    )
    parsed = inspect_document(playbook)

    def forbidden_open(*_args, **_kwargs):
        raise AssertionError("legacy detector reopened an already parsed YAML file")

    monkeypatch.setattr(builtins, "open", forbidden_open)

    assert detect_missing_tags(playbook, parsed_document=parsed)[0] >= 1
    assert detect_shell_instead_of_module(playbook, parsed_document=parsed)[0] == 1
    assert detect_missing_validate_certs(playbook, parsed_document=parsed)[0] == 1
    assert detect_deprecated_modules(playbook, parsed_document=parsed)[0] >= 0
    assert detect_redirected_modules(playbook, parsed_document=parsed)[0] >= 0
    assert detect_handler_issues(playbook, parsed_document=parsed)[0] == 1
    assert detect_loop_legacy_syntax(playbook, parsed_document=parsed)[0] == 1


def test_checklist_detector_families_reuse_parsed_document(tmp_path, monkeypatch):
    playbook = tmp_path / "site.yml"
    playbook.write_text(
        "- name: broad privilege\n"
        "  hosts: all\n"
        "  become: true\n"
        "  tasks:\n"
        "    - name: write file\n"
        "      file: {path: /tmp/x, state: touch, mode: '0666'}\n"
        "    - name: register value\n"
        "      command: echo ok\n"
        "      register: result\n",
        encoding="utf-8",
    )
    parsed = inspect_document(playbook)

    def forbidden_open(*_args, **_kwargs):
        raise AssertionError("checklist detector reopened an already parsed YAML file")

    monkeypatch.setattr(builtins, "open", forbidden_open)

    review = detect_review_checklist_smells(playbook, parsed_document=parsed)
    partial = detect_partial_checklist_smells(playbook, parsed_document=parsed)
    assert review["insecure_permissions"] == 1
    assert partial["unused_registered_variables"] == 1
    assert detect_become_scope_too_broad(playbook, parsed_document=parsed)[0] == 0


def test_duplicate_key_detector_reuses_loader_evidence(tmp_path, monkeypatch):
    playbook = tmp_path / "duplicate.yml"
    playbook.write_text(
        "- hosts: all\n"
        "  tasks:\n"
        "    - name: duplicate\n"
        "      debug: {msg: one}\n"
        "      debug: {msg: two}\n",
        encoding="utf-8",
    )
    parsed = inspect_document(playbook)

    def forbidden_open(*_args, **_kwargs):
        raise AssertionError("duplicate-key detector reopened an already parsed YAML file")

    monkeypatch.setattr(builtins, "open", forbidden_open)
    report = detect_duplicate_keys_per_task(playbook, parsed_document=parsed)
    assert report and "debug" in report[0]["duplicates"]


def test_task_metric_detectors_reuse_parsed_document(tmp_path, monkeypatch):
    playbook = tmp_path / "metrics.yml"
    playbook.write_text(
        "- hosts: all\n"
        "  tasks:\n"
        "    - debug: {msg: one}\n"
        "    - name: repeated\n"
        "      debug: {msg: two}\n"
        "    - name: repeated\n"
        "      debug: {msg: three}\n",
        encoding="utf-8",
    )
    parsed = inspect_document(playbook)

    def forbidden_open(*_args, **_kwargs):
        raise AssertionError("task metric detector reopened an already parsed YAML file")

    monkeypatch.setattr(builtins, "open", forbidden_open)
    unnamed_play_count, unnamed_play_details = unnamed_play(
        playbook, parsed_document=parsed
    )
    unnamed_task_count, unnamed_task_details = unnamed_tasks(
        playbook, parsed_document=parsed
    )
    assert unnamed_play_count == 1
    assert unnamed_play_details == [{"line": 1}]
    assert unnamed_task_count == 1
    assert unnamed_task_details == [{"task_name": "Unknown", "line": 3}]
    assert repeated_task_names(playbook, parsed_document=parsed) == 1


def test_credential_detector_reuses_parsed_document(tmp_path, monkeypatch):
    playbook = tmp_path / "credential.yml"
    playbook.write_text(
        "- hosts: all\n"
        "  tasks:\n"
        "    - name: expose password\n"
        "      debug:\n"
        "        msg: '{{ password }}'\n",
        encoding="utf-8",
    )
    parsed = inspect_document(playbook)

    def forbidden_open(*_args, **_kwargs):
        raise AssertionError("credential detector reopened an already parsed YAML file")

    monkeypatch.setattr(builtins, "open", forbidden_open)
    warnings, count, _details = detect_credentials_leaking_in_log(
        playbook, module_metadata={}, parsed_document=parsed
    )
    assert count == 1
    assert warnings


def test_repository_recovery_check_reuses_shared_documents(tmp_path, monkeypatch):
    main = tmp_path / "roles/web/tasks/main.yml"
    recovery = tmp_path / "roles/web/tasks/recovery.yml"
    main.parent.mkdir(parents=True)
    main.write_text(
        "- name: risky command\n"
        "  command: /bin/false\n"
        "  ignore_errors: true\n"
        "  register: result\n"
        "- include_tasks: recovery.yml\n",
        encoding="utf-8",
    )
    recovery.write_text(
        "- debug:\n    var: result\n",
        encoding="utf-8",
    )
    context = build_repository_analysis_context(tmp_path, [main, recovery])
    monkeypatch.setattr(
        "ansibleguard.detectors.review_checklist._repository_yaml_documents",
        lambda *_: (_ for _ in ()).throw(AssertionError("repository reparsed")),
    )

    assert detect_silent_error_suppression(
        main,
        symbol_index=object(),
        parsed_document=context.document_for(main),
        repository_context=context,
    ) == (0, [])


def test_role_defaults_are_reused_by_semantic_detectors(tmp_path, monkeypatch):
    defaults = tmp_path / "roles/web/defaults/main.yaml"
    tasks = tmp_path / "roles/web/tasks/main.yml"
    defaults.parent.mkdir(parents=True)
    tasks.parent.mkdir(parents=True)
    defaults.write_text("hide_credentials: true\nweb_mode: enabled\n", encoding="utf-8")
    tasks.write_text(
        "- name: configure password\n"
        "  example_module:\n"
        "    password: literal\n"
        "  no_log: '{{ hide_credentials }}'\n"
        "- name: repeat default\n"
        "  set_fact:\n"
        "    web_mode: enabled\n",
        encoding="utf-8",
    )
    context = build_repository_analysis_context(tmp_path, [defaults, tasks])
    monkeypatch.setattr(
        "ansibleguard.detectors.credentials_leaking_in_log._stdlib_yaml.safe_load",
        lambda *_: (_ for _ in ()).throw(AssertionError("defaults reparsed")),
    )

    assert detect_credentials_leaking_in_log(
        tasks,
        module_metadata={},
        parsed_document=context.document_for(tasks),
        repository_context=context,
    )[1] == 0
    assert detect_redundant_default_values(
        tasks,
        parsed_document=context.document_for(tasks),
        repository_context=context,
    )[0] == 1


def test_detector_families_skip_unselected_rule_work(tmp_path, monkeypatch):
    playbook = tmp_path / "tasks.yml"
    playbook.write_text(
        "- name: write file\n"
        "  file: {path: /tmp/example, mode: '0666'}\n",
        encoding="utf-8",
    )
    parsed = inspect_document(playbook)

    def forbidden(*_args, **_kwargs):
        raise AssertionError("unselected detector executed")

    monkeypatch.setattr(
        "ansibleguard.detectors.paper_candidates.detect_broken_role_dependencies",
        forbidden,
    )
    monkeypatch.setattr(
        "ansibleguard.detectors.review_checklist.detect_silent_error_suppression",
        forbidden,
    )
    monkeypatch.setattr(
        "ansibleguard.detectors.missing_checklist.detect_deprecated_module_options",
        forbidden,
    )

    paper = detect_paper_candidates(
        playbook,
        parsed_document=parsed,
        enabled_rules={"complex-expression"},
    )
    review = detect_review_checklist_smells(
        playbook,
        parsed_document=parsed,
        enabled_rules={"insecure-permissions"},
    )
    missing = detect_missing_checklist_smells(
        playbook,
        parsed_document=parsed,
        enabled_rules={"unexpected-task-location"},
    )

    assert paper["broken_role_dependencies"] == 0
    assert review["silent_error_suppressions"] == 0
    assert missing["deprecated_module_options"] == 0


def test_role_dependency_graph_reuses_shared_meta_documents(tmp_path, monkeypatch):
    files = []
    for role, dependency in (("web", "db"), ("db", "web")):
        tasks = tmp_path / f"roles/{role}/tasks/main.yml"
        meta = tmp_path / f"roles/{role}/meta/main.yml"
        tasks.parent.mkdir(parents=True)
        meta.parent.mkdir(parents=True)
        tasks.write_text("- debug: {msg: ready}\n", encoding="utf-8")
        meta.write_text(
            f"dependencies:\n  - {dependency}\n", encoding="utf-8"
        )
        files.extend((tasks, meta))
    context = build_repository_analysis_context(tmp_path, files)
    monkeypatch.setattr(
        type(files[0]),
        "read_text",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("role metadata reread")
        ),
    )

    count, details = detect_broken_role_dependencies(
        tmp_path / "roles/db/tasks/main.yml", repository_context=context
    )
    assert count == 1
    assert "cycle" in details[0]["issue"]


def test_size_metric_detectors_reuse_parsed_document(tmp_path, monkeypatch):
    playbook = tmp_path / "site.yml"
    playbook.write_text(
        "- name: web\n"
        "  hosts: all\n"
        "  tasks:\n"
        "    - name: noop\n"
        "      debug: {msg: ok}\n",
        encoding="utf-8",
    )
    parsed = inspect_document(playbook)

    def forbidden_open(*_args, **_kwargs):
        raise AssertionError("size metric detector reopened an already parsed YAML file")

    monkeypatch.setattr(builtins, "open", forbidden_open)
    assert calculate_metrics_task(playbook, parsed_document=parsed)[0]
    assert calculate_metrics_play(playbook, parsed_document=parsed)["Plays"]
    assert calculate_metrics_playbook(playbook, parsed_document=parsed)["num_plays"] == 1


def test_vault_overload_reuses_repository_documents(tmp_path, monkeypatch):
    tasks = tmp_path / "roles" / "web" / "tasks" / "main.yml"
    values = tmp_path / "roles" / "web" / "vars" / "vault.yml"
    tasks.parent.mkdir(parents=True)
    values.parent.mkdir(parents=True)
    tasks.write_text("- debug: {msg: ok}\n", encoding="utf-8")
    values.write_text(
        "one: !vault |\n  encrypted\n"
        "two: !vault |\n  encrypted\n"
        "three: !vault |\n  encrypted\n"
        "four: !vault |\n  encrypted\n",
        encoding="utf-8",
    )
    context = build_repository_analysis_context(tmp_path, [tasks, values])

    def forbidden_read(*_args, **_kwargs):
        raise AssertionError("vault detector reopened repository YAML")

    monkeypatch.setattr(Path, "read_text", forbidden_read)
    assert detect_vault_inline_overload(tasks, repository_context=context)[0] == 1
