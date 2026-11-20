# False-positive precheck of the v0.0.7 run (2026-10-15)

**This is an AI precheck, not human gold.** It was made to find
false-positive *mechanisms* to fix, not to estimate precision. It must not be
merged with Reviewer A/B labels or used in agreement or performance
statistics.

## Sample

- Source: `aggregate/all-internal-source-occurrences.csv` of the frozen run
  `v007-full-repro-2026` (identical to its reproduction).
- Population: **calibration-split repositories only** (heldout repositories
  were not opened), optional style-policy findings excluded, and items already
  in the 350-row agreement pilot excluded.
- Design: 2 findings per rule (52 rules, 101 items), seeded
  (`v007-audit-2026-10-15-fp-precheck`), drawn by
  `scripts/v007_fp_precheck_sample.py`.
- Evidence: the source window at the frozen commit (regenerate with the
  sampler; not committed because excerpts are unredacted), plus
  repository-wide `git grep` where the rule depends on other files.

## Result

| Label | Items |
|---|---:|
| TP | 54 |
| FP | 19 |
| uncertain | 28 |

54 / 73 decidable = 74.0 %. This is unweighted across rules and is **not** a
population estimate.

## What it found

| Mechanism | Items | Status |
|---|---|---|
| Handlers imported via `import_tasks` / notifies from included files invisible (`missing-handler` is an error) | 051, 052, 096 | fixed |
| `-o`/`--output` of kubectl treated as a file write | 055 | fixed |
| Marker joined to an identifier (`containerd-hack`) | 023 | fixed |
| Galaxy role `ns.name` treated as local role `name` | 003 | fixed |
| `threshold=None` and "curl" in messages | 020, 021, 063, 064 | fixed |
| Module-level `no_log` arguments not recognized | 008, 009 | open |
| File-scoped reasoning for variables / registered results | 098, 100, 101 | open |
| Non-Ansible YAML analyzed (`Taskfile.yml`) | 080 | open |
| Data fields mistaken for module arguments (`port: 0` in `set_fact`) | 030, 031 | open |
| Path vs secret (`deploy_private_key: ~/.ssh/id_rsa`), local role pinning, `/sys` writes, controller env reads | 061, 088, 091, 093 | open |
| File-level "count=N" findings without the offending task — not reviewable | most "uncertain" | open |

`labels.csv` holds every item with its label and reason.
