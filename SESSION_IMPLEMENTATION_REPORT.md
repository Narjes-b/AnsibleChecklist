# AnsibleGuard detector expansion — implementation report

## Purpose

In this work session, I consolidated the detector work on the
`sarif-validation-support` branch, preserved the resilient parsing and GitHub
SARIF pipeline, brought the newer refactoring-branch checks back into the
original `Narjes-b/AnsibleChecklist` repository, and expanded the tool using two
research sources.

My goal was not to inflate the detector count with renamed or unverifiable
rules. I treated a smell as implemented only when live code could produce a
normalized finding and the behavior had focused tests. Criteria requiring
runtime intent, external issue state, or unavailable service schemas remain
explicitly partial or missing.

## Repository and baseline

I verified that `origin` points to:

```text
https://github.com/Narjes-b/AnsibleChecklist.git
```

The branch already contained resilient YAML classification, external-tool
status handling, JSON findings, and SARIF validation. I kept that parsing path
instead of replacing it with the older `yaml.safe_load`-only behavior from the
refactoring branch.

## Work completed

### 1. Refactoring-branch detector integration

I fetched the current remote branches and identified five detector modules that
were newer than the local refactoring base:

- missing certificate validation;
- deprecated modules and alias/FQCN guidance;
- missing tags;
- shell commands that should use native modules;
- missing and unused handlers.

I integrated their parser metrics, assessed metrics, CSV columns, flat finding
rules, and SARIF output. I also added the refactoring branch's `inventory.md`.
The resilient `inspect_document()` classification remained the entry gate.

### 2. Configuration-smell paper candidates

I reviewed the supplied CSV based on *Does Your Configuration Code Smell?* and
separated already-covered, statically feasible, heuristic, and non-actionable
items. I implemented nine defensible checks in
`detectors/paper_candidates.py`:

- complex expressions;
- incomplete TODO/FIXME-style tasks;
- long source statements;
- unstructured roles/modules;
- empty abstractions;
- excessive block/rescue/always nesting;
- missing abstraction in large task files;
- broken local role dependencies;
- unguarded Jinja variables.

I used one shared traversal module because the checks need the same safe loader,
nested-task traversal, role discovery, line lookup, and visible-variable
collection. Each smell still has its own metric, detail list, rule ID, severity,
CSV column, and tests.

### 3. Mapping the 2025 code-review checklist

I extracted Table 7 from *Towards Understanding Code Review Practices for
Infrastructure-as-Code: An Empirical Study on OpenStack Projects*. I mapped all
38 criteria to live code rather than relying on names in documentation. The
first audit found 9 direct, 9 partial, and 20 missing criteria.

This audit exposed a concrete documentation/code mismatch: insecure permissions
was described in the old inventory but had no live detector on the branch. I
therefore marked it missing until I implemented it.

### 4. Additional checklist automation

I implemented seven source checks in `detectors/review_checklist.py`:

- insecure file/resource permissions;
- well-known default credentials;
- mutating commands without idempotency guards;
- silent failure suppression;
- role assignments that repeat defaults;
- shell environment exports;
- undocumented complex tasks.

I kept their scope narrow and explainable. For example, the permissions rule
uses permission bits rather than comparing strings, the credential rule skips
Jinja and Vault values, and the idempotency rule only claims recognized mutating
command families.

### 5. Strengthening partial criteria

I added four more file-level checks in `detectors/partial_checklist.py`:

- unused registered task results;
- shell variables absent from Ansible environment mappings;
- invalid YAML types for universal task attributes;
- invalid literal ports and negative retry/timing controls.

These checks improve unused-code, environment encapsulation, parameter-type,
and parameter-value coverage without claiming to replace runtime module
schemas.

### 6. Git-aware review checks

Several checklist items cannot be decided from an isolated YAML file. I added
`detectors/review_metadata.py`, which locates the Git root and analyzes HEAD
once per project. It checks:

- whether configuration changes include a release note;
- whether bug/fix commits include a bug reference;
- whether present `Depends-On` trailers are valid review URLs or Change-Ids;
- whether commit subjects and bodies follow the documented 50/72 format;
- whether a copyright notice was removed from a modified file header;
- whether production YAML changes include test/Molecule changes;
- whether defaults/vars changes include override-related test changes.

I integrated these findings after the per-file loop so a project-level issue is
not repeated for every YAML file. Each detail can point to its own changed file
in JSON and SARIF.

## Pipeline integration

For file-level checks, I followed the existing path:

```text
detector count/details
  -> parser.py raw metrics
  -> smells.py assessed metrics
  -> csv_writer.py per-file columns
  -> findings.py normalized rule/severity/message
  -> findings.json, findings.csv, findings.txt, and findings.sarif
```

