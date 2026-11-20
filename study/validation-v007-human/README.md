# V0.0.7 human validation

This package contains split-safe validation preparation for run `v007-full-repro-2026`. Follow `VALIDATION_STATUS.md` as the resumable state machine. Current phase: `WAITING_FOR_HUMANS` for the independent agreement pilot. No human labels or detector performance estimates exist.

## Frozen inputs

- The supplied execution plans and exact sampling spec are byte-preserved in `protocol/source/`; their hashes and original names are in `protocol/source/INPUT_PROVENANCE.json`.
- The exact 65-row allocation matrix is in `mappings/source-rule-allocation-matrix.csv`. `mappings/rule-family-map.csv` assigns 60 static/static-special and five separate review/history rules to seven families.
- `identities/static-source-candidates.csv.gz` contains 265,434 namespaced static-source identities verified against the frozen commits.
- `splits/repository-split.csv` freezes 144 calibration and 62 heldout repositories. Read the balance audit and manifest before sampling.

## Agreement-pilot artifacts

`samples/agreement-pilot/agreement-pilot-master.csv` is the immutable 350-item master. `reviewers/reviewer-a/agreement-pilot.csv` and `reviewers/reviewer-b/agreement-pilot.csv` are identical blank forms. `reviewers/ai-shadow/agreement-pilot.csv` carries the same evidence/IDs and separate blank AI fields; formal AI labels wait until human gold is frozen. Each row links to a frozen context bundle under `samples/agreement-pilot/context/`. Six static families and the review/history family each have 50 cases. Of 335 calibration history candidates, 299 lack an actual first parent; 196 of those are excluded because their diff-dependent rules require it. The 103 parentless message-only cases remain eligible from their exact target commit messages. The resulting context-eligible history pool is 139 before rare-rule protection and deterministic selection.

Pilot generation is deterministic from the pinned identity, split, and family-map hashes:

```sh
.venv/bin/python scripts/v007_validation_pilot.py --dry-run
.venv/bin/python scripts/v007_validation_pilot.py
.venv/bin/python -m scripts.validate_v007_validation_pilot
```

The writer refuses to overwrite changed artifacts. The validator checks hashes, row identity/order, blank decisions, calibration-only selection, family/rule/repository count reconciliation, context redaction, exact target commits, and rule-appropriate parent/diff evidence. Read `VALIDATION_INTEGRITY_REPORT.md` and `SAMPLING_AUDIT.md` for the latest results.

## Later-stage methods and source readiness

`WEIGHTING_METHOD.md`, `RECALL_PROTOCOL.md`, `THRESHOLD_VALIDATION_PROTOCOL.md`, and `AI_SHADOW_PROTOCOL.md` define the downstream estimands and safeguards without creating downstream human labels. `threshold-human-condition-map.csv` maps 24 threshold metrics to 13 deduplicated human conditions. `THRESHOLD_SOURCE_AUDIT.md` verifies its retained full observation source against the frozen split and exact run commits. This preflight does not create calibration/heldout samples; exact execution order still requires agreement-pilot closeout and codebook freeze first.

`LEGACY_THRESHOLD_ARCHIVE_NOTICE.md` explains why historical full-corpus threshold reviewer labels are preserved but excluded from the current split-safe human gold.

When both reviewers return their completed files, keep the frozen blank templates unchanged and run the reviewer validator/agreement analysis on the separate returned copies:

```sh
.venv/bin/python -m scripts.v007_human_agreement \
  --reviewer-a /path/to/returned-reviewer-a.csv \
  --reviewer-b /path/to/returned-reviewer-b.csv
```

It refuses incomplete or altered sheets, computes raw agreement, Cohen's kappa, Gwet's AC1, prevalence, category-specific agreement, confusion matrices, and writes a disagreement sheet plus report without editing either reviewer file. Adjudication remains a separate human step.

## Reviewer handoff

Both reviewers should use their own file, `HUMAN_REVIEWER_A_INSTRUCTIONS.md` or `HUMAN_REVIEWER_B_INSTRUCTIONS.md`, the shared `codebooks/REVIEWER_INSTRUCTIONS.md`, the row’s family codebook, and `HUMAN_REVIEW_CHECKLIST.md`. They must return independent completed copies and leave the blank frozen templates unchanged.

To create separate, blinded handoff ZIPs, run:

```sh
.venv/bin/python -m scripts.export_v007_reviewer_packets \
  --output-dir ~/Downloads/V007_CHAT_HANDOFF_2026-10-06/reviewer_packets
```

The resulting `reviewer-a/` and `reviewer-b/` folders each contain one content-addressed ZIP and a SHA-256 sidecar. A packet includes only its assigned blank CSV, that reviewer's instructions, the shared/family codebooks, rule overrides, and exactly the referenced context bundles. It excludes the other reviewer form, AI-shadow form, pilot master, selection audit, and sampling manifest. Give each ZIP only to its named reviewer; keep the blank repository templates unchanged. The exporter verifies the pilot manifest and frozen codebook/context hashes before writing.

Do not sample primary calibration performance, source-first recall, thresholds, AI-shadow labels, or heldout occurrences until the pilot is closed, agreement is analyzed, any codebook revisions are documented, and final codebooks are frozen. Review/history is always a separate panel from static-source precision.
