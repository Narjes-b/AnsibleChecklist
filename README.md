# AnsibleChecklist

A static-analysis tool for Ansible playbooks. It scans `.yml`/`.yaml` files
for Infrastructure-as-Code smells (large playbooks/plays/tasks, unnamed
plays/tasks, duplicate keys, unused `set_fact`, missing boolean filters,
credential leaks, hardcoded secrets via GitLeaks, and `ansible-lint`
findings) and writes the results out as CSV, TXT, and JSON reports.

This README replaces the previous one. It folds in a full debugging pass
that took the pipeline from "crashes on import" to a working, tested,
end-to-end tool, and documents exactly what changed, how the pipeline is
wired together, and how to verify it still works after future edits.

---

## 1. Setup (fresh machine)

```bash
cd AnsibleGuard
pip install -r requirements.txt --break-system-packages   # or inside a venv
python3 -c "import nltk; nltk.download('wordnet'); nltk.download('omw-1.4')"
python3 -c "from Install_Gitleaks import ensure_gitleaks_installed; ensure_gitleaks_installed()"
./gitleaks-bin/gitleaks version   # sanity check — should print a version string
```

Confirm paths resolve correctly:

```bash
python3 -c "from config import TEST_PLAYBOOK, THRESHOLDS_FILE, yaml_files_folder, RESULTS_DIR; print(TEST_PLAYBOOK.exists(), THRESHOLDS_FILE.exists(), yaml_files_folder.exists(), RESULTS_DIR.exists())"
# expect: True True True True
```

> **Note:** everything must run from inside `AnsibleGuard/`, not the repo
> root — internal imports are bare (`from config import ...`) and only
> resolve when `AnsibleGuard/` is the working directory. This is a known
> structural limitation, see [§6](#6-known-issues--next-steps).

## 2. Running it

```bash
cd AnsibleGuard
python3 smellsDetector.py
```

This batch-processes every `.yml`/`.yaml` file in `config.yaml_files_folder`
(currently `TestData/tasks/`) and writes one results folder per file to
`TestData/Results/<file_stem>/`:

| Output file | Contents |
|---|---|
| `IaC_Smells.csv` | one-row summary per playbook |
| `Play_Level_Analysis.txt` | human-readable per-play/per-task smell report |
| `Technical_Analysis.json` | raw metrics, before threshold evaluation |
| `ansiblelint.txt` | `ansible-lint` output |
| `gitleaks.txt` | GitLeaks output |

## 3. Pipeline architecture

```
smellsDetector.py  (run this)
  │
  ├── config.py                     # all paths — check first if a file can't be found
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
  │     ├── sem_cohesion.py              (playbook-level similarity, spaCy)
  │     ├── incohesive_plays.py          (play-level similarity, spaCy)
  │     │     └── detect_large_play.py
  │     ├── duplicate_task_Name.py       (→ detect_large_task.py)
  │     ├── files_extensions.py
  │     ├── filters_for_comparison.py
  │     ├── credentials_leaking_in_log.py (→ detect_large_task.py)
  │     └── include_vars.py              (→ write_to_text.write_unused_vars_to_txt)
  │
  ├── assess_code_smells()  [inside smellsDetector.py]
  │     — takes parser_playbook's raw metrics + thresholds.csv,
  │       decides which smells actually fire
  │     ├── GitLeaks_hardcoded_credentials.py  (→ Install_Gitleaks.py for the binary)
  │     └── Ansible_Lint.py
  │
  └── write_to_csv.py / write_to_text.py   — final report output
```

**Dead code — nothing imports these, edits here won't affect the tool:**
`parser_playbook_mod.py`, `parser_playbook.ipynb`, `GeneralsmellsDetector.py`
(stale fork of `smellsDetector.py`), `exceptions.py` (empty).

**Data flow, one line per stage:**
1. `detect_large_task.py` / `detect_large_play.py` / `detect_large_playbook.py`
   read the YAML and produce raw counts (LOC, task counts, names) — no
   threshold logic yet.
2. `parser_playbook.py`'s `mainn()` calls every detector and assembles one
   `main_metrics` dict per playbook — still no pass/fail decisions.
3. `smellsDetector.py`'s `assess_code_smells()` takes that dict, loads
   `thresholds.csv`, and decides which smells actually fire.
4. `write_to_csv.py` / `write_to_text.py` render the decisions to disk.

If a number looks wrong: check `Technical_Analysis.json` first (stage 2's
raw output). If it's already wrong there, the bug is in a `detect_large_*.py`
file. If the raw number is right but the CSV flag is wrong, the bug is in
`smellsDetector.py`'s threshold logic instead.

## 4. What changed in this pass

The tool didn't run at all at the start of this pass — a chain of
unguarded module-level test code and hardcoded `/Users/narjes/...` paths
crashed on plain `import`. It's now a working, spot-checked, end-to-end
pipeline. Full detail in the sections below; short version:

**New file:** `main.py` (repo root) — a real CLI entry point wrapping
`smellsDetector.py`'s per-file logic. Accepts a single file, a folder, or
defaults to `config.yaml_files_folder`.

**Crash-on-import fixed (11 files):** `config.py` (rebuilt around portable
`BASE_DIR`/`PROJECT_ROOT`), `detect_large_task.py`, `detect_large_play.py`,
`detect_large_playbook.py`, `duplicate_task_Name.py`,
`credentials_leaking_in_log.py`, `unnamed_tasks.py`, `unnamed_play.py`,
`set_fact.py`, `overriding_facts.py`, `incohesive_plays.py`,
`parser_playbook.py`.

**Silent wrong-output bugs fixed:**
- `duplicate_task_Name.py` — tuple-unpacking bug meant `repeated_task_names()`
  always returned `0`.
- `credentials_leaking_in_log.py` — was reading the (almost always empty)
  `top_level_tasks` list instead of the full metrics list, silently finding
  zero leaks on any normal file.
- `detect_large_play.py` vs `detect_large_task.py` — disagreed on whether a
  `block:` wrapper counts as one task or should be recursed into, so
  `play_metrics` and `task_metrics` described two different task sets for
  the same play. Fixed by making both recurse into `block`/`rescue`/`always`
  the same way.
- **Root-cause data integrity bug** in `detect_large_task.py`:
  `calculate_metrics_task()` included `"block" in entry` when deciding play
  boundaries; `detect_large_play.py`'s equivalent check did not. Any
  top-level task-with-a-block caused the two functions' play numbering to
  drift apart, silently pairing each real play with a *different* play's
  tasks throughout the pipeline. Fixed by removing that clause so both
  functions agree.
- `smellsDetector.py` — 8 separate bugs: `RESYULTS_DIR` import typo;
  unassigned `play_metrics_dict` (`NameError`); `findings`/`lint_results`
  not initialized before `try:` (masked real errors); `num_large_task=+1`
  (assignment, not increment) fixed to `+=`; `is_large_play` per-play flag
  overwritten with the running playbook-wide count; `large_play`/
  `unnamed_play` counters reset to `0` on the trailing "Global tasks" group,
  wiping earlier plays' counts; threshold key mismatches (`num_tasks_in_play`
  vs `num_tasks_play`, `num_tasks_playbook` vs `num_nested_tasks_playbook`,
  `Num_Roles` case); hardcoded `/Users/narjes/.../Results` path.
