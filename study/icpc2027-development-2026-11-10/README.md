# Local-model development results — V4.1 to V4.3

Local inference works with `qwen2.5-coder:7b`. The latest scoped pipeline passed
the decision contracts on 24 development cases and eight additional structural
challenges. **These are backend-constrained engineering checks, not independent
model classification accuracy. Model prose still contains contradictions.**

Work began November 10 and resumed November 11 after an execution-service restart.
The directory and run names retain their original date. No additional model was
downloaded. The separate 48-case evaluation panel has not been used for inference
or scoring, and its manifest and blank reviewer forms still pass their original
checksums. Earlier setup and acceptance attempts remain in the
[model setup record](../icpc2027-model-setup-2026-11-10/README.md).

## Retained development attempts

Each row reports matches against authored engineering expectations, including
failed requests in the denominator. The first three rows reuse the same 24 cases;
they are not 72 independent observations. Each case runs fixed-window then scoped
mode. Timing is affected by model warm-up and host workload.

| Attempt | Cases | Window matches / errors | Scoped matches / errors | Scoped decision constraints |
|---|---:|---:|---:|---|
| V4.1 | 24 | 11 / 2 | 20 / 0 | 10 required abstentions |
| V4.2 | 24 | 11 / 1 | 20 / 0 | 10 required abstentions |
| V4.3 | 24 | 10 / 4 | 24 / 0 | 14 predicates + 10 required abstentions |
| V4.3 additional challenges | 8 | 3 / 1 | 8 / 0 | 7 predicates + 1 required abstention |

See [comparison-summary.json](comparison-summary.json) and the complete per-attempt
summaries, decisions, failures, and input checksums under [results](results).
Raw requests, responses, envelopes, histories and source archives remain under:

```text
study/runs/icpc2027-development-v41-pass1-20261110/
study/runs/icpc2027-development-v42-pass2-20261110/
study/runs/icpc2027-development-v43-pass3-20261110/
study/runs/icpc2027-development-v43-challenges-20261110/
```

These raw run directories are ignored by Git; retain them with the research
artifact package. Failed records were neither removed nor replaced. The V4.3
original run persisted one result before interruption. The recovery reused it and
processed 47 pending records with the same recorded pipeline hashes and model
digest. Its manifest records the interruption and unknown in-flight outcome;
recovery timing excludes the interruption. `resume-v43.py` and `recovery.log`
provide the recovery audit, not a new model attempt chosen to improve a score.

## Repairs and their scope

V4.1 exposed incorrect permission-policy and logging decisions. Wording and
permission-bit explanations in V4.2 did not resolve the four scoped mismatches.
V4.3 moves closed static questions into explicit backend checks, so the model
explains a bounded result instead of deciding the rule's policy:

- Literal TLS settings identify whether verification is explicitly disabled.
- Direct module mappings reuse the existing permission detector on the supplied
  leaf, including intentional shared-directory handling.
- Direct `debug` displays use the existing logging policy with literal effective
  `no_log`, including inherited controls and task overrides. Opaque register
  aliases and dynamic controls are outside this bounded check.
- Unconditional, must-visible anchored variable definitions contradict a missing
  source-definition claim. Unknown runtime inputs still require abstention.

The generation schema constrains verified decision states and requires missing
context to produce low-confidence, non-actionable abstention with no fix. Runtime
validation still checks responses and citations. Reports label backend condition
checks separately from unverified AI explanations. Failed evidence assembly does
not send incomplete source context to the model.

This is the tool's bounded static policy, not proof of a deployed defect. Other
syntax, opaque value flow, module behavior and deployment context remain limited.
All 32 latest scoped decisions were constrained: there were **zero unconstrained
model decisions** in these two runs. Therefore 32/32 cannot support a claim about
model reasoning accuracy or a retrieval-only improvement.

## Unresolved explanation failures

Correct structured states did not make the prose reliable. Agent inspection found
summaries that deny visible variable definitions, ignore effective `no_log: true`,
or assert that an unresolved TLS variable disables verification. The additional
challenges reproduce the logging and variable-summary problems.

[prose-audit.json](prose-audit.json) preserves diagnostic flags and exact response
excerpts. These are agent observations, not independent reviewer labels, an
exhaustive audit, or a measured explanation-quality score. Citation membership
checks verify that a cited line was supplied; they do not prove entailment.
No code suggestions were proposed in these development runs, so they do not
establish suggestion quality or safety.

## Validation and candidate identity

- Full suite: **1,609 passed, two skipped**, exit 0; see [pytest-v43.log](pytest-v43.log).
- Offline wheel build and imports of the evidence and explanation modules passed.
- Original readiness-package checksums passed, including all evaluation forms.
- Prompt `local-review-v4.3`, response schema 3, evidence contract 3.
- Model digest and artifact hashes: [candidate-manifest.json](candidate-manifest.json).
- Source and test identities: [source-files.sha256](source-files.sha256), relative
  to the repository root.

The wheel is a provisional development candidate, not a quality-certified release.
The paper can describe the implemented checks and these engineering diagnostics.
Claims about grounded or useful explanations require the planned two-reviewer
source/output review and adjudication. Keep the 48 evaluation cases separate from
further development, freeze the evaluated candidate before inference, and retain
errors, abstentions and prose contradictions in the final analysis. Final release
PR replay, public artifact verification, and the recording remain outstanding.

To reproduce a new development run without downloading a model:

```sh
ANSIBLEGUARD_DISABLE_ANSIBLE_DOC=1 .venv/bin/python scripts/icpc_llm_evaluation.py run \
  --manifest study/icpc2027-readiness-2026-11-10/evaluation/cases.json \
  --panel development --output /path/to/new-run --timeout 120 --budget 3600
.venv/bin/python scripts/summarize_icpc_development.py \
  --manifest study/icpc2027-readiness-2026-11-10/evaluation/cases.json \
  --run /path/to/new-run --output /path/to/new-analysis
```
