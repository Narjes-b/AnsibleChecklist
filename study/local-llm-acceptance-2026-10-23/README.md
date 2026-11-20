# Local synthetic acceptance — first pass, 2026-10-23

**Failed at transport: no model answers were produced.** This is a production-path engineering diagnostic, not real-project accuracy or human labelling. Preserve this pass when repairing the backend.

Follow-up: [grammar repair and second live pass](grammar-repair/README.md). Transport succeeds there, but quotation errors and contradictory prose still prevent acceptance.

Next: [neutral schema v3 and third development pass](neutral-v3/README.md). Backend quotation and literal conditions improve; missing runtime evidence is still misclassified. These reused fixtures are not an independent evaluation set.

| Synthetic contract | Expected | Observed |
|---|---|---|
| Explicit `validate_certs: false` | supported | HTTP 400; no answer |
| Same false claim with `validate_certs: true` in source | unsupported | HTTP 400; no answer |
| Undefined-variable claim without runtime/inventory evidence | insufficient-evidence | HTTP 400; no answer |
| Anchor 999 in a one-line file | insufficient-context; no request | passed; no request |

Four cases retained, three model requests, one attempt per case, no retry. Duration **10.485 seconds**. The local Qwen 7.6B Q4_K_M digest stayed `dae161e27b0e90dd1856c8bb3209201fd6736d8eb66298e75ed87571486f4364`. Local Ollama CLI observed version: **0.31.1**.

## Diagnosis and next repair

The three case records preserve the exact system/user prompts, HTTP error, duration, source, engineering expectation and integrated result. `acceptance-manifest.json` hashes the case records, backend, runner, prompt, schema and fixture definitions, records model identity before/after, and explicitly excludes performance scoring.

One additional diagnostic replay of the first request captured the response body in [transport-diagnostic.json](transport-diagnostic.json): sampler grammar initialization failed. This extra diagnostic request is separate from the manifest's three case requests; it also produced no model answer.

The local server journal reported:

```text
parse: error parsing grammar: number of repetitions exceeds sane defaults, please reduce the number of repetitions
Failed to initialize samplers: failed to parse grammar
```

The newly added 20,000-character schema string bounds become excessive grammar repetition bounds in this installed backend. The next repair will separate the generation grammar's compatible constraints from authoritative runtime validation. Runtime size checks, byte caps, enum/type/field checks, citation matching and no-fix-on-abstention rules must remain enforced. Rerun into a **new directory** and retain this failed pass.

## Reproduce

```sh
.venv/bin/python scripts/check_local_llm_acceptance.py \
  --output /tmp/ansibleguard-local-acceptance-REPLAY --timeout 60 --budget 180
```

The runner uses the integrated `explain_occurrence` path and loopback-only transport. It writes each completed case and an atomic progress manifest, preserves mismatches/errors, records pending IDs on interruption, and refuses existing output directories. The budget controls remaining per-request timeout checks; it is not a process-level deadline for every context/preparation operation.

Harness regression check: **136 passed** across harness, LLM and assessment reporting suites, including valid-but-semantically-wrong model stubs retained as mismatches, interruption, budget exhaustion and no remote endpoints. Stub tests passing did not prevent this live grammar failure, which is why both records are reported separately.
