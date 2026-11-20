# v0.0.7 Variable Resolution Primary Review

## Scope and status

This review covers 847 primary units: the complete 247-occurrence suppression census, 450 emitted occurrences (150 per resolution class), and 150 source-first files. Selection is deterministic, repository-capped, and frozen by SHA-256 hashes.

The labels are a single-agent, code-assisted source review. They are not independent human gold-standard labels and cannot establish inter-rater agreement.

## Results

| Measure | Result | Naive Wilson 95% interval |
|---|---:|---:|
| Suppression safety (required-argument census) | 247/247 (100.0%) | 98.5%–100.0% |
| CANDIDATE_MISSING precision among decided labels | 84/84 (100.0%) | 95.6%–100.0% |
| CANDIDATE_MISSING conservative TP yield | 84/150 (56.0%) | 48.0%–63.7% |
| Resolution-class accuracy among decided labels | 366/366 (100.0%) | 99.0%–100.0% |
| Resolution-class decision coverage | 366/450 (81.3%) | 77.5%–84.7% |
| Source-first supported recall, occurrence level | 10/11 (90.9%) | 62.3%–98.4% |
| Source-first supported recall, repository level | 1/2 (50.0%) | 9.5%–90.5% |

## Label distribution

- All 247 suppressed occurrences were verified safe through applicable required role argument contracts.
- `CANDIDATE_MISSING`: 84 TP and 66 uncertain; no reviewed false positives.
- `EXTERNAL_INPUT_UNCERTAIN`: 150 uncertainty labels with 150 correct class decisions.
- `RUNTIME_CONTEXT_UNCERTAIN`: 150 uncertainty labels; 132 correct class decisions and 18 unclear.
- Source-first blocks: 133 TN, 3 containing supported issues, and 14 unresolved-context blocks.

## Missed supported issue

- `NationalGenomicsInfrastructure/miarka-provision:roles/tarzan/defaults/main.yml:8` uses `tarzan_proj_dir` without a visible definition. The surrounding defaults file defines `tarzan_root_dir`, making this a likely variable-name typo and a detector false negative.

## Interpretation limits

The Wilson intervals treat occurrences as independent and therefore understate uncertainty when findings cluster by repository. Repository-level recall is reported alongside occurrence-level recall. The inspected corpus has already influenced development, so this is calibration evidence rather than a final unseen held-out evaluation. Formal agreement still requires a second independent reviewer.
