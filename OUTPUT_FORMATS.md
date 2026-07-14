# AnsibleGuard — Output Formats: The Three Ways Results Are Presented

Companion to `ARCHITECTURE.md` (call graph), `PROJECT_STATUS.md` (bug
log), and `CLI_STATUS.md` (CLI development log). This file answers one
question: **when you run the `ansibleguard` command against a project,
what do you actually get, and which of the output files should you look
at for what.**

> **Note:** the project is now a real installable package
> (`src/ansibleguard/...`, `pip install -e .`) — `cli.py` below is
> `ansibleguard/cli.py`, invoked via the installed `ansibleguard` command
> (e.g. `ansibleguard ~/my-project/ -o ./results/`), not
> `python3 cli.py`. Historical packaging details are recorded in
> `CLI_STATUS.md`.

There are three layers, each answering a different question, aimed at a
different consumer. They're built from the exact same underlying data —
nothing is computed twice — they're just three different *shapes* of the
same analysis, because "a human reviewing one file" and "a CI pipeline
deciding whether to fail a PR" need genuinely different things.

```
ansibleguard/cli.py analyze_path(target, output_root)
  │
  ├── LAYER 1 — per-file detailed reports (one set per analyzed file)
  │     output_root/<mirrored/path/to/file>/
  │       ├── Technical_Analysis.json   (raw metrics, before threshold logic)
  │       ├── IaC_Smells.csv            (one-row summary for this file)
  │       ├── Play_Level_Analysis.txt   (human-readable per-play/task breakdown)
  │       ├── ansiblelint.txt
  │       └── gitleaks.txt
  │
  ├── LAYER 2 — project-wide rollup (one file each, covering every analyzed file)
  │     output_root/summary.csv
  │
  └── LAYER 3 — normalized findings (each covers file and Git review rules)
        output_root/findings.json
        output_root/findings.csv
        output_root/findings.txt
        output_root/findings.sarif
        output_root/review_metrics.json
```

---

## Layer 1 — Per-file detailed reports

**Question it answers:** "What exactly is going on in *this one file*?"

**Who it's for:** A human doing a deep-dive on a specific playbook — the
original design of this whole project, before the CLI/PR-bot goal existed,
and still the right tool for that job. `Technical_Analysis.json` is the
ground truth (raw metrics, before any threshold decides pass/fail —
`ARCHITECTURE.md`'s "Data flow" section explains why this is the first
place to look when a number seems wrong). `IaC_Smells.csv` and
`Play_Level_Analysis.txt` are two different renderings of the same
threshold-evaluated decision, for spreadsheet vs. plain-text reading.

**Nothing about this layer changed** when Layers 2 and 3 were added —
every file here is written exactly as it always was, by the exact same
`execute_for_single_file()` call. This layer is untouched, on purpose:
plenty of existing tests and workflows already depend on its exact shape.

**Downside, which is exactly why Layers 2 and 3 exist:** with 42 files
analyzed, that's 42 separate directories to open by hand to answer "which
files actually need attention." There's no ranking, no aggregate view, and
(before this round) no real per-line location for most findings.

---

## Layer 2 — `summary.csv`: the project-wide rollup

**Question it answers:** "Out of everything just analyzed, which files
are actually worth looking at, and how bad are they relative to each
other?"

**Who it's for:** A human (or a script) doing a first pass over a whole
project, before diving into any one file's Layer 1 report.

**Shape:** one row per analyzed file, pre-sorted worst-first (most errors,
then most warnings, then most total findings):

| file | errors | warnings | notes | total |
|---|---|---|---|---|
| `roles/apache/tasks/main.yml` | 2 | 0 | 1 | 3 |
| `roles/nginx/tasks/main.yml` | 0 | 0 | 1 | 1 |

