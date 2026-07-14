# AnsibleChecklist — Architecture & Test Guide

Companion to `PROJECT_STATUS.md` (bug log), `TESTING.md` (pytest inventory),
`CLI_STATUS.md` (CLI development log), and `OUTPUT_FORMATS.md` (what each of
the three project-wide output layers is for). This file answers: what calls
what, what still needs eyes on it, and how to verify the whole project end
to end. For the forward-looking packaging/refactoring plan, see
`REFACTOR_PLAN.md`.

## Entry point and call graph — UPDATED, package refactor complete

The project is now installed as `ansibleguard` (`src/ansibleguard/`, see
`REFACTOR_PLAN.md` for the full move log). Every flat-file module named
below has moved into the package; the box on the left of each line is the
**old** flat name for continuity with earlier debugging history, the arrow
shows where it lives now.

```
ansibleguard.cli   (run via the installed `ansibleguard` command — arbitrary
                    target path/directory, real project use; this is now the
                    documented entry point, superseding the old batch script)
  │
  ├── config.py               → ansibleguard/config.py            # all paths
  │
  ├── collect_yaml_files()    # recursive discovery, excludes molecule/.git/.venv/etc.
  ├── output_dir_for()        # collision-safe output path per file (mirrors relative structure)
  ├── analyze_path()
  │     ├── smells.execute_for_single_file()   [ansibleguard/smells.py, was smellsDetector.py]
  │     │     — same pipeline as before, per file:
  │     │     │
  │     │     ├── parser.py            → ansibleguard/parser.py [was parser_playbook.py]
  │     │     │     │  # orchestrates ONE playbook's full analysis
  │     │     │     ├── detectors/large_playbook.py    [was detect_large_playbook.py]
  │     │     │     │     ├── detectors/large_task.py  (calculate_metrics_task)
  │     │     │     │     └── detectors/large_play.py  (calculate_metrics_play)
  │     │     │     ├── detectors/large_play.py         (calculate_metrics_play)
  │     │     │     ├── detectors/large_task.py         (calculate_metrics_task)
  │     │     │     ├── detectors/high_coupling.py
  │     │     │     ├── detectors/duplicate_code.py
  │     │     │     ├── detectors/set_fact.py
  │     │     │     ├── detectors/overriding_facts.py
  │     │     │     ├── detectors/unnecessary_abstraction.py  [was unecessary_abs.py]
  │     │     │     ├── detectors/unnamed_play.py
  │     │     │     ├── detectors/is_unnamed.py               [was is_unamed.py — typo fixed]
  │     │     │     ├── detectors/unnamed_tasks.py             (→ .large_task)
  │     │     │     ├── detectors/overridden_keys.py           [was overriden_keys.py — typo fixed]
  │     │     │     │     (→ ansibleguard.report.text_writer.write_duplicates_to_txt)
  │     │     │     ├── detectors/semantic_cohesion.py         [was sem_cohesion.py]
  │     │     │     ├── detectors/incohesive_plays.py
  │     │     │     │     └── detectors/large_play.py
  │     │     │     ├── detectors/duplicate_task_names.py      [was duplicate_task_Name.py]
  │     │     │     │     (→ .large_task)
  │     │     │     ├── detectors/file_extensions.py           [was files_extensions.py]
  │     │     │     ├── detectors/bool_filters.py              [was filters_for_comparison.py]
  │     │     │     ├── detectors/credentials_in_log.py        [was credentials_leaking_in_log.py]
  │     │     │     ├── detectors/include_vars.py
  │     │     │           (→ ansibleguard.report.text_writer.write_unused_vars_to_txt)
  │     │     │     └── detectors/paper_candidates.py
  │     │     │           (9 source/task/role checks sharing one safe traversal engine)
  │     │     │
  │     │     ├── smells.assess_code_smells()  [inside smells.py itself]
  │     │     │     — takes parser's raw metrics + thresholds.csv,
  │     │     │       decides which smells actually fire (large_play, complex_playbook, etc.)
  │     │     │     ├── external/gitleaks.py       [was GitLeaks_hardcoded_credentials.py]
  │     │     │     │     (→ external/install_gitleaks.py for the binary)
  │     │     │     └── external/ansible_lint.py   [was Ansible_Lint.py]
  │     │     │
  │     │     └── report/csv_writer.py / report/text_writer.py
  │     │           [was write_to_csv.py / write_to_text.py] — final per-file report output
  │     │
  │     ├── report/findings.py.build_findings_list()  — flattens one file's (metrics, result,
  │     │     gitleaks findings, lint results) into {file, line, rule_id, severity, message}
  │     └── _write_rollups() — accumulates every file's findings + a per-file
  │           summary row, writes THREE project-wide files once at the end:
  │           summary.csv, findings.json, findings.sarif (via report/sarif_writer.py)
  │
  └── report/sarif_writer.py     # findings.py's flat list → real SARIF 2.1.0 document,
                                  # validated against the actual OASIS schema
```