- `unecessary_abs.py` — crashed on empty/`None` YAML; never recursed into a
  block nested inside another block; unsafe `yaml.load` → `yaml.safe_load`.
  Detection extended into `rescue`/`always`.
- `sem_cohesion.py` — crashed on non-dict list items; `encoding='latin1'` →
  `utf-8` (was corrupting non-ASCII names before similarity comparison);
  unsafe `yaml.load` → `yaml.safe_load`; task-name collection now recurses
  into `block`/`rescue`/`always`.
- `Install_Gitleaks.py` — no ARM64 Linux branch; disconnected default
  version parameter; renamed release asset tags between GitLeaks versions.
  Pinned version, fixed URLs.
- `is_unamed.py` — only treated `None` as unnamed, not empty/whitespace;
  now matches `unnamed_play.py`.

**Removed:** `parser_playbook_mod.py`, `parser_playbook.ipynb` — both
imported a nonexistent `CodeSmellsTool` package and used hardcoded Windows
paths; nothing else in the codebase imported either file.

**Environment fixes:** two invalid `requirements.txt` lines identified
(`pytest=9.1.1`, duplicate `requests=2.34.2`); NLTK corpus data documented
as a required setup step (`wordnet`, `omw-1.4`), needed by `sem_cohesion.py`
and `incohesive_plays.py`.

Full file-by-file fix table and root-cause explanations: see
`PROJECT_STATUS.md`.

## 5. Testing

Run this full regression check after any change — the pipeline is tightly
coupled, and bugs in one file have silently corrupted another file's output
more than once.

