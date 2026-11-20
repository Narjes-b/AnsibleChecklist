# RQ1 (Precision) and RQ2 (Co-occurrence)

> **Current status — 2026-10-31:** This is a historical draft, not submission-ready evidence. Adjudication alone does not make the old calibration pilot eligible for population precision. Use the [recovery RQ1 status](../../study/rq1-agreement-pilot/recovery-2026-10-23/RQ1_RESULTS.md), [dataset-scoped provenance](../../study/exploratory-labels/PROVENANCE.md), and [ICPC readiness plan](icpc-readiness-and-local-llm-plan-2026-10-31.md). The owner-attested human A/B pilot and separate AI exploratory samples must not be conflated; older statements below are retained as drafting history. RQ2 remains detector-output association, with inferential limitations recorded in the recovery plan.

Drafted for the AnsibleGuard paper. RQ1 follows the structural rigor of
Bessghaier et al.'s prevalence RQ1 (SANER'24, *"On the Prevalence,
Co-occurrence, and Impact of Infrastructure-as-Code Smells"*) but measures
precision, since that is what this study actually has data for. RQ2 directly
reuses that same paper's co-occurrence methodology (Apriori-style
support/confidence/lift, Chi-squared significance, Cramer's V effect size),
applied to AnsibleGuard's own occurrence data instead of Puppet IaC smells.

All numbers below are computed from data already in this repository; none
are estimated or placeholder.

> **Status 2026-10-22: the numbers in this draft are superseded.**
> - **RQ2**: recomputed on the 2026-10-22 rerun with every analysed file as a transaction (including files without
>   findings) and a file-size control (Mantel–Haenszel): [`study/rq2-v0071-rerun-2026-10-22/RQ2_RESULTS.md`](../../study/rq2-v0071-rerun-2026-10-22/RQ2_RESULTS.md).
> - **RQ1**: Reviewer A/B agreement, the adjudication sheet and precision with intervals are in
>   [`study/rq1-agreement-pilot/RQ1_RESULTS.md`](../../study/rq1-agreement-pilot/RQ1_RESULTS.md). Precision becomes final once
>   the 119 semantic disagreements are adjudicated ([guide](../../study/rq1-agreement-pilot/ADJUDICATION_GUIDE.md)).
>   The single-reviewer precision tables below are not to be reported.
> - The description of how the labels were produced is to be written by the reviewers themselves.

---

## RQ1: How precise is AnsibleGuard at detecting the conditions it reports?

**Motivation.** A static analysis tool is only useful if developers can
trust what it reports. Before any claim about AnsibleGuard's coverage or
impact is meaningful, it is necessary to establish how often its flagged
occurrences are genuine instances of the documented condition, versus false
positives caused by incomplete context or detector limitations.

**Approach.** We draw on three independently labeled samples spanning two
tool versions:

| Sample | N | Tool version | Sampling method |
|---|---:|---|---|
| Agreement pilot | 350 | v0.0.7 (pre-fix) | Calibration-repository blinded sample |
| Stratified sample | 400 | v0.0.7 (pre-fix) | Impact-weighted, full-corpus |
| Stratified sample (rebuilt) | 352 | v0.0.7.1 (fixed) | Impact-weighted, full-corpus |

