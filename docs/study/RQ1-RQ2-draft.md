# RQ1 (Precision) and RQ2 (Co-occurrence)

The agreement pilot was designed for calibration. Its [RQ1 report](../../study/rq1-agreement-pilot/recovery-2026-10-23/RQ1_RESULTS.md) records adjudication status and the pilot's exclusion from population precision estimation. For current co-occurrence results, see the [RQ2 rerun](../../study/rq2-v0071-rerun-2026-10-22/RQ2_RESULTS.md), which includes all analyzed files and adjusts for file size.

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

- RQ2: `docs/study/compute_rule_cooccurrence.py`, run against
  `docs/study/v0071-all-internal-source-occurrences.csv` (a copy of
  `study/runs/v0071-final-2026/aggregate/all-internal-source-occurrences.csv`
  from the WSL reproduction checkout, 243,748 rows). Full pairwise output in
  `docs/study/rq2-cooccurrence-pairs.csv` (709 rows, every pair that ever
  co-occurs, not just the top 10 shown above).
