#!/usr/bin/env python3
"""Freeze the V007 repository-level calibration/held-out split.

This script consumes only pre-human AnsibleGuard source summaries. It writes
repository assignments and balance reports; it does not select occurrences or
open held-out review samples.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics
from collections import Counter, defaultdict
from typing import Any


SPLIT_SEED = "v007-human-repo-split-20261005"
SOURCE_SHA256 = "7ea8943bf40a6b05f2e33c4140446757c45b6d218e81a75096591f046a81978b"
IDENTITY_SHA256 = "2b70672c1f89039386f6cfb4bb73460059f05014a6b7248e4865f951150c7d6b"
TOTAL_REPOSITORIES = 206
CALIBRATION_REPOSITORIES = 144
HELDOUT_REPOSITORIES = 62
TOP_RULE_COUNT = 15


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def split_rank(seed: str, repository: str) -> str:
    return hashlib.sha256(f"{seed}|{repository}".encode("utf-8")).hexdigest()


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def rank_quartiles(
    values: dict[str, float], seed: str
) -> dict[str, int]:
    """Assign deterministic equal-count rank quartiles; hash-break feature ties."""
    if not values:
        raise ValueError("cannot calculate quartiles for an empty population")
    ordered = sorted(
        values,
        key=lambda repository: (
            math.log1p(max(0.0, values[repository])),
            split_rank(seed, repository),
            repository,
        ),
    )
    count = len(ordered)
    return {
        repository: min(4, (index * 4) // count + 1)
        for index, repository in enumerate(ordered)
    }


def iterative_split(
    repository_tokens: dict[str, set[str]],
    seed: str,
    heldout_capacity: int,
) -> dict[str, str]:
    """Greedy multilabel iterative stratification with hard set capacities.

    At each step the rarest token among unassigned repositories is processed.
    Its candidates are considered by the prescribed SHA256 rank. Each candidate
    goes to the set with the larger mean normalized deficit over its tokens.
    A score tie is broken by the candidate's hash rank (first hex digit 0-4 ->
    held-out; 5-f -> calibration). Capacity is enforced for every assignment.
    """
    repositories = set(repository_tokens)
    total = len(repositories)
    calibration_capacity = total - heldout_capacity
    if not 0 < heldout_capacity < total:
        raise ValueError("held-out capacity must be between zero and population size")
    all_tokens = sorted({token for tokens in repository_tokens.values() for token in tokens})
    population_by_token = Counter(
        token for tokens in repository_tokens.values() for token in tokens
    )
    target_heldout = {
        token: round(0.30 * population_by_token[token]) for token in all_tokens
    }
    target_calibration = {
        token: population_by_token[token] - target_heldout[token]
        for token in all_tokens
    }
    assigned_by_token = {
        "heldout": Counter(),
        "calibration": Counter(),
    }
    assignment: dict[str, str] = {}
    unassigned = set(repositories)
    ranks = {repository: split_rank(seed, repository) for repository in repositories}

    def normalized_deficit(repository: str, split: str) -> float:
        token_set = repository_tokens[repository]
        targets = target_heldout if split == "heldout" else target_calibration
        current = assigned_by_token[split]
        scores = [
            (targets[token] - current[token]) / max(1, targets[token])
            for token in token_set
        ]
        return sum(scores) / len(scores) if scores else 0.0

    while unassigned:
        remaining_by_token = {
            token: sum(token in repository_tokens[repository] for repository in unassigned)
            for token in all_tokens
        }
        active = [(count, token) for token, count in remaining_by_token.items() if count]
        if not active:
            raise RuntimeError("unassigned repositories remain without balancing tokens")
        _remaining_count, rarest_token = min(active, key=lambda pair: (pair[0], pair[1]))
        candidates = sorted(
            (
                repository
                for repository in unassigned
                if rarest_token in repository_tokens[repository]
            ),
            key=lambda repository: (ranks[repository], repository),
        )
        for repository in candidates:
            eligible = []
            if sum(value == "heldout" for value in assignment.values()) < heldout_capacity:
                eligible.append("heldout")
            if sum(value == "calibration" for value in assignment.values()) < calibration_capacity:
                eligible.append("calibration")
            scores = {side: normalized_deficit(repository, side) for side in eligible}
            best_score = max(scores.values())
            best_sides = [side for side, score in scores.items() if score == best_score]
            if len(best_sides) == 1:
                chosen = best_sides[0]
            else:
                chosen = "heldout" if int(ranks[repository][0], 16) < 5 else "calibration"
                if chosen not in best_sides:
                    chosen = best_sides[0]
            assignment[repository] = chosen
            unassigned.remove(repository)
            for token in repository_tokens[repository]:
                assigned_by_token[chosen][token] += 1

    counts = Counter(assignment.values())
    if counts != {"calibration": calibration_capacity, "heldout": heldout_capacity}:
        raise RuntimeError(f"hard capacities were not met: {dict(counts)}")
    return assignment


def _pct(numerator: int, denominator: int) -> float:
    return round(numerator * 100 / denominator, 4) if denominator else 0.0


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"refusing to write empty CSV: {path}")
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build_split(root: Path, output_dir: Path) -> dict:
    run_dir = root / "study/runs/v007-full-repro-2026"
    source_path = run_dir / "aggregate/all-internal-source-occurrences.csv"
    identity_manifest_path = (
        root / "study/validation-v007-human/identities/static-source-candidates.manifest.json"
    )
    if sha256_file(source_path) != SOURCE_SHA256:
        raise RuntimeError("authoritative internal-source CSV SHA changed; stop and investigate")
    identity_manifest = json.loads(identity_manifest_path.read_text(encoding="utf-8"))
    if identity_manifest.get("candidate_file_sha256") != IDENTITY_SHA256:
        raise RuntimeError("namespaced identity table changed; stop and investigate")

    execution = {
        row["repository"]: row
        for row in _read_csv(run_dir / "tables/repository-execution-status.csv")
    }
    analyzable = {
        repository
        for repository, row in execution.items()
        if row.get("ansibleguard_status") == "completed"
    }
    if len(analyzable) != TOTAL_REPOSITORIES:
        raise RuntimeError(f"expected 206 analyzable repositories, found {len(analyzable)}")

    summaries = {
        row["project"]: row
        for row in _read_csv(run_dir / "aggregate/repository-summary.csv")
        if row.get("project") != "__ALL__"
    }
    if not analyzable <= summaries.keys():
        raise RuntimeError("one or more analyzable repositories lack aggregate summaries")
    source_counts: Counter[str] = Counter()
    rule_counts: Counter[str] = Counter()
    rule_repositories: dict[str, set[str]] = defaultdict(set)
    with source_path.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            if row.get("provider") != "ansibleguard" or row.get("source_population") != "production_ansible":
                raise RuntimeError("unexpected row in source population during split construction")
            source_counts[row["project"]] += 1
            rule_counts[row["rule_id"]] += 1
            rule_repositories[row["rule_id"]].add(row["project"])
    top_rules = [
        rule
        for rule, _count in sorted(rule_counts.items(), key=lambda item: (-item[1], item[0]))[:TOP_RULE_COUNT]
    ]

    features: dict[str, dict[str, Any]] = {}
    selected_loc_values: dict[str, float] = {}
    density_values: dict[str, float] = {}
    for repository in sorted(analyzable):
        summary = summaries[repository]
        selected_loc = int(summary.get("selected_loc") or 0)
        selected_files = int(summary.get("selected_files") or 0)
        occurrences = source_counts[repository]
        density = occurrences / selected_loc if selected_loc else 0.0
        selected_loc_values[repository] = float(selected_loc)
        density_values[repository] = density
        features[repository] = {
            "repository": repository,
            "commit_sha": summary.get("commit_sha", ""),
            "selected_loc": selected_loc,
            "selected_files": selected_files,
            "internal_static_occurrences": occurrences,
            "internal_static_density": density,
        }
    if any(not row["commit_sha"] for row in features.values()):
        raise RuntimeError("analyzable repository missing frozen commit SHA")

    size_quartiles = rank_quartiles(selected_loc_values, SPLIT_SEED)
    density_quartiles = rank_quartiles(density_values, SPLIT_SEED)
    repository_tokens: dict[str, set[str]] = {}
    for repository, row in features.items():
        tokens = {
            f"SIZE_Q{size_quartiles[repository]}",
            f"DENSITY_Q{density_quartiles[repository]}",
        }
        tokens.update(
            f"RULE_PRESENT_{rule}"
            for rule in top_rules
            if repository in rule_repositories[rule]
        )
        repository_tokens[repository] = tokens

    assignment = iterative_split(repository_tokens, SPLIT_SEED, HELDOUT_REPOSITORIES)
    split_rows = []
    for repository in sorted(features):
        row = features[repository]
        split_rows.append({
            **row,
            "split": assignment[repository],
            "split_seed": SPLIT_SEED,
            "split_rank_sha256": split_rank(SPLIT_SEED, repository),
            "size_quartile": size_quartiles[repository],
            "density_quartile": density_quartiles[repository],
            "balancing_tokens": ";".join(sorted(repository_tokens[repository])),
        })

    split_counts = Counter(assignment.values())
    balance_rows = []
    for token in sorted({token for tokens in repository_tokens.values() for token in tokens}):
        members = [repo for repo, tokens in repository_tokens.items() if token in tokens]
        heldout_target = round(0.30 * len(members))
        heldout_actual = sum(assignment[repo] == "heldout" for repo in members)
        calibration_actual = len(members) - heldout_actual
        balance_rows.append({
            "token": token,
            "population_repositories": len(members),
            "target_heldout_repositories": heldout_target,
            "target_calibration_repositories": len(members) - heldout_target,
            "actual_heldout_repositories": heldout_actual,
            "actual_calibration_repositories": calibration_actual,
            "heldout_prevalence_percent": _pct(heldout_actual, split_counts["heldout"]),
            "calibration_prevalence_percent": _pct(calibration_actual, split_counts["calibration"]),
            "heldout_share_of_token_percent": _pct(heldout_actual, len(members)),
            "heldout_share_delta_from_30pp": round(_pct(heldout_actual, len(members)) - 30.0, 4),
        })

    summary_rows = []
    for split_name in ("calibration", "heldout"):
        members = [features[repo] for repo, split_name_actual in assignment.items() if split_name_actual == split_name]
        count = len(members)
        summary_rows.append({
            "split": split_name,
            "repositories": count,
            "mean_selected_loc": round(statistics.mean(row["selected_loc"] for row in members), 2),
            "median_selected_loc": round(statistics.median(row["selected_loc"] for row in members), 2),
            "mean_selected_files": round(statistics.mean(row["selected_files"] for row in members), 2),
            "median_selected_files": round(statistics.median(row["selected_files"] for row in members), 2),
            "mean_internal_static_occurrences": round(statistics.mean(row["internal_static_occurrences"] for row in members), 2),
            "median_internal_static_occurrences": round(statistics.median(row["internal_static_occurrences"] for row in members), 2),
            "mean_internal_static_density_per_1000_loc": round(statistics.mean(row["internal_static_density"] for row in members) * 1000, 4),
            "median_internal_static_density_per_1000_loc": round(statistics.median(row["internal_static_density"] for row in members) * 1000, 4),
            **{
                f"size_q{q}_repositories": sum(size_quartiles[repo] == q for repo, side in assignment.items() if side == split_name)
                for q in range(1, 5)
            },
            **{
                f"density_q{q}_repositories": sum(density_quartiles[repo] == q for repo, side in assignment.items() if side == split_name)
                for q in range(1, 5)
            },
        })

    output_dir.mkdir(parents=True, exist_ok=True)
    split_csv = output_dir / "repository-split.csv"
    balance_csv = output_dir / "repository-split-balance.csv"
    summary_csv = output_dir / "repository-split-summary.csv"
    _write_csv(split_csv, split_rows)
    _write_csv(balance_csv, balance_rows)
    _write_csv(summary_csv, summary_rows)

    rule_balance = [
        row for row in balance_rows if row["token"].startswith("RULE_PRESENT_")
    ]
    large_gaps = [
        row for row in rule_balance
        if abs(
            float(row["heldout_prevalence_percent"])
            - float(row["calibration_prevalence_percent"])
        ) > 10
    ]
    lines = [
        "# Repository split balance report",
        "",
        f"Seed: `{SPLIT_SEED}`. Repository-level split only; aggregate counts were used for the prescribed balance features. No source-context bundles, human labels, or held-out review samples were opened.",
        "",
        f"Calibration: {CALIBRATION_REPOSITORIES} repositories. Held-out: {HELDOUT_REPOSITORIES} repositories. Total: {len(assignment)}.",
        "",
        "## Distribution summary",
        "",
        "| Split | Repositories | Mean selected LOC | Median selected LOC | Mean source density / 1,000 LOC | Median source density / 1,000 LOC |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in summary_rows:
        lines.append(
            f"| {row['split']} | {row['repositories']} | {row['mean_selected_loc']} | {row['median_selected_loc']} | "
            f"{row['mean_internal_static_density_per_1000_loc']} | {row['median_internal_static_density_per_1000_loc']} |"
        )
    lines.extend([
        "",
        "## Top-15 rule presence balance",
        "",
        "| Rule | Present in calibration | Present in held-out | Calibration prevalence | Held-out prevalence | Difference (pp) | Flag >10 pp |",
        "|---|---:|---:|---:|---:|---:|---|",
    ])
    for row in rule_balance:
        rule = row["token"].removeprefix("RULE_PRESENT_")
        cal_n = int(row["actual_calibration_repositories"])
        held_n = int(row["actual_heldout_repositories"])
        cal_pct = float(row["calibration_prevalence_percent"])
        held_pct = float(row["heldout_prevalence_percent"])
        difference = round(held_pct - cal_pct, 4)
        lines.append(
            f"| `{rule}` | {cal_n} | {held_n} | {cal_pct}% | {held_pct}% | {difference} | "
            f"{'YES — inspect, do not manually move repos' if abs(difference) > 10 else 'no'} |"
        )
    lines.extend([
        "",
        f"Rules flagged for manual inspection: {len(large_gaps)}. Flags are diagnostic only; repositories were not manually reassigned.",
        "",
        "Size and density quartiles use deterministic rank bins on `log1p(value)`, with equal feature values broken by the frozen SHA256 repository rank. Rule-presence tokens are exactly the 15 most prevalent static-source rules by occurrence count.",
    ])
    balance_md = output_dir / "repository-split-balance.md"
    balance_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    split_summary_path = output_dir / "repository-split-summary.csv"
    manifest = {
        "schema_version": 1,
        "seed": SPLIT_SEED,
        "source_run": "v007-full-repro-2026",
        "source_hashes": {
            "all_internal_source_occurrences_csv_sha256": sha256_file(source_path),
            "static_source_identity_manifest_sha256": sha256_file(identity_manifest_path),
            "static_source_candidate_table_sha256": identity_manifest["candidate_file_sha256"],
            "repository_summary_csv_sha256": sha256_file(run_dir / "aggregate/repository-summary.csv"),
            "repository_execution_status_csv_sha256": sha256_file(run_dir / "tables/repository-execution-status.csv"),
        },
        "algorithm": {
            "name": "deterministic rarest-token iterative stratification with hard capacities",
            "version": "v1",
            "heldout_capacity": HELDOUT_REPOSITORIES,
            "calibration_capacity": CALIBRATION_REPOSITORIES,
            "target_heldout_per_token": "round(0.30 * token_population)",
            "assignment_score": "mean normalized deficit over the candidate repository's tokens",
            "token_order": "smallest remaining unassigned carrier count, then token name",
            "candidate_order": "SHA256(seed + '|' + repository), ascending",
            "assignment_tie_break": "candidate hash first hex digit 0-4 -> heldout; 5-f -> calibration",
            "hard_capacities_enforced_during_assignment": True,
            "quartiles": "equal-count rank bins over log1p(feature), ties by repository hash rank",
            "tokens": "SIZE_Q1..Q4; DENSITY_Q1..Q4; RULE_PRESENT for top 15 rules",
            "ecosystem_family": "not used; no non-subjective frozen family field was available",
        },
        "calibration_count": split_counts["calibration"],
        "heldout_count": split_counts["heldout"],
        "top_15_rules": top_rules,
        "repository_split_csv_sha256": sha256_file(split_csv),
        "repository_split_balance_csv_sha256": sha256_file(balance_csv),
        "repository_split_summary_csv_sha256": sha256_file(split_summary_path),
        "repository_split_balance_md_sha256": sha256_file(balance_md),
        "rule_prevalence_flags_over_10_percentage_points": [
            row["token"].removeprefix("RULE_PRESENT_") for row in large_gaps
        ],
        "human_labels_used": False,
        "heldout_occurrence_samples_generated": False,
    }
    manifest_path = output_dir / "repository-split-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument(
        "--output-dir", type=Path, default=Path("study/validation-v007-human/splits")
    )
    args = parser.parse_args()
    root = args.root.resolve()
    output_dir = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    print(json.dumps(build_split(root, output_dir), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
