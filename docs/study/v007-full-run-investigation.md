# AnsibleGuard v0.0.7 — Full-Run Investigation, Reproducibility Audit, Mapping Plan, and Repair Roadmap

**Project:** AnsibleChecklist / AnsibleGuard  
**Study run:** `v007-full-repro-2026`  
**Frozen population:** 207 repositories  
**Original v0.0.7 baseline:** `ac82dd6af849552391c876876d63f28adeb7640f`  
**Analysis commit recorded by the run:** `3391f2756c1079a7da9d2fd94c7a0960ff526ebd`  
**Final package-builder / current reproducibility-branch head:** `d1711f90b7ab45fe80f429927c310cf58a323f77`  
**Branch inspected:** `chore/v007-reproducible-full-run`  
**Purpose of this report:** explain exactly what the run measured, what worked, what did not work, which results can currently be trusted, which presentation artifacts are wrong, what mappings still need to be implemented, and what should be repaired before final scientific validation.

---

# 1. Executive conclusion

The v0.0.7 run is **substantively useful** and represents a major improvement over the earlier study state. The most important achievement is not the raw number of findings; it is that AnsibleGuard's internal analysis completed on **206 of 207 frozen repositories (99.52%)**, with raw evidence preserved, provider states separated, canonical occurrence identities generated, and deterministic post-processing demonstrated.

However, the result package is **not yet publication-clean**. There are two different layers:

1. **The underlying aggregate study data is largely coherent and useful.**
2. **Several generated helper tables/charts and parts of the reproducibility/CI metadata are incorrect or incomplete.**

The biggest reporting defects found are:

- the numbered `04-top-rules` chart is wrong because short internal rule IDs are joined against provider-prefixed canonical rule IDs;
- the failed repository is converted to `0` findings in some chart source data even though it should remain missing;
- the general findings-density chart mixes providers that have incompatible analysis populations;
- the provider-completeness chart uses overlapping categories and sums to more than 207;
- the "uncertain vs actionable" chart does not actually calculate actionability;
- external-tool overlap is intentionally **not modeled**, so the current zero bar means "no mapping exists", not "zero overlap";
- a sanity check intended to ensure incomplete-provider findings are not zeroed is a tautology because the condition contains `or True`;
- sanity checks verify existence of chart data and SVGs, not semantic correctness of chart values;
- PNG generation is optional and no PNGs were produced because CairoSVG was not available;
- the canonical run used Python 3.14.7 while the reproduction guide tells collaborators to create Python 3.12 environments;
- the run does not record an exact GitLeaks version;
- the current GitHub test suite passes, but CI remains red because generated documentation and `rule-catalog.json` are stale;
- CI uses dependency versions different from the frozen study environment.

None of those presentation/reproducibility defects proves that the detector findings are wrong. They mean that **the next task should repair the result/reproducibility layer without changing detector semantics, then freeze one final canonical result package before accuracy validation.**

---

# 2. Evidence hierarchy used in this investigation

Not every artifact should have equal authority.

## Tier A — authoritative analytical evidence

Prefer these for numerical claims:

- `aggregate/all-canonical-occurrences.csv`
- `aggregate/all-raw-findings.csv`
- `aggregate/all-internal-source-occurrences.csv`
- `aggregate/all-ansible-lint-occurrences.csv`
- `aggregate/all-ansible-lint-comparable-occurrences.csv`
- `aggregate/all-gitleaks-occurrences.csv`
- `aggregate/rule-summary.csv`
- `aggregate/concept-summary-internal.csv`
- `aggregate/resolution-summary.csv`
- `aggregate/provider-health.csv`
- `aggregate/repository-summary.csv`
- `tables/repository-execution-status.csv`

These are preferable to a chart when the chart disagrees with the aggregate.

## Tier B — generated analytical reports

Useful, and mostly consistent with Tier A:

- `FULL_RUN_REPORT.md`
- `report/FULL_STUDY_REPORT.md`
- `DETERMINISM_REPORT.md`
- `SANITY_CHECKS.md`

Their prose and tables must still be reconciled with the underlying CSVs.

## Tier C — presentation artifacts

These are derived convenience artifacts:

- `charts/data/*.csv`
- `charts/svg/*.svg`
- `charts/png/*`

Several of these were found to be wrong or semantically misleading, so they must not override Tier A.

## Tier D — repository / CI state

Used to audit reproducibility and implementation:

- branch `chore/v007-reproducible-full-run`
- `scripts/v007_full_repro.py`
- `scripts/study_pipeline.py`
- `scripts/study_reporting.py`
- `study/configs/v007-207.yaml`
- `docs/study/v007-reproduce-full-run.md`
- GitHub Actions run for branch head `d1711f90...`

---

# 3. What the full run actually did

The intended pipeline is:

```text
207 frozen repository identities
        ↓
exact frozen commit checkout
        ↓
file classification
        ↓
AnsibleGuard internal analysis
        ↓
external providers
    ├── ansible-lint
    └── GitLeaks
        ↓
raw findings
        ↓
canonical occurrence identity / deduplication
        ↓
provider-aware aggregation
        ↓
tables + reports + chart source data
        ↓
charts
        ↓
sanity checks
        ↓
deterministic re-postprocessing check
        ↓
portable archive + checksums
```

The study correctly distinguishes core AnsibleGuard analysis from optional/external provider completeness. This distinction is essential when interpreting the 35 partial repositories.

---

# 4. Repository execution health

## 4.1 Overall repository state

