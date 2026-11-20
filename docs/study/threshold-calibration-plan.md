# Numeric Threshold Calibration and Agreement Plan

## Purpose

This plan defines how AnsibleGuard's numeric detector thresholds will be
calibrated and validated on the selected real-world repository corpus. It also
separates three different questions that must not be conflated:

1. How are metric values distributed in real Ansible code?
2. Which threshold gives the preferred precision/recall trade-off against
   independent human judgments?
3. How closely does an LLM acting as an Ansible reviewer agree with the human
   gold standard?

The procedure begins with `large-task` because its current 15-line cutoff has
the highest observed candidate rate among the audited numeric detectors. The
same procedure will then be applied to every detector governed by a meaningful
numeric cutoff.

## Current evidence

The existing sensitivity audit examined 31,919 production Ansible files and
reported that `large_task` flags approximately 20.94% of the population at the
current threshold of 15, compared with 32.38% at 10 and 14.38% at 20.

These are candidate rates, not precision estimates. They show how much output
a threshold produces, but not whether the findings are correct. The current
validation labels were not allocated across alternative threshold values, so
they cannot be reused to claim threshold-specific precision, recall, or F1.

Relevant existing components are:

- `scripts/audit_experimental_thresholds.py` for candidate-rate sensitivity;
- `scripts/prepare_manual_validation.py` for two-reviewer ledgers and Cohen's
  kappa;
- `scripts/calibrate_detectors.py` for TP, FP, TN, FN, precision, recall, and
  F1 calculations;
- the v0.0.5 threshold-justification and validation reports (removed from
  the working tree; recoverable from Git history, see `docs/README.md`) for
  the earlier sensitivity and LLM-assisted validation evidence.

### v0.0.7 pre-benchmark readiness gate

The first 207-repository execution is diagnostic evidence, not the final
benchmark. Before human sampling begins, the following gates must be satisfied:

- preserve failed repositories as missing observations rather than converting
  them to zero findings;
- keep internal static-source, ansible-lint, whole-repository GitLeaks, and
  Git-history review populations separate;
- calculate selected-YAML-LOC rates only for internal and ansible-lint output;
- restrict cross-provider comparisons to repositories where the relevant
  providers completed;
- report semantic `concept_id` totals as well as compatibility `rule_id`
  totals;
- retain uncertain findings as a separate review stratum;
- freeze a clean Git commit, container image identity, manifest hashes, tool
  versions, and configuration before producing publication evidence.

The diagnostic run found one repository timeout and optional ansible-lint
partial results. Those are completeness limitations, not clean scans. Its
output also showed that a few high-volume rules dominate the corpus, so all
sampling and descriptive statistics must include repository-weighted views and
rule/concept-level outlier checks.

### Variable finding semantics

`ansibleguard/unguarded-variable` remains the stable detector/rule ID for
configuration and backward compatibility, but the backend already divides its
output into three semantic concepts:

- `missing-internal-variable`: no definition evidence or external-input
  uncertainty was found; this is the actionable correctness candidate;
- `undeclared-input-contract`: the value may be a role, playbook, or task
  fragment input, but no visible default or explicit contract was found;
- `unresolved-runtime-input`: inventory, caller context, facts, dependencies,
  dynamic includes, or another runtime source may provide the value.

The latter two are uncertain because source-only analysis cannot prove the
complete runtime variable environment. They must not be counted as confirmed
defects or silently merged with `missing-internal-variable`. Human review must
sample these concepts separately, with enough caller, defaults, inventory, and
dependency context to resolve the case where possible. Agreement and detector
metrics must report `uncertain` independently; binary metrics may use only
adjudicated TP/FP labels and must disclose excluded unresolved cases.

## Required study inputs

Before calibration starts, freeze and record:

- AnsibleGuard version and Git commit, initially the `v0.0.7` release line;
- the exact repository manifest;
- one immutable commit SHA for every repository;
- the analysis profile and configuration;
- the detector implementation and metric definition;
- the sampling seed;
- the human-review rubric version;
- the LLM model, model version, prompt, and decoding settings if the optional
  LLM comparison is run.

