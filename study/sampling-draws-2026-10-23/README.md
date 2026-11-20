# Calibration probability draws and design checks — 2026-10-23

These are development draws from the existing frozen population. They select
identifiers and source locations only. All retrieval and label states remain
pending. They are not final evaluation samples or fresh agreement pilots;
prior item reuse has not been filtered. No source context, reviewer label or
model output was used to choose examples.

## Draws

The common population is the calibrated repository partition of
`v0071-rerun-2026-10-22`, using the audited canonical-provider allocation.

| Draw | Eligible occurrences | Selected | Repositories represented | Rules | Maximum groups per size stratum |
|---|---:|---:|---:|---:|---:|
| `required/` | 59,891 | 861 | 125 | 51 | 3 |
| `required-more-groups/` | 59,891 | 1,266 | 131 | 51 | 5 |
| `uncertainty/` | 38,000 | 88 | 41 | 4 | 3 |
| `optional-policy/` | 90,542 | 116 | 48 | 6 | 3 |

The two required draws are alternative workloads, not additive samples.
The other instruments have separate populations and interpretations. No
review workload has been approved by the statistical acceptance gate.

The 861-case required draw contains 804 CONFIRMED, 23 EXPOSED, 20 UNRESOLVED
and 14 ORDERED_CONFLICT occurrences. Those are detector states, not validated
human judgments.

## Selection contract

1. Verify all four audited frame outputs and the exact source CSV hash.
2. Retain only the calibration partition and the specified instrument.
3. Form cells by native rule, policy, certainty, resolution state and scope.
4. Within cells, use frozen repository-size quartiles. Sample repository
   groups uniformly without replacement, then up to two occurrences uniformly
   within each selected group. A cell with at most 30 occurrences is censused.
5. Retain sparse size bins explicitly; select every group when there are
   fewer groups than the configured first-stage quota.
6. Store `pi = (selected_groups / population_groups) * (group_sample / group_population)`
   and `sampling_weight = 1 / pi` for each selected occurrence.

Group membership defaults to repository identity. Shared-content independence
is unverified. An explicit map can pool all members of a group before stage 2;
its size stratum is the maximum frozen size quartile among its members. A map
must cover the frame and may not cross dataset partitions. Supplying a map
does not certify its review status.

`selection-ledger.csv` is an analysis artifact. Keep its weights, detector
state and design metadata out of blinded reviewer forms. It records source
identity, selection probabilities, the source anchor, and pending retrieval
and label states. No item is dropped because it is hard to retrieve.

`sampling-plan.csv` records all selected-population strata and their expected
workload. Achieved draw sizes can differ from expectations because some
selected groups have fewer than two occurrences. The base required design
expects 850.62 items; the larger design expects 1,274.70. Quotas are not
adjusted after drawing to force a particular total.

Each `selection-manifest.json` records design, seed, Python version, frame,
source/group-map/script hashes, output hashes and calibration-only scope.
The writer refuses to overwrite an existing draw directory.

## Reproduction

With the original aggregate CSV extracted, run from the project root:

```sh
.venv/bin/python scripts/sample_partitioned_occurrences.py \
  --frame-dir study/sampling-design-2026-10-23 \
  --occurrences /path/to/extracted-run/aggregate/all-internal-source-occurrences.csv \
  --instrument required \
  --groups-per-stratum 3 --occurrences-per-group 2 --census-at 30 \
  --seed recovery-two-stage-20261023-v1 \
  --output-dir /tmp/calibration-required-new-draw
```

Use `--groups-per-stratum 5` for the larger alternative, or change the
instrument to `uncertainty` / `optional-policy`. Use a distinct output
directory for each invocation. This version deliberately has no option to
draw final evaluation or old-heldout examples.

## Simulation

The two `simulation-required*` directories compare these designs on planted
finite binary populations: six scenarios, 400 repeated draws per scenario,
four point estimators. The same first-stage selection kernel is used; the
within-group outcome count is drawn from the exact hypergeometric law of
sampling without replacement. Shared group effects and size correlation
are modeled. The truth populations are fixed within each scenario.

```sh
.venv/bin/python scripts/simulate_partitioned_sampling.py \
  --frame-dir study/sampling-design-2026-10-23 \
  --occurrences /path/to/extracted-run/aggregate/all-internal-source-occurrences.csv \
  --instrument required --groups-per-stratum 3 \
  --seed recovery-design-check-20261023-v1 --replications 400 \
  --output-dir /tmp/calibration-required-new-simulation
```

Use five groups for the larger comparison. Runtime for this recorded check
was Python 3.14.8; the manifests record NumPy and script versions.

See [SIMULATION.md](SIMULATION.md) for outcomes and limits. These are synthetic
design diagnostics, not measured tool accuracy. Confidence intervals,
reviewer error, nonresponse, classification error and final population
independence have not been validated by this simulation.

## Remaining gates

- Review the claim and repository/exposure/group registry.
- Choose allocation and estimator using a broader simulation suite, including
  interval coverage and retrieval failures; three/five groups are comparison
  configurations, not a statistical acceptance decision.
- Implement exact-snapshot, rule-specific evidence packets and preserve
  retrieval failures in the ledger.
- Define prior-item exclusions for a fresh agreement pilot and freeze its
  selection design before labeling.
- Validate independent reviewer instruments and final evaluation eligibility.

Implementation: [sampler](../../scripts/sample_partitioned_occurrences.py),
[simulation](../../scripts/simulate_partitioned_sampling.py).
Methodology and change history: [sampling methodology](../../docs/study/sampling-methodology-2026-10-23.md),
[recovery progress](../../docs/study/recovery-progress.md).
