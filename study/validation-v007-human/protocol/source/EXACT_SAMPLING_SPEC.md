# Luna 6 XHigh — Exact Sampling Specification for AnsibleGuard v0.0.7 Human Validation

## Status of this document

This document is the **exact sampling addendum** to:

`LUNA6_XHIGH_V007_HUMAN_VALIDATION_EXECUTION_PLAN.md`

When the earlier plan uses general language such as "balance the split", "top up rules", or "preserve sampling weights", this document defines exactly how Luna should implement those instructions.

If the two documents conflict on sampling mechanics, **this exact-sampling specification wins**.

The accompanying planning matrix is:

`V007_HUMAN_VALIDATION_RULE_ALLOCATION_MATRIX.csv`

Important: the matrix contains current full-corpus counts only as planning evidence. Luna must recompute calibration and held-out counts after the repository split from the authoritative occurrence files.

---

# 1. Authoritative populations

## 1.1 Repository universe

Start from the repository execution/status evidence for the canonical v0.0.7 run.

Create exactly two repository universes:

```text
EXECUTION universe:
207 frozen repositories

DETECTOR-QUALITY universe:
206 repositories with a usable AnsibleGuard core analysis
```

The timed-out repository remains in execution/reliability reporting but is excluded from precision/recall because there is no detector result.

## 1.2 Static precision universe

The static precision source is:

```text
aggregate/all-internal-source-occurrences.csv
```

not:

```text
all provider canonical findings
ansible-lint findings
GitLeaks findings
review/history findings
broken helper-chart CSVs
```

Before sampling assert:

```text
provider == ansibleguard
repository is in 206 analyzable repositories
occurrence_id is unique
source context can be reconstructed
```

Record the actual population count and SHA256.

If it does not match the expected canonical run state, stop and investigate.

## 1.3 Review/history universe

Use only AnsibleGuard review/history occurrences and keep them in a separate panel.

Do not merge them with static-source precision.

## 1.4 External-provider universe

ansible-lint/GitLeaks do not enter AnsibleGuard-native precision.

They get a separate normalization/overlap panel.

---

# 2. Stable identities

Before sampling, every candidate needs:

```text
repository
commit_sha
provider
canonical_rule_id
concept_id
resolution_status
path
line/span
object_kind
object_id
occurrence_id
```

The primary immutable sampling key is:

```text
occurrence_id
```

If an occurrence lacks a stable identity, fix the identity pipeline before sampling it.

---

# 3. Deterministic hash selection — use this everywhere

Do not use runtime RNG state.

For any sampling operation use a stable SHA256 rank:

```text
rank_key =
SHA256(
  sampling_seed
  + "|"
  + stable_item_id
)
```

Sort lexicographically by `rank_key`.

Take the first `n` eligible rows.

This makes sampling reproducible across machines and Python versions.

Every sub-study gets a distinct frozen seed.

Examples:

```text
v007-human-repo-split-20261005
v007-human-pilot-v1
v007-human-core-calibration-v1
v007-human-rule-<rule>-calibration-v1
v007-human-concept-<concept>-calibration-v1
v007-human-heldout-core-v1
```

Save every seed in a manifest.

---

# 4. Exact 144 / 62 repository split

Target:

```text
calibration = 144
heldout    = 62
total      = 206
```

The split happens once and is frozen before human labels.

## 4.1 Features used to balance the split

For each repository calculate from pre-human detector data:

```text
selected_loc
selected_files
internal_static_occurrences
internal_static_density
presence/absence of each of the 15 most prevalent AnsibleGuard static rules
```

Transform:

```text
size_quartile    = quartile(log1p(selected_loc))
density_quartile = quartile(log1p(internal_static_density))
```

Create multilabel balancing tokens:

```text
SIZE_Q1 ... SIZE_Q4
DENSITY_Q1 ... DENSITY_Q4
RULE_PRESENT_<top15 rule ids>
```

No human labels are used.

## 4.2 Deterministic iterative assignment

Implement repository-level iterative stratification.

High-level exact procedure:

1. Compute the desired held-out count for every balancing token as `round(0.30 * token_count)`.
2. Start with both sets empty.
3. Process the currently rarest unassigned token first.
4. Among unassigned repositories carrying that token, sort by:
   `SHA256(split_seed + "|" + repository)`.
5. Assign each repository to the set with the largest normalized deficit for its tokens.
6. Respect hard capacities:
   - heldout cannot exceed 62;
   - calibration cannot exceed 144.
