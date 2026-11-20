# ICPC 2027 development readiness package

This package records implemented engineering work and the remaining release gates.
It is **not a completed LLM evaluation or a publication-ready release**.

| Artifact | Purpose |
|---|---|
| [Engineering record](../../docs/study/icpc2027-tool-readiness-2026-11-10.md) | Behavior, commands, limits and release gates |
| [Validation summary](validation-summary.json) | Test/build/demo results and outstanding work |
| [Implementation manifest](implementation-manifest.json) | Exact source hashes, environment, prompt/schema versions and binary identity |
| [PR replay summary](pr-replay-summary.json) | 21 comparisons, provider exclusions, attribution status and implementation-stability limitations |
| [Evaluation manifest](evaluation/cases.json) | 24 development and 48 evaluation cases; controlled expectations are not human gold |
| [Reviewer instructions](evaluation/REVIEW.md) | Independent source review, output review and adjudication |
| [Paper preparation](PAPER_PREPARATION.md) | Four-page outline, claim ledger, figure source and recording script |

The final engineering suite passed **1,597 tests with two skips**. The latest
focused checks passed 223 tests. The controlled demo completed with both external
providers, no execution diagnostics, and three introduced occurrences. The local
wheel was built without dependency downloads and imported successfully from an
isolated target using the existing dependency environment.

Generated outputs, retained locally under ignored `study/runs/`:

- `icpc2027-demo-20261110/`: illustrative scan, comparison, logs and clean fixture.
- `icpc2027-build-20261110/`: development wheel; its hash is in the validation summary.
- `icpc2027-pr-replay-20261110/`: exact historical PR pair replay and diagnostics.

PR replay is a development smoke exercise performed while engineering changes
were being made. Its initial source hashes do not establish an immutable final
release across every subprocess. Inspect the replay summary and rerun against the
eventual frozen release before using it as paper evidence. Automated change
attribution is separate from human defect correctness.

**Downloads are stopped.** The owner requires an explicit request before any
model download resumes. The model is not currently installed and no live V4
quality result exists. Source/output reviewer forms and adjudication remain blank.
Reviewers must supply their own judgments; neither model output nor controlled
engineering expectations substitute for human labels.
