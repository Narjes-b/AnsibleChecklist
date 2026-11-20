#!/usr/bin/env python3
"""Validate hashes, row counts, strata, and frozen-label boundaries."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path


LABEL_COLUMNS = (
    "reviewer_1_label", "reviewer_2_label", "adjudicated_label", "ai_label",
)
WORK_CONTENT_FIELDS = (
    "reviewer_1_label", "reviewer_1_reason", "reviewer_2_label",
    "reviewer_2_reason", "initial_agreement", "adjudicated_label",
    "adjudication_reason", "ai_label", "ai_reason", "ai_prompt_version",
    "ai_model_version",
)


def _rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _check_hashes(base: Path, manifest: dict) -> int:
    checked = 0
    for name, expected in manifest.get("artifacts", {}).items():
        path = base / name
        assert path.is_file(), f"missing hashed artifact: {path}"
        assert _sha256(path) == expected, f"hash mismatch: {path}"
        checked += 1
    return checked


def _check_sample(path: Path, expected_rows: int) -> list[dict]:
    rows = _rows(path)
    assert len(rows) == expected_rows, f"row-count mismatch: {path}"
    observation_ids = [row["observation_id"] for row in rows]
    strata = [row["sample_stratum"] for row in rows]
    assert len(observation_ids) == len(set(observation_ids)), f"duplicate observation: {path}"
    assert len(strata) == len(set(strata)), f"duplicate stratum: {path}"
    assert all(row.get("source_context", "").strip() for row in rows), f"missing context: {path}"
    assert all(row.get("context_strategy", "").strip() for row in rows), f"missing context strategy: {path}"
    assert all(int(row.get("source_total_lines") or 0) > 0 for row in rows), f"missing source size: {path}"
    assert all(
        abs(float(row["inclusion_probability"]) * float(row["sampling_weight"]) - 1) < 1e-6
        for row in rows
    ), f"invalid sampling weight: {path}"
    assert all(not row.get(column, "").strip() for row in rows for column in LABEL_COLUMNS), (
        f"frozen sample contains labels: {path}"
    )
    return rows


def _check_blank_working_copy(frozen: Path, working: Path) -> None:
    """A blank working template should track its current frozen source exactly."""
    assert working.is_file(), f"missing working review file: {working}"
    rows = _rows(working)
    has_content = any(
        str(row.get(column, "")).strip()
        for row in rows
        for column in WORK_CONTENT_FIELDS
    )
    if not has_content:
        assert working.read_bytes() == frozen.read_bytes(), f"stale blank template: {working}"


def _check_observations(path: Path, expected_rows: int) -> int:
    """Stream the population once and reject duplicate observation identities."""
    previous_id = None
    rows = 0
    with gzip.open(path, mode="rt", newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            observation_id = row["observation_id"]
            # The benchmark writer sorts by metric/project/path/line/id, and an
            # identical identity necessarily shares those preceding keys.
            assert observation_id != previous_id, f"duplicate population observation: {observation_id}"
            previous_id = observation_id
            rows += 1
    assert rows == expected_rows, f"observation-count mismatch: expected {expected_rows}, found {rows}"
    return rows


def validate(root: Path) -> dict:
    benchmark = json.loads((root / "benchmark-manifest.json").read_text(encoding="utf-8"))
    hash_count = _check_hashes(root, benchmark)
    distributions = _rows(root / "distribution-summary.csv")
    sensitivities = _rows(root / "candidate-sensitivity.csv")
    metric_ids = {row["metric_id"] for row in distributions}
    assert len(metric_ids) == 24, f"expected 24 metrics, found {len(metric_ids)}"
    assert metric_ids == {row["metric_id"] for row in sensitivities}
    assert not _rows(root / "scan-failures.csv"), "scan failures are not empty"
    observation_rows = _check_observations(
        root / "observations.csv.gz", int(benchmark["observation_count"]),
    )

    large_rows = _check_sample(
        root / "large-task-review-sample.csv",
        int(benchmark["large_task_review_sample_count"]),
    )
    _check_blank_working_copy(
        root / "large-task-review-sample.csv", root / "large-task-review-labels.csv",
    )
    large_pilot_manifest = json.loads(
        (root / "large-task-agreement-pilot-manifest.json").read_text(encoding="utf-8")
    )
    assert _sha256(root / "large-task-agreement-pilot.csv") == large_pilot_manifest["pilot_sha256"]
    assert len(_rows(root / "large-task-agreement-pilot.csv")) == 75
    _check_blank_working_copy(
        root / "large-task-agreement-pilot.csv",
        root / "large-task-agreement-pilot-labels.csv",
    )

    study_count = 1
    primary_rows = len(large_rows)
    pilot_rows = 75
    for directory in sorted(path for path in root.iterdir() if path.is_dir()):
        sample_manifest_path = directory / "sample-manifest.json"
        if not sample_manifest_path.exists():
            continue
        sample_manifest = json.loads(sample_manifest_path.read_text(encoding="utf-8"))
        hash_count += _check_hashes(directory, sample_manifest)
        rows = _check_sample(directory / "review-sample.csv", int(sample_manifest["sample_rows"]))
        _check_blank_working_copy(directory / "review-sample.csv", directory / "review-labels.csv")
        assert _sha256(directory / "review-sample.csv") == sample_manifest["review_sample_sha256"]
        pilot_manifest = json.loads(
            (directory / "agreement-pilot-manifest.json").read_text(encoding="utf-8")
        )
        assert _sha256(directory / "agreement-pilot.csv") == pilot_manifest["pilot_sha256"]
        assert len(_rows(directory / "agreement-pilot.csv")) == 75
        _check_blank_working_copy(
            directory / "agreement-pilot.csv", directory / "agreement-pilot-labels.csv",
        )
        study_count += 1
        primary_rows += len(rows)
        pilot_rows += 75

    assert study_count == 24, f"expected 24 study packets, found {study_count}"
    assert pilot_rows == 1800, f"expected 1,800 pilot rows, found {pilot_rows}"
    return {
        "status": "valid",
        "metrics": len(metric_ids),
        "study_packets": study_count,
        "primary_sample_rows": primary_rows,
        "population_observation_rows": observation_rows,
        "agreement_pilot_rows": pilot_rows,
        "hashed_artifacts_checked": hash_count,
        "scan_failures": 0,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="study/threshold-benchmark-v007")
    args = parser.parse_args(argv)
    print(json.dumps(validate(Path(args.root)), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
