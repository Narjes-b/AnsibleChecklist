# ICPC 2027 Tool Demonstration readiness — 2026-11-10

**Development follow-up:** [V4.1–V4.3 results](../../study/icpc2027-development-2026-11-10/README.md)
record the paired development runs, backend predicate checks, unresolved prose
contradictions, and current validation. The 48 evaluation cases remain unused
for inference and scoring; human output review is still required.

**Later update:** the owner subsequently authorized the paused model download.
It is installed, local inference works, and V4.1 passed four controlled live
acceptance checks after preserving and repairing one V4 mismatch. See the
[model setup and acceptance record](../../study/icpc2027-model-setup-2026-11-10/README.md).
The initial checkpoint below remains a historical record; its paused-download
and no-live-V4-result statements describe that earlier phase. Human quality
evaluation and final release gates remain open.

Status: development implementation and reproducible engineering checks. **Not a
validated LLM release or a completed paper evaluation.** Local model downloads
were stopped at the owner's request. Do not start or resume downloads until the
owner explicitly asks. Existing frozen study results and labels are unchanged.

Recorded engineering verification: **1,597 passed, two skipped** in the full
suite; 223 latest focused checks passed. Documentation drift, compilation,
whitespace checks, offline wheel build and isolated wheel imports also pass.
See the [validation summary](../../study/icpc2027-readiness-2026-11-10/validation-summary.json).

## Implemented workflow

The paper's intended workflow is repository scan → inspect source evidence →
assess a finding with a local model → inspect a mechanically checked optional
suggestion → compare base/head findings in a pull request. CLI, Markdown, CSV,
JSON, SARIF, and existing GitHub annotations remain the interfaces.

- Prompt `local-review-v4`, response schema 3, evidence packet version 1.
  Response fields are compatible with the prior neutral condition/actionability
  contract; packet, token-usage, suggestion-check, and checkpoint fields are additive.
- Full declared task spans replace fixed windows for recognized source units.
  Inherited controls are supplied with original coordinates. Aliases, merged or
  duplicate mappings, invalid anchors, and ambiguous units remain unavailable
  evidence rather than being rebound to a nearby task.
- Specialized evidence covers explicit TLS verification, file permissions,
  credential logging, and variable-resolution rules, including canonical runtime
  input classifications. Generic rules have explicitly limited coverage.
- Variable queries use task ordinal, play index, task path, case-sensitive name,
  and role visibility. Definition anchors use typed containers, not forward
  substring searches. Unrelated same-name definitions do not resolve a reference.
  Dynamic inputs, unavailable definitions, and omitted candidates stay visible.
- Required missing evidence rejects decisive model answers. Explicit TLS and
  inherited logging facts have bounded consistency checks. These are backend
  predicates, **not independent evidence of model reasoning quality**.
- Citations are checked against the exact snippets supplied in that request;
  quoted source is attached by the backend. Location membership alone does not
  prove relevance or entailment.

Packet `complete` means the implemented bounded evidence contract has no recorded
missing requirement. It does not certify all Ansible runtime behavior. Permissions
still depend on sharing/sensitivity policy; sensitive-value flow and custom module
redaction are not generally certified. Normalized source-line hashes identify
packet contents; evaluation files also retain raw source-byte hashes and Git SHAs.

## Local execution and optional suggestions

```sh
.venv/bin/ansibleguard /path/to/repository --explain \
  --explain-max-items 6 --explain-timeout 120 --explain-budget 600 \
  --explain-checkpoint-dir /private/path/to/attempts
```

The same flags work with `ansibleguard diff`. Ollama must already be running on
loopback with the requested model installed. These commands do not download it.
Hosted endpoints, environment proxies, and redirects remain disabled.

The overall budget limits scheduling and supplies the remaining time to each
HTTP call and suggestion check. Budget-exhausted items stay visible. Blocking
HTTP operations still depend on the transport's timeout semantics; this is not
a hard process-wide cancellation guarantee. No decisive source is silently
truncated. A conservative UTF-8 byte-token ceiling for the selected Qwen byte-BPE
model reserves output/template/schema space; actual Ollama prompt/generation
counts are recorded. Other tokenizers are not certified by that bound.

Private checkpoints use 0700 directories and 0600 files. Every attempt is retained
in `history/`; a separate latest record supports resume. Successful reuse requires
matching source-tree bytes, model digest, occurrence, prompt, schema, generation
settings, and package implementation. Symlink/oversized/unverifiable trees disable
reuse. A changing source tree invalidates the stored result for resume. Cache
writes failing do not discard an otherwise completed explanation. Checkpoints
contain local source and model text; do not publish them without reviewing them.

Suggestions are optional, never applied automatically, and never become native
SARIF fixes. Current permitted edits are narrowly limited to changing an explicit
TLS verification flag to true or adding task-local `no_log: true`. A disposable
copy must parse as one leaf task, preserve unrelated fields, clear the targeted
detector, and pass offline ansible-lint. Other edits, including permissions or
variable changes requiring deployment intent, are withheld. Passing checks does
not establish behavioral equivalence or deployment suitability.

