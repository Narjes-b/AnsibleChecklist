# AnsibleGuard

**AnsibleGuard** is a static-analysis tool for Ansible playbooks. Point it
at a single playbook or a whole Ansible project, and it reads every YAML
file, measures dozens of structural properties, compares those
measurements against a set of thresholds, and reports the **code smells**
it finds — things that aren't necessarily bugs, but are warning signs of
future bugs, security leaks, or maintenance pain.

It also runs two mature external tools alongside its own checks:
[GitLeaks](https://github.com/gitleaks/gitleaks) (hardcoded secrets) and
[`ansible-lint`](https://ansible.readthedocs.io/projects/lint/) (general
best-practice violations) — so one run gives you a combined view instead of
three separate tools to remember.

The end goal this project is building toward is a **GitHub PR-review bot**:
this rule-based pipeline plus an AI layer that filters noise and suggests
fixes, triggered automatically when a developer opens a pull request. Every
design decision below (the CLI, the SARIF output, the line-accurate
findings) exists in service of that goal.

---

## Quick start

```bash
git clone <repo-url>
cd ansibleguard
pip install -e .

# one-time model/data downloads the detectors depend on
python -c "import nltk; nltk.download('wordnet')"
python -m spacy download en_core_web_lg

# installs the gitleaks binary if it isn't already available
python -c "from ansibleguard.external.install_gitleaks import ensure_gitleaks_installed; ensure_gitleaks_installed()"

ansibleguard --help
```

Then run it against any real Ansible project or single playbook:

```bash
ansibleguard ~/my-ansible-project/            # whole project, recursive
ansibleguard playbook.yml -o ./results/       # single file, custom output dir
```

For CI or explicit setup, install the pinned GitLeaks binary without causing
downloads during package import:

```bash
ansibleguard install-tools
ansibleguard . -o ansibleguard-output --fail-on error
```

Vars/defaults files, inline `!vault` values, invalid YAML, and fully encrypted
vault files are now classified separately from playbooks. Structural detectors
run only where applicable, while GitLeaks scans the target independently and
its findings are retained even when YAML parsing fails. See
[`PARSING_GITHUB_IMPLEMENTATION.md`](PARSING_GITHUB_IMPLEMENTATION.md) for the
step-by-step implementation and GitHub PR workflow.

`ansibleguard` is a real installed command — it works from any directory
on the machine, not just from inside this repo. This is a genuine, working
tool, not a script you need to remember how to invoke — no `cd` into a
particular folder required.

---

## What it actually detects

AnsibleGuard organizes checks by the level of the file they describe —
whole playbook, one play, or one task — plus two checks that come from
external tools.

### Playbook-level
| Smell | What it means |
|---|---|
| Large Playbook | The file overall is too big (lines, number of plays, average play size, or total nested tasks) |
| Complex Playbook | Big *and* structurally tangled, or has heavy external coupling |
| Insufficient Modularization | Too many lines *and* too many plays — probably should be split into roles |
| High Playbook Coupling | Depends on too many `import_tasks`/`include_tasks`/`import_playbook`/`roles:` references |
| Incohesive Playbook | Task/play names across the file don't seem conceptually related (semantic similarity via spaCy) |
| Duplicated Code | The same task body (ignoring the name) appears more than once |
| Unnecessary `set_fact` | A variable is set but never actually used |
| Overriding Facts | The same fact gets set to two different values in the same file |
| Unnecessary Abstraction | A `block:` wraps just one single task for no real grouping benefit |
| Missing File Extension | A file reference (`src:`, `dest:`, `path:`, ...) has no extension |
| Overridden Keys | The same key appears twice inside one task (e.g. `mode:` set twice — silently discards data) |
| Duplicated Task Names | Two tasks share the exact same `name:` |
| Missing Bool Filter | A `when:` condition looks boolean-ish but skips the `| bool` filter |
| Unnecessary Dependency | An `include_vars:` file is pulled in but none of its variables are used |
| Credentials Leaking In Log | A task handles a secret-looking value without `no_log: true` |
| Complex Expression | A Jinja or conditional expression has excessive syntactic complexity |
| Incomplete Task | Source still contains `TODO`, `FIXME`, `HACK`, or `XXX` work markers |
| Long Statement | A YAML source line exceeds 120 characters |
| Empty Abstraction | A YAML task structure or block/rescue/always section is empty |
| Excessive Nesting | Block/rescue/always nesting exceeds three levels |
| Missing Abstraction | A large task file uses no roles or task includes |
| Unguarded Variable | A Jinja variable has no visible definition or default/defined guard |

### Role/project structure
| Smell | What it means |
|---|---|
| Unstructured Module | A role is missing a conventional `main.yml` entry point |
| Broken Role Dependency | Local role dependencies are missing, cyclic, or self-referential |

### Play-level
| Smell | What it means |
|---|---|
| Large Play | One specific play is too big |
| Unnamed Play | A play has no `name:` field |
| Incohesive Play | Same idea as Incohesive Playbook, scoped to one play |

### Task-level
| Smell | What it means |
|---|---|
| Large Task | One specific task is too big |
| Long Task Name | A task's `name:` is unreasonably long |
| Unnamed Task | A task has no `name:` field at all |
| Inconsistent Naming Convention | A task or play name has an unusual amount of punctuation/symbols |

### Security (external tools)
| Smell | What it means |
|---|---|
| Hardcoded Credentials | A real secret is hardcoded in the file, via `gitleaks` |
| Design Smells | General best-practice violations, via `ansible-lint` |

Full explanations of *how* each check actually works are in
[`HOW_IT_WORKS.md`](HOW_IT_WORKS.md). The paper-derived checks and their
limitations are documented in
[`PAPER_SMELLS_IMPLEMENTATION.md`](PAPER_SMELLS_IMPLEMENTATION.md).

---

## What you get back

Every run produces layered output, built from the same underlying analysis
but shaped for different audiences:

```
<output>/
├── <mirrored-path-per-file>/          # LAYER 1 — one set per analyzed file
│   ├── Technical_Analysis.json        #   raw metrics, before threshold logic
│   ├── IaC_Smells.csv                 #   one-row summary for this file
│   ├── Play_Level_Analysis.txt        #   human-readable per-play/task breakdown
│   ├── ansiblelint.txt
│   └── gitleaks.txt
├── summary.csv                        # LAYER 2 — project-wide rollup, worst-first
├── findings.json                      # LAYER 3 — flat findings list, one entry per problem
└── findings.sarif                     # LAYER 3 — same data as real SARIF 2.1.0
```

- **Layer 1** is for a human doing a deep-dive on one specific playbook.
- **Layer 2** (`summary.csv`) answers "out of everything just analyzed,
  which files actually need attention" in one spreadsheet-friendly file.
- **Layer 3** is built for machines: CI pipelines, and GitHub's Code
  Scanning feature specifically, which natively renders `findings.sarif`
  as inline PR annotations — no bot code required to post comments.

Full detail on when to use which layer, what the severity levels
(`error`/`warning`/`note`) mean, and how SARIF line numbers work is in
[`docs/OUTPUT_FORMATS.md`](docs/OUTPUT_FORMATS.md).

---

## Project layout

```
ansibleguard/
├── pyproject.toml                 # package metadata, dependencies, the `ansibleguard` entry point
├── requirements.txt
├── .gitignore
├── src/
│   └── ansibleguard/
│       ├── cli.py                 # the `ansibleguard` command itself
│       ├── config.py              # all shared paths/settings
│       ├── parser.py              # orchestrates one playbook's full analysis
│       ├── smells.py              # threshold logic — decides which smells fire
│       ├── detectors/             # detector modules; paper candidates share paper_candidates.py
│       ├── external/              # wrappers around gitleaks and ansible-lint
│       ├── report/                # csv_writer.py, text_writer.py, findings.py, sarif_writer.py
│       └── thresholds.csv         # every threshold value, one CSV
├── tests/
│   ├── fixtures/                  # hand-built YAML files, one per known bug/behavior
│   ├── test_detectors.py
│   ├── test_smells_thresholds.py
│   ├── test_cli.py
│   └── test_pipeline_end_to_end.py
└── docs/
    ├── HOW_IT_WORKS.md            # plain-language explanation of every stage and every smell
    ├── ARCHITECTURE.md            # call graph, file-by-file status, full test guide
    ├── OUTPUT_FORMATS.md          # the three output layers, in depth
    ├── CLI_STATUS.md              # CLI development history and the bugs found building it
    ├── PROJECT_STATUS.md          # the full detector bug-fixing log
    └── REFACTOR_PLAN.md           # the packaging roadmap this layout was built from
```

Everything under `src/ansibleguard/` is installed and importable
(`import ansibleguard`) from anywhere on the machine — this is a real
Python package, not a folder of scripts that only works from inside
itself. Every internal import is a relative package import
(`from .config import ...`), so there's no hidden dependency on your
current working directory.

---

## How it works, in three stages

Every file goes through exactly three stages, always in this order:

1. **Measure** (`parser.py` + `detectors/*.py`) — read the YAML, count
   things. No judgment calls yet, just numbers and lists.
2. **Judge** (`smells.py`) — compare those numbers against
   `thresholds.csv`. Cross a threshold, and it's a smell.
3. **Report** (`report/*.py`) — write the judged results to disk in every
   format described above.

If a number in a report ever looks wrong: check `Technical_Analysis.json`
first — that's the raw, pre-judgment output. If the raw number is already
wrong, the bug is in a detector. If the raw number is right but the smell
flag is wrong, the bug is in `smells.py`'s threshold logic instead.

The full plain-language walkthrough, including why one detector needs
`ruamel.yaml` instead of plain `PyYAML`, how `block`/`rescue`/`always`
nesting is handled, and how tasks get matched back to the right play, is
in [`docs/HOW_IT_WORKS.md`](docs/HOW_IT_WORKS.md).

---

## Running the tests

```bash
pytest tests/ -v
```

The test suite covers every detector (with a real fixture YAML per known
bug/behavior found during development), the CLI's file-discovery and
output-path logic, and a full end-to-end pipeline run. See
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the complete call graph
and a manual regression procedure if you want to verify something by hand
instead.

---

## Current status and known limitations

The detection logic and the packaging are both done and stable — this is
a genuinely runnable tool against real, arbitrary Ansible projects, not
just a fixed local fixture folder. What's still open:

- **Thresholds aren't empirically calibrated yet** — `thresholds.csv`'s
  values are a reasonable starting point (prior literature / judgment
  call), not the result of running against a large real-world corpus and
  picking a percentile.
- **No structured logging** — the tool uses `print()` throughout; fine for
  interactive use, not ideal for unattended runs over hundreds of files.
- **Some internal function/variable names are still in French**
  (file names themselves are English now; internal identifiers weren't in
  scope for the packaging refactor).
- **GitLeaks doesn't run on files that fail YAML parsing** — a known,
  accepted gap (see `docs/CLI_STATUS.md`), since GitLeaks' content-scan
  doesn't technically need valid YAML, but the pipeline currently skips
  those files entirely.
- **The SARIF severity/rule catalog is a stated judgment call**, not an
  empirically calibrated one — see `docs/OUTPUT_FORMATS.md` for the exact
  reasoning behind each `error`/`warning`/`note` assignment.

The full, detailed bug-fixing history — every bug found, how it was
confirmed, and how it was fixed — lives in
[`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md), and is worth reading
if you're about to touch a detector: several of the bugs found were subtle
enough (silently reading from the wrong dictionary, a placeholder string
masking a real check) that similar mistakes are easy to reintroduce
without realizing it.

---

## Where to look next

| I want to... | Read |
|---|---|
| Understand what the tool does and why, in plain language | `docs/HOW_IT_WORKS.md` |
| See the exact call graph and file-by-file status | `docs/ARCHITECTURE.md` |
| Understand the three output layers in depth | `docs/OUTPUT_FORMATS.md` |
| See the CLI's development history and the bugs it surfaced | `docs/CLI_STATUS.md` |
| See the full detector bug-fixing log | `docs/PROJECT_STATUS.md` |
| Understand why the project is packaged the way it is | `docs/REFACTOR_PLAN.md` |
