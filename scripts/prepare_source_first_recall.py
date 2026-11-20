#!/usr/bin/env python3
"""Sample source files before running AnsibleGuard for natural-recall review."""

from __future__ import annotations

import argparse
import csv
import hashlib
import random
from pathlib import Path


FIELDS = (
    "review_unit_id", "project", "commit_sha", "path", "document_type",
    "ansible_artifact_kind", "loc", "reviewer_1_defect_present",
    "reviewer_1_concept_id", "reviewer_1_line", "reviewer_1_reason",
    "reviewer_2_defect_present", "reviewer_2_concept_id", "reviewer_2_line",
    "reviewer_2_reason", "adjudicated_defect_present", "adjudicated_concept_id",
    "adjudicated_line", "adjudicated_reason", "reference_set_frozen",
    "ansibleguard_occurrence_id", "recall_outcome",
)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository-manifest", type=Path, required=True)
    parser.add_argument("--file-manifests-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--files-per-repository", type=int, default=3)
    parser.add_argument("--seed", type=int, default=404)
    args = parser.parse_args(argv)

    with args.repository_manifest.open(newline="", encoding="utf-8") as stream:
        repositories = list(csv.DictReader(stream))
    rng = random.Random(args.seed)
    rows = []
    for repository in repositories:
        project = repository["project"]
        commit = repository["commit_sha"]
        manifest = args.file_manifests_dir / (
            project.replace("/", "__") + f"__{commit}.csv"
        )
        if not manifest.is_file():
            continue
        with manifest.open(newline="", encoding="utf-8") as stream:
            candidates = [
                row for row in csv.DictReader(stream)
                if str(row.get("included", "")).lower() == "true"
            ]
        # Selection depends only on the frozen source manifest, never findings.
        rng.shuffle(candidates)
        selected = candidates[: args.files_per_repository]
        for source in selected:
            identity = f"{project}|{commit}|{source.get('path', '')}"
            rows.append(
                {
                    "review_unit_id": hashlib.sha256(identity.encode()).hexdigest(),
                    "project": project,
                    "commit_sha": commit,
                    "path": source.get("path", ""),
                    "document_type": source.get("document_type", ""),
                    "ansible_artifact_kind": source.get("ansible_artifact_kind", ""),
                    "loc": source.get("loc", ""),
                    **{field: "" for field in FIELDS[7:]},
                }
            )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
