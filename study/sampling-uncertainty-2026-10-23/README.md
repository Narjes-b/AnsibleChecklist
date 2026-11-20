# Sampling variance and interval diagnostic — 2026-10-23

**The normal 95% interval candidate is rejected.** Correct selection probabilities and better point estimates do not, by themselves, produce reliable intervals. These are planted finite binary populations, not human labels or measured AnsibleGuard precision. Final population/estimator/interval/workload eligibility remains false.

We repeated the earlier six populations and 400 draws per scenario, using the same seed and production group-selection/within-group sampling law. Both allocations have exactly the earlier HT/global-Hájek point estimates (mean, bias, RMSE and workload verified against the preserved point-study outputs). The new diagnostic adds both-stage variance, standard errors and an explicit normal-Wald candidate, without changing the samples.

## Full coverage results

Each cell is observed coverage out of 400 draws. Nominal coverage is 95%; intervals are the **unclipped normal candidate** `estimate ± 1.95996 × estimated SE`.

| Planted scenario | HT, 3 groups | HT, 5 groups | Global Hájek, 3 groups | Global Hájek, 5 groups |
|---|---:|---:|---:|---:|
| Constant baseline 0.60 | 90.75% | 92.00% | 92.25% | 92.50% |
| Size-positive baseline 0.60 | 90.50% | 90.25% | 92.50% | 90.75% |
| Size-negative baseline 0.60 | 90.25% | 91.25% | 93.25% | 93.50% |
| Heterogeneous baseline 0.95 | 91.00% | 90.50% | 80.75% | 86.50% |
| Near-boundary baseline 0.995 | 89.50% | 90.50% | **51.00%** | **66.25%** |
| All positive | 89.75% | 90.50% | 100.00% | 100.00% |

The scenario baseline is the generating parameter, not the realized finite truth. Near-boundary truth is **99.25698%**. The more-groups design has the same planted population; it is not a second independent truth/evaluation sample. At 51% coverage, Monte Carlo SE is about 2.50 percentage points; this failure is much larger than ordinary simulation noise.

The all-positive Hájek control is exactly one in every draw, so its zero-width interval covers that particular constant truth. This is not evidence that observing only positives in a non-census sample justifies a zero-width confidence interval.

## Near-boundary failure in detail

| Diagnostic | Up to 3 groups | Up to 5 groups |
|---|---:|---:|
| Mean selected occurrences | 850.6275 | 1,274.2825 |
| Mean global Hájek estimate | 99.32275% | 99.19386% |
| Coverage count | 204/400 | 265/400 |
| Misses with truth below the entire interval | 196 | 135 |
| Misses with truth above the entire interval | 0 | 0 |
| Zero-SE draws, despite non-census design | 8 | 0 |
| Median interval width | 0.89567 percentage points | 1.29329 percentage points |
| Mean interval width | 2.095 percentage points | 2.314 percentage points |

Most misses persist even with nonzero estimated variance; simply forbidding zero-width intervals does not repair the method. Mean point bias is small here, yet many intervals are overconfident on the optimistic side. Increasing groups improves this scenario but does not reach nominal coverage, and does not uniformly improve coverage in the other scenarios. No outcome was removed from these tables.

## Variance implementation and verification

[sampling_uncertainty.py](../../scripts/sampling_uncertainty.py) implements the ideal independent-stratum two-stage SRS-without-replacement law. For one stratum with `M` groups, `k` sampled groups, group size `N_g`, within sample `m_g`, and observed binary positives `h_g`:

```text
t_g = N_g * h_g / m_g
HT total = (M/k) * sum_selected(t_g)
v_g = N_g*(N_g-m_g) * h_g*(m_g-h_g) / [m_g²*(m_g-1)]
Vhat(HT total) = M*(M-k)/k * sample_variance(t_g)
                 + (M/k) * sum_selected(v_g)
```

`v_g=0` when the group is fully censused, including size-one groups. If `m_g=1<N_g`, within-group variance is unavailable. If `k=1<M`, between-group variance is unavailable. Neither case is imputed zero. A complete census must reconcile with the known population.

