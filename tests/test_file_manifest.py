import csv
import json

import pytest

from ansibleguard.cli import analyze_path, collect_yaml_files
from ansibleguard.external.gitleaks import ToolResult
from ansibleguard.file_manifest import (
    FileManifestError,
    classify_repository,
    included_files_from_manifest,
    read_file_manifest,
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
        "primary_ansibleguard_files": 1,
        "paper_comparable_files": 1,
        "import_only_ansible_files": 0,
    }


def test_classifier_ignores_ansible_runtime_cache(tmp_path):
    repository = _repository(tmp_path)
    cached = repository / ".ansible" / "roles" / "downloaded" / "tasks"
    cached.mkdir(parents=True)
    (cached / "main.yml").write_text("- debug:\n    msg: cache\n")

    paths = {row["path"] for row in classify_repository(repository)}

    assert not any(path.startswith(".ansible/") for path in paths)


@pytest.mark.parametrize(
    "directory", ("fixture", "fixtures", "spec", "specs", "testdata", "test_data")
)
def test_task_shaped_fixture_paths_never_enter_production_population(
    tmp_path, directory
):
    repository = tmp_path / "repository"
    source = repository / "roles" / "web" / directory / "tasks.yml"
    source.parent.mkdir(parents=True)
    source.write_text("- name: Fixture task\n  debug: {msg: test}\n")

    row = classify_repository(repository)[0]

    assert row["file_class"] == "fixture_or_generated"
    assert row["included"] == "false"


@pytest.mark.parametrize("directory", ("demo", "demos", "sample", "samples"))
def test_demo_and_sample_tasks_are_explicit_examples(tmp_path, directory):
    source = tmp_path / directory / "tasks.yml"
    source.parent.mkdir(parents=True)
    source.write_text("- debug: {msg: example}\n", encoding="utf-8")

    row = classify_repository(tmp_path)[0]

    assert row["file_class"] == "documentation_example"
    assert row["included"] == "false"


@pytest.mark.parametrize("directory", ("archive", "archived"))
def test_archived_tasks_are_a_historical_population(tmp_path, directory):
    source = tmp_path / directory / "tasks.yml"
    source.parent.mkdir(parents=True)
    source.write_text("- debug: {msg: old}\n", encoding="utf-8")

    row = classify_repository(tmp_path)[0]

    assert row["file_class"] == "historical_ansible"
    assert row["included"] == "false"


def test_classifier_records_non_utf8_yaml_without_stopping(tmp_path):
    repository = tmp_path / "repository"
    tasks = repository / "roles" / "broken" / "tasks"
    tasks.mkdir(parents=True)
    target = tasks / "main.yml"
    target.write_bytes(b"\x85not utf-8\n")

    rows = classify_repository(repository)

    assert len(rows) == 1
    assert rows[0]["path"] == "roles/broken/tasks/main.yml"
    assert rows[0]["parse_status"] == "invalid-encoding"
    assert rows[0]["file_class"] == "invalid_yaml"
    assert rows[0]["classification_reason"] == "parse_status_invalid-encoding"
    assert rows[0]["loc"] == "0"
    assert rows[0]["included"] == "false"


def test_comment_only_group_vars_are_recorded_but_not_analyzable(tmp_path):
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
    assert row["file_class"] == "other_yaml"
    assert row["classification_reason"] == "empty_yaml"
    assert row["included"] == "false"
    assert row["primary_ansibleguard_cohort"] == "false"


def test_primary_and_paper_cohorts_distinguish_vars_and_import_only(tmp_path):
    repository = tmp_path / "repository"
    tasks = repository / "roles" / "web" / "tasks"
    defaults = repository / "roles" / "web" / "defaults"
    tasks.mkdir(parents=True)
    defaults.mkdir(parents=True)
    (tasks / "imports.yml").write_text("- import_tasks: configure.yml\n")
    (defaults / "main.yml").write_text("service_enabled: true\n")
    rows = {row["path"]: row for row in classify_repository(repository)}
    imported = rows["roles/web/tasks/imports.yml"]
    variables = rows["roles/web/defaults/main.yml"]
    assert imported["import_only"] == "true"
    assert imported["primary_ansibleguard_cohort"] == "true"
    assert imported["paper_comparable_cohort"] == "false"
    assert variables["ansible_artifact_kind"] == "defaults"
    assert variables["primary_ansibleguard_cohort"] == "true"
    assert variables["paper_comparable_cohort"] == "false"


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


def test_legacy_manifest_without_cohort_columns_remains_readable(tmp_path):
    repository = _repository(tmp_path)
    rows = classify_repository(repository)
    for row in rows:
        for field in (
            "ansible_artifact_kind", "import_only", "primary_ansibleguard_cohort",
            "paper_comparable_cohort", "cohort_reason",
        ):
            row.pop(field)
    manifest = tmp_path / "legacy.csv"
    fields = list(rows[0])
    with manifest.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    loaded = read_file_manifest(manifest)
    assert loaded[0]["primary_ansibleguard_cohort"] in {"true", "false"}
    assert loaded[0]["paper_comparable_cohort"] == "not-evaluated"


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


def test_build_and_vendor_role_names_are_not_generated(tmp_path):
    repository = _repository(tmp_path)
    for role_name in ("build", "vendor"):
        tasks = repository / "roles" / role_name / "tasks" / "main.yml"
        tasks.parent.mkdir(parents=True)
        tasks.write_text("- debug: {msg: ready}\n", encoding="utf-8")
    root_build = repository / "build" / "generated.yml"
    root_build.parent.mkdir()
    root_build.write_text("- debug: {msg: generated}\n", encoding="utf-8")

    by_path = {row["path"]: row for row in classify_repository(repository)}

    assert by_path["roles/build/tasks/main.yml"]["file_class"] == "production_ansible"
    assert by_path["roles/vendor/tasks/main.yml"]["file_class"] == "production_ansible"
    assert by_path["build/generated.yml"]["file_class"] == "generated_or_vendor"


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
