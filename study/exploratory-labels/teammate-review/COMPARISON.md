# AI-vs-AI comparison: my labeling vs. teammate's Reviewer C precheck

**Both are independent AI labelings of the same 350-item agreement-pilot sample**
(`study/validation-v007-human/samples/agreement-pilot/agreement-pilot-master.csv`),
done blind to each other. Neither is human gold. Per the pilot protocol, this
agreement-pilot sample is permanently excluded from detector performance scoring —
this comparison is about inter-AI-rater agreement only, not precision/recall.

- Mine: `ai-shadow-review/agreement-pilot-ai-shadow-completed.csv` (model: claude-sonnet-5,
  protocol: ai-shadow-v1)
- Teammate's: `teammate-review/REVIEWER_C_AI_PRECHECK.csv` (`reviewer-c-ai-precheck-exploratory`,
  explicitly logged by them as an exploratory precheck, not human gold or AI-shadow)

## Headline numbers

| Metric | Value |
| --- | --- |
| Rows compared | 350 / 350 |
| Raw agreement | 66.0% (231/350) |
| Expected (chance) agreement | 35.9% |
| Cohen's kappa | **0.47** (moderate) |

## Per-family raw agreement

| Family | Agreement |
| --- | ---: |
| Style/policy | 82.0% |
| Security | 78.0% |
| Variable/reference reasoning | 76.0% |
| Structure/reuse | 74.0% |
| Maintainability/complexity | 72.0% |
| Objective correctness | 50.0% |
| Review/history | 30.0% |

## Confusion matrix (rows = mine, columns = teammate's)

|            | positive | negative | uncertain | unreviewable |
| ---------- | -------: | -------: | --------: | -----------: |
| positive   |      115 |       34 |        35 |             0 |
| negative   |        8 |       94 |        24 |             1 |
| uncertain  |        4 |       10 |        21 |             2 |
| unreviewable |      0 |        1 |         0 |             1 |

## What's driving the disagreement

1. **Review/history (30% agreement) is the weakest family by far.** Teammate's agent
   marked all 25 `commit-message-format` rows `uncertain`, reasoning that each
   repository's actual configured subject/body length policy wasn't in the frozen
   bundle. I judged most of these against general Conventional-Commit norms instead,
   landing on `positive`/`negative`. This is a genuine, defensible difference in how
   strictly to interpret "policy not stated in evidence" — not a mistake on either
   side — and is exactly the kind of disagreement a real human agreement-pilot round
   is supposed to surface and resolve via codebook revision.

2. **Objective correctness (50%)** — the second weakest family — shows a similar
   pattern: where evidence was sufficient but the "correct" reading required inferring
   intent (e.g. idempotency of a command given surrounding guards), the two agents
   sometimes read the same evidence differently.

3. **69 of 119 disagreements (58%) involve `uncertain` on one side only** — i.e., one
   agent called a binary label where the other called `uncertain`. This is the single
   largest disagreement pattern (see confusion matrix row/column `uncertain`), and
   suggests the codebook's threshold for "evidence is sufficient" needs tightening
   before a real human round, since two independent AI readings of the identical
   written rubric diverge mainly on *how much missing context forces `uncertain`*
   rather than on the underlying semantic call.

4. **Security, Style/policy, Variable/reference, Structure/reuse all agree 72–82%**,
   which is a reasonable range for a first-pass pilot and suggests those family
   codebooks are comparatively well-specified.

## Caveat

Kappa of 0.47 would not clear the study's own stated human-pilot target (Cohen's
kappa ≥ 0.80, per `PILOT_PROTOCOL.md`). That target is defined for two **independent
human** reviewers, not two AI passes, so this number is informative about where the
codebooks are still ambiguous — it is not a claim that either AI labeling is "wrong,"
and it is not a substitute for the actual human agreement-pilot round.
