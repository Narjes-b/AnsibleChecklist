# Frozen timeout triage — complete source-only CLI

Status: source-only pipeline and report generation complete. This is a diagnostic on current code, not the historical full-profile run or a performance/accuracy evaluation.

After the [GitLeaks repair](../timeout-gitleaks-2026-10-23/README.md), run the complete `snapshot-source` CLI against the already verified full blob mirror for `encapsulate-xyz/cosmos-ansible` at `a49d30281d2d3c763ef0d50a7aaddc751a460863`. Module docs are disabled; external providers and history review are excluded by this profile. The worker has a 150-second process-group deadline and fails on analysis errors. No target programs or LLMs execute.

**Completed in 8.089 seconds, exit 0.** All 145 selected YAML files are parsed and processed, including the fallback source checks omitted from earlier metric-only probes. There are 67 structural task/play files and 78 parser-skipped source documents; the full CLI processes those remaining documents with the appropriate source checks. Zero diagnostic faults, parse failures, partial files or failed files. Report artifacts are generated: JSON, CSV, SARIF, canonical occurrences and summary.

| Report quantity | Value |
|---|---:|
| Raw internal findings | 1,128 |
| Canonical occurrences | 1,127 |
| Static resolved includes | 39 |
| Static missing includes | 49 |
| Static role references | 31 |
| Dynamic includes | 6 |

These are unvalidated tool outputs. Operational completion does not certify the rule predicates or dependency completeness: 49 static-missing and six dynamic include outcomes remain explicit evidence limitations, and do not by themselves establish defects. No source-only result is added to the old full-profile denominators.

[probe-manifest.json](probe-manifest.json) records the exact executable/arguments, current Git commit, source inventory identity, selected profile, aggregate health/timings/counts, ignored output/log hashes and limits. After the CLI completed, all **417 blobs / 470,774,640 bytes** were checked against their original copied SHA-256 values: source bytes remain unchanged. Fresh Git metadata and removed executable modes remain declared differences from original execution. The CLI metadata reports local-source provenance; the frozen SHA relationship is established by this external verified inventory, not invented as an original checkout.

An initial launcher attempt incorrectly inserted a `scan` subcommand. This installed entrypoint expects the target directly and rejected the arguments before analysis (exit 2). [initial-launch.json](initial-launch.json) retains the failed invocation/log hashes with an explicit launcher-error classification; it is not a detector or source failure. The corrected run uses a new output directory.

To reproduce with the existing immutable mirror and a new output path:

```sh
ANSIBLEGUARD_DISABLE_ANSIBLE_DOC=1 PYTHONUNBUFFERED=1 \
  .venv/bin/ansibleguard \
  study/evidence-local/timeout-gitleaks-repaired-2026-10-23/source \
  --profile snapshot-source \
  --file-manifest study/evidence-local/timeout-context-2026-10-23/worker/classification.csv \
  --fail-on analysis-error -o study/evidence-local/timeout-source-cli-NEW/scan
```

The recorded run is additionally parent-bounded at 150 seconds, killing its process group on timeout. Timings are a single development run with warm filesystem state and differ from earlier cProfile instrumentation; no controlled speedup comparison is claimed. The preceding production repair passed the full suite: **1,520 passed, 2 skipped**. This step changes only diagnostic artifacts/documentation.

Next isolate module metadata and ansible-lint, then test the combined full-profile/reporting path with all provider rows under a new run ID. Keep historical results and original timeout intact. Semantic evidence packets, fresh sampling-frame freeze and human agreement remain separate gates.
