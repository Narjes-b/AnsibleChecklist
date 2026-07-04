# AnsibleGuard — Per-File Pipeline Reference

Companion to `ARCHITECTURE.md` (call graph + testing) and `REFACTOR_PLAN.md`
(packaging roadmap). Those answer "what calls what" and "how do we ship
this." This file answers a narrower question for each individual file:
**what does it actually compute, where does that number end up, and what's
its current bug status.**

Organized by pipeline stage, matching the call graph in `ARCHITECTURE.md`.
"Feeds → " lines trace a value from the detector function, through the key
it's stored under in `parser_playbook.py`'s `main_metrics` dict, to the
`Technical_Analysis.json` key, to (where applicable) the threshold check in
`smellsDetector.py`, to the final `IaC_Smells.csv` column.

---

## Entry point & orchestration

### `smellsDetector.py`
**Role:** Batch entry point. Loops over every `.yml`/`.yaml` in
`yaml_files_folder`, calls `parser_playbook.mainn()` per file to get raw
metrics, then `assess_code_smells()` (defined in this same file) applies
`thresholds.csv` to decide which smells actually fire. Also invokes
GitLeaks and ansible-lint per file and writes all five output files per
playbook (`Technical_Analysis.json`, `IaC_Smells.csv`,
`Play_Level_Analysis.txt`, `ansiblelint.txt`, `gitleaks.txt`).
**Status:** ✅ 8 bugs fixed in earlier rounds (see `PROJECT_STATUS.md`).
**Known fragility (not a live bug):** `assess_code_smells()` reads the
module-level `yaml_file_path` name (imported from `config.py`) rather than
receiving it as a parameter. It currently resolves correctly only because
the `for yaml_file_path in yaml_files:` loop at module scope silently
rebinds that same global before each call. Correct today; worth making
explicit (pass it as a real argument) during the Part 2 `src`-layout
refactor, since relative imports will force a signature change here anyway.

### `parser_playbook.py`
**Role:** Per-file orchestrator. `mainn(yaml_file_path)` calls essentially
every detector below, assembles one `main_metrics` dict (playbook-level
metrics + a `"plays"` list with per-play/per-task breakdowns), and returns
it to `smellsDetector.py`. This dict *is* `Technical_Analysis.json`.
**Status:** ✅ fixed — guard only.
**Design note (not a correctness bug):** every detector function
independently re-opens and re-parses the same YAML file with its own
`yaml.safe_load()` call — the file is parsed on the order of 15+ separate
times per playbook (`calculate_metrics_task` alone runs 4 times: once
directly, and again inside `unnamed_tasks`, `duplicate_task_Name`, and
`credentials_leaking_in_log`, each of which re-derives it from scratch).
Doesn't produce wrong output, but it's the first thing that will matter
once `REFACTOR_PLAN.md` Part 3's `rglob`-based CLI runs this against a real
multi-role project instead of 3 tiny fixtures — worth a shared "parse once,
pass the dict around" pass alongside the packaging work.

### `config.py`
**Role:** All paths, built from `BASE_DIR`/`PROJECT_ROOT` so the tool isn't
tied to one machine's absolute paths. Nothing computational.
**Status:** ✅ fixed — portable paths.

---

## Stage 1 — raw metrics (no threshold logic, just measurement)

### `detect_large_task.py`
**Role:** `calculate_metrics_task()` walks the playbook and returns
`(all_metrics, top_level_tasks)`: `all_metrics` is a flat list of computed
per-task metrics (`task_name`, `LOC_task`, `task_name_len`,
`special_chars`) for **every** task anywhere in the file (nested in plays,
in `block`/`rescue`/`always`, or bare top-level) tagged with a `play_id`
(`-1` means "global", not inside any play). `top_level_tasks`, by contrast,
is the much narrower list of *raw* task dicts that sit directly in the
playbook with no `hosts`/`tasks` wrapper at all — this distinction is the
root of the `credentials_leaking_in_log.py` bug below.
**Feeds →** `metrics_task` in `parser_playbook.py` → `plays[].task_metrics`
in `Technical_Analysis.json` → per-task `LOC_task`/`task_name_len`/
`special_chars` threshold checks in `smellsDetector.py` → CSV columns
`Large Task`, `Long Task Name`, `Inconsistent Naming Convention`.
**Status:** ✅ fixed — guard, play-boundary bug, `UnboundLocalError` on
non-list YAML (vault files).

