# Verified-claim explanation pipeline: internal development evaluation

Use `--explain --explain-style verified-facts` for source-bound explanations.
The existing `free` style remains a separate option and historical baseline.

The local model selects claim IDs from backend-authored facts. The backend computes bounded static assessments, checks source visibility, attaches exact citations, and renders selected facts. This contract prevents invented model prose but does not establish independent model reasoning or the necessity of using a model. A deterministic primary-claim selector has the same main summary, assessment and citations.

The 48 explanation cases and fixed AI source references are unchanged from V7. Window uses the original +/-6 lines plus the original candidate-definition context; full-file parsing provides structural task binding. Explicit local facts are permitted only when all relevant proof spans are supplied. Otherwise, an exact supplied-window span accompanies a conservative unknown answer. Scoped mode uses the complete relevant task/context.

Final live comparison: 96/96 calls available, with 41/48 verified-window and 45/48 verified-scoped outputs rated adequate with supporting citations under the unchanged fixed-reference rubric. Prior free-prose results were 9/48 and 42/48, respectively. This is a different complete pipeline, not an isolated model intelligence improvement.

`simulated-reviewer-A.csv` and `simulated-reviewer-B.csv` are two internal passes by the same automated evaluator. Each records 86/96 adequate outputs. Their 100% consistency is not independent human agreement; no human kappa or AC1 is reported. Original human forms remain blank. See `model-role.json`, `simulated-review-consistency.json`, `RESULTS.md` and the raw run records for provenance.

The 12 additional authored source-shape fixtures were run in both modes (24 calls); all 24 matched their authored expected configuration states. These are developer fixtures, not independent natural-data validation. Full suite: 1,696 passed, two skipped.

Final sources are archived in `implementation.tar.gz`; model identity and settings are in `freeze.json`. Raw calls, including source/claim prompts and model outputs, are retained under `study/runs/llm-v82-verified-explanation-2026-11-15/` and `study/runs/llm-v82-shape-checks-2026-11-15/`. Earlier V8/V8.1 experiments remain retained separately. No final failed outcome was replaced with a favorable retry.

The paper reading copies are explicitly non-submission drafts with the requested title marker. Detection agreement corrections of 67%, 27%, 77% are author-supplied, not recomputed; unresolved denominators/paired labels remain noted. No participant study or developer comprehension benefit is claimed.
