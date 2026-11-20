# Point-estimator simulation results — 2026-10-23

Status: calibration design diagnostic. These are synthetic binary outcomes on the real count structure, not measured AnsibleGuard accuracy. Confidence-interval coverage, nonresponse and reviewer error are not evaluated.

Follow-up: the original point results below are preserved. The subsequent [variance/interval diagnostic](../sampling-uncertainty-2026-10-23/README.md) replays the same planted populations and point estimates and rejects the normal 95% interval candidate: near-boundary global-Hájek coverage is only 51% / 66.25% for the three/five-group allocations. This is synthetic development evidence, not measured tool accuracy.

## Design and truth

Both alternatives use the same 59,891 calibration required occurrences and 167 rule/decision/size strata. Each scenario plants one finite population, then repeats the sampling process 400 times. The alternatives select up to three or five groups per stratum, then up to two occurrences per selected group; cells of at most 30 occurrences are censused. Group identity defaults to repository identity.

The six scenarios cover near-constant 60% probability, positive/negative relationships between group size and validity, heterogeneous high probability, a near-boundary high probability, and a completely positive finite population. Group effects are shared across strata. Actual finite-population fractions differ from the nominal planting parameters. They are recorded in the CSV and identical across the two designs.

First-stage selection uses the production sampler. Second-stage positive counts use its exact sampling-without-replacement distribution. Seeds, design parameters, source/script hashes and NumPy version are recorded in each simulation manifest.

## Bias and error

All following numbers are percentage points. Bias is mean estimate minus the fixed finite truth; RMSE combines variance and bias. Monte Carlo SE measures uncertainty in the reported simulation mean, not uncertainty in a real tool-accuracy estimate.

### Three groups per stratum

| Scenario | Naive bias | Global Hajek bias | HT bias | Within-stratum Hajek bias | Global Hajek RMSE | MC SE of global mean |
|---|---:|---:|---:|---:|---:|---:|
| constant-60 | -0.189 | 0.203 | -0.319 | 0.153 | 6.209 | 0.311 |
| size-positive-60 | -14.699 | -0.581 | -0.946 | -6.689 | 4.953 | 0.246 |
| size-negative-60 | 14.854 | 0.917 | 0.443 | 7.595 | 5.919 | 0.293 |
| heterogeneous-95 | 2.471 | -0.090 | -0.884 | 0.141 | 4.714 | 0.236 |
| near-boundary-995 | 0.346 | 0.066 | -0.660 | 0.046 | 1.078 | 0.054 |
| all-positive | 0.000 | 0.000 | -0.732 | 0.000 | 0.000 | 0.000 |

### Five groups per stratum

| Scenario | Naive bias | Global Hajek bias | HT bias | Within-stratum Hajek bias | Global Hajek RMSE | MC SE of global mean |
|---|---:|---:|---:|---:|---:|---:|
| constant-60 | -0.187 | -0.306 | -0.505 | -0.317 | 4.900 | 0.245 |
| size-positive-60 | -15.436 | -0.160 | -0.209 | -3.504 | 3.964 | 0.198 |
| size-negative-60 | 15.373 | 0.311 | 0.094 | 4.049 | 4.786 | 0.239 |
| heterogeneous-95 | 2.221 | -0.173 | -0.458 | -0.073 | 3.665 | 0.183 |
| near-boundary-995 | 0.285 | -0.063 | -0.321 | -0.063 | 0.858 | 0.043 |
| all-positive | 0.000 | 0.000 | -0.260 | 0.000 | 0.000 | 0.000 |

## Findings and decisions

- Naive pooling has about 15 percentage points of bias when validity and group size are correlated. More labels under that same naive estimator do not repair its selection bias.
- Global product-weight Hajek ratios reduce that bias in these planted scenarios, but retain finite-sample bias and substantial sampling variability. Their RMSE ranges up to 6.21 percentage points in the three-group design, versus 4.90 in the larger alternative.
- Within-stratum ratio normalization reduces some variance but has up to 7.60 percentage points of observed bias with three groups and 4.05 with five. Known stratum totals do not make a sparse ratio estimator unbiased. This candidate is not accepted for final reporting.
- HT totals divided by the known population size have the design-unbiased expectation confirmed by exact enumeration in the regression suite. Their sampled fractions can leave [0,1], and their variance is high here. The CSV reports those rates; results are not clipped.
- Under constant validity, naive pooling has lower RMSE than the weighted alternatives. That favorable scenario does not justify ignoring weights when actual validity is heterogeneous. These checks demonstrate a bias/variance tradeoff, not universal superiority of one estimator.
- The larger draw has 1,266 selected IDs compared with 861 in the smaller draw. It adds reviewer cost and improves the simulated weighted RMSE, but its budget and estimator have not passed a final acceptance gate.
- The all-positive scenario cannot validate confidence intervals: a sample that looks perfect still requires an interval with a defensible design. No interval has been evaluated in this check.

## Remaining work

1. Extend the simulation to interval coverage, uncertain/unreviewable outcomes, retrieval failures correlated with complexity, and reviewer error.
2. Compare allocations that control large inverse weights, including more independent groups, certainty selection of dominant groups or a separate representative core, with explicit probabilities for each design.
3. Review actual repository/role dependence and rerun with the reviewed grouping registry.
4. Freeze the accepted allocation, estimator and interpretation before drawing an eligible final sample or collecting final labels.

Until these gates pass, the committed selections are development draws with pending retrieval and labels. They must not be combined into one unweighted precision figure.

Reproduction and file inventory: [README.md](README.md). Raw simulation records: [three-group results](simulation-required/simulation-results.csv), [five-group results](simulation-required-more-groups/simulation-results.csv).
