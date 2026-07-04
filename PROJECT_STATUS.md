# AnsibleChecklist — Debugging Status

## What this project does
Analyzes Ansible playbooks for IaC code smells (large playbooks/plays/tasks,
unnamed plays/tasks, duplicate keys, unused `set_fact`, missing bool filters,
credential leaks, hardcoded secrets via GitLeaks, and `ansible-lint` issues),
then writes results to CSV, TXT, and JSON reports.

## How to run it
Everything must be run from inside `AnsibleGuard/`, not the repo root —
internal imports are bare (`from config import ...`) and only resolve when
`AnsibleGuard/` is the working directory.

```bash
cd AnsibleGuard
python smellsDetector.py
```

This batch-processes every `.yml`/`.yaml` file in `config.yaml_files_folder`
(currently `TestData/tasks/`) and writes results to
`TestData/Results/<file_stem>/`:
- `IaC_Smells.csv` — one-row summary per playbook
- `Play_Level_Analysis.txt` — human-readable per-play/per-task smell report
- `Technical_Analysis.json` — raw metrics before threshold evaluation
- `ansiblelint.txt`, `gitleaks.txt` — external tool output

## Setup checklist (fresh machine)
1. `pip install -r requirements.txt --break-system-packages` (or in a venv)
   — note: `requirements.txt` currently has two invalid lines
   (`requests=2.34.2` duplicate, `pytest=9.1.1`) that will make `pip install`
   fail; not yet fixed.
2. Install GitLeaks: `python -c "from Install_Gitleaks import ensure_gitleaks_installed; ensure_gitleaks_installed()"`
   then verify with `./gitleaks-bin/gitleaks version`.
3. Confirm `config.py` paths resolve:
   ```bash
   python -c "from config import TEST_PLAYBOOK, THRESHOLDS_FILE, yaml_files_folder, RESULTS_DIR; print(TEST_PLAYBOOK.exists(), THRESHOLDS_FILE.exists(), yaml_files_folder.exists(), RESULTS_DIR.exists())"
   ```
   All four should print `True`.

## How we've been testing each module
Two-step check per file, used throughout this debugging pass:
```bash
python -c "import <module_name>"   # should be silent — catches unguarded module-level code
python <module_name>.py            # runs its own __main__ block against config.TEST_PLAYBOOK
```
For logic bugs (not just crashes), we built small throwaway fixture YAMLs
(e.g. two tasks with identical names, a task with a `password` field with/without
`no_log: true`) and called the function directly to confirm correct output —
not just "doesn't crash."

`TestData/tasks/main3.yml` is the most useful fixture we have: it has real
plays (`hosts:`/`tasks:`), top-level tasks-with-blocks, duplicate keys, an
unused `include_vars`, and a hardcoded credential — good coverage for a
regression check after any change to `smellsDetector.py` or the `detect_large_*`
modules.

## Threshold key names — the confirmed mapping
This mismatch caused several silent bugs (checks always defaulting to a
threshold of 0). Confirmed against the real `thresholds.csv` and the actual
metric-producing functions:

| thresholds.csv column | metric field it should compare against | produced by |
|---|---|---|
| `LOC_playbook` | `LOC_playbook` | `detect_large_playbook.py` |
| `num_plays` | `num_plays` | `detect_large_playbook.py` |
| `avg_play_size` | `avg_play_size` | `detect_large_playbook.py` |
| `num_tasks_playbook` | `num_nested_tasks_playbook` | `detect_large_playbook.py` |
| `avg_task_playbook` | *(not currently checked anywhere — see Known Issues)* | — |
| `Num_Imports` | `Num_Imports` | `high_coupling.py` |
| `Num_Roles` | `Num_Roles` | `high_coupling.py` |
| `LOC_play` | `LOC_play` | `detect_large_play.py` |
| `num_tasks_play` | `num_tasks_in_play` | `detect_large_play.py` |
| `avg_task_play` | `avg_task_play` | `detect_large_play.py` |
| `LOC_task` | `LOC_task` | `detect_large_task.py` |
| `task_name_len` | `task_name_len` | `detect_large_task.py` |
| `special_chars` | `special_chars` | `detect_large_task.py` / `detect_large_play.py` |

