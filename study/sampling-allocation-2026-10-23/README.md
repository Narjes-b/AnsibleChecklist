# Development allocation comparison — 2026-10-23

Status: all six configurations compared; normal intervals remain rejected and no final allocation is accepted. Configurations were fixed before executing the four new comparisons. This is development after observed failures, not final-design preregistration or independent validation. No labels are collected and no final workload is accepted.

The [normal interval diagnostic](../sampling-uncertainty-2026-10-23/README.md) failed, and the [finite-design benchmark](../sampling-bounds-2026-10-23/README.md) is too wide. The largest-size rule/decision strata dominate its bound. Compare both stages rather than increasing one generic category quota.

| Maximum groups per stratum | Within-group quota | Expected selected IDs | Status |
|---:|---:|---:|---|
| 3 | 2 | 850.62 | Existing baseline |
| 5 | 2 | 1,274.70 | Existing alternative |
| 3 | 5 | 1,450.28 | New comparison |
| 5 | 5 | 2,256.88 | New comparison |
| 10 | 2 | 2,220.39 | New comparison |
| 10 | 5 | 4,095.36 | New comparison |

Small cells remain censused; sparse group strata retain all available groups; within draws are capped by actual group size. Expected counts come from the frame and probabilities before new outcomes are examined. Selected fixed-seed sample counts and reviewer hours may differ. Human effort has not been measured.

[allocation-plan.json](allocation-plan.json) records creation time, exact configuration matrix, seed, scenarios, input hashes, rationale and interpretation limits. Use the same six fixed finite truth populations, 400 replications each, and the tested production sampling/variance implementation. Compare coverage, width, point bias/RMSE, variance availability and expected workload together, retaining unfavorable outcomes. The two similarly priced allocations (5×5 vs. 10×2) help separate group diversity from more occurrences per group.

These are reused development populations and the frozen baseline frame. Any selected candidate needs fresh stress populations, correlated nonresponse/reviewer-error checks, a human effort pilot, and a refreshed final frame after code freeze. A normal interval remains unaccepted even if one configuration improves these cases.

## Observed coverage and error

Each cell below is global-Hájek candidate normal-interval coverage over all 400 planned draws, in percent. Nominal coverage is 95%. All configurations have estimable variances in these scenarios; that does not make the intervals valid.

| Synthetic population | 3×2 | 5×2 | 3×5 | 5×5 | 10×2 | 10×5 |
|---|---:|---:|---:|---:|---:|---:|
| constant-60 | 92.25 | 92.50 | 94.00 | 93.50 | 95.00 | 96.75 |
| size-positive-60 | 92.50 | 90.75 | 91.00 | 93.25 | 94.25 | 92.75 |
| size-negative-60 | 93.25 | 93.50 | 92.00 | 93.50 | 93.75 | 94.50 |
| heterogeneous-95 | 80.75 | 86.50 | 82.50 | 89.25 | 92.00 | 94.25 |
| near-boundary-995 | 51.00 | 66.25 | 64.00 | 72.25 | 70.75 | 75.75 |
| all-positive | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 |

Global-Hájek point RMSE in **percentage points**, independent of interval validity:

| Synthetic population | 3×2 | 5×2 | 3×5 | 5×5 | 10×2 | 10×5 |
|---|---:|---:|---:|---:|---:|---:|
| constant-60 | 6.209 | 4.900 | 3.792 | 3.111 | 3.347 | 2.161 |
| size-positive-60 | 4.953 | 3.964 | 3.610 | 2.704 | 2.571 | 1.976 |
| size-negative-60 | 5.919 | 4.786 | 4.519 | 3.322 | 3.381 | 2.400 |
| heterogeneous-95 | 4.714 | 3.665 | 3.186 | 2.562 | 2.346 | 1.632 |
| near-boundary-995 | 1.078 | 0.858 | 0.694 | 0.537 | 0.602 | 0.382 |
| all-positive | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |

The largest allocation still misses the near-boundary truth in **97/400 draws** (75.75% coverage; Monte Carlo SE 2.14 pp). That fixed truth fraction is 99.2569835%, not exactly the scenario-name target 99.5%. Normal intervals remain rejected. Near-boundary mean width falls from 2.095 to 1.275 pp while point RMSE falls from 1.078 to 0.382 pp; narrower intervals alone are not evidence of accuracy.