7. Tie-break by the repository hash rank.
8. Continue until all 206 are assigned.
9. If the exact capacities are not 144/62 because of rounding/ties, perform deterministic swaps minimizing total token imbalance until capacities are exact.

## 4.3 Acceptance checks

The split must report:

```text
mean selected LOC in each set
median selected LOC
mean internal density
median internal density
size quartile proportions
density quartile proportions
top-15 rule prevalence in each set
```

Flag any top-15 rule prevalence difference >10 percentage points for manual inspection.

Do NOT manually move repositories because later human results are inconvenient.

Freeze:

```text
repository-split.csv
repository-split-manifest.json
repository-split-balance.csv
repository-split-balance.md
```

---

# 5. Important held-out rule

After the repository split is frozen:

```text
calibration data may be inspected and used for tuning
heldout data may NOT be used for tuning
```

This applies to:

- detector precision;
- source-first recall;
- threshold selection;
- codebook tuning;
- rule redesign.

The existing threshold benchmark was created over the full 207-repository corpus.

Therefore:

**Do not use threshold-review rows from held-out repositories to select thresholds.**

Rebuild/filter threshold calibration batches using only the 144 calibration repositories.

If the existing threshold population artifact needed to do that is missing, stop threshold calibration and document the blocker. Do not use mixed calibration+heldout rows.

---

# 6. Agreement pilot — exact selection

Agreement pilots exist to improve the human instructions, not to estimate final precision.

Use only calibration repositories.

Target families:

```text
objective correctness
variable/reference reasoning
security
style/policy
maintainability/complexity
structure/reuse
review/history
```

Target:

```text
50 unique rows per family
≈350 total
```

## 6.1 Keep pilot rows out of calibration performance scoring

Pilot rows are codebook-development data.

Once used to discuss disagreements, they must not become primary performance rows.

Store:

```text
is_agreement_pilot = true
eligible_for_performance_scoring = false
```

## 6.2 Family balancing

Within each family:

1. Prefer rules with at least 5 eligible calibration examples.
2. Round-robin across rules rather than taking 50 rows from the dominant rule.
3. Within each rule use deterministic hash rank.
4. Prefer repository diversity:
   - first pass: at most one row/repository;
   - second pass: allow additional rows only if needed.
5. Stop at 50 rows or census the family if fewer than 50 usable rows exist.

Do not use very rare rule occurrences in the pilot if consuming them would prevent meaningful primary validation.

---

# 7. Calibration precision sample — exact two-layer design

Use calibration repositories only.

Exclude agreement-pilot occurrence IDs.

The human workload is a **union of unique source items**.

The statistics are computed through explicit **sub-study membership**.

Create:

```text
validation-items.csv
sample-membership.csv
```

## 7.1 `validation-items.csv`

One row per unique human-review item.

A human labels each row once even if it belongs to several sub-studies.

## 7.2 `sample-membership.csv`

One row per:

```text
(sample_id, sub_study_id)
```

Fields:

```text
sample_id
sub_study_id
estimand
population_id
stratum_id
population_N
sample_n
selection_probability
sampling_weight
seed
```

This solves overlapping-sample weighting cleanly.

---

# 8. Layer A — representative core

Draw exactly:

```text
1,000 unique calibration static occurrences
```

from the eligible calibration static population after excluding pilot rows.

Method:

```text
simple random sample without replacement
implemented by SHA256 rank
```

Every eligible occurrence has:

```text
pi_core = 1000 / N_calibration_static
weight_core = N_calibration_static / 1000
```

This sub-study is the primary estimator for:

```text
real-world occurrence-weighted semantic precision
real-world occurrence-weighted actionability
overall uncertain rate
```

Do not modify the core to make rule counts look balanced.

---

# 9. Layer B — rule/concept validation sample

The core alone is not enough for per-rule validation.

After selecting the core, create per-rule/per-concept strata.

Rows already present in the core count toward a stratum's target.

For each stratum:

```text
c = number of core rows in the stratum
T = target for the stratum
```

If:

```text
c >= T
```

do not add top-up rows.

If:

```text
c < T
```

draw:

```text
T - c
```

additional rows from eligible non-core rows in that stratum, using the stratum-specific SHA256 seed.

The final stratum sample is therefore:

```text
n_final = max(c, T)
```

Record actual `n_final`.

---