See `OUTPUT_FORMATS.md` for what each of the three project-wide output layers
(per-file reports, `summary.csv`, `findings.json`/`findings.sarif`) is
actually for and when to use which.

The algorithms, thresholds, role-anchor deduplication, and limitations of the
nine paper-derived checks are specified in `PAPER_SMELLS_IMPLEMENTATION.md`.

Every arrow between sibling modules inside the same subpackage
(`detectors/`, `external/`, `report/`) is now a real relative import
(`from .large_task import ...`); every arrow crossing from `detectors/` or
`external/` or `report/` up to `config.py` is `from ..config import ...`.
Nothing in the live pipeline resolves via bare, `cd`-dependent imports
anymore — confirmed by grepping the whole package for any import not
prefixed with `.` or `ansibleguard`, which now returns nothing.

**Not in the call graph at all** (nothing imports them — these stayed
behind in the old flat `AnsibleGuard/` folder and were never moved into
`src/ansibleguard/`; their fate is still Known Issue #4 in
`PROJECT_STATUS.md` — delete vs. keep):
- `parser_playbook_mod.py` — an older/alternate version of `parser.py`'s
  predecessor with its own CSV-writing logic. Diverged fork, not used.
- `parser_playbook.ipynb` — notebook version, same idea, not used by any script.
- `GeneralsmellsDetector.py` — stale fork of `smells.py`'s predecessor (see
  `PROJECT_STATUS.md` Known Issue #4).
- `exceptions.py` — empty, unused.

If you're editing detection logic, **`ansibleguard/parser.py` +
`ansibleguard/detectors/large_*.py` + `ansibleguard/smells.py` is the real,
live pipeline.** The `_mod`/`.ipynb`/`General*` files are not — changes
there won't affect `ansibleguard`'s output, and they aren't part of the
installed package at all.

## Data flow in one sentence per stage
1. `detectors/large_task.py` / `detectors/large_play.py` /
   `detectors/large_playbook.py` (was `detect_large_task.py` /
   `detect_large_play.py` / `detect_large_playbook.py`) read the YAML and
   produce **raw counts** (LOC, task counts, names) — no threshold logic
   here, just measurement.
2. `parser.py`'s `mainn()` (was `parser_playbook.py`) calls all the
   raw-metric functions above plus every other detector
   (`detectors/set_fact.py`, `detectors/overriding_facts.py`, etc.) and
   assembles one big `main_metrics` dict per playbook — still no
   pass/fail decisions.