### `detect_large_play.py`
**Role:** `calculate_metrics_play()` computes per-play `LOC_play`,
`num_tasks_in_play`, `avg_task_play`, and collects `tasks_names` (names of
real tasks in the play, correctly skipping `block:` wrappers themselves).
**Feeds →** `metrics_play` → `plays[].play_metrics` in JSON → `LOC_play` /
`num_tasks_play` / `avg_task_play` threshold checks → CSV column
`Large Play`. Also the sole upstream data source for `incohesive_plays.py`.
**Status:** ✅ fixed — guard only; block/rescue/always recursion now
matches `detect_large_task.py`'s task semantics.

### `detect_large_playbook.py`
**Role:** `calculate_metrics_playbook()` — playbook-wide roll-up:
`LOC_playbook` (via the `ansiblemetrics` library's `LinesCode` +
`LinesComment`), `num_plays`, `avg_play_size`, `num_nested_tasks_playbook`,
`num_global_tasks_playbook`, by summing the per-play/per-task results from
the two files above.
**Feeds →** `metrics_playbook` → `playbook.metrics` in JSON →
`large_playbook` / `complex_playbook` / `insufficient_modularization`
threshold checks → CSV columns `Large Playbook`, `Complex Playbook`,
`Insufficient Modularization`.
**Status:** ✅ fixed — guard + try/except widened. `NumTasks`, `NumPlays`,
`AvgPlaySize`, `AvgTaskSize` are imported from `ansiblemetrics` but never
actually used (the file computes its own versions instead) — dead imports,
harmless, cosmetic cleanup candidate only.

---

## Stage 2 — individual smell detectors

### `high_coupling.py`
**Role:** Counts `import_playbook`/`import_tasks`/`include_tasks` (at play
level and recursively inside `block`/`rescue`/`always`) and `roles:` usage
per playbook → `Num_Imports`, `Num_Roles`.
**Feeds →** `metrics_high_coupling` → `playbook.metrics` →
`high_coupling` threshold check → CSV column `High Playbook Coupling`.
**Status:** ✅ fixed — `KeyError` on singular `role:`; nested
`import_tasks`/`include_tasks` detection; type guard on non-list YAML.

### `overriden_keys.py`
**Role:** Detects a YAML mapping key repeated within the same task (e.g.
two `msg:` lines under one `debug:`), using `ruamel.yaml`'s real parse tree
to find task/block boundaries rather than a text heuristic.
**Feeds →** `overridenKeys` → `playbook.metrics.overriden_keys` (the raw
list of `{task_name, start_line, duplicates}` dicts, not a count) → CSV
column `Overriden keys` → also rendered as its own section in
`Play_Level_Analysis.txt` via `write_duplicates_to_txt`.
**Status:** ✅ fixed this session — depth-aware duplicate detection so a
task's own `name:` is never confused with an unrelated nested module
parameter also called `name:` (e.g. `apt: {name: nginx}`). Verified against
4 fixtures plus the real `main3.yml`.

### `sem_cohesion.py`
**Role:** `calculate_similarity()` — playbook-wide semantic cohesion: uses
spaCy word vectors to compare all play names to each other and all task
names to each other (recursing into `block`/`rescue`/`always`), returns one
average similarity score for the whole file.
**Feeds →** `similarityPlaybook` → `playbook.metrics.similarity` →
compared against `thresholds.csv`'s `similarity` key → CSV column
`Incohesive Playbook`.
**Status:** ✅ fixed — recurses into nested sections, guards non-dict
entries; **non-English/out-of-vocabulary names now correctly return `None`
("unmeasurable") instead of falsely reporting "perfectly cohesive."**
Required a matching `None`-vs-blank fix in `write_to_csv.py` (below).

