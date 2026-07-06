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

### `smellsDetector.py` — `assess_code_smells()` silently scanned the wrong file for every single file, ever (most severe bug found this session)
Found while wiring the CLI against a real 42-file external Ansible project,
not by direct code review — worth noting, since this bug had been sitting
in the pipeline through the entire debugging session and every test written
so far, undetected.

`assess_code_smells(metrics, thresholds, txt_output_files)` — three
parameters — internally calls:
```python
findings = scan_with_gitleaks_file_output(yaml_file_path, GITLEAKS_PATH)
lint_results = run_ansible_lint(yaml_file_path)
```
`yaml_file_path` is not a parameter of this function. Python resolved it by
falling back to the **module-level global** imported from `config.py` at
the top of the file — a single, fixed path, completely independent of
which file's `metrics` dict was actually passed in. Confirmed the bug
reached production, not just a theoretical code-reading concern:
`execute_for_single_file(yaml_file_path, ...)` has the correct per-file
path as its own local parameter, but never passed it through when calling
`assess_code_smells()` three lines later — so **every file this pipeline
has ever processed** — `main.yml`, `main3.yml`, `main-2.yml`, and every one
of the 42 real files in the CLI validation run — had its
`hardcoded_credentials` and `ansible_lint_issues` (the CSV's "Design
Smells" column) computed against `config.yaml_file_path`, not against
itself. Every other metric (everything flowing through `metrics` from
`parser_playbook.py`'s `mainn()` — duplicated code, large playbook, etc.)
was unaffected; only these two, gitleaks- and ansible-lint-derived values
were silently wrong for every file except whichever one happened to match
the config global.

This is exactly the class of bug the earlier `test_smellsDetector.py`
test could not have caught: that test deliberately monkeypatched
`scan_with_gitleaks_file_output`/`run_ansible_lint` to
`lambda *a, **kw: []` specifically to isolate the counter-accumulation
logic under test — which meant it never inspected *what argument* those
functions were being called with, only that they returned something
usable.

**Fixed** by adding `yaml_file_path` as an explicit required 4th parameter
to `assess_code_smells()`, updating `execute_for_single_file()`'s call site
to pass its own already-correct local path through, and removing the now-
dead (and dangerous to leave in place) `yaml_file_path` import from
`config` at the top of `smellsDetector.py` — leaving it there was exactly
the landmine that caused this bug to be possible in the first place.
Confirmed via a dedicated pytest regression test that calls
`assess_code_smells()` twice with two different file paths and asserts the
mocked external-tool calls actually received two *different* paths, not
one shared fallback.

**Two more bugs found in this same function immediately after, once the
full CLI → `execute_for_single_file()` → `assess_code_smells()` chain was
run end-to-end against the real 42-file project** (not just `mainn()` in
isolation) — this function has now yielded three independent, previously
undiscovered bugs from real-world data alone:

**Bug A — same None-vs-missing-key hazard, twice more, in the same
function.** `playbook_metrics = metrics.get("playbook_metrics", {})` — the
default only applies when the key is *missing*; `mainn()` legitimately sets
this key to `None` (not absent) for any non-playbook file, so
`playbook_metrics` came out `None` itself, crashing the very next line
(`playbook_metrics.get("num_plays", 0)` → `AttributeError`). Reproduced
exactly using the real `mainn()` output captured from a genuine failing
file (`group_vars/tomcat.yml`) before fixing. Separately, and independently
confirmed: `Num_Imports`/`Num_Roles` were being read from `playbook_metrics`
in the `complex_playbook` and `high_coupling` checks, but those keys never
exist there — they live in a completely separate top-level dict,
`high_coupling_metrics`, that `mainn()` builds from `high_coupling.py`'s
real output. This meant `High Playbook Coupling` (and half of
`Complex Playbook`'s OR-conditions) had never fired correctly for *any*
file, ever, regardless of real coupling data — invisible all session
because `main3.yml`, the primary fixture, genuinely had zero imports/zero
roles, so "always reports 0" and "correctly reports 0" were
indistinguishable until a real project with actual role dependencies was
run through it. Fixed with explicit `is None` checks for both dicts, and
both misrouted `Num_Imports`/`Num_Roles` lookups corrected to read from
`high_coupling_metrics`.

**Bug B — `execute_for_single_file()` never checked whether `mainn()`
returned `None` before handing it to `assess_code_smells()`.** Even after
`mainn()`'s own vault-tag guard (added during CLI validation, see
`CLI_STATUS.md`) and Bug A's fix above, running the full pipeline still
crashed on the same 2 vault-tagged files — a *different* crash
(`'NoneType' object has no attribute 'get'` on the whole `metrics` dict
itself, one level further up the call stack) than either previous fix
reached. `mainn()` was correctly returning `None` for these files;
`execute_for_single_file()` simply never checked for that before
proceeding. Fixed with an explicit `if metrics is None:` guard immediately
after calling `mainn()`, printing a clear skip message and returning early.
**Known, accepted limitation:** a file that hits this path never gets
scanned by `gitleaks`/`ansible-lint` either, since both are invoked from
inside `assess_code_smells()`, which this guard now skips entirely — not a
new regression (these files crashed before reaching those tools anyway),
but a real, currently-unaddressed coverage gap worth revisiting, since
GitLeaks' content-scan doesn't actually require valid YAML structure to
find a hardcoded secret.

**Confirmed via a genuine full end-to-end run** — not `mainn()` in
isolation, the actual `cli.py` → `execute_for_single_file()` →
`assess_code_smells()` chain, exactly as a future PR bot would invoke it —
against all 42 real files: **42 out of 42 produced a complete, real report**
(`Technical_Analysis.json`, `IaC_Smells.csv`, `Play_Level_Analysis.txt`,
`ansiblelint.txt`, `gitleaks.txt`), verified by counting actual
`IaC_Smells.csv` files on disk, not by absence of a traceback. Worth
remembering as its own lesson: earlier "42/42" claims in this session
(before Bugs A and B were found) were checked only by "nothing crashed,"
which is a materially weaker claim than "the intended output was actually
produced" — the two silently diverged here, with roughly half the files
producing no report at all while the run still reported "success."

### `overriden_keys.py` — structural rewrite (this round)
The old version detected task boundaries by looking for lines starting with
the literal text `- name:` — a text heuristic with no real awareness of YAML
structure. Two confirmed failure modes, both worse than previously
documented: (1) a duplicate key found after a *play's* own `- name:` line got
misattributed to the play instead of the real task; (2) far more seriously,
the moment any task's first key wasn't literally `name:` (e.g. `become:`
before `name:` — ordinary, common Ansible style), boundary tracking silently
closed and **never reopened until the next `- name:` line appeared anywhere
in the file**, at any nesting depth. Confirmed via fixture: a task with a
genuine duplicate key (`msg`/`msg`) returned `[]` — completely invisible,
not even a wrong answer.

Rewritten to parse the file once with `ruamel.yaml`'s round-trip loader
(`YAML(typ="rt")`, `allow_duplicate_keys=True` so it doesn't hard-crash on
the exact thing being detected). Round-trip mode preserves a `.lc.line`
attribute on every parsed dict — real line numbers from the parser, not
guessed from text. Recursively walk the actual tree (plays → `tasks`/
`block`/`rescue`/`always`, matching the recursion pattern already
established in `detect_large_task.py`/`unecessary_abs.py`) collecting every
dict's start line as a boundary marker, sorted, chunked. Key order inside a
task can no longer confuse boundary detection, because the marker is "this
dict exists starting at line N," independent of what's inside it.

Confirmed via 4 fixtures (unnamed task, name-not-first task, the previous
total-blackout case, and a block-wrapper-vs-child-task case with
independent duplicates in each) — all now correctly detected and
attributed. No regression on `main3.yml`'s `task8` (still finds all 5
duplicated keys, correct line numbers).

**Known limitation, documented rather than fixed:** if a `block:` wrapper
has keys *after* the `block:` key (legal YAML, unusual Ansible style), those
trailing keys land in the next sibling task's span rather than the
wrapper's own. Normal Ansible style (`when`/`tags`/`become` before `block:`)
never triggers this.

### `include_vars.py` — tuple-shape crash (this round)
`detect_unused_include_vars()`'s dict-not-list early-return path returned a
bare `0` instead of the `(0, [])` tuple every other path (and every caller,
e.g. `parser_playbook.py`'s `unused_include_vars, WarningUnusedIncludeVars =
detect_unused_include_vars(...)`) expects. Confirmed crash:
`TypeError: cannot unpack non-iterable int object` on any non-list top-level
YAML — a dict-shaped vars file, or a vault-encrypted file (which
`yaml.safe_load()` parses as a plain string). Fixed to `return 0, []`.

### Confirmed clean this round (tested against adversarial input, not just read)
- `Ansible_Lint.py` — real playbook (findings returned correctly), nonexistent
  target path (degrades to structured `load-failure` entries, doesn't crash),
  simulated missing binary (`[]`, no crash). One non-bug worth knowing: a
  missing target file is reported as 2 lint "issues" rather than a distinct
  error state, which could read as false findings in a report.
- `unecessary_abs.py` — empty file, nested single-task block, rescue-nested
  block (block wrapper's own single-task block counted independently from a
  block nested inside `rescue:`).
- `overriding_facts.py` — non-list (vault-string) input handled without
  crashing.
- `unnamed_play.py` / `is_unamed.py` — both previously-documented bugs
  (AND-vs-OR condition, None-only check) confirmed fixed and working via
  direct fixture tests.

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
  exactly once after the loop completes. **Confirmed via pytest** with a
  genuine 2-play fixture where both plays independently trip all three
  thresholds — final counts correctly show `2` (both plays counted), not `1`
  (only the last play surviving a reset).
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
the same way `detect_large_task.py` does. **`incohesive_plays.py` needed no
changes for this specific bug** — it's a pure consumer and correctly
benefited automatically — but it did need a separate, unrelated fix later
(see below).

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
it to the regex check — this part was genuinely fixed in an earlier round
and remains correct.

**The `rescue`/`always` recursion half of this entry was previously
recorded as fixed but was not actually true.** `extract_when_from_tasks()`
only ever recursed into `task['block']` — there was no matching check for
`'rescue'` or `'always'` at all, so a `when:` condition sitting inside a
`rescue:` section was completely invisible to this detector. This was only
caught because the pytest regression suite (built this round, covering
every bug found so far) included a test asserting the *correct* expected
behavior for this exact scenario — the test failed against real code,
which is what exposed the doc's claim as false. Fixed for real this round
(added the missing `rescue`/`always` checks, matching the pattern already
used in every other detector), confirmed via the same pytest test now
passing, and via a manual regression check that the bare-boolean fix
(above) still works with no interference from the new recursion.

**Process note, worth repeating:** this is the concrete argument for why
the pytest suite (Part 4 of `REFACTOR_PLAN.md`) takes priority over trusting
status-doc claims going forward — a doc entry said "fixed," looked
authoritative, and was wrong. A test that actually executes the real code
against a concrete fixture can't drift out of sync the way a written status
note can.

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

**Follow-up found via pytest, this round:** the fix above tracked "did any
name have a vector" as **one shared counter across plays and tasks
combined**, not per group. A file with a normal English play name (e.g.
`"Play"` — has a real vector) wrapping entirely non-English task names would
have that single vectorizable play name mask that the task names
specifically were never measured — `names_with_vector` came out to `1` (the
play name), so the `names_with_vector == 0` condition was false, and it
silently fell through to `average_similarity = 1` again, the exact bug the
first fix was meant to close. Caught by a pytest test built directly against
this scenario. Fixed by tracking `play_total`/`play_with_vector` and
`task_total`/`task_with_vector` as two independent groups — `None` now
fires if *either* group has 2+ names with zero vectors among them, not just
when the whole file combined has zero. Confirmed via a monkeypatched test
that controls `has_vector` directly (rather than depending on the real
model's specific vocabulary, which is a moving target across spaCy
versions) — both the mixed-language case (→ `None`) and the all-English
case (→ a real score) verified on the actual project machine.

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
it currently works. **Confirmed via pytest this round**, including a test
that deliberately locks in the append-mode behavior as intentional (writes
known pre-existing content, calls the append-mode writer, asserts the prior
content survives) — this turns the "fragile but currently correct"
assessment above into an actively-guarded contract rather than an
unverified assumption.

### `duplicate_code.py`
Previously reviewed as "no bug found," which undersold a real, documented
gap: `duplicate_code()` required `'name' in task` before considering a task
at all, in both its `tasks:` and `block:` handling. Two unnamed tasks with
otherwise identical parameters were completely invisible to this detector.
This was captured earlier as a deliberate pytest `xfail` (asserting the
correct eventual behavior, marked as expected-to-fail) rather than silently
missed — the difference matters: an `xfail` is a tracked, visible admission
of a known gap; "no bug found" was not accurate framing.

Fixed properly this round: rewrote around one recursive helper
(`_collect_task_signatures`) that no longer requires a `name` key
(`task.pop("name", None)` is safe whether or not it exists) and added
`block`/`rescue`/`always` recursion, which the original never had in any
form. Confirmed via 4 tests: the original passing case (named duplicates,
no regression), the previously-`xfail`'d case (unnamed duplicates, now a
real pass), a new case (duplicates nested in two separate `block:`
wrappers), and a clean negative case. The `xfail` marker is gone from the
test suite — this is a genuine fix, not a documented limitation anymore.

### `GitLeaks_hardcoded_credentials.py` — unguarded crash on missing binary
A nonexistent playbook path was already handled gracefully (real GitLeaks
exits non-zero on a bad `--source`; the `else` branch already returned
`[]`). A missing or misconfigured `gitleaks` binary path, however, raised
an unguarded `FileNotFoundError` from `subprocess.run()`. Doesn't crash the
whole batch run (`execute_for_single_file`'s outer `try/except` catches
it), but silently skips that file's entire analysis and prints a message
that reads as if the *playbook* is missing rather than the *binary*. Fixed
by catching `FileNotFoundError` at the source with a message pointing at
the real fix (`Install_Gitleaks.py` / check `GITLEAKS_PATH`). Verified
against all three paths: missing binary, bad target, successful scan with
real findings.

### `credentials_leaking_in_log.py` — scope bug, most severe finding of its round
Sourced its raw task dicts from `detect_large_task.py`'s `top_level_tasks`
— which, by that function's own design, contains *only* tasks with no
`hosts:`/`tasks:` wrapper at all. Every task living inside a normal
`- hosts: ... tasks: [...]` play — the overwhelming majority of real
Ansible content — was completely invisible to this check. Confirmed live:
a fixture matching `main3.yml`'s real hardcoded-secret task returned
`nbLeaks: 0`. Fixed by replacing the `top_level_tasks` dependency with a
self-contained recursive collector (`_collect_all_raw_tasks`, mirroring
`files_extensions.py`'s traversal) that gathers every real task's raw
dict regardless of nesting depth. Verified against nested secrets, mixed
top-level+nested, `no_log: true` suppression, and block-nested secrets.

### `incohesive_plays.py` — same OOV bug as `sem_cohesion.py`, missed in the earlier pass
Carries the exact "falsely perfectly cohesive" bug already found and fixed
in `sem_cohesion.py`: a play whose task names are all non-English/
out-of-vocabulary gets `average_similarity = 1` (perfectly cohesive)
purely because nothing had a usable word vector, not because the tasks
are actually related. Separate bug from the block-recursion issue already
covered above — that clearance was correct for block-recursion but didn't
cover this axis. Confirmed via isolated logic test (mocking
`doc.has_vector = False`). Fixed the same way as `sem_cohesion.py`: an
all-OOV play is skipped (counted toward neither cohesive nor incohesive)
rather than assumed cohesive. Unlike `sem_cohesion.py`, this function only
ever returns a plain integer count, so no downstream `None`-handling fix
was needed.

### `smellsDetector.py` — `play_special_chars` double-`.get()` crash
`play_special_chars = (play.get("play_metrics") or {}).get("special_chars", 0)`
already unwraps to a plain `int` — the very next line then called
`.get("special_chars", 0)` on that same int again:
`AttributeError: 'int' object has no attribute 'get'`. Only fired when the
*task's own* `special_chars` did not exceed threshold (Python's `or`
short-circuits, skipping the buggy right-hand side otherwise) — which is
why it never surfaced on the project's own tiny fixtures, none of which
had a real structured play with a plain, low-special-char task name reach
that branch. Confirmed against the real, unmodified function with a
synthetic metrics dict before fixing (not just reasoned through). Fixed by
removing the redundant second `.get()`. Locked in as three pytest cases:
the previously-working short-circuit path, the exact crash condition (now
correctly flags the smell instead of crashing), and a clean negative case.

### Real per-line location data — `ruamel.yaml` rewrite of five detectors
Every finding besides `overriden_keys.py`'s only ever had a task/play
*name*, never a real source line — a real gap once the goal became
feeding a PR bot (see `OUTPUT_FORMATS.md`), since "leave a comment on this
line" needs exactly that. `detect_large_task.py`, `detect_large_play.py`,
`unnamed_play.py`, `unnamed_tasks.py`, and `credentials_leaking_in_log.py`
all rewritten to use `ruamel.yaml`'s round-trip loader (`.lc.line`),
matching the pattern `overriden_keys.py` already established.

Two silent-drift risks caught and fixed before shipping, not assumed away:
1. Naively `yaml.dump()`-ing a `ruamel`-loaded object with PyYAML doesn't
   error — it silently serializes ruamel's *internal implementation
   details* (`_yaml_line_col`, `state`, etc.) instead of the actual
   content. Confirmed this exact failure mode directly. Would have
   corrupted `LOC_task`/`LOC_play` completely. Fixed with a `_to_plain()`
   conversion back to plain dict/list before the existing PyYAML dump
   path in all three affected files.
2. Even using `ruamel`'s *own* dumper (which preserves original
   comments/blank-lines/flow-style formatting) instead of PyYAML's
   canonical re-serialization produces a genuinely *different* line count
   once comments or flow-style lists are involved — confirmed directly:
   12 vs 11 lines on one realistic test case. Exactly the kind of silent
   shift that would move "Large Play"/"Large Task" threshold decisions
   without anyone noticing. Fixed the same way as #1 — `LOC_task`/
   `LOC_play` confirmed byte-identical to pre-rewrite output on content
   with comments and flow-style lists.

Also re-verified: vault-tagged files, genuinely malformed YAML, and
duplicate-key files all still degrade the same way as before the `ruamel`
switch (no new crashes) — `isinstance(x, dict)`/`isinstance(x, list)`
checks throughout these files continue to work unchanged, since
`ruamel`'s `CommentedMap`/`CommentedSeq` genuinely subclass `dict`/`list`
(confirmed directly rather than assumed).

**Two more real bugs found while doing this line-tracking work, unrelated to line numbers themselves:**

- **`unnamed_tasks()` always returned `0`, for every file, always.** It
  iterated `top_level_tasks` (raw dicts, no computed fields) and checked
  `task.get("task_name")` — a key that only exists on the *computed*
  entries in `all_metrics`. Confirmed directly: a fixture with one
  genuinely unnamed top-level task returned `0`, not `1`; the "Unnamed
  Task" CSV column has very likely reported `0` for every file, always,
  this entire project. Fixed by iterating `all_metrics` instead — this
  also fixes the structural gap that `top_level_tasks` could never see an
  unnamed task nested inside a real play at all (confirmed this exact
  case is now caught). `unnamed_tasks()` now returns `(count, details)`
  with a real per-task `"line"`, mirroring
  `credentials_leaking_in_log.py`'s `(warnings, nbLeaks)` pattern.

- **The per-play "Unnamed Play" count undercounted, silently, in
  `parser_playbook.py`.** `detect_large_play.py` substitutes the
  placeholder string `"unknown"` for `Play_name` when a play has no real
  name (so display code always has something to show). `parser_playbook.py`'s
  per-play loop then called `is_unnamed()` on that *already-substituted
  placeholder* — `"unknown"` is a non-empty string, so
  `is_unnamed("unknown")` always returns `0`, silently masking every
  genuinely unnamed play in the final count. Confirmed directly: a real
  `hosts:`-only play with no `name:` reported `unnamed_play == 0` all the
  way through to the final CSV-level aggregate, not just an intermediate
  dict. Fixed by having `parser_playbook.py` use `unnamed_play.py`'s own
  `unnamed_play_details` (rewritten the same way as `unnamed_tasks()`,
  built from a fresh, correct check against the raw YAML, unaffected by
  the placeholder) matched by real line number, instead of re-checking
  the already-corrupted `Play_name` field.

### `high_coupling.py` — malformed entry poisons the whole file's data
A single malformed/blank list item (e.g. a stray `- ` or `- null` in
hand-edited YAML — a common typo) wasn't a crash outward (the function's
own broad `except Exception` catches the resulting `TypeError`), but
silently discarded *every other real play's* coupling data for the entire
file, since the per-entry loop had no `isinstance(play, dict)` guard
before that outer `except` swallowed the error. Confirmed directly with a
two-entry fixture (one real play, one `null`) — the whole file returned
`None` instead of the real play's actual coupling numbers. Fixed with a
per-entry guard so one malformed item only skips itself.

### New: `cli.py`, `findings.py`, `sarif_writer.py` — SARIF/PR-bot output layer
Built out this round to give the pipeline a real front door onto arbitrary
projects (not just `config.py`'s hardcoded fixture folder) and a
PR-bot-ready output shape, not just the existing per-file reports. Full
design rationale and what each of the three project-wide output layers is
for now lives in `OUTPUT_FORMATS.md`. Highlights:
- `output_dir_for()`'s collision-safe naming was verified against a real
  collision, not a hypothetical one — two different roles' `tasks/main.yml`
  files in the same real downloaded project.
- The generated SARIF is validated against the actual downloaded OASIS
  2.1.0 schema (`jsonschema.validate()`), not just eyeballed, including
  the repo-relative-URI requirement GitHub Code Scanning needs.
- The rule/severity catalog in `findings.py` is explicitly a stated,
  provisional judgment call (security > correctness > style tiers), not
  an empirically calibrated one — flagged for a future pass against the
  project's own `Literature_review/` sources, the same way `thresholds.csv`
  itself is flagged as needing calibration in `REFACTOR_PLAN.md`.

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
10. ~~**`sem_cohesion.py` uses `encoding='latin1'`**~~ — **RESOLVED**,
    confirmed via direct inspection of the current file: it uses `utf-8`,
    consistent with the rest of the codebase. The discrepancy flagged
    earlier is no longer open.

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
9. **Never stress-tested inputs**: multi-document YAML (`---` separators
   within one file), Ansible Vault-encrypted variables (`!vault |` blocks),
   dict-style `roles:` entries (`roles: [{role: x, vars: {...}}]` instead of
   a flat string list, which would likely break `high_coupling.py`'s
   `num_roles += len(roles)`), and non-English task names (both
   `sem_cohesion.py` and `incohesive_plays.py` hard-depend on
   `en_core_web_lg`; non-English names would silently degrade to poor/no
   vectors rather than error).


Full pipeline (`python smellsDetector.py`) runs clean against all three
`TestData/tasks/*.yml` fixtures with no crashes, correct play/task pairing
(confirmed via `Technical_Analysis.json` for `main3.yml`), correct threshold
evaluation for playbook- and play-level large/complex checks, and working
GitLeaks + ansible-lint integration.
