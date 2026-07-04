# AnsibleChecklist — Architecture & Test Guide

Companion to `PROJECT_STATUS.md` (bug log). This file answers: what calls
what, what still needs eyes on it, and how to verify the whole project end
to end. For the forward-looking packaging/refactoring plan, see
`REFACTOR_PLAN.md`.

## Entry point and call graph

```
smellsDetector.py  (run this)
  │
  ├── config.py                     # all paths — read first if anything can't find a file
  │
  ├── parser_playbook.py            # orchestrates ONE playbook's full analysis
  │     │
  │     ├── detect_large_playbook.py
  │     │     ├── detect_large_task.py   (calculate_metrics_task)
  │     │     └── detect_large_play.py   (calculate_metrics_play)
  │     │
  │     ├── detect_large_play.py         (calculate_metrics_play)
  │     ├── detect_large_task.py         (calculate_metrics_task)
  │     ├── high_coupling.py
  │     ├── duplicate_code.py
  │     ├── set_fact.py
  │     ├── overriding_facts.py
  │     ├── unecessary_abs.py
  │     ├── unnamed_play.py
  │     ├── is_unamed.py
  │     ├── unnamed_tasks.py             (→ detect_large_task.py)
  │     ├── overriden_keys.py            (→ write_to_text.write_duplicates_to_txt)
  │     ├── sem_cohesion.py              (playbook-level similarity, spacy)
  │     ├── incohesive_plays.py          (play-level similarity, spacy)
  │     │     └── detect_large_play.py
  │     ├── duplicate_task_Name.py       (→ detect_large_task.py)
  │     ├── files_extensions.py
  │     ├── filters_for_comparison.py
  │     ├── credentials_leaking_in_log.py (→ detect_large_task.py)
  │     └── include_vars.py              (→ write_to_text.write_unused_vars_to_txt)
  │
  ├── assess_code_smells()  [inside smellsDetector.py itself]
  │     — takes parser_playbook's raw metrics + thresholds.csv,
  │       decides which smells actually fire (large_play, complex_playbook, etc.)
  │     ├── GitLeaks_hardcoded_credentials.py  (→ Install_Gitleaks.py for the binary)
  │     └── Ansible_Lint.py
  │
  └── write_to_csv.py / write_to_text.py   — final report output
```

**Not in the call graph at all** (nothing imports them):
- `parser_playbook_mod.py` — an older/alternate version of `parser_playbook.py`
  with its own CSV-writing logic. Diverged fork, not used by `smellsDetector.py`.