## Fixed so far

### Import-crash cascade (11 files)
Root cause: unguarded module-level test code (`metrics = calculate_metrics_task(hardcoded_path)`
running on plain `import`, not inside `if __name__ == "__main__":`), plus
hardcoded `/Users/narjes/...` paths from the original author's machine.
Fixed in: `detect_large_task.py`, `detect_large_play.py`, `detect_large_playbook.py`,
`duplicate_task_Name.py`, `credentials_leaking_in_log.py`, `unnamed_tasks.py`,
`unnamed_play.py`, `set_fact.py`, `overriding_facts.py`, `incohesive_plays.py`,
`parser_playbook.py`.

### `config.py`
Rebuilt around `BASE_DIR`/`PROJECT_ROOT` (`Path(__file__).resolve().parent` and
`.parent`), all fixture and output paths made portable. `varsfiles_folder` is
currently `None` — no matching sample data exists yet (see Known Issues).

### `duplicate_task_Name.py`
`calculate_metrics_task()` returns a tuple `(all_metrics, top_level_tasks)`; this
file was assigning the whole tuple to one variable instead of unpacking it,
so `repeated_task_names()` always returned `0`. Fixed.

### `Install_Gitleaks.py`
Three separate bugs found while getting GitLeaks working:
1. No ARM64 Linux branch (`platform.machine()` never checked — always built
   an `amd64` URL, "exec format error" on ARM64 machines).
2. `get_gitleaks_download_url()`'s default parameter (`"8.18.1"`) was a second,
   disconnected copy of `GITLEAKS_VERSION` — bumping the module constant did
   nothing.
3. GitLeaks renamed release asset tags between versions (`amd64` → `x64`).
   Pinned `GITLEAKS_VERSION = "8.30.1"` and updated tag names to match
   confirmed-real assets for that version.

### `smellsDetector.py` — several bugs
- `RESYULTS_DIR` typo in the `config` import (blocked everything).
- `play_metrics_dict` referenced but never assigned (`NameError`).
- `findings`/`lint_results` not initialized before `try:` — a real error
  inside `assess_code_smells()` was being masked by a second crash
  (`UnboundLocalError`) in the `except` block's own `return` statement.
- `num_large_task=+1` — parsed as "assign +1", not "increment by 1"; fixed to `+=`.
- `large_task`/`long_task_name`/`inconsistent_naming_convention` playbook-level
  counters (`num_large_task`, `task_name`, `naming_convention`) were reset to
  `0` at the top of *each* play's task loop and the playbook-level result got
  overwritten every iteration — same bug shape as the `large_play` reset bug
  above, just in the task-level block. Final CSV value was only ever the last
  play processed, not the true playbook-wide total. Fixed the same way:
  initialize all three counters once before the per-play loop, accumulate
  across every play, write the result to `result["playbook"]["metrics"]`
  exactly once after the loop completes.
- `is_unamed.py`'s `is_unnamed()` only treated `None` as unnamed, not an
  empty/whitespace string, inconsistent with `unnamed_play.py`. Fixed to also
  catch `isinstance(play_name, str) and not play_name.strip()`.
- `unnamed_play.py`'s play-detection condition used
  `"hosts" in item and "tasks" in item` (AND) while every other
  play-detection function in the codebase uses OR — undercounted plays that
  had only one of the two keys. Fixed to `"hosts" in item or "tasks" in
  item`. Confirmed via fixture: a `tasks:`-only play with no name previously
  went undetected (`0`), now correctly reports `1`.
- `is_large_play` — per-play flag was being overwritten immediately after being
  set correctly, with the running playbook-wide count (so every play showed
  the total instead of its own true/false).