3. `smells.py`'s `assess_code_smells()` (was `smellsDetector.py`) takes that
   dict, loads `thresholds.csv`, and decides which smells actually fire
   (that's where `is_large_play`, `complex_playbook`, etc. get computed).
4. `report/csv_writer.py` / `report/text_writer.py` (was `write_to_csv.py` /
   `write_to_text.py`) render the final decision dict to disk.

This matters for debugging: if a number looks wrong, check
`Technical_Analysis.json` first (that's stage 2's raw output, before any
threshold logic) — if the raw number is already wrong, the bug is in a
`detectors/large_*.py` file. If the raw number is right but the CSV's smell
flag is wrong, the bug is in `smells.py`'s threshold logic instead. This is
exactly how we found the original `detect_large_task.py` play-numbering bug,
before it was renamed/moved.

## Files touched and fix status

> **Note:** this table is a historical bug log from the debugging pass and
> intentionally uses the **old, pre-refactor flat filenames**
> (`detect_large_task.py`, `write_to_csv.py`, etc.) since that's what the
> bugs were found and fixed against at the time. See the call graph above
> for the current `src/ansibleguard/...` location of every file listed here.

| File | Status |
|---|---|
| `config.py` | ✅ fixed — portable paths |
| `detect_large_task.py` | ✅ fixed, **then rewritten this round** — guard, play-boundary bug, `UnboundLocalError` on non-list YAML (vault files); now uses `ruamel.yaml` round-trip loading (matching `overriden_keys.py`'s existing pattern) to give every task a real `"line"` field. Caught a real silent-corruption risk before shipping it: naively `yaml.dump()`-ing a `ruamel`-loaded task doesn't error, it silently serializes ruamel's *internal implementation details* instead of the actual content — confirmed directly, would have corrupted every `LOC_task` count. Fixed with a `_to_plain()` conversion back to plain dict/list before the existing PyYAML dump path, confirmed `LOC_task` is byte-identical to pre-rewrite output on content with comments/flow-style. |
| `detect_large_play.py` | ✅ fixed, **then rewritten this round** — guard only; block/rescue/always recursion now matches `detect_large_task.py`'s task semantics. Same `ruamel` line-tracking rewrite as above for a real per-play `"line"` field. **Caught a second, subtler drift risk**: using `ruamel`'s *own* dumper (which preserves original comments/blank-lines/flow-style formatting) instead of PyYAML's canonical re-serialization produces a genuinely *different* `LOC_play` line count once comments or flow-style lists are involved (confirmed: 12 vs 11 lines on one realistic test case) — exactly the kind of silent shift that would move "Large Play" threshold decisions without anyone noticing. Fixed the same way: `_to_plain()` + the original PyYAML dump path, confirmed byte-identical. |
| `detect_large_playbook.py` | ✅ fixed — guard + try/except widened |
| `duplicate_task_Name.py` | ✅ fixed — guard + tuple-unpack bug |
| `credentials_leaking_in_log.py` | ✅ fixed — guard only; **fixed again for a much more severe scope bug** — it originally only scanned tasks with no play wrapper at all (`top_level_tasks`), missing virtually every real-world credential-leak case (any task inside a normal `hosts:`/`tasks:` play); **fixed a third time this round**: (1) had no top-level parse guard at all — a `!vault`-tagged file raised an uncaught `ConstructorError`, shielded in the normal pipeline only by `mainn()`'s own guard (incidental protection from a caller, the exact anti-pattern already fixed once this session for `mainn()` itself), but a real crash for any direct caller — confirmed a test in the suite calls this function directly; (2) rewritten with `ruamel.yaml` for a real per-task `"line"` field, keeping `warnings`/`nbLeaks`'s type and wording unchanged for backward compatibility and adding a new third `details` return value with real line numbers for `findings.py`. |
| `unnamed_tasks.py` | ✅ fixed — guard only; **fixed again this round for a serious, previously-undiscovered bug**: it iterated `top_level_tasks` (the *raw* dicts `calculate_metrics_task()` returns, which have no computed fields at all) and checked `task.get("task_name")` — a key that only exists on the *computed* entries in `all_metrics`, never on a raw task dict. Confirmed directly: a fixture with one genuinely unnamed task returned `0`, not `1` — the "Unnamed Task" CSV column has very likely reported `0` for every file, always, this entire session. Fixed by iterating `all_metrics` instead (also fixes the structural gap that `top_level_tasks` could never see tasks nested inside a real play at all). Now returns `(count, details)` with a real per-task `"line"`. |
| `unnamed_play.py` | ✅ fixed — guard done; OR/AND bug fixed, confirmed working (hosts-only play now correctly caught); **fixed again this round for a real undercounting bug found in `parser_playbook.py`'s consumption of it, not this file itself**: `detect_large_play.py` substitutes the placeholder string `"unknown"` for `Play_name` when a play has no real name (so display code always has something to show), but `parser_playbook.py`'s per-play loop then called `is_unnamed()` on that *already-substituted placeholder* — `"unknown"` is a non-empty string, so `is_unnamed("unknown")` always returned `0`, silently masking every genuinely unnamed play in the final per-play/CSV count. Confirmed directly: a real `hosts:`-only play with no `name:` reported `unnamed_play == 0`. Fixed by having `parser_playbook.py` use this file's own `unnamed_play_details` (rewritten to return `(count, details)` with a real per-play `"line"`, built from a fresh, correct check against the raw YAML, unaffected by the placeholder) matched by line number, instead of re-checking the corrupted `Play_name` field. |
| `set_fact.py` | ✅ fixed — guard only |
| `overriding_facts.py` | ✅ fixed — guard only; confirmed no crash on non-list (vault-string) input |
| `incohesive_plays.py` | ✅ fixed — guard + threshold path; **fixed again**: carried the same non-English/out-of-vocabulary false-cohesion bug already found and fixed in `sem_cohesion.py` (a play whose task names are all OOV was scored as perfectly cohesive instead of unmeasurable), missed by the earlier "confirmed good, pure consumer of `detect_large_play.py`" clearance below, which was correct about block-recursion specifically but didn't cover this separate axis. Now mirrors `sem_cohesion.py`'s fix; unlike that file, this one only ever returns a plain count, so no downstream `None`-handling change was needed. |
| `parser_playbook.py` | ✅ fixed — guard only |
| `smellsDetector.py` | ✅ fixed — 8 original bugs, **plus a fourth found via real-world CLI validation** (see `PROJECT_STATUS.md` and `CLI_STATUS.md`): (1) `assess_code_smells()` used a bare `yaml_file_path` that silently fell back to a module-level global instead of the real file being analyzed; (2) `playbook_metrics`/`high_coupling_metrics` crashed on present-but-`None` values, and `Num_Imports`/`Num_Roles` were read from the wrong dict entirely, meaning `High Playbook Coupling` never fired correctly for any file, ever; (3) `execute_for_single_file()` never checked whether `mainn()` returned `None` before using it. **(4), found while auditing the rest of the function for the same `None`-vs-missing-key hazard class**: `play_special_chars = (play.get("play_metrics") or {}).get("special_chars", 0)` already unwraps to a plain `int`, but the very next line called `.get("special_chars", 0)` on that same int again — `AttributeError: 'int' object has no attribute 'get'`. Only fired when the task's own `special_chars` didn't exceed threshold (Python's `or` short-circuits, skipping the buggy right-hand side otherwise), which is why it never surfaced on the project's own tiny fixtures. Confirmed against the real, unmodified function before fixing; fixed by removing the redundant second `.get()`. `execute_for_single_file()` also now returns the raw `metrics` dict and the structured `result` dict alongside `findings`/`lint_results` (a 4-tuple, was a 2-tuple) so `cli.py` can build detailed findings without re-parsing the file — both call sites (this file's own batch-mode `__main__`, and `cli.py`) updated. |
| `cli.py` | ✅ new this round — `collect_yaml_files()` (recursive discovery, proven against a real 42-file external project), `output_dir_for()` (collision-safe per-file output paths — confirmed the naive file-stem-only naming really does collide on real projects, e.g. two different roles' `tasks/main.yml`), `analyze_path()` (wires the existing per-file pipeline into an arbitrary target path/output directory instead of `config.py`'s hardcoded folder, and accumulates project-wide rollups — see `OUTPUT_FORMATS.md`). |
| `findings.py` | ✅ new this round — flattens one file's `(metrics, result, gitleaks findings, lint results)` into `{file, line, rule_id, severity, message}` dicts. Rule/severity catalog (`RULE_CATALOG`) is a stated, provisional judgment call (security > correctness > style), not yet empirically calibrated — flagged for a future pass against the project's own `Literature_review/` sources. |
| `sarif_writer.py` | ✅ new this round — serializes `findings.py`'s flat list into a real SARIF 2.1.0 document. Validated against the actual downloaded OASIS schema (not just eyeballed) — including the repo-relative-URI requirement GitHub Code Scanning needs to correctly map an annotation back to a file in a PR diff. |
| `Install_Gitleaks.py` | ✅ fixed — arch detection + version wiring |
| `is_unamed.py` | ✅ fixed — None-or-empty check, confirmed working |
| `duplicate_code.py` | ✅ **fixed and pytest-confirmed** — previously required `'name' in task` to consider a task at all, so two unnamed tasks with identical parameters were completely invisible (this was originally a documented `xfail` limitation, not silently unnoticed). Rewritten to drop the name requirement (`task.pop('name', None)` is safe either way) and added `block`/`rescue`/`always` recursion, which the original never had at all. Confirmed via 4 tests: named duplicates (original passing case, no regression), unnamed duplicates (the fixed case), duplicates nested in separate `block:` wrappers (new coverage), and a clean negative case. |
| `files_extensions.py` | ✅ fixed — missing `rescue`/`always` recursion, triple-count bug in task collection |
| `filters_for_comparison.py` | ✅ **genuinely fixed and pytest-confirmed** — `TypeError` crash on bare-boolean `when:` conditions was real and fixed; the `rescue`/`always` recursion claimed fixed in an earlier pass was **not actually present in the code** (confirmed false via a failing pytest test — see `PROJECT_STATUS.md`). Real fix applied and verified this round. |
| `overriden_keys.py` | ✅ **rewritten** — replaced the fragile `- name:` text-heuristic with a structural approach using `ruamel.yaml`'s round-trip loader (`.lc.line` for real per-dict line numbers). Old version misattributed duplicates to the wrong entity and, worse, silently stopped scanning the rest of the file the moment any task's first key wasn't literally `name:` (e.g. `become:` before `name:` — ordinary Ansible style). Confirmed via 4 targeted fixtures plus no regression on the original `task8` case from `main3.yml`. |
| `Ansible_Lint.py` | ✅ confirmed clean — tested against real findings, nonexistent target path, and simulated missing binary; all degrade correctly, never crash |
| `unecessary_abs.py` | ✅ confirmed clean — tested against empty file, nested single-task block, and rescue-nested block fixtures |
| `include_vars.py` | ✅ fixed — dict-not-list early-return path returned a bare `0` instead of the `(0, [])` tuple every caller expects; crashed `parser_playbook.py`'s unpacking on any non-list top-level YAML (dict-shaped vars files, vault-encrypted files) |
| `high_coupling.py` | ✅ fixed — `KeyError` on singular `role:`; nested `import_tasks`/`include_tasks` detection; missing type guard on non-list YAML (vault files); **fixed again this round**: a single malformed/blank list item (e.g. a stray `- ` or `- null` in hand-edited YAML — a common typo) wasn't a crash (caught by the function's own broad `except`), but silently discarded *every other real play's* coupling data for the whole file, since the per-entry loop had no `isinstance(play, dict)` guard before the outer `except` swallowed the resulting `TypeError`. Confirmed directly. Fixed with a per-entry guard so one bad item only skips itself. |
| `sem_cohesion.py` | ✅ **genuinely fixed and pytest-confirmed** — recurses into `block`/`rescue`/`always`, guards non-dict entries, `utf-8` encoding confirmed (an earlier discrepancy flag is resolved). The non-English/OOV handling had a real follow-up bug: vector availability was tracked as one shared counter across plays and tasks combined, so a normal English play name could mask that the task names specifically were entirely unmeasurable, silently falling through to a false "perfectly cohesive" result again. Fixed by tracking each group (plays, tasks) independently. Confirmed via a monkeypatched test controlling `has_vector` directly, not dependent on the real model's specific vocabulary. |
| `GitLeaks_hardcoded_credentials.py` | ✅ fixed — a nonexistent target playbook path was already handled gracefully (real GitLeaks exits non-zero, the `else` branch returns `[]`); a missing/misconfigured `gitleaks` **binary** path raised an unguarded `FileNotFoundError` from `subprocess.run()`, caught one level up by `execute_for_single_file`'s broad `try/except` (so it didn't crash the batch run) but silently skipped the file's entire analysis with a misleading error that read as if the *playbook* was missing rather than the *binary*. Fixed with an explicit `except FileNotFoundError` pointing at the real fix. Verified against all three paths: missing binary, bad target, successful scan with real findings. |
| `write_to_csv.py` | ✅ **fixed and pytest-confirmed** — `None` vs. blank regression from the `sem_cohesion.py` fix; `ansible_lint_issues` consistency gap |
| `write_to_text.py` | ✅ **fixed and pytest-confirmed** — Global-tasks group printed with no header, visually indistinguishable from belonging to the preceding play; confirmed misleading via `main3.yml`'s final regression run, not just cosmetic. Append-mode call-order dependency (multiple writer functions share one output file, some `'w'` some `'a'`) is real and intentional — now locked in by a dedicated test rather than left as an undocumented trap. |
| `requirements.txt` | 🟡 reviewed — 2 invalid lines, not fixed |
| `GeneralsmellsDetector.py` | 🟡 reviewed — decide delete/keep |
| `parser_playbook_mod.py` | ⚪ not reviewed (dead code, low priority) |
| `parser_playbook.ipynb` | ⚪ not reviewed (dead code, low priority) |
| `exceptions.py` | ⚪ empty, unused |

**Note:** `include_vars.py`'s regex looseness (misses `{{var_name}}` with no
spaces, and `{{ var_name | default(...) }}`) is still open — a separate,
narrower issue from the tuple-shape crash bug that was fixed this round.

**Both items previously listed here as "next candidates to review"
(non-English playbook handling, `write_to_csv.py`/`write_to_text.py`) are
now resolved and pytest-covered** — see the "Automated regression suite"
section below for current remaining candidates.

## Automated regression suite (pytest) — now the primary way to verify fixes

`AnsibleGuard/tests/` contains a growing `pytest` suite, one file per
detector, seeded from every bug found and manually verified across this
whole debugging effort. Run the whole thing with:
```bash
cd ~/Documents/AnsibleChecklist/AnsibleGuard
python3 -m pytest tests/ -v
```

**Why this now takes priority over the manual "How to test" section below:**
a status doc claiming a bug is fixed can silently go stale the moment the
code changes without the doc changing too — and it did, for real, this
round (`filters_for_comparison.py`'s `rescue`/`always` recursion was
recorded here as fixed, and wasn't; a pytest test asserting the correct
behavior failed against the real code, which is what caught it). A test
that actually executes the real function against a concrete fixture can't
drift out of sync the same way. Treat a green pytest run as the source of
truth; treat this file's status table as a human-readable summary that
should always agree with it, not the other way around.

Structure:
- `tests/conftest.py` — the shared `fixtures_dir` pytest fixture every test
  file uses to locate `tests/fixtures/`
- `tests/fixtures/*.yml` — real YAML sample files, one or more per bug
  scenario, readable on their own
- `tests/test_<module_name>.py` — one file per source module under test

Coverage so far (all confirmed passing on the actual project machine, not
just in isolation): `duplicate_task_Name.py`, `overriden_keys.py`,
`high_coupling.py`, `credentials_leaking_in_log.py`, `detect_large_task.py`,
`detect_large_play.py`, `detect_large_playbook.py`, `unecessary_abs.py`,
`include_vars.py`, `is_unamed.py`, `unnamed_play.py`, `Ansible_Lint.py`,
`overriding_facts.py`, `set_fact.py`, `duplicate_code.py` (was an `xfail`
documenting a known limitation — now a real, complete fix, see status table
above), `files_extensions.py`, `filters_for_comparison.py`,
`smellsDetector.py`'s `assess_code_smells()` aggregation logic (confirmed
the documented per-play counter-reset bug is NOT actually present — a
genuine, valuable correction in the *opposite* direction from the
`filters_for_comparison.py` discovery: that time the doc wrongly claimed
"fixed," this time an earlier doc pass correctly recorded it as fixed and
pytest now independently confirms that claim is true), `sem_cohesion.py`
(found and fixed a real follow-up bug in an earlier "fixed" pass — see
`PROJECT_STATUS.md`), `write_to_csv.py`, `write_to_text.py` (both were
already genuinely correctly fixed in an earlier pass; this round gave them
pytest coverage for the first time, including an explicit test locking in
the append-mode call-order fragility as a documented, intentional behavior
rather than an undocumented trap).

