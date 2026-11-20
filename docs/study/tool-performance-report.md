# AnsibleGuard performance: precision, recall, and what's actually measured

This answers "report the performance of the tool — precision, recall, etc."
directly and honestly: **there is no final, human-validated precision or
recall number yet.** What exists is (a) a rigorous validation *design* for
getting one, not yet executed with real human reviewers, and (b) several
real, already-computed data points — AI-vs-detector and AI-vs-AI, not
AI-vs-ground-truth — that are informative but must not be presented as a
final precision/recall figure. This document gives both, clearly labeled.

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

## 2. The one calibration-scale precision data point that exists on the official track

A 101-item AI precheck (`study/fp-precheck-v007-2026-10-15/` on the audit
branch) — **AI-labeled, not human gold, explicitly calibration-only**:

**54 TP / 19 FP / 28 uncertain** → 74.0% precision among the 73 decidable
items (54/73). This also directly drove eleven identified false-positive
mechanisms, six of which are now fixed in the merged detector code.

## 3. PR-replay: a different, already-measured metric (not precision)

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

## 4. Our own data: AI-vs-detector agreement across three samples

This is the most current, directly computable data we have — **Reviewer A
(an independent AI pass) judging whether the detector's own flagged
occurrence is a genuine positive, across three samples.** This is a
precision *proxy*, not a validated precision number: it's AI judgment
against the detector, not human-verified ground truth, and every number
below excludes "uncertain"/"unreviewable" rows from the denominator (stated
explicitly, not hidden).

| Sample | N | Positive (TP-like) | Negative (FP-like) | Uncertain | Unreviewable | Precision-proxy (pos / (pos+neg)) |
|---|---:|---:|---:|---:|---:|---:|
| 350-item agreement pilot (v0.0.7 corpus) | 350 | 184 | 127 | 37 | 2 | **59.2%** (n=311 decidable) |
| 400-item stratified sample (v0.0.7 corpus) | 400 | 195 | 79 | 115 | 11 | **71.2%** (n=274 decidable) |
| 352-item stratified sample (fixed v0.0.7.1 corpus) | 352 | 188 | 62 | 101 | 1 | **75.2%** (n=250 decidable) |

**The upward trend (59% → 71% → 75%) is suggestive but must not be
oversold**: the three samples use different sampling methodologies (the
350-item pilot is calibration-repo-only; the two stratified samples are
impact-weighted across the full corpus) and two different detector versions
(v0.0.7 vs. the fixed v0.0.7.1), so this is not a controlled before/after
comparison — it's consistent with the detector fixes having helped, but
isn't proof on its own.

### Per-family breakdown, most current sample (v0.0.7.1, fixed detector)

| Review family | N | Positive | Negative | Uncertain | Unreviewable | Precision-proxy |
|---|---:|---:|---:|---:|---:|---:|
| Objective correctness | 45 | 37 | 3 | 5 | 0 | **92.5%** |
| Structure/reuse | 28 | 4 | 1 | 23 | 0 | 80.0% (n=5, small) |
| Style/policy | 117 | 85 | 23 | 9 | 0 | **78.7%** |
| Security | 35 | 26 | 8 | 1 | 0 | **76.5%** |
| Maintainability/complexity | 82 | 30 | 17 | 35 | 0 | 63.8% |
| Variable/reference reasoning | 45 | 6 | 10 | 28 | 1 | **37.5%** (weakest family) |

The **Variable/reference reasoning** family is notably weak (37.5%) and
matches a pattern independently found in the local-LLM evaluation
(`study/exploratory-labels/local-llm/eval/EVAL_RESULTS.md`): both the detector and a separate LLM
pass struggle specifically with variables whose definition lives outside
the single file being examined (role defaults, `group_vars`), tending to
flag "undefined" when the variable is actually defined elsewhere. This
family also has the highest uncertain rate (62%), which is consistent with
that same root cause — the reviewer (AI, in this case) correctly can't
decide without seeing more context, same as the detector can't.

## 5. What to tell your supervisor, concretely

- **No precision or recall number currently meets a "measured, human-validated"
  bar.** Saying otherwise would overstate what exists.
- **A rigorous design for getting real precision numbers is already built**
  (stratified by rule tier, repository-capped, with confidence intervals
  planned) — it just hasn't been run with actual human reviewers yet. That's
  the real bottleneck, not methodology.
- **Recall has no study at all yet** — this would need new work (an
  independent smell-audit sample), not just more labeling of what the tool
  already found.
- **We do have real, computed AI-vs-detector precision proxies** (§4 above)
  across 1,102 total labeled occurrences spanning both detector versions,
  with a consistent weak spot identified (variable/reference reasoning,
  cross-file visibility) that reproduces across two completely independent
  evaluation efforts (the detector-precision labeling here, and the
  local-LLM explainer evaluation). That reproducibility across independent
  methods is itself a meaningful, reportable finding, even without a human
  gold standard.