- `large_play`/`unnamed_play` playbook-level counters reset to `0` whenever a
  trailing "Global tasks" group (tasks outside any play) was processed —
  always wiped the accumulated count from real plays. Fixed by initializing
  once before the loop and never touching the counters in the "Global" branch.
- Threshold key mismatches: `num_tasks_in_play` vs `num_tasks_play`,
  `num_tasks_playbook` (doesn't exist) vs `num_nested_tasks_playbook`,
  `Num_Roles` vs `num_roles` case mismatch. See mapping table above.

### `detect_large_task.py` — root-cause data integrity bug
`calculate_metrics_task()`'s play-boundary detection included `"block" in entry`
as a condition for incrementing `play_id`; `detect_large_play.py`'s equivalent
check does not. Any top-level task-with-a-block (not a real play) caused the
two functions' `play_id` numbering to drift apart, silently pairing every real
play with a *different* play's tasks throughout the whole pipeline. This was
likely corrupting every task-level smell result for any playbook mixing plays
with top-level block-tasks. Fixed by removing the `"block" in entry` clause so
both functions agree on what counts as a play.

### `detect_large_play.py` — block-recursion mismatch with `detect_large_task.py`
Separate bug, found later: `compter_tasks_dans_play()` never recursed into
`block:` at all — it counted a block wrapper as one task using the wrapper's
own name (e.g. a task named `Notconsideredtask3` wrapping real tasks
`task4`/`task5`), while `detect_large_task.py` correctly recursed into the
block and only recorded the real children. Same play, two files, completely
disjoint task data (confirmed on `main3.yml`: `play_metrics` said play1 had 2
tasks named `Notconsideredtask3`/`Notconsideredtask4`; `task_metrics` for the
same play showed 3 different tasks, `task4`/`task5`/`task6`, zero overlap).
This corrupted `num_tasks_in_play` (undercounted, affecting the `Large Play`
threshold check) and `incohesive_plays.py`'s cohesion scoring (compared
generic wrapper labels instead of real task names for any block-using play).
Fixed by making `detect_large_play.py` recurse into `block`/`rescue`/`always`
the same way `detect_large_task.py` does. `incohesive_plays.py` needed no
changes — it's a pure consumer and now gets correct data automatically.

### `files_extensions.py`
Two bugs. First, `recurse_extract()` only recursed into `block:`, silently
skipping any task inside `rescue:`/`always:` — inconsistent with
`detect_large_task.py`'s convention, meaning error-handling tasks were
invisible to the file-extension check entirely. Second, once `rescue`/
`always` recursion was added, an early version of the fix placed the
"append this task if it has no nested section" check *inside* the
per-section loop instead of evaluating it once per task — this caused plain
tasks (no block at all) to be appended 3 times (once per section checked),
tripling their contribution to the final count. Confirmed via a fixture with
one task missing a file extension: buggy version reported `3`, fixed version
correctly reports `1`.

### `filters_for_comparison.py`
Real crash, not just a gap: `when: true` (or `yes`/`1`, any unquoted
YAML-native boolean) parses via `yaml.safe_load()` as a Python `bool`, not a
string. `check_missing_bool_filter()` passes this straight into
`re.search(pattern, condition_str, ...)`, which requires a string — raising
`TypeError: expected string or bytes-like object, got 'bool'` on any
playbook using an unquoted boolean `when:` condition, which is extremely
common in real Ansible. Fixed by wrapping the value in `str()` before passing
it to the regex check. Also had the same missing `rescue`/`always` recursion
bug as `files_extensions.py`; fixed the same way.

