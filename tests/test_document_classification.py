from ansibleguard.document import inspect_document


def test_dict_shaped_vars_file_is_valid_but_not_structural(fixtures_dir):
    info = inspect_document(fixtures_dir / "vars_file_not_a_playbook.yml")
    assert info.parse_status == "parsed"
    assert info.document_type == "vars"
    assert not info.structurally_analyzable


def test_inline_vault_tag_is_loaded_safely_and_classified_as_vars(fixtures_dir):
    info = inspect_document(fixtures_dir / "vars_inline_vault.yaml")
    assert info.parse_status == "parsed"
    assert info.document_type == "vars"
    assert info.document["database_password"]["__ansible_tag__"] == "!vault"


def test_invalid_yaml_has_explicit_status(fixtures_dir):
    info = inspect_document(fixtures_dir / "invalid_with_secret.yaml")
    assert info.parse_status == "invalid"
    assert info.document_type == "unknown"
    assert info.diagnostics


def test_task_file_classified_by_shape(fixtures_dir):
    info = inspect_document(fixtures_dir / "parser_playbook_task_only.yml")
    assert info.document_type == "tasks"
    assert info.structurally_analyzable


def test_multi_document_yaml_is_explicitly_unsupported(tmp_path):
    target = tmp_path / "multi.yml"
    target.write_text("a: 1\n---\nb: 2\n")
    info = inspect_document(target)
    assert info.parse_status == "unsupported"
    assert info.document_type == "multi-document"
