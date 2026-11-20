# V0.0.7 human-validation weighting method

## General rules

All weights are attached to an explicit `(sample_id, sub_study_id)` membership. A unique human-review item appears once in `validation-items.csv`; overlapping estimands use multiple membership rows and never duplicate the decision. Membership records include `population_id`, `stratum_id`, `population_N`, `sample_n`, `selection_probability`, `sampling_weight`, and seed. Probabilities must be in `(0, 1]`; census memberships have probability and weight 1.

For a simple random sample without replacement within a stratum, `pi = n/N` and the design weight is `1/pi = N/n`. A census has `pi = 1`. The representative calibration core estimates occurrence-weighted precision/actionability and uncertain rate; it is not balanced by rule. Top-up or diversity-audit items never enter the core estimator.

## Core plus overlapping top-ups

Rule/concept/security estimands use the union of representative-core rows and a SHA-ranked top-up from eligible non-core items. Let `M` be the full calibration static population, `n0` the fixed core size, `N_h` the size of a target validation stratum, and `T_h` its final target. The core is an SRSWOR of size `n0` from `M`. Let `C_h` be the number of core items in stratum `h`; when `C_h < T_h`, select `T_h-C_h` by an independent SHA-ranked SRSWOR from the `N_h-C_h` non-core stratum members. If `C_h >= T_h`, add no top-up.

For a particular item in stratum `h`, the unconditional final inclusion probability under this two-stage design is:

```text
pi_h = n0/M + (1 - n0/M) * E[ I(C < T_h) * (T_h - C)/(N_h - C) | item is not in the core ]
```

where `C` conditional on the item not being in the core follows a hypergeometric distribution with population `M-1`, `N_h-1` successes, and `n0` draws. Compute this probability from the full frozen population and design; do not substitute the realized `n_final/N_h` or apply a duplicated naive weight. The membership weight is `1/pi_h`. For a census target `T_h=N_h`, `pi_h=1`.

If a later implementation uses a different selection design, it must derive and validate its actual final inclusion probability before any human labels are collected. Do not generate a sample if a valid probability cannot be calculated.

## Estimands

- Overall occurrence-weighted semantic precision: use only `representative-core` membership. The weighted ratio is `sum(w_i * I(label_i=positive)) / sum(w_i * I(label_i in {positive,negative}))`. Report uncertain and unreviewable rates separately with the same core design weights.
- Per-rule and per-concept precision: use that rule/concept's final probability-sample membership, including core and top-up rows once each, with its correct `1/pi_h` weights. For special multi-concept rules, compute concept estimates first and reconstruct a rule estimate using actual split-specific concept population weights.
- Macro precision: compute decided per-rule precision first, then take the predeclared equal-rule mean; do not weight rules by occurrence count.
- Review/history: report separately from static-source precision. A complete split-specific census has unit weights; evidence-unavailable rows remain explicitly unreviewable when the design includes them.
- Source-first recall and threshold studies: use their own candidate populations and membership-specific probabilities. Never reuse static-positive precision weights for a different universe.
- Diversity audits: report qualitatively/separately unless their inclusion probabilities are explicitly modeled and frozen.

## Uncertainty and clustering

Repository findings are clustered. For weighted confidence intervals, resample repository clusters, not individual findings. Freeze a bootstrap seed and at least 2,000 replicates before scoring. Each replicate samples calibration repositories with replacement at the repository level, retains all sampled items and their design weights, and recomputes the weighted ratio/estimand. Report the percentile interval and exact bootstrap configuration; do not describe findings as independent Bernoulli trials.

No precision or recall estimate is produced until the corresponding valid human labels and adjudication state exist. Uncertain is never silently recoded as a false positive; report decided precision and uncertainty rates, with any conservative sensitivity estimate named separately.