### `high_coupling.py`
Two separate issues, one already partially fixed in an earlier round
(`KeyError` on singular `role:` — confirmed fixed and non-regressing this
round). The new finding: `import_tasks`/`include_tasks` detection only
checked keys directly on each top-level play dict — but in real Ansible,
these almost always appear as individual entries *inside* a play's `tasks:`
list (`- hosts: all` / `tasks:` / `- import_tasks: common.yml`), not as a key
on the play itself. Only the rare task-only role file (where `import_tasks:`
appears as a bare top-level list item, no `hosts:`/`tasks:` wrapper) was
being caught — the far more common form was silently invisible, undercounting
`Num_Imports` on essentially any real playbook. Confirmed via fixture: before
the fix, a play with 2 nested `import_tasks`/`include_tasks` entries reported
`Num_Imports: 0`; after the fix, correctly reports `2`. Fixed by recursively
walking `play['tasks']` (including into `block`/`rescue`/`always`) looking
for these keys per-task, not just per-play. Also confirmed, while
investigating: dict-style `roles:` entries (`roles: [{role: x, vars: {...}}]`)
were never actually broken — `len(roles)` counts list items correctly
regardless of whether they're strings or dicts. This had been flagged as a
suspected untested risk in an earlier round; testing it directly showed it
was already correct, so no fix was needed there.

### Multi-document YAML and Ansible Vault handling
Investigated empirically (not guessed) against real `yaml.safe_load()`
behavior, since this was flagged as untested in an earlier round. Four
distinct cases, three different outcomes:

1. **Multi-document files** (`---` separators between documents) — raises
   `yaml.ComposerError`, a `YAMLError` subclass. Any function wrapped in
   `except yaml.YAMLError`/`except Exception` degrades gracefully (prints a
   message, returns `None`); `smellsDetector.py`'s outer
   `execute_for_single_file` try/except catches anything not caught closer to
   the source, so one bad file doesn't crash the whole batch. **Not a crash**,
   but a real coverage gap worth knowing about.
2. **Inline `!vault |` tags** on individual variables (a common, recommended
   real-world pattern for per-variable secrets) — raises
   `yaml.ConstructorError`, also a `YAMLError` subclass, same graceful
   degradation as above. **Not a crash**, but means any playbook using this
   pattern gets its *entire* analysis silently skipped — exactly the kind of
   file you'd most want smell detection on (e.g. checking for `no_log:` near
   a vaulted secret).
3. **Fully vault-encrypted files** (whole file is
   `$ANSIBLE_VAULT;1.1;AES256` + ciphertext, no surrounding YAML structure)
   — this is the dangerous one. It's not invalid YAML syntax, so
   `yaml.safe_load()` doesn't raise at all — it silently parses the whole
   thing into a single Python **string** (not a list, not an error). That
   string then behaves differently depending on which detector receives it:
   - `detect_large_task.py`'s `calculate_metrics_task()` — **confirmed real
     crash**: `UnboundLocalError: cannot access local variable
     'top_level_tasks'`. The `isinstance(playbook, list)` guard skips the
     whole function body (a string isn't a list), so `top_level_tasks` is
     never defined before the `return` statement needs it. Fixed by
     initializing `top_level_tasks = []` before the `isinstance` check.
   - `high_coupling.py` — **no crash, but silently wrong**: had no type
     guard at all, so `for play in playbook:` iterated the string
     *character by character*, every `in` check trivially failed, and it
     confidently returned `{'Num_Imports': 0, 'Num_Roles': 0}` — reporting
     "no coupling issues" for a file it never actually read. Fixed by adding
     the same `if not playbook or not isinstance(playbook, list): return
     None` guard `detect_large_play.py` already had.
   - `detect_large_play.py` — already correct, already had this exact guard.
     Good pattern to standardize on; several other detectors that iterate
     `for play in playbook:` without first checking `isinstance(playbook,
     list)` may have the same latent risk and haven't been individually
     re-verified against this specific input yet.

### Non-English playbooks — `sem_cohesion.py`
Investigated empirically. Since the real `en_core_web_lg` model couldn't be
downloaded in the sandbox used for part of this investigation (network
restriction unrelated to the code itself), the finding was first proven
using `spacy.blank('en')` (identical `has_vector=False` code path to any
out-of-vocabulary input), then independently confirmed against the real
model with actual Arabic task names, both producing the same result. The
bug: `average_similarity = 1` (the "nothing to compare" fallback) fires
identically whether a playbook has too few names to form any pair *or*
every name is outside the model's vocabulary (non-English, or otherwise
unrecognized) — collapsing "too small to judge" and "language not
supported" into the same falsely-reassuring "perfectly cohesive" result.
This is worse than a crash: an incohesive non-English playbook — exactly
what `incohesive_plays.py` exists to catch — would score as the *best*
possible result instead of being flagged as unmeasurable. Fixed by tracking
how many names actually had a usable vector; if there were 2+ names but zero
had vectors, return `None` (with a printed warning) instead of `1`. This in
turn required a follow-on fix in `smellsDetector.py`'s `incohesive_playbook`
threshold check, which previously did `metrics.get("similarity", 0) <
threshold` — `.get(key, 0)` only defaults when the key is *missing*, not
when it's present with value `None`, so comparing `None < float` would have
raised a `TypeError` the first time this code path was hit for real. Fixed
by checking for `None` explicitly before comparing, setting
`incohesive_playbook` to `None` (propagated correctly) rather than crashing
or guessing.

