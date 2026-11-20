# V6 development improvement and repeated experiment

Paper files, original human forms, and previous result files remain untouched.
This is another development iteration on exposed cases, not a new held-out study.
Developer recruitment remains deferred by the owner.

## Changes

- The fixed-window/generic path has its own source-only prompt. It no longer
  requests a nonexistent backend-authored summary. Both conditions reason before
  producing a summary; neither treats the detector accusation as evidence.
- Prompt compaction retains parsed numeric permission types/bits and whether
  no_log is shown, literal, or runtime-dependent. Full primary source spans stay
  present. Important typed facts are no longer lost to the last-note-only shortcut.
- Bounded checks reject explicit numeric contradictions and invented no_log
  usage. This is not general verification of model reasoning; all rejected calls
  remain failed outcomes in the denominator.
- Mode-omission citations include an exact, complete leaf mapping as an additive
  `source_span` alongside the original line quote. This makes the omission
  inspectable without inventing a nonexistent mode line. Scalar command bodies
  cite actual sensitive-reference lines as well as their header.
- `scripts/requested_repair.py --generator local-model` explicitly asks the local
  model to generate a selected narrow edit from the BEFORE task and caller intent.
  No reference AFTER snippet is sent. Eligibility, AST preservation, targeted-rule
  clearance, offline lint and source-change checks are independent backend gates.
  Failed generations are retained and never replaced with backend drafts.

The existing backend generator remains the default, with its origin unchanged.
Neither generator applies source changes. The model-written requested-edit task
is separate from spontaneous repair/actionability recommendation; its proposal
rate cannot replace the earlier 0/8 spontaneous fix rate.

Packet version is 3, contract version 5, prompt `local-review-v6.0`. Response schema
is still version 3; source-span support is additive backend evidence metadata.

## Evaluation

Repeat the same 48 cases under window/scoped conditions and retain every outcome,
including invalid responses, rejects and interrupted unknowns. Keep the original
AI source labels fixed. A new manual AI-rating CSV must cover all 96 new outputs;
previous case-specific content ratings are not reused to grade new prose.
Adequacy includes BOTH backend fact summaries and free model reasoning; a correct
summary does not rescue incorrect reasoning. Strict citation review can inspect
the newly attached exact source span for omission claims.

The same Qwen model digest, 8192-token context, 1024-token generation limit,
temperature 0.1 and 120-second request timeout are retained. The requested-edit
model is given a different, simpler output contract and explicit edit selection;
that task change is intentional and must be disclosed in any comparison.
Source/module-policy ambiguity in three generic credential reference labels
remains disclosed; do not revise labels to inflate the new score.

This is a single, unblinded AI implementer's exploratory assessment. It does not
establish independent human correctness, population quality, causal retrieval
benefit, necessity of LLM explanations, or developer comprehension benefit.
Timing is descriptive: shared host workloads and the model request queue affect it.

## Example: explicitly requested model-written draft

```sh
.venv/bin/python scripts/requested_repair.py \
  --root /path/to/repository --file tasks.yml --line 12 \
  --kind enable-tls-verification --generator local-model \
  --intent 'Endpoint authentication is required and its certificate is trusted.' \
  --output /private/path/to/model-proposal.json
```

Use protect-task-output only for supported direct debug displays. Four already-
correct/unknown-runtime fixtures must be withheld before any generation request.
No repository code is applied or executed by the generator. The behavioral probes
run only tightly bounded synthetic fixture tasks inside isolated containers.
