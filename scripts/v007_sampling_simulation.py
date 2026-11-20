#!/usr/bin/env python3
"""Simulate the v0.0.7 heldout sampling design on the real rule populations.

Question: does the planned design (per-rule samples, at most CAP occurrences
per repository, two-stage selection) recover a *known* precision, and do the
reported intervals cover it?

Truth model (planted, because real precision is what the study measures):
for rule r and repository j the probability that an occurrence is a true
positive is ``expit(logit(p_r) + sigma * (rho * s_rj + sqrt(1-rho^2) * z_rj))``
where ``s_rj`` is the standardized log of the repository's count for that rule
(rho > 0: larger repositories differ in precision) and ``z_rj`` is N(0,1)
(sigma: between-repository heterogeneity). True positives are drawn per
repository (binomial) so the finite-population precision is exact, and the
sample is drawn from that finite population (hypergeometric).

Design simulated (per required rule, heldout population only):

- N_r <= 30: census (every occurrence labelled; no sampling variance);
- 30 < N_r < 500: target 30; N_r >= 500: target 40;
- two-stage: simple random sample of m repositories, then up to CAP
  occurrences per repository (cap relaxed only if the rule cannot otherwise
  reach its target);
- estimators: naive (pooled proportion, Wilson interval) and Hajek ratio with
  weights N_rj / n_rj and a repository-cluster bootstrap interval;
- overall precision: stratified, sum_r N_r p_r / sum_r N_r.

Not simulated: the 400-item representative core, rater error, `uncertain` /
`unreviewable` outcomes (they change the denominator, not the sampling
logic), and the secondary panels.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import math
from pathlib import Path
import sys

import numpy as np

CAP = 2
CENSUS_AT = 30
MID_TARGET = 30
LARGE_TARGET = 40
LARGE_AT = 500
Z = 1.959963984540054


def wilson(successes: float, n: float) -> tuple[float, float]:
    if n <= 0:
        return 0.0, 1.0
    p = successes / n
    denominator = 1 + Z * Z / n
    center = (p + Z * Z / (2 * n)) / denominator
    half = Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / denominator
    return max(0.0, center - half), min(1.0, center + half)


def tier_of(total: int) -> str:
    if total < CENSUS_AT:
        return "rare"
    return "large" if total >= LARGE_AT else "mid"


def plan_for(counts: np.ndarray) -> dict:
    """Return the sampling plan for one rule (its repository count vector)."""
    total = int(counts.sum())
    tier = tier_of(total)
    if total <= CENSUS_AT:
        return {"tier": tier, "census": True, "target": total, "cap": None, "m": len(counts)}
    target = LARGE_TARGET if total >= LARGE_AT else MID_TARGET
    cap = CAP
    while np.minimum(counts, cap).sum() < target:
        cap += 1
    m = min(len(counts), math.ceil(target / np.minimum(counts, cap).mean()))
    return {"tier": tier, "census": False, "target": target, "cap": cap, "m": m}


def effective_n_wilson(estimate: float, bootstrap_variance: float, sampled: float) -> tuple[float, float]:
    """Wilson interval on the design-effective sample size.

    The bootstrap variance gives n_eff = p(1-p)/v. A percentile bootstrap
    collapses to a point when every sampled item is correct (and is unstable
    with few repositories); Wilson stays proper near 0 and 1. n_eff is capped
    at the number of labelled items, so clustering can only widen the interval.
    """
    if 0 < estimate < 1 and bootstrap_variance > 0:
        effective = estimate * (1 - estimate) / bootstrap_variance
    else:
        effective = sampled
    effective = min(max(effective, 1.0), sampled)
    return wilson(estimate * effective, effective)


def hajek(cluster_y: np.ndarray, cluster_weight: np.ndarray) -> float:
    """Ratio estimator sum(T_y) / sum(T_w) over sampled repositories."""
    return float(cluster_y.sum() / cluster_weight.sum())


def build_counts(occurrences: Path, split_file: Path, output: Path) -> None:
    csv.field_size_limit(1 << 30)
    split = {r["repository"]: r["split"] for r in csv.DictReader(open(split_file, encoding="utf-8"))}
    counts: dict[tuple[str, str], int] = defaultdict(int)
    with open(occurrences, newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            if row["policy"] == "required":
                counts[(row["rule_id"], row["project"])] += 1
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["rule_id", "repository", "split", "occurrences"])
        for (rule, repository), count in sorted(counts.items()):
            writer.writerow([rule, repository, split.get(repository, "unknown"), count])


def load_population(counts_file: Path, split: str) -> dict[str, np.ndarray]:
    by_rule: dict[str, list[int]] = defaultdict(list)
    with open(counts_file, newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            if row["split"] == split:
                by_rule[row["rule_id"]].append(int(row["occurrences"]))
    return {rule: np.array(values) for rule, values in sorted(by_rule.items())}


def expit(x):
    return 1.0 / (1.0 + np.exp(-x))


def logit(p):
    return np.log(p / (1 - p))


def planted_precisions(rules: list[str], scenario: str) -> dict[str, float]:
    generator = np.random.default_rng({"high": 11, "mixed": 22, "low": 33}[scenario])
    if scenario == "high":
        values = np.full(len(rules), 0.95)
    elif scenario == "low":
        values = np.full(len(rules), 0.60)
    else:
        values = generator.uniform(0.45, 0.99, len(rules))
    return dict(zip(rules, values))


class Accumulator:
    def __init__(self) -> None:
        self.rows: dict[tuple, list[float]] = defaultdict(lambda: [0, 0.0, 0.0, 0.0, 0.0])

    def add(self, key: tuple, estimate: float, truth: float, low: float, high: float) -> None:
        row = self.rows[key]
        row[0] += 1
        row[1] += estimate - truth
        row[2] += (estimate - truth) ** 2
        row[3] += float(low <= truth <= high)
        row[4] += high - low


def simulate(population: dict[str, np.ndarray], scenario: str, sigma: float, rho: float,
             replications: int, boots: int, seed: int) -> Accumulator:
    rng = np.random.default_rng(seed)
    rules = list(population)
    planted = planted_precisions(rules, scenario)
    plans = {rule: plan_for(population[rule]) for rule in rules}
    standardized = {}
    for rule, counts in population.items():
        log_counts = np.log(counts)
        spread = log_counts.std()
        standardized[rule] = (log_counts - log_counts.mean()) / spread if spread > 0 else np.zeros_like(log_counts, dtype=float)
    totals = {rule: int(population[rule].sum()) for rule in rules}
    grand_total = sum(totals.values())
    accumulator = Accumulator()
    for _ in range(replications):
        overall_truth_numerator = 0.0
        naive_overall = 0.0
        naive_variance = 0.0
        hajek_overall = 0.0
        boot_overall = np.zeros(boots)
        labelled = 0
        for rule in rules:
            counts = population[rule]
            plan = plans[rule]
            effect = sigma * (rho * standardized[rule] + math.sqrt(1 - rho * rho) * rng.standard_normal(len(counts)))
            probability = expit(logit(planted[rule]) + effect)
            positives = rng.binomial(counts, probability)
            truth = positives.sum() / counts.sum()
            overall_truth_numerator += positives.sum()
            if plan["census"]:
                labelled += int(counts.sum())
                naive_overall += positives.sum()
                hajek_overall += positives.sum()
                boot_overall += positives.sum()
                continue
            chosen = rng.choice(len(counts), plan["m"], replace=False)
            sizes = counts[chosen]
            drawn = np.minimum(sizes, plan["cap"])
            hits = rng.hypergeometric(positives[chosen], sizes - positives[chosen], drawn)
            pooled = hits.sum() / drawn.sum()
            low, high = wilson(hits.sum(), drawn.sum())
            accumulator.add((scenario, sigma, rho, plan["tier"], "naive-pooled+wilson"), pooled, truth, low, high)
            cluster_y = sizes * hits / drawn
            weights = sizes.astype(float)
            estimate = hajek(cluster_y, weights)
            index = rng.integers(0, len(chosen), (boots, len(chosen)))
            replicates = cluster_y[index].sum(axis=1) / weights[index].sum(axis=1)
            accumulator.add((scenario, sigma, rho, plan["tier"], "hajek+cluster-bootstrap"), estimate,
                            truth, float(np.quantile(replicates, 0.025)), float(np.quantile(replicates, 0.975)))
            low2, high2 = effective_n_wilson(estimate, float(replicates.var(ddof=1)) if len(replicates) > 1 else 0.0,
                                             float(drawn.sum()))
            accumulator.add((scenario, sigma, rho, plan["tier"], "hajek+wilson-neff"), estimate, truth, low2, high2)
            naive_overall += totals[rule] * pooled
            naive_variance += (totals[rule] ** 2) * pooled * (1 - pooled) / drawn.sum()
            hajek_overall += totals[rule] * estimate
            boot_overall += totals[rule] * replicates
            labelled += int(drawn.sum())
        truth_overall = overall_truth_numerator / grand_total
        naive_p = naive_overall / grand_total
        half = Z * math.sqrt(naive_variance) / grand_total
        accumulator.add((scenario, sigma, rho, "overall", "naive-pooled+wilson"), naive_p, truth_overall,
                        naive_p - half, naive_p + half)
        boot_overall /= grand_total
        accumulator.add((scenario, sigma, rho, "overall", "hajek+cluster-bootstrap"), hajek_overall / grand_total,
                        truth_overall, float(np.quantile(boot_overall, 0.025)), float(np.quantile(boot_overall, 0.975)))
        low3, high3 = effective_n_wilson(hajek_overall / grand_total, float(boot_overall.var(ddof=1)), float(labelled))
        accumulator.add((scenario, sigma, rho, "overall", "hajek+wilson-neff"), hajek_overall / grand_total,
                        truth_overall, low3, high3)
    return accumulator


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output-dir", type=Path, default=Path("study/validation-design-v007"))
    parser.add_argument("--occurrences", type=Path, help="all-internal-source-occurrences.csv (to rebuild population-counts.csv)")
    parser.add_argument("--replications", type=int, default=200)
    parser.add_argument("--bootstrap", type=int, default=300)
    parser.add_argument("--seed", type=int, default=20261016)
    args = parser.parse_args()
    root = args.root.resolve()
    out = args.output_dir if args.output_dir.is_absolute() else root / args.output_dir
    counts_file = out / "population-counts.csv"
    if args.occurrences:
        build_counts(args.occurrences, root / "study/validation-v007-human/splits/repository-split.csv", counts_file)
    population = load_population(counts_file, "heldout")
    plan_rows = []
    for rule, counts in population.items():
        plan = plan_for(counts)
        plan_rows.append({
            "rule_id": rule, "heldout_occurrences": int(counts.sum()), "heldout_repositories": len(counts),
            "max_repository_share": round(float(counts.max() / counts.sum()), 3), "tier": plan["tier"],
            "design": "census" if plan["census"] else "two-stage", "target": plan["target"],
            "cap_used": plan["cap"] or "", "repositories_sampled": plan["m"],
            "cluster_interval_reliable": plan["census"] or plan["m"] >= 8,
        })
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "design-plan.csv", "w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(plan_rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(plan_rows)
    results = []
    for scenario in ("high", "mixed", "low"):
        for sigma in (0.5, 1.5):
            for rho in (0.0, 0.7):
                accumulator = simulate(population, scenario, sigma, rho, args.replications, args.bootstrap, args.seed)
                for (sc, sg, rh, tier, method), (n, bias, squared, covered, width) in sorted(accumulator.rows.items()):
                    results.append({
                        "scenario": sc, "sigma": sg, "rho": rh, "tier": tier, "method": method, "trials": n,
                        "bias": round(bias / n, 4), "rmse": round(math.sqrt(squared / n), 4),
                        "coverage_95": round(covered / n, 3), "mean_half_width": round(width / n / 2, 4),
                    })
                print(f"done {scenario} sigma={sigma} rho={rho}", flush=True)
    with open(out / "simulation-results.csv", "w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(results[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