Why both terms are needed: let `v_g` be the true within-group total variance. The true design variance is `M*(M-k)/k * S²(group totals) + (M/k)*sum_all(v_g)`. The expected sample variance of noisy group-total estimates is `S²(group totals) + sum_all(v_g)/M`. The first estimated term therefore adds `(M-k)/k * sum_all(v_g)`; the expected second term adds `sum_all(v_g)`. Together these recover the true variance. Omitting either stage would be wrong.

For the global Hájek fraction, the code substitutes the sample ratio `R` into residual group totals `t_g - R*N_g`, applies the same variance kernel and divides by estimated population size squared. For a **fixed** residual constant the kernel is design unbiased; fitting `R` makes the fraction variance a **plug-in linearization approximation**, not an exact unbiased variance for the ratio. HT fraction variance divides total variance by known population size squared. HT fractions/intervals may lie outside [0,1]; clipping a point estimate would change its bias and is not silently applied.

**41 focused tests passed.** Exact enumeration over all group/within-group selections in an unequal-size toy population verifies the expected total and expected variance against the actual sampling variance, for three fixed residual constants. Tests also verify census/singleton behavior, invalid binary data, no dropped unestimable draws, deterministic replay and parity with the earlier point-estimator simulation. This is stronger than checking a formula against itself, but does not validate every confidence interval approximation.

On both real-frame allocations, all simulated draws have estimable variance under these rules. This availability is not interval reliability. `uncertainty-summary.csv` records empirical variance, mean estimated variance, their ratio, coverage/Monte Carlo SE, interval width/range violations, zero-variance fractions and all eligibility flags. `uncertainty-draws.csv` retains all **4,800 estimator/draw rows per allocation**. All output hashes and 24 estimator/scenario point comparisons against the earlier outputs were verified.

## What changes in the sampling methodology

1. **Reject normal-Wald reporting for final precision.** Neither the larger workload nor small point bias makes this candidate valid. Do not substitute an ordinary unweighted binomial interval for clustered, unequal-weight sampling.
2. **Change allocation and interval method together.** Compare within-group quotas above two, group allocation alternatives and pre-specified size/rule/decision strata. Sparse/certainty strata and large groups can still have only two sampled occurrences after all their available groups are selected. More groups alone cannot fix every source of sparse within-group evidence.
3. **Test boundary-aware methods and honest bounds.** Preserve two-stage weights/finiteness in any score, replicate or design-based candidate. Include the near-boundary and all-positive controls; add fresh stress populations before accepting a method. A conservative finite-design bound is a useful benchmark even if its width proves impractical.
4. **Keep nonresponse and rater error explicit.** Current simulation assumes complete, correct binary outcomes. The construct audit has alias/duplicate/identity gaps; dropping those selected rows could bias a real estimate. Simulate correlated retrieval/label missingness and reviewer error, and report identification limits instead of promoting complete-case scores.
5. **Choose a budget only after these gates and a human effort pilot.** The previous stratum-calibrated ratio also showed substantial point bias. Switching estimators or merely raising a quota is not a substitute for checking the whole design. Current 861/1,266 selected required draws remain development alternatives, not an approved final workload.

## Reproduce

Use a new output directory for each allocation, from the project root. The external aggregate CSV is the previously checksum-verified frozen input.

```sh
.venv/bin/python scripts/sampling_uncertainty.py \
  --frame-dir study/sampling-design-2026-10-23 \
  --occurrences /tmp/ansibleguard-overlap-repair-2026-10-23/aggregate/all-internal-source-occurrences.csv \
  --instrument required --groups-per-stratum 3 --occurrences-per-group 2 --census-at 30 \
  --replications 400 --seed recovery-design-check-20261023-v1 \
  --output-dir /tmp/ansibleguard-uncertainty-REPLAY-3
```

Repeat with `--groups-per-stratum 5` and a different new output path. Manifests record design, seed, source/frame/group-map hashes, implementation/dependency hashes, NumPy version and interpretation limits. See the [earlier point study](../sampling-draws-2026-10-23/SIMULATION.md), [construct evidence gaps](../evidence-constructs-2026-10-23/README.md), [methodology](../../docs/study/sampling-methodology-2026-10-23.md) and [running log](../../docs/study/recovery-progress.md).
