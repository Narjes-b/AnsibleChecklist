# AnsibleGuard v0.0.7: analysis of the full run and a revised validation plan

*Prepared 2026-10-15 from the frozen run `v007-full-repro-2026` (207
repositories), its 2026-10-15 reproduction, a 101-item false-positive
precheck, and a replay of real merged pull requests. Companion documents:
[v007-audit-2026-10-15.md](v007-audit-2026-10-15.md) (what was broken and
fixed) and [../pr-scan.md](../pr-scan.md) (how PR mode works).*

## 1. Summary

1. **The run is reproducible.** Re-executing the frozen analysis commit
   reproduced every AnsibleGuard, GitLeaks, and review-range occurrence
   exactly (390,286 raw findings in both). Seven of 108,749 ansible-lint
   occurrences differed because of provider non-determinism; one cause
   (set-ordered messages) is fixed.
2. **Most AnsibleGuard output is not a defect claim.** Of 265,434 internal
   static-source occurrences, **181,937 (68.5 %) are optional-policy
   findings** (`missing-tags`, `unguarded-variable`,
   `variable-naming-convention`, …), and **54,196 (20.4 %) are UNCERTAIN**
   by the tool's own resolution model. The required, defect-claiming
   population is **83,497 occurrences over 52 rules**.
3. **Category rankings in the published charts are misleading.**
   "Correctness" appears as the second-largest category (54,382), but 95 % of
   it is the optional, 100 %-uncertain `unguarded-variable` rule; required
   correctness findings number 2,895.
4. **The population is highly concentrated.** The top 3 rules hold 65.8 % of
   internal findings and the top 10 hold 87.4 %; across repositories the Gini
   coefficient is 0.59 and the 20 largest repositories hold 38.6 %. Simple
   random sampling would mostly re-measure a few rules in a few repositories.
5. **Rare rules cannot get per-rule heldout estimates.** 20 of the 52 required
   rules have fewer than 30 heldout findings, often from 1–9 repositories.
6. **Several study results were artefacts that the tool or pipeline
   produced, not properties of the code under study** — whole-repository
   "changes" for review rules on shallow snapshots, provider-comparable
   tables that counted missing ansible-lint data as zero, ansible-lint
   rewriting the scanned checkouts, and PR comparisons that reported moved
   findings as hundreds of fixed+introduced pairs. All are fixed on branch
   `fix/v007-audit-2026-10-15`; results that depend on them must be
   regenerated with the fixed version.
7. **A precheck of 101 calibration findings** (AI, not human gold) found
   54 TP / 19 FP / 28 uncertain (74 % of decidable), and — more usefully —
   eleven distinct false-positive mechanisms, six of which are now fixed.
   28 % of items could not be decided, mostly because file-level "count=N"
   findings do not identify the offending task: **reviewability, not only
   precision, is a validation problem.**
8. **The validation design must change** (section 7): validate the fixed and
   frozen version, separate required from optional rules, sample by rule tier
   with repository caps, pool rare rules by family, estimate with design
   weights and repository-cluster bootstrap, validate review rules only on
   real PR ranges, and add PR-mode attribution and recall studies.

## 2. Data and reproduction

| Item | Value |
|---|---|
| Frozen population | 207 GitHub repositories (`study/manifests/github-v2-final-eligible.csv`), exact SHAs |
| Execution | 171 complete, 35 ansible-lint-partial, 1 timeout (`encapsulate-xyz/cosmos-ansible`) |
| Raw / canonical | 390,286 / 376,115 |
| AnsibleGuard internal static-source | 265,434 occurrences, 60 rules, 206 repositories |
| ansible-lint | 108,749 occurrences (83,411 from complete repositories) |
| GitLeaks | 1,434 |
| Review-range | 497 (artefactual; see 4.1) |
| Split | 144 calibration / 62 heldout repositories (189,029 / 76,405 internal occurrences) |

The reproduction is described in the audit (section 2). Its tables match the
frozen package; the analysis below uses the frozen aggregates.

## 3. What the run says

### 3.1 Policy and certainty

| Population | Occurrences | Share |
|---|---:|---:|
| Required (defect-claiming) | 83,497 | 31.5 % |
| Optional style/policy | 181,937 | 68.5 % |
| — of which `missing-tags` | 98,005 | 36.9 % |
| — of which `unguarded-variable` | 52,474 | 19.8 % |
| — of which `variable-naming-convention` | 24,121 | 9.1 % |
| CONFIRMED (resolution evidence resolved) | 203,812 | 76.8 % |
| UNCERTAIN | 54,196 | 20.4 % |
| EXPOSED / UNRESOLVED / ORDERED_CONFLICT | 6,251 / 997 / 178 | 2.8 % |