**Known environment gap:** `overriden_keys.py`'s tests depend on
`ruamel.yaml`, which is not currently listed in `requirements.txt` — a
fresh install would hit `ModuleNotFoundError` even though existing
development machines already have it installed. Needs adding.

**All items from the previous "still to write" list are now covered.** Next
candidates, not yet given pytest coverage: `parser_playbook.py`'s `mainn()`
end-to-end orchestration as its own direct test (currently only exercised
indirectly through `test_smellsDetector.py`); `incohesive_plays.py` itself
(its upstream dependency `detect_large_play.py` is well-covered, but the
play-level cohesion function has no direct test of its own yet);
`GitLeaks_hardcoded_credentials.py` — now stress-tested (see its status row
above); `Install_Gitleaks.py` still not stress-tested against "target path
doesn't exist" (its own responsibility is installing the binary, not
scanning a target, so this may not even apply — worth a quick check rather
than assuming).

## Manual regression procedure (fallback / pre-pytest reference)

This section predates the pytest suite above and is kept as a fallback for
whole-pipeline smoke-testing (running `smellsDetector.py` itself against
real fixture files) — the pytest suite is more precise for verifying
individual bug fixes, but doesn't yet replace an actual end-to-end run of
the real entry point.

## How to test the *whole* project, start to finish — UPDATED for the package

