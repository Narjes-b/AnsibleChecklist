# v0.0.7 validation plan v2 (researcher's redesign)

2026-10-16. Supersedes the staging, not the content, of
[v007-validation-protocol.md](v007-validation-protocol.md): modes A/B/C, the weighting
and the estimators stay. What changes is the order of work, the gates, and where human effort goes.
Use the calibration pilot to check whether the codebook and evidence bundles support reliable review.

## 1. Claims first: one instrument per claim

| Claim the paper may make | Instrument | Humans needed |
|---|---|---|
| Precision of each required rule | stratified two-stage human sample (mode C) | yes |
| Deterministic rules implement their predicate | independent re-implementation or oracle on the whole population (mode A) | edge cases only |
| Thresholds are meaningful | banded panels by metric value (mode B) | yes, smaller |
| Category prevalence ("X % of repos have Y") | precision-corrected counts, repo-cluster bootstrap | no extra |
| Recall | `RECALL_PROTOCOL.md` source-first panels; seeded defects; ansible-lint overlap on the 171 provider-complete repos; fix-commit tracing. Say plainly which rules are not recall-estimable | yes, small |
| PR mode is useful | 21-PR replay plus a human review of introduced/fixed findings | yes, small |

A claim without an instrument is dropped from the paper, not estimated loosely.

## 2. Order of work (each step is a gate for the next)

1. **Codebook v2** ([decisions](../../study/validation-v007-human/codebooks-v2-draft/POLICY_DECISIONS.md)): define every term the pilot showed to be undefined. Owner decisions required.
2. **Tool v0.0.7.1**: Fix false positives found on calibration data. Keep heldout data unopened, then freeze, rerun, and verify checksums.
3. **Bundle generator v2**: full tree listing, non-YAML diffs, imported handler files, name the asserted variable/attribute, stronger redaction plus an independent secret/email/key-body scan. No bundle leaves the machine before this.
4. **Pilot 2 on new items** (not the 350: memory effects). Gate, per family, decided before labelling:
   - κ on decided items ≥ 0.70 between two humans (target; ≥ 0.60 minimum);
   - human `uncertain` + `unreviewable` ≤ 25 % of items;
   - bundle-defect rate ≤ 5 %.
   A family that fails twice is dropped from precision claims; agreement is still reported.
5. **Pre-registration**: allocation, estimators, decision rules (section 4), signed off by a non-author, before heldout contexts exist.
6. **Heldout labelling** with the protocol in section 3.
7. **Analysis** per the protocol; decisions applied per section 4.

Stop rule: if any gate fails, stop and fix the instrument; never relabel to rescue a number.

## 3. Labelling protocol

- Two independent humans on pilots; on the main set, all items double-labelled for mode C and a share for A/B, disagreements adjudicated by a third person who sees both labels.
- **Consistency check**: 8 % of main items are re-inserted (disguised) so each reviewer's own repeat agreement is measurable. This is the drift measure.
- Randomised item order; time per item recorded; calibration session before each family.
- Three separated questions: is the claim true (semantic), does it matter (actionability), is it in scope (policy). Never one mixed reason code.
- Uncertain is reported, never silently dropped. Precision is reported as an interval: uncertain as true / uncertain as false.

## 4. Decisions the validation must drive (pre-registered)

| Rule precision (lower CI bound, ≥ 20 items from ≥ 8 repos) | Catalog action |
|---|---|
| ≥ 0.80 | keep required |
| 0.50–0.80 | keep, label "moderate precision" in outputs; fix top FP patterns |
| < 0.50 | demote to optional / experimental |
| not reportable | descriptive counts only, state the reason |

Report both occurrence-weighted and rule-averaged (macro) precision. A single weighted number
hides weak rules. (The thresholds above are proposals; the owner must confirm them before pre-registration.)

## 5. Effort allocation (importance-weighted)

Script: `scripts/v007_validation_plan_v2.py`; output `study/validation-design-v007/allocation-v2.csv`.

| Mode | v1 items | v2 items | Why |
|---|---:|---:|---|
| A deterministic (31 rules) | 160 | 134 | oracle covers the population; ≤ 8 edge cases |
| B threshold (15 rules) | 418 | 288 | 20 banded items per rule |
| C semantic (14 rules) | 375 | 445 | +10 items for tier-1 (security/reliability/correctness) rules with N ≥ 100, cap 50 |
| **Total** | **953** | **867** | |

Plus 69 re-inserted duplicates and about 173 adjudicated items. Main-label effort ≈ 135 reviewer-hours
(two raters, minutes per item as in the protocol §8), excluding pilot 2, recall panels and secondary panels.
13 rules with heldout occurrences stay "descriptive-only" (fewer than 20 items and not a census).

## 6. Sampling-frame rules (to implement in the sampler)

Exclude or separately stratify vendored third-party roles, bot and merge commits; dedupe sibling files and
twin rows from one repository; cap items per repository per rule; unit of analysis is the repository cluster.

## 7. Threats to validity to write up

GitHub selection bias; a single tool; Ansible-version dependence (state the ansible-core version used for judgments);
reviewer expertise and fatigue; overlapping rules (non-idempotent vs read-only command);
detector changes after sampling void the sample.

## 8. Owner confirmations (2026-10-16) and what is still open

Confirmed by the study owner: the 16 codebook v2 decisions as proposed; the pilot gates (κ ≥ 0.70 target / 0.60 minimum on decided items,
uncertain ≤ 25 %, bundle defects ≤ 5 %); the precision decision bands (0.80 / 0.50 lower bound); recall and PR-mode human review are IN scope.

Sign-off: the owner confirmed on 2026-10-16 that a non-author countersigns the analysis plan (identity held by the owner; record it in the freeze record). This is settled and is not to be raised again.

Still open: revise the family codebooks to match v2 and freeze them; overall-interval calibration (~90 % at nominal 95 %);
reviewer identities and schedule; v0.0.7.1 freeze.
