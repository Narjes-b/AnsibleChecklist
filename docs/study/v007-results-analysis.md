# v0.0.7 full run: results analysis by category

*2026-10-16. Run `v007-full-repro-2026`, re-executed from the frozen analysis
commit `d1711f90` (all AnsibleGuard, GitLeaks and review occurrences identical
to the original run). Every number below is computed from the run's
occurrence exports by `scripts/v007_results_analysis.py`; tables are in
[`study/analysis-v007-2026-10-16/`](../../study/analysis-v007-2026-10-16/).
Key figures were recomputed independently from the raw CSV by a second
script and matched exactly.*

**Counts are detector output, not validated defects.** No precision, recall or
agreement figure exists for v0.0.7 yet; the study is at the stage of
calibration preparation. This document describes what the tool *reports*, what
that does and does not allow one to conclude, and what the validation must
therefore do.

## 0. How to read the numbers

| Term | Meaning here |
|---|---|
| Occurrence | one canonical AnsibleGuard static-source finding (265,434 in 206 analyzable repositories; the 207th timed out and is a missing observation, not zero) |
| Required / optional | the tool's per-**occurrence** policy. Optional = style policy or a case the tool cannot decide; it is reported but not claimed as a defect. 83,497 required (31.5 %), 181,937 optional (68.5 %) |
| Certainty | the tool's own resolution state: `CONFIRMED` (evidence resolved), `UNCERTAIN` (cannot decide), `EXPOSED`/`UNRESOLVED`/`ORDERED_CONFLICT` (proved or candidate). **Not human confirmation** |
| Heldout / calibration | frozen repository split, 62 / 144 repositories; heldout contexts have not been opened |
| Provider-complete | the 171 repositories where AnsibleGuard, ansible-lint and GitLeaks all completed; the only valid population for cross-provider statements |

## 1. Headline

| | Value |
|---|---:|
| Occurrences (all / required / optional) | 265,434 / 83,497 / 181,937 |
| Rules with ≥ 1 occurrence | 60 (53 with required occurrences) |
| Repositories (analyzable / with ≥ 1 required) | 206 / 197 |
| Repository concentration | Gini 0.586; 10 largest repositories hold 23.0 % |
| Median required findings per 1,000 selected LOC | 51.2 (IQR 28.2–75.8; maximum 326.8) |
| Required findings from rules the catalog marks experimental / candidate | 5,375 (6.4 %) / 997 (1.2 %) |

By category (all columns are occurrences; prevalence = share of the 206
repositories with ≥ 1; density = per 1,000 selected LOC, median and IQR over
repositories; ρ = Spearman correlation between repository size and count):

| Category | Total | Share | Required | Optional | Uncertain % | Prevalence | Median per affected repo | Density | ρ(LOC) | Top rule (share of category) | Top-10 repos |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---|---:|
| style | 148,858 | 56.1 % | 24,626 | 124,232 | 1.4 | 94.7 % | 528 | 114 (73–161) | 0.88 | missing-tags (65.8 %) | 22.6 % |
| correctness | 54,382 | 20.5 % | **2,895** | 51,487 | 96.5 | 92.2 % | 89 | 19.6 (6.0–46.3) | 0.76 | unguarded-variable (96.5 %) | 34.9 % |
| maintainability | 33,780 | 12.7 % | 33,780 | 0 | 0 | 93.7 % | 81 | 20.0 (11.2–29.8) | 0.92 | large-task (36.1 %) | 29.4 % |
| security | 9,266 | 3.5 % | 8,661 | 605 | 6.5 | 86.4 % | 18 | 3.6 (1.5–7.2) | 0.78 | credentials-leaking-in-log (74.0 %) | 38.5 % |
| compatibility | 7,257 | 2.7 % | 7,257 | 0 | 0 | 71.4 % | 14 | 1.3 (0–8.2) | 0.45 | loop-legacy-syntax (87.9 %) | 42.1 % |
| documentation | 5,084 | 1.9 % | 1,285 | 3,799 | 0 | 72.8 % | 19 | 1.7 (0–6.1) | 0.66 | role-readme-absent (61.4 %) | 32.6 % |
| reliability | 2,858 | 1.1 % | 2,858 | 0 | 0 | 69.4 % | 6 | 0.7 (0–2.3) | 0.64 | silent-error-suppression (70.5 %) | 41.9 % |
| testing | 1,814 | 0.7 % | 0 | 1,814 | 0 | 47.1 % | 5 | 0 (0–1.1) | 0.43 | molecule-test-absent (100 %) | 48.9 % |
| structure | 1,686 | 0.6 % | 1,686 | 0 | 0 | 79.6 % | 5 | 0.9 (0.3–1.8) | 0.77 | missing-abstraction (97.7 %) | 30.1 % |
| dependencies | 449 | 0.2 % | 449 | 0 | 0 | 15.5 % | 2 | 0 (0–0) | 0.24 | unpinned-ansible-dependency (100 %) | 90.9 % |

