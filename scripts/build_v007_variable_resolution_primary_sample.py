#!/usr/bin/env python3
"""Freeze the primary v0.0.7 variable-resolution review samples."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


SEED = "v007-variable-resolution-primary-20260917"
RULE = "ansibleguard/unguarded-variable"
STATUSES = (
    "CANDIDATE_MISSING",
    "EXTERNAL_INPUT_UNCERTAIN",
    "RUNTIME_CONTEXT_UNCERTAIN",
)


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def stable_rank(*parts: str) -> str:
    return hashlib.sha256((SEED + "\0" + "\0".join(parts)).encode()).hexdigest()


def write_csv(path: Path, rows: list[dict], fields: list[str] | None = None) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty sample: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields or list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def capped_round_robin(rows: list[dict], total: int, cap: int) -> list[dict]:
    by_project: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_project[row["project"]].append(row)
    for project, values in by_project.items():
        values.sort(key=lambda row: stable_rank(project, row["occurrence_id"]))
        del values[cap:]
    projects = sorted(by_project, key=lambda project: stable_rank("project", project))
    selected = []
    depth = 0
    while len(selected) < total:
        added = False
        for project in projects:
            values = by_project[project]
            if depth < len(values):
                selected.append(values[depth])
                added = True
                if len(selected) == total:
                    break
        if not added:
            break
        depth += 1
    if len(selected) != total:
        raise ValueError(f"requested {total} rows but cap permits only {len(selected)}")
    return selected


def build_positive_sample(occurrences: list[dict], per_class: int) -> list[dict]:
    population_counts = Counter(
        row["resolution_status"] for row in occurrences if row["rule_id"] == RULE
    )
    selected = []
    for status in STATUSES:
        pool = [
            row for row in occurrences
            if row["rule_id"] == RULE and row["resolution_status"] == status
        ]
        cap = 5 if status == "CANDIDATE_MISSING" else 3
        chosen = capped_round_robin(pool, per_class, cap)
        project_population = len({row["project"] for row in pool})
        for row in chosen:
            selected.append({
                "sample_kind": "emitted-positive",
                "sampling_seed": SEED,
                "sampling_stratum": status,
                "stratum_population": population_counts[status],
                "stratum_sample_size": per_class,
                "naive_inclusion_probability": f"{per_class / population_counts[status]:.12g}",
                "repository_population": project_population,
                "repository_cap": cap,
                **row,
            })
    return selected


def build_source_first_sample(
    repository_rows: list[dict], occurrences: list[dict], total: int
) -> list[dict]:
    candidates = []
    for repo in repository_rows:
        manifest = Path(repo["classification_manifest"])
        for row in read_csv(manifest):
            if (
                row.get("included", "").lower() != "true"
                or row.get("file_class") != "production_ansible"
                or row.get("parse_status") != "parsed"
            ):
                continue
            candidates.append({
                "sample_kind": "source-first-recall",
                "sampling_seed": SEED,
                "project": repo["project"],
                "commit_sha": repo["commit_sha"],
                "repository_path": repo["repository_path"],
                "file": row["path"],
                "document_type": row.get("document_type", ""),
                "ansible_artifact_kind": row.get("ansible_artifact_kind", ""),
                "loc": row.get("loc", ""),
            })

    by_artifact: dict[str, list[dict]] = defaultdict(list)
    for row in candidates:
        by_artifact[row["ansible_artifact_kind"] or "unknown"].append(row)
    for artifact, values in by_artifact.items():
        values.sort(key=lambda row: stable_rank("source", artifact, row["project"], row["file"]))

    project_counts = Counter()
    selected = []
    artifacts = sorted(by_artifact, key=lambda item: stable_rank("artifact", item))
    positions = Counter()
    while len(selected) < total:
        added = False
        for artifact in artifacts:
            values = by_artifact[artifact]
            while positions[artifact] < len(values):
                row = values[positions[artifact]]
                positions[artifact] += 1
                if project_counts[row["project"]] >= 2:
                    continue
                project_counts[row["project"]] += 1
                selected.append(row)
                added = True
                break
            if len(selected) == total:
                break
        if not added:
            break
    if len(selected) != total:
        raise ValueError(f"requested {total} source files but selected {len(selected)}")
    population_by_artifact = Counter(row["ansible_artifact_kind"] or "unknown" for row in candidates)
    sample_by_artifact = Counter(row["ansible_artifact_kind"] or "unknown" for row in selected)
    for row in selected:
        artifact = row["ansible_artifact_kind"] or "unknown"
        row.update({
            "sampling_stratum": artifact,
            "stratum_population": population_by_artifact[artifact],
            "stratum_sample_size": sample_by_artifact[artifact],
            "naive_inclusion_probability": f"{sample_by_artifact[artifact] / population_by_artifact[artifact]:.12g}",
            "repository_cap": 2,
        })
    return selected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--occurrences", type=Path, required=True)
    parser.add_argument("--repositories", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--per-class", type=int, default=150)
    parser.add_argument("--source-first", type=int, default=150)
    args = parser.parse_args()

    occurrences = read_csv(args.occurrences)
    repositories = read_csv(args.repositories)
    positive = build_positive_sample(occurrences, args.per_class)
    source_first = build_source_first_sample(repositories, occurrences, args.source_first)
    write_csv(args.output_dir / "emitted-positive-sample.csv", positive)
    write_csv(args.output_dir / "source-first-sample.csv", source_first)

    hashes = {}
    for name, path in {
        "occurrence_population": args.occurrences,
        "repository_population": args.repositories,
        "emitted_positive_sample": args.output_dir / "emitted-positive-sample.csv",
        "source_first_sample": args.output_dir / "source-first-sample.csv",
    }.items():
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest = {
        "schema_version": 1,
        "sampling_seed": SEED,
        "emitted_positive_total": len(positive),
        "emitted_positive_per_resolution_class": args.per_class,
        "source_first_total": len(source_first),
        "repository_caps": {"emitted_positive": "3; 5 for CANDIDATE_MISSING", "source_first": 2},
        "hashes_sha256": hashes,
    }
    (args.output_dir / "sample-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
