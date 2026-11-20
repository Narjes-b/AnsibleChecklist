import csv
import json
from pathlib import Path
import subprocess

import pytest

from scripts.build_v005_diagnostic_cohort import (
    DIAGNOSTIC_PROJECTS,
    build_cohort,
)

from scripts.clone_study_repositories import collect_row, read_selected, write_rows
from scripts.discover_openstack_ansible import candidate_rows, write_manifest
from scripts.run_study_pilot import (
    classification_manifest_path,
    load_collected,
    output_path,
    run_row,
)
from scripts.scan_and_summarize_repositories import main as scan_all_main
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


def test_collection_removes_the_clone_when_a_later_step_fails(tmp_path, monkeypatch):
    # A failure after cloning (checkout, classification, git log parsing)
    # can leave the working directory in a bad state -- e.g. a killed
    # process leaves a stale index.lock that makes every subsequent git
    # command on this repo fail forever. Because _clone_or_update's
    # ".git exists" fast path treats any existing .git directory as "already
    # cloned, nothing to do", a repository that goes bad once would
    # otherwise never actually be re-cloned on retry.
    source = tmp_path / "source"
    _create_repository(source)
    manifest = tmp_path / "pilot.csv"
    manifest.write_text(
        "project,opendev_url,selected,revision\n"
        f"openstack/example,{source},true,\n",
        encoding="utf-8",
    )
    selected = read_selected(manifest)
    repos_dir = tmp_path / "repositories"

    import scripts.clone_study_repositories as mod

    monkeypatch.setattr(
        mod, "classify_repository",
        lambda repository: (_ for _ in ()).throw(RuntimeError("simulated corruption")),
    )

    result = collect_row(selected[0], repos_dir)

    assert result["status"] == "failed"
    destination = repos_dir / "openstack" / "example"
    assert not destination.exists(), "a broken clone must be removed, not reused on retry"


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


def test_collection_screening_flag_does_not_imply_final_selection(tmp_path):
    manifest = tmp_path / "screening.csv"
    manifest.write_text(
        "project,collect_for_screening,selected\n"
        "example/screen,true,false\n"
        "example/final,false,true\n"
        "example/ignored,false,false\n",
        encoding="utf-8",
    )

    assert [row["project"] for row in read_selected(manifest)] == [
        "example/screen",
        "example/final",
    ]


def test_frozen_writer_marks_exact_ansible_content_groups(tmp_path):
    rows = [
        {"project": "one/role", "ansible_content_fingerprint": "same", "status": "collected"},
        {"project": "two/role", "ansible_content_fingerprint": "same", "status": "collected"},
    ]
    write_rows(rows, tmp_path / "frozen.csv")
    assert rows[0]["exact_ansible_duplicate_group"] == "exact-ansible-content-1"
    assert rows[1]["exact_ansible_duplicate_group"] == "exact-ansible-content-1"
    assert rows[0]["independence_review_status"] == "exact-content-match-needs-review"


def test_collection_supports_github_rows_and_records_postclone_gates(tmp_path):
    source = tmp_path / "github-source"
    expected_sha = _create_repository(source)
    row = {
        "project": "example/ansible-role-web",
        "source_host": "github",
        "source_url": "https://github.com/example/ansible-role-web",
        "clone_url": str(source),
        "html_url": "https://github.com/example/ansible-role-web",
        "stars": "150",
        "star_band": "100-999",
        "forks": "20",
        "license_spdx": "MIT",
        "merged_prs_last_24_months": "7",
        "preclone_eligible": "true",
    }

    result = collect_row(row, tmp_path / "repositories")

    assert result["status"] == "collected"
    assert result["commit_sha"] == expected_sha
    assert result["source_host"] == "github"
    assert result["opendev_url"] == ""
    assert result["github_url"] == row["html_url"]
    assert result["stars"] == "150"
    assert result["yaml_loc"] == 8
    assert result["production_ansible_yaml_file_percent"] == 33.33
    assert result["production_ansible_yaml_loc_percent"] == 37.5
    assert result["ansible_touching_commits"] == 1
    assert result["repository_total_files"] == 3
    assert result["production_ansible_repository_file_percent"] == 33.33
    assert result["production_task_files"] == 1
    assert result["first_ansible_commit_date_utc"]
    assert result["latest_ansible_commit_date_utc"]
    assert result["ansible_history_span_days"] == "0"
    assert result["repository_owner"] == "example"
    assert result["repository_family"] == "role-web"
    assert result["project_purpose_auto"] == "example-or-training-candidate"
    assert len(result["ansible_content_fingerprint"]) == 64
    assert result["descriptive_evidence_used_for_selection"] == "false"
    assert result["eligibility_status"] == "ineligible"
    assert "fewer-than-1000-commits" in result["eligibility_reasons"]
    assert "total-prs-not-evaluated" in result["eligibility_reasons"]