| State | Repositories | Percentage |
|---|---:|---:|
| Complete | 171 | **82.61%** |
| Partial | 35 | **16.91%** |
| Failed / timed out | 1 | **0.48%** |
| Total | 207 | 100% |

A "complete" repository means the expected internal analysis and provider work completed.

A "partial" repository in this run does **not** mean AnsibleGuard's internal detector stopped halfway. For all 35 partial repositories:

```text
AnsibleGuard internal analysis = completed
GitLeaks                       = completed
ansible-lint                   = partial
```

Therefore the more important core-tool result is:

| Measure | Result |
|---|---:|
| Repositories with usable AnsibleGuard internal analysis | 206 / 207 |
| Core AnsibleGuard execution coverage | **99.52%** |

That is much stronger than simply reporting the 82.61% all-provider completion rate.

## 4.2 The one failed repository

The failed repository is:

`encapsulate-xyz/cosmos-ansible`

The run reached the configured repository timeout:

`1800 seconds = 30 minutes`

Correct interpretation:

```text
AnsibleGuard data = missing
ansible-lint data = missing
GitLeaks data     = missing
```

Incorrect interpretation:

```text
0 AnsibleGuard findings
0 ansible-lint findings
0 GitLeaks findings
```

This distinction is preserved correctly in the main status table, but not in every chart helper table.

---

# 5. Raw findings and canonical occurrences

The run produced:

| Measure | Count |
|---|---:|
| Raw findings | **390,286** |
| Canonical occurrences | **376,115** |
| Collapsed / removed by canonicalization | **14,171** |

Percentages:

- canonical occurrences retained: **96.37%**
- raw records collapsed by canonicalization: **3.63%**

This 3.63% is **not a false-positive rate**. Canonicalization is an identity/deduplication step, not human correctness validation.

The safer global study count is therefore:

**376,115 canonical occurrences**

not "390,286 defects".

---

# 6. Provider composition

## 6.1 All observed canonical occurrences

| Provider | Occurrences | Share of 376,115 |
|---|---:|---:|
| AnsibleGuard | 265,931 | **70.70%** |
| ansible-lint | 108,750 | **28.91%** |
| GitLeaks | 1,434 | **0.38%** |
| Total | 376,115 | ~100% |

These percentages describe result composition only.

They do **not** imply:

- AnsibleGuard is 70.7% accurate;
- AnsibleGuard is "better" than ansible-lint;
- one provider detects more real defects than another.

The providers operate with different rule catalogs and, importantly, different analysis populations.

## 6.2 ansible-lint comparability problem

Observed ansible-lint occurrences:

**108,750**

Occurrences belonging to repositories where ansible-lint was fully complete:

**83,412**

Excluded incomplete-provider occurrences:

**25,338**

Therefore:

- **23.30%** of observed ansible-lint occurrences belong to incomplete ansible-lint repositories;
- those 25,338 occurrences are **6.74%** of the entire 376,115-occurrence dataset.

Provider-comparable occurrences across the study:

**350,777 = 93.26%** of all canonical occurrences.

The study is correct to retain the partial ansible-lint evidence while excluding it from strict cross-provider comparisons.

---

# 7. Provider prevalence across repositories

Among repositories where the provider is eligible/usable:

| Provider | Eligible repos | Repos with ≥1 finding | Prevalence |
|---|---:|---:|---:|
| AnsibleGuard | 206 | 206 | **100%** |
| ansible-lint | 171 | 142 | **83.04%** |
| GitLeaks | 206 | 96 | **46.60%** |

"100% AnsibleGuard prevalence" means every successfully analyzed repository triggered at least one rule. It does not prove every finding is correct; broad style and maintainability policies can make high prevalence expected.

---

# 8. What "156 rules observed" really means

The report lists **156 observed rule identities**, but this is a cross-provider count:

- **65** observed `ansibleguard/...` rule IDs;
- **76** observed `ansible-lint/...` rule IDs;
- **15** observed `gitleaks/...` rule IDs.

Therefore, never write:

> "AnsibleGuard has 156 detectors"

based on this run.

The 156 number is the combined observed rule identity space across all providers.

---

# 9. Internal AnsibleGuard result composition

The internal static-source population is:

**265,434 occurrences**

An additional:

**497 review/history occurrences**

brings total AnsibleGuard-owned occurrences to:

**265,931**

## 9.1 Internal static categories

| Category | Findings | Share |
|---|---:|---:|
| Style | 148,858 | **56.08%** |
| Correctness | 54,382 | **20.49%** |
| Maintainability | 33,780 | **12.73%** |
| Security | 9,266 | **3.49%** |
| Compatibility | 7,257 | **2.73%** |
| Documentation | 5,084 | **1.92%** |
| Reliability | 2,858 | **1.08%** |
| Testing | 1,814 | **0.68%** |
| Structure | 1,686 | **0.64%** |
| Dependencies | 449 | **0.17%** |

Style + correctness + maintainability:

**89.30%** of internal static output.

Interpretation: the current tool is dominated by style/correctness/maintainability signals rather than high-severity security failures.

---

# 10. The output is extremely concentrated in a small number of rules

The three largest internal rules are:

| Internal rule | Findings | Share of internal static | Repositories affected |
|---|---:|---:|---:|
| `ansibleguard/missing-tags` | 98,005 | **36.92%** | 192 / 206 = **93.20%** |
| `ansibleguard/unguarded-variable` | 52,474 | **19.77%** | 186 / 206 = **90.29%** |
| `ansibleguard/variable-naming-convention` | 24,121 | **9.09%** | 154 / 206 = **74.76%** |

