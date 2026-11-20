# Integration into the existing project

## What already existed (inspected before writing anything new)

- **Annotation pipeline**: `scripts/export_v007_reviewer_packets.py`,
  `scripts/v007_validation_pilot.py`, and this session's own
  `ai-shadow-review/` / `teammate-review/` / `annotation-comparison/` outputs
  already establish a schema for an "issue": `sample_id`, `rule_id`,
  `review_family`, `repository`, `commit_sha`, `path`, `line_start`/`line_end`,
  `source_context` (frozen, numbered source excerpt), plus a detector/agent's
  `semantic_label`, `actionability_label`, `reason_code`, and free-text `notes`.
  **This project reuses that exact schema** for issue input — `explain.py` reads
  any CSV with those column names, so it runs unmodified against
  `annotation-comparison/consolidated-comparison.csv`, the stratified sample, or
  a fresh AnsibleGuard scan's output, without writing a second extraction layer.
- **Detection vs. explanation were already separate**: AnsibleGuard's detectors
  (`src/ansibleguard/detectors/`) produce a label + a short, fixed `message`
  string. Nothing in the existing pipeline generates an extended, contextual
  explanation of *why* a specific occurrence is a problem in its specific
  surrounding code — that's the actual gap Task 2 asked to fill, confirmed by
  reading the detector and annotation code before writing anything.

## What this adds

```
local-llm/
  MODEL_SELECTION.md       Task 2.2 — model/engine research and recommendation
  PROMPT_DESIGN.md         Task 2.3 — explanation schema and prompt, versioned
  scripts/
    prompt_template.py     the versioned system/user prompt (import, don't copy)
    explain.py             Task 2.4 — calls Ollama, writes one audit record per issue
  eval/
    eval_cases.csv          Task 2.6 — 12 hand-selected representative issues
    run_eval.py             runs explain.py over eval_cases.csv and scores against the rubric
    EVAL_RESULTS.md          Task 2.6 output — actual results, not just the harness
  outputs/
    <issue_id>.json         Task 2.5 — one full audit record per explained issue
  COMPARISON.md             Task 3 — local model vs. existing agents, per the rubric
```

## Separation of concerns (explicit, per the brief's working principles)

- **Detection** (AnsibleGuard's rule engine) is untouched. This project never
  edits a detector or a `.yml`/`.yaml` source file.
- **Classification** (the two agents' `semantic_label`/`actionability_label`
  calls, and Task 1's agreement/disagreement classification) is untouched —
  `explain.py` reads those fields read-only, into
  `original_detector_annotation` in each audit record, and never writes back to
  `annotation-comparison/consolidated-comparison.csv` or either source agent's
  CSV.
- **Explanation** (this project) is new, additive, and lives entirely under
  `local-llm/outputs/`.
- **Human validation** (`final_validated_label` in Task 1's CSV) is untouched by
  this project entirely — the local model's output is explicitly a fourth,
  separate opinion alongside the two agents', never a vote that resolves their
  disagreement and never written into that column.

## Modularity

`explain.py` only talks to Ollama's REST API (`POST /api/chat`, `format: "json"`)
over `http://127.0.0.1:11434`. Swapping the backend later — a different Ollama
model, a raw llama.cpp server with an OpenAI-compatible endpoint, or a hosted
API — only requires changing the URL/payload shape inside `call_ollama()`; the
issue-reading, audit-record, and CLI code is backend-agnostic.

## What remains incomplete (stated plainly, per the brief's final working principle)

- **End-to-end verification is now done.** `qwen2.5-coder:7b` (Q4_K_M) is
  pulled and running live via native Windows Ollama; `explain.py` has been
  run against it for all 12 eval cases, with real results in
  `eval/EVAL_RESULTS.md`. Getting here required installing Ollama itself
  (worked around a sudo-password hang in WSL and a university firewall
  resetting large downloads mid-transfer by switching networks and using a
  self-healing resumable-download loop) and fixing two real bugs in this
  pipeline's own code, both documented in `eval/EVAL_RESULTS.md`:
  `source_context` was being read under the wrong field name (so every
  pre-fix explanation was generated with no real source code at all), and
  Ollama's server-side context window defaults to 4096 tokens regardless of
  the model's advertised 32768 max, silently truncating larger prompts.
- **Ollama's `format: "json"` constrained-decoding behavior** is *not*
  reliably strict in practice: it was observed emitting syntactically valid
  JSON with entirely wrong key names (matching no part of the requested
  schema) on at least one case, and truncated/malformed JSON (degrading into
  repeated whitespace) on another case across 4 repeated attempts.
  `explain.py`'s `validate_explanation()` catches both via its missing-keys
  check, so this doesn't silently corrupt results, but confirms the defensive
  check is necessary, not just precautionary.
- **GPU behavior was observed, not rigorously benchmarked**: the model runs
  on the actual RTX 5060 Laptop GPU (confirmed via Ollama's model details,
  `"runner": "ggml"`, 7.6B params at Q4_K_M), with per-case latencies in the
  eval run mostly in the 4-20s range. No systematic throughput/VRAM-ceiling
  measurement was done beyond what's needed to get results — see
  `eval/EVAL_RESULTS.md` for what was actually measured.
- **The model's self-reported `confidence` field was found to carry no
  real information** in this eval (11/11 successful cases reported
  `confidence: high`, `limitations: None`, regardless of case difficulty or
  whether other reviewers had flagged the same issue as uncertain) — this is
  a finding about the model's behavior as integrated, not an unverified gap,
  but it means any future use of that field for triage needs this fixed
  first (see `eval/EVAL_RESULTS.md` headline section).
