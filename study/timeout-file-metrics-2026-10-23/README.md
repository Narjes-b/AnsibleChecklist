# Frozen timeout triage — file metric detectors

Status: current file-metric probe completed; historical timeout remains unexplained. This follows the [context-only probe](../timeout-context-2026-10-23/README.md) and does not replace historical results.

Same repository/SHA and verified 403 copied blobs / 14 oversized JSON omissions. All 148 YAML paths are present; 145 selected. The probe adds `--include-file-detectors` to [profile_frozen_context.py](../../scripts/profile_frozen_context.py), with a new ignored local mirror, 75-second worker deadline, 2 GiB address-space bound, module docs disabled, no providers, no LLM and no execution of target programs.

**Worker total: 10.996 seconds; peak RSS: 118,692 KiB.** All 145 selected files complete the metric stage: 67 structurally analyzed, 78 intentionally skipped by the task/play parser. No caught detector errors. Sum of file-metric stage durations: **4.191 seconds**. The skips do not mean those files are clean: the CLI's fallback source checks, threshold evaluation and report generation are outside this probe.

| Largest detector totals | Seconds |
|---|---:|
| large-playbook | 0.974 |
| partial-checklist-family | 0.688 |
| paper-candidate-family | 0.479 |
| handler-issues | 0.401 |
| missing-checklist-family | 0.277 |

[probe-manifest.json](probe-manifest.json), [stage-events.json](stage-events.json) and [top-functions.csv](top-functions.csv) retain original checkpoints, limits, current code/dependency identities and profile summaries. [file-timings.csv](file-timings.csv) and [detector-totals.csv](detector-totals.csv) are derivatives verified in [verification.json](verification.json). Original output hashes and executing probe hash were checked. Tests: **5 focused probe tests passed**, including separate-process metric-stage coverage; the prior 142-test context/retrieval/index check remains separately recorded.

Reproduce the context-only command with **new output directories** and `--include-file-detectors`. Timings are one profiled development run, not comparable performance estimates against the archived analyzer.

A subsequent exact-tree size read finds **470,774,640 bytes** across the frozen regular blobs. The 14 omitted genesis JSON files account for most bytes; the largest is 87,995,175 bytes. That makes whole-tree provider scanning/postprocessing a candidate worth isolating, but establishes no cause. Next use a complete frozen blob mirror with explicit larger acquisition limits and separately bound provider and postprocessing stages. Keep the repository's original missingness and historical deadline failure unchanged until explained.
