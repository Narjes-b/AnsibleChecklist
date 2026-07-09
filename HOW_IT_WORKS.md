# AnsibleGuard — How This Works, and What Every Smell Means

This is the plain-language companion to `ARCHITECTURE.md` (bug-focused call
graph), `PROJECT_STATUS.md` (bug log), `TESTING.md` (pytest inventory), and
`CLI_STATUS.md` (CLI development). Read this one first if you want to
understand *what the tool actually does and why*, before diving into any
bug-fixing history.

> **Note:** the project has since been packaged as a real, pip-installable
> tool (`src/ansibleguard/...`, `pip install -e .`, an `ansibleguard`
> command) — see `REFACTOR_PLAN.md` for the full rationale and move log.
> Every file path below reflects the current package layout; where it's
> useful for continuity with older bug-fix history, the old flat filename
> is noted in parentheses the first time a file is mentioned.

---

## Part 1 — The big picture

### What problem this solves

Ansible playbooks are just YAML files that describe automation steps. Like
any code, they can be badly structured, hard to maintain, or accidentally
insecure — even though YAML never "crashes" the way a Python program would.
These structural problems are called **code smells**: not bugs exactly, but
warning signs that something is likely to cause a real problem later
(a bug, a security leak, a maintenance headache).

This tool reads a playbook (or a whole folder of them), measures dozens of
specific things about its structure, compares those measurements against
sensible limits, and reports which limits got crossed. That's the entire
idea. Everything else in this project is either **measuring** something,
**deciding** whether a measurement is bad, or **writing down** the result.

### The three-stage pipeline, in one sentence each

Every file goes through exactly three stages, always in this order:

1. **Measure** — read the YAML, count things (how many tasks, how long are
   the names, are there duplicate keys, etc.) Nobody makes a judgment call
   yet — this stage just produces numbers and lists.
2. **Judge** — take those numbers and compare them against a threshold
   table. If a number crosses its threshold, that's a "smell" (`1`). If
   not, it's clean (`0`).
3. **Report** — write the judged results to disk in three formats: a CSV
   (one row per file, good for spreadsheets), a text file (readable by a
   human, organized by play/task), and a JSON file (the raw, un-judged
   numbers from stage 1, useful for debugging).

### Which file does which stage

```
Stage 1 (Measure)
  parser.py's mainn()
    ↓ calls about 16 different small detector files, one per smell,
      each living in its own .py file (detectors/large_task.py,
      detectors/overridden_keys.py, detectors/set_fact.py, etc.)
    ↓ combines all their results into one big dictionary called
      "main_metrics" — this is the raw, unjudged data

Stage 2 (Judge)
  smells.py's assess_code_smells()
    ↓ reads thresholds.csv
    ↓ compares every number in main_metrics against its threshold
    ↓ produces a second dictionary called "result" — this is the
      final 1-or-0 verdict for every smell

Stage 3 (Report)
  report/csv_writer.py + report/text_writer.py
    ↓ take "result" and write it to IaC_Smells.csv, Play_Level_Analysis.txt
    ↓ take the raw "main_metrics" and write it to Technical_Analysis.json
      (skips the judging step entirely — useful for double-checking a
      threshold decision by hand)

Entry points that kick this whole thing off
  ansibleguard's __main__ block inside smells.py — runs against a fixed
    folder (ansibleguard/config.py's yaml_files_folder), kept mainly for
    local testing now; no longer the documented way to run the tool
  ansibleguard/cli.py — installed as the `ansibleguard` command via
    `pip install -e .`; this is now the real-world, documented entry point.
    Takes any file or folder path, recursively finds every .yml/.yaml file
    (skipping test/CI folders like molecule/ and .git/), and runs the same
    three stages against each one — e.g. `ansibleguard ~/my-project/`
```

If a number in the CSV or JSON ever looks wrong, this is how you debug it:
check `Technical_Analysis.json` first (that's stage 1's raw output, before
any judging). If the raw number is already wrong, the bug is in one of the
small detector files. If the raw number is right but the CSV's 1-or-0 flag
is wrong, the bug is in `smells.py`'s threshold-comparison logic
instead.

---

## Part 2 — How parsing actually works

### The basic tool: PyYAML's `safe_load`

Almost every detector opens the file with `yaml.safe_load()` — a standard,
safe way to turn YAML text into Python data (lists and dictionaries). A
playbook, once parsed, becomes a **list of dictionaries** — each dictionary
is one "play" (`hosts: ...`, `tasks: ...`) or, for role task files, one
task directly.

