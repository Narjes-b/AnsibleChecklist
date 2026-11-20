# Frozen timeout triage — context stages

Status: bounded current-code probe completed; historical timeout remains unexplained. No study result or performance eligibility is replaced.

The historical run timed out after 1,800 seconds for `encapsulate-xyz/cosmos-ansible` at commit `a49d30281d2d3c763ef0d50a7aaddc751a460863`. Its empty log does not identify the stalled stage. [profile_frozen_context.py](../../scripts/profile_frozen_context.py) now preserves stage checkpoints, resource limits, profiles and periodic stacks in a separate process.

The probe reads exact verified Git blobs from the existing local stores. It does not checkout, fetch, execute target scripts, invoke providers or call an LLM. A fresh Git boundary prevents inherited workspace configuration. Executable modes are deliberately removed; original repository history/configuration is absent.

## Observed current-code stages

| Stage | Seconds | Result |
|---|---:|---|
| Classification | 0.951 | 148 YAML paths, 145 included |
| Selection | 0.047 | 145 selected files |
| Repository context | 4.486 | 145 parsed documents, 394 indexed tasks |
| Symbol index | 0.758 | 1,357 definitions, 114 edges |

Worker total: **6.281 seconds**, peak RSS **42,908 KiB**, deadline 75 seconds, address-space limit 2,048 MiB. No stack timeout occurred. These are single-run diagnostic timings under profiling, not a benchmark or proof that the archived implementation completed these stages.

Of 417 regular source blobs, 403 were copied and 14 exceeded the 1 MiB per-blob extraction limit. All omitted paths are `roles/node/files/.../genesis.json`; no YAML path was omitted. The same historical selected-file count is recovered. Their omission still prevents claiming a complete repository reproduction, especially for whole-tree secret scanning or data dependencies.

[probe-manifest.json](probe-manifest.json) records code/dependency hashes, worker state and limits. [stage-events.json](stage-events.json) contains flushed checkpoints. [top-functions.csv](top-functions.csv) retains the 40 largest cumulative profile entries. [source-inventory.csv](source-inventory.csv) is a controlled derivative of the ignored local source manifest: all 417 paths, modes, blob OIDs, copied hashes and explicit omissions. Original generated report hashes, source-manifest hash and implementation/dependency hashes were checked after execution. Raw source and logs remain under ignored `study/evidence-local/timeout-context-2026-10-23/`.

Validation: **142 focused tests passed**, covering immutable reads despite dirty working trees, skipped symlinks, non-execution of executable source, separate-process stage completion, rejected mutable/unsafe identities and existing retrieval/context/symbol behavior.

## Reproduce and continue

```sh
.venv/bin/python scripts/profile_frozen_context.py \
  --project encapsulate-xyz/cosmos-ansible \
  --commit a49d30281d2d3c763ef0d50a7aaddc751a460863 \
  --repositories-root study/repositories \
  --repositories-root study/cache/v0071-rerun-2026-10-22/repositories \
  --local-dir study/evidence-local/timeout-context-NEW \
  --report-dir study/timeout-context-NEW --timeout 75
```

Use new output directories. Acquisition is outside the worker deadline; individual Git reads have separate limits. The remaining candidates are per-file detectors, module metadata, external providers and later reporting. Next isolate file detectors with flushed file/stage checkpoints, then examine provider input sizes and diagnostics. Raising the old repository deadline is not yet justified.