Combined:

**174,600 occurrences = 65.78% of all internal static findings.**

This is the most important result for later validation design.

If any of these high-volume rules has weak precision, it can dominate users' perception of the entire tool.

## 10.1 `missing-tags`

`missing-tags` alone is:

- **36.92%** of internal static output;
- **26.06%** of all 376,115 canonical occurrences across all providers;
- present in **93.20%** of analyzable repositories.

The rule catalog classifies it as:

- style;
- low confidence;
- informational;
- optional policy.

Therefore the finding count must not be described as 98,005 confirmed defects.

A more faithful statement is:

> 98,005 task/tag policy observations were generated by the optional `missing-tags` rule.

## 10.2 `unguarded-variable`

Total:

**52,474**

Semantic split:

| Semantic concept | Count | Share of this rule |
|---|---:|---:|
| `undeclared-input-contract` | 34,326 | **65.42%** |
| `unresolved-runtime-input` | 17,151 | **32.68%** |
| `missing-internal-variable` | 997 | **1.90%** |

Therefore:

**98.10%** of this rule's output is not the strongest "a variable is definitely missing internally" class.

This is a major reason not to label all 52,474 findings "undefined variables".

The v0.0.7 semantic resolution work improves the tool by representing uncertainty explicitly instead of pretending every unresolved reference is a proven defect.

---

# 11. Severity, confidence, and uncertainty

## 11.1 Severity

| Severity | Count | Percentage |
|---|---:|---:|
| Note | 210,552 | **55.98%** |
| Warning | 156,480 | **41.60%** |
| Error | 9,083 | **2.41%** |

Notes + warnings:

**97.58%**

Errors:

**2.41%**

The large study count should therefore never be presented as hundreds of thousands of critical errors.

## 11.2 Confidence

| Confidence | Count | Percentage |
|---|---:|---:|
| Medium | 189,015 | **50.25%** |
| Low | 185,089 | **49.21%** |
| High | 2,011 | **0.53%** |

Almost half of the complete canonical dataset is explicitly low confidence.

Only **0.53%** is high-confidence output.

This reinforces the need for rule- and confidence-stratified validation later.

## 11.3 High-level uncertainty state

| State | Count | Percentage |
|---|---:|---:|
| CONFIRMED | 314,493 | **83.62%** |
| UNCERTAIN | 54,196 | **14.41%** |
| EXPOSED | 6,251 | **1.66%** |
| UNRESOLVED | 997 | **0.27%** |
| ORDERED_CONFLICT | 178 | **0.05%** |

"CONFIRMED" here means confirmed according to the static detector/result model. It does **not** mean confirmed by independent human annotation.

## 11.4 Detailed static-resolution status

| Resolution status | Findings | Share |
|---|---:|---:|
| `DETECTOR_RESULT` | 314,493 | **83.62%** |
| `EXTERNAL_INPUT_UNCERTAIN` | 34,326 | **9.13%** |
| `RUNTIME_CONTEXT_UNCERTAIN` | 17,161 | **4.56%** |
| `PROVEN_EXPOSED` | 6,251 | **1.66%** |
| `BOUNDED_GRAPH_UNKNOWN` | 2,106 | **0.56%** |
| `CANDIDATE_MISSING` | 997 | **0.27%** |
| `DYNAMIC_PROTECTION_UNKNOWN` | 603 | **0.16%** |
| `PROVEN_ORDERED_CONFLICT` | 178 | **0.05%** |

This is more informative than a binary "finding / no finding" model and should be preserved in validation.

---

# 12. Corpus size and normalized internal density

Across the 206 analyzable repositories:

- selected files: **31,734**
- selected YAML LOC: **1,337,631**
- internal static occurrences: **265,434**

This gives approximately:

**198.44 internal static occurrences per 1,000 selected YAML LOC**

This is an output density, not a defect density.

Multiple rules may fire on the same task/file, and low-confidence/optional rules are included.

---

# 13. Repository-level distribution

Canonical findings per usable repository are strongly right-skewed.

Approximate distribution:

| Statistic | Canonical findings |
|---|---:|
| Q1 | 308.25 |
| Median | 1,023 |
| Mean | 1,825.8 |
| Q3 | 2,349.25 |
| Maximum | 20,742 |

The mean being far above the median shows that a small set of large/noisy repositories contributes a disproportionate number of findings.

Later human validation should therefore not use a simple finding-level random sample without repository-aware weighting or stratification.

---

# 14. Runtime behavior

Across 207 target repositories:

- Q1: **11.385 s**
- median: **23.176 s**
- mean: **44.034 s**
- Q3: **40.039 s**
- maximum: **1800.021 s**

Runtime buckets:

| Duration | Repositories | Percentage |
|---|---:|---:|
| 0–59 s | 171 | **82.61%** |
| 60–119 s | 27 | **13.04%** |
| 120–179 s | 4 | **1.93%** |
| 180–239 s | 2 | **0.97%** |
| 240–299 s | 2 | **0.97%** |
| ≥300 s | 1 | **0.48%** |

**198 / 207 = 95.65%** completed in under two minutes.

The single 30-minute timeout is therefore a very strong outlier and deserves isolated performance investigation rather than changing the global timeout blindly.

---

# 15. The 35 partial repositories: what actually went wrong

The partial status is overwhelmingly an ansible-lint integration/environment issue.

