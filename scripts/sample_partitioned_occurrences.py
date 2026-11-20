#!/usr/bin/env python3
"""Draw a calibration-only, two-stage probability sample from a verified frame.

Selection uses metadata, never source availability or reviewer/model labels.
The private ledger records every selected ID and both selection probabilities.
Repository identity is the default cluster; reviewed multi-repository groups
can be supplied explicitly. This command cannot certify final evaluation data.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import platform
import random

try:
    from scripts.audit_sampling_partitions import indexed, read_csv, sha256
except ModuleNotFoundError:  # direct script execution
    from audit_sampling_partitions import indexed, read_csv, sha256


CELL_FIELDS = ("rule_id", "policy", "certainty", "resolution_status", "resolution_scope")
INSTRUMENTS = ("required", "uncertainty", "optional-policy")


def stable_digest(*parts):
    return hashlib.sha256(json.dumps(parts, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()


def choose_groups(group_ids, count, seed, stratum_id):
    """SRS without replacement; sorting makes input ordering irrelevant."""
    population = sorted(group_ids)
    return sorted(random.Random(int(stable_digest(seed, "groups", stratum_id), 16)).sample(population, count))


@dataclass(frozen=True)
class Design:
    groups_per_stratum: int = 3
    occurrences_per_group: int = 2
    census_at: int = 30

    def __post_init__(self):
        if any(type(value) is not int for value in vars(self).values()):
            raise ValueError("design quotas and cutoff must be integers")
        if self.groups_per_stratum < 1 or self.occurrences_per_group < 1 or self.census_at < 0:
            raise ValueError("group quotas must be positive and census cutoff nonnegative")


@dataclass
class Stratum:
    cell: tuple[str, ...]
    size_quartile: str
    groups: dict[str, list[dict]]
    selected_groups: int
    quota: int
    census: bool

    @property
    def identity(self):
        return stable_digest(self.cell, self.size_quartile)

    @property
    def population(self):
        return sum(len(units) for units in self.groups.values())

    def draw_size(self, group):
        return len(self.groups[group]) if self.census else min(self.quota, len(self.groups[group]))


def in_instrument(row, instrument):
    if instrument == "required":
        return row["policy"] == "required"
    if instrument == "uncertainty":
        return row["policy"] == "optional" and row["certainty"] == "UNCERTAIN"
    return row["policy"] == "optional" and row["certainty"] != "UNCERTAIN"


def build_strata(occurrences, repositories, run_id, instrument, design, group_map=None):
    if instrument not in INSTRUMENTS:
        raise ValueError(f"unsupported instrument: {instrument}")
    if group_map is not None and repositories.keys() - group_map.keys():
        raise ValueError("reviewed group map must cover every frame repository")
    mapping = group_map if group_map is not None else {name: name for name in repositories}
    group_partitions = {}
    group_sizes = {}
    for name, repo in repositories.items():
        group = mapping[name]
        if not group:
            raise ValueError("empty repository group")
        partition = repo["split"]
        if group in group_partitions and group_partitions[group] != partition:
            raise ValueError(f"repository group crosses dataset partitions: {group}")
        group_partitions[group] = partition
        if repo["core_complete"].lower() == "true":
            size = repo["size_quartile"]
            if size not in {"1", "2", "3", "4"}:
                raise ValueError(f"unknown size quartile: {name}")
            group_sizes[group] = max(group_sizes.get(group, "1"), size)

    cells = {}
    seen = set()
    for row in occurrences:
        project = row["project"]
        if project not in repositories:
            raise ValueError(f"unknown occurrence repository: {project}")
        repo = repositories[project]
        if row["run_id"] != run_id or row["commit_sha"] != repo["commit_sha"]:
            raise ValueError("occurrence source does not match frozen frame")
        if repo["core_complete"].lower() != "true":
            raise ValueError("occurrence from incomplete core scan")
        if row["provider"] != "ansibleguard" or row["scan_mode"] == "review":
            raise ValueError("expected internally assigned static-source occurrences")
        if row["policy"] not in {"required", "optional"}:
            raise ValueError("unknown occurrence policy")
        identity = (run_id, project, row["commit_sha"], row["occurrence_id"])
        if identity in seen:
            raise ValueError("duplicate occurrence in frame")
        seen.add(identity)
        # No --heldout override: this version only creates development draws.
        if repo["split"] != "calibration" or not in_instrument(row, instrument):
            continue
        cell = tuple(row[field] for field in CELL_FIELDS)
        group = mapping[project]
        unit = {
            "run_id": run_id, "repository": project, "commit_sha": row["commit_sha"],
            "occurrence_id": row["occurrence_id"], "file": row["file"], "line": row["line"],
            **{field: row[field] for field in CELL_FIELDS},
        }
        cells.setdefault(cell, {}).setdefault(group, []).append(unit)

    strata = []
    for cell, groups in sorted(cells.items()):
        census = sum(map(len, groups.values())) <= design.census_at
        bins = {}
        for group, units in sorted(groups.items()):
            units.sort(key=lambda row: (row["repository"], row["commit_sha"], row["occurrence_id"]))
            bins.setdefault(group_sizes[group], {})[group] = units
        # Keep sparse size bins explicit; all groups are selected when M < k.
        for size, members in sorted(bins.items()):
            strata.append(Stratum(cell, size, members,
                                  len(members) if census else min(design.groups_per_stratum, len(members)),
                                  design.occurrences_per_group, census))
    if not strata:
        raise ValueError("empty calibration instrument population")
    return strata


def sample_strata(strata, seed, instrument):
    selected = []
    plan = []
    for stratum in strata:
        groups = choose_groups(stratum.groups, stratum.selected_groups, seed, stratum.identity)
        first_probability = stratum.selected_groups / len(stratum.groups)
        expected = first_probability * sum(stratum.draw_size(group) for group in stratum.groups)
        plan.append({
            "stratum_id": stratum.identity, **dict(zip(CELL_FIELDS, stratum.cell)),
            "size_quartile": stratum.size_quartile, "population_occurrences": stratum.population,
            "population_groups": len(stratum.groups), "selected_groups": stratum.selected_groups,
            "within_group_quota": "all" if stratum.census else stratum.quota,
            "census_cell": stratum.census, "expected_selected_occurrences": expected,
        })
        for group in groups:
            units = stratum.groups[group]
            count = stratum.draw_size(group)
            rng = random.Random(int(stable_digest(seed, "occurrences", stratum.identity, group), 16))
            chosen = sorted(rng.sample(range(len(units)), count))
            second_probability = count / len(units)
            probability = first_probability * second_probability
            for index in chosen:
                unit = units[index]
                selected.append({
                    "sample_id": "PROB-" + stable_digest(instrument, unit["run_id"], unit["repository"],
                                                         unit["commit_sha"], unit["occurrence_id"]),
                    **unit, "dataset_role": "calibration", "instrument": instrument,
                    "stratum_id": stratum.identity, "size_quartile": stratum.size_quartile,
                    "repository_group": group, "group_population": len(units), "group_sample": count,
                    "stage1_probability": first_probability, "stage2_probability": second_probability,
                    "inclusion_probability": probability, "sampling_weight": 1 / probability,
                    "eligible_for_performance_scoring": False,
                    "retrieval_status": "pending", "label_status": "not-started",
                })
    return selected, plan


def load_verified_strata(frame_dir, occurrences_path, instrument, design, groups_path=None):
    manifest_path = frame_dir / "frame-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1 or manifest.get("population_view") != "canonical-provider-assigned internal static-source occurrences":
        raise ValueError("unsupported frame schema or population view")
    if manifest.get("eligible_for_performance_scoring") is not False:
        raise ValueError("this sampler requires an explicitly non-evaluation development frame")
    required = {"repository-frame.csv", "sampling-cells.csv", "partition-margins.csv", "rule-feasibility.csv"}
    if not required.issubset(manifest["output_sha256"]):
        raise ValueError("incomplete frame manifest")
    for name in required:
        if sha256(frame_dir / name) != manifest["output_sha256"][name]:
            raise ValueError(f"frame hash mismatch: {name}")
    hashes = [value for name, value in manifest["input_sha256"].items()
              if Path(name).name == "all-internal-source-occurrences.csv"]
    if len(hashes) != 1 or sha256(occurrences_path) != hashes[0]:
        raise ValueError("occurrence CSV does not match audited source hash")
    groups = None
    if groups_path:
        groups = {key: row["group_id"] for key, row in indexed(read_csv(groups_path), "repository").items()}
    strata = build_strata(read_csv(occurrences_path), indexed(read_csv(frame_dir / "repository-frame.csv"), "repository"),
                         manifest["run_id"], instrument, design, groups)
    return strata, manifest


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frame-dir", type=Path, required=True)
    parser.add_argument("--occurrences", type=Path, required=True)
    parser.add_argument("--instrument", choices=INSTRUMENTS, required=True)
    parser.add_argument("--groups-per-stratum", type=int, default=3)
    parser.add_argument("--occurrences-per-group", type=int, default=2)
    parser.add_argument("--census-at", type=int, default=30)
    parser.add_argument("--repository-groups", type=Path)
    parser.add_argument("--seed", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    design = Design(args.groups_per_stratum, args.occurrences_per_group, args.census_at)
    if args.output_dir.exists():
        parser.error("output directory exists; use a new draw directory")
    strata, frame = load_verified_strata(args.frame_dir, args.occurrences, args.instrument, design, args.repository_groups)
    selected, plan = sample_strata(strata, args.seed, args.instrument)
    args.output_dir.mkdir(parents=True)
    write_csv(args.output_dir / "selection-ledger.csv", selected)
    write_csv(args.output_dir / "sampling-plan.csv", plan)
    manifest = {
        "schema_version": 1, "purpose": "calibration-only probability draw; retrieval and labels pending",
        "eligible_for_performance_scoring": False, "run_id": frame["run_id"], "instrument": args.instrument,
        "prior_item_reuse": "not filtered; development draw, not a fresh agreement pilot",
        "seed": args.seed, "python_version": platform.python_version(),
        "design": vars(design), "frame_manifest_sha256": sha256(args.frame_dir / "frame-manifest.json"),
        "occurrences_sha256": sha256(args.occurrences), "implementation_sha256": sha256(Path(__file__)),
        "grouping": "explicit-map; review status not certified" if args.repository_groups else "repository-identity-only; shared-content independence unverified",
        "group_map_sha256": sha256(args.repository_groups) if args.repository_groups else None,
        "population_occurrences": sum(stratum.population for stratum in strata),
        "selected_occurrences": len(selected), "strata": len(strata),
        "expected_selected_occurrences": sum(row["expected_selected_occurrences"] for row in plan),
        "output_sha256": {name: sha256(args.output_dir / name) for name in ("selection-ledger.csv", "sampling-plan.csv")},
    }
    (args.output_dir / "selection-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: manifest[key] for key in ("population_occurrences", "selected_occurrences", "strata")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