"CONFIRMED" means the detector's resolution evidence resolved; it is not
human confirmation. `unguarded-variable` and `unnecessary-set-fact` are
100 % UNCERTAIN.

Severity follows policy almost perfectly: optional findings are notes
(181,324 of 181,937), required findings are 7,015 errors, 47,622 warnings and
28,860 notes. **Exception:** 603 `credentials-leaking-in-log` findings are
`optional` yet `error`. Analysis of the run (see
[v007-results-analysis.md](v007-results-analysis.md) §2) shows this is not a
catalog inconsistency: policy is decided **per occurrence** from the tool's
resolution state, and these 603 are the cases where `no_log:` is a dynamic
expression the tool cannot resolve (`DYNAMIC_PROTECTION_UNKNOWN`), so they are
deliberately downgraded while keeping the rule's severity. (An earlier version
of this report called it an inconsistency; that was wrong.) The real problem
it exposed is that the PR ratchet blocked any introduced error regardless of
policy, so an undecidable finding could block a pull request; the policy now
never blocks on optional findings (secrets still always block).

### 3.2 Categories (internal static-source)

| Category | All | Required | Optional |
|---|---:|---:|---:|
| style | 148,858 | 24,626 | 124,232 |
| correctness | 54,382 | **2,895** | 51,487 |
| maintainability | 33,780 | 33,780 | 0 |
| security | 9,266 | 8,661 | 605 |
| compatibility | 7,257 | 7,257 | 0 |
| documentation | 5,084 | 1,285 | 3,799 |
| reliability | 2,858 | 2,858 | 0 |
| testing | 1,814 | 0 | 1,814 |
| structure | 1,686 | 1,686 | 0 |
| dependencies | 449 | 449 | 0 |

Among required findings the order is maintainability > style > security >
compatibility > correctness. Any statement such as "correctness is the
second most common problem" is unsupported by this run.

### 3.3 Rules

- Concentration: top 1 rule 36.9 %, top 3 65.8 %, top 5 74.5 %, top 10
  87.4 %, top 20 95.3 % of internal findings.
- Size classes (all 60 rules): 31 rules ≥ 500 findings, 15 rules 30–499,
  14 rules < 30 (`unused-handler` 29 … `broken-role-dependency` 1,
  `empty-abstraction` 1).
- Required rules only (52): 24 large, 15 mid, 13 rare.
- Required rules by family: maintainability/complexity 12, objective
  correctness 11, variable/reference 8, security 7, style/policy 7,
  structure/reuse 7.

### 3.4 Repositories

- Median 694 internal occurrences per repository; 10 repositories < 10,
  10 repositories ≥ 5,000.
- Gini 0.59; the 10 largest repositories hold 23 % and the 20 largest
  38.6 % of findings.
- Density: 102 of 206 repositories have 100–300 findings per 1,000 selected
  LOC; density is dominated by `missing-tags`, so it measures tag policy more
  than defect density.

### 3.5 Providers

ansible-lint findings are 28.9 % of canonical occurrences but exist for 171
repositories only; any cross-provider figure must use the 171 complete
repositories (fixed in the pipeline). External-tool overlap is not modelled;
the overlap chart is an explicit placeholder and should stay so until a rule
mapping is validated.

## 4. Problems that affected results

### 4.1 Artefacts produced by the tool or the pipeline

| Problem | Effect on the published run | Status |
|---|---|---|
| Review rules on shallow snapshots diff against the empty tree | `missing-release-note` in 190/206 repositories, `missing-test-update` 71, `untested-override-change` 58 describe whole repositories, not changes | fixed; review results of this run are not interpretable |
| Release notes recognized only in reno layout | further false `missing-release-note` | fixed |
| Provider-comparable tables included review rules and counted missing ansible-lint data as zero | lint prevalence 58.7 % instead of 70.8 %; category shares diluted | fixed |
| ansible-lint rewrote files in 5 checkouts (and its own config) | scanned content changed during the run; same 5 repositories again on reproduction | fixed (workspace guard) |
| ansible-lint reports task findings one task late | lint findings attached to the wrong task; dedup and changed-line mapping wrong | fixed |
| Set-ordered lint messages | unstable occurrence IDs between runs | fixed |
| Parent-fetch script mutated frozen checkouts (partial clones, double deepen) | review population changed after freezing; diffs not computable offline | state restored; script redesigned |

### 4.2 Charts — are they true?

Every chart in the package was checked against its data and its title.