**Step 1 — environment sanity**
```bash
cd AnsibleGuard
python3 -c "from config import TEST_PLAYBOOK, THRESHOLDS_FILE, yaml_files_folder, RESULTS_DIR; print(TEST_PLAYBOOK.exists(), THRESHOLDS_FILE.exists(), yaml_files_folder.exists(), RESULTS_DIR.exists())"
./gitleaks-bin/gitleaks version
```

**Step 2 — import check, every module, no crashes**
```bash
for f in detect_large_task detect_large_play detect_large_playbook \
         duplicate_task_Name credentials_leaking_in_log unnamed_tasks \
         unnamed_play set_fact overriding_facts incohesive_plays \
         parser_playbook smellsDetector is_unamed high_coupling \
         duplicate_code files_extensions filters_for_comparison \
         overriden_keys include_vars unecessary_abs sem_cohesion \
         write_to_csv write_to_text Ansible_Lint Install_Gitleaks; do
  echo -n "$f: "
  python3 -c "import $f" 2>&1 | tail -1 || echo "OK"
done
```
Any output other than a blank "OK" line marks an unresolved import bug.

**Step 3 — full pipeline run**
```bash
python3 smellsDetector.py
```
Should process every file in `TestData/tasks/` with no traceback and
produce all 5 output files per fixture.

**Step 4 — data-correctness spot check (the part crash tests can't catch)**
`main3.yml` is the richest fixture (real plays, top-level block-tasks,
duplicate keys, unused `include_vars`, a hardcoded secret):
```bash
cat TestData/Results/main3/Technical_Analysis.json
cat TestData/Results/main3/IaC_Smells.csv
```
Read these against the actual `main3.yml` and `thresholds.csv` by hand —
confirm each play's `task_metrics` really belongs to that play, and that
each CSV smell flag matches the raw JSON numbers against the real threshold
values. This is how the four silent wrong-output bugs above were caught;
"doesn't crash" is not the same as "produces correct data."

**Step 5 — isolated fixture tests** (fast feedback for a single detector)
```bash
cat > /tmp/dupe_test.yml << 'EOF'
- name: Install package
  apt: {name: nginx}
- name: Install package
  apt: {name: curl}
EOF
python3 -c "from duplicate_task_Name import repeated_task_names; print(repeated_task_names('/tmp/dupe_test.yml'))"
# expect: 1
```

**Definition of done:** Step 2 clean, Step 3 no tracebacks, Step 4 every
number in the CSV traceable to `Technical_Analysis.json` and matched by hand
against `thresholds.csv`.

## 6. Known issues / next steps

- `smellsDetector.py`: `large_task`, `long_task_name`, and
  `inconsistent_naming_convention` playbook-level counters are recomputed at
  the top of *each* play's task loop and overwritten every iteration — final
  CSV reflects only the last play processed. Same bug shape as the already-
  fixed `large_play` reset, not yet applied here.
- A task with heavy `overriden_keys`-style duplication under-reports its own
  size in LOC-based metrics, because `yaml.safe_load()` silently collapses
  duplicate keys before `detect_large_task.py` sees the task (confirmed on
  `main3.yml`'s `task8`: real span ~37 lines, reported `LOC_task`: 12).
- Threshold comparisons are strict `>` everywhere, not `>=` — an implicit
  decision that should be stated explicitly.
- `include_vars.py`'s "used variable" regex misses `{{var_name}}` (no
  spaces) and `{{ var_name | default(...) }}` — a looser regex
  (`var_usage_pattern`) is already defined but unused.
- `sem_cohesion.py` and `incohesive_plays.py` each independently load
  `en_core_web_lg` at import time — real startup cost, not centralized.
- `config.py`'s `varsfiles_folder` is `None` — no `include_vars:` + `vars/`
  fixture exists yet, so unused-vars detection is untested against real data.
- `exceptions.py` is empty despite being described in `explanation.md`.
- `GeneralsmellsDetector.py` — stale fork with the pre-fix `is_large_play`
  bug, nothing imports it. Decide: delete, or mark deprecated.
- No real Python package structure — every file uses bare
  `from config import ...`, only resolving when `AnsibleGuard/` is the
  working directory. A proper package would remove this constraint.
- `main.py`'s folder-scan is non-recursive (`glob`, not `rglob`) — won't
  find playbooks nested under `roles/*/tasks/main.yml` in a real project.
- No permanent `pytest` suite yet — the throwaway fixtures built during this
  pass (empty files, nested blocks, malformed YAML, duplicate names, etc.)
  should become regression tests.
- `thresholds.csv` values are inherited from OOP-smell literature or picked
  by feel, not empirically calibrated against a real playbook corpus.

Full root-cause detail and the threshold key-name mapping table:
`PROJECT_STATUS.md`.
