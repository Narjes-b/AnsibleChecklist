# v0.0.7 validation protocol: verification, sampling and human labelling

*Drafted 2026-10-16 from the run analysis ([v007-results-analysis.md](v007-results-analysis.md)),
the sampling simulation ([study/validation-design-v007/](../../study/validation-design-v007/README.md))
and the audit ([v007-audit-2026-10-15.md](v007-audit-2026-10-15.md)). It supersedes
§7 of [the research report](v007-research-report-and-validation-plan.md) where
they differ. It is a plan to be pre-registered, not a result.*

## 1. Principle

One number such as "overall precision" is **not** the goal. The 53 rules
with required findings make three different kinds of claim, and each needs a
different kind of evidence:

| Mode | Claim | Rules with required findings | Required findings | Share | Evidence that settles it |
|---|---|---:|---:|---:|---|
| **A** deterministic predicate | "this object has property P" (task has no name, key duplicated, `validate_certs: false`) | 25 (+ 6 optional-only) | 22,701 | 27 % | an independent implementation or external oracle run on **every** occurrence; humans audit edge cases only |
| **B** metric / threshold | "this unit exceeds a size/complexity threshold" | 15 | 45,677 | 55 % | whether the **threshold** is meaningful: banded calibration panels, not precision sampling |
| **C** semantic judgement | "this is a real problem" (secret leaks, command not idempotent, variable undefined) | 13 (+ 1 optional-only) | 15,119 | 18 % | the full human design: stratified two-stage sample per rule, census for rare rules |

The assignment of every rule is in
[`rule-verification-plan.csv`](../../study/validation-design-v007/rule-verification-plan.csv).
It is a **proposal**: each assignment must be confirmed by reading the
detector before pre-registration.

## 2. What is validated (claims and what would falsify them)

| # | Claim | Population | Falsified if |
|---|---|---|---|
| C1 | Mode A predicates are implemented correctly | all occurrences of the 31 predicate rules (25 required, 6 optional-only) | the independent implementation disagrees on > 1 % of occurrences, or any human audit item shows the predicate applied to the wrong object |
| C2 | Mode B thresholds separate "needs attention" from "fine" | banded units per metric, including units **below** threshold | labelled "needs attention" rate does not rise with the metric value, or is the same below and above the threshold |
| C3 | Mode C findings are correct | 13 semantic rules | per-rule weighted precision lower bound < 0.5 for a rule declared "stable" |
| C4 | Optional findings apply their policy | optional occurrences | policy applied wrongly in > 5 % of audit items |
| C5 | UNCERTAIN means uncertain | uncertain variable findings | a resolvable majority (> 50 % definitely defined or definitely undefined) |
| C6 | Recall of implemented smells | heldout files with injected and naturally occurring smells | injected-defect detection < 90 % for a class the rule claims to cover |
| C7 | PR mode attributes changes correctly | real merged PRs | introduced/fixed findings not supported by the diff |
| C8 | Findings matter | later history | flagged objects are not changed or removed more often than matched controls |

C8 is not required for the paper's main claim but is the only evidence that
does not depend on a rater's opinion.

## 3. Prerequisites (before any sample is drawn)

1. Merge the audit fixes; produce a **frozen `v0.0.7.1` run** whose provenance
   passes the validation gate (the previous run's review rules and
   provider-comparable tables are not interpretable).
2. Make every file-level finding name its subject (task, play, variable, role)
   so a reviewer can tell what is asserted; for variable rules the unit is
   **(location, variable)**: 5,425 rows share a location with another finding.
3. Decide, and document in the catalog, what `policy` means (it is currently
   per occurrence and driven by the resolution state).
4. Make `credentials-leaking-in-log` read module argument specs
   (`no_log` parameters), which removes the largest known false-positive
   mechanism in the rule that is 74 % of security.
5. Freeze: tool commit, rule catalog hash, thresholds, codebooks, context
   generator, seed. Any detector change afterwards starts a new version.
6. Heldout contexts stay unopened until the freeze; calibration is used for
   pilots, codebook revision, threshold calibration and error analysis.

## 4. Populations and units

| Population | Unit | Source |
|---|---|---|
| required static-source | (rule, location, subject) | `all-internal-source-occurrences.csv`, `policy = required` |
| optional static-source | (rule, location, subject) | same, `policy = optional` |
| uncertain variable findings | (location, variable) | `certainty = UNCERTAIN` |
| metric observations | (object, metric value) | threshold source population (2,986,459 rows) |
| files | file | heldout files stratified by kind |
| pull requests | merged first-parent PR | repositories with full history |