At similar expected cost, 5×5 vs. 10×2 has mixed outcomes: 10×2 improves heterogeneous-high coverage (92% vs. 89.25%) and RMSE (2.346 vs. 2.562 pp), while 5×5 improves near-boundary RMSE (0.537 vs. 0.602 pp). These reused scenarios do not establish a universally superior allocation.

All-positive global-Hájek samples produce a zero-width interval at one. Its 100% coverage on an entirely positive fixed population is an algebraic boundary case, not evidence that an unseen rare negative is excluded. The adjacent near-boundary population demonstrates the risk. The HT known-N candidate, its full bias/width results and all raw draws are retained in the CSVs; no unfavorable estimator was dropped.

## Conservative benchmark and cost

The same finite-design variance-envelope/Chebyshev method is reapplied to every allocation. Its guarantee is conditional on the fixed binary finite frame, independent two-stage SRS without replacement and complete accurate outcomes; it does not cover reviewer error/nonresponse/generalization. See the [proof and assumptions](../sampling-bounds-2026-10-23/README.md).

| Allocation | Mean selected IDs | Untrimmed radius (pp) | Constant-scenario mean width (pp) | Constant full-unit sets (%) |
|---|---:|---:|---:|---:|
| 3×2 | 850.63 | 73.492 | 99.510 | 91.75 |
| 5×2 | 1,274.28 | 54.960 | 94.411 | 26.25 |
| 3×5 | 1,449.73 | 69.872 | 99.301 | 87.75 |
| 5×5 | 2,254.81 | 52.050 | 92.007 | 10.50 |
| 10×2 | 2,219.85 | 35.158 | 69.914 | 0.00 |
| 10×5 | 4,093.62 | 32.868 | 65.596 | 0.00 |

Every scenario has observed benchmark coverage 100%, with no empty sets, under all six allocations. Even 10×5 retains a 32.868 pp untrimmed radius and 65.596 pp mean width in the constant scenario: this benchmark remains impractical. More groups reduce the conservative envelope substantially at similar cost (10×2 vs. 5×5); this is a statement about a bound, not estimated actual variance or optimal human workload. All 167 strata use 152 exact vertex DPs plus 15 single-group bounds; no analytic fallback occurred.

## Artifacts and reconciliation

- [allocation-comparison.csv](allocation-comparison.csv): 72 estimator/scenario/configuration rows, including both point estimators, bias, RMSE, mean estimated/empirical variance, availability, coverage, width and workload.
- [bound-comparison.csv](bound-comparison.csv): 36 conservative benchmark summaries.
- [comparison-verification.json](comparison-verification.json): original output/manifest hashes, plan hash, identical seeds/frame/truths, complete unique keys and derived CSV hashes. In total, the comparison references 28,800 estimator/draw rows and 14,400 bound/draw rows. Existing baseline artifacts are linked rather than rewritten.
- `groups-*/`: four new uncertainty runs, retaining all 19,200 estimator/draw rows. `bounds-*/`: four benchmark runs, retaining all 9,600 bound/draw rows. Every output hash was verified before combining.

New runs use `scripts/sampling_uncertainty.py` with the exact [plan](allocation-plan.json) flags, followed by `scripts/finite_population_bounds.py --uncertainty-dir <run>`. Frame: `study/sampling-design-2026-10-23`; occurrence CSV SHA-256: `71be3560cfb8194aa50d63a0ce323737e35ca9aaec0d01004d114b3bd995cecd`. Required calibration population: 59,891. No model calls, performance labels or human hours are inferred. The pre-execution plan remains unchanged.

## Next methodology decision

Keep decision/rule/policy/certainty/scope/size cells and both inclusion probabilities. Compare boundary-aware finite-design methods and allocation targeted to the high-contribution size strata, with explicit small-domain precision targets and costs. Before selecting a candidate, add fresh stress populations, correlated repository nonresponse and asymmetric reviewer error. Preserve every originally selected ID and report incomplete outcomes rather than silently replacing difficult cases. A final sampling frame follows detector/metric code freeze; source-first recall controls and fresh human agreement are separate required instruments.