The preserved diagnostics show real-project conditions such as:

- `ansible-playbook --syntax-check` failures;
- missing project-specific collection/module context;
- repository context expected by syntax checks;
- obsolete or incompatible `.ansible-lint` configuration;
- duplicate YAML keys;
- malformed or incompatible requirements files;
- provider/config load failures.

A primary-cause grouping from the preserved raw diagnostics is approximately:

| Primary class | Repositories | Share of partial repos |
|---|---:|---:|
| Syntax/context/YAML-related ansible-lint failures | ~25 | **~71.43%** |
| Obsolete/incompatible `.ansible-lint` configuration | 6 | **17.14%** |
| Provider load failure | 2 | **5.71%** |
| Invalid requirements-style input | 1 | **2.86%** |
| ansible-lint failed before usable JSON | 1 | **2.86%** |

This grouping is diagnostic rather than a mutually exclusive taxonomy of every low-level message; one repository can emit several diagnostic types.

The key methodological conclusion is:

> Do not discard the whole repository when ansible-lint is partial. Preserve AnsibleGuard internal results and mark only ansible-lint observations incomplete.

The study currently does this correctly.

## 15.1 Concentration of excluded ansible-lint output

Five partial repositories account for roughly **70.54%** of the 25,338 excluded ansible-lint occurrences:

| Repository | ansible-lint occurrences |
|---|---:|
| RedHatGov/redhatgov.workshops | 7,189 |
| dimagi/commcare-cloud | 2,820 |
| pulibrary/princeton_ansible | 2,814 |
| snowdrop/k8s-infra | 2,663 |
| cfpb/aurora | 2,388 |
| **Total** | **17,874** |

This demonstrates why dropping all partial repositories from the entire study would disproportionately remove large real-world projects.

---

# 16. Reporting-layer defects found

This section is critical. These are implementation defects in the generated presentation package, not evidence that the underlying aggregate dataset is invalid.

## 16.1 Broken `04-top-rules` chart

`charts/data/04-top-rules.csv` contains rows such as:

```text
missing-tags                  raw_findings > 0
canonical_occurrences        = 0
repositories_affected        = 0
```

while the authoritative aggregate contains:

```text
ansibleguard/missing-tags = 98,005
```

### Root cause

In `scripts/v007_full_repro.py`:

```python
rule_source = {
    row["rule_id"]: row
    for row in _read_csv(aggregate / "rule-summary.csv")
}

catalog = profile_metadata(... )["rule_ids"]

rule_source.get(rule, {})
```

The profile catalog provides short internal IDs such as:

```text
missing-tags
```

while aggregate canonical IDs are:

```text
ansibleguard/missing-tags
```

The join therefore fails and defaults to zero.

### Required fix

Do not build the chart table from short profile IDs and then join by a different namespace.

Preferred solution:

- use `aggregate/rule-summary.csv` directly as the authoritative table;
- or introduce an explicit namespace-normalization function, for example:
  - internal `missing-tags` → `ansibleguard/missing-tags`;
  - imported/native providers remain `ansible-lint/...` and `gitleaks/...`.

Add a reconciliation assertion:

```text
sum(findings-by-rule.canonical_occurrences)
==
sum(rule-summary.findings)
==
376115
```

for the intended all-provider rule table.

## 16.2 Failed repository incorrectly converted to zero

The authoritative repository report correctly leaves the timed-out repository's analytical results blank/missing.

However these chart helpers use patterns such as:

```python
row.get("canonical_occurrences", 0)
```

and:

```python
row.get("canonical_per_1000_loc") or 0
```

Consequently:

`encapsulate-xyz/cosmos-ansible`

is plotted as `0`.

### Why this is wrong

Missing observation:

`NA`

is not the same as:

`0 findings`.

### Required fix

Keep missing analytical fields as null/blank and:

- exclude failed observations from distributions that require a result;
- show failed observations separately;
- never coerce missing analytical data to zero for plotting.

Add a sanity check:

```text
if overall_status == failed:
    canonical_occurrences must be blank/null
```

## 16.3 Density chart mixes incompatible provider populations

The numbered chart says:

> Canonical occurrences per 1,000 selected Ansible LOC

but "canonical occurrences" includes:

- internal AnsibleGuard static findings;
- ansible-lint;
- GitLeaks whole-repository findings;
- review/Git-history findings.

Selected YAML LOC is not a valid denominator for GitLeaks or Git-history findings.

### Required fix

Replace the chart with provider-specific normalization.

Recommended:

```text
internal static occurrences / selected YAML LOC
```

and, optionally:

```text
complete ansible-lint occurrences / selected YAML LOC
```

as a separate chart.

Do not normalize GitLeaks or review-history occurrences using selected YAML LOC.

## 16.4 Provider-completeness chart categories overlap

Code currently calculates:

```python
"all expected providers complete"
= overall_status == complete

"partial ansible-lint"
= ansible_lint_status != completed

"failed gitleaks"
= gitleaks_status != completed

"other incomplete"
= overall_status == failed
```

The failed repository belongs to several categories simultaneously.

This makes the chart total exceed 207.

### Required fix

Either make categories mutually exclusive:

```text
complete
partial_ansible_lint
failed_repository
```

for this run,

or display each provider as an independent stacked/status table instead of pretending the categories form one partition.

For provider health, the authoritative values are:

- ansible-lint: 171 completed, 35 partial, 1 missing;
- GitLeaks: 206 completed, 1 missing.

