# Canonical catalog of active AnsibleGuard smells

This is the canonical list of rules that are active in the current branch.
Unlike historical inventories, inclusion here requires both a live
`RULE_CATALOG` entry and a path that can produce a finding. There are **46
active rules**: 44 internal rules, one GitLeaks rule, and one general
`ansible-lint` rule.

The paper's 38 review criteria and these 46 rules are not one-to-one. One paper
criterion can need several narrow detectors, while many existing size, naming,
cohesion, and security smells are outside that paper checklist. This is why the
tool can have more active smells than directly covered paper criteria.

## Security and correctness

| Rule | Severity | How it is detected | Main limitation |
|---|---|---|---|
| `hardcoded-credentials` | error | GitLeaks scans the target for known secret formats and entropy patterns. | Requires the GitLeaks binary; examples can trigger. |
| `credentials-leaking-in-log` | error | Sensitive-keyword tasks are checked for task/play-level `no_log: true`. | Keyword heuristic cannot understand every custom secret. |
| `insecure-permissions` | error | File-module modes are parsed; world-write and world-readable sensitive resources are reported. | Variable-computed modes are unresolved. |
| `default-credentials` | error | Credential-like keys are compared with conservative well-known default values. | Product-specific defaults outside the list are missed. |
| `missing-validate-certs` | warning | `uri`/`get_url` tasks explicitly setting `validate_certs: false` are reported. | Templated values cannot be evaluated. |
| `overriden-keys` | error | Ruamel/source-depth analysis finds duplicate YAML keys inside the same task. | Complex YAML constructs may reduce source-span accuracy. |
| `missing-handler` | error | `notify` names are cross-referenced with handlers defined in the file. | Included/role handlers outside the file are invisible. |
| `broken-role-dependency` | error | Local role metadata is graphed to find missing roles, self-dependencies, and cycles. | External qualified roles are assumed resolvable. |
| `missing-bool-filters` | warning | Bare boolean-looking `when` terms without `| bool` are identified recursively. | Static expression splitting is heuristic. |
| `overriding-facts` | warning | Repeated `set_fact` assignments with different values are compared. | Assignments in dynamic includes are invisible. |
| `unguarded-variable` | warning | Jinja references are compared with visible vars/defaults/register/set_fact definitions and guards. | Inventory, facts, includes, and extra-vars can cause false positives. |
| `non-idempotent-command` | warning | Recognized mutating shell/command/raw operations must have `creates`, `removes`, or change guards. | Arbitrary shell behavior is not interpreted. |
| `silent-error-suppression` | warning | `ignore_errors: true`/`failed_when: false` without `register` is reported. | Independent warning paths cannot be associated reliably. |
| `shell-environment-export` | warning | `export NAME=value` in command-like tasks is detected and mapped to `environment:`. | A self-contained shell export can be intentional. |

## Size, structure, and maintainability

