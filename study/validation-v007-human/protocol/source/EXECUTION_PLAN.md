# Luna 6 XHigh — AnsibleGuard v0.0.7 Human Validation Execution Plan

## Mission

Work on:

- Repository: `JedidiAymen/AnsibleChecklist`
- Current working branch to inspect first: `chore/v007-reproducible-full-run`
- Branch head observed when this handoff was written: `cb304a52bb8fcc4db12f58aa8c44f53e4411ef18`
- Study/run identity: `v007-full-repro-2026`
- Tool version: `0.0.7`

Create and execute the complete **human-validation preparation and validation infrastructure** for the v0.0.7 study.

This task is not “make one CSV with some random findings.”

The purpose is to build a defensible validation design that supports:

1. real-world weighted precision;
2. per-rule precision;
3. semantic-concept precision;
4. practical actionability;
5. human inter-reviewer agreement;
6. source-first recall where a valid negative/candidate universe exists;
7. numerical-threshold calibration without contaminating final evaluation;
8. final held-out evaluation after code/thresholds are frozen;
9. blinded AI-vs-human comparison;
10. full reproducibility of all sampling and statistics.

The validation must remain scientifically honest.

**Never fabricate human labels.**
**Never put AI labels into human-review columns.**
**Never call Luna/AI labels “human validation.”**
**Never tune on the held-out final repositories.**

---

# 0. Core principle

The current detector output is extremely imbalanced.

The current run includes 65 observed AnsibleGuard rule IDs, with a few rules dominating the internal population. Important examples include:

- `ansibleguard/missing-tags`: 98,005
- `ansibleguard/unguarded-variable`: 52,474
- `ansibleguard/variable-naming-convention`: 24,121
- `ansibleguard/large-task`: 12,179
- `ansibleguard/complex-expression`: 11,003
- `ansibleguard/unnamed-task`: 10,244

Therefore:

```text
one simple random sample
    -> represents overall user exposure
    -> but barely validates rare rules

one equal-per-rule sample
    -> covers rare rules
    -> but biases overall precision
```

The validation must use a **hybrid probability design**:

```text
representative occurrence-level core
        +
rule-balanced top-ups
        +
special semantic/risk strata
        +
rare-rule censuses
```

Every sampled row must preserve its selection probability and sampling weight.

---

# 1. Do not start human labeling until the validation source is clean

Before creating final human samples, inspect the investigation material already added to the branch and the current result package.

At minimum inspect:

- `ANSIBLEGUARD_V007_FULL_RUN_INVESTIGATION_REPORT.md`
- `ANSIBLEGUARD_EXTERNAL_TOOL_MAPPING_STARTER.csv`
- `FULL_RUN_REPORT.md`
- `report/FULL_STUDY_REPORT.md`
- `aggregate/all-canonical-occurrences.csv`
- `aggregate/all-internal-source-occurrences.csv`
- `aggregate/rule-summary.csv`
- `aggregate/concept-summary-internal.csv`
- `aggregate/resolution-summary.csv`
- `aggregate/repository-summary.csv`
- `aggregate/provider-health.csv`
- `tables/repository-execution-status.csv`
- `study/threshold-benchmark-v007/PROTOCOL.md`
- `study/threshold-benchmark-v007/LABELING_CODEBOOK.md`
- `study/threshold-benchmark-v007/START_HERE_FILE_MAP_AND_PLAN.md`

Also inspect current GitHub CI and the implementation that generates the study/reporting artifacts.

## 1.1 Pre-validation cleanliness gate

The validation sampling code must use **authoritative aggregate data**, not the known-bad helper chart tables.

The following previously identified reporting issues must either be fixed first or explicitly isolated so they cannot contaminate the validation samples:

- short rule ID versus canonical provider-prefixed rule ID mismatch;
- failed repository coerced to zero;
- density charts mixing incompatible populations;
- overlapping provider-completeness categories;
- misleading `uncertain vs actionable` chart;
- external-overlap zero bar meaning "not modeled";
- tautological sanity check containing `or True`;
- stale generated rule documentation/catalog;
- environment metadata inconsistencies.

**Do not change detector semantics merely to fix reporting.**

If reporting fixes can be regenerated from frozen raw outputs, do that instead of rerunning 207 repositories.

Create:

`study/validation-v007-human/PRE_VALIDATION_GATE.md`

It must state:

```text
source run
source commit(s)
authoritative occurrence file
number of analyzable repositories
number of internal static occurrences
number of AnsibleGuard rules included
known exclusions
reporting defects fixed
reporting defects still outstanding
CI status
```

Do not generate the frozen human sample until this gate is explicit.

---

# 2. Work on a dedicated branch

Create a new branch from the latest verified reproducibility branch head.

Suggested branch:

```text
study/v007-human-validation
```

Record the actual parent SHA.

Do not silently base this work on an old local branch.

Keep commits logically separated, for example:

```text
study: define v007 human validation protocol
study: freeze calibration and heldout repository split
study: add validation codebooks and schemas
study: generate agreement pilot
study: generate representative precision sample
study: add rule-balanced and semantic topups
study: prepare source-first recall panels
study: prepare threshold validation batches
study: add blinded reviewer workbooks
study: add AI shadow review pipeline
study: add agreement and scoring scripts
study: document human handoff
```

Push the branch and every frozen CSV/manifest/codebook that is meant to be shared.

---

