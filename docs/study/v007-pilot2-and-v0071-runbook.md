# Runbook: v0.0.7.1 freeze and pilot 2

2026-10-16. What is ready, what blocks, and the exact order. Read with
[validation plan v2](v007-validation-plan-v2.md).

## Ready (committed on `fix/v007-audit-2026-10-15`)
| Piece | Where |
|---|---|
| Codebook v2.0, frozen, hashes | `study/validation-v007-human/codebooks-v2/` (`FREEZE_RECORD.md`) |
| Form schema v2: builder, validator | `scripts/v007_review_schema_v2.py` |
| Bundle generator v2, bundle validator, secret scanner, redactor | `scripts/v007_bundle_context_v2.py`, `v007_bundle_validate_v2.py`, `v007_bundle_secret_scan.py`, `v007_bundle_redact_v2.py` |
| Pilot-2 selection (exclusions, caps, no pilot-1 reuse) | `scripts/v007_pilot2_selection.py` |
| Agreement and gate report | `scripts/v007_agreement_v2.py` |
| Detector fixes for v0.0.7.1 | CHANGELOG "Unreleased" |
| Allocation for the heldout phase | `study/validation-design-v007/allocation-v2.csv` |

## Resolved: the v0.0.7.1 run (done 2026-10-16, see [run summary](v0071-run-summary.md))
The old unpacked run was deleted with the owner's approval after its archive checksum was verified, the runner was generalised, and the run completed with `--minimum-free-gib 20`. The text below is kept for the record.

## (historical) Blocker
- The runner requires ≥ 40 GiB free (`--minimum-free-gib`); the disk has about 17 GiB free (93 % used).
- `study/runs` holds about 12 GB (frozen run plus the re-execution), `study/repositories` 18 GB (verified clone cache).
- Do not lower the guard on a nearly full disk: a run that fills it fails midway and can corrupt other work.
- Needed: move `study/runs/v007-full-repro-2026*` (with the `.sha256` files) to external storage, verify checksums there, then free space. This deletes nothing by itself and is the owner's action because it touches the only copies of frozen results.

## Code changes needed in the runner (before the run)
- `scripts/v007_full_repro.py` hard-codes `RUN_ID = "v007-full-repro-2026"` and `study/configs/v007-207.yaml` pins `tool.version: 0.0.7`.
  Create `study/configs/v0071-207.yaml` with a new run id (for example `v0071-full-2026`) and version `0.0.7.1`; make the runner read the id from the config.
  Never reuse the old id (the config says so).
- Bump the package version and CHANGELOG heading together; the working tree must be clean (`allow_dirty: false`).

## Order
1. Free disk; archive the v0.0.7 outputs externally.
2. Runner generalisation, config, version bump; full tests.
3. Run (4 workers); gate: sanity, determinism, counts; record checksums.
4. Re-run the split check: calibration/heldout repository sets must be identical (they are frozen by repository list, not by run).
5. Pilot 2 sample: build candidates from calibration repositories of the new run, call `select_pilot2` (25 per family, 175 items), generate bundles with `v007_bundle_context_v2`, run the secret redactor and `v007_bundle_validate_v2` (must exit 0, defect rate ≤ 5 %).
6. Build blank v2 forms with `v007_review_schema_v2.py build`; adapt the packet exporter to them.
7. Two humans label independently; `v007_agreement_v2.py` evaluates the gates. Failing a gate twice drops the family from precision claims.
8. Pre-register, then generate heldout contexts (never before).

## Known limits
- The exporter and pilot validator are still tied to pilot-1 paths; adapt them in step 6.
- Bundles for review/history items were tested on synthetic repositories; run the validator on the real ones in step 5.