# 10. Generic rule target function

For a static rule with calibration population `N_rule`:

```text
if N_rule <= 50:
    T = N_rule             # census
elif 51 <= N_rule <= 199:
    T = 30
elif 200 <= N_rule <= 999:
    T = 45
elif 1000 <= N_rule <= 4999:
    T = 60
elif 5000 <= N_rule <= 19999:
    T = 75
else:
    T = 100
```

This target is computed from **calibration N**, not blindly copied from the full-corpus planning matrix.

---

# 11. Security / experimental / candidate floor

For a rule whose authoritative rule metadata says:

```text
category == security
```

OR:

```text
status in {experimental, candidate}
```

use:

```text
T = min(N_rule, max(generic_T, 75))
```

unless a stronger special-stratum rule below applies.

This gives more evidence to high-risk or less-mature detectors.

---

# 12. Special rule — `unguarded-variable`

Do NOT use one rule-level target.

Split by semantic concept:

```text
undeclared-input-contract
unresolved-runtime-input
missing-internal-variable
```

For each concept in each repository split:

```text
T_concept = min(100, N_concept)
```

If the concept population is smaller than 100, census it.

Rows from the representative core count toward these targets.

Report these concepts separately.

The rule-level result may later be reconstructed by population-weighting concept-level results.

---

# 13. Special rule — `credentials-leaking-in-log`

Do NOT treat all evidence states as equivalent.

Stratify by:

```text
resolution_status
```

or the strongest equivalent evidence-state field.

For each state:

```text
if N_state < 30:
    census
else:
    T_state = min(100, N_state)
```

At minimum preserve distinction between states such as:

```text
PROVEN_EXPOSED
DYNAMIC_PROTECTION_UNKNOWN
```

if present.

Report state-specific correctness and uncertainty.

---

# 14. Other multi-concept rules

Before sampling, use the authoritative concept mapping.

If one rule maps to materially different semantic concepts:

- make concept a primary stratum;
- apply the same target logic at concept level;
- reconstruct rule-level estimates by actual concept population weights.

Do not hide different semantics inside one average.

---

# 15. Rare rules

For any validation stratum with:

```text
N <= 50
```

perform a census.

This means every occurrence in that repository split is human-reviewed.

Label the result:

```text
corpus/split census
```

Do not imply universal generalization outside the corpus.

---

# 16. Repository-diversity audit

Primary per-rule/per-concept samples use occurrence-level probability sampling.

Do not distort the main estimator merely to force repository diversity.

After the sample is selected, report:

```text
unique repositories
max share of rows from one repository
top-5 repository share
```

If a rule sample has:

```text
< min(20, floor(n_final/2))
```

unique repositories despite the rule existing in substantially more repositories, create an additional:

```text
diversity-audit
```

sample from unsampled repositories.

Important:

- diversity-audit rows are human-reviewed;
- they are reported qualitatively / separately;
- they do NOT enter the primary probability estimate unless their inclusion probabilities are modeled explicitly.

---

# 17. Overlap of core and top-ups

Do not duplicate human work.

If occurrence `X` appears in:

```text
representative core
rule sample
concept sample
security sample
```

then:

```text
validation-items.csv
```

contains X once.

`sample-membership.csv` contains multiple memberships.

Humans label X once.

Each statistical estimator selects the memberships relevant to that estimand.

Never count the same human label twice inside one estimator.

---

# 18. Review/history panel

The current review/history population is small.

Use a census strategy within each split.

During calibration:

```text
review every review/history occurrence belonging to the 144 calibration repositories
```

After final freeze:

```text
review every review/history occurrence belonging to the 62 held-out repositories
```

Keep review/history evidence and metrics separate from static-source precision.

---

# 19. Human workbooks

From the unique `validation-items.csv`, generate:

```text
reviewer-a/<panel>.csv
reviewer-b/<panel>.csv
ai-shadow/<panel>.csv
```

Reviewer A and B files:

- identical sample IDs;
- identical visible evidence;
- decision fields blank;
- no AI fields;
- no other-reviewer fields.

AI-shadow:

- identical sample IDs/evidence;
- AI-specific blank decision fields.

---

# 20. Primary calibration scoring rules

## 20.1 Overall weighted precision

Use only:

```text
sub_study_id = representative-core
```

for the simplest primary overall occurrence-weighted estimate.

This avoids ambiguity from oversampled rare rules.

## 20.2 Per-rule precision

