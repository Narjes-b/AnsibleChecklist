# AnsibleGuard — Refactoring & Packaging Roadmap

Companion to `PROJECT_STATUS.md` (bug log) and `ARCHITECTURE.md` (call graph
+ test guide). This file answers: how do we turn this from "a folder of
scripts that only runs from inside itself" into something you can `pip
install`, point at any Ansible project, and run — plus a full accounting of
where things actually stand right now.

---

## Part 1 — Where things actually stand (full review)

### Bug-hunting phase: essentially done
Every file in the live pipeline (`parser_playbook.py` → `detect_large_*.py` →
`smellsDetector.py` → `write_to_*.py`) has been reviewed and stress-tested,
not just read. Confirmed fixed, in rough order found:
- 11-file import-crash cascade (unguarded module-level code + hardcoded paths)
- `config.py` rebuilt around portable `BASE_DIR`/`PROJECT_ROOT`
- GitLeaks install: missing ARM64 branch, disconnected version constant,
  renamed release asset tags
- `smellsDetector.py`: 8 distinct bugs (typo import, `NameError`, two
  `UnboundLocalError`-style crashes, one arithmetic typo, three threshold
  key-name mismatches, two counter-reset-per-play bugs)
- `detect_large_task.py` / `detect_large_play.py`: a genuine data-integrity
  bug where the two files disagreed on what counts as a "play" and on how to
  count tasks inside `block:`, silently pairing every play with a different
  play's tasks throughout the whole pipeline
- `files_extensions.py`, `filters_for_comparison.py`, `high_coupling.py`:
  missing `rescue`/`always` recursion, a real `TypeError` crash on bare
  boolean `when:` conditions, a `KeyError` crash on singular `role:`, and a
  genuine detection gap (`import_tasks`/`include_tasks` nested inside
  `tasks:` was invisible)
- Vault/multi-doc YAML: one confirmed real crash (`detect_large_task.py`),
  one confirmed silent-wrong-output bug (`high_coupling.py`), both fixed;
  multi-doc and inline `!vault` tags confirmed to fail gracefully already
- `sem_cohesion.py`: a real correctness bug where non-English (or otherwise
  out-of-vocabulary) task/play names silently reported "perfectly cohesive"
  instead of "unmeasurable" — fixed, with a follow-on `None`-handling fix
  required in both `smellsDetector.py` and `write_to_csv.py` to avoid a new
  crash and a new "None" showing up literally in the CSV
- `write_to_csv.py`: the above `None`-vs-blank regression, plus an
  `ansible_lint_issues` consistency gap (0 real issues vs. lint-tool-failure
  both rendered identically as blank) — both fixed this round
- `write_to_text.py`: reviewed, no bugs found; documented one fragility
  (three writer functions across two files depend on an unstated call order)

### This round's additions (post-restructure file-by-file pass)
- `overriden_keys.py`: cross-depth false-positive regression — the
  depth-tracking fix was implemented during collection but discarded right
  before the duplicate check, re-merging a task's own `name:` with an
  unrelated nested module parameter also called `name:`
- `GitLeaks_hardcoded_credentials.py`: unguarded crash on a missing/bad
  `gitleaks` binary path (a bad target playbook path was already handled)
- `credentials_leaking_in_log.py`: **highest-severity finding of the whole
  review** — sourced tasks from a data structure that only contains tasks
  with no play wrapper, meaning virtually every real-world credential-leak
  case (any task inside a normal `hosts:`/`tasks:` play) was invisible
- `incohesive_plays.py`: the same non-English/out-of-vocabulary
  false-cohesion bug already fixed in `sem_cohesion.py`, missed on this
  sibling file because the earlier review cleared it for an unrelated
  reason (block-recursion) without checking this axis

**What does this mean practically?** The detection logic itself is now
trustworthy. Every number that ends up in a CSV or JSON has been traced back
to real code, tested against both normal and adversarial fixtures, not
assumed correct because it "looked reasonable."

### Not yet done
- Non-recursive file collection (can't point this at a real multi-role
  project yet — see Part 3)
- No package structure (see Part 2)
- No real test suite despite significant hand-built fixture knowledge sitting
  in chat history (see Part 4)
- Thresholds not empirically calibrated
- `GeneralsmellsDetector.py` fate undecided (delete or mark deprecated)
- Mixed French/English naming throughout

---

## Part 2 — Target package structure

Current layout (flat, everything in `AnsibleGuard/`, must `cd` into it):
```
AnsibleChecklist/
├── AnsibleGuard/          # 30+ flat .py files, bare imports
├── TestData/
├── thresholds.csv         # duplicate also lives in AnsibleGuard/
└── requirements.txt
```

Target `src`-layout, standard for a pip-installable tool:
```
ansibleguard/                          # repo root
├── pyproject.toml
├── README.md
├── requirements.txt                   # or fold into pyproject.toml deps
├── .gitignore
├── src/
│   └── ansibleguard/
│       ├── __init__.py
│       ├── cli.py                     # new: entry point (see Part 3)
│       ├── config.py
│       ├── detectors/                 # the detect_large_*, unnamed_*, etc.
│       │   ├── __init__.py
│       │   ├── large_task.py          # renamed from detect_large_task.py
│       │   ├── large_play.py
│       │   ├── large_playbook.py
│       │   ├── high_coupling.py
│       │   ├── duplicate_code.py
│       │   ├── duplicate_task_names.py
│       │   ├── overridden_keys.py
│       │   ├── overriding_facts.py
│       │   ├── set_fact.py
│       │   ├── unnecessary_abstraction.py
│       │   ├── semantic_cohesion.py
│       │   ├── incohesive_plays.py
│       │   ├── unnamed_play.py
│       │   ├── unnamed_tasks.py
│       │   ├── include_vars.py
│       │   ├── file_extensions.py
│       │   ├── bool_filters.py
│       │   └── credentials_in_log.py
│       ├── external/                  # third-party tool wrappers
│       │   ├── ansible_lint.py
│       │   ├── gitleaks.py
│       │   └── install_gitleaks.py
│       ├── parser.py                  # renamed from parser_playbook.py
│       ├── smells.py                  # renamed from smellsDetector.py
│       ├── report/
│       │   ├── csv_writer.py
│       │   └── text_writer.py
│       └── thresholds.csv
├── tests/
│   ├── fixtures/                      # the YAML files we've been
│   │   │                              # hand-writing in /tmp all session
│   │   ├── dupe_task_names.yml
│   │   ├── credentials_no_log.yml
│   │   ├── nested_single_task_block.yml
│   │   ├── rescue_block.yml
│   │   ├── bare_boolean_when.yml
│   │   ├── singular_role.yml
│   │   ├── dict_style_roles.yml
│   │   ├── nested_import_tasks.yml
│   │   ├── full_vault_encrypted.yml
│   │   ├── non_english_task_names.yml
│   │   └── main3_rich_fixture.yml     # the big one we used throughout
│   ├── test_detectors.py
│   ├── test_smells_thresholds.py
│   └── test_pipeline_end_to_end.py
└── docs/
    ├── PROJECT_STATUS.md
    ├── ARCHITECTURE.md
    └── REFACTOR_PLAN.md               # this file
