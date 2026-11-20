import json
from pathlib import Path

import pytest

from ansibleguard.cli import analyze_path
from ansibleguard.sources.local import LocalSource
from ansibleguard.sources.capabilities import validate_profile_capabilities
from ansibleguard.sources.errors import SourceCapabilityError
from ansibleguard.sources.snapshot import (
    MaterializedSource,
    SourceSnapshot,
    fingerprint_tree,
)


def _repository(path: Path) -> Path:
    tasks = path / "roles" / "web" / "tasks"
    defaults = path / "roles" / "web" / "defaults"
    tasks.mkdir(parents=True)
    defaults.mkdir(parents=True)
    (defaults / "main.yml").write_text("web_port: 8080\n", encoding="utf-8")
    (tasks / "main.yml").write_text(
        "- name: Show port\n  debug:\n    msg: '{{ web_port }}'\n",
        encoding="utf-8",
    )
    return path


def _items(path: Path):
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload.get("items", payload) if isinstance(payload, dict) else payload


def test_tree_fingerprint_is_independent_of_absolute_acquisition_path(tmp_path):
    first = _repository(tmp_path / "first")
    second = _repository(tmp_path / "second")

    first_hash, first_entries = fingerprint_tree(first)
    second_hash, second_entries = fingerprint_tree(second)

    assert first_hash == second_hash
    assert first_entries == second_entries
    assert str(first) not in json.dumps(first_entries)


def test_tree_fingerprint_excludes_git_and_analysis_output(tmp_path):
    repository = _repository(tmp_path / "repository")
    baseline, _ = fingerprint_tree(repository)
    (repository / ".git").mkdir()
    (repository / ".git" / "config").write_text("secret", encoding="utf-8")
    (repository / "ansibleguard-output").mkdir()
    (repository / "ansibleguard-output" / "findings.json").write_text(
        "[]", encoding="utf-8"
    )

    assert fingerprint_tree(repository)[0] == baseline


def test_tree_fingerprint_changes_when_source_bytes_change(tmp_path):
    repository = _repository(tmp_path / "repository")
    before, _ = fingerprint_tree(repository)
    (repository / "roles" / "web" / "defaults" / "main.yml").write_text(
        "web_port: 9090\n", encoding="utf-8"
    )
    assert fingerprint_tree(repository)[0] != before


def test_local_source_produces_credential_free_provenance(tmp_path):
    repository = _repository(tmp_path / "repository")
    with LocalSource(repository).materialize() as snapshot:
        provenance = snapshot.provenance()

    assert provenance["provider"] == "local"
    assert provenance["acquisition"] == "filesystem"
    assert len(provenance["tree_sha256"]) == 64
    assert provenance["temporary"] is False
    assert "token" not in json.dumps(provenance).lower()


def test_materialized_source_removes_temporary_directory_after_success(tmp_path):
    temporary = tmp_path / "temporary"
    temporary.mkdir()
    snapshot = SourceSnapshot(temporary, "fixture", temporary=True)

    with MaterializedSource.temporary_directory(snapshot, temporary):
        assert temporary.is_dir()

    assert not temporary.exists()


def test_materialized_source_removes_temporary_directory_after_failure(tmp_path):
    temporary = tmp_path / "temporary"
    temporary.mkdir()
    snapshot = SourceSnapshot(temporary, "fixture", temporary=True)

    with pytest.raises(RuntimeError):
        with MaterializedSource.temporary_directory(snapshot, temporary):
            raise RuntimeError("analysis failed")

    assert not temporary.exists()


def test_direct_local_and_explicit_local_source_are_analysis_equivalent(tmp_path):
    repository = _repository(tmp_path / "repository")
    direct_output = tmp_path / "direct-output"
    source_output = tmp_path / "source-output"

    direct = analyze_path(repository, direct_output, profile="developer-fast")
    with LocalSource(repository).materialize() as snapshot:
        via_source = analyze_path(
            snapshot.root,
            source_output,
            profile="developer-fast",
            source_snapshot=snapshot,
        )

    assert direct == via_source
    assert _items(direct_output / "canonical" / "occurrences.json") == _items(
        source_output / "canonical" / "occurrences.json"
    )
    assert _items(direct_output / "raw" / "findings.json") == _items(
        source_output / "raw" / "findings.json"
    )
    direct_metadata = json.loads((direct_output / "run_metadata.json").read_text())
    source_metadata = json.loads((source_output / "run_metadata.json").read_text())
    assert direct_metadata["symbol_index"] == source_metadata["symbol_index"]
    assert direct_metadata["source"] == source_metadata["source"]


def test_review_profile_rejects_working_tree_without_git_history(tmp_path):
    repository = _repository(tmp_path / "repository")
    with LocalSource(repository).materialize() as snapshot:
        with pytest.raises(SourceCapabilityError, match="requires Git history"):
            validate_profile_capabilities(snapshot, "technical-full")
        validate_profile_capabilities(snapshot, "developer-fast")