For empty, vars, metadata, or otherwise structurally skipped YAML, the CLI runs
only the safe source/role bundles for project rollups. It does not misclassify
the file as a playbook or increment the structural-analysis count.

For Git-aware rules, `cli.analyze_path()` runs the detector once after file
analysis and adds a single review-metadata summary row.

## Test strategy

I added focused tests for every new family:

- `test_paper_candidates.py` covers all nine paper-derived checks and finding
  integration;
- `test_review_checklist.py` covers the seven security/reliability checks,
  including negative cases;
- `test_partial_checklist.py` covers used versus unused registers, environment
  scope, type validation, and numeric ranges;
- `test_review_metadata.py` creates real temporary Git repositories and checks
  both an incomplete review commit and a fully documented/tested commit;
- `test_cli_statuses.py` verifies that safe findings survive structural skips.

The final local suite now contains 163 passing tests. I also verified the
ansible-lint wrapper in a newly created temporary virtual environment.

## Documentation produced

I created and maintained the following documentation:

- `PAPER_SMELLS_IMPLEMENTATION.md` — algorithms for the first nine paper
  candidates;
- `CODE_REVIEW_CHECKLIST_COVERAGE.md` — all 38 review criteria with direct,
  partial, or missing status;
- `REVIEW_CHECKLIST_IMPLEMENTATION.md` — the seven additional source checks;
- `PARTIAL_AND_REVIEW_METADATA_IMPLEMENTATION.md` — strengthened partial and
  Git-aware checks;
- `MISSING_CHECKLIST_IMPLEMENTATION.md` — three formerly missing criteria;
- `ALL_DETECTED_SMELLS.md` — canonical live-code catalog of every active rule;
- updates to README, architecture, output-format, project-status, and inventory
  documents.

## Final measured state

- Active finding rules: **60**.
- Paper checklist coverage: **15 direct**, **18 partial**, **5 missing**.
- Tests: **163 passing**, including profile, classified-input, study-pipeline, and fresh-environment validation.
- Parsing behavior: resilient document classification preserved.
- Output behavior: all applicable rules flow to normalized CSV, JSON, text,
  and SARIF, with raw Git review metrics retained separately.
- Repository: original `Narjes-b/AnsibleChecklist` remote retained.

## Remaining checklist gaps

Three former gaps now have conservative automation: objective role-file
placement, linear use-before-definition ordering, and deprecated module-option
metadata. The five criteria still marked missing require information or intent
that the current analyzer cannot establish reliably:

- enforcing a blank-line convention before configuration groups;
- knowing which deprecated parameters must be set to `UNDEF` across versions;
- following changing OpenStack IRC/process conventions;
- proving cross-service parameter-value compatibility;
- proving that tests assert the assigned values correctly.

I left these visible instead of converting weak guesses into high-noise rules.
The next defensible improvement is configurable value/type schemas, followed by
execution-order modeling for known Ansible resource relationships.

## Final hardening pass

I completed the seven follow-up priorities as a single consistency pass. I
unified normalized outputs across JSON, CSV, text, and SARIF; added a raw Git
review metrics file; and made the legacy per-file text report include every
normalized rule. I replaced fallback locations in five older detector groups
with parser-derived YAML coordinates and locked their exact lines in tests.

I changed review metadata analysis from a latest-commit check to a complete
base-to-head PR analysis. The workflow now fetches full history, supplies both
SHAs, checks every commit message, and compares copyright content at committed
revisions. I also introduced one `.ansibleguard.yml` configuration surface for
threshold overrides, detector-specific values, externally supplied variables,
and rule suppressions.

For validation, I added cross-format contract tests and a reproducible corpus
runner. The 56-file corpus exposed false positives in empty variable files and
runtime/inventory variables; I corrected both sources and recorded the before
and after behavior in `CORPUS_VALIDATION.md`. Finally, I made local
`ansible-lint` resolution independent of the caller's PATH and moved its Ansible
temporary directory to a writable location.

I worked on all seven requested areas. I did not calculate an artificial
precision/recall percentage because the corpus has no ground-truth labels; that
is the only remaining research limitation, and it is documented explicitly.

## Commit history for this session

| Commit | Work |
|---|---|
| `07eeb22` | Added missing certificate validation, deprecated modules, and missing tags. |
| `b46e515` | Added shell/module and handler checks. |
| `1f7f928` | Added the smell inventory. |
| `7270f39` | Cleaned detector parser wiring. |
| `b902b6d` | Added nine configuration-paper detectors. |
| `a98aef1` | Added the 38-item paper coverage matrix. |
| `54a1570` | Added seven additional review-checklist detectors and the canonical catalog. |
| `98ac114` | Added four partial-coverage rules, seven Git-aware rules, and this complete implementation record. |