# 3. Freeze a deterministic repository-level calibration / held-out split

Use only the **206 analyzable repositories** for detector-quality validation.

The one repository with no core AnsibleGuard result remains in execution-reliability reporting but cannot contribute to precision/recall.

Create:

```text
study/validation-v007-human/splits/repository-split.csv
```

Target:

```text
calibration/development: 144 repositories
heldout/final:            62 repositories
total:                   206 repositories
```

That is approximately 70/30.

## 3.1 Split at repository level

Never split individual files/findings from one repository across calibration and held-out sets.

If:

```text
repository A -> calibration
```

then every finding and source-first candidate from A is calibration-only.

If:

```text
repository B -> heldout
```

then every item from B is heldout-only.

## 3.2 Deterministic seed

Freeze a seed such as:

```text
v007-human-validation-20261005
```

Record it in a manifest.

Never use unseeded random sampling.

## 3.3 Balance the split

Do not simply shuffle 206 names and take 62.

Stratify/balance using as much trustworthy information as available, including:

- repository selected YAML LOC;
- selected file count;
- internal finding count/density;
- major rule-presence vector;
- repository family/ecosystem if derivable without subjective guessing;
- presence of rare/high-risk rules where feasible.

The objective is to make calibration and held-out distributions broadly comparable while still preserving a true held-out partition.

Generate:

```text
repository-split.csv
repository-split-summary.csv
repository-split-balance.md
repository-split-manifest.json
```

The manifest must contain:

```text
seed
source hashes
algorithm
calibration count
heldout count
SHA256 of split CSV
```

## 3.4 Do not optimize the split using human labels

No human labels exist when the split is frozen.

Do not later move repositories because their labels are difficult or because detector precision looks poor.

---

# 4. Separate validation panels

Do not create one scientifically ambiguous master question.

Create distinct panels.

At minimum:

```text
A. static precision
B. review/history precision
C. source-first recall
D. threshold calibration
E. final held-out evaluation
F. external-provider normalization/overlap
G. AI-shadow comparison
```

All may have a shared row identity system, but they must remain distinguishable.

Recommended root:

```text
study/validation-v007-human/
├── README.md
├── PROTOCOL.md
├── VALIDATION_STATUS.md
├── PRE_VALIDATION_GATE.md
├── manifests/
├── splits/
├── codebooks/
├── samples/
│   ├── agreement-pilot/
│   ├── calibration/
│   ├── recall/
│   ├── thresholds/
│   └── heldout/
├── reviewers/
│   ├── reviewer-a/
│   ├── reviewer-b/
│   └── ai-shadow/
├── adjudication/
├── results/
├── scripts/
└── checksums/
```

---

# 5. Human label model

The human gold-standard question must not be reduced to one TP/FP checkbox.

For emitted findings, collect at least two independent judgments.

## 5.1 Semantic label

Allowed values:

```text
positive
negative
uncertain
unreviewable
```

Meaning:

### positive

The documented underlying condition genuinely exists in the frozen source/repository context.

For an emitted finding this becomes a true positive.

### negative

The documented condition is not present.

For an emitted finding this becomes a false positive.

### uncertain

A reasonable expert cannot decide from static repository evidence because runtime/external/project context is genuinely required.

Do not silently treat uncertain as false.

### unreviewable

The source/context bundle is missing, corrupt, incomplete, or structurally unusable.

This is a validation-data failure, not a detector false positive.

## 5.2 Actionability label

Allowed values:

```text
blocking
actionable
advisory
not-actionable
uncertain
not-applicable
```

This measures practical usefulness separately from semantic correctness.

Example:

```text
missing-tags:
semantic_label     = positive
actionability      = not-actionable
```

can be a valid outcome if the task truly has no explicit/inherited tag but the repository does not need selective tag execution.

## 5.3 Context sufficiency

Also collect:

```text
context_sufficient = yes/no
requires_external_context = yes/no
```

## 5.4 Controlled reason codes

Create a codebook rather than relying only on free text.

Suggested negative reason codes:

```text
predicate-not-satisfied
context-refutes-detector-assumption
valid-project-convention
external-or-runtime-value-resolves
wrong-source-object
duplicate-or-alias
policy-not-applicable
threshold-not-semantically-problematic
other
```

Suggested uncertain codes:

```text
external-inventory-required
runtime-variable-required
dynamic-include-or-lookup
missing-collection-context
missing-role-context
repository-policy-ambiguous
source-context-insufficient
other
```

Keep a free-text `reviewer_notes` column as well.

---

# 6. Family-specific review questions

Do not use the same wording for all 65 rules.

Create family codebooks.

At minimum use families similar to:

```text
1. objective correctness
2. variable/reference reasoning
3. security
4. style/policy
5. maintainability/complexity
6. structure/reuse
7. review/history
```

Map every AnsibleGuard rule to one primary validation family.

Examples:

### Objective correctness

- invalid-task-attribute-type
- invalid-numeric-value
- duplicate/overridden key
- missing-handler

Question style:

> Does the frozen source actually violate the documented correctness condition?

### Variable/reference reasoning

- unguarded-variable
- variable-use-before-definition
- unscoped-shell-variable
- role-variable-precedence-collision

Question style:

> Given all statically available repository evidence, what is the strongest supported variable/reference state?

### Security

- insecure-permissions
- plaintext-sensitive-variable
- missing-validate-certs
- default-credentials
- credentials-leaking-in-log
- unsafe-file-write

