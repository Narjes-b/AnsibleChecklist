# Simulation of the v0.0.7 heldout sampling design (2026-10-16)

`scripts/v007_sampling_simulation.py` plants a known precision per rule in the
**real heldout population** and checks whether the planned design recovers it.
It answers: *do the sample sizes, the per-repository cap, and the intervals in
the validation plan do what the plan says?* Before this simulation the plan's
"±12–15 pp" was an assumption.

## Inputs

- `population-counts.csv`: required-rule occurrence counts per rule and
  repository, with the repository's split. Derived from
  `aggregate/all-internal-source-occurrences.csv` of the publishable
  re-execution of `v007-full-repro-2026` (counts only; no source content).
- `design-plan.csv`: the sampling plan the design produces for every required
  rule in the heldout population.
- `simulation-results.csv`: bias, RMSE, 95 % coverage and mean half-width by
  scenario, tier, and estimator.

## Truth model and design

- Per-rule planted precision: 0.95 (`high`), 0.45–0.99 random (`mixed`), 0.60
  (`low`).
- Repository effect on the log-odds, standard deviation `sigma` ∈ {0.5, 1.5};
  correlation `rho` ∈ {0, 0.7} between repository size and precision
  (larger repositories differ systematically — generated roles, vendored
  code).
- 400 replications × 12 scenarios; 400 bootstrap resamples; fixed seed.
- Design: census when a rule has ≤ 30 heldout occurrences; otherwise a
  two-stage sample (repositories at random, then at most 2 occurrences per
  repository; cap relaxed only if the target is unreachable), target 30
  (mid, < 500 occurrences) or 40 (large, ≥ 500).

## What the real population looks like

| | Rules | Items |
|---|---:|---:|
| Census (≤ 30 heldout occurrences) | 18 | 155 |
| Mid (30 – 499), target 30 | 23 | 690 |
| Large (≥ 500), target 40 | 10 | 400 |
| **Total** | **51** | **1,245** |

The earlier plan tiered by *overall* counts (24 large / 15 mid / 13 rare) and
budgeted ~1,900 items. By the heldout population that matters there are only
**10 large rules**. Two sampled rules have fewer than 8 repositories to
sample (`excessive-nesting`: 2, `deprecated-modules`: 4), so no
cluster-based interval is reliable for them (`cluster_interval_reliable =
False`); five rules have one repository holding more than half of their
occurrences.

## Findings

1. **Design weights are not optional.** With the cap and a size–precision
   correlation (ρ = 0.7), the naive pooled proportion is biased by up to −0.21
   (rule level) and its Wilson interval covers the truth only 19–91 % of the
   time; the overall estimate has bias −0.02 to −0.21 and coverage 0–64 %. The
   weighted (Hájek) estimator has |bias| ≤ 0.01 in every scenario.
2. **The naive interval looks fine only when it is least needed.** With no
   size–precision correlation it covers 82–96 %; the cap alone does not break
   it, the combination of cap and heterogeneity does.
3. **A cluster-bootstrap percentile interval is not good enough at these
   sample sizes.** Rule-level coverage was 67–95 % (median 89 %), worst when
   precision is high: if every sampled item is correct the interval collapses
   to a point.
4. **A Wilson interval on the design-effective sample size is better.**
   `n_eff = p(1-p)/Var_bootstrap`, capped at the labelled count. Rule-level
   coverage 89–96 % (median 93 %, mean 92.9 %); it is still slightly below
   the nominal 95 %.
5. **Honest precision for a single rule is modest.** Half-widths for the
   recommended interval are about ±8–14 pp when precision is high, ±16–20 pp
   at mixed precision and ±19–23 pp at 0.6. The plan's "±12–15 pp per rule"
   held only for the (invalid) naive interval.
6. **The overall estimate is tighter but not exactly calibrated.** Half-width
   ±2–4 pp (high precision) to ±6–8 pp (low), bias ≤ 0.01, but coverage of the
   95 % interval is 82–95 % (typically ~90 %); the effective-n correction does
   not help here.

## Consequences for the plan

- Report **weighted** estimates with design weights `N_rj / n_rj` and
  repository-level weights from the actual selection probabilities; never a
  pooled proportion.
- Use the effective-n Wilson interval for rules; for rules with fewer than 8
  sampled repositories report counts and exact binomial limits on the labelled
  items only, labelled "not generalizable beyond the sampled repositories".
- Tier by **heldout** population; present the 18 census rules as complete
  enumerations, not estimates.
- Budget 1,245 items for the per-rule design, plus the representative core and
  secondary panels, not 1,900.
- Calibrate the overall interval (choose the nominal level that gives 95 %
  simulated coverage) before the study; this is not yet done.

## Limits

The representative 400-item core, rater error, and the `uncertain` /
`unreviewable` outcomes are not simulated; the planted truth is a model, not
the world; repositories are treated as exchangeable within a rule; the
frozen-run population still contains the artefacts described in the audit
(its review rules are not interpretable), and the counts must be refreshed
from the fixed `v0.0.7.1` run before sampling.

## Reproduce

```bash
python scripts/v007_sampling_simulation.py \
  --occurrences <run>/aggregate/all-internal-source-occurrences.csv \
  --replications 400 --bootstrap 400     # rebuilds population-counts.csv
python scripts/v007_sampling_simulation.py --replications 400 --bootstrap 400
```