### `write_to_csv.py`
Reviewed against `smellsDetector.py`'s actual output shape — structurally
sound (every field name checked and matched correctly), but two issues
found. First, a regression from the `sem_cohesion.py` fix above: since
`incohesive_playbook` can now be explicitly `None`, `.get('incohesive_playbook',
'')` doesn't catch it (that default only applies to a *missing* key) — the
CSV would have literally shown the string `"None"` in that cell instead of
blank. Fixed by checking `is not None` explicitly, careful to preserve a
legitimate `0` value (a naive `value or ''` would have wrongly blanked `0`
too, since `0` is falsy in Python). Second, unrelated: `ansible_lint_issues`
was only ever set inside `if lint_results:` in `smellsDetector.py` — meaning
"0 real lint issues" and "ansible-lint failed to run at all" both rendered
as an identical blank cell in the CSV, with no way to distinguish them.
Fixed by setting it unconditionally
(`len(lint_results) if lint_results else 0`). Not a bug, but noted: the large
commented-out per-play/per-task writer block actually targets the *correct*
schema that `smellsDetector.py` produces — just dead code, safe to leave or
delete.

### `write_to_text.py`
Reviewed, no bugs found. The three-writer file-mode chain
(`write_unused_vars_to_txt` truncates with `'w'`, then
`write_duplicates_to_txt` and `write_results_to_txt` both append with `'a'`)
is correct and already verified against real output on `main3.yml` earlier
in this process — but it's fragile: correctness depends entirely on an
unstated call order across two different files. If the three calls in
`smellsDetector.py` are ever reordered, the `'w'`-mode call would silently
wipe out anything written before it. Worth documenting explicitly or
restructuring into a single orchestrating function later; not urgent since
it currently works.

### `overriden_keys.py` — cross-depth false positive
The depth-tracking fix (grouping by `(depth, key)` to stop a task's own
`name:` from being confused with a nested module parameter also called
`name:`, e.g. `apt: {name: nginx}`) was implemented correctly during
collection, but a later line collapsed `(depth, key)` back down to a plain
key name *before* checking for duplicates — silently discarding the very
distinction it had just made. Confirmed via fixture: a task with only
`- name: task4` / `apt: {name: nginx, state: present}` (no real duplicate
anywhere) was reported as having a duplicated `name:` key. Fixed by
deciding duplication within each `(depth, key)` bucket first, and only
collapsing to a plain key name for the report after that check passes.
Verified against 4 fixtures (the original 3 plus a mixed case combining a
real duplicate and a cross-depth `name:` collision in the same file) and
against the real `main3.yml`.