## 2. Cross-cutting observations

1. **The headline category ranking is misleading.** Style and correctness
   are 76.6 % of occurrences, but 124,232 of the style findings are optional
   policy and 51,477 of the correctness findings are one rule's uncertain
   cases. Among *required* findings the order is maintainability (33,780) >
   style (24,626) > security (8,661) > compatibility (7,257) > correctness
   (2,895) > reliability (2,858) > structure (1,686) > documentation (1,285) >
   dependencies (449); testing has none.
2. **Policy is decided per occurrence, not per rule.** Three rules are
   mixed: `unguarded-variable` (997 required warnings, 51,477 optional notes),
   `credentials-leaking-in-log` (6,251 required, 603 optional) and
   `variable-use-before-definition` (178 / 10). The optional ones are the
   cases the tool downgrades when it cannot decide (`DYNAMIC_PROTECTION_UNKNOWN`,
   `RUNTIME_CONTEXT_UNCERTAIN`). So the 603 "optional errors" are not an
   inconsistency but deliberate: a dynamic `no_log:` expression cannot be
   proven either way. Any statistic must be computed on the occurrence's
   policy, never on a rule label.
3. **What "uncertain" is made of** (54,196 occurrences, 95 % `unguarded-variable`):
   the most frequent uncertainty sources are `possible_required_role_input`
   (28,433), `possible_playbook_input` (8,879), `static_include_execution_context`
   (6,133), `dynamic_include` (5,039) and `conditional_runtime_definition`
   (3,872). Most of the uncertainty is the ordinary Ansible pattern of a role
   expecting its caller to supply variables; it is a property of the language,
   not a defect rate.
4. **More than half of the required findings are threshold-driven.** Fifteen
   rules (large-task, complex-expression, large-playbook, complex-playbook,
   large-play, missing-abstraction, duplicated-code, high-coupling,
   undocumented-complex-task, long-statement, long-task-name, excessive-nesting,
   insufficient-modularization, inconsistent-naming-convention,
   become-scope-too-broad) produce 45,677 required findings (54.7 %). For them
   "is the finding correct?" is trivially yes when the metric is computed
   correctly; the real question is whether the *threshold* identifies something
   a maintainer would act on. The default thresholds
   (`src/ansibleguard/thresholds.csv`, e.g. 15 LOC per task, 75-character task
   names, 110 LOC per playbook, 4 imports / 5 roles) are inherited defaults,
   not calibrated on this corpus.
5. **Severity is not confidence.** There are 7,618 errors, but only 345 are
   high confidence, 5,972 medium and 1,301 low. Warnings are 47,632 and notes
   210,184; 28,860 *required* findings are notes. A PR gate that blocks on
   `error` is therefore blocking on a mixture of confidence levels.
6. **Findings concentrate in a few rules and repositories.** Top 1, 3, 10 and
   20 rules hold 36.9 %, 65.8 %, 87.4 % and 95.3 % of occurrences; the 20
   largest repositories hold 38.6 %. Ten required rules have one repository
   holding ≥ 40 % of their occurrences (`excessive-nesting` 72 %,
   `unexpected-task-location` 83 %, `missing-handler` 63 %, `overriden-keys`
   50 %, `unscoped-shell-variable` 46 %, `unsafe-file-write` 43 %,
   `inconsistent-naming-convention` 40 %, and three rules confined to a single
   repository).
