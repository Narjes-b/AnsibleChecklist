import csv
import json

import pytest

from ansibleguard.cli import analyze_path, collect_yaml_files
from ansibleguard.external.gitleaks import ToolResult
from ansibleguard.file_manifest import (
    FileManifestError,
    classify_repository,
    included_files_from_manifest,
    summarize_classification,
    write_file_manifest,
)


def _repository(tmp_path):
    repository = tmp_path / "repository"
    tasks = repository / "roles" / "web" / "tasks"
    tasks.mkdir(parents=True)
    (tasks / "main.yml").write_text(
        "- name: Configure web\n  debug:\n    msg: ready\n", encoding="utf-8"
    )
    tests = repository / "tests"
    tests.mkdir()
    (tests / "integration.yml").write_text(
        "- name: Exercise role\n  hosts: localhost\n  tasks: []\n", encoding="utf-8"
    )
    docs = repository / "docs"
    docs.mkdir()
    (docs / "example.yml").write_text("setting: example\n", encoding="utf-8")
    (repository / ".zuul.yaml").write_text(
        "- job:\n    name: check\n", encoding="utf-8"
    )
    (repository / "broken.yaml").write_text("broken: [yaml\n", encoding="utf-8")
    return repository


def test_classifier_emits_one_explained_row_per_yaml_candidate(tmp_path):
    repository = _repository(tmp_path)
    data = repository / "roles" / "web" / "files"
    data.mkdir()
    (data / "application.yaml").write_text("setting: value\n", encoding="utf-8")
    (repository / "roles" / "web" / "tasks" / "alias.yml").symlink_to("main.yml")
    rows = classify_repository(repository, "openstack/example", "a" * 40)

    assert len(rows) == 7
    by_path = {row["path"]: row for row in rows}
    assert by_path["roles/web/tasks/main.yml"]["file_class"] == "production_ansible"
    assert by_path["roles/web/tasks/main.yml"]["included"] == "true"
    assert by_path["tests/integration.yml"]["file_class"] == "test_ansible"
    assert by_path[".zuul.yaml"]["file_class"] == "ci_yaml"
    assert by_path["docs/example.yml"]["file_class"] == "documentation_example"
    assert by_path["broken.yaml"]["file_class"] == "invalid_yaml"
    assert by_path["roles/web/files/application.yaml"]["file_class"] == "other_yaml"
    assert (
        by_path["roles/web/tasks/alias.yml"]["classification_reason"]
        == "symlink_alias_to_repository_file"
    )
    assert all(row["classification_reason"] for row in rows)
    assert all(
        not row["exclusion_reason"] if row["included"] == "true" else row["exclusion_reason"]
        for row in rows
    )

    counts = summarize_classification(rows)
    assert counts == {
        "yaml_files": 7,
        "production_ansible_files": 1,
        "test_ansible_files": 1,
        "other_yaml_files": 4,
        "invalid_yaml_files": 1,
        "production_ansible_loc": 3,
    }


def test_classifier_ignores_ansible_runtime_cache(tmp_path):
    repository = _repository(tmp_path)
    cached = repository / ".ansible" / "roles" / "downloaded" / "tasks"
    cached.mkdir(parents=True)
    (cached / "main.yml").write_text("- debug:\n    msg: cache\n")

    paths = {row["path"] for row in classify_repository(repository)}

    assert not any(path.startswith(".ansible/") for path in paths)


def test_comment_only_group_vars_are_empty_production_ansible(tmp_path):
    repository = tmp_path / "repository"
    group_vars = repository / "inventory" / "sample" / "group_vars" / "all"
    group_vars.mkdir(parents=True)
    (group_vars / "cloud.yml").write_text(
        "# Enable this provider when needed\n# provider_enabled: true\n",
        encoding="utf-8",
    )

    row = classify_repository(repository)[0]

    assert row["parse_status"] == "empty"
    assert row["document_type"] == "empty"
    assert row["file_class"] == "production_ansible"
    assert row["classification_reason"] == "ansible_role_or_inventory_path"
    assert row["included"] == "true"


