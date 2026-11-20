# V0.0.7 human-validation status

Status date: 2026-10-06
Phase: `WAITING_FOR_HUMANS` — independent agreement-pilot labels

## Resumable state machine

Current state: **`WAITING_FOR_HUMANS`**. This is not overall validation completion. The dedicated branch is `study/v007-human-validation`; it was created from starting branch head `cb304a52bb8fcc4db12f58aa8c44f53e4411ef18`. The source state used for this ledger was commit `3439a62f76d0f543167e0f49b8d85034e9896eda`, which was pushed to both `myfork` and `origin` before this status-ledger update.

The phase ledger below records the last verified input/output hashes. Hashes identify the exact artifact; manifests contain the full per-file checksum inventories.

| Phase | State | Inputs and hashes | Outputs and hashes | Next action | Blocking dependency |
|---|---|---|---|---|---|
| Pre-validation source gate | PASS | Run `v007-full-repro-2026`; authoritative static source SHA-256 `7ea8943bf40a6b05f2e33c4140446757c45b6d218e81a75096591f046a81978b` | `PRE_VALIDATION_GATE.md`: `92a69fbeb8b34eeeff7ef7e2fdf04cc58a77dacce4d068a423c7b19fc4874933` | None; source gate is frozen | None |
| Identity, split, and rule mapping | PASS | Exact allocation matrix: `657759e3d5cf76e79ce3dacc9afcd7f2b0986fa5d86a43a8c7787d1ee1596c2f`; source identity index: `2b70672c1f89039386f6cfb4bb73460059f05014a6b7248e4865f951150c7d6b` | Split CSV: `c6f50da3bd52130cd0a32ab48e322dfa666419d12bccdb1e7a4796d885260f65`; family map: `914215d3c2ca0c9443ddd424ad0b8a8d9d9f317f2abc1fa27bb6ba7f842d4317`; split/family manifests record the complete audits | None; 144 calibration / 62 heldout are frozen | None |
| Agreement-pilot package | PASS | Plan: `0ad90df2988431f9d8d476bf806cae41c083537bba47abc8bd19b8191bfeb838`; exact sampling spec: `9c4a9004ea5e97652fc240904c9035665ffbcd59967eedce08e1bb6d9c094aa8`; pilot seed `v007-human-pilot-v1` | Pilot manifest: `f88cb28bf4f97cb6703ce09263b861c920317b22f94654e5c9d487092845a6c6`; master: `0a96f7cef4471bc51e5b627b88349f90c98a09a350a0a92915f50f24fd87efb8`; integrity report: `fa2adba7ef2341afc42ca3c777f4c1d7bebc70f9f9f2cf45184f049f9ae4eaa5` | None; integrity audit PASS, 33 checks | None |
| Threshold source and condition-map preflight | PASS | Full observations SHA-256 `3f4b35e1e0fbe7751ac394b1ce9113329f2548a8a071a50f166ee99f3765edb8`; exact 24-metric condition map SHA-256 `5b36248c9473df844961970d8008a1ecaa3e8cbe184988047dc358ba462f1fde` | `THRESHOLD_SOURCE_AUDIT.md`: `b0f036a8c00d86615a4bb686d5bcf33f6f4d69131ecbdd6966d9ea31cd123283`; JSON audit verifies 2,986,459 rows, 207 projects, 13 condition families, zero commit mismatches; timeout excluded | None; source population is available for later split-safe batch generation | Calibration/heldout threshold batches remain gated by pilot closeout/final freeze |
| Reviewer A independent labels | `WAITING_FOR_HUMANS` | Frozen blank A template SHA-256 `f4c0cedf5fb5f98e0e0621a3bc1f812ed483e9cc18c3d6ecdf4ea6a8a86ac9ff`; A packet SHA-256 `45164008e76ef75e4730f1159cd8e957bdb33182acea4b0303a0ab026cc9b06d` | Returned A CSV and its SHA-256: pending; do not replace the blank template | Reviewer A independently fills only the eight decision columns and returns a separate copy | External Reviewer A decisions |
| Reviewer B independent labels | `WAITING_FOR_HUMANS` | Frozen blank B template SHA-256 `f4c0cedf5fb5f98e0e0621a3bc1f812ed483e9cc18c3d6ecdf4ea6a8a86ac9ff`; B packet SHA-256 `3d73b50db9f7351176340f32385acb15ee7143881e0c9110aab43ca0af37fc66` | Returned B CSV and its SHA-256: pending; do not replace the blank template | Reviewer B independently fills only the eight decision columns and returns a separate copy | External Reviewer B decisions |
| Agreement analysis and pilot closeout | `NOT_STARTED` | Two separate returned CSVs, each checked against the frozen master and pilot manifest | `results/agreement-summary.json`, `.csv`, `adjudication/disagreements.csv`, and `HUMAN_AGREEMENT_REPORT.md`: not generated | Run `scripts.v007_human_agreement`; inspect disagreements using only this pilot round | Both reviewer files; human adjudication/codebook decisions if needed |
| Final codebook freeze and primary calibration preparation | `NOT_STARTED` | Closed pilot, agreement results, documented pilot-only codebook decisions | Final codebook checksums, calibration precision/top-up/review-history/recall/threshold samples: not generated | Freeze codebooks, then execute exact sampling spec sections 7–23 and audit every panel | Agreement pilot closeout; do not generate primary items early |
| Calibration scoring and final freeze | `NOT_STARTED` | Independently completed calibration labels and human adjudication | Calibration estimands, uncertainty intervals, calibration decisions, `FINAL_VALIDATION_FREEZE.md`: not generated | Score only after primary calibration reviews return; freeze detector/threshold/mappings/codebooks | Calibration human review and adjudication |
| Heldout evaluation and final report | `NOT_STARTED` | Final freeze and untouched 62-repository heldout split | Heldout human labels, final report/checksums: not generated | Generate heldout samples only after final freeze; both humans review and adjudicate | Final freeze, then separate human heldout review/adjudication |

