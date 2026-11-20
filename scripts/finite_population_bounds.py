#!/usr/bin/env python3
"""Conservative design-only variance envelope and Chebyshev interval benchmark.

Complete fixed binary populations, known finite frame, ideal independent-stratum
two-stage SRSWOR. This is a design benchmark, never human-label/tool scoring.
Between and within maxima need not occur in the same population, so their sum
is conservative even when the between-group bound is exact.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
import math
from pathlib import Path
import sys

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.sample_partitioned_occurrences import Design, load_verified_strata, read_csv, sha256, write_csv


def between_group_bound(sizes, *, max_dp_population=200_000, max_dp_work=10_000_000):
    sizes = tuple(sizes)
    if not sizes or any(type(size) is not int or size < 1 for size in sizes):
        raise ValueError("positive integer group sizes required")
    M, total = len(sizes), sum(sizes)
    if M == 1:
        return 0.0, "single-group"
    # The variance is separately convex in each total Y_g in [0,N_g],
    # so its maximum lies at a vertex Y_g in {0,N_g}. A subset-sum DP
    # retains the largest sum(N_g²) at each possible positive total T.
    if (total <= max_dp_population and M * total <= max_dp_work
            and M * sum(size * size for size in sizes) <= np.iinfo(np.int64).max):
        best = np.full(total + 1, -1, dtype=np.int64)
        best[0], reached = 0, 0
        for size in sizes:
            source = best[:reached + 1].copy()
            candidate = np.where(source >= 0, source + size * size, -1)
            target = best[size:size + reached + 1]
            np.maximum(target, candidate, out=target)
            reached += size
        totals = np.flatnonzero(best >= 0)
        numerator = int(np.max(M * best[totals] - totals * totals))
        return numerator / (M * (M - 1)), "exact-vertex-dp"
    ordered = sorted(sizes)
    bound = min(sum(size * size for size in sizes) / (M - 1),
                M * max(sizes) ** 2 / (4 * (M - 1)),
                sum(index * size * size for index, size in enumerate(ordered)) / (M * (M - 1)))
    return bound, "analytic-upper-bound"


def within_group_bound(population, sampled):
    if (type(population) is not int or type(sampled) is not int or not 1 <= sampled <= population):
        raise ValueError("valid positive within-group sizes required")
    if sampled == population:
        return 0.0
    return (population - sampled) * (population * population // 4) / (sampled * (population - 1))


def stratum_envelope(sizes, sampled_groups, within_sizes):
    sizes, within_sizes = tuple(sizes), tuple(within_sizes)
    if (type(sampled_groups) is not int or not 1 <= sampled_groups <= len(sizes)
            or len(sizes) != len(within_sizes)):
        raise ValueError("invalid group allocation")
    bound, method = between_group_bound(sizes)
    M, k = len(sizes), sampled_groups
    between = M * (M - k) / k * bound
    within = M / k * math.fsum(within_group_bound(N, m) for N, m in zip(sizes, within_sizes))
    return {"between_variance_bound": between, "within_variance_bound": within,
            "total_variance_bound": between + within, "between_bound_method": method}


def confidence_set(estimate, known_population, variance_bound, *, alpha=0.05):
    if (type(known_population) is not int or known_population < 1 or not math.isfinite(estimate)
            or not math.isfinite(variance_bound) or variance_bound < 0 or not 0 < alpha < 1):
        raise ValueError("invalid interval inputs")
    radius = math.sqrt(variance_bound / alpha) / known_population
    low, high = max(0.0, estimate - radius), min(1.0, estimate + radius)
    return {"low": low, "high": high, "radius": radius,
            "empty_set": low > high, "width": max(0.0, high - low)}


def frame_envelope(strata):
    rows = []
    for stratum in strata:
        names = sorted(stratum.groups)
        sizes = [len(stratum.groups[name]) for name in names]
        within = [stratum.draw_size(name) for name in names]
        rows.append({"stratum_id": stratum.identity, **dict(zip(
            ("rule_id", "policy", "certainty", "resolution_status", "resolution_scope"), stratum.cell)),
                     "size_quartile": stratum.size_quartile, "population_occurrences": sum(sizes),
                     "population_groups": len(names), "sampled_groups": stratum.selected_groups,
                     "largest_group": max(sizes), "expected_selected_occurrences": stratum.selected_groups / len(names) * sum(within),
                     **stratum_envelope(sizes, stratum.selected_groups, within)})
    total_bound = math.fsum(row["total_variance_bound"] for row in rows)
    for row in rows:
        row["share_of_variance_bound"] = row["total_variance_bound"] / total_bound if total_bound else 0.0
    return sorted(rows, key=lambda row: (-row["total_variance_bound"], row["stratum_id"]))


def apply_benchmark(draws, known_population, bound, alpha):
    records, by_scenario = [], {}
    for row in draws:
        if row["estimator"] != "ht-known-population":
            continue  # This guarantee uses an unbiased known-N total, not a ratio.
        interval = confidence_set(float(row["estimate"]), known_population, bound, alpha=alpha)
        truth = float(row["synthetic_population_fraction"])
        result = {"scenario": row["scenario"], "replication": row["replication"], "estimate": row["estimate"],
                  "synthetic_population_fraction": truth, **interval,
                  "covers": not interval["empty_set"] and interval["low"] - 1e-14 <= truth <= interval["high"] + 1e-14,
                  "full_unit_interval": interval["low"] == 0 and interval["high"] == 1,
                  "eligible_for_performance_scoring": False}
        records.append(result)
        by_scenario.setdefault(row["scenario"], []).append(result)
    summaries = [{"scenario": scenario, "replications": len(rows),
                  "coverage": sum(row["covers"] for row in rows) / len(rows),
                  "mean_width": float(np.mean([row["width"] for row in rows])),
                  "full_unit_interval_fraction": sum(row["full_unit_interval"] for row in rows) / len(rows),
                  "empty_set_fraction": sum(row["empty_set"] for row in rows) / len(rows),
                  "known_population": known_population, "total_variance_bound": bound,
                  "radius_fraction": confidence_set(0.5, known_population, bound, alpha=alpha)["radius"],
                  "nominal_minimum_coverage_under_stated_design": 1 - alpha,
                  "final_method_accepted": False, "measured_tool_accuracy": False}
                 for scenario, rows in sorted(by_scenario.items())]
    return summaries, records


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--uncertainty-dir", type=Path, required=True)
    parser.add_argument("--frame-dir", type=Path, required=True)
    parser.add_argument("--occurrences", type=Path, required=True)
    parser.add_argument("--repository-groups", type=Path)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.output_dir.exists() or not 0 < args.alpha < 1:
        parser.error("use a new output directory and alpha in (0,1)")
    source_path = args.uncertainty_dir / "uncertainty-manifest.json"
    source = json.loads(source_path.read_text())
    if (source.get("eligible_for_performance_scoring") is not False
            or source.get("purpose") != "synthetic design variance/normal-interval diagnostic; not measured accuracy"
            or source["frame_manifest_sha256"] != sha256(args.frame_dir / "frame-manifest.json")
            or source["occurrences_sha256"] != sha256(args.occurrences)
            or source["group_map_sha256"] != (sha256(args.repository_groups) if args.repository_groups else None)):
        raise ValueError("synthetic source/frame/group provenance mismatch")
    ledger = args.uncertainty_dir / "uncertainty-draws.csv"
    if source["output_sha256"][ledger.name] != sha256(ledger):
        raise ValueError("source draw hash mismatch")
    design = Design(**source["design"])
    strata, frame = load_verified_strata(args.frame_dir, args.occurrences, source["instrument"], design, args.repository_groups)
    draws = list(read_csv(ledger))
    expected = {(scenario, str(replication), estimator) for scenario in source["scenarios"]
                for replication in range(source["replications_per_scenario"])
                for estimator in ("ht-known-population", "hajek-product-weights")}
    identities = [(row["scenario"], row["replication"], row["estimator"]) for row in draws]
    if len(identities) != len(set(identities)) or set(identities) != expected:
        raise ValueError("source simulation rows missing/duplicated")
    bounds = frame_envelope(strata)
    population = sum(stratum.population for stratum in strata)
    total_bound = math.fsum(row["total_variance_bound"] for row in bounds)
    summaries, records = apply_benchmark(draws, population, total_bound, args.alpha)
    args.output_dir.mkdir(parents=True)
    for name, values in (("stratum-bounds.csv", bounds), ("bound-summary.csv", summaries), ("bound-draws.csv", records)):
        write_csv(args.output_dir / name, values)
    manifest = {"purpose": "conservative finite-design interval/width benchmark; not measured tool accuracy",
                "run_id": frame["run_id"], "instrument": source["instrument"], "design": vars(design),
                "alpha": args.alpha, "known_population": population, "variance_bound": total_bound,
                "between_bound_methods": dict(Counter(row["between_bound_method"] for row in bounds)),
                "source_uncertainty_manifest_sha256": sha256(source_path), "source_draws_sha256": sha256(ledger),
                "implementation_sha256": sha256(Path(__file__)),
                "dependency_sha256": {name: sha256(Path(__file__).with_name(name)) for name in
                                      ("sample_partitioned_occurrences.py", "audit_sampling_partitions.py")},
                "numpy_version": np.__version__, "eligible_for_performance_scoring": False, "final_method_accepted": False,
                "output_sha256": {name: sha256(args.output_dir / name) for name in ("stratum-bounds.csv", "bound-summary.csv", "bound-draws.csv")},
                "assumptions": ["Known finite frame and complete fixed binary outcomes", "Independent strata, two-stage SRSWOR",
                                "HT total divided by known N; no Hájek guarantee", "No retrieval nonresponse or reviewer error",
                                "Guarantee is conditional on the design, not generalization to unseen repositories"],
                "limits": ["Conservative between/within maxima are not jointly optimized", "Wide/full-unit sets can be uninformative",
                           "No final population/workload/interval gate passed"]}
    (args.output_dir / "bound-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"population": population, "variance_bound": total_bound,
                      "radius_fraction": confidence_set(0.5, population, total_bound, alpha=args.alpha)["radius"],
                      "bound_methods": manifest["between_bound_methods"]}), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