Heldout required occurrences by category: maintainability 10,189, style 6,050,
security 2,376, compatibility 1,854, correctness 702, reliability 727,
documentation 492, structure 457, dependencies 163 (total 23,010).

## 5. Sampling design

### 5.1 Mode C (semantic) — full design

- Tier by the rule's **heldout** required count N: census if N ≤ 30; target 30
  if N < 500; target 40 if N ≥ 500.
- Two-stage: repositories at random, then at most 2 occurrences per
  repository (cap relaxed only to reach the target).
- Estimator: Hájek ratio with weights N_rj / n_rj; interval = Wilson on the
  design-effective sample size. The simulation showed a pooled proportion is
  biased by up to −0.21 and covers 0–64 % of the time when precision varies
  with repository size, while the weighted estimator is within ±0.01 and the
  effective-n interval covers 89–96 % (median 93 %).
- Rules with fewer than 8 sampleable repositories: exact limits on the labelled
  items only, marked non-generalizable.
- Items: 375 (13 rules; the 14th semantic rule is optional-only).

### 5.2 Mode B (threshold) — banded calibration panels

- For each of the 15 rules sample up to 30 objects from the metric
  observations, **including objects that are not flagged**, in four bands of
  the metric relative to the threshold: just below (80–100 %), just above
  (100–125 %), clearly above (125–200 %), far above (> 200 %).
- Reviewers answer "would a maintainer act on this?" (split, simplify,
  document), not "is the metric correct".
- Output: the rate of "act" per band, and the metric value at which it crosses
  50 % — a threshold estimate with a bootstrap interval.
- Items: 418.

### 5.3 Mode A (deterministic) — automatic verification plus audit

- Re-implement each predicate independently (separate code path, ideally by a
  different person) or use an external oracle where one exists:
  ansible-core's task attribute types, argument specs, `runtime.yml`
  routing/deprecation metadata, and strict YAML duplicate-key detection.
  Compare on **all** occurrences and on a random sample of **non-flagged**
  objects (to estimate misses).
- Humans audit 10 items per rule: 5 random and 5 selected for features likely
  to confuse the predicate (Jinja in names, includes, templates, generated
  files).
- Items: 160.

### 5.4 Secondary panels

| Panel | Sample | Estimates |
|---|---:|---|
| UNCERTAIN variable findings (C5) | 120: 30 each for `possible_required_role_input`, `possible_playbook_input`, include-related, other; weighted by stratum size | share that is resolvable, defined, undefined, genuinely unknowable |
| Optional policy audit (C4) | 20 per optional rule with ≥ 1 heldout occurrence | policy applied correctly |
| Recall (C6) | 60 heldout files (20 playbooks, 20 role task files, 20 vars/defaults), reviewed blind to the tool, plus **mutation injection**: apply known defects (remove `no_log`, `mode: 0777`, add `with_items`, drop a task name, set `validate_certs: false`, unsafe `shell`) to copies of real files | per-class detection rate and the share of reviewer-found smells outside any rule |
| PR attribution (C7) | ≥ 100 real merged PRs (extend history for shallow calibration clones); all introduced/fixed findings checked against the diff automatically; 60 items labelled by humans | attribution correctness; moved-vs-churn error rate |
| Behaviour (C8) | every sampled finding | fixed/changed within the post-freeze history versus matched controls (same file, same object kind, not flagged) |

### 5.5 What is not done

No single overall precision is reported: a number that pools predicates,
thresholds and semantic judgements would have no interpretation. Two headline
statements are made instead: weighted precision over the 13 semantic rules
(18 % of required findings), and the automatic agreement rate over the 25
predicate rules with required findings (27 %).

## 6. Human labelling

### 6.1 Roles and blinding

Two independent reviewers (A, B) with Ansible experience; an adjudicator who
did not label the item. Reviewers see only the frozen context bundle: no tool
message beyond the rule definition, no other reviewer's label, no AI output,
no sampling weight. Presentation order is shuffled; 10 % of items are repeated
(same reviewer, at least a week apart) to measure intra-rater stability.

### 6.2 Labels

`semantic_label` ∈ {TP, FP, uncertain, unreviewable}; `actionability` ∈
{act-now, advisory, ignore}; `context_sufficient`; `needs_external_context`;
reason code from the codebook; free text. `unreviewable` and `uncertain` are
reported, never dropped.