### Why one detector doesn't use `safe_load` — and why that matters

`detectors/overridden_keys.py` (the detector that finds duplicate keys,
like a task that accidentally sets `mode:` twice) is the one exception.
Here's why:
**PyYAML silently keeps only the *last* value when a key repeats.** If a
task has `mode: 0644` and later `mode: 0755`, `safe_load()` just hands you
`mode: 0755` — the duplicate is already gone by the time your code sees it.
There's no way to detect a duplicate key using `safe_load()`, because the
duplicate has already been erased.

So this one detector uses a different library, `ruamel.yaml`, configured
specifically to **allow** duplicate keys instead of silently collapsing
them, and to remember the exact line number every piece of data started at
(`.lc.line`). This lets the detector walk the real structure of the file —
knowing exactly where each task starts and ends — while still being able
to see every duplicate key, not just the last one.

### The recursive walk: `block`, `rescue`, `always`

Ansible lets you nest tasks inside a `block:` (a grouping construct), and a
block can have a `rescue:` (runs if something in the block fails) and an
`always:` (runs no matter what). None of these are "real" tasks themselves
— they're containers. A `block:` wrapper never executes anything on its
own; only the tasks inside it do.

Every detector that needs to walk through a playbook's tasks follows the
same rule, consistently: **recurse into `block`, `rescue`, and `always`,
but never count the wrapper itself as a task.** This was a real, repeated
source of bugs early in this project — two different files disagreeing
about whether a block wrapper counted as "one task" caused play-level and
task-level data to describe completely different sets of tasks for the
same play. Every detector now follows the same recursion rule for
consistency.

### How tasks get matched to the right play: `play_id`