Use that rule's final probability sample:

```text
core members in rule
+
deterministic top-ups to target
```

Record actual `N_rule`, `n_rule`, and weights.

## 20.3 Per-concept precision

Use the corresponding concept stratum.

## 20.4 Macro precision

Compute per-rule decided precision first, then average rules using the declared macro convention.

Do not let huge rules dominate macro precision.

## 20.5 Uncertain cases

Primary semantic precision denominator:

```text
positive + negative
```

Report uncertain and unreviewable rates separately.

Also provide a conservative sensitivity analysis if useful, e.g. treating uncertain as non-positive, but never silently merge it into FP.

---

# 21. Held-out sampling — do this only after final freeze

Do NOT generate/open the final held-out human source package before:

```text
detector code frozen
thresholds frozen
codebooks frozen
mapping frozen
calibration decisions frozen
```

After freeze, run the same algorithm on the 62 held-out repositories.

## 21.1 Held-out representative core

Draw:

```text
1,000 held-out static occurrences
```

or census if the eligible population is <1,000.

## 21.2 Held-out per-rule/concept targets

Apply the same target formula using **held-out N**, including:

- rare census;
- security/experimental/candidate floor;
- unguarded-variable concept targets;
- credential-log evidence-state targets.

Do not transfer calibration rows.

## 21.3 Reviewers

Both human reviewers independently label **100% of the final held-out union sample**.

No split workload on the final held-out evaluation.

---

# 22. Source-first recall sampling

Recall needs candidate universes independent of detector positives.

For each recall-eligible rule/family:

1. define the complete source candidate universe;
2. remove any use of detector output from the human question;
3. split by repository calibration/heldout;
4. sample source units with deterministic hash ranking;
5. preserve inclusion probability;
6. compare human positive/negative truth with detector firing afterward.

Never derive recall from emitted findings alone.

Create:

```text
recall-eligibility.csv
```

For rules where a candidate universe cannot be defined defensibly:

```text
recall_estimable = false
```

No global recall number should be manufactured from incompatible universes.

---

# 23. Exact threshold leakage rule

The threshold benchmark currently contains samples constructed from the full frozen corpus.

After the 144/62 split:

### For threshold calibration

Use only observations from the 144 calibration repositories.

Regenerate:

```text
calibration threshold sample
calibration agreement pilot
calibration review batches
```

using the same corrected measurement logic and frozen calibration seeds.

### For final threshold evaluation

After choosing/fixing thresholds:

use only observations/source units from the 62 held-out repositories.

Never let a held-out threshold label influence threshold selection.

If the full population artifact required to regenerate split-safe threshold samples is unavailable:

```text
STOP threshold-selection work
document blocker
```

Do not use the old mixed sample as calibration.

---

# 24. Threshold human-condition deduplication

The 24 numerical metrics include multiple measurements of the same source object/human condition.

Create:

```text
threshold-human-condition-map.csv
```

Example groups:

```text
large_play_loc
large_play_task_count
large_play_avg_task_size
    -> human condition: large-play
    -> object: play

large_playbook_loc
large_playbook_play_count
large_playbook_avg_play_size
large_playbook_task_count
large_playbook_avg_task_size
    -> human condition: large-playbook
    -> object: playbook

complex_expression_score
complex_expression_length_chars
    -> human condition: complex-expression
    -> object: expression/task
```

A human labels the underlying condition once per unique source object.

Metric scoring reuses that gold label only when the human question is genuinely the same.

---

# 25. Threshold staged-batch rule

For each threshold human-condition family, pre-freeze:

```text
Batch 1: 150 unique source objects when available
Batch 2: next 150
Batch 3: remaining reserve
```

All batch memberships are frozen before labels.

After Batch 1:

open Batch 2 only if the predeclared statistical stopping rule requires more evidence.

Do not select extra cases because they look favorable.

The exact stopping rule must be written before human labels.

---

# 26. AI-shadow timing

Generate identical blank AI-shadow files during preparation.

Formal AI labels happen only after:

```text
human labels frozen
human adjudication frozen
```

Luna must not see human answers when doing the formal AI review.

If Luna uses AI before then for schema/source-context debugging, store those outputs under:

```text
ai-precheck/
```

and exclude them from final AI-vs-human statistics.

---

# 27. Rule allocation matrix

Use the accompanying:

`V007_HUMAN_VALIDATION_RULE_ALLOCATION_MATRIX.csv`