- `parser_playbook.ipynb` — notebook version, same idea, not used by any script.
- `GeneralsmellsDetector.py` — stale fork of `smellsDetector.py` (see
  `PROJECT_STATUS.md` Known Issue #7).
- `exceptions.py` — empty, unused.

If you're editing detection logic, **`parser_playbook.py` +
`detect_large_*.py` + `smellsDetector.py` is the real, live pipeline.** The
`_mod`/`.ipynb`/`General*` files are not — changes there won't affect
`smellsDetector.py`'s output.

## Data flow in one sentence per stage
1. `detect_large_task.py` / `detect_large_play.py` / `detect_large_playbook.py`
   read the YAML and produce **raw counts** (LOC, task counts, names) — no
   threshold logic here, just measurement.
2. `parser_playbook.py`'s `mainn()` calls all the raw-metric functions above
   plus every other detector (`set_fact.py`, `overriding_facts.py`, etc.) and
   assembles one big `main_metrics` dict per playbook — still no
   pass/fail decisions.
3. `smellsDetector.py`'s `assess_code_smells()` takes that dict, loads
   `thresholds.csv`, and decides which smells actually fire (that's where
   `is_large_play`, `complex_playbook`, etc. get computed).
4. `write_to_csv.py` / `write_to_text.py` render the final decision dict to
   disk.

This matters for debugging: if a number looks wrong, check
`Technical_Analysis.json` first (that's stage 2's raw output, before any
threshold logic) — if the raw number is already wrong, the bug is in a
`detect_large_*.py` file. If the raw number is right but the CSV's smell flag
is wrong, the bug is in `smellsDetector.py`'s threshold logic instead. This is
exactly how we found the `detect_large_task.py` play-numbering bug.

## Files touched and fix status

| File | Status |
|---|---|
| `config.py` | ✅ fixed — portable paths |
| `detect_large_task.py` | ✅ fixed — guard, play-boundary bug, `UnboundLocalError` on non-list YAML (vault files) |
| `detect_large_play.py` | ✅ fixed — guard only; block/rescue/always recursion now matches `detect_large_task.py`'s task semantics |
| `detect_large_playbook.py` | ✅ fixed — guard + try/except widened |
| `duplicate_task_Name.py` | ✅ fixed — guard + tuple-unpack bug |
| `credentials_leaking_in_log.py` | ✅ fixed — guard only |
| `unnamed_tasks.py` | ✅ fixed — guard only |
| `unnamed_play.py` | ✅ fixed — guard done; OR/AND bug fixed, confirmed working (hosts-only play now correctly caught) |
| `set_fact.py` | ✅ fixed — guard only |
| `overriding_facts.py` | ✅ fixed — guard only; confirmed no crash on non-list (vault-string) input |
| `incohesive_plays.py` | ✅ fixed — guard + threshold path |
| `parser_playbook.py` | ✅ fixed — guard only |
| `smellsDetector.py` | ✅ fixed — 8 separate bugs, see `PROJECT_STATUS.md` |
| `Install_Gitleaks.py` | ✅ fixed — arch detection + version wiring |
| `is_unamed.py` | ✅ fixed — None-or-empty check, confirmed working |
| `duplicate_code.py` | ✅ **fixed and pytest-confirmed** — previously required `'name' in task` to consider a task at all, so two unnamed tasks with identical parameters were completely invisible (this was originally a documented `xfail` limitation, not silently unnoticed). Rewritten to drop the name requirement (`task.pop('name', None)` is safe either way) and added `block`/`rescue`/`always` recursion, which the original never had at all. Confirmed via 4 tests: named duplicates (original passing case, no regression), unnamed duplicates (the fixed case), duplicates nested in separate `block:` wrappers (new coverage), and a clean negative case. |
| `files_extensions.py` | ✅ fixed — missing `rescue`/`always` recursion, triple-count bug in task collection |
| `filters_for_comparison.py` | ✅ **genuinely fixed and pytest-confirmed** — `TypeError` crash on bare-boolean `when:` conditions was real and fixed; the `rescue`/`always` recursion claimed fixed in an earlier pass was **not actually present in the code** (confirmed false via a failing pytest test — see `PROJECT_STATUS.md`). Real fix applied and verified this round. |
| `overriden_keys.py` | ✅ **rewritten** — replaced the fragile `- name:` text-heuristic with a structural approach using `ruamel.yaml`'s round-trip loader (`.lc.line` for real per-dict line numbers). Old version misattributed duplicates to the wrong entity and, worse, silently stopped scanning the rest of the file the moment any task's first key wasn't literally `name:` (e.g. `become:` before `name:` — ordinary Ansible style). Confirmed via 4 targeted fixtures plus no regression on the original `task8` case from `main3.yml`. |
| `Ansible_Lint.py` | ✅ confirmed clean — tested against real findings, nonexistent target path, and simulated missing binary; all degrade correctly, never crash |
| `unecessary_abs.py` | ✅ confirmed clean — tested against empty file, nested single-task block, and rescue-nested block fixtures |
| `include_vars.py` | ✅ fixed — dict-not-list early-return path returned a bare `0` instead of the `(0, [])` tuple every caller expects; crashed `parser_playbook.py`'s unpacking on any non-list top-level YAML (dict-shaped vars files, vault-encrypted files) |
| `high_coupling.py` | ✅ fixed — `KeyError` on singular `role:`; nested `import_tasks`/`include_tasks` detection; missing type guard on non-list YAML (vault files) |
| `sem_cohesion.py` | ✅ **genuinely fixed and pytest-confirmed** — recurses into `block`/`rescue`/`always`, guards non-dict entries, `utf-8` encoding confirmed (an earlier discrepancy flag is resolved). The non-English/OOV handling had a real follow-up bug: vector availability was tracked as one shared counter across plays and tasks combined, so a normal English play name could mask that the task names specifically were entirely unmeasurable, silently falling through to a false "perfectly cohesive" result again. Fixed by tracking each group (plays, tasks) independently. Confirmed via a monkeypatched test controlling `has_vector` directly, not dependent on the real model's specific vocabulary. |
| `incohesive_plays.py` | ✅ confirmed good — pure consumer of `detect_large_play.py`, correctly benefits from its block-recursion fix with no changes needed |
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
`GitLeaks_hardcoded_credentials.py` and `Install_Gitleaks.py` (never
stress-tested against "gitleaks binary not installed" or "target path
doesn't exist," unlike `Ansible_Lint.py` which has exactly this coverage).

## Manual regression procedure (fallback / pre-pytest reference)

This section predates the pytest suite above and is kept as a fallback for
whole-pipeline smoke-testing (running `smellsDetector.py` itself against
real fixture files) — the pytest suite is more precise for verifying
individual bug fixes, but doesn't yet replace an actual end-to-end run of
the real entry point.

## How to test the *whole* project, start to finish

This is the full regression check — run it after any change, not just the
file you touched, since the pipeline is tightly coupled (we've seen bugs in
one file silently corrupt another file's output more than once).

### 1. Environment sanity
```bash
cd ~/Documents/AnsibleChecklist/AnsibleGuard
python -c "from config import TEST_PLAYBOOK, THRESHOLDS_FILE, yaml_files_folder, RESULTS_DIR; print(TEST_PLAYBOOK.exists(), THRESHOLDS_FILE.exists(), yaml_files_folder.exists(), RESULTS_DIR.exists())"
# expect: True True True True
./gitleaks-bin/gitleaks version
# expect: a version string, not an error
```

### 2. Import check — every module, no crashes
```bash
for f in detect_large_task detect_large_play detect_large_playbook \
         duplicate_task_Name credentials_leaking_in_log unnamed_tasks \
         unnamed_play set_fact overriding_facts incohesive_plays \
         parser_playbook smellsDetector is_unamed high_coupling \
         duplicate_code files_extensions filters_for_comparison \
         overriden_keys include_vars unecessary_abs sem_cohesion \
         write_to_csv write_to_text Ansible_Lint Install_Gitleaks; do
  echo -n "$f: "
  python -c "import $f" 2>&1 | tail -1 || echo "OK"
done
```
Anything other than a blank "OK" line means that file has a crash-on-import
bug we haven't caught yet.

### 3. Full pipeline run
```bash
python smellsDetector.py
```
Should process all files in `TestData/tasks/` with no traceback, print
`[✔] Results are saved to ...` for each, and produce a
`TestData/Results/<file_stem>/` folder per file with all 5 output files
(`IaC_Smells.csv`, `Play_Level_Analysis.txt`, `Technical_Analysis.json`,
`ansiblelint.txt`, `gitleaks.txt`).

### 4. Data-correctness spot check (the part import/crash tests can't catch)
Always check `main3.yml`'s output — it's the richest fixture (real plays,
top-level block-tasks, duplicate keys, unused include_vars, a hardcoded
secret):
```bash
cat TestData/Results/main3/Technical_Analysis.json
```
Confirm, by reading the actual `main3.yml` alongside it:
- Each play's `task_metrics` list contains tasks that actually belong to
  that play (this is exactly where the `detect_large_task.py` play-numbering
  bug hid — silently plausible-looking but wrong data).
- The "Global" group (`play_metrics: null`) contains only tasks genuinely
  outside any play.

Then:
```bash
cat TestData/Results/main3/IaC_Smells.csv
```
Cross-check a couple of columns by hand against `thresholds.csv` and the raw
JSON — e.g. does `Large Play` actually match how many plays in the JSON have
`LOC_play`/`num_tasks_in_play`/`avg_task_play` exceeding the real threshold
values? Don't just check "a number appears" — check it's the *right* number.
That's the difference between the "doesn't crash" bugs (caught by step 2) and
the "produces wrong data silently" bugs (only caught this way) — we found
four of the latter kind so far, and they were the most damaging ones.

### 5. Isolated fixture tests (for specific detectors)
Useful when you've changed one detector and want a fast, controlled check
without running the whole pipeline:
```bash
# duplicate task names
cat > /tmp/dupe_test.yml << 'EOF'
- name: Install package
  apt: {name: nginx}
- name: Install package
  apt: {name: curl}
EOF
python -c "from duplicate_task_Name import repeated_task_names; print(repeated_task_names('/tmp/dupe_test.yml'))"
# expect: 1

# credential leaking without no_log
cat > /tmp/creds_test.yml << 'EOF'
- name: Set database password
  set_fact: {db_password: "supersecret123"}
EOF
python -c "from credentials_leaking_in_log import detect_credentials_leaking_in_log as d; w,n = d('/tmp/creds_test.yml'); print(n, w)"
# expect: 1 [warning about no_log]
```
Build similar tiny fixtures for anything else you change — much faster
feedback loop than re-running the whole pipeline every time.

## What "done" looks like
- Step 2 (import check) — all clean.
- Step 3 (full run) — no tracebacks, all output files present for all
  fixtures in `TestData/tasks/`.
- Step 4 (data correctness on `main3.yml`) — every number in the CSV
  traceable back to a real value in `Technical_Analysis.json`, matched by
  hand against `thresholds.csv` and the actual YAML.
- `unecessary_abs.py` and `sem_cohesion.py` reviewed with the same rigor
  as everything else in the table above.
- The "Known issues" list in `PROJECT_STATUS.md` empty, or intentionally
  deferred with a reason written down.
