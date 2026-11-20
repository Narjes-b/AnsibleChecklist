import hashlib
import pickle

from ansibleguard.document import PARSER_CACHE_VERSION, inspect_document
from ansibleguard.detectors.source_lines import source_line


def _write_cache_attack_marker(path):
    path.write_text("executed", encoding="utf-8")


class _ExecutablePickle:
    def __init__(self, marker):
        self.marker = marker

    def __reduce__(self):
        return (_write_cache_attack_marker, (self.marker,))


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


def test_non_utf8_yaml_has_explicit_status(tmp_path):
    target = tmp_path / "invalid-encoding.yml"
    target.write_bytes(b"\x85not utf-8\n")

    info = inspect_document(target)

    assert info.parse_status == "invalid-encoding"
    assert info.document_type == "unknown"
    assert info.diagnostics


def test_task_file_classified_by_shape(fixtures_dir):
    info = inspect_document(fixtures_dir / "parser_playbook_task_only.yml")
    assert info.document_type == "tasks"
    assert info.structurally_analyzable


def test_multi_document_yaml_is_parsed_once_and_retained(tmp_path):
    target = tmp_path / "multi.yml"
    target.write_text("a: 1\n---\nb: 2\n")
    info = inspect_document(target)
    assert info.parse_status == "parsed"
    assert info.document_type == "multi-document"
    assert info.documents == ({"a": 1}, {"b": 2})
    assert not info.structurally_analyzable


def test_ansible_and_unknown_tags_are_safe_and_recorded(tmp_path):
    target = tmp_path / "tags.yml"
    target.write_text(
        "unsafe_value: !unsafe '{{ literal }}'\n"
        "custom_value: !project_tag hello\n",
        encoding="utf-8",
    )

    info = inspect_document(target)

    assert info.parse_status == "parsed"
    assert {item["tag"] for item in info.tags} == {"!unsafe", "!project_tag"}
    assert info.document["unsafe_value"]["value"] == "{{ literal }}"


def test_duplicate_keys_are_diagnostic_not_parse_failure(tmp_path):
    target = tmp_path / "duplicates.yml"
    target.write_text("value: first\nvalue: second\n", encoding="utf-8")

    info = inspect_document(target)

    assert info.parse_status == "parsed"
    assert info.duplicate_keys[0]["key"] == "value"
    assert "Duplicate key" in info.diagnostics[0]


def test_parse_cache_never_executes_tampered_pickle_payload(tmp_path):
    source = tmp_path / "tasks.yml"
    source.write_text("- debug: {msg: ready}\n", encoding="utf-8")
    marker = tmp_path / "cache-code-executed"
    cache = tmp_path / "cache"
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    cache_key = hashlib.sha256(
        f"{PARSER_CACHE_VERSION}:{source.resolve()}:{source_hash}".encode()
    ).hexdigest()
    cache.mkdir()
    (cache / f"{cache_key}.json").write_bytes(
        pickle.dumps(_ExecutablePickle(marker))
    )
    stats = {}

    parsed = inspect_document(source, cache_dir=cache, cache_stats=stats)

    assert parsed.parse_status == "parsed"
    assert not marker.exists()
    assert stats["cache_errors"] == 1


def test_safe_document_retains_mapping_and_key_source_lines_through_cache(tmp_path):
    source = tmp_path / "tasks.yml"
    source.write_text(
        "---\n- name: first\n  debug:\n    msg: ready\n- debug:\n    msg: unnamed\n",
        encoding="utf-8",
    )
    cache = tmp_path / "cache"

    parsed = inspect_document(source, cache_dir=cache)
    cached = inspect_document(source, cache_dir=cache)

    for document in (parsed, cached):
        assert source_line(document.document[0]) == 2
        assert source_line(document.document[0], "debug") == 3
        assert source_line(document.document[1]) == 5
