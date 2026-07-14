# AnsibleGuard — CLI Development Status

> Historical implementation log. Current verified state (July 14, 2026): 57
> active rules, 144 passing tests, normalized JSON/CSV/text/SARIF output,
> complete PR base-to-head review analysis, configurable suppressions, and a
> successful fresh-environment ansible-lint run. Older counts below are retained
> only as chronological evidence of what was true at that development stage.

Companion to `PROJECT_STATUS.md` (detector bug log), `ARCHITECTURE.md` (current
call graph), and `OUTPUT_FORMATS.md` (current output contract).
This file answers: where are we on making this tool runnable against an
arbitrary real project, not just our fixed `TestData/tasks/` folder.

> **Note:** the packaging work this file tracked has since completed —
> the project is now installed via `pip install -e .` with an `ansibleguard`
> command. File paths below have been updated to
> the current `src/ansibleguard/...` locations; the bug narrative itself is
> unchanged, since it describes real bugs found and fixed during this CLI
> development work, before the later file-move refactor.

## Why this matters (the actual goal)

The stated end goal is a GitHub PR-review bot: hardcoded rules (this
pipeline) combined with an AI layer that filters noise and suggests fixes,
triggered when a developer opens a PR. When that bot fires, it has a
checked-out repo at some arbitrary path and needs to say "analyze *this*
path." The CLI is what defines that contract — not a new detector, a new
front door onto the exact pipeline already built and tested.

## What's built so far

### `ansibleguard/cli.py` — `collect_yaml_files()`
Recursive file discovery (`rglob`, not the old `glob("*.yml")` which only
ever found files in one flat folder). Excludes `molecule/`, `.github/`,
`.git/`, `.venv/`, `venv/` — directories that contain real YAML but aren't
production Ansible content (Molecule test scenarios, CI config).

**Validated against a real downloaded project**, not just hand-built
fixtures: a two-role Ansible Vagrant-style project
(`large-ansible`/`small-ansible`, ~78 files total, including `molecule/`
scenarios, `group_vars/`, `env_vars/`, `requirements.yml`, role
`defaults/`/`vars`/`meta`/`handlers`). Found exactly 42 YAML files,
manually cross-checked against the real directory tree — exact match, zero
`molecule/` paths leaked through.

### The real bug this surfaced: `mainn()` had no top-level parse guard
Running `parser_playbook.mainn()` directly against all 42 real files (not
through `smells.py`, which has its own outer `try/except`) crashed
on 2 of them: `env_vars/dev.yml` and `env_vars/stage.yml`, both containing
an inline `!vault |` tag on a variable — a common, real, recommended
Ansible pattern for per-variable secrets.

Root cause: `mainn()`'s very first line,
`playbook = yaml.safe_load(f)`, had **no try/except at all** — unlike
every individual detector it calls, which each independently catch
`yaml.YAMLError`. `smells.py`'s `execute_for_single_file()`
happened to catch this one level up in production, which is why it was
never noticed before — but that's incidental protection from a *caller*,
not `mainn()` protecting itself, and the CLI calls `mainn()` more directly.

**Fixed**: wrapped `mainn()`'s top-level parse in
`try/except yaml.YAMLError`, returning `None` — consistent with how every
other "fundamentally unusable input" case already degrades elsewhere in
the codebase. Confirmed fixed against the real files that crashed
(`Could not parse ... !vault ...` now prints cleanly, `mainn()` returns
`None`, no crash) and locked in permanently as
`tests/test_parser_playbook_vault_crash.py`.

**Why this bug specifically mattered for the CLI, not just as another bug
fix**: this is the first bug in the whole session that a hand-built
fixture would have been unlikely to catch — we'd have had to specifically
think to test "what if `mainn()`'s own parse fails, independent of
`smells.py`'s outer safety net," which only became obvious once we
were pointing the pipeline at real, messy, third-party data instead of
fixtures we designed ourselves.

### Full real-world validation run
After the fix, ran `mainn()` against all 42 real files directly:

```
42 succeeded, 0 crashed out of 42 total
```

Covered file shapes never tested before this round: genuine populated
vars-style dicts (`roles/tomcat/defaults/main.yml`, real content, not
empty), empty files, Galaxy `requirements.yml`, role `meta/main.yml`,
`handlers/main.yml`. All degrade gracefully — either to `None` (shape is
fundamentally wrong, e.g. `high_coupling.py` on a dict) or to a full
`main_metrics` dict with everything correctly zeroed/emptied (shape is a
valid-but-empty list).

Locked in permanently: `tests/test_vars_file_not_a_playbook.py` (a real
vars file, dict-shaped, must not crash `mainn()` or `high_coupling.py` —
this is a genuinely different failure mode than the vault-string case
tested earlier, which was a parsed *string*, not a real dict).

### Two more real bugs found once `ansibleguard/cli.py` and `smells.py` were wired together for a genuine end-to-end run

**Bug A — `assess_code_smells()`'s `playbook_metrics`/`high_coupling_metrics`
None-vs-missing-key bug (same shape as the `report/csv_writer.py` bug found
earlier, now confirmed twice more in one file).** `metrics.get("playbook_metrics", {})`
only substitutes the default when the key is *missing*, not when it's
present with value `None` — which is exactly what `mainn()` returns for
any non-playbook file. This crashed the moment the code tried
`playbook_metrics.get("num_plays", 0)`. Separately, and independently
confirmed via isolated reproduction: `Num_Imports`/`Num_Roles` were being
read from `playbook_metrics` in two places (the `complex_playbook` and
`high_coupling` checks), but those keys **never exist there at all** —
they live in a completely separate top-level dict, `high_coupling_metrics`,
that `parser.py`'s `mainn()` builds from `high_coupling.py`'s real
output. This meant `High Playbook Coupling` (and half of `Complex Playbook`'s
conditions) had never actually fired correctly for *any* file, ever,
regardless of real coupling data — invisible all session because
`main3.yml`, the primary fixture, happened to have zero imports/zero
roles, so "always reports 0" and "correctly reports 0" looked identical.

Fixed: explicit `is None` checks for both `playbook_metrics` and the newly
introduced `high_coupling_metrics`, and both misrouted lookups corrected to
read from `high_coupling_metrics`. Confirmed via isolated reproduction
before the fix (`AttributeError` reproduced exactly; `high_coupling` check
proven to silently read `False` against real nonzero coupling data) and via
two new permanent pytest tests after
(`tests/test_assess_code_smells_none_handling.py`).

**Bug B — `execute_for_single_file()` never checked whether `mainn()`
returned `None` before handing it to `assess_code_smells()`.** Once Bug A's
fix (and the earlier `mainn()` vault-tag fix) were in place, running the
*full* `ansibleguard/cli.py` → `execute_for_single_file()` → `assess_code_smells()`
chain against the real 42-file project still crashed on exactly the 2
files containing an inline `!vault` tag — a **different** crash than
before (`'NoneType' object has no attribute 'get'`, this time on the whole
`metrics` dict itself, not just one of its values), one level further up
the call stack than the original vault-tag fix reached. `mainn()` was
correctly returning `None` for these files; `execute_for_single_file()`
simply never checked for that before proceeding to call
`assess_code_smells(metrics, ...)` on it.

Fixed: added an explicit `if metrics is None:` guard immediately after
calling `mainn()`, printing a clear skip message and returning early with
the already-initialized empty `findings`/`lint_results` rather than
crashing. Known, accepted limitation from this specific fix: for a file
that hits this path, `gitleaks`/`ansible-lint` never run at all (they're
invoked from inside `assess_code_smells()`, which this guard now skips
entirely) — not a new regression, since before the whole vault-tag fix
chain these files crashed before reaching those tools anyway, just now
happening cleanly instead of via an uncaught exception. Worth revisiting
later if scanning genuinely-unparseable files for hardcoded secrets via
GitLeaks turns out to matter (GitLeaks' content-scan doesn't actually
require valid YAML structure, so this is a real, if currently unaddressed,
coverage gap).