7. **Counts scale with code size**, most strongly for maintainability
   (ρ = 0.92) and style (0.88); density per 1,000 LOC is the comparable
   measure, and compatibility, dependencies and testing depend little on size
   (ρ 0.24–0.45), i.e. on repository age or convention instead.
8. **A location can carry several findings.** 5,425 rows share project, rule,
   file and line with another row, always with a different message
   (98 % `unguarded-variable`: several variables on one line). They are not
   duplicates, but they mean the review unit for variable rules is
   (location, variable), and a reviewer must be told which variable.
9. **Experimental and candidate rules are 7.6 % of required findings**
   (`silent-error-suppression` 2,016, `undocumented-complex-task` 1,285,
   `shell-instead-of-module` 687, `high-coupling` 480, `insecure-permissions`
   450, `default-credentials` 248, `variable-use-before-definition` 178,
   `unstructured-module` 31, and `unguarded-variable`'s 997 required cases).
   They are the rules the authors themselves are least sure of and should be
   labelled first.
10. **The split is balanced enough.** Median selected LOC 3,686 (calibration)
    vs 3,227 (heldout); median required density 53.3 vs 46.7 per KLOC.

## 3. By category

### 3.1 Style — 148,858 (56.1 %), required 24,626

- Two thirds is `missing-tags` (98,005 optional, 192 repositories, median 320
  per affected repository): a policy about being able to select tasks with
  `--tags`, true of any untagged task. With `variable-naming-convention`
  (24,121) and `unnecessary-set-fact` (2,106; all uncertain) the optional
  part is 124,232.
- Required style: `unnamed-task` 10,244 (113 repositories), `long-statement`
  5,530, `long-task-name` 5,236, `unnamed-play` 1,661, `duplicate-task-names`
  1,282, `unnecessary-abstraction` 607, `inconsistent-naming-convention` 52,
  `missing-file-extension` 14.
- All findings are notes. Density (median 114 per KLOC) tracks code size
  (ρ 0.88), so the category mostly measures how much YAML a repository has and
  whether it tags.
- Mechanisms: `unnamed-task`, `unnamed-play`, `duplicate-task-names` and
  `missing-file-extension` are parser predicates; `long-*` are threshold
  rules (160 characters, 75 characters). No false-positive mechanism was found
  in the calibration precheck.
- **For validation:** verify the predicates automatically against an
  independent implementation; ask humans only about usefulness of the two
  thresholds.

### 3.2 Correctness — 54,382 (20.5 %), required 2,895

- 96.5 % is `unguarded-variable` (52,474; 186 repositories). Of these 51,477
  are optional and uncertain (role/playbook inputs, includes); only 997 are
  required warnings (`CANDIDATE_MISSING`: the tool found no visible source).
- Required correctness is 2,895: `non-idempotent-command` 1,476,
  `unguarded-variable` 997, `variable-use-before-definition` 178,
  `unscoped-shell-variable` 80, `role-variable-precedence-collision` 50,
  `invalid-task-attribute-type` 47, `overriding-facts` 23,
  `missing-bool-filters` 19, `missing-handler` 8, `overriden-keys` 6,
  `shell-environment-export` 6, `invalid-numeric-value` 4,
  `broken-role-dependency` 1. Eleven of thirteen rules are rare (≤ 80 findings).
- The 66 errors are exactly the rare deterministic rules
  (`invalid-task-attribute-type` 47, `missing-handler` 8, `overriden-keys` 6,
  `invalid-numeric-value` 4, `broken-role-dependency` 1).
- Calibration precheck found real defects here: handlers imported from another
  file (fixed), `port: 0` as a data field mistaken for a port (open), and the
  attribute-type rule rejecting a valid list for `environment` (fixed).
- **For validation:** the variable rules need the dedicated resolution study
  (`study/validation-v007-variable-resolution/`) and a (location, variable)
  unit; all rare rules are census; do not report a category-level figure.

### 3.3 Maintainability — 33,780 (12.7 %), all required

- `large-task` 12,179 (184 repositories), `complex-expression` 11,003,
  `large-playbook` 3,100, `complex-playbook` 2,514, `large-play` 1,444,
  `unused-registered-variable` 1,210, `shell-instead-of-module` 687,
  `duplicated-code` 603, `high-coupling` 480, `deprecated-modules` 338, and
  small ones.
- 32,547 warnings and 1,233 notes; no errors. Strongest size dependence of
  any category (ρ 0.92).
- Twelve of fifteen rules are metric/threshold rules, so this category is
  mostly a statement about the default thresholds. `excessive-nesting` (57
  findings, 5 repositories, one holds 72 %) and `deprecated-modules` (338 in
  22 repositories; 4 heldout) cannot be generalised.
- **For validation:** threshold-calibration panels, not precision sampling;
  only `unused-registered-variable` and `shell-instead-of-module` need
  semantic labels.

### 3.4 Security — 9,266 (3.5 %), required 8,661

- `credentials-leaking-in-log` is 74 % (6,854: 6,251 `PROVEN_EXPOSED`
  required, 603 optional dynamic-`no_log`), then `plaintext-sensitive-variable`
  668, `missing-validate-certs` 577, `become-scope-too-broad` 467,
  `insecure-permissions` 450, `default-credentials` 248, `vault-inline-overload` 2.
- The only category where errors dominate: 7,552 errors, 1,712 warnings. Yet
  the largest rule rests on one mechanism ("no `no_log` proven"), and two of
  two sampled cases were judged false positives in the precheck because the
  module's own argument spec already hides the secret (confirmed for
  `ansible.builtin.uri`: `url_password`, alias `password`, is `no_log`;
  the FreeIPA case rests on the module source; the rule does not yet read
  argument specs, open). Category-level precision is therefore
  mostly the precision of this rule.
