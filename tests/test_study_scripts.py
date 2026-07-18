import csv
import json
from pathlib import Path
import subprocess

from scripts.clone_study_repositories import collect_row, read_selected, write_rows
from scripts.discover_openstack_ansible import candidate_rows, write_manifest
from scripts.run_study_pilot import (
    classification_manifest_path,
    load_collected,
    output_path,
    run_row,
)
from scripts.classify_study_files import generate_for_row
from ansibleguard.file_manifest import file_manifest_metadata


def _git(args, cwd):
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _create_repository(path):
    path.mkdir()
    _git(["init"], path)
    _git(["config", "user.name", "Study Test"], path)
    _git(["config", "user.email", "study@example.com"], path)
    (path / "roles" / "web" / "tasks").mkdir(parents=True)
    (path / "roles" / "web" / "tasks" / "main.yml").write_text(
        "- name: Configure web\n  debug:\n    msg: ready\n", encoding="utf-8"
    )
    (path / "tests").mkdir()
    (path / "tests" / "test.yml").write_text(
        "- name: Test web\n  hosts: localhost\n  tasks: []\n", encoding="utf-8"
    )
    (path / ".zuul.yaml").write_text("- job:\n    name: check\n", encoding="utf-8")
    _git(["add", "."], path)
    _git(["commit", "-m", "Initial study fixture"], path)
    return _git(["rev-parse", "HEAD"], path)


def test_candidate_discovery_is_openstack_only_and_never_auto_selects(tmp_path):
    entries = [
        {
            "project": "openstack/openstack-ansible-os_nova",
            "description": "Role os_nova for OpenStack-Ansible",
            "groups": ["openstack-ansible"],
        },
        {
            "project": "openstack/retired-ansible-role",
            "description": "RETIRED, old Ansible role",
            "acl-config": "openstack/retired.config",
        },
        {"project": "openstack/nova", "description": "Compute service"},
        {"project": "example/ansible", "description": "Not OpenStack"},
    ]
    rows = candidate_rows(entries, "2026-07-18T00:00:00+00:00", "fixture")
    assert [row["project"] for row in rows] == [
        "openstack/openstack-ansible-os_nova",
        "openstack/retired-ansible-role",
    ]
    assert all(row["selected"] == "false" for row in rows)
    assert rows[1]["retired"] == "true"
    assert rows[1]["exclusion_reason"] == "retired"

    manifest = write_manifest(rows, tmp_path / "candidates.csv")
    with manifest.open(newline="", encoding="utf-8") as stream:
        assert len(list(csv.DictReader(stream))) == 2


def test_collection_clones_selected_repository_and_freezes_sha(tmp_path):
    source = tmp_path / "source"
    expected_sha = _create_repository(source)
    manifest = tmp_path / "pilot.csv"
    manifest.write_text(
        "project,opendev_url,selected,revision\n"
        f"openstack/example,{source},true,\n"
        f"openstack/skipped,{source},false,\n",
        encoding="utf-8",
    )
    selected = read_selected(manifest)
    assert [row["project"] for row in selected] == ["openstack/example"]

    result = collect_row(selected[0], tmp_path / "repositories")
    assert result["status"] == "collected"
    assert result["commit_sha"] == expected_sha
    assert result["total_commits"] == "1"
    assert result["contributors"] == 1
    assert result["yaml_files"] == 3
    assert result["production_ansible_files"] == 1
    assert result["test_ansible_files"] == 1
    assert result["other_yaml_files"] == 1
    assert result["production_ansible_loc"] == 3

    frozen = write_rows([result], tmp_path / "frozen.csv")
    assert load_collected(frozen)[0]["commit_sha"] == expected_sha


def test_pilot_runner_refuses_a_repository_that_moved(tmp_path, monkeypatch):
    repository = tmp_path / "repository"
    expected_sha = _create_repository(repository)
    row = {
        "project": "openstack/example",
        "repository_path": str(repository),
        "commit_sha": expected_sha,
        "status": "collected",
    }
    assert output_path(tmp_path / "out", row["project"], expected_sha).name == expected_sha

    (repository / "new.yml").write_text("value: changed\n", encoding="utf-8")
    _git(["add", "."], repository)
    _git(["commit", "-m", "Move repository head"], repository)

    try:
        run_row(row, tmp_path / "out", tmp_path / "logs")
    except RuntimeError as exc:
        assert "frozen manifest requires" in str(exc)
    else:
        raise AssertionError("run_row accepted a repository whose HEAD moved")


def test_pilot_runner_writes_command_output(tmp_path, monkeypatch):
    repository = tmp_path / "repository"
    expected_sha = _create_repository(repository)
    row = {
        "project": "openstack/example",
        "repository_path": str(repository),
        "commit_sha": expected_sha,
        "status": "collected",
    }

    class Completed:
        returncode = 0

    calls = []

    def fake_run(command, stdout=None, stderr=None):
        calls.append(command)
        destination = Path(command[command.index("--output") + 1])
        destination.mkdir(parents=True, exist_ok=True)
        (destination / "findings.json").write_text("[]", encoding="utf-8")
        return Completed()

    monkeypatch.setattr("scripts.run_study_pilot.subprocess.run", fake_run)
    # _git_head also uses subprocess.run, so preserve it through a focused stub.
    monkeypatch.setattr("scripts.run_study_pilot._git_head", lambda path: expected_sha)
    status, destination = run_row(row, tmp_path / "out", tmp_path / "logs")
    assert status == "completed"
    assert (destination / "findings.json").is_file()
    assert "ansibleguard.cli" in calls[0]


def test_classification_generation_and_pilot_manifest_argument(tmp_path, monkeypatch):
    repository = tmp_path / "repository"
    expected_sha = _create_repository(repository)
    row = {
        "project": "openstack/example",
        "repository_path": str(repository),
        "commit_sha": expected_sha,
        "status": "collected",
    }
    manifests = tmp_path / "manifests"
    generated, rows = generate_for_row(row, manifests)
    assert generated == classification_manifest_path(
        manifests, row["project"], expected_sha
    )
    assert len(rows) == 3

    class Completed:
        returncode = 0

    calls = []

    def fake_run(command, stdout=None, stderr=None):
        calls.append(command)
        destination = Path(command[command.index("--output") + 1])
        destination.mkdir(parents=True, exist_ok=True)
        (destination / "findings.json").write_text("[]", encoding="utf-8")
        (destination / "file_selection.json").write_text(
            json.dumps(file_manifest_metadata(generated)), encoding="utf-8"
        )
        return Completed()

    monkeypatch.setattr("scripts.run_study_pilot.subprocess.run", fake_run)
    monkeypatch.setattr("scripts.run_study_pilot._git_head", lambda path: expected_sha)
    status, _ = run_row(
        row,
        tmp_path / "out",
        tmp_path / "logs",
        file_manifests_dir=manifests,
    )
    assert status == "completed"
    assert calls[0][calls[0].index("--file-manifest") + 1] == str(generated)
    status, _ = run_row(
        row,
        tmp_path / "out",
        tmp_path / "logs",
        skip_existing=True,
        file_manifests_dir=manifests,
    )
    assert status == "skipped"
    assert len(calls) == 1


def test_nontechnical_profile_uses_a_separate_output_directory(tmp_path):
    destination = output_path(
        tmp_path, "openstack/example", "a" * 40, "snapshot-source"
    )
    assert destination.parts[-2:] == (("a" * 40), "snapshot-source")