### `GitLeaks_hardcoded_credentials.py` — unguarded crash on missing binary
A nonexistent playbook path was already handled gracefully (real GitLeaks
exits non-zero on a bad `--source`; the `else` branch already returned
`[]`). A missing or misconfigured `gitleaks` binary path, however, raised
an unguarded `FileNotFoundError` from `subprocess.run()` with no matching
`except`. It doesn't crash the whole batch run — `execute_for_single_file`'s
outer `try/except` catches it — but it silently skips that file's entire
analysis and prints a misleading message that reads as if the *playbook*
is missing rather than the *gitleaks binary*. Fixed by catching
`FileNotFoundError` at the source and printing a message that actually
points at the fix (`Install_Gitleaks.py` / check `GITLEAKS_PATH`). Verified
against all three paths: missing binary (now fails gracefully with a clear
message), bad target path (unaffected, still returns `[]`), successful
scan with real findings (unaffected).

### `credentials_leaking_in_log.py` — scope bug, most severe finding this round
This function sourced its raw task dicts from `detect_large_task.py`'s
`top_level_tasks` return value — which, by that function's own design,
contains *only* the tasks with no `hosts:`/`tasks:` wrapper at all (the
`play_id=-1` "Global" group). Every task living inside a normal
`- hosts: ... tasks: [...]` play — the overwhelming majority of real
Ansible content, including the exact "Set AWS secret key (bad practice!)"
example already present in `main3.yml` — was completely invisible to this
check. Confirmed live: a `main3.yml`-shaped fixture containing that exact
secret task returned `nbLeaks: 0`. This means the credential-leak check,
arguably the single most security-relevant smell this tool detects, has
likely been silently reporting near-zero findings on every real playbook
run through it so far, regardless of actual content. Fixed by replacing
the `top_level_tasks` dependency with a self-contained recursive collector
(same traversal pattern as `files_extensions.py`) that gathers every real
task's raw dict regardless of nesting depth. Verified against 4 cases:
secret nested inside a play (now caught), a mix of one top-level and one
nested secret (both caught), a task with `no_log: true` (correctly still
not flagged), and a secret nested inside `block:` (still caught).