### `incohesive_plays.py`
**Role:** `calculate_similarity()` (same name, play-scoped) — per-play
version of the above: for each play, compares that play's own task names
to each other and counts how many plays fall below the `similarityPlays`
threshold.
**Feeds →** `similarityPlays` → `playbook.metrics.similarityPlays` (a plain
count of incohesive plays, not a score) → CSV column `Incohesive Play`.
**Status:** 🔧 **fixed this session.** Carried the exact same
falsely-cohesive bug `sem_cohesion.py` already had: a play whose task names
are all non-English/out-of-vocabulary produced `average_similarity = 1`
(perfectly cohesive) purely because nothing had a usable word vector, not
because the tasks are actually related. This is a different bug from the
block-recursion issue `ARCHITECTURE.md`'s status table checked when it
cleared this file as "confirmed good, no changes needed" — that clearance
was correct for block-recursion but didn't cover this. Now mirrors
`sem_cohesion.py`'s fix: an all-OOV play is skipped (contributes to neither
the cohesive nor incohesive count) rather than assumed cohesive. Unlike
`sem_cohesion.py`, this function only ever returns a plain integer count,
so no downstream `write_to_csv.py`/`None`-handling change was needed.

### `duplicate_task_Name.py`
**Role:** `repeated_task_names()` — counts how many distinct task names
appear more than once anywhere in the file, using `detect_large_task.py`'s
`all_metrics` (which, unlike `top_level_tasks`, already covers every task
regardless of nesting).
**Feeds →** `duplicate_task_names` → `playbook.metrics` → CSV column
`Duplicated Task Names`.
**Status:** ✅ fixed — guard + tuple-unpack bug.

### `unnamed_play.py`
**Role:** `unnamed_play()` — counts plays with no `name:` (or a
whitespace-only one).
**Feeds →** `unnamedPlay` → `playbook.metrics.unnamed_play` → CSV column
`Unnamed Play` (also independently recomputed per-play via `is_unamed.py`
inside `parser_playbook.py`'s play loop, see below).
**Status:** ✅ fixed — guard done; OR/AND bug fixed a prior round. Has
dead code after its `return len(unnamed_plays)` (`if unnamed_plays: return
1 else: return 0`, unreachable) — cosmetic only; the live `return` already
matches what `smellsDetector.py` expects (a count, checked via `> 0`
elsewhere), so this isn't producing wrong output, just leftover cruft from
an earlier boolean-flag design.

### `is_unamed.py`
**Role:** `is_unnamed(play_name)` — one-line predicate, `1` if a play name
is `None`/empty/whitespace-only, else `0`. Used per-play inside
`parser_playbook.py`'s loop (separately from `unnamed_play.py`'s
whole-file count) to tag each individual play entry.
**Feeds →** `play_entry["unnamed_play"]` in each play dict in
`Technical_Analysis.json`'s `plays[]` list; also summed into
`num_unnamed_plays` inside `smellsDetector.py`'s play loop.
**Status:** ✅ fixed this round — `None`-or-empty check.

### `unnamed_tasks.py`
**Role:** `unnamed_tasks()` — counts tasks whose computed `task_name`
came out as `"Unknown"` (i.e. no real `name:` key), using
`detect_large_task.py`'s full `all_metrics` list (covers nested tasks
correctly, unlike `credentials_leaking_in_log.py`'s use of the same
upstream function).
**Feeds →** `unnamedTasks` → `playbook.metrics.unnamed_tasks` → CSV column
`Unnamed Task`.
**Status:** ✅ fixed — guard only. Same dead-code-after-return pattern as
`unnamed_play.py` — harmless, same reasoning applies.

### `set_fact.py`
**Role:** `set_fact()` — finds `set_fact:` variables that are declared but
never referenced anywhere else in the file (via a `{{ var }}` string
match).
**Feeds →** `unecessary_set_fact` → `playbook.metrics` → CSV column
`Unnecessary set_fact`.
**Status:** ✅ fixed — guard only. Same dead-code-after-return pattern.

### `overriding_facts.py`
**Role:** `overriding_facts()` — finds `set_fact:` variable names that get
assigned more than once with *different* values anywhere in the file
(compares all pairs, not just consecutive assignments — correct but
somewhat redundant computation, not a bug).
**Feeds →** `overriding_facts` → `playbook.metrics` → CSV column
`Overriding Facts`.
**Status:** ✅ fixed — guard only. Same dead-code-after-return pattern.

### `unecessary_abs.py`
**Role:** `unecessary_abs()` — counts `block:` wrappers (at any nesting
depth, including inside `rescue`/`always`) that wrap exactly one task, a
sign the block adds no real grouping value.
**Feeds →** `unecessary_abstraction` → `playbook.metrics` → CSV column
`Unecessary Abstraction`.
**Status:** ⚪ reviewed, no bug found — tested against an empty file and a
nested single-task block fixture.