When `mainn()` collects tasks, it needs to know which play each task
belongs to, so it can later report "play1 has these 3 tasks specifically."
Every task gets tagged with a `play_id` — a running counter, one per real
play in the file (0, 1, 2, ...). Tasks that sit outside any play entirely
(a plain list of tasks with no `hosts:`/`tasks:` wrapper — the shape of a
typical role's `tasks/main.yml`) get a special `play_id` of `-1`, and are
reported separately as "Global" tasks in the final text report.

### Degrading gracefully instead of crashing

A huge fraction of the bugs found this session were about what happens
when a file **isn't a playbook at all** — a `group_vars/all.yml` file is
just a flat dictionary of variables, not a list of plays. Every detector is
expected to recognize this ("this isn't the shape I expect") and return a
safe, empty-but-valid result (`None`, `0`, or `[]`, depending on the
detector) instead of crashing. This matters enormously in practice: a real
Ansible project is mostly *not* task files — `group_vars/`, `defaults/`,
`vars/`, `meta/`, `requirements.yml` are all completely valid, common files
that simply have nothing to do with tasks or plays, and the tool needs to
say "nothing to report here" cleanly rather than fall over.

---

## Part 3 — How thresholds work

### The file: `thresholds.csv`

A simple two-column CSV — a metric name, and the number it needs to exceed
to count as a smell:

| Threshold key | Value | Meaning |
|---|---|---|
| `LOC_playbook` | 110 | Lines of code in the whole playbook file |
| `num_plays` | 4 | Number of plays in one file |
| `avg_play_size` | 50 | Average lines of code per play |
| `num_tasks_playbook` | 15 | Total nested tasks across the whole playbook |
| `avg_task_playbook` | 15 | Average lines per task, playbook-wide (currently unused — see `PROJECT_STATUS.md` known issues) |
| `Num_Imports` | 4 | Number of `import_tasks`/`include_tasks`/`import_playbook` references |
| `Num_Roles` | 5 | Number of `roles:` dependencies |
| `similarity` | 0.4 | Minimum acceptable semantic similarity between task names, playbook-wide |
| `similarityPlays` | 0.5 | Same idea, but measured per individual play |
| `LOC_play` | 50 | Lines of code in one play |
| `num_tasks_play` | 7 | Number of tasks in one play |
| `avg_task_play` | 15 | Average lines per task, within one play |
| `special_chars` | 3 | Number of punctuation/symbol characters allowed in a name before it's flagged |
| `LOC_task` | 15 | Lines of code in one task |
| `task_name_len` | 75 | Maximum characters allowed in a task's name |

### How a "raw number" becomes a "smell"

Every threshold comparison in this codebase follows the same shape:
```python
if some_measured_value > thresholds.get("some_threshold_key", 0):
    smell_flag = 1
else:
    smell_flag = 0
```
This is always a **strict greater-than** comparison, not "greater than or
equal to" — a task with exactly `special_chars == 3` against a threshold of
`3` does *not* get flagged. This is a deliberate, consistent choice
throughout the codebase (see `PROJECT_STATUS.md` for the discussion of
whether this should ever change to `>=`).

### Compound smells: more than one condition combined

A few smells aren't a single number vs. a single threshold — they're a
combination. For example, **Complex Playbook** fires if *any* of several
different conditions are true (too many lines AND too many plays, OR too
many lines AND too many tasks, OR too many imports, OR too many role
dependencies). This is intentional — there's more than one way for a
playbook to be "too complex," and the tool checks for all of them.

### When a number can't be measured at all: `None`

Some things genuinely can't always be measured — the clearest example is
**cohesion** (how related are the task names to each other, semantically).
If every task name in a file happens to be non-English, or otherwise
outside the vocabulary of the language model used to compare them, there's
nothing to actually measure. The correct answer in that case is
**"unmeasurable" (`None`)**, not a fake "everything's fine" or a fake
"everything's bad." Every place that handles this value has to explicitly
check `if value is None:` before doing anything else with it — a
comparison like `None < 0.4` would crash, and treating `None` as `0` or
skipping the check entirely reintroduces exactly the kind of silent, wrong
result this whole project has spent a lot of effort finding and fixing
(see `PROJECT_STATUS.md`'s `detectors/semantic_cohesion.py` and `assess_code_smells()`
entries for the real bugs this exact mistake caused).

---

## Part 4 — The full smell catalog

Organized by *level* — some smells describe the whole playbook file, some
describe one play, some describe one task. A few come from external tools
rather than this project's own code.

### Playbook-level smells

**Large Playbook** — the file overall is too big.
- *Detected by:* `detectors/large_playbook.py`
- *Raw numbers:* `LOC_playbook`, `num_plays`, `avg_play_size`, `num_nested_tasks_playbook`
- *Fires if:* any one of those four exceeds its threshold
- *CSV column:* `Large Playbook`

**Complex Playbook** — the file is big *and* structurally tangled (or has heavy external coupling).
- *Detected by:* combination of `detectors/large_playbook.py` + `detectors/high_coupling.py`, judged in `smells.py`
- *Fires if:* (big AND many plays) OR (big AND many tasks) OR too many imports OR too many role dependencies
- *CSV column:* `Complex Playbook`
- *Note:* this is the exact check that had a real bug — it was reading `Num_Imports`/`Num_Roles` from the wrong dictionary and could never actually fire on real coupling data until fixed this session.

**Insufficient Modularization** — the playbook should probably have been split into smaller files/roles.
- *Detected by:* `detectors/large_playbook.py`'s numbers, judged in `smells.py`
- *Fires if:* too many lines AND too many plays, together
- *CSV column:* `Insufficient Modularization`

**High Playbook Coupling** — the playbook depends on too many other files (imports, roles).
- *Detected by:* `detectors/high_coupling.py`
- *Raw numbers:* `Num_Imports` (from `import_tasks`/`include_tasks`/`import_playbook`), `Num_Roles` (from `roles:`)
- *Fires if:* either number exceeds its threshold
- *CSV column:* `High Playbook Coupling`
- *Note:* correctly finds `import_tasks`/`include_tasks` nested inside a play's `tasks:` list (the common real-world form), not just as a bare top-level key — this was a real gap found and fixed via a real external project.

**Incohesive Playbook** — the tasks in this file don't seem conceptually related to each other.
- *Detected by:* `detectors/semantic_cohesion.py`, using a language model (spaCy) to compare task/play names semantically
- *How it works:* every task and play name gets compared pairwise; a lemmatizer normalizes word forms first (e.g. "installing" → "install") so minor wording differences don't count against similarity
- *Fires if:* the average similarity score is below the threshold
- *Special case:* if every name in the file is outside the language model's vocabulary (commonly: non-English task names), the result is `None` (unmeasurable), not a false "perfectly cohesive." This is tracked **per group** — plays and tasks separately — so one ordinary English play name can't mask that the task names specifically were never actually measured.
- *CSV column:* `Incohesive Playbook`

**Duplicated Code** — the same task body (ignoring the name) appears more than once.
- *Detected by:* `detectors/duplicate_code.py`
- *How it works:* strips the `name:` field from each task, then compares the remaining parameters; two tasks with different names but identical parameters count as duplicates
- *Recurses into:* `block`/`rescue`/`always`, and works whether or not the task has a name at all
- *CSV column:* `Duplicated Code`

**Unnecessary set_fact** — a variable is set with `set_fact:` but never actually used anywhere.
- *Detected by:* `detectors/set_fact.py`
- *How it works:* collects every `set_fact:`'d variable name, then scans the whole file for `{{ variable }}`-style usage; anything set but never referenced is flagged
- *CSV column:* `Unnecessary set_fact`

**Overriding Facts** — the same fact gets set to two different values somewhere in the file.
- *Detected by:* `detectors/overriding_facts.py`
- *How it works:* collects every `set_fact:` assignment as a (name, value) pair, then checks whether any name appears twice with different values
- *CSV column:* `Overriding Facts`

**Unnecessary Abstraction** — a `block:` is used to wrap just one single task, adding nesting for no real grouping benefit.
- *Detected by:* `detectors/unnecessary_abstraction.py`
- *How it works:* recursively checks every `block:` (including one nested inside another, or inside `rescue`/`always`) and counts how many wrap exactly one child task
- *CSV column:* `Unecessary Abstraction`

**Missing File Extension** — a file reference (`src:`, `dest:`, `path:`, etc.) has no extension, like `myfile` instead of `myfile.conf`.
- *Detected by:* `detectors/file_extensions.py`
- *How it works:* checks both a task's direct attributes and any nested module parameters (e.g. `copy: {src: ..., dest: ...}`) for a file-looking value with no `.something` suffix
- *CSV column:* `Missing File Extension`

**Overridden Keys** — the same key appears more than once inside one task (e.g. `mode:` set twice).
- *Detected by:* `detectors/overridden_keys.py` — see Part 2 above for why this needs `ruamel.yaml` instead of `safe_load`
- *How it works:* parses with real structural line numbers, walks the tree to find where each task/wrapper starts, then scans each task's own text span for any key appearing more than once **at the same structural depth** (so a task's own `name:` field can never be confused with a same-named parameter nested inside a module, like `apt: {name: nginx}`)
- *CSV column:* `Overriden keys`

