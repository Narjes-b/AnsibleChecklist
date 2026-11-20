"""Tests for checkpoint/resume behavior in the large-scale collection stages.

Both clone_study_repositories.py and classify_study_files.py previously
processed their whole repository list in memory and wrote output only once
at the very end -- a process-level interruption (kill, crash, closed
terminal) partway through a run of hundreds of repositories lost every
already-completed repository's result, forcing a full restart. Both scripts
now support --skip-existing (resume from a prior checkpoint) and write
incrementally (clone) or isolate per-row failures (classify) so the rest of
a large batch survives one bad repository.
"""
import csv
import subprocess

import pytest

from scripts.clone_study_repositories import main as clone_main
from scripts.classify_study_files import main as classify_main, manifest_path


def _git(args, cwd):
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True,
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
    _git(["add", "."], path)
    _git(["commit", "-m", "Initial study fixture"], path)
    return _git(["rev-parse", "HEAD"], path)


def _write_selection_manifest(path, projects_and_sources):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["project", "clone_url", "selected"])
        writer.writeheader()
        for project, source in projects_and_sources:
            writer.writerow({"project": project, "clone_url": str(source), "selected": "true"})


def test_clone_skip_existing_does_not_recollect_already_frozen_rows(tmp_path, monkeypatch):
    source_a = tmp_path / "source-a"
    source_b = tmp_path / "source-b"
    _create_repository(source_a)
    _create_repository(source_b)

    manifest = tmp_path / "selection.csv"
    _write_selection_manifest(manifest, [("org/a", source_a), ("org/b", source_b)])

    already_cloned = tmp_path / "repos" / "org" / "a"
    already_cloned.mkdir(parents=True)

    output = tmp_path / "frozen.csv"
    with output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=["project", "status", "commit_sha", "repository_path"]
        )
        writer.writeheader()
        writer.writerow({
            "project": "org/a", "status": "collected", "commit_sha": "prior-sha",
            "repository_path": str(already_cloned),
        })

    calls = []
    import scripts.clone_study_repositories as mod

    def fake_collect_row(row, repos_dir, refresh=False):
        calls.append(row["project"])
        base = {field: "" for field in mod.OUTPUT_FIELDS}
        base.update(project=row["project"], status="collected", commit_sha="fresh-sha")
        return base

    monkeypatch.setattr(mod, "collect_row", fake_collect_row)

    clone_main([
        str(manifest), "--output", str(output), "--repos-dir", str(tmp_path / "repos"),
        "--skip-existing",
    ])

    assert calls == ["org/b"]
    with output.open(newline="", encoding="utf-8") as stream:
        rows = {row["project"]: row for row in csv.DictReader(stream)}
    assert rows["org/a"]["commit_sha"] == "prior-sha"
    assert rows["org/b"]["commit_sha"] == "fresh-sha"


def test_clone_skip_existing_reclones_when_directory_was_deleted(tmp_path, monkeypatch):
    # A repository can be marked status=collected from an earlier pipeline
    # attempt, then have its clone directory deleted afterward -- e.g. it
    # was disqualified and pruned, then became eligible again in a later
    # attempt once more evidence accumulated. Trusting the CSV's "collected"
    # status alone would skip re-cloning it forever, silently leaving an
    # eligible repository with no clone on disk.
    source = tmp_path / "source"
    _create_repository(source)
    manifest = tmp_path / "selection.csv"
    _write_selection_manifest(manifest, [("org/gone", source)])

    output = tmp_path / "frozen.csv"
    missing_dir = tmp_path / "repos" / "org" / "gone"  # never created / already removed
    with output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=["project", "status", "commit_sha", "repository_path"]
        )
        writer.writeheader()
        writer.writerow({
            "project": "org/gone", "status": "collected", "commit_sha": "stale-sha",
            "repository_path": str(missing_dir),
        })

    calls = []
    import scripts.clone_study_repositories as mod

    def fake_collect_row(row, repos_dir, refresh=False):
        calls.append(row["project"])
        base = {field: "" for field in mod.OUTPUT_FIELDS}
        base.update(project=row["project"], status="collected", commit_sha="fresh-sha")
        return base

    monkeypatch.setattr(mod, "collect_row", fake_collect_row)

    clone_main([
        str(manifest), "--output", str(output), "--repos-dir", str(tmp_path / "repos"),
        "--skip-existing",
    ])

    assert calls == ["org/gone"], "a collected row whose directory is gone must be re-cloned"


