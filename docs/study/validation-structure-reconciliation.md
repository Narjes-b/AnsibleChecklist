# Reconciling the two validation-tree structures

Two independent, un-merged directory structures currently hold overlapping
validation work. This document maps what's where, flags the one naming
collision that could cause real confusion, and gives a concrete
recommendation. **It does not move any files** — reconciling the actual
layout is a decision for whoever owns both branches next, not something to
do unilaterally while both sides still have active work in flight.

## The two structures

**This branch (`feat/v005-empirical-study` and descendants)** — flat,
top-level directories:
- `study/exploratory-labels/ai-shadow-review/` — my (Reviewer A / "ai-shadow") independent labels for
  the 350-item agreement-pilot sample.
- `study/exploratory-labels/teammate-review/` — the teammate's Reviewer C AI-precheck labels for the
  same sample, pulled in from their branch.
- `study/exploratory-labels/annotation-comparison/` — the mechanical agreement/disagreement
  comparison built from the two above (Phase 1), plus the Phase 2
  comparison and cross-phase summary.
- `study/exploratory-labels/stratified-sample/` — the 400-row impact-weighted sample (v0.0.7 corpus)
  plus its Reviewer A and Reviewer C labels and comparison.
- `study/exploratory-labels/stratified-sample-v0071/` — the same methodology re-run on the fixed
  v0.0.7.1 corpus (191-repo clean population), not yet labeled.

**`origin/fix/v007-audit-2026-10-15`** — nested under
`study/validation-v007-human/`:
- `samples/agreement-pilot/` — **the same 350-item master sample** this
  branch's `study/exploratory-labels/ai-shadow-review/` and `study/exploratory-labels/teammate-review/` both label (confirmed:
  this branch's Phase 1 work consumed exactly this sample, pulled in via an
  earlier commit).
- `reviewers/ai-shadow/agreement-pilot.csv` — the teammate's own copy of an
  ai-shadow pass over the same sample (separate from this branch's
  `study/exploratory-labels/ai-shadow-review/`, a third independent AI pass on the same data).
- `reviewers/reviewer-a/agreement-pilot.csv`,
  `reviewers/reviewer-b/agreement-pilot.csv` — **blank forms reserved for
  real human reviewers**, never filled in on either branch.
- `reviewers/reviewer-c-ai-precheck-exploratory/` — the source this
  branch's `study/exploratory-labels/teammate-review/REVIEWER_C_AI_PRECHECK.csv` was pulled from.
- `codebooks/` and `codebooks-v2/` — the review-family definitions; v2 is a
  rewrite responding to ambiguities both branches' AI-comparison passes
  surfaced (see `codebooks-v2/FREEZE_RECORD.md`). This branch has never
  used either version explicitly as a written codebook — the AI labeling
  passes here worked from the rule's own `message`/`concept_id` plus
  general Ansible knowledge, not a frozen family-definition document.
- `pilot2/` — a from-scratch 171-item calibration sample (55 rules, from
  calibration-only repos, built on v0.0.7.1 + codebook v2.1), purpose-built
  to replace `samples/agreement-pilot/` for the real two-human-reviewer
  round. Also has blank `reviewer-a`/`reviewer-b` slots.
- `mappings/rule-family-map.csv` — **the exact file this branch's
  `scripts/build_v007_stratified_sample.py` depends on** (restored from a stray
  local copy to build `study/exploratory-labels/stratified-sample-v0071/`; it was never actually
  committed on this branch's own history until now implicitly via that
  script's output).
- `ai-precheck/` — three more Claude-reference labeling passes at different
  dates/codebook versions, including one that computes its own κ/Gwet AC1
  against the teammate's ChatGPT pass on the same 350-item sample (a close
  but independently-derived analogue to this branch's own
  `study/exploratory-labels/teammate-review/COMPARISON.md`).

## The one real naming collision

**"Reviewer A" means two different things on the two branches.** On this
branch, "Reviewer A" (per the user's explicit instruction mid-session) is
the generic, de-identified label for *my* AI pass, used consistently across
Phase 1 and Phase 2. On the audit branch, `reviewers/reviewer-a/` is a
**blank slot reserved for a real human reviewer**, never an AI identity.
If these two trees are ever merged under one `reviewers/` directory, do
**not** let an AI-labeled "Reviewer A" file collide with or overwrite the
blank human-reviewer-a form — they must stay distinguishable (e.g. keep
this branch's AI passes under an explicitly AI-denoting path, reserving
bare `reviewer-a`/`reviewer-b` names for actual humans, matching the audit
branch's own convention).

## What's genuinely duplicate vs. complementary

- **Duplicate** (three independent AI passes exist over the *same* 350-item
  sample across the two branches: this branch's `study/exploratory-labels/ai-shadow-review/`, the
  audit branch's own `reviewers/ai-shadow/`, and the various `ai-precheck/`
  dated snapshots). None of these should be deleted — each is a real,
  timestamped, independent data point for inter-rater statistics — but any
  future "how many AI passes do we have" accounting needs to count across
  both trees, not just one.
- **Complementary, not duplicate**: this branch's `stratified-sample(-v0071)/`
  (impact-weighted, drawn from the full occurrence distribution, for
  representativeness) vs. the audit branch's `pilot2/` (capped per-family,
  from calibration repos only, for human precision/recall calibration) —
  different sampling purposes, both worth keeping.
- **Audit-branch-only, not yet reflected here at all**: `codebooks-v2/`
  (this branch's labeling never formally cited a frozen codebook version)
  and the actual blank human-reviewer forms (`reviewer-a`/`reviewer-b` on
  both `samples/agreement-pilot/` and `pilot2/`) — **no human has labeled
  anything on either branch yet**. This is the actual bottleneck for
  getting a real (non-AI-vs-AI) agreement number.

## Recommendation

1. **Do not blind-merge the two directory trees.** Both have real,
   independent commit history and neither is a strict subset of the other.
2. **Adopt the audit branch's `pilot2/` + `codebooks-v2/` as the forward
   path for the human-reviewer round** — this was already the conclusion of
   the earlier teammate-work-comparison in this session, repeated here: it
   was purpose-built to fix pilot 1's known defects and sits on the
   already-fixed v0.0.7.1 corpus.
3. **When someone does merge the trees, resolve the "Reviewer A" naming
   collision first**, per the section above, before copying any files — a
   careless merge could silently make an AI pass look like a filled human
   form or vice versa, which is exactly the kind of integrity problem this
   whole study has been careful to avoid elsewhere.
4. **`mappings/rule-family-map.csv` should be formally added to whichever
   branch survives** — right now it only exists safely in the audit
   branch's history and a stray local backup; `scripts/build_v007_stratified_sample.py`
   has a hard runtime dependency on it with no committed copy of its own.
5. This branch's `study/exploratory-labels/annotation-comparison/` tooling (`build_comparison.py`,
   `build_comparison_phase2.py`, `build_final_summary.py`) is schema-driven
   and reusable — once real human labels exist in `pilot2/reviewer-a` and
   `reviewer-b`, the same mechanical classify() approach can produce a real
   human-vs-human (and human-vs-AI) comparison with minimal new code, just
   a new script variant pointed at those files' column names.