- `default-credentials` and `insecure-permissions` are experimental.
  GitLeaks adds 1,434 findings in 96 repositories (separate tool; not part of
  these counts).
- **For validation:** use ansible-core's argument specs as a partial oracle for
  `credentials-leaking-in-log`; humans for the rest; keep secrets out of
  review bundles (redaction is already required).

### 3.5 Compatibility — 7,257 (2.7 %), required

- `loop-legacy-syntax` 6,376 (141 repositories) and `redirected-module` 881.
  All warnings/notes.
- The claim depends on a target Ansible version that is not part of the
  finding: `with_items` still works in current ansible-core; it is a
  modernisation notice, not a runtime error. Low size dependence (ρ 0.45) and
  p25 = 0: it reflects repository age and style.
- **For validation:** the codebook must state the version policy; both rules
  are deterministic predicates with ansible-core routing metadata as oracle.

### 3.6 Documentation — 5,084 (1.9 %), required 1,285

- `role-readme-absent` 3,123 and `galaxy-meta-incomplete` 676 are optional;
  the required part is the experimental `undocumented-complex-task` (1,285, 98
  repositories).
- File-level findings sit on line 1 of an arbitrary task file, so a reviewer
  cannot tell what is being asserted.
- **For validation:** existence predicates verified automatically; the
  experimental rule needs a human judgement of "complex enough to need a
  comment".

### 3.7 Reliability — 2,858 (1.1 %), required

- `silent-error-suppression` 2,016 (experimental), `read-only-command-change`
  835, `unsafe-file-write` 7. The precheck found that the read-only message
  claimed "curl" for every command (fixed).
- **For validation:** semantic labels for the first two.

### 3.8 Testing — 1,814 (0.7 %), optional only

- `molecule-test-absent` in 97 repositories (47.1 %). A policy about test
  scaffolding, not a defect; zero required findings.

### 3.9 Structure — 1,686 (0.6 %), required

- `missing-abstraction` 1,648 (97.7 %; a file with more than 10 leaf tasks and
  no roles or includes), `unstructured-module` 31, `unexpected-task-location` 6,
  `empty-abstraction` 1. Three of four rules are census-size.
- **For validation:** the layout rules are file-system predicates; the
  size rule is a threshold.

### 3.10 Dependencies — 449 (0.2 %), required