### Confirmed: full real end-to-end run, 42/42, through the actual CLI
With both bugs above fixed, ran the genuine full pipeline exactly as a
future PR bot would invoke it — `ansibleguard/cli.py`'s `analyze_path()`, calling
`execute_for_single_file()` (which itself calls `mainn()` →
`assess_code_smells()` → both external tools → both writers) against every
file `collect_yaml_files()` found in the real 42-file project:

```bash
ansibleguard ~/Documents/ansible-structure -o /tmp/ansibleguard-test-output
find /tmp/ansibleguard-test-output -name "IaC_Smells.csv" | wc -l
# -> 42
```
(Originally run pre-refactor as `python3 cli.py ~/Documents/ansible-structure
-o /tmp/ansibleguard-test-output` — shown above as the equivalent
post-refactor `ansibleguard` invocation, same underlying pipeline.)

**42 out of 42 files produced a complete, real report** (`Technical_Analysis.json`,
`IaC_Smells.csv`, `Play_Level_Analysis.txt`, `ansiblelint.txt`,
`gitleaks.txt`) — not just "didn't crash," the actual, intended output for
every single file. This is the first time in the whole project that claim
has been verified this precisely (earlier "42/42" claims, before Bug A/B
were found, were checked only by absence-of-traceback, not by confirming
the real report files existed — worth remembering as its own lesson: a
clean exit code or a "success" summary line is not the same claim as "the
intended output was actually produced," and the two can diverge silently,
exactly as they did here).

## Decisions made

### Analyze every discovered YAML file — don't pre-filter by folder convention
Considered narrowing `collect_yaml_files()` (or a later stage) to only
target conventional playbook/task locations (`tasks/`, `handlers/`,
root-level playbook files), skipping `group_vars/`, `defaults/`, `vars/`,
`meta/`, `requirements.yml` by convention, to reduce noise in the eventual
report.

**Decided against, for now.** The deciding factor: `external/gitleaks.py`
is a content scan, not a structure scan — real hardcoded secrets very
commonly leak into exactly the files a convention-based filter would
exclude (`group_vars/`, `defaults/`, `vars/` are extremely common places
for an accidentally-committed real credential). Filtering those out to
reduce console noise would silently disable the single most
security-relevant check in the tool on exactly the files most likely to
need it — a real information-loss risk, not just a cosmetic tradeoff.

The counter-concern (running the full detector stack, including two
external subprocess calls per file, against files known in advance to be
structurally incapable of producing a play/task-shaped finding) is real
but is a **performance** question, not a **correctness** one — and there's
no real timing data yet showing it's actually a problem on a repo this
size. Revisit only if a genuinely large real-project run turns out to be
slow in practice.

**Noted for that future conversation, not implemented now:** `gitleaks`
natively supports scanning an entire directory/repo in a single invocation
— running it once per project rather than once per discovered file would
likely be both faster and more thorough (catches patterns that span files)
than the current per-file invocation, entirely independent of any
folder-based exclusion question.

## This round: SARIF / PR-bot output layer

The `.get()`-audit item below (from "Next step") turned up a fourth real
bug (`play_special_chars` double-`.get()` crash — see `PROJECT_STATUS.md`),
now fixed. Separately, built out the actual PR-bot-ready output shape this
file's opening section names as the whole point of the CLI:

- **`report/findings.py`** — flattens one file's analysis into
  `{file, line, rule_id, severity, message}` dicts. Rule/severity catalog
  is explicit and provisional (security > correctness > style), not
  empirically calibrated — same open item as `thresholds.csv` itself.
- **`report/sarif_writer.py`** — serializes that flat list into a real SARIF
  2.1.0 document. **Validated against the actual downloaded OASIS
  schema** (`jsonschema.validate()`), not just eyeballed — this caught
  that the commonly-cited `$schema` URL
  (`oasis-tcs/sarif-spec/master/Schemata/...`) 404s now; the correct
  current path is `oasis-tcs/sarif-spec/main/sarif-2.1/schema/...`.
