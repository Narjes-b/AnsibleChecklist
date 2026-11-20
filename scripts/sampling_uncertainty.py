#!/usr/bin/env python3
"""Two-stage variance and synthetic interval diagnostics, never tool accuracy.

Ideal design: independent strata, SRSWOR groups, then SRSWOR occurrences.
HT total variance is design unbiased when estimable. The global ratio uses
plug-in linearization. Normal Wald intervals are candidates to stress-test,
not an accepted interval method or a final reporting API.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import math
from pathlib import Path
from statistics import NormalDist, variance
import sys

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.sample_partitioned_occurrences import Design, choose_groups, load_verified_strata, sha256, stable_digest, write_csv
from scripts.simulate_partitioned_sampling import SCENARIOS, planted_population


@dataclass(frozen=True)
class GroupCount:
    group: str
    population: int
    sampled: int
    positives: int

    def __post_init__(self):
        if (not isinstance(self.group, str) or not self.group
                or any(type(value) is not int for value in (self.population, self.sampled, self.positives))
                or not 0 <= self.positives <= self.sampled <= self.population or self.sampled < 1):
            raise ValueError("invalid complete binary group sample")


def stratum_total(population_groups, samples, *, residual_ratio=0.0):
    """HT total/variance for a fixed residual y - r; do not impute singleton SEs.

    With M groups, k chosen, group total estimates t_g and within variances
    v_g: Vhat = M(M-k)/k * s²(t_g) + M/k * sum(v_g).
    Here t_g may be residualized by subtracting r*N_g. The within variance
    is unchanged by this constant shift of each occurrence.
    """
    samples = tuple(samples)
    k, M = len(samples), population_groups
    if (type(M) is not int or not 1 <= k <= M or not isinstance(residual_ratio, (int, float))
            or isinstance(residual_ratio, bool) or not math.isfinite(residual_ratio)
            or any(not isinstance(sample, GroupCount) for sample in samples)
            or len({sample.group for sample in samples}) != k):
        raise ValueError("invalid stratum or residual ratio")
    estimates = [sample.population / sample.sampled * sample.positives for sample in samples]
    total = M / k * math.fsum(estimates)
    size_estimate = M / k * sum(sample.population for sample in samples)
    residuals = [estimate - residual_ratio * sample.population for estimate, sample in zip(estimates, samples)]
    reasons, within = [], []
    for sample in samples:
        N, m, h = sample.population, sample.sampled, sample.positives
        if m == N:
            within.append(0.0)
        elif m < 2:
            reasons.append("within-group-singleton")
        else:
            within.append(N * (N - m) * h * (m - h) / (m * m * (m - 1)))
    if k == M:
        between = 0.0
    elif k < 2:
        reasons.append("between-group-singleton")
        between = None
    else:
        between = M * (M - k) / k * variance(residuals)
    estimated_variance = None if reasons else between + M / k * math.fsum(within)
    return {"estimated_total": total, "estimated_population": size_estimate,
            "estimated_residual_total": total - residual_ratio * size_estimate, "variance_residual_ratio": residual_ratio,
            "estimated_variance": estimated_variance, "variance_unavailable_reasons": sorted(set(reasons)),
            "complete_census": k == M and all(sample.sampled == sample.population for sample in samples)}


def population_estimates(strata, known_population):
    """Combine independent strata; no missing/uncertain responses supported."""
    strata = [(identity, M, tuple(groups)) for identity, M, groups in strata]
    if (type(known_population) is not int or known_population < 1 or not strata
            or len({identity for identity, _, _ in strata}) != len(strata)):
        raise ValueError("invalid population or duplicate/empty strata")
    initial = [stratum_total(M, groups) for _, M, groups in strata]
    weighted_y = math.fsum(item["estimated_total"] for item in initial)
    weighted_n = math.fsum(item["estimated_population"] for item in initial)
    ratio = weighted_y / weighted_n
    census = all(item["complete_census"] for item in initial)
    if census and weighted_n != known_population:
        raise ValueError("census does not reconcile with known population")
    results = []
    for estimator, point, denominator, values in (
        ("ht-known-population", weighted_y / known_population, known_population, initial),
        ("hajek-product-weights", ratio, weighted_n,
         [stratum_total(M, groups, residual_ratio=ratio) for _, M, groups in strata]),
    ):
        unavailable = [identity for (identity, _, _), item in zip(strata, values) if item["estimated_variance"] is None]
        value = None if unavailable else math.fsum(item["estimated_variance"] for item in values) / denominator ** 2
        results.append({"estimator": estimator, "estimate": point, "estimated_variance": value,
                        "standard_error": None if value is None else math.sqrt(value),
                        "unavailable_strata": unavailable, "complete_census": census,
                        "zero_variance_non_census": value == 0 and not census,
                        "estimated_population": weighted_n})
    return results


def simulate_uncertainty(strata, scenario, replications, seed):
    if replications < 2:
        raise ValueError("at least two replications required")
    population = planted_population(strata, scenario, seed)
    total = sum(int(sizes.sum()) for _, sizes, _ in population)
    truth = sum(int(positive.sum()) for _, _, positive in population) / total
    z = NormalDist().inv_cdf(0.975)
    draws = []
    for replication in range(replications):
        draw_seed = stable_digest(seed, "draw", replication)
        rng = np.random.default_rng(int(stable_digest(seed, "within", scenario, replication)[:16], 16))
        observed, sample_size = [], 0
        for stratum, (names, sizes, positive) in zip(strata, population):
            chosen = choose_groups(names, stratum.selected_groups, draw_seed, stratum.identity)
            indices = np.array([names.index(group) for group in chosen], dtype=int)
            n = sizes[indices]
            m = np.array([stratum.draw_size(group) for group in chosen], dtype=int)
            hits = rng.hypergeometric(positive[indices], n - positive[indices], m)
            groups = [GroupCount(group, int(N), int(q), int(h)) for group, N, q, h in zip(chosen, n, m, hits)]
            observed.append((stratum.identity, len(names), groups))
            sample_size += int(m.sum())
        for result in population_estimates(observed, total):
            se, estimate = result["standard_error"], result["estimate"]
            low, high = (None, None) if se is None else (estimate - z * se, estimate + z * se)
            draws.append({"scenario": scenario, "replication": replication, **result,
                          "unavailable_strata": ";".join(result["unavailable_strata"]),
                          "selected_occurrences": sample_size, "synthetic_population_fraction": truth,
                          "normal_95_low": low, "normal_95_high": high,
                          "normal_95_covers": se is not None and low - 1e-14 <= truth <= high + 1e-14,
                          "normal_95_outside_unit_range": se is not None and (low < 0 or high > 1),
                          "measured_tool_accuracy": False})
    summaries = []
    for estimator in ("ht-known-population", "hajek-product-weights"):
        records = [row for row in draws if row["estimator"] == estimator]
        values = np.array([row["estimate"] for row in records])
        available = [row for row in records if row["estimated_variance"] is not None]
        empirical = float(values.var(ddof=1))
        mean_variance = float(np.mean([row["estimated_variance"] for row in available])) if available else None
        coverage = sum(row["normal_95_covers"] for row in records) / replications
        summaries.append({"scenario": scenario, "estimator": estimator, "replications": replications,
                          "synthetic_population_fraction": truth, "mean_estimate": float(values.mean()),
                          "bias": float(values.mean() - truth), "rmse": float(np.sqrt(np.mean((values - truth) ** 2))),
                          "empirical_variance": empirical, "mean_estimated_variance": mean_variance,
                          "estimated_to_empirical_variance_ratio": mean_variance / empirical if mean_variance is not None and empirical > 1e-25 else "not-applicable",
                          "interval_available_fraction": len(available) / replications,
                          "normal_95_coverage_all_draws": coverage,
                          "normal_95_coverage_available_draws": sum(row["normal_95_covers"] for row in available) / len(available) if available else "not-applicable",
                          "coverage_monte_carlo_se": math.sqrt(coverage * (1 - coverage) / replications),
                          "normal_95_mean_width": float(np.mean([row["normal_95_high"] - row["normal_95_low"] for row in available])) if available else "not-applicable",
                          "normal_95_outside_unit_range_fraction": sum(row["normal_95_outside_unit_range"] for row in records) / replications,
                          "zero_variance_non_census_fraction": sum(row["zero_variance_non_census"] for row in records) / replications,
                          "mean_selected_occurrences": float(np.mean([row["selected_occurrences"] for row in records])),
                          "candidate_interval_accepted": False, "measured_tool_accuracy": False})
    return summaries, draws


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
    if args.output_dir.exists():
        parser.error("output exists; use a new diagnostic directory")
    design = Design(args.groups_per_stratum, args.occurrences_per_group, args.census_at)
    strata, frame = load_verified_strata(args.frame_dir, args.occurrences, args.instrument, design, args.repository_groups)
    summaries, draws = [], []
    for scenario in SCENARIOS:
        rows, individual = simulate_uncertainty(strata, scenario, args.replications, args.seed)
        summaries.extend(rows)
        draws.extend(individual)
        print(f"Checked variance/normal intervals: {scenario} ({args.replications} draws)", flush=True)
    args.output_dir.mkdir(parents=True)
    write_csv(args.output_dir / "uncertainty-summary.csv", summaries)
    write_csv(args.output_dir / "uncertainty-draws.csv", draws)
    manifest = {"purpose": "synthetic design variance/normal-interval diagnostic; not measured accuracy",
                "run_id": frame["run_id"], "instrument": args.instrument, "design": vars(design),
                "replications_per_scenario": args.replications, "seed": args.seed, "scenarios": SCENARIOS,
                "numpy_version": np.__version__, "implementation_sha256": sha256(Path(__file__)),
                "dependency_sha256": {name: sha256(Path(__file__).with_name(name)) for name in
                                      ("sample_partitioned_occurrences.py", "simulate_partitioned_sampling.py", "audit_sampling_partitions.py")},
                "frame_manifest_sha256": sha256(args.frame_dir / "frame-manifest.json"),
                "occurrences_sha256": sha256(args.occurrences),
                "group_map_sha256": sha256(args.repository_groups) if args.repository_groups else None,
                "output_sha256": {name: sha256(args.output_dir / name) for name in ("uncertainty-summary.csv", "uncertainty-draws.csv")},
                "eligible_for_performance_scoring": False, "candidate_interval_accepted": False,
                "interval_candidate": "unclipped normal Wald, z=NormalDist().inv_cdf(0.975)",
                "limits": ["Fixed finite planted binary populations, not human labels",
                           "Complete response; no reviewer error/nonresponse model",
                           "HT variance uses ideal independent-stratum two-stage SRSWOR law",
                           "Ratio variance is plug-in linearization, not an exact unbiased variance",
                           "Singleton non-census variance is unavailable, never imputed zero",
                           "Zero estimated variance is not proof a non-census population is constant",
                           "Coverage of this normal candidate is measured here, not guaranteed",
                           "No final population, estimator, interval or workload gate is accepted"]}
    (args.output_dir / "uncertainty-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