def test_collection_records_unexpected_repository_error(monkeypatch, tmp_path):
    source = tmp_path / "github-source"
    _create_repository(source)
    row = {
        "project": "example/broken-role",
        "source_host": "github",
        "clone_url": str(source),
    }

    def fail_classification(*args, **kwargs):
        raise ValueError("unexpected classifier failure")

    monkeypatch.setattr(
        "scripts.clone_study_repositories.classify_repository",
        fail_classification,
    )

    result = collect_row(row, tmp_path / "repositories")

    assert result["status"] == "failed"
    assert result["project"] == "example/broken-role"
    assert result["error"] == "ValueError: unexpected classifier failure"


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
    status, destination = run_row(
        row,
        tmp_path / "out",
        tmp_path / "logs",
        python_executable="/study/version/bin/python",
    )
    assert status == "completed"
    assert (destination / "findings.json").is_file()
    assert calls[0][0] == "/study/version/bin/python"
    assert "ansibleguard.cli" in calls[0]


def test_pilot_runner_classifies_repository_timeout_as_failure(tmp_path, monkeypatch):
    repository = tmp_path / "repository"
    expected_sha = _create_repository(repository)
    row = {
        "project": "openstack/example",
        "repository_path": str(repository),
        "commit_sha": expected_sha,
        "status": "collected",
    }

    def time_out(command, **kwargs):
        raise subprocess.TimeoutExpired(command, kwargs["timeout"])

    monkeypatch.setattr("scripts.run_study_pilot.subprocess.run", time_out)
    monkeypatch.setattr("scripts.run_study_pilot._git_head", lambda path: expected_sha)

    with pytest.raises(RuntimeError, match="timed out after 12 seconds"):
        run_row(
            row,
            tmp_path / "out",
            tmp_path / "logs",
            repository_timeout=12,
        )


def test_pilot_runner_rejects_existing_output_from_another_research_image(
    tmp_path, monkeypatch
):
    repository = tmp_path / "repository"
    expected_sha = _create_repository(repository)
    row = {
        "project": "openstack/example",
        "repository_path": str(repository),
        "commit_sha": expected_sha,
        "status": "collected",
    }
    destination = output_path(tmp_path / "out", row["project"], expected_sha)
    destination.mkdir(parents=True)
    (destination / "findings.json").write_text("[]", encoding="utf-8")
    (destination / "run_metadata.json").write_text(
        json.dumps(
            {
                "profile": {"name": "technical-full"},
                "reproducibility": {
                    "research_image_digest": "sha256:old",
                    "ansibleguard_git_sha": "old-commit",
                },
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("ANSIBLEGUARD_RESEARCH_IMAGE_DIGEST", "sha256:expected")
    monkeypatch.setenv("ANSIBLEGUARD_BUILD_GIT_SHA", "expected-commit")

    try:
        run_row(
            row,
            tmp_path / "out",
            tmp_path / "logs",
            skip_existing=True,
        )
    except RuntimeError as exc:
        assert "different research image" in str(exc)
    else:
        raise AssertionError("run_row reused output from another research image")


def test_full_scan_requires_research_container_provenance(tmp_path, monkeypatch):
    manifest = tmp_path / "frozen.csv"
    manifest.write_text("project,status\n", encoding="utf-8")
    monkeypatch.delenv("ANSIBLEGUARD_RESEARCH_IMAGE_DIGEST", raising=False)
    monkeypatch.delenv("ANSIBLEGUARD_BUILD_GIT_SHA", raising=False)

    try:
        scan_all_main([str(manifest), "--require-research-container"])
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("full scan ran without research-container provenance")


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


def test_v005_diagnostic_cohort_builder_is_ordered_and_reproducible(tmp_path):
    source = tmp_path / "frozen.csv"
    source.write_text(
        "project,commit_sha,status\n"
        + "".join(
            f"{project},{index:040x},collected\n"
            for index, project in enumerate(reversed(DIAGNOSTIC_PROJECTS), 1)
        ),
        encoding="utf-8",
    )
    first = tmp_path / "first.csv"
    second = tmp_path / "second.csv"

    assert build_cohort(source, first) == 15
    assert build_cohort(source, second) == 15

    assert first.read_bytes() == second.read_bytes()
    with first.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    assert [row["project"] for row in rows] == list(DIAGNOSTIC_PROJECTS)
