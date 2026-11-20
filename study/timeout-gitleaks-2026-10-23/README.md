# Frozen timeout triage — complete-tree GitLeaks

Status: repeated full-file reads in GitLeaks noise postprocessing reproduced and repaired. The repaired provider probe completes; the historical full repository run remains incomplete and requires a fresh end-to-end rerun.

[profile_frozen_gitleaks.py](../../scripts/profile_frozen_gitleaks.py) materializes **all 417 regular frozen Git blobs / 470,774,640 bytes** for `encapsulate-xyz/cosmos-ansible` at `a49d30281d2d3c763ef0d50a7aaddc751a460863`, with a declared 100 MiB per-blob limit. No file was skipped. Source remains ignored and executable modes are removed. Fresh empty Git boundary; original history/configuration absent. No target programs or LLMs run.

The current production GitLeaks adapter is instrumented without changing its selection/filtering behavior: flushed events separately bracket native subprocess and noise postprocessing. A 90-second worker deadline kills its process group, including a surviving native child; periodic stack dumps and profiles survive where possible. The native provider has its own shorter 30-second timeout. No raw source, finding values or stderr are published.

## First observed result

- Native scan exceeds 30 seconds; adapter returns `timeout` after **30.045 seconds**.
- Noise postprocessing never starts. Zero returned findings is a timeout result, **not a clean scan**.
- Full-tree acquisition completes; inventory and every copied blob hash are retained in [source-inventory.csv](source-inventory.csv).
- Local binary reports the placeholder `version is set by build process`; a meaningful semantic version is unavailable. [probe-manifest.json](probe-manifest.json) records its executable SHA-256. Do not silently assume its version matches the archived tool.
- [stage-events.json](stage-events.json), [top-functions.csv](top-functions.csv) and [stack-frames.csv](stack-frames.csv) retain timing evidence. Generated output and implementation/dependency hashes checked after execution.

**25 focused tests passed** across both probe modes and GitLeaks behavior: real separate-process detector execution, trusted fake-provider native/filter checkpoints, retained provider timeout and rejected invalid deadline combinations. Synthetic provider fixtures are test programs, not corpus code.

## Predeclared next diagnostic

Before executing, choose exactly one additional current-code run: native timeout **120 seconds**, worker deadline **150 seconds**, otherwise the same complete frozen tree, binary and adapter. Preserve both outcomes. The purpose is to determine whether native scanning finishes and, if it does, whether noise postprocessing stalls. These shorter diagnostic limits do not reproduce or replace the study's 600-second provider / 1,800-second outer limits. No full population rerun is authorized by these results alone.

```sh
.venv/bin/python scripts/profile_frozen_gitleaks.py \
  --project encapsulate-xyz/cosmos-ansible \
  --commit a49d30281d2d3c763ef0d50a7aaddc751a460863 \
  --repositories-root study/repositories \
  --repositories-root study/cache/v0071-rerun-2026-10-22/repositories \
  --local-dir study/evidence-local/timeout-gitleaks-120-2026-10-23 \
  --report-dir study/timeout-gitleaks-2026-10-23/native-120 \
  --gitleaks /usr/bin/gitleaks --native-timeout 120 --timeout 150
```

Current source and external adapter may differ from historical environmental behavior. Even a reproduced slow stage does not uniquely explain the old empty-log timeout. Module metadata, ansible-lint, fallback source checks, reporting and their interaction remain candidates. Keep original failure evidence and explicit missingness.

## Longer baseline exposes the stall

The predeclared [120-second native / 150-second worker run](native-120/probe-manifest.json) finishes native scanning in **34.587 seconds**, returning **81,598 findings across 35 files**. JSON loading/path normalization takes a further approximately nine seconds. Noise postprocessing starts at 43.896 seconds and is still running when the 150-second worker limit stops it. Repeated stack dumps locate `Path.read_text` / UTF-8 decoding inside `_source_context`, invoked per finding by `_filter_known_noise`.

The baseline adapter is byte-identical to the archived analyzer's adapter: Git blob `8e9be6af29b87d8003cebeb8bb5497712720266d` in both the frozen analyzer commit `ad1d60023d237b6e1cfa53466e81407e3f329229` and pre-fix repair branch. The external binary/environment still differs or is unverified; an old empty log cannot establish the unique historical cause.

[native-workload.csv](native-120/native-workload.csv) accounts for all findings and source sizes. The old loop would read/decode **3,377,078,730,741 source bytes (3.377 TB)** if all rows completed. This is a projection from finding counts × file sizes, **not measured physical disk I/O**; filesystem caches do not remove repeated decoding/splitting. The largest contributors are 36,981 findings in a 36.4 MB genesis file and 30,328 in a 54.8 MB file. The native report is 63,828,894 bytes, within the existing 64 MiB output cap. Its raw values remain ignored locally. Counts are provider outputs, not validated secret/defect counts.

## Repair and observed validation

`_filter_known_noise` groups work by file, reads and splits each file once, and retains only one cached decoded file within that invocation. Both returned lists are restored to native input order. Cache state does not survive an invocation; later source edits remain visible. Missing/invalid UTF-8 files retain the prior no-context behavior. Suppression conditions and policy version are unchanged; no noisy rule or large file was discarded to improve runtime.

Two new regression tests fail against the baseline repeated reads and pass with the repair. They verify interleaved-file output/suppression order, one source read per file, no stale cache after an edit, and cached missing/invalid-encoding outcomes. **27 focused tests passed** across GitLeaks and both diagnostic probes.

- [Exact before/after subset](native-120/parity-check.json): first and last native finding from every affected file (69 rows after singleton deduplication), selected before the fix. Original and repaired findings, suppression evidence and ordering match exactly. This is a development regression subset, not an accuracy sample or benchmark.
- [All-row conditional policy comparison](native-120/all-row-policy-parity.json): execute the archived filter function on all 81,598 rows grouped by file, substituting cached source context with the original window arithmetic so it can finish. Every file's retained findings and suppression evidence match the repaired filter exactly. This validates policy parity given identical context; it does not rerun the old repeated I/O or establish secret correctness. Interleaved global order is tested separately.
- [Full native-report replay](native-120/repaired-filter-replay.json): all **81,598 rows** finish filtering in 21.564 seconds; **35 source reads / 469,203,180 bytes**, 80,058 retained and 1,540 suppressed. All suppressions use the existing public-key-context reason. [Read ledger](native-120/repaired-file-reads.csv). Timing includes instrumentation and overlapping development activity; no controlled speedup ratio is claimed.
- [Repaired integrated probe](repaired-120/probe-manifest.json): same frozen tree, same binary digest, same native/worker limits. **Completed in 75.874 seconds**: native scan 36.777 seconds, noise postprocessing 29.706 seconds, 80,058 retained / 1,540 suppressed. All output/implementation/dependency hashes verified. Profile overhead and warm filesystem state limit performance comparisons.

The full repository test suite passes: **1,520 passed, 2 skipped in 161.09 seconds**; diff whitespace check passes. The actual whole-repository scan still has other stages and output costs, especially with 80,058 provider rows. Next rerun end-to-end under a new run ID with explicit provider/reporting checkpoints. Do not overwrite the archived timeout, promote the 207th repository into old denominators, or treat any secret candidates as gold labels.
