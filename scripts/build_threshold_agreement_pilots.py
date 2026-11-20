#!/usr/bin/env python3
"""Build balanced, frozen agreement pilots from threshold primary samples."""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import hashlib
import json
from pathlib import Path

try:
    from scripts.build_threshold_benchmark import SEED, _review_file_has_content, _write_csv
    from scripts.materialize_all_threshold_studies import STUDIES
except ModuleNotFoundError:
    from build_threshold_benchmark import SEED, _review_file_has_content, _write_csv
    from materialize_all_threshold_studies import STUDIES


def _rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def _balanced_pilot(rows: list[dict], metric_id: str, size: int) -> list[dict]:
    bands = defaultdict(list)
    for row in rows:
        rank = hashlib.sha256(
            f"{SEED}\0agreement-pilot\0{metric_id}\0{row['observation_id']}".encode()
        ).hexdigest()
        group = f"{row['metric_band']}|current={row.get('current_prediction', '')}"
        bands[group].append((rank, row))
    ordered = {
        band: [row for _, row in sorted(items)]
        for band, items in bands.items()
    }
    selected = []
    band_names = sorted(ordered)
    position = 0
    while len(selected) < min(size, len(rows)):
        added = False
        for band in band_names:
            if position < len(ordered[band]):
                selected.append(dict(ordered[band][position]))
                added = True
                if len(selected) == min(size, len(rows)):
                    break
        if not added:
            break
        position += 1
    return selected


def _write_pilot(directory: Path, metric_id: str, source_name: str, prefix: str, size: int):
    source = directory / source_name
    rows = _rows(source)
    pilot = _balanced_pilot(rows, metric_id, size)
    fields = list(rows[0])
    frozen = directory / f"{prefix}agreement-pilot.csv"
    working = directory / f"{prefix}agreement-pilot-labels.csv"
    _write_csv(frozen, pilot, fields)
    if not _review_file_has_content(working):
        _write_csv(working, pilot, fields)
    status = {
        "paired_items": 0,
        "agreements": 0,
        "disagreements": 0,
        "raw_agreement": None,
        "cohens_kappa": None,
        "gwet_ac1": None,
        "label_prevalence": {},
        "label_specific_agreement": {},
        "confusion_matrix": {},
        "target": 0.8,
        "minimum_paired": 50,
        "status": "insufficient-independent-labels",
    }
    status_path = directory / f"{prefix}agreement-pilot-status.json"
    if not status_path.exists() or json.loads(status_path.read_text(encoding="utf-8")).get("paired_items") == 0:
        status_path.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest = {
        "schema_version": 1,
        "seed": SEED,
        "metric_id": metric_id,
        "source_sample": source_name,
        "source_rows": len(rows),
        "pilot_rows": len(pilot),
        "pilot_projects": len({row["project"] for row in pilot}),
        "pilot_band_counts": {
            band: sum(row["metric_band"] == band for row in pilot)
            for band in sorted({row["metric_band"] for row in pilot})
        },
        "pilot_prediction_counts": {
            prediction: sum(row["current_prediction"] == prediction for row in pilot)
            for prediction in ("false", "true")
        },
        "pilot_sha256": hashlib.sha256(frozen.read_bytes()).hexdigest(),
        "working_labels_are_mutable": True,
    }
    (directory / f"{prefix}agreement-pilot-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"{metric_id}: pilot={len(pilot)} projects={manifest['pilot_projects']}")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="study/threshold-benchmark-v007")
    parser.add_argument("--size", type=int, default=75)
    args = parser.parse_args(argv)
    root = Path(args.root)
    _write_pilot(root, "large_task_loc", "large-task-review-sample.csv", "large-task-", args.size)
    _write_pilot(
        root / "missing-abstraction", "missing_abstraction_leaf_tasks",
        "review-sample.csv", "", args.size,
    )
    for metric_id, config in STUDIES.items():
        _write_pilot(root / config["slug"], metric_id, "review-sample.csv", "", args.size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