- **`ansibleguard/cli.py`'s `analyze_path()`** — now also accumulates a flat findings
  list and a per-file summary row across the whole run, writing
  project summary, diagnostics, review metrics, and normalized
  JSON/CSV/text/SARIF once at the end, alongside every per-file report. See
  `OUTPUT_FORMATS.md` for the current contract.

**Real per-line location data** was also added this round —
`detectors/large_task.py`, `detectors/large_play.py`, `detectors/unnamed_play.py`,
`detectors/unnamed_tasks.py`, and `detectors/credentials_in_log.py` all rewritten with
`ruamel.yaml` for real source line numbers (previously only
`detectors/overridden_keys.py` had this). Two silent-drift risks caught and fixed
before shipping (see `PROJECT_STATUS.md` for detail) — this is directly
what makes SARIF annotations point at the right line instead of always
landing on line 1 of the file.

**Two more real bugs found doing that line-tracking work, unrelated to
line numbers**: `unnamed_tasks()` iterated the wrong list and always
returned `0`, for every file, always; `parser.py`'s per-play
"unnamed" count was silently undercounted by a placeholder-string
collision with `is_unnamed()`. Both confirmed and fixed — see
`PROJECT_STATUS.md`.

## Historical follow-up list

This list records what was open at this stage of CLI development. Current
resolution: GitLeaks scans the target independently and retains unparseable and
non-YAML findings; findings/SARIF have permanent regression tests; output
parity, configuration, exact legacy lines, and PR ranges are now tested. The
current backlog is in `README.md`.

- `collect_yaml_files()` and `output_dir_for()` now have real pytest
  coverage (`tests/test_cli.py`, added this round) — the item below about
  no pytest coverage is resolved.
- ~~`collect_yaml_files()` still has no pytest coverage of its own~~ —
  resolved, see above.
- ~~The GitLeaks-on-unparseable-files gap noted above~~ — resolved by running
  GitLeaks once against the scan target independently of structural parsing.
- Output location default (`./ansibleguard-output`) and the collision-safe
  `output_dir_for()` path-mirroring scheme are implemented and now proven
  against a real nested project (`large-ansible/roles/tomcat/defaults/main.yml`
  correctly produced its own output directory distinct from
  `small-ansible/roles/tomcat/defaults/main.yml`'s) — no longer just a
  sketch.
- ~~No pytest coverage for findings/SARIF~~ — resolved by `test_findings.py`,
  `test_sarif_writer.py`, and `test_output_contract.py`.
- Given how many real bugs this exact "run it against real third-party
  data" process has now found (2 in `mainn()`/`execute_for_single_file()`,
  1 more in `assess_code_smells()`'s `play_special_chars` check, 2 more
  in `unnamed_tasks()`/`detectors/unnamed_play.py`, on top of the 4 found earlier
  this session in `detectors/credentials_in_log.py`/`detectors/overridden_keys.py`/
  etc.), a **third** real project (ideally one with more variety than a
  Vagrant/Tomcat two-role demo — something with real `roles:`
  dependencies, real `import_playbook`/`import_tasks` usage, and genuine
  non-trivial coupling data) is worth running before considering the CLI
  broadly trustworthy, not just "works on this one project."

## Next step

Two real options, both reasonable:
1. **Test against a third, more complex real project** — directly
   continues the pattern that's found every real bug so far, and
   specifically exercises `Num_Imports`/`Num_Roles` against genuine
   nonzero coupling data for the first time, which this project's
   fixtures never had — now also the first real test of the SARIF/
   findings.json output at real scale, not just synthetic fixtures.
2. ~~Systematic audit of `smells.py`'s remaining `.get(key, default)`
   calls~~ — done this round, found the `play_special_chars` bug (#4 in
   this exact hazard class); consider this category closed unless a
   future real-project run reveals another instance.
3. Write permanent pytest coverage for `report/findings.py`/`report/sarif_writer.py`
   (currently only manually verified) before relying on them further.
