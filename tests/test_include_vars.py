from ansibleguard.detectors.include_vars import detect_unused_include_vars
from ansibleguard.analysis_context import build_repository_analysis_context


def test_non_list_yaml_returns_tuple_not_bare_int(fixtures_dir):
    """Regression test: the dict-not-list early-return path returned a
    bare 0 instead of (0, []) like every other path in the function.
    parser_playbook.py always unpacks two values
    (unused_include_vars, WarningUnusedIncludeVars = ...), so this crashed
    with TypeError: cannot unpack non-iterable int object on any non-list
    top-level YAML (dict-shaped vars files, vault-encrypted files)."""
    fixture = fixtures_dir / "include_vars_not_a_list.yml"
    result = detect_unused_include_vars(str(fixture))
    count, warnings = result
    assert count == 0
    assert warnings == []


def test_dynamic_include_vars_is_unresolved_not_missing(tmp_path):
    playbook = tmp_path / "tasks.yml"
    playbook.write_text(
        "- name: Select platform vars\n"
        "  include_vars: '{{ item }}'\n"
        "  loop:\n"
        "    - debian.yml\n",
        encoding="utf-8",
    )

    assert detect_unused_include_vars(playbook) == (0, [])


def _write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_static_include_with_no_repository_references_is_reported(tmp_path):
    playbook = _write(
        tmp_path / "tasks" / "main.yml",
        "- name: Load settings\n  include_vars: ../vars/settings.yml\n",
    )
    _write(tmp_path / "tasks" / "../vars/settings.yml", "alpha: one\nbeta: two\n")

    count, details = detect_unused_include_vars(playbook)

    assert count == 1
    assert "none referenced" in details[0]


def test_cross_file_reference_keeps_static_include(tmp_path):
    playbook = _write(
        tmp_path / "tasks" / "main.yml",
        "- name: Load settings\n  include_vars: ../vars/settings.yml\n",
    )
    _write(tmp_path / "vars" / "settings.yml", "alpha: one\nbeta: two\n")
    _write(
        tmp_path / "tasks" / "consumer.yml",
        "- name: Consume setting\n  debug:\n    msg: '{{ alpha }}'\n",
    )

    assert detect_unused_include_vars(playbook) == (0, [])


def test_partial_use_is_not_called_an_unused_include(tmp_path):
    playbook = _write(
        tmp_path / "tasks" / "main.yml",
        "- name: Load settings\n  include_vars: ../vars/settings.yml\n"
        "- name: Consume one setting\n  debug:\n    msg: '{{ alpha }}'\n",
    )
    _write(tmp_path / "vars" / "settings.yml", "alpha: one\nbeta: two\n")

    assert detect_unused_include_vars(playbook) == (0, [])


def test_explicit_vars_lookup_counts_as_include_consumer(tmp_path):
    playbook = _write(
        tmp_path / "tasks" / "main.yml",
        "- name: Load settings\n  include_vars: ../vars/settings.yml\n"
        "- name: Consume indirectly\n  debug:\n"
        "    msg: '{{ vars[\"alpha\"] }}'\n",
    )
    _write(tmp_path / "vars" / "settings.yml", "alpha: one\n")

    assert detect_unused_include_vars(playbook) == (0, [])


def test_dynamic_variable_lookup_keeps_include_runtime_uncertain(tmp_path):
    playbook = _write(
        tmp_path / "tasks" / "main.yml",
        "- name: Load settings\n"
        "  include_vars: ../vars/settings.yml\n"
        "- name: Select setting dynamically\n"
        "  debug:\n"
        "    msg: '{{ vars[selected_setting] }}'\n",
    )
    _write(tmp_path / "vars" / "settings.yml", "alpha: one\nbeta: two\n")

    assert detect_unused_include_vars(playbook) == (0, [])


def test_dynamic_vars_lookup_plugin_keeps_include_runtime_uncertain(tmp_path):
    playbook = _write(
        tmp_path / "tasks" / "main.yml",
        "- include_vars: ../vars/settings.yml\n"
        "- debug:\n"
        "    msg: \"{{ lookup('vars', selected_setting) }}\"\n",
    )
    _write(tmp_path / "vars" / "settings.yml", "alpha: one\n")

    assert detect_unused_include_vars(playbook) == (0, [])


def test_dynamic_namespaced_include_lookup_keeps_include_runtime_uncertain(tmp_path):
    playbook = _write(
        tmp_path / "tasks" / "main.yml",
        "- include_vars:\n"
        "    file: ../vars/settings.yml\n"
        "    name: settings\n"
        "- debug:\n"
        "    msg: \"{{ vars['settings'][selected_setting] }}\"\n",
    )
    _write(tmp_path / "vars" / "settings.yml", "alpha: one\n")

    assert detect_unused_include_vars(playbook) == (0, [])


def test_shared_context_avoids_repository_reparse(tmp_path, monkeypatch):
    playbook = _write(
        tmp_path / "tasks" / "main.yml",
        "- name: Load settings\n  include_vars: ../vars/settings.yml\n",
    )
    variables = _write(tmp_path / "vars" / "settings.yml", "alpha: one\n")
    consumer = _write(
        tmp_path / "tasks" / "consumer.yml",
        "- debug:\n    msg: '{{ alpha }}'\n",
    )
    context = build_repository_analysis_context(
        tmp_path, [playbook, variables, consumer]
    )

    monkeypatch.setattr(
        "ansibleguard.detectors.include_vars._repository_documents",
        lambda *_: (_ for _ in ()).throw(AssertionError("repository reparsed")),
    )
    assert detect_unused_include_vars(
        playbook,
        repository_context=context,
        parsed_document=context.document_for(playbook),
    ) == (0, [])


def test_shared_context_abstains_for_include_outside_population(tmp_path):
    playbook = _write(
        tmp_path / "tasks" / "main.yml",
        "- include_vars: ../vars/settings.yml\n",
    )
    _write(tmp_path / "vars" / "settings.yml", "unused: value\n")
    context = build_repository_analysis_context(tmp_path, [playbook])

    assert detect_unused_include_vars(
        playbook, repository_context=context
    ) == (0, [])


def test_static_include_directory_reports_unused_file(tmp_path):
    playbook = _write(
        tmp_path / "tasks" / "main.yml",
        "- name: Load platform vars\n"
        "  include_vars:\n"
        "    dir: ../vars/platform\n",
    )
    _write(tmp_path / "vars" / "platform" / "debian.yml", "alpha: one\nbeta: two\n")

    count, details = detect_unused_include_vars(playbook)

    assert count == 1
    assert "directory" in details[0]
    assert "none referenced" in details[0]


def test_static_include_directory_preserves_namespace_reference(tmp_path):
    playbook = _write(
        tmp_path / "tasks" / "main.yml",
        "- name: Load platform vars\n"
        "  include_vars:\n"
        "    dir: ../vars/platform\n"
        "    name: platform\n"
        "- name: Use setting\n"
        "  debug:\n"
        "    msg: '{{ platform.alpha }}'\n",
    )
    variables = _write(tmp_path / "vars" / "platform" / "debian.yml", "alpha: one\n")
    consumer = _write(
        tmp_path / "tasks" / "consumer.yml",
        "- debug:\n    msg: '{{ platform.alpha }}'\n",
    )
    context = build_repository_analysis_context(tmp_path, [playbook, variables, consumer])

    assert detect_unused_include_vars(
        playbook, repository_context=context,
        parsed_document=context.document_for(playbook),
    ) == (0, [])