Question style:

> Is the documented security risk present in the available source context, and is remediation justified?

### Style/policy

- missing-tags
- variable-naming-convention
- long-statement
- long-task-name
- inconsistent-naming-convention

Question style must explicitly distinguish:

```text
predicate is true
```

from:

```text
policy is useful/actionable in this repository
```

### Maintainability/complexity

- large-task
- large-play
- large-playbook
- complex-expression
- high-coupling
- excessive-nesting

Question style:

> Does this source unit genuinely exhibit the maintainability condition independent of the numerical cutoff?

### Structure/reuse

- missing-abstraction
- duplicated-code
- unnecessary-abstraction
- unstructured-module
- role-readme-absent

### Review/history

- missing-release-note
- commit-message-format
- missing-bug-reference
- missing-test-update
- untested-override-change

These require Git/diff context rather than only YAML context.

Create:

```text
codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md
codebooks/FAMILY_VARIABLES.md
codebooks/FAMILY_SECURITY.md
codebooks/FAMILY_STYLE_POLICY.md
codebooks/FAMILY_MAINTAINABILITY.md
codebooks/FAMILY_STRUCTURE.md
codebooks/FAMILY_REVIEW_HISTORY.md
codebooks/RULE_OVERRIDES.md
```

`RULE_OVERRIDES.md` must document rules whose decision criteria differ materially from their family.

---

# 7. Agreement pilot comes before primary human labeling

Before humans label the primary sample, create a separate pilot.

Target:

```text
~50 cases per codebook family
~7 families
≈350 pilot cases
```

Use calibration repositories only.

Do not use held-out repositories.

Do not reuse these rows later as final performance rows.

Generate:

```text
samples/agreement-pilot/agreement-pilot-master.csv
reviewers/reviewer-a/agreement-pilot.csv
reviewers/reviewer-b/agreement-pilot.csv
samples/agreement-pilot/agreement-pilot-manifest.json
```

Both human reviewers must label every pilot row independently.

They must not see:

- each other's answers;
- AI answers;
- detector confidence;
- detector severity unless essential to understand rule semantics;
- rule frequency;
- sampling weight;
- population prevalence.

After both human pilot files are complete, compute:

```text
raw agreement
Cohen's kappa
Gwet's AC1
positive-specific agreement
negative-specific agreement
uncertain-specific agreement
label prevalence
confusion matrix
```

Target:

```text
Cohen's kappa >= 0.80
```

but do not use kappa alone. Inspect AC1, prevalence and label-specific agreement.

If agreement is poor:

```text
inspect disagreements
revise codebook
draw NEW pilot rows
repeat
```

Do not tune the codebook repeatedly on the final primary sample.

Keep every pilot round.

---

# 8. Static precision sampling design

This is the central emitted-finding validation.

Use only AnsibleGuard-owned **internal static-source occurrences** for this panel.

Do not mix in:

- ansible-lint findings;
- GitLeaks provider findings;
- Git-history/review rules.

## 8.1 Layer A — representative core

From the full internal static occurrence population, draw:

```text
1,000 unique occurrences
```

using a reproducible probability sample.

This core exists to estimate real-world occurrence-weighted precision.

Do not make it equal-per-rule.

Preserve:

```text
population size
selection probability
sampling weight
seed
stratum
```

## 8.2 Layer B — rule-balanced top-ups

After the 1,000 representative rows are selected, calculate how many examples each rule already has.

Top up only the rules that are below their minimum target.

Use:

| Rule population | Minimum final human sample for that rule |
|---:|---:|
| >20,000 | 100 |
| 5,000–19,999 | 75 |
| 1,000–4,999 | 60 |
| 200–999 | 45 |
| 51–199 | 30 |
| ≤50 | census all findings |

The representative-core rows count toward these targets.

Do not blindly add the full target on top of the representative core.

## 8.3 Rare rules

If a rule has `N <= 50`, include every occurrence in the relevant calibration/final population where possible.

Clearly distinguish:

```text
corpus census precision
```

from:

```text
generalization beyond this corpus
```

## 8.4 Repository diversity

Within each top-up stratum, avoid taking all samples from one repository when the rule exists across many repositories.

Use repository-aware selection.

Prefer broad repository coverage while preserving valid inclusion probabilities.

---

# 9. Special strata override generic rule sampling

Some rules require semantic stratification stronger than the volume-based rule target.

## 9.1 `unguarded-variable`

Do not validate this as one homogeneous rule.

The current semantic concepts include:

```text
undeclared-input-contract
unresolved-runtime-input
missing-internal-variable
```

Target at least:

```text
100 undeclared-input-contract
100 unresolved-runtime-input
100 missing-internal-variable
```

when enough calibration/held-out rows exist.

If a held-out stratum has fewer than the target, census it.

Preserve the concept ID in the sample.

Report precision/uncertainty separately for each concept.

## 9.2 Credential-log exposure

Stratify at least by resolution/evidence state, including:

```text
PROVEN_EXPOSED
DYNAMIC_PROTECTION_UNKNOWN
```

Target approximately 100 per sufficiently large state.

## 9.3 Security rules

For security rules, require a stronger minimum even if the generic population band would allocate fewer.

Target:

```text
75 per security rule when N >= 75
census when N < 75
```

unless a more specific semantic stratum already creates a larger sample.

## 9.4 Other multi-concept rules

