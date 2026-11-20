# Canonical catalog of active AnsibleGuard smells

This explanatory catalog is subordinate to
[`RULE_REFERENCE.generated.md`](../../RULE_REFERENCE.generated.md), which CI
generates from `RULE_CATALOG`. The executable catalog currently contains **76
rules: 64 active, 12 experimental, and 0 disabled**. Experimental findings are
low-confidence signals and must not be described as independently validated.

The paper's 38 review criteria and these 76 rules are not one-to-one. One paper
criterion can need several narrow detectors, while many existing size, naming,
cohesion, and security smells are outside that paper checklist. This is why the
tool can have more active smells than directly covered paper criteria.

Execution profiles do not change this canonical catalog. They select explicit
subsets: 67 internal rules in `snapshot-source`, a provisional 8-rule
`research-core`, 59 disjoint `extended-ansible` rules, and 7 `review-range`
rules; the 2 aggregate external rules are technical-only. See
[PROFILE_REFERENCE.generated.md](../../PROFILE_REFERENCE.generated.md) for the exact generated mapping.

## Security and correctness

| Rule | Severity | How it is detected | Main limitation |
|---|---|---|---|
| `hardcoded-credentials` | error | GitLeaks scans the target for known secret formats and entropy patterns. | Requires the GitLeaks binary; examples can trigger. |
| `credentials-leaking-in-log` | error | Sensitive-keyword tasks are checked for task/play-level `no_log: true`. | Keyword heuristic cannot understand every custom secret. |
| `insecure-permissions` | error | File-module modes are parsed; world-write and world-readable sensitive resources are reported. | Variable-computed modes are unresolved. |
| `default-credentials` | error | Credential-like keys are compared with conservative well-known default values. | Product-specific defaults outside the list are missed. |
| `plaintext-sensitive-variable` | warning | Literal sensitive values in vars/defaults/group/host vars are reported without copying the value. | v0.0.4: integer/float values excluded; 14 new non-secret suffix patterns added (ttl, timeout, backend, mode, etc.). |
| `missing-validate-certs` | warning | `uri`/`get_url` tasks explicitly setting `validate_certs: false` are reported. | Templated values cannot be evaluated. |
| `overriden-keys` | error | Ruamel/source-depth analysis finds duplicate YAML keys inside the same task. | Complex YAML constructs may reduce source-span accuracy. |
| `missing-handler` | error | `notify` names are cross-referenced with handlers defined in the file. | Included/role handlers outside the file are invisible. |
| `broken-role-dependency` | error | Role metadata is graphed to find self-dependencies and dependency cycles. Missing-local-role check removed in v0.0.4. | External Galaxy/collection dependencies are not resolved locally; only cycles and self-dependencies are reliable. |
| `missing-bool-filters` | warning | Bare boolean-looking `when` terms without `| bool` are identified recursively. | Static expression splitting is heuristic. |
| `overriding-facts` | warning | Repeated `set_fact` assignments with different values are compared. | Assignments in dynamic includes are invisible. |
| `unguarded-variable` | warning | Jinja references are compared with visible vars/defaults/register/set_fact definitions and guards. | Inventory, facts, includes, and extra-vars can cause false positives. |
| `non-idempotent-command` | warning | Recognized mutating shell/command/raw operations must have `creates`, `removes`, or change guards. | Arbitrary shell behavior is not interpreted. |
| `silent-error-suppression` | warning | `ignore_errors: true`/`failed_when: false` without `register` is reported. | Independent warning paths cannot be associated reliably. |
| `shell-environment-export` | warning | `export NAME=value` in command-like tasks is detected and mapped to `environment:`. | A self-contained shell export can be intentional. |
| `variable-use-before-definition` | warning | A Jinja/condition reference is compared with later `register` and `set_fact` definitions in the same linear task section. | Dynamic control flow and external definitions are deliberately excluded. |
| `role-variable-precedence-collision` | warning | The same role key in defaults/main and vars/main is reported because vars prevents normal overrides. | Deliberate fixed role vars can be intentional. |
| `become-scope-too-broad` | warning | `become: true` at play level is detected; all tasks in the play inherit root privilege. | Task-level become cannot be suppressed without explicit `become: false`. |
| `vault-inline-overload` | note | Roles with many inline `!vault \|` values are reported; loading from a dedicated vault file is preferred. | Threshold is heuristic and may need project-specific tuning. |
| `yaml-truthy-value` | warning | YAML boolean-like values `yes`/`no`/`on`/`off` are detected; `true`/`false` is required by YAML 1.2. | Promoted from the `yaml[truthy]` ansible-lint rule. |

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
| `deprecated-modules` | warning | Installed `ansible-doc` deprecation metadata is checked with a conservative removed-module fallback. | Results depend on installed Ansible/collections. |
| `redirected-module` | note | Legacy redirects and short names are separated from true deprecations and mapped to current FQCNs. | Project collection resolution can make some short names acceptable. |
| `loop-legacy-syntax` | warning | Tasks using deprecated `with_*` loop keywords are detected; `loop:` with an appropriate filter is the replacement. | Some `with_*` forms have no exact `loop:` equivalent. |
| `fqcn-migration` | note | Short module names (`copy`, `template`, etc.) are detected where the FQCN form (`ansible.builtin.copy`) is required. | Promoted and merged from `fqcn[action-core]`, `fqcn[action]`, and `fqcn[builtins]` ansible-lint rules. |
| `shell-instead-of-module` | warning | Common shell command patterns are mapped to native Ansible modules. | Complex or uncommon commands are not understood. |
| `unused-handler` | warning | Defined handler names not present in collected notifications are reported. | Notifications from other files are invisible. |
| `complex-expression` | warning | Jinja/condition operators, filters, comparisons, grouping, indexing, and length form a score. | Syntactic complexity can overstate difficulty. |
| `incomplete-task` | warning | Parsed task names and module argument fields are scanned for TODO/FIXME/HACK/XXX; YAML comment lines are excluded. | Intentional roadmap comments still trigger. |
| `unstructured-module` | warning | Role standard directories are checked for required `main.yml`/`.yaml` entry points. | Custom layouts are reported. |
| `empty-abstraction` | warning | Empty documents and empty block/rescue/always sections are detected. | Scaffolding placeholders are intentionally flagged. |
| `excessive-nesting` | warning | Recursive block/rescue/always depth greater than three is reported. | Depth alone does not measure conceptual complexity. |
| `missing-abstraction` | warning | More than ten leaf tasks without role/task includes triggers the rule. | Intentionally self-contained files may trigger. |
| `redundant-default-value` | note | Role defaults are compared with exact task/play vars and `set_fact` values. | Only same-role static values are available. |
| `unexpected-task-location` | warning | Role-file document shapes, embedded plays, and handler-only `listen` placement are validated. | Business-purpose placement remains a human/project-policy decision. |
| `deprecated-module-option` | warning | Supplied task arguments are compared with installed Ansible deprecation metadata and project overrides. | Removed/unavailable collection metadata can be absent. |
| `unpinned-ansible-dependency` | warning | Requirements and external role meta dependencies are checked for an explicit version. | Short local sibling-role dependencies are intentionally excluded. |
| `unsafe-file-write` | warning | File-capable module arguments using `unsafe_writes: true` are reported. | Some broken or overlay filesystems genuinely require unsafe writes. |