### Sequencing note

The execution plan has a conflict: §32 says to generate primary precision/recall/threshold samples before asking humans to do anything, while §7 and the exact execution order in §30 require the agreement pilot to be labeled and closed, codebooks frozen, and only then primary samples generated. This run follows the more specific pilot-first sequence in §§7 and 30 and the exact sampling spec's stop conditions. No primary performance rows or heldout contexts have been generated/opened. The ambiguity is recorded rather than silently resolved by crossing the pilot/codebook gate.

## Current state

The pre-validation gate is **PASS for calibration-only preparation**. The frozen split contains 144 calibration and 62 heldout repositories out of the 206 analyzable repositories. Heldout occurrence data has not been sampled or opened for contexts.

The rule-family map covers all 65 allocated rules: 60 static/static-special rules and five separate review/history rules. Seven initial family codebooks, rule overrides, the exact source plans, and independent reviewer instructions are present. These codebooks remain **draft-for-pilot**; there is no final codebook freeze.

The agreement pilot is generated and frozen:

- 350 unique items total: 50 in each of the six static-source families and 50 review/history items.
- Of 335 calibration review/history candidate findings, 299 lack an actual first parent in the existing shallow snapshots. A parent is required for three diff-dependent rules: 196 findings are excluded because that required parent is missing. The other 103 parentless cases are message-only (`commit-message-format` / `missing-bug-reference`) and remain eligible using the exact target commit message. This gives 139 context-eligible history cases; rare-rule protection applies before the 50-item selection.
- Reviewer A and B each have 350 rows with identical bytes and blank decision columns.
- There are 350 frozen context bundles. The master marks every row `is_agreement_pilot=true` and `eligible_for_performance_scoring=false`.
- The pilot manifest records source/script commit and hash, source hashes, family/rule/repository selected and excluded counts, context-availability exclusions, and per-output checksums. `VALIDATION_INTEGRITY_REPORT.md` and `validation-integrity.json` record the pilot package audit.
- Reviewer-specific content-addressed ZIPs were generated; A and B packets exclude the other reviewer CSV, master, selection audit, and sampling manifest. Their packet hashes are recorded in the phase ledger above.
- A threshold-source preflight confirms the retained full observation population joins exactly to all frozen run commits and covers every split repository. The condition map and downstream weighting/recall/threshold/AI protocols are prepared, but no primary threshold or other performance sample has been emitted.