Inspect `concept-summary-internal.csv` and rule metadata.

If one rule ID maps to multiple semantically different concepts, validate the concepts separately.

Do not hide concept imbalance inside one aggregate rule precision number.

---

# 10. Expected static validation size

Do not hardcode the final number because the representative core contributes to the rule minima.

The expected order of magnitude is roughly:

```text
3,000–3,500 unique internal static findings
```

after:

- 1,000 representative core;
- rule top-ups;
- rare-rule censuses;
- semantic/security overrides.

The actual frozen count must be computed from the current authoritative data and documented.

Create:

```text
samples/calibration/static-precision-master.csv
samples/calibration/static-precision-allocation.csv
samples/calibration/static-precision-manifest.json
```

The allocation file must list every rule and:

```text
population_N
representative_core_n
generic_target_n
special_target_n
final_unique_n
repository_count_in_sample
sampling_strategy
```

---

# 11. Separate review/history panel

Do not mix Git-history rules into static-source precision.

Create a separate review-history sample.

The current review-only population is small enough that a substantial fraction can be reviewed.

Rules include at least:

```text
missing-release-note
commit-message-format
missing-bug-reference
missing-test-update
untested-override-change
```

Use the correct evidence bundle:

```text
commit SHA
commit message
diff
changed files
relevant release-note/test paths
nearby history context where required
```

Create separate reviewer CSVs.

---

# 12. Human reviewer files

Humans must never edit the immutable master sample.

For every human panel, create two identical reviewer workbooks with decision columns blank.

Example:

```text
reviewers/reviewer-a/static-precision.csv
reviewers/reviewer-b/static-precision.csv
```

The two files must contain identical `sample_id` ordering and identical source/context fields.

They must NOT contain the other reviewer's decision columns.

They must NOT contain Luna's AI labels.

## 12.1 Human reviewer CSV schema

Recommended visible fields:

```text
sample_id
panel
rule_id
concept_id
review_family
review_question

repository
commit_sha
path
line_start
line_end
object_kind
object_id

source_context
context_bundle_path

semantic_label
actionability_label
context_sufficient
requires_external_context
reason_code
reviewer_notes
```

Decision columns are blank at generation time.

## 12.2 Hidden/non-review fields

Keep these in the master file but omit them from the blinded reviewer files when not required:

```text
selection_probability
sampling_weight
rule_population
rule_prevalence
detector_confidence
detector_severity
detector certainty if it biases the question
other reviewer's answer
AI answer
```

For threshold panels also hide:

```text
current detector prediction
current threshold
candidate thresholds
```

when the human question can be judged without those values.

---

# 13. Human review instructions

Create:

```text
HUMAN_REVIEWER_A_INSTRUCTIONS.md
HUMAN_REVIEWER_B_INSTRUCTIONS.md
```

The files should be substantively identical except reviewer identity.

They must explain, slowly and concretely:

1. what `positive`, `negative`, `uncertain`, `unreviewable` mean;
2. what the actionability scale means;
3. how to inspect full source context;
4. when repository-wide search is permitted/required;
5. when external/runtime context makes a case uncertain;
6. not to infer correctness from AnsibleGuard's message;
7. not to use the other reviewer's decisions;
8. not to use Luna's AI-shadow labels;
9. not to use ansible-lint/GitLeaks as the human answer unless the codebook explicitly asks for external comparison;
10. how to write a short evidence-based reason;
11. how to save/push the CSV without changing row IDs/order.

Also create:

```text
HUMAN_REVIEW_CHECKLIST.md
```

for a reviewer to follow per row.

---

# 14. AI-shadow dataset

The user explicitly wants Luna to create an identical review dataset and label it herself.

Do this, but preserve scientific separation.

## 14.1 Create identical AI files

For every human-review sample create a corresponding AI-shadow file:

```text
reviewers/ai-shadow/agreement-pilot.csv
reviewers/ai-shadow/static-precision.csv
reviewers/ai-shadow/review-history.csv
reviewers/ai-shadow/recall-*.csv
reviewers/ai-shadow/threshold-*.csv
reviewers/ai-shadow/heldout-*.csv
```

The AI files use the same immutable `sample_id`s.

## 14.2 AI labels are never human labels

Luna must never write her answer into:

```text
reviewer-a
reviewer-b
adjudicated human
```

columns.

Use AI-specific fields:

```text
ai_semantic_label
ai_actionability_label
ai_context_sufficient
ai_requires_external_context
ai_reason_code
ai_notes
ai_confidence
ai_model_identity
ai_review_protocol_version
```

## 14.3 Blinding rule

The scientifically clean comparison requires:

```text
human codebook frozen
        ↓
human labels frozen
        ↓
human adjudication frozen
        ↓
AI blinded review
        ↓
AI-vs-human comparison
```

Therefore:

- create the AI-shadow CSV structure now;
- do not expose AI decisions to humans;
- for the formal AI comparison, run Luna's labeling only after the corresponding human gold-standard labels are frozen.

If an earlier AI pre-check is useful for verifying context bundles or schema quality, store it separately under:

```text
ai-precheck/
```

and explicitly mark:

```text
NOT PART OF THE VALIDATION RESULTS
```

Never use pre-check labels as human replacement or as final AI-vs-human comparison.

---

# 15. Human agreement and adjudication

After human reviewer files are filled:

1. validate schemas;
2. verify same sample IDs;
3. verify no rows were added/deleted;
4. calculate agreement;
5. generate disagreements;
6. preserve original human labels;
7. adjudicate.

Create:

```text
results/agreement-summary.json
results/agreement-summary.csv
adjudication/disagreements.csv
adjudication/adjudicated.csv
```

Never overwrite Reviewer A or Reviewer B.

For disagreements:

```text
reviewer_a_label
reviewer_b_label
adjudicated_label
adjudication_reason
adjudicator
```

If no genuine third human adjudicator exists, record joint human consensus as such.

Do not let Luna silently adjudicate human disagreement and then call it human consensus.

Luna may provide a **separate AI recommendation** column, but it cannot become human adjudication automatically.

---

# 16. Precision estimands

Do not publish one vague "accuracy" number.

Compute at least:

## 16.1 Weighted micro semantic precision

Represents the actual occurrence distribution.

Use inclusion probabilities / sampling weights.

## 16.2 Macro semantic precision

Each rule contributes equally.

This prevents huge rules from hiding weak rare rules.

## 16.3 Per-rule precision

With:

```text
reviewed N
positive
negative
uncertain
unreviewable
decided precision
uncertain rate
95% CI
```

## 16.4 Per-concept precision

Especially for multi-concept rules.

## 16.5 Per-category precision

At least:

```text
style
correctness
maintainability
security
compatibility
documentation
reliability
testing
structure
dependencies
```

where enough human evidence exists.

## 16.6 Per-confidence precision

```text
high
medium
low
```

## 16.7 Per-resolution/evidence-state precision

Examples:

```text
DETECTOR_RESULT
EXTERNAL_INPUT_UNCERTAIN
RUNTIME_CONTEXT_UNCERTAIN
PROVEN_EXPOSED
BOUNDED_GRAPH_UNKNOWN
CANDIDATE_MISSING
DYNAMIC_PROTECTION_UNKNOWN
PROVEN_ORDERED_CONFLICT
```

## 16.8 Actionable precision

Report practical usefulness independently from semantic correctness.

## 16.9 Human uncertain rate

This is a result, not a nuisance to hide.

Do not automatically count uncertain as FP.

---

# 17. Weighting

Because rare rules are deliberately oversampled, simple averaging of reviewed rows is invalid for population-wide precision.

Every sampled row must have:

```text
population_id
stratum_id
population_size
stratum_population_size
selection_probability
sampling_weight
```

For simple within-stratum sampling:

```text
sampling_weight = N_stratum / n_stratum
```

If the design uses multiple overlapping top-up mechanisms, calculate the actual final inclusion probability correctly rather than applying a naive duplicated weight.

Deduplicate by immutable occurrence identity before freezing the sample.

Document the exact weighting estimator in:

```text
WEIGHTING_METHOD.md
```

---

# 18. Confidence intervals

Findings from the same repository are correlated.

Do not pretend every finding is an independent Bernoulli draw.

Use repository-cluster bootstrap confidence intervals for weighted estimates.

Freeze:

```text
bootstrap seed
number of bootstrap replicates
clustering unit = repository
```

Recommended:

```text
>= 2,000 bootstrap replicates
```

unless resource constraints justify another number.

Report the method explicitly.

---

# 19. Source-first recall validation

Positive-finding precision does not measure false negatives.

Build separate recall panels only where there is a definable source universe.

Examples:

## 19.1 Variable resolution

Sample variable references from frozen source independent of whether AnsibleGuard fired.

Human label:

```text
valid/resolved
missing-internal
external-input
runtime-input
uncertain
```

Compare to detector output.

This supports recall for the concepts that have a valid candidate universe.

## 19.2 Handler references

Sample notify/listen/reference relationships, including detector negatives, where a source-first universe can be enumerated.

## 19.3 Objective structural/correctness rules

Where it is feasible to enumerate all candidate source units, build source-first negative samples.

Do not fabricate a global recall figure by combining incompatible universes.

For rules where no defensible negative/candidate universe exists, state:

```text
recall not estimated
```

Create a recall matrix:

```text
results/recall-eligibility.csv
```

Columns:

```text
rule_id
recall_estimable
candidate_universe_definition
sampling_method
reason_if_not_estimable
```

---

# 20. Threshold study integration

Reuse the good structure already present in:

`study/threshold-benchmark-v007/`

Do not discard the existing frozen samples.

The current threshold benchmark already has:

- frozen observations;
- deterministic samples;
- inclusion weights;
- agreement pilots;
- reviewer columns;
- codebooks;
- candidate thresholds;
- project-cluster bootstrap design.

However, do not ask humans to label all existing rows immediately.

## 20.1 Treat threshold labels as calibration data

Threshold human labels used to choose a new threshold belong to the calibration repository set.

If they influence threshold selection, they cannot later be used as final held-out performance evidence.

## 20.2 Collapse duplicated human questions

The 24 numerical metrics do not necessarily require 24 independent human decisions.

Examples:

```text
large_play_loc
large_play_task_count
large_play_avg_task_size
```

may share the same human judgment of whether the play is genuinely too large.

Likewise large-playbook metrics share a common source object.

Build a mapping:

```text
threshold metric
    -> human condition family
    -> source object identity
```

Reuse one human judgment across metric analyses only when the underlying human question is genuinely identical.

Do not merge semantically different metrics merely to reduce workload.

## 20.3 Suggested human-condition families

Approximately:

```text
large task
long task name
naming special characters
long statement
complex expression
nesting
missing abstraction
undocumented complexity
large play
large playbook
high coupling
cohesion
complex playbook
```

Generate:

```text
threshold-human-condition-map.csv
```

## 20.4 Staged batches

Instead of opening all 16,971 primary rows immediately:

```text
Batch 1: ~100–150 unique human source objects/family
Batch 2: additional reserve if required
Batch 3: reserve
```

Freeze all batches and stopping criteria before seeing labels.

Document the stopping rule.

---

# 21. Calibration phase

Once the pilot codebooks are frozen, human reviewers label the calibration samples.

Use these data to:

- identify false-positive mechanisms;
- assess policy actionability;
- evaluate thresholds;
- decide whether detector semantics need changes.

If the team changes:

```text
detector logic
threshold
rule severity/confidence
semantic classification
```

because of calibration labels, record the change.

Create:

```text
CALIBRATION_DECISIONS.md
```

For every change:

```text
evidence
old behavior
new behavior
reason
rules affected
tests added
whether rerun is required
```

---

# 22. Freeze before final held-out evaluation

Before opening held-out human validation:

1. detector code frozen;
2. thresholds frozen;
3. rule catalog frozen;
4. codebooks frozen;
5. mapping files frozen;
6. sampling scripts frozen;
7. final run/package frozen;
8. human held-out samples frozen.

Create:

```text
FINAL_VALIDATION_FREEZE.json
FINAL_VALIDATION_FREEZE.md
```

Include hashes of every critical artifact.

After this point:

**no tuning from held-out labels.**

If a serious defect is discovered, report it and start a new validation version instead of quietly changing v0.0.7 results.

---

# 23. Held-out final evaluation

Generate final held-out samples only from the 62 held-out repositories.

Do not reuse calibration rows.

Both human reviewers should independently label the final core held-out evaluation.

This is the strongest final evidence.

Target strong double review for:

- representative held-out precision;
- high-risk/security items;
- special variable-resolution concepts;
- rule families used in major paper claims.

For rare rules not present in held-out repositories:

- do not move them into held-out;
- report calibration/corpus evidence separately;
- state that held-out support is absent.

---

# 24. Reviewer workload strategy

Ideal:

```text
both humans independently label every final evaluation item
```

For the broader calibration top-up workload, use:

| Dataset | Reviewer A | Reviewer B |
|---|---|---|
| Agreement pilot | 100% | 100% |
| Representative precision core | 100% | 100% |
| High-risk/security strata | 100% | 100% |
| Special semantic strata | 100% | 100% |
| Remaining calibration top-ups | primary half | primary half |
| Audit subset of top-ups | cross-review ~25–30% | cross-review ~25–30% |
| Any uncertain row | second review required | second review required |
| Final held-out evaluation | 100% | 100% |

The exact realized workload must be generated and reported.

---

# 25. External providers

Do not mix external-provider precision into AnsibleGuard-native detector precision.

## 25.1 Integration normalization audit

Audit a small sample of external-provider conversion:

```text
ansible-lint native result -> normalized result
GitLeaks native result      -> normalized result
```

Check:

```text
repository
file
line/span
native rule
canonical provider rule
message
provider status
```

Suggested:

```text
50–100 normalization rows/provider
```

## 25.2 External overlap

Use the explicit mapping work from:

`ANSIBLEGUARD_EXTERNAL_TOOL_MAPPING_STARTER.csv`

Before computing overlap:

- complete the mapping;
- freeze relationship types;
- freeze occurrence-matching rules;
- restrict ansible-lint comparisons to comparable/complete provider populations;
- use same repository/commit/source-object identity.

Report overlap as overlap, not precision/recall.

---

# 26. AI-shadow review procedure

Once human gold-standard labels for a panel are frozen:

1. make an identical row set for Luna;
2. hide:
   - human labels;
   - adjudication;
   - agreement statistics;
   - AI-precheck answers;
3. use the same frozen human codebook;
4. have Luna inspect the source/repository evidence herself;
5. fill only AI fields;
6. preserve Luna's notes/reasons;
7. hash the completed AI file;
8. compare AI labels with adjudicated humans afterward.

Generate:

```text
results/ai-vs-human-agreement.csv
results/ai-vs-human-summary.md
```

Compute at least:

```text
raw agreement
Cohen's kappa
Gwet's AC1
positive agreement
negative agreement
uncertain agreement
per-rule agreement
per-family agreement
```

Never merge AI and human labels into one gold-standard vote.

---

# 27. Scripts Luna must create

Prefer scripts over manual spreadsheet manipulation.

At minimum create tools for:

```text
build_repository_split.py
build_agreement_pilot.py
build_precision_sample.py
build_rule_topups.py
build_reviewer_workbooks.py
validate_reviewer_workbook.py
compare_human_reviewers.py
build_disagreement_sheet.py
score_precision.py
score_actionability.py
build_recall_samples.py
score_recall.py
prepare_threshold_batches.py
score_thresholds.py
prepare_ai_shadow.py
compare_ai_to_humans.py
validate_validation_package.py
```

Names may differ if the project already has suitable tools.

Reuse existing threshold scripts where they already implement the needed logic correctly.

Do not duplicate mature code unnecessarily.

---

# 28. Validation package integrity

Create checks that fail if:

