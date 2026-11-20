# v0.0.7 207-Repository Pre-Benchmark Readiness Report

## Decision

The diagnostic corpus run is suitable for planning and sampling, but it is not
yet publication-ready. Of 207 frozen repositories, 206 have analyzable internal
results, one timed out, and ansible-lint is complete for 171 repositories and
partial for 35. Failed and partial observations are now represented explicitly
and are not treated as zero findings.

The generated study report is:

- `study/runs/v007-207/report/FULL_STUDY_REPORT.md`

The calibration and agreement procedure is:

- `docs/study/threshold-calibration-plan.md`

## Run status

| Measure | Result |
|---|---:|
| Frozen repositories | 207 |
| Internal-analyzable repositories | 206 |
| Complete across required/optional providers | 171 |
| Partial because of ansible-lint | 35 |
| Failed repository scans | 1 |
| Raw findings | 390,441 |
| Canonical occurrences | 376,271 |
| Internal static-source occurrences | 265,586 |
| ansible-lint occurrences, all output | 108,757 |
| ansible-lint occurrences on completed repositories | 83,419 |
| GitLeaks whole-repository occurrences | 1,434 |
| Git-history review occurrences | 494 |
| Uncertain occurrences | 54,443 |

The failed repository is `encapsulate-xyz/cosmos-ansible`. It timed out after
1,800 seconds. A retry reused its completed parse cache but still did not
produce final artifacts. This is a detector/indexing performance case, not a
clean scan, and remains a missing observation.

## The eight remediation steps

### 1. Current and historical artifact layouts

Validation and aggregation now resolve both the current flat v0.0.7 artifacts
(`findings.json` and `occurrences.json`) and historical nested artifacts
(`raw/findings.json` and `canonical/occurrences.json`). A regression test covers
the current layout.

### 2. Separate analysis populations

The aggregate no longer combines fundamentally different denominators. It now
exports separate populations for internal selected-source analysis,
ansible-lint, whole-repository GitLeaks, Git-history review rules, uncertain
findings, and provider-comparable results. Selected YAML LOC normalization is
used only for internal and ansible-lint source populations.

### 3. Correct review-rule classification

The 494 Git-history findings are now classified as `scan_mode=review` instead
of source findings:

| Review concept | Occurrences |
|---|---:|
| missing-release-note | 189 |
| commit-message-format | 142 |
| missing-test-update | 70 |
| untested-override-change | 56 |
| missing-bug-reference | 37 |

### 4. Correct missing-data denominators

Every grouped summary reports eligible and missing repository counts. The
failed repository is excluded from analyzable denominators rather than assigned
zero findings. Repository prevalence, median, Q1, and Q3 include zero counts
only for eligible repositories with a completed observation.

### 5. Isolate incomplete providers

The 35 partial ansible-lint repositories remain available as diagnostic output
but are excluded from provider-comparable estimates. Separate `all` and
`comparable` exports preserve both views. GitLeaks completed for all 206
analyzable repositories.

### 6. Identify concentrated provider outliers

`ansible-lint/yaml[quoted-strings]` contributes 2,776 findings from one
repository. The rule affects only 1 of the 171 ansible-lint-complete
repositories. It must be reported as a concentrated repository/rule effect and
must not be interpreted as corpus-wide prevalence. Repository-weighted
quartiles and prevalence are now included beside raw totals.

### 7. Identify dominant internal rules

Three rules contribute 174,847 internal source occurrences, about 65.8% of the
internal population:

| Stable rule | Occurrences | Internal share |
|---|---:|---:|
| missing-tags | 98,005 | 36.90% |
| unguarded-variable | 52,721 | 19.85% |
| variable-naming-convention | 24,121 | 9.08% |

This concentration means raw pooled totals are not sufficient for threshold or
quality claims. The benchmark must report per-rule/per-concept and
repository-weighted results. `missing-tags` is an optional low-confidence
policy signal and must not be presented as 98,005 confirmed defects.

### 8. Expose uncertain semantic concepts

The report now includes concept-level tables and a concept chart. The stable
configuration rule `ansibleguard/unguarded-variable` was already divided by
the backend; the older rule-level table hid that distinction:

| Semantic concept | Occurrences | Meaning |
|---|---:|---|
| missing-internal-variable | 997 | No internal definition or external-input uncertainty was found; actionable candidate, but currently represented as `UNRESOLVED`, not human-confirmed. |
| undeclared-input-contract | 34,006 | May be an input to a role, playbook, or task fragment, but no visible default or explicit contract was found. |
| unresolved-runtime-input | 17,718 | May be supplied by inventory, a caller, facts, dependencies, dynamic includes, or other runtime context. |

The last two concepts are marked uncertain because static analysis cannot see
every runtime variable source. Uncertainty can be introduced by dynamic
includes or roles, dynamic `vars_files`, dynamic inventory, external role
dependencies, custom module facts, inventory precedence, and caller-provided
role/playbook/task-fragment inputs. “Uncertain” therefore means “insufficient
static evidence to prove either missing or safely defined”; it does not mean
true positive or false positive.

All uncertain output contains the following concepts:

| Concept | Uncertain occurrences |
|---|---:|
| undeclared-input-contract | 34,006 |
| unresolved-runtime-input | 17,718 |
| unnecessary-set-fact | 2,106 |
| credential-log-exposure | 603 |
| variable-use-before-definition | 10 |

These cases must form separate sampling strata during human evaluation. Only
adjudicated binary labels may enter precision, recall, and F-score calculations;
unresolved cases must be disclosed rather than silently counted as errors.

## Cleanup performed

The authoritative manifests were preserved, including the historical
149-repository manifest. Superseded generated scans were permanently removed:

- all `study/runs/v0061-*` directories;
- `study/snapshots-v007-207`;
- `study/snapshots-offline-lint`;
- `study/snapshots`.

The current structured run `study/runs/v007-207`, the frozen manifests, and
derived `study/analysis` evidence were retained. The deleted generated scans
are not recoverable locally, but can be regenerated from their manifests and
commits. Available disk space increased from approximately 6.3 GB to 43 GB.

## Verification

- Study-pipeline regression tests: 7 passed.
- Full test suite: 1,008 passed, 2 skipped.
- `git diff --check`: passed.
- Regenerated aggregate and report: completed.
- Validation status: failed for publication readiness because one repository is
  missing; 35 optional ansible-lint providers are partial.

## Before threshold benchmarking

Use the diagnostic output to design strata, but do not claim precision or
recall from it. The next benchmark stage must use the frozen plan: extract the
numeric populations, generate box plots and Q1/Q2/Q3 candidates, split at the
repository level, obtain independent blinded human labels until Cohen's kappa
reaches at least 0.80 on a fresh pilot, repair systematic detector mechanisms,
then score frozen thresholds on adjudicated labels. An LLM comparison is a
separate human-to-AI agreement experiment and is not needed to calculate
threshold metrics.