## Evaluation instrument and reproduction

The [case manifest](../../study/icpc2027-readiness-2026-11-10/evaluation/cases.json)
contains 24 development cases and 48 evaluation cases: 24 controlled challenges
and 24 real-source detector examples, six real examples per family. Real cases
come from five previously exposed calibration repositories at frozen SHAs, with
at most two examples per family per repository. This is a convenience case study,
not a probability sample or an untouched repository test set. Controlled panels
exercise related mechanisms in different source structures; they do not establish
generalization to independent natural data.

The package includes blank independent source-review forms, output-quality forms,
and an adjudication sheet. Engineering expectations are explicitly separate from
human labels. No human labels have been generated or adjudicated by this work.

```sh
# Prepare a new instrument; refuses to overwrite existing output.
ANSIBLEGUARD_DISABLE_ANSIBLE_DOC=1 .venv/bin/python scripts/icpc_llm_evaluation.py \
  prepare --output /path/to/new-instrument

# Only after the owner requests model setup and the local model is available:
.venv/bin/python scripts/check_local_llm_acceptance.py --help
.venv/bin/python scripts/icpc_llm_evaluation.py run \
  --manifest study/icpc2027-readiness-2026-11-10/evaluation/cases.json \
  --panel development --output /private/path/to/new-development-run
```

The paired comparison uses the same model/settings with `window` or `scoped`
evidence. It compares the complete evidence/consistency pipeline, not just model
reasoning. Invalid answers, transport failures, and abstentions stay in the
denominator. Natural cases must still match their frozen SHA, clean checkout, and
file hash when run. Complete development checks before opening evaluation outputs;
freeze the implementation and prompts for evaluation. Human agreement, semantic
accuracy, explanation entailment, harmful suggestions, and developer benefit
remain unmeasured until the corresponding reviews/studies are completed.

## Demonstration and PR replay

```sh
# No model invocation or model/dependency downloads by default.
ANSIBLEGUARD_DISABLE_ANSIBLE_DOC=1 .venv/bin/python scripts/run_icpc_demo.py \
  --output /path/to/new-demo

# Replay the exact historical pairs rather than selecting newer merges.
ANSIBLEGUARD_DISABLE_ANSIBLE_DOC=1 .venv/bin/python scripts/pr_replay_study.py \
  --prs-manifest study/pr-replay-v007-2026-10-15/prs.csv \
  --work-dir /path/to/new-scratch-directory \
  --output-dir /path/to/new-replay-results --workers 1 --timeout 600
```

The controlled demo completed with both external providers, no execution
diagnostics, clean source, and three introduced occurrences: TLS verification,
missing tags, and undeclared runtime input. Ratchet reports the warning-level TLS
regression without blocking under the current policy. This is an illustrative
scenario, not evidence of population accuracy. Add `--explain` to the demo only
after local model setup; it also records a runtime-input assessment separately.

Replay records include exact pairs, input hash, implementation hashes, provider
exclusions, timings, and cleanup status. Historical results are not overwritten.
Attribution review concerns whether changes support introduced/fixed status;
whether a finding is a true defect is a separate human judgment.

The development replay completed all 21 pairs: 14 with full provider coverage
and seven with ansible-lint excluded. It reported 44 introduced, seven fixed,
683 moved, 51,058 unchanged, and four uncertain occurrences. All source clones
remained clean and no worktrees were left behind. Automated attribution supported
50 of 51 introduced/fixed findings; one play-level case remains for human review.
These are tool-output counts, not confirmed defects. Three explanation modules
changed during this smoke exercise; its initial implementation hashes therefore
do not certify one immutable release across the entire run. The [replay summary](../../study/icpc2027-readiness-2026-11-10/pr-replay-summary.json)
records this explicitly. Repeat after the release is frozen. Timings also reflect
concurrent host workloads and are not a controlled performance comparison.

## Remaining release and paper gates

1. Owner explicitly requests model download/setup; complete live acceptance and
   retain failures. No current live V4 quality result exists.
2. Two reviewers complete source and output forms; adjudicate disagreements.
   Do not substitute model outputs or engineering expectations for human gold.
3. Freeze a release candidate, rerun affected checks and the accepted evaluation,
   inspect provider partials, and review introduced/fixed attribution.
4. Verify a clean install and public artifact access, resolve licensing with the
   owner, and prepare the recording and final paper figures/tables.

The [official Tool Demonstration call](https://conf.researchr.org/track/icpc-2027/icpc-2027-tool-demonstration)
sets November 19, 2026 AoE, IEEE 4+1 pages, non-anonymous submission, public source
or binaries, and an optional 3–5 minute video. The intended contribution is
evidence-grounded Ansible review support, not validated population precision,
recall, causal impact, or proven developer comprehension benefit.