- Only `unpinned-ansible-dependency`, in 32 repositories (15.5 %); the 10 largest
  repositories hold 90.9 % (Gini 0.96). Heldout: 163 findings in 11
  repositories.
- **For validation:** predicate verified automatically; report as a per-
  repository fact, not a rate.

## 4. Providers (171 provider-complete repositories)

| Category | AnsibleGuard (all / required) | ansible-lint | GitLeaks |
|---|---:|---:|---:|
| style | 116,153 / 19,859 | 23,631 | – |
| correctness | 38,340 / 2,084 | 10,147 | – |
| maintainability | 26,991 / 26,991 | 487 | – |
| compatibility | 4,660 / 4,660 | 21,463 | – |
| security | 6,819 / 6,389 | 2,686 | 1,155 |
| reliability | 1,962 / 1,962 | 394 | – |
| (lint) | – | 24,604 | – |

Categories are not equivalent across tools (ansible-lint "compatibility" is
mostly FQCN naming; "lint" has no AnsibleGuard counterpart), and the overlap
is not modelled: no cross-provider agreement or "extra detections" statement
is supported. Review-range findings (497) are excluded from every comparison.

## 5. Repositories

- 8 repositories have no finding and 9 have no required finding.
- Densest (required per 1,000 LOC): `TerryHowe/ansible-modules-hashivault`
  (327, heldout), `grycap/im` (199), `ansible-lockdown/RHEL7-STIG` (173),
  `mother-of-all-self-hosting/mash-playbook` (171, heldout).
- Largest absolute: `spantaleev/matrix-docker-ansible-deploy` (3,429
  required), `redhat-openstack/infrared` (2,908), `Linuxfabrik/lfops` (2,858),
  `IBM/ibm-spectrum-scale-install-infra` (2,806).
- Low-density outlier: `freifunk-berlin/bbb-configs` (22,420 selected LOC but
  only 85 required findings, 3.8 per KLOC against a median of 51), worth
  inspecting for selected-file coverage.

## 6. Charts: are they true?

**Correction 2026-10-17.** Chart 04b ("required only") had dropped whole rules instead of counting required occurrences, so it showed 6,854 `credentials-leaking-in-log` (6,251 required + 603 optional), 188 `variable-use-before-definition` (178 required) and listed `unnecessary-set-fact`. It is regenerated per occurrence by `scripts/v007_charts.py`. All 17 chart datasets were then recomputed from the raw v0.0.7 re-execution and compared with the published CSVs: the other 16 charts have identical values. `scripts/v007_charts_check.py` checks a chart set against the run's own summaries (all checks pass for v0.0.7 and v0.0.7.1).

All charts were rendered and looked at (not only their SVG source). Original
set: wrong titles/populations, a distribution chart drawing 25 of 139 bins,
meaningless colours (error in green), decimals on counts, an unreadable
heatmap and a scatter without ticks. The corrected set
(`study/analysis-v007-2026-10-16/charts/`, 17 charts, generated from the
fixed code) was spot-checked value by value against its CSV by an independent
review, states each population, and uses ordinal order and colour only where they carry meaning.
Remaining caveats: bins are unequal, so bar length is not density; chart 03
mixes provider populations by necessity and says so.

## 7. What these results cannot say

- Anything about **precision, recall or usefulness** of any rule.
- A **defect rate** per category: counts are detector output; optional,
  threshold and uncertain findings are not defect claims.
- **Cross-provider** agreement.
- Anything about **review-range** rules in this run: they were evaluated on
  shallow snapshots (fixed in the tool; rerun needed).
- Generalisation beyond the **frozen selected repositories**.

## 8. Reproduce

```bash
python scripts/v007_results_analysis.py \
  --run study/runs/v007-full-repro-2026 \
  --output-dir study/analysis-v007-2026-10-16
python scripts/v007_verification_plan.py \
  --rule-profile study/analysis-v007-2026-10-16/rule-profile.csv \
  --output study/validation-design-v007/rule-verification-plan.csv
```

Tables: `category-overview.csv`, `rule-profile.csv`, `family-overview.csv`,
`crosstab-category-policy-severity-confidence-certainty.csv`,
`repository-profile.csv`, `provider-by-category-complete-repositories.csv`.