### `files_extensions.py`
**Role:** `extract_tasks_from_playbook()` walks every real task (correctly
skipping `block`/`rescue`/`always` wrappers, only counting their children)
and `check_missing_extension()` flags file-reference attributes (`src`,
`file`, `cmd`, `path`, at both task level and nested one level inside
module parameters like `template:`/`copy:`) that lack a file extension.
**Feeds →** `extension` (a total count) → `playbook.metrics
.missing_files_extension` → CSV column `Missing File Extension`.
**Status:** ✅ fixed — missing `rescue`/`always` recursion, triple-count
bug in task collection.

### `filters_for_comparison.py`
**Role:** `get_when_conditions()` collects every `when:` condition in the
file (recursing into `block`) and `check_missing_bool_filter()` flags ones
that compare a variable to the string `"true"`/`"false"` instead of using
`| bool`, or that reference a bare variable/expression without a `| bool`
filter at all.
**Feeds →** `missing_bool_filters` → `playbook.metrics` → CSV column
`Missing Bool Filter`.
**Status:** ✅ fixed — `TypeError` crash on bare-boolean `when:`
conditions, missing `rescue`/`always` recursion.

### `credentials_leaking_in_log.py`
**Role:** `detect_credentials_leaking_in_log()` — flags tasks that
reference sensitive keywords (`password`, `secret`, `api_key`, `token`,
`access_key`, `client_secret`) without setting `no_log: true`.
**Feeds →** `nbLeaks` → `playbook.metrics.credentials_leaking_in_log` →
CSV column `Credentials Leaking In Log`.
**Status:** 🔧 **fixed this session — this was the most severe bug found
in either batch.** The function sourced its raw task dicts from
`detect_large_task.py`'s `top_level_tasks`, which by design contains
*only* tasks with no `hosts`/`tasks` wrapper at all (the `play_id=-1`
"Global" group). Every task living inside a normal `- hosts: ... tasks:
[...]` play — the overwhelming majority of real Ansible content, including
the exact "Set AWS secret key (bad practice!)" example already present in
`main3.yml` — was silently invisible to this check. Confirmed live: the
`main3.yml`-shaped fixture returned `nbLeaks: 0` despite containing an
unguarded hardcoded-looking secret task. Fixed by replacing the
`top_level_tasks` dependency with a self-contained recursive collector
(mirroring `files_extensions.py`'s traversal) that gathers every real
task's raw dict regardless of nesting. Verified against 4 cases: nested
secret (now caught), mixed top-level + nested (both caught), `no_log:
true` still correctly suppresses a flag, and a secret nested inside
`block:` is still caught.

### `include_vars.py`
**Role:** `detect_unused_include_vars()` — finds `include_vars:` files that
are loaded but whose declared variables are never referenced via `{{ var
}}` anywhere in the playbook.
**Feeds →** `unused_include_vars` → `playbook.metrics.unused_include_vars`
→ CSV column `Unecessary Dependency`; `WarningUnusedIncludeVars` also
written to `Play_Level_Analysis.txt` via `write_unused_vars_to_txt`.
**Status:** 🟡 reviewed, not fixed — regex looseness noted (the `{{ var
}}` usage-detection pattern is a plain string containment check, so it
won't correctly account for filters/whitespace variations in every case).
Lower priority than the two fixed above since it degrades gracefully
(under-detects "used," which only means an unused var might be
missed — not a false accusation).

---

## External tool wrappers

### `GitLeaks_hardcoded_credentials.py`
**Role:** `scan_with_gitleaks_file_output()` shells out to the `gitleaks`
binary and parses its JSON report. This is a distinct, separate check from
`credentials_leaking_in_log.py` above — GitLeaks does raw secret-pattern
/ entropy scanning of file content; `credentials_leaking_in_log.py` checks
for missing `no_log:` on tasks that merely *reference* sensitive key names.
**Feeds →** `findings` (list) → `hardcoded_credentials` count →
`playbook.metrics.hardcoded_credentials` → CSV column `Hardcoded
Credentials`; full findings also written to `gitleaks.txt`.
**Status:** 🔧 **fixed this session.** A nonexistent-target-path scenario
was already handled gracefully (GitLeaks itself exits non-zero and this
code's `else` branch returns `[]`). A missing/misconfigured **`gitleaks`
binary path**, however, raised an unguarded `FileNotFoundError` from
`subprocess.run()` — caught one level up by `execute_for_single_file`'s
broad `try/except`, so it didn't crash the whole batch run, but it silently
skipped that file's entire analysis and printed a misleading error that
looked like the *playbook* was missing rather than the *gitleaks binary*.
Now caught explicitly with a message pointing at the real fix (run
`Install_Gitleaks.py` or check `GITLEAKS_PATH`). Verified against all three
paths: missing binary (now fails gracefully), bad target (unaffected),
successful scan with real findings (unaffected).

### `Install_Gitleaks.py`
**Role:** Detects OS/architecture, downloads the matching `gitleaks`
release tarball/zip from GitHub, extracts it, `chmod`s it executable.
**Status:** ✅ fixed — ARM64 branch, version constant wiring, asset
filename format. **Independently re-verified this session** against the
real `v8.30.1` GitHub release listing — asset names
(`gitleaks_8.30.1_linux_x64.tar.gz`, `_darwin_arm64.tar.gz`, etc.) match
this file's `get_gitleaks_download_url()` exactly. No bug found.

### `Ansible_Lint.py`
**Status:** ⚪ reviewed, no bug found (per `ARCHITECTURE.md`). Not
re-tested this session against a missing-binary scenario the way
`GitLeaks_hardcoded_credentials.py` was — still an open item per
`REFACTOR_PLAN.md` Part 5 #8 if `ansible-lint` isn't guaranteed installed
on a fresh clone.

---

## Output writers

### `write_to_csv.py`
**Role:** `write_results_to_csv()` — flattens `playbook.metrics` from every
analyzed file into one row per playbook in `IaC_Smells.csv`, one column per
smell. Almost 200 lines of commented-out per-play/per-task row logic sit
unused below the live function — dead code, not a bug.
**Status:** ✅ fixed — the `None`-vs-blank regression that `sem_cohesion
.py`'s OOV fix introduced (a `None` similarity score needed to render as a
blank cell, not the literal string `"None"`); also an `ansible_lint_issues`
consistency gap (0 real issues vs. lint-tool failure both previously
rendered identically as blank).

### `write_to_text.py`
**Role:** Four independent writer functions for the four `.txt`-style
outputs: `write_AnsibleLint_results_to_txt`, `write_GitLeaks_results_to_txt`
(actually writes JSON despite the name), `write_unused_vars_to_txt`,
`write_duplicates_to_txt`, plus `write_results_to_txt` for the main
play/task smell breakdown.
**Status:** ✅ fixed — the "Global" tasks group (tasks outside any play)
was being printed with no header, visually indistinguishable from
belonging to the preceding play; confirmed misleading via `main3.yml`'s
regression run. **Fragility documented, not fixed:** `write_duplicates_to_txt`
opens its output file in **append** mode (`"a"`) while every other writer
in this file uses **write** mode (`"w"`/`"a"` inconsistently across
functions) — the three writer functions that share `Play_Level_Analysis
.txt` depend on being called in an unstated, specific order by
`smellsDetector.py`. Reordering those calls would silently corrupt or
duplicate sections of that file.

---

## Summary of bugs found and fixed this session

| File | Bug | Severity |
|---|---|---|
| `overriden_keys.py` | Cross-depth key collapse caused false-positive duplicate-key reports (a task's own `name:` merged with a nested module's `name:` param) | Medium — false positives on common real playbooks |
| `GitLeaks_hardcoded_credentials.py` | Unguarded `FileNotFoundError` crash when the `gitleaks` binary path is wrong/missing, with a misleading error message | Medium — silently skips a file's whole analysis with a confusing error |
| `credentials_leaking_in_log.py` | Only scanned tasks with no play wrapper at all; every task inside a real `hosts:`/`tasks:` play was invisible to the no-log/credential check | **High — silently misses the overwhelming majority of real-world cases for the pipeline's most security-relevant check** |
| `incohesive_plays.py` | Plays whose task names are all non-English/out-of-vocabulary were reported as "perfectly cohesive" instead of "unmeasurable," mirroring a bug already fixed in the sibling `sem_cohesion.py` | Medium — false negative specifically for non-English playbooks |

All four are fixed, tested against multiple fixtures each (including
regression checks against previously-working behavior), and the fixed
files are in this conversation's outputs.
