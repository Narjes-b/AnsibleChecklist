import csv
import json

from scripts.compare_validation_versions import (
    compare_roots,
    compare_version_occurrences,
    write_outputs,
)


def _snapshot(root, project, sha, items):
    path = root / project.replace("/", "__") / sha / "canonical" / "occurrences.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({"items": items}), encoding="utf-8")


def _scope(root, project, sha, scope):
    path = root / project.replace("/", "__") / sha / "run_metadata.json"
    path.write_text(json.dumps({
        "analysis_scope": {"ansible_lint": {"scope": scope}}
    }), encoding="utf-8")


def _occurrence(identifier, concept, file="tasks/main.yml", message="message"):
    return {
        "occurrence_id": identifier,
        "semantic_key": identifier,
        "concept_id": concept,
        "file": file,
        "line": 4,
        "severity": "warning",
        "confidence": "low",
        "message": message,
        "native_rules": [f"ansibleguard/{concept}"],
        "evidence_fingerprints": [],
    }


def test_paired_comparison_writes_review_queue_and_preserves_old_label(tmp_path):
    project = "example/role"
    sha = "a" * 40
    manifest = tmp_path / "manifest.csv"
    manifest.write_text(f"project,commit_sha\n{project},{sha}\n", encoding="utf-8")
    labels = tmp_path / "labels.csv"
    labels.write_text(
        "project,occurrence_id,consensus_label,consensus_reason\n"
        f"{project},old,false-positive,dispatcher\n",
        encoding="utf-8",
    )
    base_root = tmp_path / "base"
    head_root = tmp_path / "head"
    _snapshot(base_root, project, sha, [
        _occurrence("same", "stable-rule"),
        _occurrence("old", "high-coupling", message="old coupling"),
    ])
    _snapshot(head_root, project, sha, [
        _occurrence("same", "stable-rule"),
        _occurrence("new", "new-rule", message="new finding"),
    ])

    rows, repositories = compare_roots(manifest, base_root, head_root, labels)
    summary = write_outputs(rows, repositories, tmp_path / "out")

    assert summary["repositories_compared"] == 1
    assert summary["pair_status_counts"] == {
        "fixed": 1, "introduced": 1, "unchanged": 1
    }
    fixed = next(row for row in rows if row["status"] == "fixed")
    assert fixed["old_consensus_label"] == "false-positive"
    with (tmp_path / "out" / "paired-review-queue.csv").open(newline="") as stream:
        review = list(csv.DictReader(stream))
    assert {row["status"] for row in review} == {"fixed", "introduced"}


def test_missing_head_snapshot_is_reported_not_compared(tmp_path):
    project = "example/role"
    sha = "b" * 40
    manifest = tmp_path / "manifest.csv"
    manifest.write_text(f"project,commit_sha\n{project},{sha}\n", encoding="utf-8")
    _snapshot(tmp_path / "base", project, sha, [])

    rows, repositories = compare_roots(manifest, tmp_path / "base", tmp_path / "head")

    assert rows == []
    assert repositories[0]["status"] == "missing-head"


def test_semantic_version_match_handles_changed_occurrence_identity():
    base = _occurrence("base-id", "rule")
    head = {**base, "occurrence_id": "head-id"}

    comparison = compare_version_occurrences([base], [head])

    assert comparison["moved"][0]["match"] == "semantic"
    assert comparison["introduced"] == []
    assert comparison["fixed"] == []


def test_location_match_preserves_base_and_head_labels():
    base = _occurrence("base-id", "rule", message="old")
    head = {**base, "occurrence_id": "head-id", "semantic_key": "different", "message": "new"}
    comparison = compare_version_occurrences([base], [head])
    assert comparison["location"][0]["base"]["occurrence_id"] == "base-id"
    assert comparison["location"][0]["head"]["occurrence_id"] == "head-id"


def test_mismatched_ansible_lint_populations_are_excluded_not_called_changes(
    tmp_path,
):
    project = "example/role"
    sha = "c" * 40
    manifest = tmp_path / "manifest.csv"
    manifest.write_text(f"project,commit_sha\n{project},{sha}\n", encoding="utf-8")
    base_root = tmp_path / "base"
    head_root = tmp_path / "head"
    native = {
        **_occurrence("lint-old", "yaml-formatting"),
        "canonical_provider": "ansible-lint",
        "detectors": [{"provider": "ansible-lint"}],
    }
    _snapshot(base_root, project, sha, [native])
    _snapshot(head_root, project, sha, [
        {**native, "occurrence_id": "lint-new", "line": 8}
    ])
    _scope(base_root, project, sha, "requested-target")
    _scope(head_root, project, sha, "v005-selected")

    rows, repositories = compare_roots(manifest, base_root, head_root)

    assert rows == []
    assert repositories[0]["provider_scope_status"] == (
        "ansible-lint-excluded-scope-mismatch"
    )
    assert repositories[0]["excluded_noncomparable_provider_occurrences"] == 2
