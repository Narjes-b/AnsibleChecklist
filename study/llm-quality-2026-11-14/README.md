# Independent LLM quality study

Paper files are unchanged. This package separates implemented evaluation tooling
and automated execution from scientific results that require real human input.

**Scope update:** the owner deferred developer recruitment on November 14 because
of the November 16 submission deadline. Comprehension materials remain dormant;
no participant study or comprehension benefit is claimed. Continue explanation
and repair evaluation only. The frozen original protocol remains unchanged for
auditability; see SCOPE_CHANGE.md for the active scope.

## Current human gates

- **Explanation correctness:** reviewers A and B must independently complete the
  48 explanation source rows, then a facilitator adjudicates them. Model outputs
  stay private until this step finishes. Only then export and judge outputs.
- **Semantic fix correctness:** independently review the 12 repair source cases
  and declared deployment intent before running repair inference. Mechanical and
  synthetic behavioral results do not replace human intent judgments.
- **Developer comprehension:** independently finalize the 12 comprehension source
  cases and scoring rubrics, then record recruitment requirements, generate the
  frozen explanations and offline pages, and collect actual developer responses.

All 72 source cases have blank independent A/B forms and a separate adjudication
form. Review only the relevant panel if staging the work. Never copy engineering
expectations or AI prechecks into these human forms.

The active reviewer ZIPs contain only the 60 explanation/repair source cases.
Each ZIP includes a reviewer-specific blank CSV, source packets and instructions,
without model outputs or engineering expectations. Return the CSV under its
original name; preserve the original completed forms before adjudicating.

The authoritative [protocol](../../docs/study/llm-quality-study-protocol.md)
defines outcomes and limits. [Reviewer instructions](REVIEWERS.md),
[facilitator instructions](FACILITATOR.md), and [draft consent](CONSENT-DRAFT.md)
describe the human work. Final execution status is recorded in STATUS.json.

## Commands

Run from the repository root with the existing virtual environment. Commands
refuse to overwrite study packages, freezes, review exports, participant imports,
and behavioral results. Keep raw run directories private.

```sh
# Already prepared and frozen. Do not repeat against the same directory.
.venv/bin/python scripts/llm_quality_study.py prepare --output /path/to/new-package
.venv/bin/python scripts/llm_quality_study.py freeze --package /path/to/new-package

# Frozen 48-case comparison; a failure remains in the denominator.
ANSIBLEGUARD_DISABLE_ANSIBLE_DOC=1 .venv/bin/python scripts/llm_quality_study.py run \
  --package study/llm-quality-2026-11-14 --panel explanation \
  --run /private/path/to/new-explanation-run --output /private/path/to/run-summary.json
# Add --resume only for an existing interrupted run. Completed failures are not retried.

# After both independent source forms and source-adjudication.csv are complete:
.venv/bin/python scripts/llm_quality_study.py export-review \
  --package study/llm-quality-2026-11-14 \
  --run study/runs/llm-quality-2026-11-14-explanation --output /private/path/to/output-review
# Distribute only packets/ and the assigned reviewer's CSV. Keep mapping-private.json private.

# After independent output review AND separate output adjudication:
.venv/bin/python scripts/llm_quality_study.py summarize \
  --package study/llm-quality-2026-11-14 \
  --run study/runs/llm-quality-2026-11-14-explanation \
  --review /private/path/to/output-review --output /private/path/to/explanation-quality.json

# After repair source approval, use run with --panel repair and a new run directory.
# Then test delivered suggestions only; no proposals means no measured repair quality.
.venv/bin/python scripts/llm_behavior_checks.py \
  --package study/llm-quality-2026-11-14 --run /private/path/to/repair-run \
  --output /private/path/to/repair-behavior.json

# After comprehension source/rubric approval, use run with --panel comprehension.
# Record actual review determination and closing date in recruitment.json before opening.
.venv/bin/python scripts/llm_quality_study.py participant-pages \
  --package study/llm-quality-2026-11-14 --run /private/path/to/comprehension-run \
  --output /private/path/to/participant-pages
.venv/bin/python scripts/llm_quality_study.py participant-import \
  --package study/llm-quality-2026-11-14 --responses /private/path/to/P01-responses.json \
  --output /private/path/to/participant-import
# Import all received JSON files together. --allow-partial preserves incomplete
# sessions separately rather than silently treating them as completed participants.
.venv/bin/python scripts/llm_quality_study.py participant-summarize \
  --package study/llm-quality-2026-11-14 --responses /private/path/to/participant-import \
  --grades /private/path/to/participant-import --output /private/path/to/comprehension-results.json
```

No recruitment or participant simulation occurs automatically. The scripts do
not send messages, apply fixes to a repository, or edit a manuscript.

## Reproducibility and privacy

`manifest.json` retains the original case hash and separate panels. `freeze.json`
records implementation, source-packet and assignment identities and local model
digest. `implementation.tar.gz` preserves the candidate sources. `environment.json`
records installed packages. Raw requests, responses and checkpoint histories are
under ignored `study/runs/` paths; preserve them when preparing a research archive.

Do not give reviewers the freeze/manifest, private inference records, engineering
expectations, or assignment keys before their independent source judgments. Do
not publish participant data, repository source snippets, or raw inference before
reviewing consent, licenses, and sensitive content.