Each occurrence was labeled `positive` (the detector's documented condition
genuinely holds, given the frozen source snippet shown), `negative` (false
positive), `uncertain` (the snippet does not contain enough evidence to
decide either way), or `unreviewable` (the snippet itself is unusable, e.g.
truncated or not the file the detector claims). The agreement pilot and the
first stratified sample each have two independent AI-generated label passes
over the same items ("Reviewer A" and "Reviewer B" for the pilot, "Reviewer
A" and "Reviewer C" for the stratified sample), each working only from the
frozen source snippet, never shown the detector's verdict as ground truth or
the other pass's labels. Measured raw agreement and Cohen's kappa between
the two passes: **66.0% / κ = 0.47** for the agreement pilot (n=350),
**58.8% / κ = 0.38** for the stratified sample (v0.0.7, n=400). No
disagreement between the two passes was resolved into a single merged label
for either sample. The precision figures reported below are Reviewer A's
labels specifically (the one pass present across all three samples, for
comparability); Reviewer B's and Reviewer C's own precision are not
separately reported here. The rebuilt v0.0.7.1 stratified sample currently
has only one label pass ("Reviewer A"); it has no second pass yet and
therefore no agreement statistic to report for it.

Precision is computed as `positive / (positive + negative)`, excluding
`uncertain` and `unreviewable` rows from the denominator (reported
explicitly, not hidden). These are reviewability gaps, not disagreements
about correctness, and pooling them into either side would misstate the
result in either direction.

**Results.** Precision improves across the two tool versions and the
third-party rebuild cycle:

| Sample | N | Positive | Negative | Uncertain | Unreviewable | Precision (decidable) |
|---|---:|---:|---:|---:|---:|---:|
| Agreement pilot (v0.0.7) | 350 | 184 | 127 | 37 | 2 | **59.2%** (n=311) |
| Stratified sample (v0.0.7) | 400 | 195 | 79 | 115 | 11 | **71.2%** (n=274) |
| Stratified sample (v0.0.7.1) | 352 | 188 | 62 | 101 | 1 | **75.2%** (n=250) |

Per-family breakdown on the most current sample (v0.0.7.1, the fixed
detector):

| Review family | N | Positive | Negative | Uncertain | Unreviewable | Precision |
|---|---:|---:|---:|---:|---:|---:|
| Objective correctness | 45 | 37 | 3 | 5 | 0 | **92.5%** |
| Structure/reuse | 28 | 4 | 1 | 23 | 0 | 80.0% (n=5, small) |
| Style/policy | 117 | 85 | 23 | 9 | 0 | **78.7%** |
| Security | 35 | 26 | 8 | 1 | 0 | **76.5%** |
| Maintainability/complexity | 82 | 30 | 17 | 35 | 0 | 63.8% |
| Variable/reference reasoning | 45 | 6 | 10 | 28 | 1 | **37.5%** |

The weakest family, **Variable/reference reasoning**, has both the lowest
precision (37.5%) and the highest uncertain rate (62.2%). Qualitative review
of the uncertain and negative cases in this family shows a consistent
mechanism: a flagged variable's definition commonly lives outside the single
file shown to the reviewer (role defaults, `group_vars`, a calling
playbook's extra-vars), and the detector, like the independent reviewer
given the same limited context, cannot distinguish "genuinely undefined"
from "defined elsewhere, not visible here." The same failure mode was
independently observed in a separate evaluation of a local LLM's
issue-explanation output over the same corpus
(`study/exploratory-labels/local-llm/eval/EVAL_RESULTS.md`): across 3 of 3 opportunities, the LLM
likewise asserted a variable was undefined purely because its definition was
not in view, violating its own explicit instruction not to do so. This
cross-method reproducibility (two independently built evaluation pipelines,
neither aware of the other's output, landing on the same weak spot for the
same underlying reason) is itself a finding: single-file context is a
structural blind spot for this rule family, not a quirk of any one
evaluation method.

**Threats to validity.** All labels in this RQ are AI-generated, not
human-labeled ground truth: the agreement pilot and first stratified sample
each have two independent AI passes (Reviewer A/B, Reviewer A/C), and the
rebuilt v0.0.7.1 sample currently has only Reviewer A's pass, with no second
rater yet. No reviewer saw anything beyond the frozen single-file snippet
(role defaults, `group_vars`, and calling playbooks were not shown), so
labels for context-dependent rules (notably Variable/reference reasoning)
reflect what is decidable from that snippet, not from the full repository.
A stratified validation design with additional, genuinely blind human
sampling exists for this project
(`docs/study/v007-research-report-and-validation-plan.md`, RQ1) but has not
yet been executed. The upward trend across tool versions
is consistent with, but does not on its own prove, the detector fixes between
v0.0.7 and v0.0.7.1 having improved precision, since the three samples
differ in both tool version and sampling scope simultaneously.

---

## RQ2: Which rule violations tend to co-occur in the same file?

**Motivation.** Understanding which AnsibleGuard rule violations commonly
co-occur can reveal compounding quality problems and help prioritize fixes:
if two conditions are strongly associated, addressing the root cause behind
one may resolve both, and a developer encountering one can be alerted to
check for the other. This directly mirrors SANER'24 RQ2's motivation for
Puppet IaC smells, applied here to AnsibleGuard rule violations.

**Approach.** We use the full v0.0.7.1 internal occurrence population
(243,574 occurrences, 191 repositories), restricted to **required
(defect-claiming) rules only** (77,247 occurrences) for the same reason
given in this project's own validation-plan document: pooling in
optional-policy rules (e.g. `missing-tags`) would let them dominate purely
on volume rather than genuine defect co-occurrence. The transaction unit is
one `(project, file)` pair; its items are the set of distinct required
`rule_id`s with at least one occurrence in that file. For every pair of
rules `(a, b)` that ever co-occurs in the same file, we compute:

- **Support**: the fraction of all transactions containing both `a` and `b`.
- **Confidence** (both directions): `P(b | a)` and `P(a | b)`.
- **Lift**: `Support(a,b) / (Support(a) * Support(b))`. A value above 1
  indicates the pair co-occurs more than chance would predict.
- **Chi-squared test and Cramer's V**, on the pair's 2×2 contingency table,
  to assess statistical significance and effect size of the association,
  exactly as in SANER'24 RQ2.

Following that paper's own calibration approach, pairs with fewer than 10
joint occurrences are excluded from ranking (at that scale, lift is
dominated by sampling noise, e.g. two rules that each occur exactly once in
the same file trivially produce "perfect" lift with no statistical meaning).

**Results.** Of 14,461 files with at least one required-rule occurrence,
**57.7% contain two or more distinct rule violations**, comparable in
spirit to SANER'24's finding that 52.29% of smelly Puppet files exhibit two
or more IaC smell types, despite the different tool and language. 709
distinct rule pairs co-occur at all; 401 do so at least 10 times.

Top 10 pairs by Lift (both_count ≥ 10):

| Rule A | Rule B | n | Support | Conf(A→B) | Conf(B→A) | Lift | p-value | Cramer's V |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| default-credentials | plaintext-sensitive-variable | 118 | 0.82% | 0.634 | 0.350 | **27.22** | <0.001 | 0.462 |
| high-coupling | insufficient-modularization | 37 | 0.26% | 0.090 | 0.597 | 21.05 | <0.001 | 0.225 |
| become-scope-too-broad | insufficient-modularization | 24 | 0.17% | 0.076 | 0.387 | 17.71 | <0.001 | 0.164 |
| non-idempotent-command | shell-instead-of-module | 254 | 1.76% | 0.398 | 0.641 | 14.52 | <0.001 | 0.488 |
| become-scope-too-broad | large-play | 252 | 1.74% | 0.798 | 0.226 | 10.36 | <0.001 | 0.404 |
| insufficient-modularization | large-play | 47 | 0.33% | 0.758 | 0.042 | 9.85 | <0.001 | 0.168 |
| ansible-lint/ignore-errors | silent-error-suppression | 89 | 0.62% | 0.659 | 0.091 | 9.79 | <0.001 | 0.229 |
| duplicated-code | insufficient-modularization | 22 | 0.15% | 0.039 | 0.355 | 9.15 | <0.001 | 0.107 |
| read-only-command-change | unscoped-shell-variable | 18 | 0.12% | 0.032 | 0.340 | 8.66 | <0.001 | 0.094 |
| become-scope-too-broad | high-coupling | 67 | 0.46% | 0.212 | 0.163 | 7.48 | <0.001 | 0.165 |

Top pairs by Cramer's V (effect size, both_count ≥ 10) surface a different,
arguably more important picture: strength of association rather than rare
coincidence:

| Rule A | Rule B | n | Support | Lift | Cramer's V |
|---|---|---:|---:|---:|---:|
| complex-playbook | large-playbook | 2115 | 14.63% | 4.63 | **0.786** |
| non-idempotent-command | shell-instead-of-module | 254 | 1.76% | 14.52 | 0.488 |
| default-credentials | plaintext-sensitive-variable | 118 | 0.82% | 27.22 | 0.462 |
| large-playbook | missing-abstraction | 1026 | 7.09% | 3.50 | 0.420 |
| complex-playbook | missing-abstraction | 889 | 6.15% | 3.79 | 0.408 |
| become-scope-too-broad | large-play | 252 | 1.74% | 10.36 | 0.404 |
| large-play | large-playbook | 812 | 5.62% | 3.68 | 0.385 |
| complex-playbook | high-coupling | 357 | 2.47% | 5.47 | 0.332 |
| duplicate-task-names | duplicated-code | 272 | 1.88% | 5.87 | 0.293 |
| large-playbook | large-task | 1828 | 12.64% | 1.73 | 0.277 |

Two interpretable clusters emerge:

1. **A maintainability/size cluster** (`complex-playbook`, `large-playbook`,
   `large-play`, `large-task`, `missing-abstraction`, `high-coupling`,
   `insufficient-modularization`): these are mutually reinforcing. A large
   playbook is mechanically more likely to also be complex, to contain large
   plays/tasks, and to lack abstraction. `complex-playbook ↔ large-playbook`
   has both the highest support (14.6% of all files with a required
   violation) and by far the strongest effect size (Cramer's V = 0.786),
   mirroring SANER'24's own finding that design-related smells
   (`Multifaceted Abstraction`, `Insufficient Modularization`, `Tightly
   Coupled Modules`, `Unstructured Module`) cluster together and dominate
   co-occurrence counts.
2. **A security cluster**: `default-credentials ↔ plaintext-sensitive-variable`
   is the strongest security-specific association (lift 27.22, Cramer's V
   0.462, p < 0.001). Files with a hardcoded default credential are
   substantially more likely to also contain a separate plaintext-sensitive
   variable, consistent with a project-wide secrets-handling practice (or
   lack thereof) rather than two independent, unrelated mistakes.

A smaller, non-maintainability pair worth noting: `ansible-lint/ignore-errors
↔ silent-error-suppression` (lift 9.79). Files that suppress ansible-lint's
own error reporting are also disproportionately likely to suppress runtime
task errors, suggesting a general "error visibility" practice at the file
level rather than two unrelated choices.

**Threats to validity.** As in SANER'24 RQ2, a high lift or Cramer's V does
not establish that one condition *causes* the other. Both could stem from
a shared root cause (e.g., file size driving both `complex-playbook` and
`large-playbook` mechanically, by construction of how those rules are
defined, rather than one being evidence of the other as an independent
phenomenon). The maintainability cluster in particular should be read with
this in mind: several of these rule pairs may be partially definitionally
correlated (e.g. a playbook's line count contributes to both "large" and
"complex" thresholds), not purely empirically discovered co-occurrence.

---

## Reproducing these numbers

- RQ1: `study/exploratory-labels/annotation-comparison/consolidated-comparison.csv`,
  `study/exploratory-labels/annotation-comparison/consolidated-comparison-phase2.csv`,
  `study/exploratory-labels/stratified-sample-v0071/stratified-sample-completed.csv`.
- RQ2: `docs/study/compute_rule_cooccurrence.py`, run against
  `docs/study/v0071-all-internal-source-occurrences.csv` (a copy of
  `study/runs/v0071-final-2026/aggregate/all-internal-source-occurrences.csv`
  from the WSL reproduction checkout, 243,748 rows). Full pairwise output in
  `docs/study/rq2-cooccurrence-pairs.csv` (709 rows, every pair that ever
  co-occurs, not just the top 10 shown above).
