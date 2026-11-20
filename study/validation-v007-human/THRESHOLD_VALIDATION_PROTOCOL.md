# V0.0.7 threshold validation protocol

## Scope and gate

Threshold observations used to choose detector thresholds are calibration data, not final heldout evidence. Regenerate split-safe threshold batches only after agreement-pilot closeout and codebook freeze. Do not edit, relabel, or treat historical threshold reviewer files as labels for this validation study.

The existing full-corpus `study/threshold-benchmark-v007/observations.csv.gz` is the population input, not a reviewer sample. Its SHA-256 is `3f4b35e1e0fbe7751ac394b1ce9113329f2548a8a071a50f166ee99f3765edb8`. The manifest records 2,986,459 observations, 24 metrics, and 207 projects. A read-only audit joined each observation's `(project, commit_sha)` to `study/runs/v007-full-repro-2026/tables/repository-execution-status.csv`: all 207 projects matched and there were zero commit mismatches. All 206 repositories in the frozen split have observations (144 calibration, 62 heldout); the one extra project is `encapsulate-xyz/cosmos-ansible`, the run timeout, and is excluded from both validation splits.

The older benchmark manifest points to `study/runs/v007-207/input/repositories.csv`, which is not present in this checkout. The retained observations and current frozen-run status table provide the verified split/commit join instead. If either source hash or commit join changes, stop and re-audit before preparing threshold batches.

The reproducible preflight is `scripts.audit_v007_threshold_source`. Its current `THRESHOLD_SOURCE_AUDIT.md` reports PASS: 2,986,459 rows, 24 mapped metrics, 13 human-condition families, all 207 project commits joined, zero mismatches, all 206 split repositories present, and the timeout as the sole out-of-split project. The machine-readable result is `threshold-source-audit.json`; the exact condition map is checksummed in that report. Re-run the audit after any source, split, run-status, or condition-map change:

```sh
.venv/bin/python -m scripts.audit_v007_threshold_source
```

This audit checks identity/schema only. It does not emit calibration or heldout samples and does not interpret metric values/predictions or import prior labels.

Historical files under `study/threshold-benchmark-v007/**/review-sample.csv` and `review-labels.csv` remain preserved as historical benchmark artifacts. They may contain prior human judgments from a different design; they must not be copied into V0.0.7 calibration or heldout labels. The new batches must be regenerated from the population observations after filtering by the frozen repository split.

## Human-condition deduplication

`threshold-human-condition-map.csv` maps all 24 threshold metrics to 13 human-condition families, their source-object unit, and stable object-key fields. It follows the production metric inventory and the observed `unit` values in `observations.csv.gz`. A human decision can be reused across metrics only when both the human-condition family and frozen object identity agree. Different conditions on the same file/task remain separate human questions.

The metric-to-condition mapping intentionally keeps these condition groups distinct: large task, long task name, inconsistent naming, long statement, complex expression, excessive nesting, missing abstraction, undocumented complex task, large play, large playbook, high coupling, playbook cohesion, and complex playbook. The multi-metric groups are: complex-expression score/length; all three large-play measurements; all five large-playbook measurements; both high-coupling measurements; both naming-special-character measurements; and all three undocumented-complexity branches.

## Calibration and heldout rules

After pilot closeout:

1. Verify `observations.csv.gz` against its pinned checksum and re-join every project/commit to the frozen run and split. Filter calibration batches to the 144 calibration repositories only. Exclude the timeout and any row not belonging to the frozen analyzed population.
2. Deduplicate human workload by `(human_condition_id, project, commit_sha, path, unit, source_ordinal)`; for `unit=line`, use the source `line` as the object anchor. Preserve the originating metric IDs as memberships. Do not merge distinct conditions because they share a file or task.
3. Freeze all source-object batches, metric memberships, selection probabilities, sampling weights, and stopping criteria before opening labels. Use the exact sampling specification's staged design: Batch 1 targets 150 unique objects per condition when available, Batch 2 the next 150, and Batch 3 the remaining reserve. The batch-specific source populations and inclusion probabilities must be recorded.
4. Threshold labels that influence a cutoff belong to calibration only. A stopping rule must be written into the batch manifest before reviewers see Batch 1; do not expand a batch based on favorable labels.
5. Do not select or open heldout threshold objects until detector, thresholds, codebooks, mapping, and calibration decisions are frozen. Then draw only from the 62 heldout repositories and treat those labels as final evaluation, never as tuning data.

Each underlying source object is labeled once per human-condition family. When several metrics share a decision, their metric memberships point to that same item; do not duplicate a label or count it more than once in an estimator. Metric-specific performance is scored only when the mapped human condition is genuinely the same. Any metric without a defensible human-condition mapping is reported as not human-validated rather than assigned a proxy label.

## Required future outputs

After the gate, create split-specific threshold populations and frozen batch artifacts under `samples/thresholds/` with manifests and checksums. Reviewer A and B receive identical evidence/IDs with independent blank decision columns; AI-shadow stays separate until adjudicated human gold is frozen. Every batch must identify its source population, metric memberships, condition/object identity, split, seed, sample size, inclusion probability, weight, and reserve/batch number. No historical reviewer labels are imported.