### Recovered corpus manifest (2026-09-17)

The authoritative `study/manifests/github-v2-final-eligible.csv` was recovered
from contributor commit `df69e9345cfa2d45947ba7bba224a8f27c0d0c00` and verified
to contain 207 unique repositories with frozen commit SHAs. It is now the
selected corpus. The old 149-repository manifest is preserved for historical
reproduction. There are 133 repositories common to the old and new lists.

`scripts/materialize_207.py` reuses existing clean clones and fetches missing
commits. It checks out each exact manifest SHA and records local paths and
outcomes in `study/manifests/github-207-local-frozen.csv`. Newly fetched history
is shallow; history-dependent studies must obtain sufficient history separately.

The following records the gap before the manifest was pushed and recovered.

### Historical corpus-manifest gap

The study reports state that the final corpus contains 207 repositories and
identify `study/manifests/github-v2-final-eligible.csv` as the 207-row output.
At the initial inspection, that file was absent from the working tree and
reachable Git history.

The available files are not equivalent replacements:

- `study/manifests/github-candidates-v2-final.csv` currently has 149 rows with
  `final_eligible=true`;
- the locally ignored `study/manifests/github-v2-final-frozen.csv` also has
  149 repositories;
- `study/repositories/` currently contains 302 repository directories.

At that point, the exact 207-repository list needed to be recovered from the machine or
artifact location used for the v0.0.5 empirical run, or reproducibly
regenerated from the recorded selection inputs. Calibration must not infer the
207 by arbitrarily selecting from the 302 local clones.

Once recovered, the authoritative manifest must be preserved with at least:

- `project`;
- source and clone URLs;
- frozen `commit_sha`;
- selection status and gate evidence;
- repository family/ecosystem;
- project-size measurements;
- content fingerprint where available.

The manifest should be checksummed and stored as a release evidence artifact.

## Phase 1: inventory numeric detectors and analysis units

Create a registry for every detector with a meaningful numeric threshold. For
each detector record:

- stable rule/concept ID;
- analysis unit: task, play, file, role, or repository;
- measured feature;
- comparison operator (`>`, `>=`, `<`, or `<=`);
- current default threshold;
- project-configurable override key;
- literature/domain basis, if one exists;
- known semantic confounders;
- candidate values already used in sensitivity analysis.

Pattern-based detectors without a single meaningful numeric cutoff must not be
forced into this procedure.

For `large-task`, confirm the exact measurement in code before extraction. If
the implementation uses physical task LOC, the population must contain one
record per parsed task, not one record per file.

## Phase 2: extract the population and describe its distribution

For every eligible analysis unit in every frozen repository, create a row with:

- repository and commit SHA;
- file path and source location;
- artifact/document kind;
- detector ID;
- raw metric value;
- current detector outcome;
- relevant structural context such as loops, inline variables, blocks, and
  multiline module arguments.

Produce for each detector:

- box plot;
- histogram and/or empirical cumulative distribution function;
- Q1, median/Q2, Q3, and IQR;
- current threshold overlay;
- literature/domain threshold overlays;
- candidate rate at each proposed threshold;
- per-repository distributions and repository-weighted summaries.

Repository-weighted summaries are required because a small number of very
large repositories must not dominate a task-level distribution.

The distribution is descriptive. Q1, Q2, and Q3 generate candidate thresholds;
they do not establish that any threshold represents a real smell boundary.

## Phase 3: freeze calibration and held-out repository sets

Split at the repository level so tasks from the same repository cannot appear
in both tuning and final evaluation.

The split must be stratified by available variables such as:

- project-size quartile;
- repository family/ecosystem;
- project purpose;
- Ansible artifact mix;
- production Ansible LOC;
- independence/duplicate-content group.

Repositories with identical or closely related Ansible content must remain in
the same partition. The calibration partition may be used for rubric pilots,
detector repair, and threshold choice. The held-out partition may be evaluated
only after the detector logic, rubric, and threshold-selection rule are frozen.