The initial context audit found that prefixed credential keys could evade redaction. This was corrected before any form was shared: prefixed keys, JSON keys, multiline sensitive blocks, and private-key content are now redacted; regression tests pass; the frozen context bundles pass the redaction-idempotence check. A protocol audit also corrected an over-restrictive parent requirement: exact first parents are mandatory only for diff-dependent history rules, not commit-message-only rules. No previous pilot files were labeled or distributed.

## Source population and run caveats

- Authoritative static source: `study/runs/v007-full-repro-2026/aggregate/all-internal-source-occurrences.csv`; SHA-256 `7ea8943bf40a6b05f2e33c4140446757c45b6d218e81a75096591f046a81978b`.
- There are 265,434 static-source occurrences across 60 observed rules. Namespaced validation IDs address raw occurrence-ID collisions.
- All source paths/anchors were audited against frozen Git blobs. The timed-out repository is not converted to a zero-finding result.
- The 35 partial run results have completed AnsibleGuard and GitLeaks; only optional ansible-lint is partial. Their causes are detailed in `FULL_RUN_PARTIALS.md`.
- External-tool overlap remains unestimated because rule equivalence is unvalidated. Exact GitLeaks version metadata is unavailable.

## Completed versus not yet permitted

Completed: authoritative-source gate, identity and context audit, 144/62 split, mapping, pilot codebooks, blank pilot forms, contexts, manifest, and pilot-stage integrity report.

Not generated: calibration representative core, rule/concept/security top-ups, static performance panel, source-first recall panels, threshold calibration batches, final freeze, or any heldout sample/results. Do not generate primary performance samples until both pilot files return, agreement is analyzed, any pilot-only codebook revisions are made, and final codebooks are frozen.

## Human action required

Reviewer A and Reviewer B must independently fill their own copy of `reviewers/reviewer-a/agreement-pilot.csv` or `reviewers/reviewer-b/agreement-pilot.csv`, using `HUMAN_REVIEWER_A_INSTRUCTIONS.md` / `HUMAN_REVIEWER_B_INSTRUCTIONS.md`, the shared codebook instructions, the family codebook, and each row’s context bundle. Edit only the eight decision columns. Preserve every ID, evidence field, and row order; do not add AI answers or view the other reviewer’s decisions. Return completed copies separately and retain the blank templates.

Content-addressed, reviewer-specific ZIP handoffs are available under `/home/aymmzn/Downloads/V007_CHAT_HANDOFF_2026-10-06/reviewer_packets/reviewer-a/` and `.../reviewer-b/`. Send Reviewer A only the ZIP in the A folder and Reviewer B only the ZIP in the B folder. Each packet omits the other reviewer form, the master, and the sampling manifest. Their `.sha256` sidecars allow transfer verification. The repository templates remain the frozen originals.

After both separate copies return, keep the blank templates unchanged and run:

```sh
.venv/bin/python -m scripts.v007_human_agreement \
  --reviewer-a /path/to/returned-reviewer-a.csv \
  --reviewer-b /path/to/returned-reviewer-b.csv
```

The tool validates immutable columns/order and decisions, then writes raw agreement, Cohen’s kappa, Gwet’s AC1, positive/negative/uncertain/unreviewable-specific agreement, prevalence, confusion matrices, a disagreement sheet, and a report. Inspect disagreements using only this pilot round. If codebooks change, record a versioned decision and draw a new pilot with new occurrence IDs. Only after pilot closeout may primary calibration sampling begin. The tool has only synthetic unit-test coverage until real reviewer files are returned; no agreement result currently exists.