## 16.5 "Uncertain vs actionable" is semantically wrong

Current code creates:

```text
uncertain
other detector result
```

based on whether:

```python
certainty == "UNCERTAIN"
```

The second group includes confirmed, exposed, unresolved, ordered-conflict and other states.

That is **not the same as actionability**.

### Required fix

Rename the chart to:

`Uncertain vs other certainty states`

or calculate actionability from actual rule/actionability metadata.

Do not use "actionable" unless the rule catalog's actionability field is actually used.

## 16.6 External-tool overlap chart is not an overlap result

Current code deliberately creates:

```text
No valid mapping = 0
```

because no machine-readable equivalence mapping exists.

This is conservative internally, but a zero bar is easy to misread as:

> "There is zero overlap."

### Required fix

Render:

```text
N/A — overlap not computed because no equivalence mapping is defined
```

Prefer no quantitative bar at all until the mapping exists.

## 16.7 Sanity check contains a tautology

Current implementation includes:

```python
all(row["overall_status"] != "complete" or True for row in statuses)
```

Because of `or True`, the condition is always true.

Therefore the check named:

`provider_incompleteness_not_zeroed`

does not test what its name claims.

### Required fix

Replace it with real invariants such as:

```text
failed repository => canonical occurrences is null
partial ansible-lint => ansible_lint_status == partial
partial ansible-lint => internal data remains present
missing provider => provider findings excluded from comparable population
```

## 16.8 Sanity checks test file existence, not analytical reconciliation

Current checks confirm:

- 207 rows;
- commit SHA present;
- occurrence IDs unique;
- known providers;
- raw >= canonical;
- 15 chart CSVs exist;
- SVGs exist.

Those are good structural checks.

They do **not** verify:

- chart totals equal aggregate totals;
- chart rule IDs join successfully;
- failed rows remain NA;
- denominators correspond to provider population;
- provider-completeness categories are exclusive;
- percentages sum correctly.

This explains how sanity checks can pass while a chart is wrong.

### Required fix

Add semantic reconciliation checks.

## 16.9 PNG output was not generated

`study_reporting.optional_png()` only converts SVG files if Python can import `cairosvg`.

CairoSVG was not available, so:

`charts/png/`

is empty.

This is not analytically serious because SVG is actually preferable for LaTeX/vector reports, but the deliverable should either:

- make PNG explicitly optional; or
- add CairoSVG to the reproducible environment if PNG is required.

---

# 17. Reproducibility audit

## 17.1 What is strong

The run records:

- frozen repository identities;
- exact repository SHAs;
- environment information;
- dependency list;
- input/output checksums;
- run state;
- raw outputs;
- deterministic derived outputs.

The deterministic post-processing test reports:

- expected deterministic artifacts: **43**
- identical artifacts: **43**
- result: **100% identical**

This proves:

> same raw snapshots → same aggregate/report/chart-data outputs

It does not prove:

> two independent full scans from scratch produce byte-identical raw outputs.

That stronger full rerun test has not been demonstrated.

## 17.2 Analysis commit versus package-builder commit

Environment metadata contains:

- analysis commit: `3391f2756c1079a7da9d2fd94c7a0960ff526ebd`
- package builder commit: `d1711f90b7ab45fe80f429927c310cf58a323f77`

The later commits were reproducibility/packaging fixes, not detector tuning, so this split is explainable.

For the final canonical study, however, a cleaner setup would be:

```text
one final code commit
↓
full run
↓
result package produced by the same commit
```

That removes ambiguity completely.

## 17.3 Python mismatch

Actual run:

**Python 3.14.7**

Reproduction guide:

```bash
python3.12 -m venv .venv
```

This means the documented reproduction procedure does not recreate the exact original interpreter.

### Required fix

Choose one canonical Python version and enforce it.

Because the run was already executed on 3.14.7, options are:

1. rerun the final canonical experiment in a frozen Python 3.12 environment and make 3.12 the contract; or
2. change the reproduction contract to Python 3.14.x and pin it explicitly.

The important requirement is not which version is chosen; it is that the run and reproduction guide match.

## 17.4 GitLeaks version is not captured

Environment metadata says only:

`version is set by build process`

This is not an exact tool identity.

### Required fix

Record:

- GitLeaks semantic version;
- binary SHA256;
- download/release identity or container image digest.

## 17.5 Ansible version capture failed

Environment metadata reports the `ansible` command as unavailable through the chosen invocation.

Yet the environment includes Ansible components.

### Required fix

Record exact versions using working commands, for example the correct installed CLI entry point or package metadata.

At minimum record:

- ansible package;
- ansible-core;
- ansible-compat;
- ansible-lint.

## 17.6 Canonical run environment and CI environment differ

Frozen run environment includes approximately:

- ansible-lint 26.4.0;
- ansible-core 2.21.0;
- ansible-compat 26.3.0;
- Python 3.14.7.

The current GitHub CI installs from project dependency ranges and the latest inspected run resolved different versions, including:

- ansible-lint 26.9.0;
- a different ansible-core version;
- Python 3.10/3.12 matrix.

Compatibility CI is useful, but it does not verify the frozen study environment.

### Required fix

Maintain two jobs:

**Compatibility CI**
- supported Python matrix;
- allowed current dependency ranges.

**Frozen study environment CI**
- exact lock/requirements;
- exact Python;
- exact external binaries;
- validates that the reproducibility environment can still be built.

Best option for collaborator equality:

- publish/build a frozen Docker image;
- record its image digest;
- run the study inside that image.