## Phase 4: build a threshold-independent validation sample

For each detector, divide its metric population into bands:

- below Q1;
- Q1 to Q2;
- Q2 to Q3;
- above Q3.

Add boundary strata around every serious candidate threshold, including the
current threshold. Stratify further by:

- project-size quartile;
- artifact kind;
- repository family/ecosystem;
- current detector outcome;
- structural confounders;
- provisional LLM TP/FP judgment, if available.

An LLM judgment may be used to diversify the sample, but it is not a gold
label. Human reviewers must be blind to it.

The sample must contain below-threshold cases. A sample containing only
findings can estimate precision but cannot estimate false negatives or recall.

If complete repository representation is a study requirement, select at least
one unit from each recovered repository and then oversample boundary cases,
rare strata, and suspected error mechanisms. The final sample size must be
justified by the desired confidence-interval width rather than repository count
alone.

Record each unit's inclusion probability so population-level metrics can be
weighted correctly after stratified oversampling.

## Phase 5: create and pilot the human-review rubric

The rubric must define the smell independently of the implemented threshold.
It must specify:

- the semantic property that makes an instance problematic;
- relevant source context reviewers must inspect;
- positive and negative examples;
- exclusions and confounders;
- treatment of generated code and test fixtures;
- treatment of long loops, inline data, variables, comments, blocks, and
  multiline expressions;
- when to use `uncertain` or `out-of-scope`.

Two Ansible-qualified reviewers independently label the same units as:

- `true-positive` / genuine smell;
- `false-positive` / not a smell;
- `uncertain`;
- `out-of-scope`.

Reviewers receive the relevant source context but must not see:

- the threshold value being tested;
- the detector verdict;
- the LLM verdict;
- the other reviewer's answer.

### Human-to-human agreement loop

1. Both reviewers label a balanced pilot batch independently.
2. Calculate raw agreement and Cohen's kappa.
3. If kappa is below 0.80, categorize the causes of disagreement.
4. Clarify the rubric and examples without rewriting answers to force
   agreement.
5. Label a new, previously unseen pilot batch.
6. Repeat until kappa is at least 0.80 or conclude that the concept is too
   subjective for reliable binary automation.

The Python workflow may detect completed batches and calculate agreement, but
it cannot replace the independent human judgments. Repeatedly changing labels
on the same batch until kappa reaches 0.80 is prohibited.

Because kappa is sensitive to label prevalence, report raw agreement and the
label distribution alongside it. An additional prevalence-robust agreement
measure may be reported as a sensitivity check.

After preserving the original independent labels and agreement result,
disagreements may be adjudicated by a third expert or documented consensus
meeting. The adjudicated result becomes the human gold label.

## Phase 6: score candidate thresholds

Apply every candidate threshold to the same locked human-labeled sample. At a
minimum, test:

- Q1;
- Q2;
- Q3;
- the current production threshold;
- supported literature/domain thresholds;
- nearby values in the promising range.

For every threshold calculate:

- TP, FP, TN, and FN;
- precision;
- recall;
- specificity;
- F1;
- F0.5 when false-positive avoidance has priority;
- candidate rate;
- 95% confidence intervals.

Use sampling weights for corpus estimates and repository-clustered bootstrap
confidence intervals to account for multiple units coming from the same
repository.

### Threshold selection rule

Do not select the threshold with the highest precision alone. A threshold that
emits one obvious finding may have perfect precision but unusable recall.

Before inspecting candidate results, predeclare an objective such as:

> Select the threshold with the highest F0.5, provided precision is at least
> 85% and recall is at least 70%.

The exact objective and minimum acceptable precision/recall values must be
agreed and frozen before threshold results are revealed. Report the complete
trade-off table even after selecting a threshold.

## Phase 7: repair detector logic before hiding errors with a threshold

Every false positive and false negative should be assigned an error mechanism.
For `large-task`, candidate mechanisms include:

- long `loop`/`with_items` data;
- large inline `vars` blocks;
- multiline module arguments;
- comments or formatting inflating physical LOC;
- generated or repetitive content;
- incorrect task-boundary parsing;
- valid Ansible structures that are long but not complex;
- genuinely overloaded tasks missed by a simplistic LOC measure.

If many errors share a semantic mechanism, correct the detector logic rather
than merely raising the threshold. Add a regression test for every repaired
mechanism.

After a logic change:

1. rerun the calibration set;
2. regenerate distributions if the measured feature changed;
3. rescore thresholds;
4. keep the held-out test set sealed.

## Phase 8: final held-out evaluation

Freeze:

- detector code;
- chosen threshold;
- configuration;
- review rubric;
- scoring script;
- analysis exclusions.

Run the held-out repositories once. Report threshold-specific precision,
recall, F1/F0.5, candidate rate, confidence intervals, and repository-level
variation. Do not continue adjusting the detector against held-out failures;
those become future-work observations or inputs to a new study iteration.

## Phase 9: optional human-to-LLM agreement experiment

An LLM is not needed to choose or score numerical thresholds.
Threshold scoring is deterministic Python over metric values and human gold
labels.

An LLM may instead be evaluated as a separate reviewer after the human gold
standard is locked:

1. freeze one Ansible-expert prompt and model version;
2. give the model the same source context and rubric available to humans;
3. hide detector, threshold, and human judgments;
4. run it on the locked human-labeled sample;
5. compare its labels with the adjudicated human gold standard;
6. report human-to-LLM agreement, kappa, precision, recall, F1, uncertainty,
   and failure categories.

A versioned API/model call or
other reproducible inference interface is preferable because the exact prompt,
model, inputs, and outputs can be archived. The LLM must not adjudicate its own
labels or be presented as human ground truth.

## Required implementation artifacts

The implementation should produce or extend the following components:

1. A numeric-detector registry.
2. A population extractor producing one row per detector analysis unit.
3. A distribution/box-plot generator.
4. A deterministic repository-level split generator.
5. A stratified threshold-validation sampler with inclusion probabilities.
6. A versioned human-review rubric and reviewer packets.
7. An agreement calculator that preserves every pilot result.
8. A weighted threshold scorer with confidence intervals and clustered
   bootstrap support.
9. An error-mechanism report for detector repair.
10. An optional blinded human-to-LLM comparison runner.
11. A machine-readable final report containing all candidate thresholds, not
    only the selected value.

Every generated artifact must record input hashes, code commit, random seed,
configuration, and creation time.

## Acceptance criteria

Calibration is complete for a detector only when:

- the exact frozen repository corpus is available and checksummed;
- the detector's population and metric definition are reproducible;
- candidate distributions and thresholds are recorded;
- two independent humans reach kappa >= 0.80 on a fresh pilot batch, or the
  detector is explicitly classified as too subjective;
- the main labels are independently produced and adjudicated;
- threshold metrics use both positive and negative review units;
- the selection objective was declared before inspecting results;
- recurring semantic errors were repaired and regression-tested;
- the selected detector/threshold was evaluated once on held-out repositories;
- limitations and any LLM assistance are disclosed explicitly.

## End-to-end flow

```text
Recover and freeze the exact 207-repository manifest
                         |
                         v
Extract one metric row per detector analysis unit
                         |
                         v
Plot distributions and derive candidate thresholds
                         |
                         v
Create repository-level calibration and held-out sets
                         |
                         v
Sample across metric bands, repositories, and confounders
                         |
                         v
Two independent human reviewers on blinded source context
                         |
                         v
Fresh pilot batches until kappa >= 0.80; then lock rubric
                         |
                         v
Adjudicate labels and score all thresholds on calibration data
                         |
                         v
Repair semantic detector errors and rerun calibration
                         |
                         v
Select threshold using the predeclared F0.5/F1 constraints
                         |
                         v
Evaluate once on the held-out repositories
                         |
                         v
Optionally compare a frozen LLM reviewer with human gold labels
```