| Rule | Severity | How it is detected | Main limitation |
|---|---|---|---|
| `large-playbook` | warning | Playbook LOC, play count, average play size, and nested-task count are compared with thresholds. | Thresholds need corpus calibration. |
| `complex-playbook` | warning | Combines size/task conditions with import and role coupling. | Composite thresholds are heuristic. |
| `insufficient-modularization` | warning | High playbook LOC together with many plays triggers the rule. | Small monoliths may remain below thresholds. |
| `large-play` | warning | Per-play LOC, task count, and average task size are thresholded. | Generated/simple tasks can inflate size. |
| `large-task` | warning | Per-task LOC is compared with the task-size threshold. | LOC does not equal semantic complexity. |
| `high-coupling` | warning | Imports, includes, and roles—including FQCN forms—are counted. | It counts links but not their architectural necessity. |
| `duplicated-code` | warning | Canonicalized task bodies, excluding names, are compared for exact duplication. | Semantically equal but differently ordered bodies may be missed. |
| `deprecated-modules` | warning | Module names are checked against curated deprecation and alias/FQCN maps. | The mapping must be maintained with Ansible releases. |
| `shell-instead-of-module` | warning | Common shell command patterns are mapped to native Ansible modules. | Complex or uncommon commands are not understood. |
| `unused-handler` | warning | Defined handler names not present in collected notifications are reported. | Notifications from other files are invisible. |
| `complex-expression` | warning | Jinja/condition operators, filters, comparisons, grouping, indexing, and length form a score. | Syntactic complexity can overstate difficulty. |
| `incomplete-task` | warning | Source lines containing TODO/FIXME/HACK/XXX are reported. | Intentional roadmap comments still trigger. |
| `unstructured-module` | warning | Role standard directories are checked for required `main.yml`/`.yaml` entry points. | Custom layouts are reported. |
| `empty-abstraction` | warning | Empty documents and empty block/rescue/always sections are detected. | Scaffolding placeholders are intentionally flagged. |
| `excessive-nesting` | warning | Recursive block/rescue/always depth greater than three is reported. | Depth alone does not measure conceptual complexity. |
| `missing-abstraction` | warning | More than ten leaf tasks without role/task includes triggers the rule. | Intentionally self-contained files may trigger. |
| `redundant-default-value` | note | Role defaults are compared with exact task/play vars and `set_fact` values. | Only same-role static values are available. |

## Style, naming, documentation, and semantics

| Rule | Severity | How it is detected | Main limitation |
|---|---|---|---|
| `unnamed-play` | note | Plays without a nonblank `name` are counted with source lines. | Imported/generated names are not resolved. |
| `unnamed-task` | note | Recursive task metrics identify missing task names. | Dynamic task generation is outside static YAML. |
| `long-task-name` | note | Task-name length is compared with the configured threshold. | Long descriptive names can be legitimate. |
| `inconsistent-naming-convention` | note | Excess punctuation/special characters in play/task names are counted. | This is not a full team naming policy. |
| `duplicate-task-names` | note | Exact task-name frequencies are counted. | Same names in different plays can be intentional. |
| `missing-tags` | note | Leaf tasks lacking own or inherited tags are reported. | Small playbooks may not need selective execution. |
| `missing-file-extension` | note | File-looking task attributes without suffixes are detected. | Extensionless valid files such as `Dockerfile` exist. |
| `long-statement` | note | Physical source lines longer than 120 characters are reported. | URLs/generated values may be unavoidable. |
| `unnecessary-abstraction` | note | A block wrapping exactly one child task is counted recursively. | Wrappers used for attribute inheritance may be intentional. |
| `unnecessary-set-fact` | note | `set_fact` definitions not referenced in visible Jinja expressions are reported. | Indirect and cross-file uses can be missed. |
| `unused-include-vars` | note | Included variable keys are compared with visible Jinja references. | Indirect/cross-file references can be missed. |
| `undocumented-complex-task` | note | Complex/deep tasks without an immediately preceding comment are reported. | Comment presence does not prove quality. |
| `incohesive-playbook` | note | spaCy similarity across play/task names estimates file-level semantic cohesion. | Non-English/out-of-vocabulary names can be unmeasurable. |
| `incohesive-play` | note | The same semantic similarity calculation is scoped per play. | Short names produce noisy similarity. |

## External aggregate rule

| Rule | Severity | How it is detected | Main limitation |
|---|---|---|---|
| `ansible-lint-issue` | warning | Every issue returned by the integrated `ansible-lint` JSON scan becomes a finding. | Requires the executable and compatible runtime dependencies. |

## Output path

Every rule above is normalized by `report/findings.py` to `file`, `line`,
`rule_id`, `severity`, and `message`. The same normalized records feed
`findings.json` and SARIF, while corresponding counts are exposed in per-file
technical JSON and CSV. External findings survive structural YAML skips; safe
source/role checks also contribute project rollup findings for skipped YAML
documents.

For implementation details of the two recent detector bundles, see
`PAPER_SMELLS_IMPLEMENTATION.md` and `REVIEW_CHECKLIST_IMPLEMENTATION.md`. For
the 38-criterion paper comparison, see `CODE_REVIEW_CHECKLIST_COVERAGE.md`.