## Style, naming, documentation, and semantics

| Rule | Severity | How it is detected | Main limitation |
|---|---|---|---|
| `unnamed-play` | note | Plays without a nonblank `name` are counted with source lines. | Imported/generated names are not resolved. |
| `unnamed-task` | note | Recursive task metrics identify missing task names. | Dynamic task generation is outside static YAML. |
| `long-task-name` | note | Task-name length is compared with the configured threshold. | Long descriptive names can be legitimate. |
| `inconsistent-naming-convention` | note | Excess punctuation/special characters in play/task names are counted. | This is not a full team naming policy. |
| `duplicate-task-names` | note | Exact task-name frequencies are counted. | v0.0.4: scoped per-play; cross-play identical names no longer fire. |
| `missing-tags` | note | Leaf tasks lacking own or inherited tags are reported. | Small playbooks may not need selective execution. |
| `missing-file-extension` | note | File-looking task attributes without suffixes are detected. | Extensionless valid files such as `Dockerfile` exist. |
| `long-statement` | note | Physical source lines longer than the configured threshold (160 by default) are reported. | URLs/generated values may be unavoidable. |
| `unnecessary-abstraction` | note | A block wrapping exactly one child task is counted recursively. | v0.0.4: blocks with rescue/always/when/tags/become are exempt — they carry block-level semantics. |
| `unnecessary-set-fact` | note | `set_fact` definitions not referenced in visible Jinja expressions are reported. | Indirect and cross-file uses can be missed. |
| `unused-include-vars` | note | Included variable keys are compared with visible Jinja references. | Experimental; indirect/cross-file references can be missed. |
| `undocumented-complex-task` | note | Complex/deep tasks without an immediately preceding comment are reported. | Experimental; comment presence does not prove quality. |
| `incohesive-playbook` | note | spaCy similarity across play/task names estimates file-level semantic cohesion. | Experimental; non-English/out-of-vocabulary names can be unmeasurable. |
| `incohesive-play` | note | The same semantic similarity calculation is scoped per play. | Experimental; short names produce noisy similarity. |
| `yaml-formatting` | note | YAML formatting issues (indentation, trailing spaces, line endings, colon spacing) are detected via ansible-lint and promoted to a canonical concept. | Promoted and merged from `yaml[indentation]`, `yaml[trailing-spaces]`, `yaml[colons]`, and similar ansible-lint rules. |
| `variable-naming-convention` | note | Role variables not prefixed with the role name are detected to prevent cross-role collisions. | Promoted and merged from the `var-naming[no-role-prefix]` ansible-lint rule. |
| `role-readme-absent` | note | Roles without a `README.md` at their root are reported. | README presence does not guarantee quality or completeness. |
| `galaxy-meta-incomplete` | note | Roles with a missing or empty `meta/main.yml`, or missing required `galaxy_info` fields, are reported. | Roles not intended for Galaxy publication may legitimately omit this file. |
| `molecule-test-absent` | note | Ansible roles without a `molecule/` directory containing at least one scenario are reported. | Roles tested by other frameworks or integration tests will trigger this rule. |