def test_clone_writes_a_checkpoint_after_every_repository(tmp_path, monkeypatch):
    source_a = tmp_path / "source-a"
    source_b = tmp_path / "source-b"
    _create_repository(source_a)
    _create_repository(source_b)
    manifest = tmp_path / "selection.csv"
    _write_selection_manifest(manifest, [("org/a", source_a), ("org/b", source_b)])
    output = tmp_path / "frozen.csv"

    import scripts.clone_study_repositories as mod
    write_calls = []
    real_write_rows = mod.write_rows

    def counting_write_rows(rows, output_path):
        write_calls.append(len(rows))
        return real_write_rows(rows, output_path)

    monkeypatch.setattr(mod, "write_rows", counting_write_rows)

    clone_main([str(manifest), "--output", str(output), "--repos-dir", str(tmp_path / "repos")])

    # One checkpoint write per repository (growing row counts), plus the
    # final write -- not a single write at the very end.
    assert write_calls == [1, 2, 2]


def test_classify_skip_existing_does_not_reclassify(tmp_path, monkeypatch):
    repository = tmp_path / "repository"
    sha = _create_repository(repository)
    frozen = tmp_path / "frozen.csv"
    with frozen.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=["project", "status", "commit_sha", "repository_path"]
        )
        writer.writeheader()
        writer.writerow({
            "project": "org/example", "status": "collected",
            "commit_sha": sha, "repository_path": str(repository),
        })

    output_dir = tmp_path / "classifications"
    output_dir.mkdir()
    manifest_path(output_dir, "org/example", sha).write_text(
        "path,file_class,document_type,loc,included\n", encoding="utf-8"
    )

    import scripts.classify_study_files as mod

    def fail_if_called(row, output_dir):
        raise AssertionError("should not reclassify an already-classified project")

    monkeypatch.setattr(mod, "generate_for_row", fail_if_called)

    classify_main([str(frozen), "--output-dir", str(output_dir), "--skip-existing"])


def test_classify_continues_past_one_failing_repository(tmp_path, monkeypatch):
    good_repo = tmp_path / "good"
    bad_repo = tmp_path / "bad"
    good_sha = _create_repository(good_repo)
    bad_sha = _create_repository(bad_repo)
    frozen = tmp_path / "frozen.csv"
    with frozen.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=["project", "status", "commit_sha", "repository_path"]
        )
        writer.writeheader()
        writer.writerow({
            "project": "org/bad", "status": "collected",
            "commit_sha": bad_sha, "repository_path": str(bad_repo),
        })
        writer.writerow({
            "project": "org/good", "status": "collected",
            "commit_sha": good_sha, "repository_path": str(good_repo),
        })

    output_dir = tmp_path / "classifications"

    import scripts.classify_study_files as mod
    real_generate_for_row = mod.generate_for_row

    def flaky_generate_for_row(row, output_dir):
        if row["project"] == "org/bad":
            raise RuntimeError("simulated classification crash")
        return real_generate_for_row(row, output_dir)

    monkeypatch.setattr(mod, "generate_for_row", flaky_generate_for_row)

    with pytest.raises(SystemExit):
        classify_main([str(frozen), "--output-dir", str(output_dir)])

    assert mod.manifest_path(output_dir, "org/good", good_sha).is_file()
    assert not mod.manifest_path(output_dir, "org/bad", bad_sha).is_file()