| Chart | Verdict | Fix |
|---|---|---|
| 01 status, 02 raw vs canonical, 03 provider, 12 completeness | true | integer labels, single colour |
| 04 top rules, 05 prevalence | true numbers, misleading reading: optional and 100 %-uncertain rules dominate unmarked | rules labelled `[optional]` / `[N% uncertain]`; new **04b** without optional rules |
| 06 findings per repository | **false**: only 25 of 139 bins drawn (76 of 206 repositories) and bins re-sorted by count | complete logarithmic bins in order |
| 07 density | misleading: 25 highest-density repositories (outliers) shown as if a distribution | density distribution over all repositories |
| 08 severity, 09 confidence | **mislabelled**: "canonical occurrences" but plots internal static-source only; `error` drawn green | correct titles, ordinal order, semantic colours |
| 10 certainty | true, but "CONFIRMED" reads as validation | subtitle states meaning |
| 11 actionability | true | ordinal order, semantic colours |
| 13 runtime | bins re-sorted by count | time order; timeout bin named |
| 14 size vs findings | true | — |
| 15 heatmap | true raw counts; volume-driven | title states raw counts and selection |
| 16 overlap | honest placeholder | — |
| legacy `findings-by-category/severity/certainty/provider`, `top-rules` | **mix providers and review rules**; certainty pie says 83.6 % CONFIRMED vs 76.8 % for internal findings because external findings default to CONFIRMED | category pie uses internal population; other titles state the mixed population |

The fixes are in `scripts/study_reporting.py`, `scripts/v007_full_repro.py`,
and `scripts/study_pipeline.py`. Charts must be regenerated with
`--postprocess-only` from a restored run.

### 4.3 False-positive mechanisms (precheck)

`study/fp-precheck-v007-2026-10-15/` (AI precheck, calibration only):

| Mechanism | Examples | Status |
|---|---|---|
| Handlers imported via `import_tasks`, listen topics, notifies from included files invisible — `missing-handler` is an **error** | 3 | fixed |
| kubectl `-o` / `--output` treated as a file write → "mutating command" | 1 | fixed |
| Marker inside an identifier (`containerd-hack`) | 1 | fixed |
| Galaxy role `ns.name` treated as local role `name` | 1 | fixed |
| Wrong messages (`threshold=None`, "curl") | 4 | fixed |
| Module argument specs with `no_log` not recognized (`credentials-leaking-in-log`) | 2 | open |
| File-scoped reasoning for variables and registered results | 3 | open |
| Non-Ansible YAML analysed (`Taskfile.yml`) | 1 | open |
| Data fields mistaken for module arguments (`port: 0` in `set_fact`) | 2 | open |
| Path versus secret, local role pinning, `/sys` writes, controller env reads | 4 | open |
| File-level "count=N" findings that do not name the task | most "uncertain" | open (reviewability) |

## 5. Pull-request mode on real pull requests

Twenty-one real merged pull requests (the most recent qualifying merge of
every full-history calibration repository) were replayed through
`ansibleguard diff` (`study/pr-replay-v007-2026-10-15/`).

| Measure | Before the fixes | After |
|---|---:|---:|
| Aborted comparisons | 13 / 21 | 0 / 21 |
| Introduced / fixed findings | 462 / 422 | 46 / 7 |
| Moves recognized | — | 688 |
| Policy failures | 1 (false positive, `environment` list) | 0 |
| Clones modified / worktrees left | 0 / 0 | 0 / 0 |

Attribution of every introduced and fixed finding is supported by the diff
(46/46 introduced, 7/7 fixed after one manual check). The replay found four
PR-mode defects that synthetic tests had not exposed: comparisons aborted on
partial providers and unparseable non-Ansible YAML; moved findings were
reported as churn (identity and provider fingerprints include line numbers);
a valid `environment` list was an `error` that blocked a PR; and review rules
treated Kubernetes YAML, changelog fragments, and merge-commit messages as
reviewable changes. All are fixed. **Implication for validation:** PR-mode
attribution (RQ5) must be measured on real pull requests, and the review rules
must be validated only on real `base..head` ranges.


## 6. Consequences for validation

1. **Validate a frozen, fixed version.** The current pilot and split were
   built from the run with the artefacts above. The repository split is
   independent of the tool and stays valid; samples and contexts must be
   regenerated from a new frozen run of the fixed version (`v0.0.7.1`).
2. **Precision of what?** Optional-policy findings are not defect claims;
   UNCERTAIN findings are explicitly undecided by the tool. Pooling them with
   required findings would let `missing-tags` (a correct but optional policy)
   dominate any overall number.
3. **Concentration requires stratification and caps**; a uniform sample would
   be 37 % `missing-tags` and 39 % from 20 repositories.
