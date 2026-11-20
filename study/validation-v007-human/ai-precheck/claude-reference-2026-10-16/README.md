# Claude reference labels for the 350-item agreement pilot (2026-10-16)

## What this is
An AI "reference" labelling of the calibration-only agreement pilot
(`samples/agreement-pilot/`, 350 items, 7 review families x 50). It exists so the human
reviewers' later labels can be compared with a fixed, written-down baseline to see how far
they drift. **It is not gold, not a reviewer, and must never enter precision estimates,
reviewer packets, or the AI-shadow file.**

Protocol note: `protocol/AI_SHADOW_PROTOCOL.md` prefers AI labels to be produced after human
gold. Producing them before was an explicit request from the study owner; keep this folder
separate and never show it to reviewers.

## How it was made
- 7 blind subagents (one per family, 50 items each) followed `codebooks/REVIEWER_INSTRUCTIONS.md`,
  the family codebook and `RULE_OVERRIDES.md`, reading only the frozen context bundles.
  They were told not to read the Reviewer C precheck or any other reviewer file.
- Four agents hit a rate limit and were resumed; no label was invented to fill gaps.
- Rows pass the frozen reviewer validator (0 violations). Extra columns (`ai_confidence`,
  `bundle_issue`) are in `claude-reference-extra.csv` so the main file keeps the frozen schema.

## Files
| File | Content |
|---|---|
| `claude-reference-agreement-pilot.csv` | labels, frozen reviewer schema |
| `claude-reference-extra.csv` | confidence and bundle-defect flag per item |
| `claude-reference-manifest.json` | checksums, counts, validator verdict |
| `observations/*.md` | each agent's free-text observations per family |
| `qc-independent-labels-21-items.csv` | my own blind labels for 21 items (3 per family) |
| `comparisons/` | reference vs Reviewer C (earlier ChatGPT precheck) |
| `FINDINGS.md` | every detail noticed while labelling |

## Distribution (350 items)
semantic: positive 155, negative 120, uncertain 73, unreviewable 2. Confidence: high 109,
medium 169, low 72. Bundle problems flagged: 74 items (other 31, codebook-ambiguous 21,
truncated 14, redaction-hides 7, missing-subject 1).

| Family | positive | negative | uncertain | unreviewable |
|---|---:|---:|---:|---:|
| objective correctness | 28 | 12 | 10 | 0 |
| variable reasoning | 16 | 22 | 11 | 1 |
| security | 32 | 15 | 3 | 0 |
| style/policy | 29 | 10 | 11 | 0 |
| maintainability | 21 | 25 | 4 | 0 |
| structure/reuse | 16 | 27 | 6 | 1 |
| review/history | 13 | 9 | 28 | 0 |

## How reliable is it (read before using)
- **QC against my own blind labels** (21 items): semantic agreement 14/21 = 67%, actionability
  13/21 = 62%. All 7 disagreements were adjudicated; none was an agent mistake I could prove:
  - OC-017: list-valued `vars`. I verified ansible-core 2.21 `--syntax-check` rejects it and a
    mapping passes; the agent judged it valid from older-Ansible knowledge. The codebook has no
    Ansible-version policy.
  - OC-028: `authorized_key` redirect holds in 2.21 routing; agent said uncertain (no version context).
  - RH-026: a PR number used as "bug reference" is undefined in the codebook.
  - SEC-036: my own label drifted toward actionability; the agent's positive/not-actionable follows the separation better.
  - SEC-041: dependency behaviour needs bundle evidence; agent used outside knowledge (my label was the stricter reading).
  - STYLE-047: the codebook gives no length limit.
  - STRUCTURE-030: positive/not-actionable (me) vs uncertain (agent); no definition of the unit.
  The labels stay unchanged as the reference; the disagreements show where the codebook, not the rater, is the problem.
- **Versus Reviewer C** (ChatGPT precheck), 350 items: raw agreement 0.683, kappa 0.516,
  AC1 0.595; on items where both decided (n=232) agreement 0.858, kappa 0.715. Per family
  raw/kappa: objective 0.56/0.33, variables 0.68/0.48, security 0.74/0.47, style 0.76/0.59,
  maintainability 0.62/0.40, structure 0.76/0.57, review/history 0.66/0.42. The two AIs differ
  mostly about whether to commit (reference uncertain 73 vs Reviewer C 84 uncertain+unreviewable)
  and on rules with no operational definition (deprecated-modules, loop-legacy-syntax,
  missing-handler, missing-tags: 0 agreement; see `comparisons/`).
- Expect human-vs-reference agreement to be noisy where the codebook is silent, notably
  review/history (28/50 uncertain). A low number there measures the codebook, not the human.

## Measuring human drift
```
python scripts/v007_human_agreement.py --reviewer-a <human returned file> \
    --reviewer-b study/validation-v007-human/ai-precheck/claude-reference-2026-10-16/claude-reference-agreement-pilot.csv
python scripts/v007_label_comparison.py --a <human file> --b <reference file> --a-name human --b-name reference \
    --output-dir <new dir>
```
Treat rule/family cells with fewer than ~10 items as anecdotes.

## Warning: residual sensitive data in the bundles
While labelling I found data the "redacted" bundles still contain (values not reproduced here):
SECURITY-037 has a token-like string and an email; SECURITY-013 has 8 long base64-looking lines;
14 distinct non-example email addresses appear across the 350 bundles. They come from public
repositories, but the claim "redacted" is not true. The redaction-idempotence check passes on
them, so it cannot detect misses. Regenerate bundles with stronger redaction before sending packets
to human reviewers. See `docs/study/v007-cleanup-for-next-runs.md`.

### Scan result (2026-10-16, `scripts/v007_bundle_secret_scan.py`)
350 pilot bundles: 57 findings in 18 files (47 non-example email addresses, 8 long base64 lines,
2 high-entropy words); 34 of them in review/history bundles (commit author data) and 18 in security bundles.
The CSV `bundle-residual-scan-pilot-350.csv` lists file, line, kind and length only, never the value.