---

# 18. GitHub branch / CI audit

The reproducibility branch is:

`chore/v007-reproducible-full-run`

Current inspected head:

`d1711f90b7ab45fe80f429927c310cf58a323f77`

It is six commits ahead of the original v0.0.7 baseline `ac82dd6...` and zero commits behind.

The commits are infrastructure-focused:

1. add v007 reproducible full-run orchestration;
2. guard disk budget / shallow acquisition;
3. preserve active virtualenv interpreter;
4. reuse verified frozen local checkouts;
5. prefer verified cache over interrupted checkout;
6. preserve incomplete scan outcomes in result package.

No detector-tuning commit was found in this branch delta.

## 18.1 Test suite status

Current branch GitHub Actions test execution:

**1031 passed, 2 skipped**

This means the previous `.venv/bin/python` study-pipeline failure was successfully fixed.

## 18.2 Why CI is still red

The overall workflow still fails after tests because:

```text
python scripts/generate_docs.py --check
```

reports stale generated files:

- `RULE_REFERENCE.generated.md`
- `rule-catalog.json`

### Required fix

Regenerate them from the authoritative rule metadata, inspect the diff, and commit the generated artifacts.

Because `rule-catalog.json` is itself included as evidence/input metadata in the study package, this synchronization failure should be fixed before declaring the branch release-clean.

---

# 19. Mapping work that still needs to be implemented

There is not one mapping problem. There are several.

---

# 20. Mapping A — rule namespace / identity mapping

## Problem

The code uses several identities:

```text
missing-tags
ansibleguard/missing-tags

ansible-lint-issue
ansible-lint/fqcn[action-core]

gitleaks generic output
gitleaks/generic-api-key
```

These are not interchangeable.

The top-rule chart bug was caused directly by this identity mismatch.

## Required canonical rule identity

Every aggregated occurrence should expose:

```text
provider
provider_native_rule_id
canonical_rule_id
internal_short_rule_id (only when applicable)
semantic_concept_id
```

Example:

```text
provider               = ansibleguard
provider_native_rule_id= missing-tags
canonical_rule_id      = ansibleguard/missing-tags
semantic_concept_id    = missing-tags
```

For external provider:

```text
provider               = ansible-lint
provider_native_rule_id= fqcn[action-core]
canonical_rule_id      = ansible-lint/fqcn[action-core]
semantic_concept_id    = <optional mapped concept>
```

Do not use string guessing in report code.

Create one canonical mapping function and unit-test it.

---

# 21. Mapping B — internal rule → semantic concept

This already exists conceptually and should become an explicit stable table.

Most internal rules are approximately one-to-one:

```text
ansibleguard/missing-tags
    → missing-tags
```

but some are not.

Critical example:

```text
ansibleguard/unguarded-variable
    ├── undeclared-input-contract
    ├── unresolved-runtime-input
    └── missing-internal-variable
```

Validation must sample these concepts independently because their semantics and expected precision differ strongly.

Recommended file:

`study/mappings/internal-rule-concepts.csv`

Columns:

```text
canonical_rule_id
concept_id
resolution_status
default_confidence
taxonomy
actionability
notes
```

---

# 22. Mapping C — AnsibleGuard ↔ ansible-lint semantic equivalence

This mapping is required before calculating external-tool overlap.

Do **not** map rules just because names sound similar.

Use relationship types:

```text
substantial
partial
adjacent
none
```

If an external result is imported one-for-one rather than independently detected, use a separate relationship such as:

```text
integration
```

## Recommended initial mapping candidates

| AnsibleGuard rule | ansible-lint rule/family | Relationship | Notes |
|---|---|---|---|
| `overriden-keys` | `yaml[key-duplicates]` | substantial | Same duplicate-mapping-key defect; parser/reporting details differ |
| `deprecated-modules` | `deprecated-module` | substantial | Same module-deprecation area; catalogs can differ |
| `shell-instead-of-module` | `command-instead-of-module` | substantial/partial | Curated command recognition differs |
| `shell-instead-of-module` | `command-instead-of-shell` | partial | Related but not identical predicate |
| `non-idempotent-command` | `no-changed-when` | substantial/partial | AG first classifies mutating command; lint rule is broader/different |
| `shell-environment-export` | `inline-env-var` | substantial | Same embedded environment-assignment smell in many cases |
| `long-statement` | `yaml[line-length]` | substantial if thresholds/config match | Must compare configured thresholds first |
| `unnamed-task` | `name[missing]` | substantial | Match task object, not merely line |
| `unnamed-play` | `name[missing]` | substantial | Match play object |
| `variable-naming-convention` | `var-naming[...]` family | partial/family | Not one-to-one; map subrules carefully |
| `insecure-permissions` | `risky-file-permissions` | partial | Module/context assumptions differ |
| `silent-error-suppression` | `ignore-errors` | partial | AG also reasons about `failed_when` / result handling |
| `large-task` | `complexity[tasks]` | partial/adjacent | Threshold and structural units differ |
| `large-play` | complexity family | adjacent/partial | Must confirm exact ansible-lint predicate |
| `large-playbook` | complexity family | adjacent/partial | Must confirm exact predicate |
| `invalid-task-attribute-type` | `schema[tasks]`, `args[module]` | partial | Schema/module validation is broader |
| `invalid-numeric-value` | schema/args rules | partial | Only some numeric constraints overlap |
| `credentials-leaking-in-log` | `no-log-password` if available | partial | AG covers broader sensitive terms/context |
| `missing-tags` | **no direct mapping** | none | Do not confuse with `meta-no-tags`; different semantics |
| `unguarded-variable` | **no direct mapping** | none | Keep as AnsibleGuard-native semantic analysis |