4. **Rare rules need census and pooling**, and their estimates are
   descriptive with exact intervals.
5. **Reviewability is a measured property.** Items whose evidence does not
   identify the defect must be labelled `unreviewable`, counted, and fixed in
   the tool (file-level findings must name their subject).
6. **Review rules need real ranges**: validate them on replayed pull
   requests, never on snapshots.

## 7. Revised validation and sampling plan

> **Superseded in detail by [v007-validation-protocol.md](v007-validation-protocol.md)**,
> which classifies every rule by verification mode (deterministic predicate /
> threshold / semantic) and reduces the human design accordingly. The text
> below remains as the first version of the plan.

### 7.1 Research questions

- **RQ1 Precision.** For required rules, what fraction of reported
  occurrences are correct instances of the documented condition — per rule
  (large and mid tiers), per family, and overall (population-weighted)?
- **RQ2 Policy conformance.** For optional rules, is the finding a correct
  application of the stated policy (not "is it a defect")?
- **RQ3 Resolution accuracy.** For UNCERTAIN variable findings, how often is
  the uncertainty justified, and how often is the variable really undefined?
- **RQ4 Recall.** What fraction of codebook-defined smells present in a file
  does AnsibleGuard report, per family?
- **RQ5 PR attribution.** In real pull requests, are "introduced" findings
  caused by the change and are "fixed" findings really removed?
- **RQ6 Agreement and reviewability.** How reliably can two reviewers apply
  the codebooks, and what share of findings is reviewable from the evidence?

### 7.2 Versions and freezes

1. Merge `fix/v007-audit-2026-10-15`; document in the catalog that `policy` is
   a per-occurrence property driven by the resolution state.
2. Fix file-level findings so each names its subject task/variable/play
   (prerequisite for RQ1 on 11 structural/size rules).
3. Run the frozen corpus with the fixed version as `v0.0.7.1` (new run
   identity; provenance must pass the validation gate).
4. Freeze: tool commit, rule catalog hash, thresholds, codebooks, context
   generator, sampling seed. No detector change after the heldout sample is
   drawn; any change starts a new version.

### 7.3 Units and populations

| Population | Unit | Used for |
|---|---|---|
| Required static-source | canonical occurrence | RQ1 |
| Optional static-source | canonical occurrence | RQ2 |
| UNCERTAIN variable findings | canonical occurrence | RQ3 |
| Heldout files (stratified by kind) | file | RQ4 |
| Replayed real pull requests | introduced / fixed occurrence | RQ5, review rules |
| ansible-lint, GitLeaks | provider occurrence | out of scope for AnsibleGuard precision; overlap only with a validated mapping |

Calibration repositories are used for pilots, codebook refinement, threshold
calibration, and error analysis. **Heldout repositories are used once**, for
the final estimates, after the freeze.

### 7.4 Sampling design (heldout, primary estimates)

Strata are rules within families. Within each rule, sampling is
repository-balanced: at most **2 occurrences per repository per rule** in the
first pass (relaxed only when the rule cannot otherwise reach its target),
selected by seeded random order. This limits the effect of the 0.59 Gini.

Tiers are defined by the **heldout** population of each required rule (the
population the estimates are made on), as simulated in
[`study/validation-design-v007/`](../../study/validation-design-v007/README.md):

| Tier (heldout occurrences of a required rule) | Rules | Per-rule sample | Items | Reported as |
|---|---:|---|---:|---|
| Large (≥ 500) | 10 | 40, two-stage | 400 | weighted per-rule precision, effective-n Wilson interval (about ±8–14 pp at high precision, ±16–23 pp otherwise) |
| Mid (31–499) | 23 | 30, two-stage | 690 | same; family pooling for context |
| Census (≤ 30) | 18 | every heldout occurrence | 155 | complete enumeration, no sampling error; family pooling |
| Representative core | all required | 400, probability-proportional to rule size | 400 | overall precision (not yet simulated) |

Two-stage means: repositories sampled at random, then at most 2 occurrences
per repository (cap relaxed only to reach the target). Rules with fewer than 8
sampleable repositories (`excessive-nesting`, `deprecated-modules`) get exact
limits on the labelled items only and are labelled non-generalizable.

Items selected by both the core and a rule stratum are labelled once and
carry both inclusion probabilities.

Secondary heldout panels:

| Panel | Sample | Purpose |
|---|---|---|
| Optional rules (RQ2) | 20 per optional rule (8 rules) = 160 | policy-conformance rate |
| UNCERTAIN variables (RQ3) | 120, stratified by uncertainty source | resolution accuracy |
| Recall (RQ4) | 60 heldout files: 20 playbooks, 20 role task files, 20 vars/defaults | per-family recall; reviewers blind to tool output |
| PR attribution (RQ5) | ≥ 40 replayed PRs; 100 introduced + 100 fixed, PR-capped at 10 | attribution correctness |
| Review rules | census of review findings on the replayed PRs | precision of review rules on real ranges |