This is the cheapest of the three layers to build — it's a `csv.DictWriter`
call over data `report/findings.py` already computed for Layer 3 — but it's the
one that directly answers the most common real question ("where do I even
start") without needing any tooling beyond a spreadsheet.

---

## Layer 3 — normalized JSON, CSV, text, and SARIF findings

**Question it answers:** "Give me every individual problem, as one flat
list, with enough detail that a machine (not a human reading prose) can
act on each one independently."

**Who it's for:** CI pipelines, GitHub's Code Scanning feature, and the
eventual AI-filtering layer the whole CLI effort exists to support (see
`CLI_STATUS.md`'s opening section on the actual goal). This is the layer
that didn't exist before this round, and it's the one that makes the
PR-bot use case actually reachable.

### The shape

Both files are built from `report/findings.py`'s `build_findings_list()`, which
flattens everything (playbook-level counts, per-play/per-task smells,
GitLeaks findings, ansible-lint issues) down to one consistent record:

```json
{
  "file": "roles/apache/tasks/main.yml",
  "line": 7,
  "rule_id": "credentials-leaking-in-log",
  "severity": "error",
  "message": "Task 'Set apache admin password' handles a sensitive value but does not use no_log: true — secrets may leak in logs."
}
```

`findings.json` is the canonical list. `findings.csv` has the same five fields
for spreadsheets, `findings.txt` renders the same records for humans, and SARIF
maps the same records to Code Scanning. `review_metrics.json` retains raw Git
review-range counts and details. The normalized section appended to each
`Play_Level_Analysis.txt` uses the same records, so newer detectors are visible
in the legacy human-readable report too.

### Why SARIF specifically

SARIF (Static Analysis Results Interchange Format) is an OASIS JSON
standard that essentially every static-analysis tool now speaks — CodeQL,
ansible-lint itself, Bandit, Semgrep, Trivy. The reason it's worth the
extra format here, not just `findings.json`: **GitHub's Code Scanning
feature natively consumes SARIF.** Upload a `.sarif` file from a CI
workflow (`github/codeql-action/upload-sarif`) and GitHub renders every
result as a real inline PR annotation — the same red/yellow squiggle
experience as any other code-scanning tool — automatically, with no bot
code needed to post comments via the GitHub API.

That's a materially different architecture than "a bot reads our JSON and
decides what to comment." SARIF gets you the annotation UI for free, for
the rule-based layer, before any AI involvement. The AI layer's job then
narrows to something more tractable: filtering *which* SARIF results are
worth surfacing, or drafting a suggested fix — not building comment-posting
infrastructure from scratch.

`report/sarif_writer.py`'s output has been validated against the actual
downloaded OASIS 2.1.0 schema (`jsonschema.validate()`), not just
eyeballed — this is also how a stale, commonly-cited schema URL was
caught (the old `oasis-tcs/sarif-spec/master/Schemata/...` path 404s now;
the current one is `oasis-tcs/sarif-spec/main/sarif-2.1/schema/...`).

One detail worth knowing if you're debugging a SARIF file that isn't
annotating a PR correctly: `artifactLocation.uri` must be **relative to
the repo root**, not an absolute path — that's the only way GitHub can map
an annotation back to the right file in a PR diff. `_to_repo_relative()`
in `report/sarif_writer.py` handles this.

### Severity — what `error`/`warning`/`note` actually mean here

This is a judgment call, stated as such, not an empirically calibrated
scale — worth being upfront about, the same way `thresholds.csv`'s values
are documented as not yet empirically calibrated against a labeled corpus.
`report/findings.py`'s `RULE_CATALOG` groups by *consequence*:

- **`error`** — real security/correctness problems: `hardcoded-credentials`
  (GitLeaks), `credentials-leaking-in-log`, `overriden-keys` (a duplicate
  key silently discards data — a real bug, not style), and
  `broken-role-dependency`, `insecure-permissions`, and
  `default-credentials`, `invalid-task-attribute-type`, and
  `invalid-numeric-value`.
- **`warning`** — don't break anything today, but increase bug risk:
  `missing-bool-filters`, `overriding-facts`, `duplicated-code`,
  `high-coupling`, `large-playbook`/`complex-playbook`/`large-play`/
  `large-task`, `complex-expression`, `incomplete-task`,
  `unstructured-module`, `empty-abstraction`, `excessive-nesting`,
  `missing-abstraction`, `unguarded-variable`, ansible-lint's own findings (no clean severity field to
  inherit from most ansible-lint output modes), plus
  `non-idempotent-command`, `silent-error-suppression`, and
  `shell-environment-export`, `unscoped-shell-variable`,
  `invalid-depends-on-reference`, `removed-copyright-notice`,
  `missing-test-update`, and `untested-override-change`.
- **`note`** — style/maintainability, low consequence: `unnamed-play`/
  `unnamed-task`, `long-task-name`, `inconsistent-naming-convention`,
  `missing-file-extension`, `unnecessary-abstraction`,
  `long-statement`,
  `redundant-default-value`, `undocumented-complex-task`,
  `unused-registered-variable`, `missing-release-note`,
  `missing-bug-reference`, `commit-message-format`,
  `incohesive-playbook`/`incohesive-play` (a soft NLP-based signal that
  can misfire on real, fine code — deliberately not weighted as `error`).

The catalog lives in one place (`report/findings.py`'s `RULE_CATALOG` dict), not
scattered through logic, so retuning it later is a data change, not a
code change. The project's own `Literature_review/` sources are the right
evidence base for a real calibration pass, once the detection engine
itself has stabilized further — this table is a reasonable starting point,
not a finished answer.

### Real line numbers — what's covered and what isn't yet

As of this round, real per-line location data (via `ruamel.yaml`, not a
line-1 fallback) is available for: `overriden-keys`, `unnamed-play`,
`unnamed-task`, `large-play`, `large-task`, `long-task-name`,
`inconsistent-naming-convention`, `credentials-leaking-in-log`, `missing-tags`,
`deprecated-module`, `missing-validate-certs`, `shell-instead-of-module`,
`missing-handler`, and `unused-handler`. GitLeaks
and ansible-lint findings already carried real line data from those tools
themselves. Playbook-level counts (`large-playbook`, `high-coupling`, etc.)
are inherently file-wide, not tied to one line, so `line: 1` there is
arguably already correct, not a gap.

---

## Quick reference: which layer for which question

| Question | Layer |
|---|---|
| "What exactly is wrong with this one file?" | 1 — `Technical_Analysis.json` / `Play_Level_Analysis.txt` |
| "Which files in this project need attention first?" | 2 — `summary.csv` |
| "Feed this into CI / GitHub Code Scanning / an AI filtering layer" | 3 — normalized JSON/CSV/text/SARIF |