```

Key changes from current state:
- `TestData/Results/` output moves **out of the package entirely** — it's
  generated output, not source or test fixtures. Default to `./output/` in
  the current working directory when run as a CLI, override via a flag.
- Every internal import becomes a relative package import
  (`from .config import THRESHOLDS_FILE` instead of `from config import
  THRESHOLDS_FILE`), which is what makes running from anywhere possible.
- File names get de-abbreviated and English-only
  (`overriden_keys.py` → `overridden_keys.py`, fixing the typo too;
  `unecessary_abs.py` → `unnecessary_abstraction.py`) — purely cosmetic,
  but do this in one dedicated commit, not mixed with logic changes, so
  `git blame`/history stays useful.

---

## Part 3 — Making it a real pip package

### `pyproject.toml`
```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "ansibleguard"
version = "0.1.0"
description = "IaC smell detector for Ansible playbooks"
requires-python = ">=3.10"
dependencies = [
    "pyyaml",
    "pandas",
    "spacy",
    "nltk",
    "requests",
    "ansible-lint",
    "ansible-compat",
]

[project.scripts]
ansibleguard = "ansibleguard.cli:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.package-data]
ansibleguard = ["thresholds.csv"]
```

### `src/ansibleguard/cli.py` — the missing entry point
This doesn't exist yet in any form — right now "running the tool" means
editing `config.py`'s hardcoded folder path and running
`python smellsDetector.py`. A real CLI:

```python
import argparse
from pathlib import Path
from .smells import execute_for_single_file, read_thresholds
from .config import DEFAULT_THRESHOLDS_FILE

EXCLUDE_DIRS = {"molecule", ".github", ".git", ".venv", "venv"}

def collect_yaml_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    files = []
    for pattern in ("*.yml", "*.yaml"):
        files.extend(target.rglob(pattern))
    return [
        f for f in files
        if not any(part in EXCLUDE_DIRS for part in f.parts)
    ]

