# Local model setup and live development acceptance — 2026-11-10

The owner explicitly authorized completing the paused download. **Ollama now has
`qwen2.5-coder:7b` installed and local inference works.** No other model was downloaded.
Ollama is version 0.31.1; the model is Q4_K_M, 7.6B parameters, approximately 4.7 GB.
The [setup record](model-setup.json) contains the exact model and weight digests.

The native multipart download stalled and rolled progress back after connection
resets. Resumable IPv4 ranges retrieved the exact official-registry weight blob;
its SHA-256 was checked locally and by Ollama's blob API before the native pull
completed the original manifest, template, system prompt and license. The temporary
duplicate weight file was removed after the Ollama copy was verified. Completed
PR scan outputs were archived and checksummed under
`study/runs/icpc2027-pr-replay-20261110/scan-artifacts.tar.gz` before their temporary
scratch copies were removed; original corpus clones were preserved.

## Retained live development attempts

| Attempt | Result | Interpretation |
|---|---|---|
| [V4](acceptance/acceptance-manifest.json) | 3/4 expectations matched | The runtime-input answer listed missing evidence but chose unsupported; the validator rejected it. |
| [V4.1](acceptance-v41/acceptance-manifest.json) | 4/4 expectations matched | Two literal TLS conditions, one required-context abstention, and one invalid-anchor no-call check passed. |

V4.1 expresses an existing backend requirement in the generation schema: when a
specialized packet records required missing evidence, only insufficient-evidence,
low confidence, non-actionable states and null fixes can be generated. Unrestricted
requests retain the general schema. Runtime validation remains independent and
still rejects malformed or inconsistent answers. Actual per-call schema hashes
are retained. The original failed answer was not edited or discarded.

**This is backend-constrained development acceptance, not independent evidence of
model reasoning accuracy.** All four cases are controlled contracts; the fourth
makes no model request. Natural-case accuracy, explanation entailment, harmful
suggestions and developer comprehension still need their planned human reviews.
The 24/48-case instrument and blank reviewer forms remain unchanged.

Validation after this repair: **224 focused tests passed** across explanation,
evidence, snapshot, reporting and evaluation tooling. Observed runtime placement
was 91% GPU / 9% CPU on the RTX 3050 6 GB, with an 8,192-token context. These are
configuration observations, not a controlled performance benchmark.

The controlled end-to-end CLI demo also completed with live explanations:
both scan/comparison commands exited 0, no providers were excluded, the TLS
explanation was accepted with no model errors, and the runtime-input example
returned insufficient-evidence. Source remained clean. Outputs are retained in
`study/runs/icpc2027-demo-with-llm-20261110/`. This remains an illustrative demo,
not the human-reviewed evaluation panel.

Reproduce into a new output directory:

```sh
ANSIBLEGUARD_DISABLE_ANSIBLE_DOC=1 .venv/bin/python scripts/check_local_llm_acceptance.py \
  --output /path/to/new-acceptance-run --timeout 120 --budget 360
```

This command uses the installed local model and does not download one. Model
setup unblocks the development evaluation; human validation and a final immutable
release remain open gates for the paper.
