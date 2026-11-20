# Conservative finite-design benchmark — 2026-10-23

**Coverage is honest under the stated complete-binary sampling assumptions, but intervals are too broad to be useful here. No final method or workload is accepted.** This benchmark complements the rejected normal candidate; it is not measured tool accuracy and uses no human labels.

The same 2,400 HT draws per allocation are read from the previous hash-verified simulation. No new favorable draws are selected. The guarantee applies to the unbiased **HT total divided by known population size**, not the global Hájek ratio.

## Observed coverage and width

Coverage is **100% in every one of the six scenarios for both allocations**, over 400 draws each. Mean width and full [0,1] sets show how little information that coverage provides:

| Planted scenario | Mean width, 3 groups | Full [0,1], 3 groups | Mean width, 5 groups | Full [0,1], 5 groups |
|---|---:|---:|---:|---:|
| Constant baseline 0.60 | 99.51 pp | 91.75% | 94.41 pp | 26.25% |
| Size-positive baseline 0.60 | 93.73 pp | 42.00% | 78.24 pp | 0.75% |
| Size-negative baseline 0.60 | 99.94 pp | 95.75% | 91.45 pp | 6.75% |
| Heterogeneous baseline 0.95 | 84.11 pp | 8.00% | 65.61 pp | 0.00% |
| Near-boundary baseline 0.995 | 74.81 pp | 2.50% | 56.02 pp | 0.00% |
| All positive | 74.15 pp | 2.25% | 55.22 pp | 0.00% |

The untrimmed radius is **73.4924 percentage points** at three groups and **54.9600** at five, before intersecting with [0,1]. There are no empty confidence sets in these simulations; empty sets are retained as misses if they arise. These widths are properties of this conservative envelope; tighter verified methods may be possible.

For a same-estimator comparison, the normal **HT** candidate's constant-scenario widths are 38.49 / 29.69 pp with coverage 90.75% / 92%; this benchmark gives 99.51 / 94.41 pp and 100% observed coverage. The much narrower normal Hájek intervals use a different point estimator and do not inherit this guarantee.

## Which partitions drive the envelope

The source frame has 59,891 required calibration occurrences and 167 rule/decision/size strata. All six leading strata are **size quartile 4**, with the following three-group contributions. The ordering is the same at five groups.

| Rule | Certainty / scope | Occurrences | Groups in stratum | Share of total variance bound |
|---|---|---:|---:|---:|
| long-statement | CONFIRMED / rule-static | 3,832 | 23 | 19.63% |
| complex-expression | CONFIRMED / rule-static | 5,784 | 36 | 15.68% |
| large-task | CONFIRMED / rule-static | 5,840 | 37 | 12.08% |
| long-task-name | CONFIRMED / rule-static | 3,173 | 34 | 11.59% |
| unnamed-task | CONFIRMED / rule-static | 4,335 | 19 | 11.15% |
| credentials-leaking-in-log | EXPOSED / task-static | 2,780 | 34 | 8.78% |

These six contribute **78.91% / 78.94%** of the bound under three/five groups. All size-quartile-4 strata contribute **88.52% / 88.56%**. The between-group component accounts for **84.13% / 82.98%** of the envelope. These are conservative design-bound contributions, not observed variance components or error prevalence.

The table motivates allocation comparisons by **rule × certainty × scope × size**, rather than a blanket category quota. It does not prove an optimal allocation. Within-group sampling still matters, especially for rare outcomes; all available groups in a sparse stratum can be selected while only two occurrences per large group are reviewed. Both stages and costs must be examined.

This frame describes the frozen baseline output population. Core task/metric repairs change a future output population; rebuild its frame after code freeze before any final draw.

## Bound and proof

[finite_population_bounds.py](../../scripts/finite_population_bounds.py) uses known group sizes and planned sampling fractions, without outcome estimates. For a group with `N` fixed binary values and a within-group SRS of `m`:

```text
max S²(binary population) = floor(N²/4) / [N*(N-1)]
within-total variance bound = (N-m)*floor(N²/4) / [m*(N-1)]
```

For a census, including `N=m=1`, this is zero. It is computable even when an observed non-census singleton cannot estimate its own variance.

For between-group variance, group totals satisfy `0 <= Y_g <= N_g`. Their sample variance is separately convex in each coordinate, so a maximum occurs at endpoints `Y_g in {0,N_g}`. A bounded subset-sum dynamic program keeps the maximum sum of squared group sizes at each possible positive total `T`, then maximizes:

```text
[M*sum_selected(N_g²) - T²] / [M*(M-1)]
```

The dynamic program avoids floating-point cancellation by maximizing an integer numerator. All 152 multi-group strata use this exact vertex maximum; 15 single-group strata have no between-group variance. Large hypothetical frames fall back to a declared analytic upper bound rather than allocate unbounded memory. Between/within maxima need not be jointly attainable, so the combined envelope is conservative.

For each stratum, use the two-stage variance identity from the [variance diagnostic](../sampling-uncertainty-2026-10-23/README.md):

```text
U_h = M*(M-k)/k * bound(S²(group totals))
      + (M/k)*sum_all_groups(bound(within-total variance))
U = sum_strata(U_h)
r = sqrt(U/alpha) / known_population_size
confidence set = [HT_fraction-r, HT_fraction+r] intersect [0,1]
```

With complete fixed binary outcomes, ideal two-stage SRSWOR and independent stratum selections, HT is unbiased and its variance is at most `U`. Applying the nonnegative squared-error bound gives `P(abs(HT_fraction - truth) >= r) <= alpha`. This is a design-conditional statement about the defined finite frame, not a guarantee about unseen repositories, label errors, retrieval failures or an exposed final evaluation population. Do not apply it to a ratio estimator or clip the HT point before forming the set.

**54 focused tests passed** across finite bounds, two-stage variance, simulation and sampling. Exhaustive vertex comparisons verify the dynamic program; all binary populations of the unequal-size toy frame are checked against exact two-stage variance/coverage; within-group bounds are checked over every binary toy population. Other checks cover census, invalid sizes, bounded-memory fallback, retained empty sets and use of HT draws only.

## Files and next steps

Each allocation contains `stratum-bounds.csv`, `bound-summary.csv`, `bound-draws.csv` and `bound-manifest.json`. All **4,800 HT confidence sets** across the two allocations are retained. Source draw/manifest/frame/group hashes, script/dependency hashes, dynamic-program method counts and output hashes are recorded and verified. All performance/final-method eligibility flags remain false.

Next compare pre-specified group/within-group quotas and size-sensitive allocations, using the identified high-contribution cells; then test stronger boundary-aware intervals, new stress populations, correlated nonresponse and reviewer error. Width and reviewer effort must be judged alongside coverage. Current constructor/alias/identity failures cannot be dropped to create complete binary data.

Reproduce from the project root with new output directories:

```sh
.venv/bin/python scripts/finite_population_bounds.py \
  --uncertainty-dir study/sampling-uncertainty-2026-10-23/groups-3 \
  --frame-dir study/sampling-design-2026-10-23 \
  --occurrences /tmp/ansibleguard-overlap-repair-2026-10-23/aggregate/all-internal-source-occurrences.csv \
  --output-dir /tmp/ansibleguard-bound-REPLAY-3
```

Repeat with `groups-5` and a different output path. See the [methodology](../../docs/study/sampling-methodology-2026-10-23.md) and [running log](../../docs/study/recovery-progress.md).