- sample IDs are duplicated;
- same occurrence appears in calibration and held-out;
- repository appears in both calibration and held-out;
- reviewer CSV rows differ from master sample IDs;
- reviewer ordering/source context changed;
- a human file contains AI labels;
- an AI file contains human labels;
- held-out rows were generated from calibration repositories;
- sampling weight is missing where required;
- selection probability is invalid;
- a failed repository is treated as zero;
- external-provider findings enter internal detector precision;
- Git-history findings enter static-source precision;
- threshold calibration rows enter held-out performance;
- codebooks changed after final freeze;
- sample source hashes changed.

Generate:

```text
VALIDATION_INTEGRITY_REPORT.md
validation-integrity.json
```

---

# 29. Required manifests and checksums

Every frozen artifact should be checksummed.

At minimum:

```text
checksums/samples.sha256
checksums/codebooks.sha256
checksums/splits.sha256
checksums/reviewer-templates.sha256
checksums/final-freeze.sha256
```

Mutable human-label files are checksummed when returned/frozen.

Record:

```text
created_at
source commit
sampling seed
script commit
source data hash
row count
unique repository count
unique rule count
```

---

# 30. Required reports

Create:

```text
VALIDATION_DESIGN.md
VALIDATION_STATUS.md
HUMAN_REVIEWER_A_INSTRUCTIONS.md
HUMAN_REVIEWER_B_INSTRUCTIONS.md
HUMAN_REVIEW_CHECKLIST.md
WEIGHTING_METHOD.md
RECALL_PROTOCOL.md
THRESHOLD_VALIDATION_PROTOCOL.md
AI_SHADOW_PROTOCOL.md
CALIBRATION_DECISIONS.md
FINAL_VALIDATION_FREEZE.md
VALIDATION_INTEGRITY_REPORT.md
```

After human labels exist, create:

```text
HUMAN_AGREEMENT_REPORT.md
CALIBRATION_RESULTS.md
FINAL_HELDOUT_RESULTS.md
AI_VS_HUMAN_REPORT.md
VALIDATION_FINAL_REPORT.md
```

---

# 31. VALIDATION_STATUS.md must act as the resumable state machine

This project involves real humans, so Luna cannot truthfully finish human validation before the humans provide decisions.

Do not fake completion.

Use explicit phase states:

```text
NOT_STARTED
IN_PROGRESS
WAITING_FOR_HUMANS
READY_FOR_ADJUDICATION
WAITING_FOR_ADJUDICATION
CALIBRATION_COMPLETE
FINAL_FREEZE_COMPLETE
HELDOUT_WAITING_FOR_HUMANS
VALIDATION_COMPLETE
```

For each phase list:

```text
input
output
hash
status
next action
blocking dependency
```

When human input is genuinely required:

- complete everything that can be automated first;
- push the branch and blank reviewer CSVs;
- set `WAITING_FOR_HUMANS`;
- give exact instructions for what Reviewer A and Reviewer B must fill;
- do not declare validation complete.

When the human CSVs are later pushed, resume from this file and continue automatically.

---

# 32. Definition of done — preparation stage

Before asking humans to do anything, Luna must have completed all of the following:

- [ ] inspected current branch and recorded starting SHA;
- [ ] created dedicated validation branch;
- [ ] completed pre-validation cleanliness gate;
- [ ] identified authoritative internal occurrence population;
- [ ] mapped all AnsibleGuard rules to validation families;
- [ ] frozen 144/62 repository calibration/held-out split;
- [ ] generated split balance report;
- [ ] generated family codebooks;
- [ ] generated rule-specific overrides;
- [ ] generated ~350-case agreement pilot;
- [ ] generated 1,000-case representative precision core;
- [ ] generated rule-balanced top-ups;
- [ ] applied rare-rule censuses;
- [ ] applied variable/security semantic overrides;
- [ ] generated review/history panel;
- [ ] generated recall eligibility matrix;
- [ ] generated source-first recall panels where possible;
- [ ] mapped threshold metrics to human-condition families;
- [ ] created staged threshold batches;
- [ ] created Reviewer A blank CSVs;
- [ ] created Reviewer B blank CSVs;
- [ ] verified Reviewer A/B rows are identical;
- [ ] created AI-shadow template CSVs;
- [ ] created all reviewer instruction files;
- [ ] created weighting metadata;
- [ ] created sample manifests/checksums;
- [ ] validation package integrity passes;
- [ ] pushed all preparation artifacts.

Only then is it acceptable to set:

```text
WAITING_FOR_HUMANS
```

---

# 33. Definition of done — agreement stage

After human pilot files are returned:

- [ ] validate human CSV integrity;
- [ ] compute raw agreement;
- [ ] compute Cohen's kappa;
- [ ] compute Gwet's AC1;
- [ ] compute label-specific agreement;
- [ ] produce disagreement file;
- [ ] if agreement is insufficient, revise codebook using pilot only;
- [ ] generate a NEW pilot;
- [ ] repeat without contaminating primary samples;
- [ ] freeze final codebooks.

---

# 34. Definition of done — calibration stage

After primary calibration labels exist:

- [ ] preserve both independent human label files;
- [ ] adjudicate disagreements through human process;
- [ ] compute weighted micro precision;
- [ ] compute macro precision;
- [ ] compute per-rule precision;
- [ ] compute per-concept precision;
- [ ] compute per-category precision;
- [ ] compute per-confidence precision;
- [ ] compute per-resolution precision;
- [ ] compute actionability;
- [ ] compute uncertain/unreviewable rates;
- [ ] compute project-cluster bootstrap intervals;
- [ ] score source-first recall where valid;
- [ ] score threshold calibration data;
- [ ] record all calibration-driven changes;
- [ ] rerun detector/results if detector semantics changed;
- [ ] freeze final detector/threshold/codebook/mappings.

---

# 35. Definition of done — final held-out stage

After the final freeze:

- [ ] generate held-out samples only from the 62 held-out repositories;
- [ ] both humans independently label final sample;
- [ ] validate returned CSVs;
- [ ] calculate agreement;
- [ ] human adjudication complete;
- [ ] compute final weighted metrics;
- [ ] no threshold/rule tuning from held-out labels;
- [ ] freeze final human gold standard;
- [ ] Luna performs blinded AI-shadow review of identical sample;
- [ ] compute AI-vs-human comparison;
- [ ] create final validation report;
- [ ] create final checksums;
- [ ] push final artifacts.

Only then set:

```text
VALIDATION_COMPLETE
```

---

# 36. What Luna is explicitly forbidden to do

Do not:

- invent Reviewer A labels;
- invent Reviewer B labels;
- copy AI labels into human CSVs;
- call Luna a human reviewer;
- silently adjudicate humans;
- use held-out labels for tuning;
- reveal AI labels to humans before their review is frozen;
- use ansible-lint as ground truth;
- use GitLeaks as ground truth;
- call `uncertain` a false positive automatically;
- calculate recall from emitted findings only;
- report one "accuracy" number as if it represented every rule;
- average oversampled rows without weights;
- treat findings from the same repository as statistically independent;
- move difficult repositories from held-out to calibration after labels exist;
- drop rare rules because sample size is inconvenient;
- treat failed/missing analysis as zero findings;
- change detector behavior merely to improve validation scores;
- silently change codebooks after final freeze.

---

# 37. Final expected Git tree

A successful implementation should look approximately like:

```text
study/validation-v007-human/
├── README.md
├── PROTOCOL.md
├── PRE_VALIDATION_GATE.md
├── VALIDATION_DESIGN.md
├── VALIDATION_STATUS.md
├── HUMAN_REVIEWER_A_INSTRUCTIONS.md
├── HUMAN_REVIEWER_B_INSTRUCTIONS.md
├── HUMAN_REVIEW_CHECKLIST.md
├── WEIGHTING_METHOD.md
├── RECALL_PROTOCOL.md
├── THRESHOLD_VALIDATION_PROTOCOL.md
├── AI_SHADOW_PROTOCOL.md
├── CALIBRATION_DECISIONS.md
├── FINAL_VALIDATION_FREEZE.md
├── VALIDATION_INTEGRITY_REPORT.md
├── codebooks/
├── mappings/
├── manifests/
├── splits/
├── samples/
│   ├── agreement-pilot/
│   ├── calibration/
│   ├── recall/
│   ├── thresholds/
│   └── heldout/
├── reviewers/
│   ├── reviewer-a/
│   ├── reviewer-b/
│   └── ai-shadow/
├── adjudication/
├── results/
├── scripts/
└── checksums/
```

---

# 38. Final handoff Luna must give

At the end of every execution session, update `VALIDATION_STATUS.md` and report:

```text
starting Git SHA
ending Git SHA
branch
commits created
files created
files changed
tests run
validation integrity result

repository split:
calibration count
heldout count

agreement pilot:
rows
families
repositories

precision sample:
representative rows
top-up rows
rare census rows
special semantic rows
unique final rows
rules represented
repositories represented

review-history sample:
rows

recall panels:
rules/families
rows

threshold:
human-condition families
batch sizes

Reviewer A CSV paths
Reviewer B CSV paths
AI-shadow CSV paths

human work currently required
next exact command/step after humans return labels

remaining blockers
```

Push the branch.

---

# 39. Work-until-done instruction

Do not stop because one script has been written.

Do not stop because CSV headers exist.

Do not stop because the first sample was generated.

Continue through the complete preparation plan, validate every artifact, commit it, push it, and update the resumable status file.

The only acceptable reasons to pause before the full scientific validation is complete are genuine external human gates:

```text
Reviewer A labels required
Reviewer B labels required
human adjudication required
```

Before pausing for such a gate, every machine/AI-preparable artifact for that stage must already be complete, validated, committed, pushed, documented, and checksummed.

Never fabricate the missing human work just to satisfy "done."

After human files are provided, resume from `VALIDATION_STATUS.md` and continue until the next genuine human gate or until:

```text
VALIDATION_COMPLETE
```

---

# 40. Scientific interpretation to preserve

The final study should allow statements such as:

```text
weighted semantic precision across the frozen occurrence population
macro precision across rules
per-rule and per-concept precision
practical actionability
human uncertain rate
human-human agreement
source-first recall for eligible rule families
threshold performance on calibration data
final untouched held-out performance
AI-vs-human agreement
```

It should NOT collapse all of that into:

```text
"AnsibleGuard accuracy = X%"
```

without defining the estimand.

The objective is not to obtain the highest-looking number.

The objective is to create a validation package that another researcher can inspect and understand exactly:

```text
what was sampled
why it was sampled
who labeled it
what evidence they saw
what remained uncertain
how weighting was done
what was calibration
what was truly held out
what AI contributed
and what claims the evidence supports
```