**Budget.** 1,245 per-rule items + 400 core + 640 secondary ≈ 2,300 items.
At ~2 minutes per item per reviewer with two reviewers and 20 % adjudication,
≈ 200 reviewer-hours. A reduced design (large 30 per rule, mid 20, core 300,
secondary panels halved) needs ≈ 125 hours. By √n scaling it widens the
per-rule intervals by about 15–22 % (not simulated); rerun the simulation
with the reduced targets before choosing it.

### 7.5 Labelling protocol

- **Labels.** `semantic_label ∈ {TP, FP, uncertain, unreviewable}`; separate
  `actionability`; `context_sufficient`; free-text reason with a reason code.
  `unreviewable` is a first-class outcome and is reported, not dropped.
- **Context bundles.** Frozen at the exact commit and redacted. Must contain:
  the cited role (not a grouping directory), paths beside the cited file
  first, the metric value and threshold for size/complexity rules, the
  release-note and test files for review rules, and the actual parent diff
  from the side repositories. Bundles fail validation if the cited subject
  is absent.
- **Reviewers.** Two independent reviewers (A/B) per item, blind to each
  other, to AI output, and to sampling weights; an adjudicator resolves
  disagreements; pre-adjudication labels are frozen and kept.
- **Pilot gate.** Per family, 30 calibration items (210 in total). Proceed
  when Cohen's κ ≥ 0.60 **and** Gwet's AC1 ≥ 0.70 (AC1 because high TP
  prevalence depresses κ); otherwise revise the codebook and re-pilot with new
  items. Pilot items never enter estimates.
- **Codebooks.** One per family plus rule overrides; every rule states its
  positive condition, common false-positive patterns (from 4.3), and when to
  use `uncertain` versus `unreviewable`. Codebook versions are hashed and cited
  by every label.
- **AI shadow.** Only after human labels and adjudication are frozen, on the
  identical evidence, stored separately; the existing Reviewer C precheck is
  excluded from all estimates.

### 7.6 Estimation

- Per-rule precision: **weighted** TP / (TP + FP) among decidable items with
  design weights `N_rj / n_rj` (a pooled proportion is biased by up to −0.21
  when precision varies with repository size), and a Wilson interval on the
  design-effective sample size (simulated coverage 89–96 %, median 93 %);
  `uncertain` and `unreviewable` rates reported beside it. Sensitivity: worst
  case (`uncertain` as FP) and best case.
- Family and overall precision: stratified estimator
  p̂ = Σ_h W_h p̂_h with W_h = N_h / N over required rules; the
  representative core gives an independent design-based check.
- Intervals: repository-cluster bootstrap (resampling sampled repositories)
  for the variance, then the effective-n Wilson interval for rules. The
  overall interval was ~90 % in simulation, so its nominal level must be
  calibrated on the simulation before use.
- Recall: per family, with file-cluster bootstrap; reported with the share of
  smells outside any implemented rule.
- Agreement: κ, AC1, PABAK, raw agreement, per family and per rule (when
  n ≥ 20), before adjudication.

### 7.7 Threats to validity and mitigations

| Threat | Mitigation |
|---|---|
| Version drift between labelled and published tool | single frozen version; provenance gate must pass |
| Heldout leakage | heldout opened only for final sampling; this audit's precheck used calibration repositories only |
| Repository concentration | per-repository caps; cluster bootstrap |
| Rule concentration | rule strata; optional rules separated |
| Context insufficiency | bundle validator; `unreviewable` label; tool fix for file-level findings |
| Rater drift and learning | pilot gate; shuffled order; 10 % duplicate items to measure intra-rater stability |
| AI contamination | AI labels only after gold; separate storage |
| Provider non-determinism | ansible-lint excluded from AnsibleGuard precision; determinism report per run |
| Selection of repositories | report as the frozen selected population, not "Ansible in general" |

### 7.8 Deliverables

1. `v0.0.7.1` frozen run with passing validation gate and regenerated charts.
2. Revised codebooks and context generator; pilot 2 with agreement report.
3. Heldout samples (primary + secondary) with inclusion probabilities.
4. Frozen A/B labels, adjudication, agreement report.
5. Precision, policy-conformance, resolution-accuracy, recall, and
   PR-attribution reports with cluster-bootstrap intervals.
6. AI-shadow comparison (after gold).
