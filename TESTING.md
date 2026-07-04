# AnsibleGuard — Test Suite Inventory

Companion to `ARCHITECTURE.md` and `PROJECT_STATUS.md`. This file is a
complete inventory of the `pytest` regression suite built this session:
what exists, what each test protects against, and how to run it. See
`ARCHITECTURE.md`'s "Automated regression suite" section for the
philosophy (why this now outranks written status-doc claims).

## Run everything

```bash
cd ~/Documents/AnsibleChecklist/AnsibleGuard
python3 -m pytest tests/ -v
```

**Current state: 60 tests across 24 test files, all passing**, confirmed
live on the actual project machine (not just in isolation) after each
addition — including a deliberate check on the two
`GitLeaks_hardcoded_credentials.py` tests to confirm each one hit the
code path its name actually claims, not an accidental duplicate of the
other.

## Directory structure

```
tests/
├── __init__.py            # makes tests/ a real importable package
├── conftest.py             # shared fixtures_dir pytest fixture
├── fixtures/               # sample YAML files, one or more per scenario
└── test_*.py               # one file per source module under test
```

## Full inventory, by source file tested

| Test file | Tests | What it protects against |
|---|---|---|
| `test_00_smoke.py` | 2 | Pytest discovery/config itself works; `conftest.py`'s fixture wiring is correct |
| `test_duplicate_task_names.py` | 2 | Tuple-unpacking bug (`calculate_metrics_task()` returns a 2-tuple; old code assigned the whole tuple to one variable, always returning `0`) + negative case (no false positives on unique names) |
| `test_overriden_keys.py` | 3 | The structural rewrite (real `ruamel.yaml` line numbers instead of a `- name:` text heuristic): a task's own field vs. a same-named nested module parameter must not collide; a genuine same-depth duplicate must still be caught; multiple distinct duplicated keys in one task (mirrors the real `main3.yml` `task8` case) |
| `test_high_coupling.py` | 4 | Singular `role:` no longer `KeyError`s; dict-style `roles: [{role: x, vars: {...}}]` counts correctly (confirmed never actually broken); `import_tasks`/`include_tasks` nested inside a play's `tasks:` list (the common real-world form) is detected; a fully vault-encrypted file returns `None` instead of silently reporting fake all-zero results |
| `test_credentials_leaking_in_log.py` | 3 | The highest-severity bug this session — the old code read `top_level_tasks` (only tasks outside any play, rare) instead of the full recursive task list, so it was blind to credentials in ordinary `hosts:`/`tasks:` plays; `no_log: true` correctly suppresses the warning; detection still works nested inside a `block:` |
| `test_detect_large_task.py` | 3 | Vault-encrypted file doesn't crash (`UnboundLocalError` on `top_level_tasks`); a `block:` wrapper is never itself counted as a task, only its real children are; bare tasks with no play wrapper correctly get `play_id == -1` |
| `test_detect_large_play.py` | 2 | Block recursion matches `detect_large_task.py`'s semantics exactly — this was the core play/task data-mismatch bug found via `main3.yml`; non-list (vault) YAML returns `None` |
| `test_detect_large_playbook.py` | 1 | A task-only file (no `hosts:`/`tasks:` wrapper anywhere — the shape of a typical role's `tasks/main.yml`) doesn't crash on `calculate_metrics_play()` returning `None` |
| `test_unecessary_abs.py` | 2 | Empty YAML file returns `0` instead of crashing on `None` iteration; a block nested inside `rescue:` is still recursively detected |
| `test_include_vars.py` | 1 | Non-list top-level YAML returns a proper `(0, [])` tuple instead of a bare `0` that crashes every caller's unpacking |
| `test_is_unamed.py` | 4 | `None`, empty string, and whitespace-only string all correctly count as unnamed; a real name does not |
| `test_unnamed_play.py` | 1 | Play-detection condition uses OR (`hosts` or `tasks`), not AND — a `hosts:`-only play with no `tasks:` key is still counted |
| `test_ansible_lint.py` | 4 | Real findings on a real playbook; clean playbook returns `[]`; nonexistent target path doesn't crash; simulated missing binary (via `monkeypatch`) degrades to `[]` instead of crashing the pipeline |
| `test_overriding_facts.py` | 3 | Conflicting fact values (same name, different value) detected; different fact names not false-flagged; vault-encrypted (string) input doesn't crash |
| `test_set_fact.py` | 2 | Unused `set_fact` detected; used fact correctly not flagged |
| `test_duplicate_code.py` | 4 | Duplicate named tasks (identical params, different names) detected; duplicate unnamed tasks now genuinely detected (was an `xfail` documenting a known limitation — fixed for real by removing the `'name' in task` requirement and adding `block`/`rescue`/`always` recursion); duplicates nested in two separate `block:` wrappers; clean negative case |
| `test_write_to_csv.py` | 2 | `incohesive_playbook == None` (unmeasurable cohesion) writes blank in the CSV, not the literal string `"None"`; `incohesive_playbook == 0` (a real, legitimate result) does NOT get blanked — confirms the fix distinguishes "missing/unmeasurable" from "a real falsy value," which a naive `value or ''` would have gotten wrong |
| `test_write_to_text.py` | 5 | Tasks outside any play ("Global") now print under a clear header instead of being visually indistinguishable from the preceding play's tasks; GitLeaks JSON writer round-trips correctly; unused-vars writer's empty and non-empty cases; append-mode call-order behavior locked in as an intentional, tested contract — writes known pre-existing content, calls the append-mode writer, asserts the prior content survives, rather than leaving this as an unverified assumption |
| `test_files_extensions.py` | 2 | Missing file extension nested inside `rescue:` detected exactly once (regression test for a prior missing-recursion bug + a separate triple-count bug); all-extensions-present returns `0` |
| `test_filters_for_comparison.py` | 2 | Bare boolean `when: true` doesn't crash (`TypeError` on `re.split()` against a Python `bool`, not a string); missing `| bool` filter nested inside `rescue:` is detected — this test caught a real, still-open bug that a prior status-doc pass had incorrectly marked as already fixed |
| `test_smellsDetector.py` | 1 | `assess_code_smells()`'s per-task counters (`large_task`, `long_task_name`, `inconsistent_naming_convention`) genuinely accumulate across multiple plays rather than resetting — confirmed via a real 2-play fixture using the actual `mainn()` → `assess_code_smells()` pipeline (external tools mocked out via `monkeypatch` to isolate the aggregation logic specifically) |
| `test_sem_cohesion.py` | 2 | A mixed file (normal English play name wrapping entirely non-English task names) correctly returns `None` (unmeasurable), not a false "perfectly cohesive" `1` — this required a real follow-up fix (see `PROJECT_STATUS.md`); normal English names on both sides still return a real score. Uses a monkeypatched `nlp` function to control `has_vector` directly rather than depending on the real `en_core_web_lg` model's specific vocabulary (a moving target across spaCy versions) — fast and deterministic instead of needing the large model loaded per assertion |
| `test_incohesive_plays.py` | 1 | **New this round.** Direct coverage for `incohesive_plays.py` itself, previously only exercised indirectly through `detect_large_play.py`'s tests. Confirms the all-non-English-task-names case correctly returns `0` (unmeasurable play skipped, counted toward neither cohesive nor incohesive), same shape as `sem_cohesion.py`'s fix. Investigated whether this file shares `sem_cohesion.py`'s subtler "shared counter across two groups" follow-up bug — confirmed by reading the code that it structurally cannot: this function only ever compares task names to each other within one play, and never mixes in a separate play-name vector comparison the way `sem_cohesion.py` does, so there's no second group to accidentally mask the first. |
| `test_gitleaks_hardcoded_credentials.py` | 2 | **New this round.** A missing/misconfigured `gitleaks` binary path degrades gracefully (`[]`, no crash) instead of raising an unguarded `FileNotFoundError` — matters specifically for a CI/PR-bot context, where a runner without `gitleaks` pre-installed must not crash the whole check. A nonexistent target playbook path (binary present, bad `--source`) also confirmed to degrade correctly, pre-existing behavior, now locked in. Explicitly verified on the real project machine which code path each test actually exercises (not just that both passed), since a naive version of the second test could have silently exercised the same missing-binary path as the first without actually reaching real `gitleaks`. |
| `test_parser_playbook.py` | 2 | **New this round, highest-value of the three added.** End-to-end test of `mainn()`'s full assembly logic — the test that would have caught the original play-numbering desync bug directly at its source, instead of it being found by manually diffing a JSON file by hand. Confirms every real play in a `main3`-shaped fixture ends up paired with its *own* tasks (not a block-wrapper's name, not another play's tasks), and that the "Global" tasks group contains only genuinely top-level tasks. Also covers the `is_task_only_playbook` branch (a role-style file with no `hosts:`/`tasks:` anywhere), which takes an entirely different code path through `mainn()` and had no coverage at all before this. |

## Three real findings this suite has already produced

Worth remembering these as the concrete argument for why this suite exists,
not just abstract "best practice":

1. **`filters_for_comparison.py`** — a status doc claimed `rescue`/`always`
   recursion was fixed. It wasn't. A pytest test asserting the correct
   behavior failed against real code, which is what exposed it. Fixed for
   real.
2. **`smellsDetector.py`** — the opposite direction: a status doc claimed a
   counter-reset bug was fixed. This time the claim was genuinely true, and
   the pytest test independently confirmed it rather than requiring anyone
   to trust the doc's word for it.
3. **`sem_cohesion.py`** — a subtler variant of finding #1: a fix genuinely
   existed and looked correct on read-through, but a pytest test built
   against a realistic mixed-language fixture (English play name, non-English
   task names) exposed that the fix tracked vector availability as one
   shared counter across plays and tasks combined, so a single vectorizable
   play name could mask that the task names specifically were never
   measured — silently reproducing the exact bug the fix was meant to
   close. Not "no fix existed" (finding #1) or "the fix was fully correct"
   (finding #2) — a real middle case: a genuine fix with an incomplete
   scope, which only a concrete adversarial test fixture surfaced.

**Fourth finding, this round:** the inverse of #3 — `incohesive_plays.py`
was flagged as "worth checking for the same shared-counter risk" as
`sem_cohesion.py`. Direct investigation (reading the function, then
confirming with a live test) showed the risk genuinely does not apply here,
because the function's structure is different enough that the same bug
shape cannot occur. Worth recording explicitly: not every suspected risk
turns out to be a real bug, and confirming a non-issue with a real test is
just as valuable as confirming a real one — it closes the question instead
of leaving it as an open, recurring worry.

## Known environment gap

`overriden_keys.py`'s tests depend on `ruamel.yaml`, which is not yet
confirmed to be listed in `requirements.txt` — a fresh install could hit
`ModuleNotFoundError` even though existing development machines already
have it. Add `ruamel.yaml==0.19.1` (matching the installed version) if not
already present.

## Not yet covered — next candidates

All three items previously listed here are now resolved (see
`test_incohesive_plays.py`, `test_gitleaks_hardcoded_credentials.py`, and
`test_parser_playbook.py` above). No outstanding known gaps in detector-level
or orchestration-level coverage as of this update — remaining work moves to
`REFACTOR_PLAN.md` Part 3 (CLI) and Part 2 (package restructure), which are
structural, not correctness, work and don't need pytest coverage in the same
way until the new code (e.g. `cli.py`'s `collect_yaml_files()`) actually
exists.