### `incohesive_plays.py` — same OOV bug as `sem_cohesion.py`, missed in the earlier pass
Carries the exact "falsely perfectly cohesive" bug already found and fixed
in `sem_cohesion.py`: `average_similarity = 1` fires identically whether a
play genuinely has too few task names to compare, or every task name is
outside the model's vocabulary (non-English or otherwise OOV) — collapsing
"nothing to judge" and "language not supported" into the same falsely
reassuring result. This is a *separate* bug from the block-recursion issue
that was checked and cleared for this file earlier (see the
`detect_large_play.py` entry above, "`incohesive_plays.py` needed no
changes"); that clearance was correct for block-recursion specifically but
didn't cover this. Confirmed via isolated logic test (mocking
`doc.has_vector = False`, since the real `en_core_web_lg` model wasn't
downloadable in this session's sandbox). Fixed the same way as
`sem_cohesion.py`: track how many task names in the play actually had a
usable vector; if 2+ names exist but none had a vector, skip the play
(count toward neither cohesive nor incohesive) rather than assuming
cohesive. Unlike `sem_cohesion.py`, this function only ever returns a
plain integer count (not the raw similarity score), so no follow-on
`None`-handling fix was needed in `smellsDetector.py` or `write_to_csv.py`
this time.

## Known issues / not yet fixed

1. **`requirements.txt`**: `requests=2.34.2` (duplicate, invalid `=` instead
   of `==`) and `pytest=9.1.1` (same) — `pip install -r requirements.txt`
   will fail on these two lines.
2. **`varsfiles_folder`** in `config.py` is `None` — no sample data with a
   real `include_vars:` + `vars/` folder exists in `TestData/` yet, so
   `include_vars.py`'s unused-vars detection is untested against real data.
3. **`avg_task_playbook`** threshold exists in `thresholds.csv` but is never
   referenced by any check in `smellsDetector.py` — either a missing check or
   a threshold nobody uses; not investigated.
4. **`GeneralsmellsDetector.py`** is a stale fork of `smellsDetector.py` with
   its own copy of the same `is_large_play` bug (pre-fix) and its own local
   CSV/TXT writer functions instead of using `write_to_csv.py`/`write_to_text.py`.
   Nothing imports it. Decide: delete it, or clearly mark it deprecated.
5. **`exceptions.py`** is empty — `explanation.md` describes it as holding
   custom exception classes, but nothing is implemented.
6. **`include_vars.py`**: the "used variable" regex only matches
   `{{ var_name }}` with a single space and no filter — misses
   `{{var_name}}` (no spaces) and `{{ var_name | default(...) }}`, so real
   usages can be falsely flagged as unused. A looser regex
   (`var_usage_pattern`) is already defined in the file but never used.
7. **`detect_large_play.py` vs `detect_large_task.py`**: use two different
    special-character-counting regexes (`re.findall(r'[^\w\s]', ...)` vs
    Unicode-aware `regex.findall(r'[^\p{L}\p{N}\s]', ...)`) — inconsistent
    counts for the same `special_chars` metric depending on which level is
    being checked.
8. **`LOC_task` under-reports duplicate-key-heavy tasks**: `detect_large_task.py`
    computes `LOC_task` by re-`yaml.dump()`-ing the *parsed* task dict — but
    `yaml.safe_load()` silently collapses duplicate keys to their last value
    during parsing (this is exactly why `overriden_keys.py` had to do manual
    line-by-line text parsing instead of using the YAML parser). So a task
    with heavy key duplication (confirmed on `main3.yml`'s `task8`, which
    `overriden_keys.py` shows spans lines 83–121 with `src`/`dest`/`owner`/
    `group`/`mode` each duplicated 7–8 times) reports a tiny `LOC_task` (12)
    once collapsed — backwards from what you'd want for severity scoring: the
    more duplicate-key smell a task has, the *smaller* every size-based metric
    says it is. Deliberately left as-is for now — fixing means computing
    `LOC_task` from raw line span instead of the parsed dict, a bigger change;
    revisit if size-based severity scoring becomes important.
9. **Threshold comparisons are implicitly strict `>` everywhere**, not `>=`.
    E.g. `main3.yml`'s AWS-secret task has `special_chars=3` against a
    threshold of exactly `3` — doesn't fire. Not a bug, but an undecided,
    unstated design choice; worth deciding once and documenting rather than
    leaving implicit.
10. **`sem_cohesion.py` uses `encoding='latin1'`** while the rest of the
    codebase consistently uses `utf-8` — inconsistent, and would silently
    mis-decode (not error) any UTF-8 file containing non-Latin-1 characters
    (accented French, given the codebase's mixed French/English comments, is
    a real possibility). Not confirmed as causing an actual problem yet, but
    worth aligning to `utf-8` for consistency.

## Structural / architecture critique
Bug-fixing is close to done; the pipeline now runs correctly end-to-end. The
project has not yet had a structural pass, and every new detector added on
top of the current structure inherits these problems:

1. **No package structure** — everything is flat-file imports
   (`from config import ...`), which only work because you `cd AnsibleGuard`
   first. A real package (`AnsibleGuard/__init__.py`, `pip install -e .`)
   would let this run from anywhere and be imported as a library, and would
   have prevented several of the "why doesn't this find my file" bugs hit
   during debugging.
2. **`Results/` location is ambiguous** — generated output currently lives
   inside `TestData/`, sibling to source fixtures. Convention: a top-level
   `output/`/`Results/` at the repo root, not nested inside code or fixture
   folders, so it's obviously disposable and easy to `.gitignore`.
3. **No `.gitignore`** — `__pycache__/` was visible in the project tree,
   meaning it's likely being committed. Add `__pycache__/`, `*.pyc`,
   `.venv/`, `Results/`, `*.egg-info/` and `git rm -r --cached` anything
   already tracked.
4. **`tests/` folder exists but is empty/unused**, despite a large amount of
   hand-written throwaway fixture testing done during this debugging pass
   (`/tmp/dupe_test.yml`, `/tmp/creds_test.yml`, `/tmp/nested.yml`, etc.).
   Converting those into real `pytest` functions is now the single highest-
   value remaining task — that hard-won "this exact input breaks this exact
   function" knowledge otherwise evaporates once debugging stops.
5. **Thresholds are not empirically justified** — `thresholds.csv`'s values
   appear to be either inherited from prior literature or picked by feel.
   Worth a calibration pass: run the tool across a real corpus (e.g.
   `TestData/projects/` or a larger Ansible Galaxy sample), plot the actual
   metric distributions, and set thresholds near a percentile rather than a
   round guessed number.
6. **Mixed French/English naming** throughout (`compter_tasks_dans_play`,
   `nombre_tasks`, `analyser_tasks` next to `calculate_metrics_task`,
   `detect_large_play`). Not a bug, but reads as unfinished; worth
   standardizing on one language before showing this to anyone outside the
   team.
7. **`print()`-based output everywhere, no logging levels** — fine for
   solo interactive debugging, bad for running unattended over a large
   corpus: no way to silence routine progress output, separate warnings
   from errors, or grep programmatically for "this file failed." A swap to
   Python's `logging` module would pay for itself the first time this runs
   against hundreds of files.
8. **Non-recursive file collection** — the entry point currently uses
   `glob("*.yml")`, not `rglob`, so it won't find `roles/*/tasks/main.yml`
   in a real multi-role Ansible project. Needed before running this against
   an actual project rather than a flat fixture folder — along with an
   exclude list for `molecule/`, `.github/`, `.git/` once recursive globbing
   is added, since those often contain YAML that isn't a real playbook.
9. ~~**Never stress-tested inputs**: multi-document YAML, Ansible Vault,
   dict-style `roles:` entries, non-English task names.~~ **Resolved** —
   this item was stale even before this round: multi-document YAML and
   Ansible Vault handling were investigated and fixed earlier in this same
   log (see "Multi-document YAML and Ansible Vault handling" above),
   dict-style `roles:` entries were confirmed never actually broken (see
   the `high_coupling.py` entry above), and non-English task names in both
   `sem_cohesion.py` and `incohesive_plays.py` are now confirmed and fixed
   this round (see entries above) — both correctly report "unmeasurable"
   instead of falsely reporting perfect cohesion when names are entirely
   out-of-vocabulary.


Full pipeline (`python smellsDetector.py`) runs clean against all three
`TestData/tasks/*.yml` fixtures with no crashes, correct play/task pairing
(confirmed via `Technical_Analysis.json` for `main3.yml`), correct threshold
evaluation for playbook- and play-level large/complex checks, and working
GitLeaks + ansible-lint integration.

## This round's fixes (post-restructure review)
Four additional bugs found and fixed while reviewing the full file set
against `ARCHITECTURE.md`'s call graph — see the dedicated entries above
for each:
- `overriden_keys.py` — cross-depth false-positive duplicate-key reports
- `GitLeaks_hardcoded_credentials.py` — unguarded crash on a missing
  gitleaks binary
- `credentials_leaking_in_log.py` — **high severity**: only scanned tasks
  with no play wrapper, missing virtually all real-world credential-leak
  cases
- `incohesive_plays.py` — non-English/OOV task names falsely scored as
  perfectly cohesive (same bug class as the earlier `sem_cohesion.py` fix,
  missed on this sibling file)

All four verified against multiple fixtures each, including regression
checks against previously-correct behavior.
