import csv
import gzip
import hashlib
import json

from scripts.audit_v007_threshold_source import audit_threshold_source


def _write_csv(path, columns, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _fixture(tmp_path, *, mismatch_commit=False, map_rule="ansibleguard/test-rule"):
    observations_path = tmp_path / "observations.csv.gz"
    observation_rows = [
        {
            "observation_id": f"o-{index}",
            "metric_id": "test_metric",
            "rule_id": "test-rule",
            "unit": "task",
            "project": project,
            "commit_sha": ("bad-commit" if mismatch_commit and project == "org/heldout" else f"commit-{index}"),
            "path": f"tasks/{index}.yml",
            "source_ordinal": str(index),
            "line": str(index),
            "value": "must not appear in audit output",
        }
        for index, project in enumerate(("org/calibration", "org/heldout", "encapsulate-xyz/cosmos-ansible"))
    ]
    with gzip.open(observations_path, "wt", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(observation_rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(observation_rows)

    split_path = tmp_path / "split.csv"
    _write_csv(
        split_path,
        ["repository", "split"],
        [
            {"repository": "org/calibration", "split": "calibration"},
            {"repository": "org/heldout", "split": "heldout"},
        ],
    )
    status_path = tmp_path / "run-status.csv"
    _write_csv(
        status_path,
        ["repository", "commit_sha", "overall_status", "scan_status"],
        [
            {"repository": "org/calibration", "commit_sha": "commit-0", "overall_status": "complete", "scan_status": "completed"},
            {"repository": "org/heldout", "commit_sha": "commit-1", "overall_status": "complete", "scan_status": "completed"},
            {"repository": "encapsulate-xyz/cosmos-ansible", "commit_sha": "commit-2", "overall_status": "failed", "scan_status": "timeout"},
        ],
    )
    map_path = tmp_path / "condition-map.csv"
    _write_csv(
        map_path,
        ["metric_id", "human_condition_id", "rule_id", "source_object_unit", "object_identity_fields"],
        [
            {
                "metric_id": "test_metric",
                "human_condition_id": "test-condition",
                "rule_id": map_rule,
                "source_object_unit": "task",
                "object_identity_fields": "project+commit_sha+path+unit+source_ordinal",
            }
        ],
    )
    manifest_path = tmp_path / "benchmark-manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "artifacts": {"observations.csv.gz": hashlib.sha256(observations_path.read_bytes()).hexdigest()},
                "observation_count": len(observation_rows),
                "repository_count": len(observation_rows),
                "candidate_thresholds": {"test_metric": [1, 2]},
            }
        ),
        encoding="utf-8",
    )
    return observations_path, manifest_path, split_path, status_path, map_path


def test_threshold_source_audit_passes_exact_commit_join_and_timeout_exclusion(tmp_path):
    paths = _fixture(tmp_path)

    report = audit_threshold_source(
        *paths,
        expected_calibration_repositories=1,
        expected_heldout_repositories=1,
    )

    assert report["passed"]
    assert report["counts"] == {
        "observations": 3,
        "metrics": 1,
        "human_condition_families": 1,
        "projects": 3,
        "frozen_split_repositories": 2,
        "calibration_repositories": 1,
        "heldout_repositories": 1,
        "out_of_split_projects": ["encapsulate-xyz/cosmos-ansible"],
        "commit_mismatches": 0,
        "missing_run_status": 0,
        "multi_commit_projects": 0,
    }
    serialized = json.dumps(report)
    assert "must not appear in audit output" not in serialized


def test_threshold_source_audit_fails_commit_mismatch(tmp_path):
    paths = _fixture(tmp_path, mismatch_commit=True)

    report = audit_threshold_source(
        *paths,
        expected_calibration_repositories=1,
        expected_heldout_repositories=1,
    )

    assert not report["passed"]
    assert report["counts"]["commit_mismatches"] == 1
    assert any("commit" in failure for failure in report["failures"])


def test_threshold_source_audit_fails_rule_mapping_mismatch(tmp_path):
    paths = _fixture(tmp_path, map_rule="ansibleguard/different-rule")

    report = audit_threshold_source(
        *paths,
        expected_calibration_repositories=1,
        expected_heldout_repositories=1,
    )

    assert not report["passed"]
    assert any("rule/unit" in failure for failure in report["failures"])
