# AnsibleGuard performance: precision, recall, and what's actually measured

A final estimate of precision or recall requires eligible samples and independent human adjudication. The [agreement pilot](../../study/rq1-agreement-pilot/recovery-2026-10-23/RQ1_RESULTS.md) supports calibration.

## 1. There is a formal, unexecuted validation plan

A detailed validation design already exists
(`docs/study/v007-research-report-and-validation-plan.md` on
`fix/v007-audit-2026-10-15`, superseded in detail by
`v007-validation-protocol.md`), defining exactly six research questions:

| RQ | Question | Status |
|---|---|---|
| RQ1 Precision | Of reported occurrences for *required* (defect-claiming) rules, what fraction are correct — per rule, per family, overall? | Design complete (stratified by rule tier, repository-capped sampling); **not yet executed with human reviewers** |
| RQ2 Policy conformance | For *optional* rules (e.g. `missing-tags`), is the finding a correct application of the stated policy? | Not yet executed |
| RQ3 Resolution accuracy | For UNCERTAIN variable findings, how often is the uncertainty actually justified? | Not yet executed |
| RQ4 Recall | What fraction of codebook-defined smells actually present in a file does AnsibleGuard report? | **Not yet executed — no recall study has been run at all.** This needs a sample of files manually audited for smells independent of what the tool flagged, which does not exist yet. |
| RQ5 PR attribution | In real merged PRs, are "introduced"/"fixed" findings actually caused by the change? | **Partially measured** — see §3 below |
| RQ6 Agreement/reviewability | How reliably can two reviewers apply the codebooks, and what share of findings is reviewable at all from the evidence shown? | Partially measured — see §2 and §4 |

**The short version for recall: we cannot report a recall number. No study
has measured what AnsibleGuard misses, because that requires an independent
audit of files for smells regardless of what the tool found — a different
and not-yet-built sample, not a byproduct of reviewing the tool's own
output.**

## 2. PR-replay: a different, already-measured metric (not precision)

21 real merged pull requests were replayed through `ansibleguard diff`
(`study/pr-replay-v007-2026-10-15/`). This measures whether the tool's
introduced/fixed *attribution* is correct, not whether a flagged defect is
real:

| Measure | Before fixes | After fixes |
|---|---:|---:|
| Aborted comparisons | 13/21 | 0/21 |
| Introduced / fixed findings reported | 462 / 422 | 46 / 7 |
| Moves correctly recognized (not churn) | — | 688 |
| Attribution manually verified correct | — | 46/46 introduced, 7/7 fixed |

This says the diff mechanism itself is now accurate on real PRs — it does
not say 46/46 *flagged issues* are real defects, only that the tool
correctly identified them as newly introduced by that specific change.
