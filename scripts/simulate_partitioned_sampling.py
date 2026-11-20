#!/usr/bin/env python3
"""Check sampling bias on planted finite populations using the real design.

These synthetic binary outcomes are not reviewer labels or measured tool
accuracy. This initial check compares point estimators; confidence intervals,
nonresponse and reviewer error remain outside its scope.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

try:
    from scripts.sample_partitioned_occurrences import (
        Design, choose_groups, load_verified_strata, sha256, stable_digest, write_csv,
    )
except ModuleNotFoundError:
    from sample_partitioned_occurrences import (
        Design, choose_groups, load_verified_strata, sha256, stable_digest, write_csv,
    )


SCENARIOS = {
    "constant-60": (0.60, 0.0, 0.0),
    "size-positive-60": (0.60, 1.2, 0.8),
    "size-negative-60": (0.60, 1.2, -0.8),
    "heterogeneous-95": (0.95, 1.2, 0.0),
    "near-boundary-995": (0.995, 0.8, 0.0),
    "all-positive": (1.0, 0.0, 0.0),
}


def planted_population(strata, scenario, seed):
    base, sigma, rho = SCENARIOS[scenario]
    rng = np.random.default_rng(int(stable_digest(seed, "truth", scenario)[:16], 16))
    groups = sorted({group for stratum in strata for group in stratum.groups})
    effects = dict(zip(groups, rng.standard_normal(len(groups))))
    population = []
    for stratum in strata:
        names = sorted(stratum.groups)
        sizes = np.array([len(stratum.groups[name]) for name in names], dtype=int)
        logged = np.log(sizes)
        size_effect = (logged - logged.mean()) / logged.std() if logged.std() else np.zeros(len(names))
        if base == 1.0:
            positive = sizes.copy()
        else:
            latent = math.log(base / (1 - base)) + sigma * (
                rho * size_effect + math.sqrt(1 - rho * rho) * np.array([effects[name] for name in names])
            )
            positive = rng.binomial(sizes, 1 / (1 + np.exp(-latent)))
        population.append((names, sizes, positive))
    return population


def simulate(strata, scenario, replications, seed):
    if replications < 2:
        raise ValueError("at least two replications are required for Monte Carlo error")
    population = planted_population(strata, scenario, seed)
    total = sum(int(sizes.sum()) for _, sizes, _ in population)
    truth = sum(int(positive.sum()) for _, _, positive in population) / total
    estimates = {name: [] for name in (
        "naive-pooled", "hajek-product-weights", "ht-known-population", "stratified-hajek",
    )}
    sample_sizes = []
    for replication in range(replications):
        pooled_y = pooled_n = weighted_y = weighted_n = stratified_y = 0.0
        draw_seed = stable_digest(seed, "draw", replication)
        rng = np.random.default_rng(int(stable_digest(seed, "within", scenario, replication)[:16], 16))
        for stratum, (names, sizes, positive) in zip(strata, population):
            chosen = choose_groups(names, stratum.selected_groups, draw_seed, stratum.identity)
            indices = np.array([names.index(group) for group in chosen], dtype=int)
            n = sizes[indices]
            m = np.array([stratum.draw_size(group) for group in chosen], dtype=int)
            hits = rng.hypergeometric(positive[indices], n - positive[indices], m)
            first_probability = stratum.selected_groups / len(names)
            weights = n / m / first_probability
            pooled_y += float(hits.sum())
            pooled_n += float(m.sum())
            weighted_y += float((weights * hits).sum())
            weighted_n += float((weights * m).sum())
            # Known stratum totals can also calibrate a ratio within each
            # stratum. Compare its finite-sample bias rather than assuming
            # poststratification automatically improves this sparse design.
            stratified_y += int(sizes.sum()) * float((weights * hits).sum() / (weights * m).sum())
        estimates["naive-pooled"].append(pooled_y / pooled_n)
        estimates["hajek-product-weights"].append(weighted_y / weighted_n)
        estimates["ht-known-population"].append(weighted_y / total)
        estimates["stratified-hajek"].append(stratified_y / total)
        sample_sizes.append(pooled_n)
    rows = []
    for estimator, values in estimates.items():
        values = np.array(values)
        bias = float(values.mean() - truth)
        mc_se = float(values.std(ddof=1) / math.sqrt(replications))
        rows.append({
            "scenario": scenario, "estimator": estimator, "replications": replications,
            "synthetic_population_fraction": truth, "mean_estimate": float(values.mean()),
            "bias": bias, "rmse": float(np.sqrt(np.mean((values - truth) ** 2))),
            "monte_carlo_se_of_mean": mc_se,
            "bias_divided_by_mc_se": bias / mc_se if mc_se > 1e-15 else "not-applicable",
            "outside_zero_one_fraction": float(np.mean((values < -1e-12) | (values > 1 + 1e-12))),
            "mean_selected_occurrences": float(np.mean(sample_sizes)),
            "min_selected_occurrences": int(min(sample_sizes)), "max_selected_occurrences": int(max(sample_sizes)),
            "confidence_interval_status": "not-evaluated", "measured_tool_accuracy": False,
        })
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frame-dir", type=Path, required=True)
    parser.add_argument("--occurrences", type=Path, required=True)
    parser.add_argument("--instrument", choices=("required", "uncertainty", "optional-policy"), required=True)
    parser.add_argument("--groups-per-stratum", type=int, default=3)
    parser.add_argument("--occurrences-per-group", type=int, default=2)
    parser.add_argument("--census-at", type=int, default=30)
    parser.add_argument("--repository-groups", type=Path)
    parser.add_argument("--replications", type=int, default=400)
    parser.add_argument("--seed", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    design = Design(args.groups_per_stratum, args.occurrences_per_group, args.census_at)
    if args.output_dir.exists():
        parser.error("output directory exists; use a new simulation directory")
    strata, frame = load_verified_strata(args.frame_dir, args.occurrences, args.instrument, design, args.repository_groups)
    rows = []
    for scenario in SCENARIOS:
        rows.extend(simulate(strata, scenario, args.replications, args.seed))
        print(f"Simulated {scenario}: {args.replications} draws", flush=True)
    args.output_dir.mkdir(parents=True)
    write_csv(args.output_dir / "simulation-results.csv", rows)
    manifest = {
        "schema_version": 1, "purpose": "synthetic point-estimator design check; not measured accuracy",
        "run_id": frame["run_id"], "instrument": args.instrument, "design": vars(design),
        "replications_per_scenario": args.replications, "seed": args.seed,
        "scenarios": SCENARIOS, "numpy_version": np.__version__,
        "sampler_sha256": sha256(Path(__file__).with_name("sample_partitioned_occurrences.py")),
        "implementation_sha256": sha256(Path(__file__)),
        "frame_manifest_sha256": sha256(args.frame_dir / "frame-manifest.json"),
        "occurrences_sha256": sha256(args.occurrences),
        "group_map_sha256": sha256(args.repository_groups) if args.repository_groups else None,
        "output_sha256": {"simulation-results.csv": sha256(args.output_dir / "simulation-results.csv")},
        "eligible_for_performance_scoring": False,
        "confidence_interval_status": "not-evaluated",
        "limits": ["No nonresponse or reviewer error", "No final evaluation population certified",
                   "Finite planted binary populations, not actual labels", "HT fractions can lie outside [0,1]",
                   "Global and stratum-calibrated Hajek ratios can have finite-sample bias",
                   "No interval or final-budget acceptance gate passed"],
    }
    (args.output_dir / "simulation-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