## External aggregate rule

| Rule | Severity | How it is detected | Main limitation |
|---|---|---|---|
| `ansible-lint-issue` | warning | Every issue returned by the integrated `ansible-lint` JSON scan becomes a finding. | Requires the executable and compatible runtime dependencies. |

## Strengthened partial and Git-review rules

| Rule | Severity | How it is detected | Main limitation |
|---|---|---|---|
| `unused-registered-variable` | note | Collected `register` names are compared with all other scalar references in the file. | Cross-file/dynamic uses are invisible. |
| `unscoped-shell-variable` | warning | Shell `$VAR` references are compared with task/play environment mappings, inline assignments, and standard process variables. | Host-provided custom environment variables can be intentional. |
| `invalid-task-attribute-type` | error | Universal boolean, integer, mapping, and tags task attributes are type-checked. | Collection-specific module schemas remain ansible-lint's responsibility. |
| `invalid-numeric-value` | error | Literal ports and retry/timing controls are checked for valid numeric ranges. | Templated and service-specific ranges are unresolved. |
| `read-only-command-change` | note | Read-only curl tasks without `changed_when: false` are reported because command-like modules otherwise claim a change. | The conservative implementation is currently curl-focused. |
| `missing-release-note` | note | A PR/review range changing production YAML must add a release-note file. | Some internal changes legitimately need no public note. |
| `missing-bug-reference` | note | Bug/fix commit subjects require a recognized numeric bug trailer/reference. | External issue existence is not verified. |
| `invalid-depends-on-reference` | warning | Present `Depends-On` trailers must be review URLs or Gerrit Change-Ids. | The tool cannot infer when an absent dependency was required. |
| `commit-message-format` | note | Every review-range commit's subject/body lengths and blank separation are validated. | Project-specific exceptions are not modeled. |
| `removed-copyright-notice` | warning | Modified file headers are compared between the committed review base and head. | Renames and notices outside the first 20 lines are not compared. |
| `missing-test-update` | warning | Production-YAML changes in the review range require a test/tests/Molecule co-change. | Co-change does not prove meaningful test coverage. |
| `untested-override-change` | warning | Defaults/vars changes require a test or Molecule co-change. | Tests are not executed or semantically matched to each option. |

## Output path

Every rule above is normalized by `report/findings.py` with provider, native
rule, concept, file, line, severity, and message. Raw records feed
`raw/findings.*`; grouped occurrences feed `canonical/occurrences.*` and
SARIF. Corresponding counts
are exposed in per-file technical JSON and CSV, and normalized findings are
appended to the per-file text report. External findings survive structural YAML skips; safe
source/role checks also contribute project rollup findings for skipped YAML
documents.

For implementation details of the recent detector bundles, see
`PAPER_SMELLS_IMPLEMENTATION.md`, `REVIEW_CHECKLIST_IMPLEMENTATION.md`, and
`PARTIAL_AND_REVIEW_METADATA_IMPLEMENTATION.md`, and
`MISSING_CHECKLIST_IMPLEMENTATION.md`. For
the 38-criterion paper comparison, see [checklist-coverage.md](../research/checklist-coverage.md).
