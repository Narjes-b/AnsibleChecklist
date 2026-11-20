# V0.0.7 chat handoff archive guide

Prepared 2026-10-06 from the frozen run `v007-full-repro-2026` and the current V0.0.7 human-validation preparation branch. This guide is included in Part 1; the seven ZIPs and SHA-256 sidecars are in `~/Downloads/V007_CHAT_HANDOFF_2026-10-06/`.

## Archive parts

The matching ZIP files are in the handoff folder under `~/Downloads/V007_CHAT_HANDOFF_2026-10-06/`. Each ZIP can be opened independently and preserves repository-relative paths.

1. `PART1_REPORTS_AND_PROBLEMS` — investigation, full-run reports, partial/failure diagnosis, reproducibility notes, validation status/phase ledger, threshold-source preflight, exact plan/spec, codebooks, and downstream method protocols.
2. `PART2_SUMMARY_TABLES_CHARTS` — compact aggregate summaries, all run tables, chart data/SVGs, report data, frozen input list, and environment metadata.
3. `PART3_OCCURRENCE_EXPORTS_INTERNAL` — full internal/static-source/review/uncertainty occurrence exports.
4. `PART4_OCCURRENCE_EXPORTS_CROSS_PROVIDER` — canonical and raw findings plus ansible-lint, GitLeaks, and provider-comparable occurrence exports.
5. `PART5_HUMAN_VALIDATION_MATERIALS` — split/identity inputs, mappings, codebooks, generated blank 350-row A/B and AI-shadow templates with contexts, selection audit, integrity/sampling reports, threshold human-condition map/source audit, weighting/recall/threshold/AI protocols, pilot generator/validator, blinded reviewer-packet exporter, reviewer agreement-analysis tool, and tests.
6. `PART6_THRESHOLD_SOURCE_POPULATION` — the 2,986,459-row threshold observation population, its benchmark manifest and source summaries. It includes metric measurements across the frozen corpus, including heldout repositories; it is for machine/source auditing, not reviewer distribution.
7. `PART7_THRESHOLD_LEGACY_REVIEW_ARTIFACTS` — preserved pre-split threshold samples, historical review/AI/adjudication files, per-metric results, codebooks, contexts, and manifests. These are legacy full-corpus benchmark artifacts, not valid human gold for the current split-safe validation.

Every archive has a `.sha256` sidecar. Check an archive with `sha256sum -c <archive>.sha256`; test its ZIP structure with `unzip -t <archive>`.

## What the results say

- The frozen population has 207 repositories: 171 complete, 35 partial, and one timeout. AnsibleGuard analysis completed on 206 repositories. The 35 partials are missing optional ansible-lint evidence; they are not zero-finding results. The timeout is `encapsulate-xyz/cosmos-ansible`.
- The 35 ansible-lint partials have separately classified causes in `FULL_RUN_PARTIALS.md`; the evidence does not justify treating every syntax-check failure as an invalid repository.
- The run reports 390,286 raw findings and 376,115 canonical occurrences. Canonicalization is not human correctness validation and these counts are not precision estimates.
- Current split-safe human validation is still calibration preparation. The repository split is 144 calibration / 62 heldout; no labels for this validation, primary human sample, or detector performance estimate have been produced. The agreement pilot has 50 cases in each of six static families plus 50 review/history cases. Across 335 history candidates, 299 lack an actual first parent; 196 are excluded because their rules require a diff, while 103 message-only cases remain eligible from the exact target message. No heldout human-review context was opened.
- An identical 350-row AI-shadow template is included with AI-only blank fields. Formal AI labels are deferred until the human pilot labels and adjudication are frozen.
- Part 7 contains earlier threshold-benchmark reviewer/AI labels from a full-corpus design. Preserve them as historical evidence only; never copy them into the new Reviewer A/B, calibration, or heldout files. Part 6 includes threshold measurements from all repositories but does not contain human labels.

## Scope and exclusions

The archive parts contain aggregate result exports, summary/presentation data, the threshold population source, legacy threshold artifacts, and key Markdown that explains the run and its problems. They deliberately omit the 9.1-GB frozen repository checkout snapshots, per-repository raw scan payloads, and full runner logs. Those are not needed to interpret the aggregate results and can include source material or sensitive scanner output. The complete local run remains at `study/runs/v007-full-repro-2026/`.

Upload Part 1 first for context. Add Parts 2–4 for aggregate tables/charts and occurrence exports, Part 5 for current validation preparation, and Parts 6–7 only when threshold source data or the legacy threshold benchmark is relevant. Do not send Parts 5–7 to pilot reviewers; give them only their separate reviewer-specific ZIP.

## Independent reviewer handoffs

Separate content-addressed reviewer ZIPs are stored beside these archives in `reviewer_packets/reviewer-a/` and `reviewer_packets/reviewer-b/`. Send each ZIP only to its named reviewer. A packet contains that person's blank form, instructions, codebooks, rule overrides, and referenced contexts; it omits the other reviewer's CSV, the AI-shadow file, the pilot master, and the sampling manifest. These reviewer packets are distinct from the seven chat archives.