### 6.3 Context bundles (must contain)

The exact source at the frozen commit, redacted; the full cited **role**
(not a grouping directory); paths beside the cited file first; for variable
rules the variable name and where it is used; for threshold rules the metric
value and the threshold; for secrets the module's `no_log` parameters; for
review/PR items the real `base..head` diff. A bundle fails validation if the
cited subject is not visible.

### 6.4 Codebooks

One per family plus rule overrides; each states the positive condition, known
false-positive patterns (from the calibration precheck), and when to choose
`uncertain` versus `unreviewable`. Codebooks are hashed and cited by every
label. Version policy for compatibility rules is stated explicitly.

### 6.5 Pilot and gate

A second pilot (the first was built from artefact-laden findings): 30 items
per semantic/threshold family, calibration repositories only, items never
reused. Proceed when, per family, Krippendorff's α ≥ 0.667, Cohen's κ ≥ 0.60
and Gwet's AC1 ≥ 0.70 (AC1 because high prevalence depresses κ). Otherwise
revise the codebook and repeat with new items. At most two revision rounds;
after that the family is reported as "not reliably labelable".

### 6.6 Adjudication

Disagreements go to the adjudicator, who sees both labels and reasons.
Pre-adjudication labels are frozen and kept; agreement is computed before
adjudication. A third rater labels a random 10 % of agreed items to detect
shared error.

### 6.7 AI

AI labels are produced only after human labels and adjudication are frozen, on
identical evidence, and stored separately. They are never ground truth. The
existing exploratory precheck is excluded from every estimate.

## 7. Estimation and reporting

- Per rule: weighted precision among decidable items, effective-n Wilson
  interval, plus `uncertain` and `unreviewable` shares; worst case
  (`uncertain` counted as FP) and best case.
- Report a rule's estimate only if ≥ 20 labelled items from ≥ 8 repositories;
  otherwise descriptive counts.
- Family and semantic-class estimates: stratified, weights N_r / ΣN_r;
  repository-cluster bootstrap for variance. The simulation showed the overall
  interval is about 90 % at nominal 95 %: calibrate the nominal level on the
  simulation before use.
- Agreement: α, κ, AC1, PABAK, raw agreement, per family and per rule (n ≥ 20);
  a Dawid–Skene model as a sensitivity analysis for rater error.
- 53 rules are reported with intervals, not tests; no multiplicity claims.
- Everything is tied to the frozen version and checksums.

## 8. Effort (planning estimate)

| Task | Items | Minutes per item per rater | Raters | Hours |
|---|---:|---:|---:|---:|
| Mode A audit | 160 | 2 | 2 | 11 |
| Mode B bands | 418 | 5 | 2 | 70 |
| Mode C semantic | 375 | 4 | 2 | 50 |
| Secondary panels (uncertain 120, PR 60) | 180 | 3 | 2 | 18 |
| Recall files | 60 | 15 | 2 | 30 |
| Pilot 2 | 180 | 3 | 2 | 18 |
| Adjudication (20 % of main items at 5 min) | 190 | 5 | 1 | 16 |
| **Total** | | | | **≈ 213** |

Plus engineering: independent implementations of the 31 predicates and the mutation
harness. If effort must be cut, cut Mode B to 20 items per rule (−23 h) and
the recall files to 40 (−10 h) before touching Mode C.

## 9. Pre-registration and freeze checklist

- [ ] rule-to-mode assignment confirmed against detector source
- [ ] frozen `v0.0.7.1` run with a passing provenance gate; run checksum
- [ ] codebooks, thresholds, context generator, seed, simulation code hashed
- [ ] simulation re-run on the new run's populations; overall-interval
      calibration done
- [ ] pilot 2 passed per family or families dropped
- [ ] analysis plan (this document, finalized) signed off by a reviewer who is
      not an author **before** heldout contexts are generated

## 10. Risks and stop rules

| Risk | Stop rule / mitigation |
|---|---|
| detector changes after sampling | new version; the sample is void |
| reviewers cannot agree on a family | drop the family from precision claims; report agreement |
| bundle shows the wrong or no subject | bundle validator fails the build; fix the tool, not the labels |
| few repositories per rule | descriptive only; never extrapolate |
| rater fatigue | ≤ 2 h per session, order shuffled, duplicates measure drift |
| secrets in contexts | redaction check is part of the gate |
| selection bias of the 207 repositories | statements are about the frozen selected population |
| ansible-lint non-determinism | provider findings are outside AnsibleGuard precision |