def test_manifest_selects_only_included_files_and_requires_complete_coverage(tmp_path):
    repository = _repository(tmp_path)
    rows = classify_repository(repository)
    manifest = write_file_manifest(rows, tmp_path / "files.csv")

    selected = included_files_from_manifest(repository, manifest)
    assert [path.relative_to(repository).as_posix() for path in selected] == [
        "roles/web/tasks/main.yml"
    ]
    assert collect_yaml_files(repository, manifest) == selected

    with manifest.open(newline="", encoding="utf-8") as stream:
        incomplete = list(csv.DictReader(stream))[1:]
    write_file_manifest(incomplete, manifest)
    with pytest.raises(FileManifestError, match="manifest does not match target"):
        included_files_from_manifest(repository, manifest)


def test_classifier_handles_deployment_config_and_dependency_manifests(tmp_path):
    repository = tmp_path / "repository"
    config = repository / "etc" / "kayobe"
    config.mkdir(parents=True)
    (config / "globals.yml").write_text("deployment_mode: production\n")
    (repository / "ansible-role-requirements.yml").write_text(
        "- name: external_role\n  src: example.external_role\n"
    )
    notes = repository / " releasenotes" / "notes"
    notes.mkdir(parents=True)
    (notes / "change.yml").write_text("features:\n  - New behavior\n")

    by_path = {
        row["path"]: row for row in classify_repository(repository)
    }

    assert by_path["etc/kayobe/globals.yml"]["file_class"] == "production_ansible"
    assert by_path["etc/kayobe/globals.yml"]["included"] == "true"
    assert (
        by_path["ansible-role-requirements.yml"]["classification_reason"]
        == "ansible_dependency_manifest"
    )
    assert by_path["ansible-role-requirements.yml"]["included"] == "false"
    assert by_path[" releasenotes/notes/change.yml"]["file_class"] == (
        "documentation_example"
    )
    manifest = write_file_manifest(by_path.values(), tmp_path / "classified.csv")
    assert included_files_from_manifest(repository, manifest) == [
        config / "globals.yml"
    ]


def test_manifest_rejects_repository_escape_paths(tmp_path):
    repository = _repository(tmp_path)
    rows = classify_repository(repository)
    rows[0]["path"] = "../outside.yml"
    manifest = write_file_manifest(rows, tmp_path / "unsafe.csv")
    with pytest.raises(FileManifestError, match="safe repository-relative"):
        included_files_from_manifest(repository, manifest)


def test_cli_manifest_scan_excludes_unselected_yaml_findings(tmp_path, monkeypatch):
    repository = tmp_path / "repository"
    tasks = repository / "roles" / "web" / "tasks"
    tasks.mkdir(parents=True)
    (tasks / "main.yml").write_text(
        "- name: Configure web\n  debug:\n    msg: ready\n", encoding="utf-8"
    )
    (repository / ".zuul.yaml").write_text(
        "- job:\n    name: check\n", encoding="utf-8"
    )
    manifest = write_file_manifest(
        classify_repository(repository, "openstack/example", "b" * 40),
        tmp_path / "files.csv",
    )
    monkeypatch.setattr(
        "ansibleguard.external.gitleaks.scan_with_gitleaks",
        lambda *args, **kwargs: ToolResult(
            "completed",
            [
                {
                    "File": "roles/web/tasks/main.yml",
                    "StartLine": 1,
                    "Description": "included fixture",
                },
                {
                    "File": ".zuul.yaml",
                    "StartLine": 1,
                    "Description": "excluded fixture",
                },
            ],
        ),
    )
    monkeypatch.setattr(
        "ansibleguard.external.ansible_lint.scan_with_ansible_lint",
        lambda *args, **kwargs: ToolResult("completed"),
    )

    output = tmp_path / "output"
    run = analyze_path(repository, output, file_manifest=manifest)

    assert run["discovered"] == 1
    summary = (output / "summary.csv").read_text(encoding="utf-8")
    assert "roles/web/tasks/main.yml" in summary
    assert ".zuul.yaml" not in summary
    findings = json.loads((output / "findings.json").read_text(encoding="utf-8"))
    assert all(".zuul.yaml" not in finding["file"] for finding in findings)
    selection = json.loads(
        (output / "file_selection.json").read_text(encoding="utf-8")
    )
    assert selection["mode"] == "classification-manifest"
    assert selection["candidate_rows"] == 2
    assert selection["included_files"] == 1
    assert len(selection["manifest_sha256"]) == 64