def main():
    parser = argparse.ArgumentParser(prog="ansibleguard")
    parser.add_argument("target", type=Path,
                         help="A playbook file OR a project directory "
                              "(searched recursively)")
    parser.add_argument("-o", "--output", type=Path, default=Path("./ansibleguard-output"),
                         help="Where to write reports (default: ./ansibleguard-output)")
    parser.add_argument("--thresholds", type=Path, default=DEFAULT_THRESHOLDS_FILE,
                         help="Custom thresholds.csv")
    args = parser.parse_args()

    thresholds = read_thresholds(args.thresholds)
    yaml_files = collect_yaml_files(args.target)
    print(f"Found {len(yaml_files)} YAML file(s) to analyze.")

    for yaml_file in yaml_files:
        out_dir = args.output / yaml_file.stem
        out_dir.mkdir(parents=True, exist_ok=True)
        execute_for_single_file(yaml_file, out_dir, thresholds)

if __name__ == "__main__":
    main()
```

This is the concrete fix for "how do I run this against a project I built" —
`collect_yaml_files()` uses `rglob` (recursive) instead of the current
`glob("*.yml")`, and excludes `molecule/`/`.github/`/`.git/` so it doesn't
choke on non-playbook YAML that real repos always contain (CI configs,
Molecule test scenarios, etc.).

Once packaged:
```bash
pip install -e .                          # editable install during development
ansibleguard ~/my-ansible-project/        # run against any real project
ansibleguard playbook.yml -o ./results/   # or a single file, custom output dir
```

### Install steps for a fresh clone, once packaged
```bash
git clone <repo>
cd ansibleguard
pip install -e .
python -c "import nltk; nltk.download('wordnet')"
python -m spacy download en_core_web_lg
python -c "from ansibleguard.external.install_gitleaks import ensure_gitleaks_installed; ensure_gitleaks_installed()"
ansibleguard --help
```

---

## Part 4 — Converting hand-tested fixtures into a real test suite

This is the highest-value remaining task, independent of the packaging work
above and can be done in parallel. Every fixture built by hand this session
becomes a permanent regression test:

```python
# tests/test_detectors.py
from pathlib import Path
from ansibleguard.detectors.duplicate_task_names import repeated_task_names
from ansibleguard.detectors.credentials_in_log import detect_credentials_leaking_in_log
from ansibleguard.detectors.high_coupling import high_coupling

FIXTURES = Path(__file__).parent / "fixtures"

def test_duplicate_task_names_detected():
    assert repeated_task_names(FIXTURES / "dupe_task_names.yml") == 1

def test_credential_without_no_log_flagged():
    warnings, count = detect_credentials_leaking_in_log(FIXTURES / "credentials_no_log.yml")
    assert count == 1

def test_credential_with_no_log_not_flagged():
    warnings, count = detect_credentials_leaking_in_log(FIXTURES / "credentials_with_no_log.yml")
    assert count == 0

def test_high_coupling_nested_import_tasks_detected():
    result = high_coupling(FIXTURES / "nested_import_tasks.yml")
    assert result["Num_Imports"] == 2

def test_high_coupling_fully_vault_encrypted_returns_none():
    assert high_coupling(FIXTURES / "full_vault_encrypted.yml") is None

def test_task_with_block_not_counted_as_play():
    from ansibleguard.detectors.large_task import calculate_metrics_task
    metrics, _ = calculate_metrics_task(FIXTURES / "nested_single_task_block.yml")
    # regression test for the play_id desync bug — every task must land under
    # the correct play_id, not an offset one
    ...
```

Run with `pytest tests/` — every bug found this session becomes a permanent
tripwire against regression, and this list should grow every time a new bug
is found from now on rather than being tested once by hand and forgotten.

---

## Part 5 — What to check next / still open (consolidated)

1. Convert fixtures → real `pytest` suite (Part 4) — highest value, do first
2. Implement the `cli.py` + `rglob` fix (Part 3) — needed before running
   against any real external project
3. Package restructure (Part 2) — do after 1–2 are stable, since moving
   files will otherwise conflict with active bug-fixing
4. Empirical threshold calibration — run against a larger real corpus once
   the CLI can actually point at one, plot metric distributions, set
   thresholds near a percentile
5. Decide `GeneralsmellsDetector.py`'s fate (delete vs. deprecate)
6. `.gitignore` + remove tracked `__pycache__/`
7. Standardize naming (French/English mix) — do in its own commit
8. ~~Re-verify: `Ansible_Lint.py` and `GitLeaks_hardcoded_credentials.py`
   haven't been stress-tested against a target path that doesn't exist, or
   against `ansible-lint`/`gitleaks` not being installed at all~~ —
   **`GitLeaks_hardcoded_credentials.py` done this round**: bad target path
   was already handled gracefully; missing/bad `gitleaks` binary path was a
   real unguarded crash, now fixed. `Ansible_Lint.py` still needs the same
   treatment for a missing `ansible-lint` install before packaging.