Observed comparison-side counts exist, for example:

- `ansible-lint/no-changed-when`: 4,816;
- `ansible-lint/risky-file-permissions`: 3,405;
- `ansible-lint/yaml[line-length]`: 2,979;
- `ansible-lint/name[missing]`: 2,907;
- `ansible-lint/command-instead-of-shell`: 1,266;
- `ansible-lint/ignore-errors`: 700;
- `ansible-lint/var-naming[pattern]`: 632;
- `ansible-lint/command-instead-of-module`: 582;
- `ansible-lint/deprecated-module`: 166;
- `ansible-lint/yaml[key-duplicates]`: 28;
- `ansible-lint/inline-env-var`: 26;
- `ansible-lint/complexity[tasks]`: 6.

Those are counts, **not overlap counts**.

---

# 23. Mapping D — AnsibleGuard ↔ GitLeaks

Current study output represents GitLeaks as its own provider, with native rules such as:

```text
gitleaks/generic-api-key
gitleaks/private-key
...
```

Do not merge these blindly into internal security detectors.

Recommended relationships:

| AnsibleGuard rule | GitLeaks family | Relationship |
|---|---|---|
| `plaintext-sensitive-variable` | relevant secret rules | partial |
| `default-credentials` | relevant secret rules | partial |
| `credentials-leaking-in-log` | GitLeaks rules | adjacent, not direct |
| internal variable/security semantics using Jinja references | GitLeaks | generally none |

GitLeaks answers approximately:

> Does source text contain something matching a secret detector?

`credentials-leaking-in-log` answers approximately:

> Could a task expose a sensitive value during execution because logging is not protected?

These should not be counted as the same defect simply because both involve credentials.

---

# 24. Mapping E — occurrence matching algorithm

A rule mapping alone is not enough. You need a way to decide whether two findings refer to the **same source problem**.

Recommended matching identity:

```text
repository
frozen commit SHA
normalized file path
object kind
object/task/play identity
semantic rule pair
source span / offending key or module
```

Avoid requiring exact line equality because tools often point to:

- task start;
- module line;
- specific key line;
- document start.

## Matching tiers

### Tier 1 — exact

Same:

```text
repository
commit
file
object identity
semantic predicate
```

and overlapping source span.

### Tier 2 — structural

Same task/play/mapping object and mapped semantic predicate, but line differs.

### Tier 3 — ambiguous

Same file and nearby lines but object identity cannot be proven.

Do not count Tier 3 automatically as overlap.

Use one-to-one matching inside each repository/file/rule pair so that one finding cannot match several findings and inflate overlap.

---

# 25. Mapping F — overlap metrics after the mapping exists

Only after mappings and occurrence matching are frozen should you calculate:

```text
matched
AnsibleGuard-only
external-only
```

Then possible descriptive metrics are:

```text
AG overlap rate
= matched / AG findings in mapped comparable population

External overlap rate
= matched / external findings in mapped comparable population

Jaccard
= matched / (AG + external - matched)
```

These are **overlap metrics**, not precision or recall.

## Correct population

For AnsibleGuard ↔ ansible-lint overlap, use only repositories where ansible-lint is complete:

**171 repositories**

unless the specific methodology can safely use a more precise finding-level completeness mask.

For AnsibleGuard ↔ GitLeaks, both providers completed on:

**206 repositories**

but only semantically mapped security rules should enter the overlap calculation.

---

# 26. Mapping G — provider/population/denominator mapping

Create an explicit table and make every chart declare which row it uses.

| Population | Eligible repos | Scope | Valid denominator |
|---|---:|---|---|
| AnsibleGuard internal static | 206 | selected Ansible/YAML source | selected files / selected YAML LOC |
| ansible-lint complete comparable | 171 | ansible-lint selected scope | selected Ansible/YAML LOC, if scope equivalent |
| GitLeaks | 206 | whole repository | whole-repository source population; **not selected YAML LOC** |
| review-only rules | 206 | Git history | commits/history; **not selected YAML LOC** |
| all canonical | varies by provider | mixed | **no single LOC denominator** |

This mapping should be machine-readable.

Recommended file:

`study/mappings/analysis-populations.yaml`

---

# 27. Mapping H — execution-state mapping

Freeze exact meanings:

```text
complete
    internal completed
    ansible-lint completed
    GitLeaks completed

partial
    internal completed
    at least one required comparison provider incomplete
    internal data remains valid

failed
    core analysis unavailable / timed out / structurally failed

missing provider
    no observation
    NOT zero findings
```

Do not use generic `!= completed` when creating a mutually exclusive chart.

---

# 28. Mapping I — run identity / environment mapping

The final package should expose a clear matrix:

| Identity | Value |
|---|---|
| detector code commit | exact SHA |
| packaging/report code commit | exact SHA |
| branch | exact branch |
| Python | exact version |
| dependency lock hash | SHA256 |
| ansible-core | exact |
| ansible-lint | exact |
| ansible-compat | exact |
| GitLeaks | exact version + binary hash |
| spaCy model | exact version + hash/source |
| frozen manifest | SHA256 |
| rule catalog | SHA256 |
| container image | digest if used |

For the final publication run, preferably use a single code commit for detector and package generation.

---

