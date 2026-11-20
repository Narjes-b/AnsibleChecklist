# v0.0.7 full-run share package

This directory contains two ways to share the run:

1. `v007-analysis-and-reports.tar.gz` is a standalone, smaller bundle with the complete aggregate CSV results, tables, chart SVGs and chart data, run/status metadata, logs, and the main Markdown reports. Start with `FULL_RUN_REPORT.md` and `report/FULL_STUDY_REPORT.md` inside it.
2. `v007-full-run.tar.gz.part-*` are consecutive byte-parts of the complete run archive. They are not separate tar archives. Download/provide every part, then concatenate them in lexical order to reconstruct `v007-full-repro-2026-results.tar.gz` before extracting.

Reconstruction and verification (run from this directory):

```sh
cat v007-full-run.tar.gz.part-* > v007-full-repro-2026-results.tar.gz
sha256sum -c v007-full-repro-2026-results.tar.gz.sha256
tar -tzf v007-full-repro-2026-results.tar.gz | head
```

`SHA256SUMS` verifies the delivered archives/parts, the original archive checksum sidecar, and this README (the checksum list does not checksum itself). The complete archive includes per-repository raw outputs and all files in the run package; the standalone analysis bundle includes aggregate occurrence CSVs but omits the very large per-file repository snapshots. The run had 171 complete, 35 partial, and 1 timed-out repository, as documented in the report and status tables.
