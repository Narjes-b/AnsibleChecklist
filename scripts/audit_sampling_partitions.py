#!/usr/bin/env python3
"""Inventory sampling partitions without selecting examples or reading source.

The current development population is not certified as independent evaluation
data. Exposure labels refer only to the explicitly supplied sample files.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


def read_csv(path):
    with Path(path).open(newline="", encoding="utf-8") as source:
        yield from csv.DictReader(source)


def indexed(rows, key):
    result = {}
    for row in rows:
        if row[key] in result:
            raise ValueError(f"duplicate {key}: {row[key]}")
        result[row[key]] = row
    return result


def audit_partitions(occurrences, splits, statuses, exposures, rules):
    repositories = {}
    for project, row in sorted(statuses.items()):
        split = splits.get(project, {})
        if split and split["commit_sha"] != row["commit_sha"]:
            raise ValueError(f"split/source revision mismatch: {project}")
        core_complete = row["ansibleguard_status"] == "completed"
        if core_complete and not split:
            raise ValueError(f"complete repository absent from split: {project}")
        repositories[project] = {
            "repository": project,
            "commit_sha": row["commit_sha"],
            "split": split.get("split", "not-assigned"),
            "size_quartile": split.get("size_quartile", "unknown"),
            "overall_status": row["overall_status"],
            "core_complete": core_complete,
            "provider_complete": row["overall_status"] == "complete",
            "exposure_status": "listed-example-present" if project in exposures else "not-in-listed-samples",
            "listed_sample_rows": exposures.get(project, 0),
            "eligible_for_performance_scoring": False,
            "occurrences": 0 if core_complete else "",
        }
    if splits.keys() - repositories.keys():
        raise ValueError("split contains repositories absent from execution status")

    cells = {}
    margins = {}
    rule_totals = {}
    seen = set()
    run_ids = set()
    for row in occurrences:
        project = row["project"]
        if project not in repositories:
            raise ValueError(f"occurrence repository absent from execution status: {project}")
        repo = repositories[project]
        if row["commit_sha"] != repo["commit_sha"] or not repo["core_complete"]:
            raise ValueError(f"occurrence not from a completed frozen snapshot: {project}")
        identity = (row["run_id"], project, row["commit_sha"], row["occurrence_id"])
        if identity in seen:
            raise ValueError(f"duplicate occurrence identity: {identity}")
        if row["provider"] != "ansibleguard" or row["scan_mode"] == "review":
            raise ValueError("frame requires internally assigned static-source occurrences")
        seen.add(identity)
        run_ids.add(row["run_id"])
        repo["occurrences"] += 1
        rule = row["rule_id"]
        if rule not in rules:
            raise ValueError(f"rule absent from profile: {rule}")
        cell_key = (repo["split"], rule, row["policy"], row["certainty"],
                    row["resolution_status"], row["resolution_scope"])
        cell = cells.setdefault(cell_key, {"occurrences": 0, "repositories": set()})
        cell["occurrences"] += 1
        cell["repositories"].add(project)
        margin_key = (repo["split"], repo["exposure_status"], repo["size_quartile"],
                      repo["provider_complete"], row["policy"], row["certainty"])
        margin = margins.setdefault(margin_key, {"occurrences": 0, "repositories": set()})
        margin["occurrences"] += 1
        margin["repositories"].add(project)
        rule_key = (repo["split"], rule)
        totals = rule_totals.setdefault(rule_key, {
            "required": 0, "optional": 0, "required_repositories": set(),
        })
        if row["policy"] not in {"required", "optional"}:
            raise ValueError(f"unknown policy: {row['policy']}")
        totals[row["policy"]] += 1
        if row["policy"] == "required":
            totals["required_repositories"].add(project)
    if len(run_ids) != 1 or not next(iter(run_ids)):
        raise ValueError("frame must contain exactly one nonempty run")

    cell_rows = []
    for key, data in sorted(cells.items()):
        split, rule, policy, certainty, resolution, scope = key
        cell_rows.append({
            "split": split, "rule_id": rule,
            "family": rules.get(rule, {}).get("family", "unmapped"),
            "taxonomy": rules.get(rule, {}).get("taxonomy", "unmapped"),
            "policy": policy, "certainty": certainty,
            "resolution_status": resolution, "resolution_scope": scope,
            "occurrences": data["occurrences"], "repositories": len(data["repositories"]),
            "eligible_for_performance_scoring": False,
        })
    margin_rows = []
    for key, data in sorted(margins.items()):
        split, exposure, size, providers, policy, certainty = key
        margin_rows.append({
            "split": split, "exposure_status": exposure, "size_quartile": size,
            "provider_complete": providers, "policy": policy, "certainty": certainty,
            "occurrences": data["occurrences"], "repositories": len(data["repositories"]),
        })
    feasibility = []
    for (split, rule), data in sorted(rule_totals.items()):
        n, clusters = data["required"], len(data["required_repositories"])
        feasibility.append({
            "split": split, "rule_id": rule, "required_occurrences": n,
            "optional_occurrences": data["optional"], "required_repositories": clusters,
            "has_20_occurrences_and_8_repositories": n >= 20 and clusters >= 8,
            "required_census_if_at_most_30": 0 < n <= 30,
            "note": "Availability screen only; not a sample-size or interval guarantee.",
        })
    return {
        "run_id": next(iter(run_ids)),
        "repository-frame.csv": list(repositories.values()),
        "sampling-cells.csv": cell_rows,
        "partition-margins.csv": margin_rows,
        "rule-feasibility.csv": feasibility,
    }


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--occurrences", required=True, type=Path)
    parser.add_argument("--repository-status", required=True, type=Path)
    parser.add_argument("--split", type=Path, default=Path("study/validation-v007-human/splits/repository-split.csv"))
    parser.add_argument("--rule-profile", type=Path, default=Path("study/analysis-v0071-rerun-2026-10-22/rule-profile.csv"))
    parser.add_argument("--exposure-samples", type=Path, nargs="+", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    exposures = Counter()
    for sample in args.exposure_samples:
        for row in read_csv(sample):
            exposures[row["repository"]] += 1
    result = audit_partitions(
        read_csv(args.occurrences), indexed(read_csv(args.split), "repository"),
        indexed(read_csv(args.repository_status), "repository"), exposures,
        indexed(read_csv(args.rule_profile), "rule_id"),
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, rows in result.items():
        if not name.endswith(".csv"):
            continue
        with (args.output_dir / name).open("w", newline="", encoding="utf-8") as target:
            writer = csv.DictWriter(target, fieldnames=list(rows[0]) if rows else [], lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
    inputs = [args.occurrences, args.repository_status, args.split, args.rule_profile, *args.exposure_samples]
    manifest = {
        "schema_version": 1, "run_id": result["run_id"],
        "population_view": "canonical-provider-assigned internal static-source occurrences",
        "purpose": "sampling frame inventory; no examples selected",
        "eligible_for_performance_scoring": False,
        "exposure_scope": "Only the listed samples were joined; absence does not establish independence.",
        "input_sha256": {str(path): sha256(path) for path in inputs},
        "output_sha256": {name: sha256(args.output_dir / name) for name in result if name.endswith(".csv")},
        "implementation_sha256": sha256(Path(__file__)),
        "occurrences": sum(row["occurrences"] for row in result["sampling-cells.csv"]),
        "sampling_cells": len(result["sampling-cells.csv"]),
    }
    (args.output_dir / "frame-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: manifest[key] for key in ("run_id", "occurrences", "sampling_cells")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