# 29. Exact repair roadmap before validation

## Priority 0 — do not change detector semantics yet

Do not tune rules based on these counts before the result layer is repaired and frozen.

## Priority 1 — fix correctness of generated result artifacts

1. Fix rule namespace mapping in `findings-by-rule.csv`.
2. Regenerate `04-top-rules`.
3. Preserve null/missing values for failed repositories.
4. Replace general canonical-density chart with provider-valid density charts.
5. Fix provider-completeness categories.
6. Rename/reimplement "uncertain vs actionable".
7. Render external overlap as N/A until mapping exists.
8. Add semantic reconciliation tests to sanity checks.
9. Remove the `or True` tautology.
10. Regenerate all tables/charts from unchanged raw snapshots.
11. Re-run the 43-artifact deterministic comparison.

This stage should not require re-running 207 repositories because it is reporting/post-processing only, provided detector code/raw evidence does not change.

## Priority 2 — clean CI / generated metadata

1. Regenerate `RULE_REFERENCE.generated.md`.
2. Regenerate `rule-catalog.json`.
3. Confirm no detector-semantic diff is introduced.
4. Make GitHub CI green.

## Priority 3 — freeze exact reproducibility environment

1. Choose canonical Python.
2. Align reproduction guide with actual Python.
3. Freeze exact Python dependencies.
4. Freeze GitLeaks version and hash.
5. Fix Ansible version capture.
6. Add a frozen-environment CI job.
7. Prefer a container image and record its digest.

## Priority 4 — implement the mapping files

Create:

```text
study/mappings/
├── rule-identities.csv
├── internal-rule-concepts.csv
├── external-equivalence.csv
├── analysis-populations.yaml
└── occurrence-matching.md
```

Add tests that reject:

- unknown rule identities;
- contradictory mappings;
- external comparison with incomplete provider;
- invalid denominator use.

## Priority 5 — regenerate one clean canonical package

Once reporting + environment + mappings are fixed:

```text
final clean commit
        ↓
clean frozen environment
        ↓
207 frozen repositories
        ↓
full run
        ↓
result package
        ↓
checksums
```

If detector code remains unchanged, the internal results should be compared against the current run and any difference must be explained.

## Priority 6 — only then design final human validation

The current results already show that future validation should account for:

- highly dominant rules;
- rare rules;
- repository size;
- confidence;
- uncertainty/resolution state;
- semantic concepts;
- provider completeness;
- source-first false-negative sampling.

But the final annotation protocol should be designed after the cleaned canonical result package is frozen.

---

# 30. What can safely be claimed now

Reasonable current claims:

- The frozen study targets 207 real repositories.
- Core AnsibleGuard analysis completed on 206/207 repositories (**99.52%**).
- All expected providers completed on 171/207 repositories (**82.61%**).
- 35 repositories (**16.91%**) have partial ansible-lint evidence while preserving internal AnsibleGuard and GitLeaks results.
- One repository (**0.48%**) timed out.
- The run produced 390,286 raw records and 376,115 canonical occurrences.
- Canonicalization collapsed approximately **3.63%** of raw records.
- 265,931 canonical occurrences belong to AnsibleGuard, 108,750 to ansible-lint, and 1,434 to GitLeaks.
- Internal static output is heavily concentrated: the top three internal rules produce **65.78%** of internal static findings.
- `missing-tags` alone produces **36.92%** of internal static findings and is an optional low-confidence style policy.
- `unguarded-variable` is semantically split and only **1.90%** of that rule is the strongest `missing-internal-variable` concept.
- Derived post-processing was deterministic for **43/43** checked artifacts from identical raw snapshots.
- The current Python tests pass (**1031 passed, 2 skipped**) on the inspected GitHub branch.

---

# 31. What must NOT be claimed yet

Do not claim:

- "376,115 real defects";
- "AnsibleGuard precision is X%";
- "AnsibleGuard recall is X%";
- "AnsibleGuard is more accurate than ansible-lint";
- "there is zero overlap with ansible-lint";
- "all 207 repositories were fully analyzed by all providers";
- "the run is publication-ready";
- "the same environment is already guaranteed for every collaborator";
- "CONFIRMED means independently human-confirmed";
- "156 AnsibleGuard rules were validated";
- "the current charts are all correct".

Those claims are not supported by the current evidence.

---

# 32. Final assessment

## Strong parts

- frozen real-world population;
- 99.52% core-tool execution coverage;
- explicit provider states;
- raw evidence preservation;
- canonical occurrence model;
- separate internal/ansible-lint/GitLeaks populations;
- explicit semantic uncertainty;
- very useful concept split for variable resolution;
- deterministic post-processing;
- large passing test suite;
- infrastructure branch does not appear to tune detectors.

## Weak parts

- ansible-lint environment/context robustness;
- one severe runtime outlier;
- several reporting/chart bugs;
- weak semantic sanity checks;
- stale generated documentation/catalog;
- environment/version mismatch between run, guide and CI;
- GitLeaks version not frozen in metadata;
- no machine-readable external equivalence mapping;
- no final independent human validation.

## Overall

The experiment is **not a failed run**.

It is better described as:

> a successful large-scale diagnostic run with very strong internal coverage and useful raw evidence, but with incomplete external-provider coverage and a reporting/reproducibility layer that still requires cleanup before the results should be frozen for scientific validation or publication.

The best next move is **not to modify detectors**. The best next move is to repair the result layer and mappings, create one final reproducible package, and only then design the human validation protocol.