This is the full regression check — run it after any change, not just the
file you touched, since the pipeline is tightly coupled (we've seen bugs in
one file silently corrupt another file's output more than once). Commands
below reflect the post-refactor package (`pip install -e .`, `ansibleguard`
CLI) — none of this requires `cd`-ing into any particular subfolder anymore.

### 1. Environment sanity
```bash
cd ~/Documents/AnsibleChecklist   # repo root — any directory actually works, this is just convenient
pip install -e .
python -c "from ansibleguard.config import THRESHOLDS_FILE; print(THRESHOLDS_FILE.exists())"
# expect: True
./gitleaks-bin/gitleaks version
# expect: a version string, not an error
```

### 2. Import check — every module, no crashes
```bash
for f in ansibleguard.detectors.large_task ansibleguard.detectors.large_play \
         ansibleguard.detectors.large_playbook ansibleguard.detectors.duplicate_task_names \
         ansibleguard.detectors.credentials_in_log ansibleguard.detectors.unnamed_tasks \
         ansibleguard.detectors.unnamed_play ansibleguard.detectors.set_fact \
         ansibleguard.detectors.overriding_facts ansibleguard.detectors.incohesive_plays \
         ansibleguard.parser ansibleguard.smells ansibleguard.detectors.is_unnamed \
         ansibleguard.detectors.high_coupling ansibleguard.detectors.duplicate_code \
         ansibleguard.detectors.file_extensions ansibleguard.detectors.bool_filters \
         ansibleguard.detectors.overridden_keys ansibleguard.detectors.include_vars \
         ansibleguard.detectors.unnecessary_abstraction ansibleguard.detectors.semantic_cohesion \
         ansibleguard.report.csv_writer ansibleguard.report.text_writer \
         ansibleguard.external.ansible_lint ansibleguard.external.install_gitleaks \
         ansibleguard.cli; do
  echo -n "$f: "
  python -c "import $f" 2>&1 | tail -1 || echo "OK"
done
```
Anything other than a blank "OK" line means that module has a crash-on-import
bug we haven't caught yet. This should also work from **any** directory, not
just the repo root — worth confirming with `cd /tmp` once, since "resolves
from anywhere" is the entire point of the refactor.

### 3. Full pipeline run
```bash
ansibleguard ~/Documents/AnsibleChecklist/TestData/tasks -o /tmp/ansibleguard-check
```
Should process every file with no traceback, print a per-file confirmation,
and produce a `/tmp/ansibleguard-check/<file_stem>/` folder per file with all
5 output files (`IaC_Smells.csv`, `Play_Level_Analysis.txt`,
`Technical_Analysis.json`, `ansiblelint.txt`, `gitleaks.txt`), plus the three
project-wide rollups (`summary.csv`, `findings.json`, `findings.sarif`) once
at the end.

Also worth re-running the real-world proof from the refactor itself:
```bash
ansibleguard ~/Documents/ansible-structure -o /tmp/ansibleguard-final-check
find /tmp/ansibleguard-final-check -name "IaC_Smells.csv" | wc -l
# expect: 42
```

### 4. Data-correctness spot check (the part import/crash tests can't catch)
Always check `main3.yml`'s output — it's the richest fixture (real plays,
top-level block-tasks, duplicate keys, unused include_vars, a hardcoded
secret):
```bash
cat /tmp/ansibleguard-check/main3/Technical_Analysis.json
```
Confirm, by reading the actual `main3.yml` alongside it:
- Each play's `task_metrics` list contains tasks that actually belong to
  that play (this is exactly where the `detect_large_task.py` play-numbering
  bug hid — silently plausible-looking but wrong data).
- The "Global" group (`play_metrics: null`) contains only tasks genuinely
  outside any play.

Then:
```bash
cat /tmp/ansibleguard-check/main3/IaC_Smells.csv
```
Cross-check a couple of columns by hand against `thresholds.csv` and the raw
JSON — e.g. does `Large Play` actually match how many plays in the JSON have
`LOC_play`/`num_tasks_in_play`/`avg_task_play` exceeding the real threshold
values? Don't just check "a number appears" — check it's the *right* number.
That's the difference between the "doesn't crash" bugs (caught by step 2) and
the "produces wrong data silently" bugs (only caught this way) — we found
four of the latter kind so far, and they were the most damaging ones.

### 5. Isolated fixture tests (for specific detectors) — now real `pytest`
The throwaway `/tmp/*.yml` fixtures used during the original debugging pass
have been converted into permanent files under `tests/fixtures/`, each with
a real `pytest` function in `tests/test_detectors.py` (see
`REFACTOR_PLAN.md` Part 4) — this is now the fast, controlled check for a
single detector, instead of hand-writing a throwaway YAML each time:
```bash
pytest tests/test_detectors.py -v
```
For example, the old
```bash
python -c "from duplicate_task_Name import repeated_task_names; print(repeated_task_names('/tmp/dupe_test.yml'))"
```
is now a permanent regression test against `tests/fixtures/dupe_task_names.yml`:
```python
def test_duplicate_task_names_detected():
    assert repeated_task_names(FIXTURES / "dupe_task_names.yml") == 1
```
Still worth hand-writing a brand-new throwaway fixture first when chasing a
*new* suspected bug — but once confirmed, fold it into `tests/fixtures/` +
`tests/test_detectors.py` rather than leaving it in `/tmp` to evaporate.

## What "done" looks like
- Step 2 (import check) — all clean, confirmed from a directory other than
  the repo root.
- Step 3 (full run) — no tracebacks, all output files present for all
  fixtures in `TestData/tasks/`, plus the real 42-file external project.
- Step 4 (data correctness on `main3.yml`) — every number in the CSV
  traceable back to a real value in `Technical_Analysis.json`, matched by
  hand against `thresholds.csv` and the actual YAML.
- `detectors/unnecessary_abstraction.py` and `detectors/semantic_cohesion.py`
  (formerly `unecessary_abs.py`/`sem_cohesion.py`) reviewed with the same
  rigor as everything else in the table above.
- The "Known issues" list in `PROJECT_STATUS.md` empty, or intentionally
  deferred with a reason written down.
- **New, post-refactor**: `pytest tests/` passes with the same count as
  before the move; `grep -n "pythonpath" pytest.ini` returns nothing;
  `ansibleguard --help` works from `/tmp`.