**Duplicated Task Names** — two tasks in the file have the exact same `name:`.
- *Detected by:* `detectors/duplicate_task_names.py`
- *CSV column:* `Duplicated Task Names`

**Missing Bool Filter** — a `when:` condition looks like it's testing a boolean-ish value without the `| bool` filter, or compares against the literal string `"true"`/`"false"` instead of a real boolean.
- *Detected by:* `detectors/bool_filters.py`
- *How it works:* splits a `when:` condition on `and`/`or`, skips anything that's clearly a comparison (`==`, `!=`, `<`, `>`) or a literal `true`/`false`, and flags anything else that doesn't already have `| bool` applied
- *Recurses into:* `block`/`rescue`/`always` (a real, previously-open bug in this exact file, only fixed after a pytest test specifically built to check it — see `PROJECT_STATUS.md`)
- *CSV column:* `Missing Bool Filter`

**Unnecessary Dependency (unused include_vars)** — a file is pulled in with `include_vars:` but none of its variables are ever actually used.
- *Detected by:* `detectors/include_vars.py`
- *CSV column:* `Unecessary Dependency`

**Credentials Leaking In Log** — a task handles something that looks like a secret (`password`, `token`, `api_key`, etc.) without `no_log: true`, meaning it could get printed into Ansible's own log output.
- *Detected by:* `detectors/credentials_in_log.py`
- *How it works:* dumps each task back to YAML text and checks for sensitive-looking keywords, then checks whether `no_log: true` is set on that same task
- *CSV column:* `Credentials Leaking In Log`
- *Note:* this was the highest-severity bug of the whole session before being fixed — it originally only scanned the rare "tasks outside any play" case, so it was blind to credentials in ordinary, normal plays (the vast majority of real playbooks).

### Play-level smells

**Large Play** — one specific play is too big.
- *Detected by:* `detectors/large_play.py`
- *Raw numbers:* `LOC_play`, `num_tasks_in_play`, `avg_task_play`
- *Fires if:* any one exceeds its threshold, for that specific play
- *CSV column:* `Large Play` (playbook-level total count of how many plays triggered this)

