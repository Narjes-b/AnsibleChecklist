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
| `credentials_leaking_in_log.py` | ✅ fixed — guard only; **fixed again this round** for a much more severe scope bug — it only scanned tasks with no play wrapper at all, missing virtually every real-world credential-leak case (see `PROJECT_STATUS.md`) |
| `GitLeaks_hardcoded_credentials.py` | ✅ fixed this round — unguarded crash when the `gitleaks` binary path is missing/misconfigured (a bad target playbook path was already handled gracefully) |
| `unnamed_tasks.py` | ✅ fixed — guard only |
| `unnamed_play.py` | ✅ fixed — guard done; OR/AND bug fixed this round |
| `set_fact.py` | ✅ fixed — guard only |
| `overriding_facts.py` | ✅ fixed — guard only |
| `incohesive_plays.py` | ✅ fixed — guard + threshold path |
| `parser_playbook.py` | ✅ fixed — guard only |
| `smellsDetector.py` | ✅ fixed — 8 separate bugs, see `PROJECT_STATUS.md` |
| `Install_Gitleaks.py` | ✅ fixed — arch detection + version wiring |
| `is_unamed.py` | ✅ fixed this round — None-or-empty check |
| `duplicate_code.py` | ⚪ reviewed, no bug found |
| `files_extensions.py` | ✅ fixed — missing `rescue`/`always` recursion, triple-count bug in task collection |
| `filters_for_comparison.py` | ✅ fixed — `TypeError` crash on bare-boolean `when:` conditions, missing `rescue`/`always` recursion |
| `overriden_keys.py` | ✅ fixed this round — cross-depth false positive (a task's own `name:` was being merged with an unrelated nested module parameter also called `name:`, e.g. `apt: {name: nginx}`) |
| `Ansible_Lint.py` | ⚪ reviewed, no bug found |
| `unecessary_abs.py` | ⚪ reviewed, no bug found — tested against empty file and nested single-task block fixture |
| `high_coupling.py` | ✅ fixed — `KeyError` on singular `role:`; nested `import_tasks`/`include_tasks` detection; missing type guard on non-list YAML (vault files) |
| `sem_cohesion.py` | ✅ fixed — recurses into `block`/`rescue`/`always`, guards non-dict entries; non-English/OOV names now correctly return `None` (unmeasurable) instead of falsely reporting "perfectly cohesive" |
| `incohesive_plays.py` | ✅ fixed this round — confirmed good for block-recursion (pure consumer of `detect_large_play.py`'s fix, no changes needed there); separately fixed for the same non-English/OOV false-cohesion bug found in `sem_cohesion.py` below, which the earlier block-recursion review didn't cover |
| `write_to_csv.py` | ✅ fixed — `None` vs. blank regression from the `sem_cohesion.py` fix; `ansible_lint_issues` consistency gap |
| `write_to_text.py` | ✅ fixed — Global-tasks group printed with no header, visually indistinguishable from belonging to the preceding play; confirmed misleading via `main3.yml`'s final regression run, not just cosmetic |
| `include_vars.py` | 🟡 reviewed — regex looseness noted, not fixed |
| `requirements.txt` | 🟡 reviewed — 2 invalid lines, not fixed |
| `GeneralsmellsDetector.py` | 🟡 reviewed — decide delete/keep |
| `parser_playbook_mod.py` | ⚪ not reviewed (dead code, low priority) |
| `parser_playbook.ipynb` | ⚪ not reviewed (dead code, low priority) |
| `exceptions.py` | ⚪ empty, unused |

**Next candidates to review**, in priority order (untested against adversarial
input, not just "read the code"):
1. ~~Non-English playbooks~~ — resolved this round; both `sem_cohesion.py`
   and `incohesive_plays.py` now correctly report "unmeasurable" instead of
   falsely-perfect cohesion when task/play names are entirely
   out-of-vocabulary.
2. `Ansible_Lint.py` — same class of risk as the `GitLeaks_hardcoded_credentials.py`
   fix this round (missing-binary crash): not yet stress-tested against
   `ansible-lint` not being installed at all. Still open — see
   `REFACTOR_PLAN.md` Part 5 #8.
3. `write_to_csv.py` / `write_to_text.py` — marked "reviewed, no bug found"
   early on before the block-recursion and play_id bugs were discovered;
   worth a second pass now that upstream data shapes have changed twice
   since that review.

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
- `credentials_leaking_in_log.py` and `incohesive_plays.py` re-verified this
  round with the same rigor after both were found to have bugs missed by
  an earlier pass — a reminder that "reviewed, no bug found" on one axis
  (e.g. crash-safety, or one specific data-shape issue) doesn't guarantee
  no bug exists on a different axis of the same file.
- The "Known issues" list in `PROJECT_STATUS.md` empty, or intentionally
  deferred with a reason written down.