only as a planning/checking artifact.

It records current full-corpus rule counts and the generic/special target logic.

Luna must generate final versions after splitting repositories:

```text
calibration-rule-allocation.csv
heldout-rule-allocation.csv
```

using actual split-specific populations.

For every row record:

```text
rule_id
concept/resolution stratum
N
core_count
target
topup_needed
final_unique_n
unique_repositories
census_yes_no
security_override_yes_no
experimental_or_candidate_override_yes_no
```

---

# 28. Sampling validation assertions

Sampling scripts must fail if any of these are false:

```text
calibration_repos ∩ heldout_repos == empty

len(calibration_repos) == 144
len(heldout_repos) == 62

pilot IDs ∩ primary-performance IDs == empty

all core rows come from calibration during calibration stage

all heldout rows come from heldout repositories after freeze

no external-provider row enters internal-static precision

no review/history row enters static precision

all sample IDs unique in validation-items.csv

all sample memberships reference existing sample IDs

all declared sampling probabilities are in (0,1]

all census strata have pi == 1

no heldout threshold row enters calibration threshold batches

reviewer A IDs == reviewer B IDs == AI template IDs
before labels

human files contain no AI labels

AI files contain no human/adjudicated labels
```

---

# 29. Required sampling audit report

Create:

`SAMPLING_AUDIT.md`

It must show:

```text
full candidate population
calibration population
heldout population

pilot counts by family/rule/repository

representative core:
N
n
unique repos
rule distribution
concept distribution

top-ups:
rule
N
core rows
target
added rows
final rows

special strata:
concept/evidence state
N
target
final n

rare censuses

review/history census counts

expected human workload:
Reviewer A rows
Reviewer B rows
AI-shadow rows

heldout rows are still unopened / or final-freeze status
```

---

# 30. Exact execution order

Luna must follow this order:

```text
1. verify branch + authoritative source files
2. fix/isolate reporting-layer defects
3. build stable occurrence identity table
4. freeze 144/62 repository split
5. generate balance report
6. map all rules to validation families
7. generate codebooks
8. generate agreement pilot from calibration only
9. generate blank human pilot CSVs
10. WAIT for human pilot
11. compute agreement
12. revise codebook only from pilot if required
13. freeze codebooks
14. generate calibration representative core
15. compute split-specific rule/concept populations
16. generate rule/concept/security/rare top-ups
17. union unique human items
18. generate membership table
19. generate Reviewer A/B CSVs
20. generate blank AI-shadow templates
21. generate calibration review/history census
22. generate source-first recall calibration panels
23. rebuild threshold calibration batches using calibration repos only
24. WAIT for calibration humans
25. score + adjudicate
26. make calibration decisions
27. if detector/threshold changed, rerun/freeze corrected detector
28. freeze FINAL_VALIDATION_FREEZE
29. generate heldout samples for first time
30. both humans review all heldout items
31. adjudicate humans
32. freeze human gold standard
33. Luna performs blinded identical AI-shadow review
34. compute final heldout + AI-vs-human results
35. push all artifacts and set VALIDATION_COMPLETE
```

---

# 31. Stop conditions

Luna may only pause early for a genuine external human gate.

She must not pause because:

```text
sampling logic is inconvenient
one rule has few findings
CSV is large
some strata overlap
threshold sample must be regenerated
```

Those are implementation tasks.

She must stop and report a scientific blocker if:

- authoritative population cannot be reconstructed;
- stable occurrence IDs are missing/corrupt;
- split leakage is detected;
- threshold calibration cannot be separated from heldout because source population data is unavailable;
- a sample's inclusion probability cannot be determined;
- human reviewer files no longer match frozen sample IDs.

Never guess around those issues.

---

# 32. Final interpretation

This exact design intentionally produces multiple samples for multiple estimands.

That is a feature, not a mistake.

```text
Representative core
    -> "What does a random user-visible finding look like?"

Rule/concept strata
    -> "How good is each detector or semantic state?"

Rare census
    -> "What happened for every observed rare occurrence in this corpus?"

Source-first panels
    -> "What did the detector miss?"

Threshold calibration
    -> "Which threshold should we choose?"

Heldout evaluation
    -> "How does the frozen final system perform on untouched repositories?"

AI shadow
    -> "How closely does Luna's independent judgment match frozen human gold?"
```

Do not collapse these into one ambiguous sample or one ambiguous accuracy number.
