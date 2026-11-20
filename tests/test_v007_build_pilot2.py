import csv
import json
import subprocess
import sys

import pytest

from scripts import v007_build_pilot2 as build


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.com", *args],
                          check=True, capture_output=True, text=True).stdout.strip()


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture
def world(tmp_path):
    clones = tmp_path / "clones"
    repo = clones / "o" / "r"
    repo.mkdir(parents=True)
    git(repo, "init", "-q")
    tasks = "\n".join(f"- name: step {i}\n  ansible.builtin.debug: {{msg: {i}}}" for i in range(12))
    (repo / "tasks").mkdir()
    (repo / "tasks/main.yml").write_text(tasks + "\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "Add tasks")
    sha = git(repo, "rev-parse", "HEAD")
    validation = tmp_path / "validation"
    write_csv(validation / "splits/repository-split.csv", [{"repository": "o/r", "commit_sha": sha, "split": "calibration"}])
    write_csv(validation / "mappings/rule-family-map.csv", [
        {"rule_id": "ansibleguard/missing-abstraction", "panel": "static", "family_id": "structure_reuse"},
        {"rule_id": "ansibleguard/commit-message-format", "panel": "review-history", "family_id": "review_history"}])
    run = tmp_path / "run"
    snapshot = run / "snap.json"
    snapshot.parent.mkdir(parents=True)
    snapshot.write_text(json.dumps([{"occurrence_id": "occ1", "file": "tasks/main.yml", "line": "1",
                                     "canonical_provider": "ansibleguard", "semantic_subject": "task: step 0"}]), encoding="utf-8")
    write_csv(run / "raw/raw-output-index.csv", [{"repository": "o/r", "canonical_occurrences": "snap.json"}])
    base = {"project": "o/r", "commit_sha": sha, "concept_id": "c", "policy": "required"}
    write_csv(run / "aggregate/all-internal-source-occurrences.csv", [
        {**base, "occurrence_id": "occ1", "rule_id": "ansibleguard/missing-abstraction", "file": "tasks/main.yml", "line": "1"},
        {**base, "occurrence_id": "occ2", "rule_id": "ansibleguard/missing-abstraction", "file": "tasks/main.yml", "line": "3", "policy": "optional"}])
    write_csv(run / "aggregate/all-review-occurrences.csv", [
        {**base, "occurrence_id": "rev1", "rule_id": "ansibleguard/commit-message-format", "file": ".", "line": "1"}])
    return clones, validation, run, sha


def test_candidates_use_required_calibration_occurrences_only(world):
    clones, validation, run, sha = world
    candidates, population, _ = build.load_candidates(run, validation, [clones])
    assert population == {"ansibleguard/missing-abstraction": 1, "ansibleguard/commit-message-format": 1}
    static = next(c for c in candidates if c["family_id"] == "structure_reuse")
    assert static["semantic_subject"] == "task: step 0" and static["object_kind"] == "task"
    review = next(c for c in candidates if c["family_id"] == "review_history")
    assert review["object_kind"] == "git_commit" and review["is_merge"] == "false" and review["_parent_sha"] == ""


def test_commit_mismatch_with_the_frozen_split_stops(world):
    clones, validation, run, _ = world
    rows = list(csv.DictReader(open(validation / "splits/repository-split.csv")))
    rows[0]["commit_sha"] = "0" * 40
    write_csv(validation / "splits/repository-split.csv", rows)
    with pytest.raises(RuntimeError, match="frozen split"):
        build.load_candidates(run, validation, [clones])


def test_end_to_end_writes_valid_bundles_and_blank_forms(world, tmp_path, monkeypatch):
    clones, validation, run, _ = world
    pilot1 = tmp_path / "pilot1.csv"
    write_csv(pilot1, [{"repository": "x/y", "rule_id": "r", "path": "p", "line_start": "1"}])
    out = tmp_path / "out"
    monkeypatch.setattr(sys, "argv", ["x", "--run-dir", str(run), "--validation-dir", str(validation), "--pilot1-master", str(pilot1),
                                      "--clone-root", str(clones), "--output-dir", str(out)])
    assert build.main() == 0
    manifest = json.loads((out / "pilot2-manifest.json").read_text())
    assert manifest["items"] == 2 and manifest["bundle_problems"] == 0
    forms = list(csv.DictReader(open(out / "reviewer-a/pilot2.csv")))
    assert len(forms) == 2 and all(row["semantic_label"] == "" for row in forms)
    assert all((out / row["context_bundle_path"]).is_file() for row in forms)
    monkeypatch.setattr(sys, "argv", ["x", "--run-dir", str(run), "--validation-dir", str(validation), "--pilot1-master", str(pilot1),
                                      "--clone-root", str(clones), "--output-dir", str(out)])
    with pytest.raises(SystemExit, match="refusing"):
        build.main()