**Unnamed Play** — a play has no `name:` field, or the name is blank/whitespace.
- *Detected by:* `detectors/unnamed_play.py` (whole-file count) and `detectors/is_unnamed.py` (per-play check used inside `mainn()`)
- *Condition:* a play is recognized by having *either* `hosts:` or `tasks:` (not both required — an earlier version incorrectly required both, undercounting real plays)
- *CSV column:* `Unnamed Play`

**Incohesive Play** — same idea as Incohesive Playbook, but scoped to just this one play's task names instead of the whole file.
- *Detected by:* `detectors/incohesive_plays.py`
- *CSV column:* `Incohesive Play`

### Task-level smells

**Large Task** — one specific task is too big.
- *Detected by:* `detectors/large_task.py`
- *Raw number:* `LOC_task`
- *CSV column:* `Large Task` (playbook-level total count of how many tasks triggered this)

**Long Task Name** — a task's `name:` is unreasonably long.
- *Detected by:* `detectors/large_task.py`
- *Raw number:* `task_name_len`
- *CSV column:* `Long Task Name`

**Unnamed Task** — a task has no `name:` field at all.
- *Detected by:* `detectors/large_task.py` (internally labels these `"Unknown"`), counted by `detectors/unnamed_tasks.py`
- *CSV column:* `Unnamed Task`

**Inconsistent Naming Convention** — a task or play's name has an unusual number of punctuation/symbol characters.
- *Detected by:* `detectors/large_task.py` (task-level `special_chars`) and `detectors/large_play.py` (play-level `special_chars`)
- *Fires if:* either the task's own name or its parent play's name has too many special characters
- *CSV column:* `Inconsistent Naming Convention`
- *Note:* the play-level half of this check had a real, permanently-dead bug — it was reading `special_chars` from the wrong dictionary and could never fire — found and fixed this session.

### Security smells (from external tools)

**Hardcoded Credentials** — a real secret (AWS key, API token, etc.) is hardcoded directly in the file.
- *Detected by:* `external/gitleaks.py`, which runs the external `gitleaks` binary against the file's actual text content
- *Why an external tool:* this is a mature, purpose-built secret-scanning tool — no reason to reinvent pattern-matching for dozens of credential formats when a well-maintained tool already does it well
- *CSV column:* `Hardcoded Credentials`

**Design Smells** — general Ansible best-practice violations (deprecated syntax, style issues, missing `become`, etc.)
- *Detected by:* `external/ansible_lint.py`, which runs the external `ansible-lint` tool
- *CSV column:* `Design Smells`

---

## Part 5 — How it all comes together for one file

Walking through exactly what happens when the tool analyzes a single file,
start to finish:

1. The installed `ansibleguard` command (`ansibleguard/cli.py`) — or
   `smells.py`'s own loop, kept for local testing — finds the file and calls
   `execute_for_single_file()`.
2. That calls `parser.py`'s `mainn()`, which:
   - Parses the YAML (safely — returns `None` and stops here if the file
     can't even be parsed, e.g. an unsupported `!vault` tag).
   - Calls all ~16 individual detector functions, each measuring its own
     specific thing.
   - Assembles every result into one big dictionary, including a `"plays"`
     list where each play's own metrics are paired up with the tasks that
     belong to it (matched by `play_id`).
3. Back in `execute_for_single_file()`, if `mainn()` returned `None`
   (unparseable file), the whole thing stops cleanly here with a skip
   message — nothing further is written for this file.
4. Otherwise, the raw dictionary is written straight to
   `Technical_Analysis.json` — this is the "before judging" snapshot.
5. `smells.py`'s `assess_code_smells()` takes that same dictionary,
   loads `thresholds.csv`, and works through every smell listed in Part 4,
   producing a final 1-or-0 (or a count, for smells that can happen more
   than once) for each one.
6. That runs `gitleaks` and `ansible-lint` against the file too (as real
   external processes), folding their results in as the two remaining
   smells.
7. The final judged dictionary gets written to `IaC_Smells.csv` (one row)
   and `Play_Level_Analysis.txt` (a readable breakdown by play and task).

That's the entire system. Every bug found and fixed across this whole
project (see `PROJECT_STATUS.md` for the full list) has been some version
of: a detector measuring the wrong thing, a threshold comparison reading
from the wrong dictionary, or a crash on a file shape nobody had tried yet
— never a change to this fundamental three-stage design, which has held up
throughout.
