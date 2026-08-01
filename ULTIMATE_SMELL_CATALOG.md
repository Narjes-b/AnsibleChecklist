# Ultimate AnsibleGuard smell catalog

## Why this document exists

This is the slow, beginner-friendly map of every active finding rule in this
repository. It answers eight questions for every rule:

1. What problem is the rule trying to find?
2. Why should a developer care?
3. What code implements it?
4. How does the algorithm work?
5. What is the rule mathematically?
6. What is its approximate time complexity?
7. Where did the idea come from?
8. Is it part of the 38-item Ansible code-review checklist, and if so, is the
   checklist criterion fully or only partially automated?

The source of truth used for this audit is the live code under
`src/ansibleguard/`, especially `report/findings.py`, `profiles.py`, the
detector modules, and the tests. Historical Markdown claims are not treated as
proof by themselves.

Current audited state on 22 July 2026:

> **30 July 2026 update:** The live catalog now contains 65 IDs. The five
> additions are `redirected-module`, `unsafe-file-write`,
> `plaintext-sensitive-variable`, `unpinned-ansible-dependency`, and
> `role-variable-precedence-collision`. Their implementation and limitations
> are documented in `DEVELOPER_PROFILES_OVERLAP_PR_IMPLEMENTATION.md`. The
> dated 22 July inventory below is retained as the earlier audit snapshot.

- 60 active normalized rule IDs;
- 58 internal rules;
- one GitLeaks aggregation rule;
- one ansible-lint aggregation rule;
- 168 automated tests passing;
- all 60 IDs assigned to exactly one profile family;
- the 38-criterion checklist is not fully automated: 15 criteria are marked
  Yes, 18 Partial, and 5 No in `CODE_REVIEW_CHECKLIST_COVERAGE.md`;
- the eight-rule `research-core` is still provisional and explicitly records
  `research_eligible=false`.

## First, three different meanings of “implemented”

These meanings must not be mixed.

### Code-operational

The rule has a live detection path, a `RULE_CATALOG` entry, normalized output,
and tests. This does not prove that every reported result is a true defect.

### Scientifically calibrated

Humans have sampled positive and negative examples, measured precision and
possibly recall, frozen the thresholds, and approved the rule for the research
population. The current research core has not reached this state.

### Checklist-complete

The automated rule is enough to satisfy the whole human review criterion. A
rule can be code-operational while checklist coverage remains Partial because
runtime behavior, project policy, external issue trackers, or human intent are
still missing.

## Reading the mathematics without fear

The notation below is only a precise way to say what the code does.

| Symbol | Simple meaning |
|---|---|
| `B` | bytes or scalar content inspected in one file |
| `L` | physical source lines |
| `P` | plays |
| `T` | leaf tasks, including tasks inside `block`, `rescue`, and `always` |
| `A` | task attributes or module arguments |
| `V` | variable definitions plus variable references |
| `H` | handlers plus notifications |
| `R` | local roles |
| `E` | role dependency edges or import/include links |
| `C` | commits in the selected review range |
| `F` | changed or repository files considered by a rule |
| `D` | embedding dimension used by spaCy |
| `K` | fixed number of regexes, keywords, or built-in tool rules |

`1[condition]` means 1 when the condition is true and 0 otherwise. Therefore:

```text
count = sum of 1[bad condition]
```

is simply “count every item for which the bad condition is true.” Complexity
uses Big-O notation. For example, `O(T)` means the work grows roughly in a
straight line with the number of tasks. Fixed rule lists are written as `K` so
the operational cost is clear, even though a fixed `K` can be treated as a
constant.

## The execution families

| Family | Rules | Meaning |
|---|---:|---|
| `research-core` | 8 | Conservative, paper-inspired primary candidates; still provisional |
| `extended-ansible` | 43 | Other internal source rules; separate from the core |
| `review-range` | 7 | Git base-to-head review rules, not snapshot smells |
| `external-tool` | 2 | GitLeaks and ansible-lint aggregation rules |

The source-profile identity is exact:

```text
research-core + extended-ansible = snapshot-source
8 + 43 = 51 source rules
```

The complete technical profile is:

```text
51 source + 7 review + 2 external = 60 rules
```

## Quick checklist map

“Yes” and “Partial” below are the statuses of the whole checklist criterion,
not a claim that one rule alone solves everything.

| Rule | Checklist relationship | Checklist status | What remains when Partial |
|---|---|---|---|
| `hardcoded-credentials` | Supports #36 default credentials | Yes jointly | GitLeaks finds secret formats; `default-credentials` handles weak defaults |
| `credentials-leaking-in-log` | Direct #37 | Yes | Nothing objective for this defined check; custom secret vocabulary can still be missed |
| `insecure-permissions` | Direct #38 | Yes | Variable-computed modes remain a detector limitation |
| `default-credentials` | Direct #36 | Yes | Product-specific default lists still need configuration |
| `missing-validate-certs` | Supports #6 value checking | Partial | Runtime/templated values and service intent |
| `overriden-keys` | General correctness, not a named checklist item | — | — |
| `missing-handler` | Supports #32 | Partial | Prove which handler should exist and resolve cross-file handlers |
| `broken-role-dependency` | Supports #31 | Partial | External roles and runtime dependency order |
| `missing-bool-filters` | Direct #12 | Yes | Complex Jinja parsing is still heuristic |
| `overriding-facts` | Supports #34 | Partial | Execute and assess override tests |
| `unguarded-variable` | Direct #7 | Yes | Repository/runtime symbol resolution is still needed for precision |
| `non-idempotent-command` | Direct #14 | Partial | Interpret arbitrary shell effects and native-module behavior |
| `silent-error-suppression` | Direct #23 | Partial | Prove a warning/recovery path exists elsewhere |
| `shell-environment-export` | Direct #9 | Partial | Host/runtime environment and intentional local export |
| `variable-use-before-definition` | Direct #10 | Partial | Blocks, dynamic includes, resource ordering, and external definitions |
| size, complexity, modularity, cohesion rules | Smell literature/Puppet adaptation | — | Not named as checklist criteria |
| naming rules | Direct/support #17 and #20 | Yes | Team-specific naming policy is broader |
| `missing-file-extension` | Direct #15 | Yes | Extensionless valid files can be intentional |
| unused-definition rules | Support #18 | Partial | Arbitrary unreachable tasks, comments, parameters, and cross-file uses |
| `shell-instead-of-module` | Direct #19 | Yes | Pattern catalog cannot understand every shell command |
| `long-statement` | Supports #22 notation | Partial | Full YAML/DSL notation is delegated partly to ansible-lint |
| `undocumented-complex-task` | Direct #3 | Partial | Comment quality and design documentation |
| `invalid-task-attribute-type` | Direct #28 | Partial | Collection schemas and templated/runtime values |
| `invalid-numeric-value` | Supports #6 | Partial | Service-specific value semantics |
| `ansible-lint-issue` | Supports #6, #19, #22, #25, #28, #30 | Mixed; #25 Yes | Native rule identity is currently collapsed |
| `missing-release-note` | Direct #1 | Partial | Decide whether the specific change really requires a note |
| `missing-bug-reference` | Direct #2 | Partial | Verify or create the external bug report |
| `invalid-depends-on-reference` | Direct #4 | Partial | Infer when an absent dependency is required and verify the target |
| `commit-message-format` | Direct #5 | Yes | Project-specific exceptions |
| `removed-copyright-notice` | Direct #26 | Yes | Notices outside inspected headers and complex renames |
| `missing-test-update` | Direct #33 | Yes for co-change | Test meaning and adequacy are separate concerns |
| `untested-override-change` | Direct #34 | Partial | Execute tests and prove the assertions cover each override |
| `unexpected-task-location` | Direct #8 | Partial | Intended business-purpose placement and project policy |
| `deprecated-module-option` | Direct #29 | Partial | Missing collection metadata and version compatibility matrix |

## Category 1 — security and secret handling

### 1. `hardcoded-credentials`

- Purpose: find real secret material committed in any scanned file, including
  API keys, tokens, private keys, and provider credentials.
- Code path: `external/gitleaks.py` runs the pinned GitLeaks 8.30.1 binary once
  for the complete target. `report/findings.py` turns every native GitLeaks
  result into this normalized rule ID.
- Algorithm: in the current integration, GitLeaks runs in directory/no-history
  mode using `detect --no-git`. It applies built-in or target `.gitleaks.toml`
  regex, keyword, entropy, allowlist, and proximity rules.
- Mathematics: for fragments `x` and GitLeaks rules `r`, report
  `sum(x,r) 1[keyword_r(x) and regex_r(x) and entropy_r(x) >= threshold_r and not allowlisted]`.
- Complexity: approximately `O(B * K)` for fixed secret rules, plus regex and
  entropy costs. The actual engine is external and optimized.
- Inspiration: GitLeaks and secret-scanning practice, not the Puppet SANER
  smell catalog.
- Checklist: supports criterion #36. The criterion is marked Yes jointly with
  `default-credentials`, but GitLeaks alone is not a weak-default checker.
- Code status and gaps: external-tool operational. It requires the binary;
  examples can produce false positives; the wrapper discards native RuleID as
  a research category; `--no-git` means it does not search deleted historical
  secrets; archive and decoding flags are not enabled.

### 2. `credentials-leaking-in-log`

- Purpose: stop a task from printing a password, token, or similar value.
- Code: `detectors/credentials_leaking_in_log.py`.
- Algorithm: recursively visit leaf tasks, serialize each task, search 14
  sensitive keywords, and require task-level or inherited `no_log: true`.
- Mathematics: `sum(t in T) 1[sensitive(t) and not no_log(t)]`.
- Complexity: `O(B + T*K)`; serialization makes total inspected task content
  the main cost.
- Inspiration: Ansible `no_log`, security best practices, and checklist #37.
- Checklist: direct #37, marked Yes.
- Code status and gaps: operational and line-addressable. Custom secret names
  outside the keyword set may be missed; a harmless key containing a sensitive
  word can trigger.

### 3. `insecure-permissions`

- Purpose: find files or resources that grant unsafe access to “other” users.
- Code: `review_checklist.py::detect_insecure_permissions`.
- Algorithm: inspect `mode` on common file-managing modules, parse literal
  octal or symbolic permissions, always report world-write, and report
  world-read when the task context looks sensitive.
- Mathematics: for mode `m`, report when `(m & 0o002) != 0`, or when the
  resource is sensitive and `(m & 0o004) != 0`; equivalent symbolic grants are
  also recognized.
- Complexity: `O(T*A)`.
- Inspiration: POSIX permissions, security guidance, and checklist #38.
- Checklist: direct #38, marked Yes.
- Code status and gaps: operational. Templated modes and uncommon modules are
  unresolved; sensitivity uses keywords rather than full data-flow analysis.

### 4. `default-credentials`

- Purpose: find credentials still set to values such as `admin`, `root`,
  `password`, `changeme`, or `123456`.
- Code: `review_checklist.py::detect_default_credentials`.
- Algorithm: recursively walk mappings, select credential-like keys, ignore
  Jinja/Vault values, and compare literal values with a conservative default
  set plus project configuration.
- Mathematics: `sum(k,v) 1[credential_key(k) and normalize(v) in Defaults]`.
- Complexity: `O(B)` with set membership `O(1)` on average.
- Inspiration: checklist #36 and common security-default guidance.
- Checklist: direct #36, marked Yes.
- Code status and gaps: operational. Product-specific defaults must be added in
  `.ansibleguard.yml`; examples and fixtures can intentionally contain them.

### 5. `missing-validate-certs`

- Purpose: detect explicit disabling of HTTPS certificate validation.
- Code: `detectors/missing_validate_certs.py`.
- Algorithm: recursively inspect `uri`, `get_url`, and FQCN equivalents and
  report literal false-like `validate_certs` values.
- Mathematics: `sum(t) 1[module(t) in {uri,get_url} and validate_certs(t) in FalseValues]`.
- Complexity: `O(T*A)`.
- Inspiration: Ansible TLS module guidance; supports checklist #6.
- Checklist: #6 is Partial because checking all assigned values requires
  runtime and service-specific knowledge.
- Code status and gaps: operational. A templated value such as
  `{{ verify_ssl }}` is intentionally not guessed; self-signed internal TLS can
  be a legitimate exception.

## Category 2 — correctness, variables, and execution behavior

### 6. `overriden-keys`

- Purpose: find duplicate YAML mapping keys that silently replace an earlier
  value. The historical ID contains the spelling `overriden`; changing it
  would break output compatibility.
- Code: `detectors/overriden_keys.py`.
- Algorithm: use ruamel line information to identify task spans, then group
  source keys by indentation depth inside each task and report repeated keys at
  the same depth.
- Mathematics: for task `t`, depth `d`, and key `k`, report when
  `frequency_t(d,k) > 1`.
- Complexity: approximately `O(L)` time and `O(L)` temporary storage.
- Inspiration: YAML uniqueness/correctness, not a named checklist item.
- Checklist: no direct criterion.
- Code status and gaps: operational with source lines. Exotic YAML constructs
  can make textual span/depth reconstruction less exact.

### 7. `missing-bool-filters`

- Purpose: prevent string values such as `"false"` from behaving as truthy in
  an Ansible `when` condition.
- Code: `detectors/filters_for_comparison.py`.
- Algorithm: collect conditions recursively, split boolean terms, and report a
  bare term that is neither a comparison nor a literal and lacks `| bool`.
- Mathematics: `sum(e in conditions) 1[bare(e) and not literal(e) and not has_bool_filter(e)]`.
- Complexity: `O(B)` for normal expressions.
- Inspiration: Ansible truthiness behavior and checklist #12.
- Checklist: direct #12, marked Yes.
- Code status and gaps: operational. Regex splitting is not a full Jinja AST,
  so nested or multiline expressions can be misclassified.

### 8. `overriding-facts`

- Purpose: identify a `set_fact` variable assigned different values more than
  once.
- Code: `detectors/overriding_facts.py`.
- Algorithm: collect fact assignments in order and compare each assignment
  with later assignments of the same name.
- Mathematics: `sum(i<j) 1[name_i = name_j and value_i != value_j]`.
- Complexity: `O(S^2)` for `S` fact assignments; memory `O(S)`.
- Inspiration: Ansible variable correctness; it also supports checklist #34.
- Checklist: #34 remains Partial because the tool does not execute or assess
  override tests.
- Code status and gaps: operational. Mutually exclusive conditions are not
  modeled and cross-file assignments are invisible.

### 9. `unguarded-variable`

- Purpose: report Jinja variables that have no visible definition and no
  `default`, `d`, or `is defined` guard.
- Code: `paper_candidates.py::detect_unguarded_variables`.
- Algorithm: build a local symbol table from play/task vars, `vars_files`, role
  defaults/vars, `set_fact`, `register`, loop variables, magic variables, and
  configured known variables; compare Jinja references with that table.
- Mathematics: `U = References - Definitions - Guarded - Magic - Configured`;
  report every member of `U`.
- Complexity: approximately `O(B + V)` using sets.
- Inspiration: paper-derived variable safety plus checklist #7.
- Checklist: direct #7, marked Yes as an objective guard/visible-definition
  check.
- Code status and gaps: code-operational but scientifically uncalibrated. It
  produced many false-positive risks in OpenStack because inventory plugins,
  gathered facts, parent playbooks, dynamic includes, and extra-vars are not
  repository-resolved. It is deliberately outside `research-core`.

### 10. `non-idempotent-command`

- Purpose: find a mutating `shell`, `command`, or `raw` action that will claim
  change every run or repeat side effects.
- Code: `review_checklist.py::detect_non_idempotent_commands`.
- Algorithm: match known mutating command families and require at least one
  recognized guard: `creates`, `removes`, `changed_when`, or check-mode logic.
- Mathematics: `sum(t) 1[command_like(t) and mutating(cmd_t) and not guarded(t)]`.
- Complexity: `O(B*K)` for a fixed command-pattern catalog.
- Inspiration: Ansible idempotency and checklist #14.
- Checklist: direct #14, Partial.
- Missing for full coverage: arbitrary shell semantics, module-specific side
  effects, and real before/after state cannot be proven statically.

### 11. `silent-error-suppression`

- Purpose: find a task that hides failure without preserving the result for
  warning, recovery, or audit.
- Code: `review_checklist.py::detect_silent_error_suppression`.
- Algorithm: report `ignore_errors: true` or `failed_when: false` when the task
  has no `register`.
- Mathematics: `sum(t) 1[suppresses_failure(t) and not registers_result(t)]`.
- Complexity: `O(T*A)`.
- Inspiration: reliable exception handling and checklist #23.
- Checklist: direct #23, Partial.
- Missing: a later independent warning path cannot be associated; registering
  a result does not prove anybody uses it correctly.

### 12. `shell-environment-export`

- Purpose: replace fragile `export NAME=value` shell code with Ansible's
  explicit `environment:` mapping.
- Code: `review_checklist.py::detect_shell_environment_exports`.
- Algorithm: scan command-like task text for shell export syntax.
- Mathematics: `sum(t) 1[command_like(t) and regex_export(command_t)]`.
- Complexity: `O(B)`.
- Inspiration: checklist #9 and Ansible environment scoping.
- Checklist: direct #9, Partial.
- Missing: determine whether a self-contained export is intentional and model
  host-provided runtime environment.

### 13. `unscoped-shell-variable`

- Purpose: find `$NAME` or `${NAME}` used by a command without a task/play
  `environment` declaration, inline assignment, or standard process meaning.
- Code: `partial_checklist.py::detect_unscoped_shell_variables`.
- Algorithm: extract shell references, subtract declared environment names,
  inline assignments, and a standard-variable allowlist.
- Mathematics: `U = ShellReferences - TaskEnv - PlayEnv - InlineAssignments - StandardEnv`.
- Complexity: `O(B + V)`.
- Inspiration: checklist #9.
- Checklist: direct #9, Partial.
- Missing: custom variables guaranteed by the remote host or wrapper process
  are unknown.

### 14. `variable-use-before-definition`

- Purpose: find a task that uses a registered result or fact before a later
  task creates it.
- Code: `missing_checklist.py::detect_variable_use_before_definition`.
- Algorithm: examine linear task sections, collect later `register` and
  `set_fact` definitions, and report earlier unguarded references after
  subtracting visible external definitions.
- Mathematics: for reference at position `i`, report when
  `first_definition(name) > i` and the name is not externally defined/guarded.
- Complexity: approximately `O(T + V)` with sequence-local sets/maps.
- Inspiration: checklist #10.
- Checklist: direct #10, Partial.
- Missing: control flow across `block/rescue/always`, dynamic includes,
  arbitrary resource order, and repository/runtime definitions.

### 15. `invalid-task-attribute-type`

- Purpose: find universal task keywords written with the wrong YAML type.
- Code: `partial_checklist.py::detect_invalid_task_attribute_types`.
- Algorithm: validate known boolean flags, integer timing/retry fields,
  mapping-valued `vars`/`environment`, and string-or-list `tags`.
- Mathematics: `sum(t,a) 1[a in KnownAttributes and type(value_ta) not in AllowedTypes_a]`.
- Complexity: `O(T*A)`.
- Inspiration: checklist #28.
- Checklist: direct #28, Partial.
- Missing: collection-specific schemas, templated values, coercion, and runtime
  compatibility are left to ansible-lint/Ansible execution.

### 16. `invalid-numeric-value`

- Purpose: reject impossible literal ports and negative retry/timing controls.
- Code: `partial_checklist.py::detect_invalid_numeric_values`.
- Algorithm: recursively visit key/value pairs, require ports in `1..65535`,
  and require selected retry/timing values to be nonnegative.
- Mathematics: report port `p` when `p < 1 or p > 65535`; report selected
  control `n` when `n < 0`.
- Complexity: `O(B)`.
- Inspiration: checklist #6 assigned-value validation.
- Checklist: supports #6, Partial.
- Missing: templated values and service-specific enums, ranges, and
  cross-version constraints.

## Category 3 — handlers, dependencies, and structure

### 17. `missing-handler`

- Purpose: find a `notify` target with no matching handler in the analyzed
  file.
- Code: `detectors/handler_issues.py`.
- Algorithm: collect handler names and notification names, then compute set
  difference while excluding a small built-in-name heuristic.
- Mathematics: `Missing = Notifications - DefinedHandlers - ExcludedPatterns`.
- Complexity: `O(T + H)` average.
- Inspiration: Ansible handlers and checklist #32.
- Checklist: supports #32, Partial.
- Missing: resolve handlers imported from roles or other files and decide when
  a task semantically needs a particular handler.

### 18. `unused-handler`

- Purpose: find a handler defined but never notified in the analyzed file.
- Code: `detectors/handler_issues.py`.
- Algorithm: reverse the previous set comparison.
- Mathematics: `Unused = DefinedHandlers - Notifications`.
- Complexity: `O(T + H)` average.
- Inspiration: dead-code practice and checklist #18/#32.
- Checklist: #18 and #32 are Partial.
- Missing: notifications in other files and dynamic role composition.

### 19. `broken-role-dependency`

- Purpose: find missing local roles, a role depending on itself, or cycles in
  local role metadata.
- Code: `paper_candidates.py::detect_broken_role_dependencies`.
- Algorithm: build a directed role graph from `meta/main.yml`, accept qualified
  external roles, check missing local vertices, and run cycle detection. One
  role anchor prevents duplicate findings.
- Mathematics: graph `G=(R,E)` is bad if an edge targets a missing local role,
  `(r,r) in E`, or `G` contains a directed cycle.
- Complexity: `O(R + E + F)` after metadata loading.
- Inspiration: Puppet missing-dependency/modularity smells adapted to Ansible;
  supports checklist #31.
- Checklist: #31 is Partial.
- Code status and gaps: research-core candidate and code-operational. External
  Galaxy/collection availability and runtime ordering are not resolved.

### 20. `high-coupling`

- Purpose: warn when one playbook depends on many imports, includes, or roles.
- Code: `detectors/high_coupling.py` plus thresholding in `smells.py`.
- Algorithm: recursively count task/play imports and role declarations,
  including FQCN forms, then compare with `Num_Imports=4` and `Num_Roles=5`.
- Mathematics: report when `imports > 4 or roles > 5`.
- Complexity: `O(T + E)`.
- Inspiration: coupling/modularity smell literature and Puppet tightly-coupled
  modularization; supports checklist #31.
- Checklist: #31 is Partial.
- Missing: architectural necessity, dependency strength, runtime order, and
  corpus-calibrated thresholds.

### 21. `unstructured-module`

- Purpose: find an Ansible role that does not have expected standard entry
  points.
- Code: `paper_candidates.py::detect_unstructured_module`.
- Algorithm: for a role, require `tasks/main.yml|yaml`; for every existing
  standard directory among handlers/defaults/vars/meta, require its main file;
  emit once at a role anchor.
- Mathematics: report role `r` when required entry point is absent from
  `Files(r)`.
- Complexity: `O(F)` for role discovery, then constant membership checks per
  standard directory.
- Inspiration: SANER/Puppeteer Unstructured Module adapted to Ansible; also
  supports checklist #8.
- Checklist: #8 is Partial.
- Code status and gaps: provisional research-core candidate. Real projects can
  intentionally load OS-specific files without `vars/main.yml`; custom layouts
  therefore require manual calibration or a refined definition.

### 22. `empty-abstraction`

- Purpose: find an empty YAML abstraction or explicitly empty
  `block/rescue/always` section.
- Code: `paper_candidates.py::detect_empty_abstractions`.
- Algorithm: parse the document and recursively inspect nested task sections.
- Mathematics: `sum(s) 1[s is an abstraction and size(s)=0]`.
- Complexity: `O(T)` after parsing.
- Inspiration: abstraction/design smell literature adapted from Puppet.
- Checklist: no direct checklist criterion.
- Code status and gaps: provisional research-core candidate. Empty no-op
  placeholders can be deliberate, so a structural match is not automatically
  a defect.

### 23. `excessive-nesting`

- Purpose: find control structures nested too deeply to read easily.
- Code: `paper_candidates.py::detect_excessive_nesting`.
- Algorithm: recursively follow `block`, `rescue`, and `always`, carrying a
  current depth, and report depth greater than 3.
- Mathematics: `sum(t) 1[depth(t) > 3]`.
- Complexity: `O(T)` time and `O(depth)` recursion stack.
- Inspiration: complexity/design smell literature adapted to Ansible.
- Checklist: no direct criterion.
- Code status and gaps: provisional research-core candidate. Depth measures
  shape, not semantic difficulty; the threshold needs validation.

### 24. `missing-abstraction`

- Purpose: find a large collection of tasks that is not split with roles or
  task includes.
- Code: `paper_candidates.py::detect_missing_abstraction`.
- Algorithm: count leaf tasks; if count is greater than 10 and no role/task
  include or import is present, report the file.
- Mathematics: report when `leaf_tasks > 10 and abstractions = 0`.
- Complexity: `O(T)`.
- Inspiration: SANER/Puppeteer Insufficient Modularization adapted to Ansible.
- Checklist: no one-to-one criterion; it loosely supports modularity review.
- Code status and gaps: provisional research-core candidate. A self-contained
  file can legitimately exceed 10 tasks, and an include's mere presence does
  not prove good decomposition.

### 25. `unexpected-task-location`

- Purpose: catch objective role-layout mistakes, such as task lists under
  `defaults/`, mappings under `tasks/`, embedded plays under roles, or `listen`
  in a normal task file.
- Code: `missing_checklist.py::detect_unexpected_task_locations`.
- Algorithm: compare parsed document shape and handler-only attributes with the
  role directory in which the file lives.
- Mathematics: `sum(f) 1[shape(f) not in AllowedShapes(directory(f))]` plus
  misplaced handler-attribute counts.
- Complexity: `O(B + T)`.
- Inspiration: checklist #8.
- Checklist: direct #8, Partial.
- Missing: business-purpose placement and project-specific path policy cannot
  be inferred from generic YAML structure.

## Category 4 — size, complexity, duplication, and modularity

### 26. `large-playbook`

- Purpose: warn that a whole file may be too large to understand comfortably.
- Code: `detect_large_playbook.py`, `large_task.py`, and `smells.py`.
- Algorithm: compare playbook LOC, play count, average play size, and nested
  task count with configured thresholds (`110`, `4`, `50`, `15`, etc.).
- Mathematics: report when any selected metric `m_i > threshold_i`.
- Complexity: `O(B + T + P)`.
- Inspiration: Ansible best practices and maintainability metrics.
- Checklist: no direct criterion.
- Code status and gaps: operational; thresholds are configurable but not yet
  scientifically calibrated for the full OpenStack corpus.

### 27. `complex-playbook`

- Purpose: combine size and dependency signals into a stronger complexity
  warning.
- Code: composite logic in `smells.py::assess_code_smells`.
- Algorithm: logical combinations of large LOC, many plays/tasks, many imports,
  or many roles.
- Mathematics: a Boolean formula over `LOC`, `P`, `T`, imports, and roles; a
  finding is produced when the formula evaluates true.
- Complexity: `O(1)` after upstream metrics; those metrics cost `O(B+T+P)`.
- Inspiration: maintainability/coupling smell literature.
- Checklist: no direct criterion.
- Code status and gaps: operational; the formula and thresholds require
  empirical calibration.

### 28. `insufficient-modularization`

- Purpose: find a large, many-play monolith.
- Code: composite logic in `smells.py`.
- Algorithm: require both playbook LOC and play count to exceed thresholds.
- Mathematics: `LOC > 110 and P > 4`.
- Complexity: `O(1)` after metric collection.
- Inspiration: Puppet Insufficient Modularization and Ansible role practice.
- Checklist: no direct criterion.
- Code status and gaps: operational extended rule; small monoliths remain below
  the thresholds and large generated/simple files can trigger.

### 29. `large-play`

- Purpose: find an individual play that is too large.
- Code: `detectors/detect_large_play.py` and `smells.py`.
- Algorithm: compute per-play LOC, recursive task count, and average task size;
  compare with thresholds such as 50 LOC and 7 tasks.
- Mathematics: for play `p`, report when any `metric_i(p) > threshold_i`.
- Complexity: `O(B + T + P)`.
- Inspiration: focused-play/single-responsibility practice.
- Checklist: no direct criterion.
- Code status and gaps: operational; size does not equal semantic complexity.

### 30. `large-task`

- Purpose: find one task with a very large YAML body.
- Code: `detectors/large_task.py` and `smells.py`.
- Algorithm: serialize each leaf task, count its lines, and compare with
  `LOC_task=15`; wrapper blocks are not treated as leaf tasks.
- Mathematics: `sum(t) 1[LOC(t) > 15]`.
- Complexity: `O(B + T)`.
- Inspiration: single-responsibility practice.
- Checklist: no direct criterion.
- Code status and gaps: operational; a long declarative module invocation can
  still be conceptually simple.

### 31. `duplicated-code`

- Purpose: find repeated task bodies that could become a shared include or
  role.
- Code: `detectors/duplicate_code.py`.
- Algorithm: remove each task's `name`, canonicalize the remaining mapping,
  count exact signatures, and report repeated signatures.
- Mathematics: the current metric is
  `number of signatures s where frequency(s)>1`; it counts duplicate groups,
  not every repeated occurrence.
- Complexity: approximately `O(B + T log A)` because task items are sorted for
  signatures.
- Inspiration: DRY/code-clone practice and checklist #24.
- Checklist: direct #24, marked Yes.
- Code status and gaps: operational. Semantically equal but differently shaped
  tasks can be missed; identical tasks with different intent can trigger.

### 32. `complex-expression`

- Purpose: find a Jinja or condition expression that is syntactically hard to
  understand.
- Code: `paper_candidates.py::detect_complex_expressions`.
- Algorithm: inspect Jinja blocks and condition fields; score Boolean
  operators, comparisons, filters, parentheses, indexing, and length; report a
  score at least the configured threshold 6.
- Mathematics: `score(e)=w1*operators + w2*comparisons + w3*filters + ...`;
  report when `score(e) >= 6`.
- Complexity: `O(B)`.
- Inspiration: SANER/Puppet Complex Expression.
- Checklist: not a direct checklist item, although complex tasks can trigger
  the separate comment criterion.
- Code status and gaps: provisional research-core candidate. Syntactic score
  does not directly measure human comprehension; threshold-5 negative examples
  and threshold-6 positives have been labeled in Nova, but broader calibration
  remains required.

### 33. `incomplete-task`

- Purpose: find unresolved work markers left in production configuration.
- Code: `paper_candidates.py::detect_incomplete_tasks`.
- Algorithm: scan non-binary source lines for `TODO`, `FIXME`, `HACK`, or `XXX`.
- Mathematics: `sum(line in L) 1[marker_regex(line)]`.
- Complexity: `O(B)`.
- Inspiration: SANER/Puppet Incomplete Tasks.
- Checklist: not a direct checklist criterion.
- Code status and gaps: provisional research-core candidate. Intentional
  roadmap comments still match; comments do not prove executable incompleteness.

### 34. `long-statement`

- Purpose: identify physical lines that are hard to review in normal tools.
- Code: `paper_candidates.py::detect_long_statements`.
- Algorithm: expand tabs and report non-comment source lines over 120
  characters.
- Mathematics: `sum(line) 1[not comment(line) and display_length(line)>120]`.
- Complexity: `O(B)`.
- Inspiration: source-format/readability practice; paper-derived candidate.
- Checklist: supports broad criterion #22, which remains Partial.
- Code status and gaps: provisional research-core candidate. URLs and generated
  values can legitimately exceed the limit.

### 35. `unnecessary-abstraction`

- Purpose: find a `block` wrapper containing exactly one task.
- Code: `detectors/unnecessary_abs.py`.
- Algorithm: recursively count one-child block sections.
- Mathematics: `sum(block b) 1[children(b)=1]`.
- Complexity: `O(T)`.
- Inspiration: readability/over-abstraction practice.
- Checklist: no direct criterion.
- Code status and gaps: operational. A one-task block can intentionally provide
  inherited `when`, `become`, `delegate_to`, or recovery structure.

### 36. `redundant-default-value`

- Purpose: find an assignment that repeats the exact value already supplied by
  the role's defaults.
- Code: `review_checklist.py::detect_redundant_default_values`.
- Algorithm: load role defaults and compare exact values with visible
  play/task vars and `set_fact` assignments.
- Mathematics: `sum(k,v) 1[k in RoleDefaults and v = RoleDefaults[k]]`.
- Complexity: `O(B + V)` average.
- Inspiration: checklist #11.
- Checklist: direct #11, marked Yes.
- Code status and gaps: operational. Only same-role static values are visible;
  Jinja equivalence and cross-role inheritance are not evaluated.

## Category 5 — naming, tags, style, and file references

### 37. `unnamed-play`

- Purpose: make execution output understandable by ensuring each play has a
  name.
- Code: `detectors/unnamed_play.py`.
- Algorithm: report plays whose `name` is missing, empty, or whitespace.
- Mathematics: `sum(p) 1[blank(name(p))]`.
- Complexity: `O(P)` after parsing.
- Inspiration: Ansible output readability and checklist #17/#20.
- Checklist: the naming criteria are marked Yes.
- Code status and gaps: operational; generated/imported naming context is not
  resolved.

### 38. `unnamed-task`

- Purpose: ensure every task has a useful label in logs.
- Code: `detectors/unnamed_tasks.py` using task metrics.
- Algorithm: recursively report tasks whose computed name is `Unknown`.
- Mathematics: `sum(t) 1[blank(name(t))]`.
- Complexity: `O(T)` after task collection.
- Inspiration: checklist #17/#20 and Ansible readability.
- Checklist: Yes.
- Code status and gaps: operational; dynamic task generation is outside static
  YAML.

### 39. `long-task-name`

- Purpose: keep task names scannable in terminal output.
- Code: task-name metrics plus thresholding in `smells.py`.
- Algorithm: compare name length with `task_name_len=75`.
- Mathematics: `sum(t) 1[length(name(t)) > 75]`.
- Complexity: `O(total name characters)`.
- Inspiration: checklist #17/#20 and readability.
- Checklist: Yes for the current naming checks.
- Code status and gaps: operational; a long but precise name can be valid.

### 40. `inconsistent-naming-convention`

- Purpose: flag names with excessive punctuation/special characters.
- Code: `detect_large_play.py`, `large_task.py`, and `smells.py`.
- Algorithm: count non-letter, non-digit, non-space characters and compare with
  threshold 3.
- Mathematics: `special(s)=sum(c in s) 1[not alnum_or_space(c)]`; report when
  `special(s)>3`.
- Complexity: `O(total name characters)`.
- Inspiration: checklist #20.
- Checklist: Yes for coherent naming at the implemented objective level.
- Code status and gaps: operational heuristic; version numbers, paths, and
  separators can legitimately contain punctuation.

### 41. `duplicate-task-names`

- Purpose: stop different tasks from becoming indistinguishable in logs.
- Code: `detectors/duplicate_task_names.py`.
- Algorithm: count exact task-name frequencies.
- Mathematics: report names `n` where `frequency(n)>1`.
- Complexity: `O(T)` average with a counter.
- Inspiration: checklist #17/#20 and Ansible log readability.
- Checklist: Yes.
- Code status and gaps: operational; repetition across separate plays can be
  intentional.

### 42. `missing-tags`

- Purpose: identify tasks that cannot be selected or skipped through tags.
- Code: `detectors/missing_tags.py`.
- Algorithm: recursively visit leaf tasks and accept own or inherited tags;
  report tasks with neither.
- Mathematics: `sum(t) 1[tags(t) union inherited_tags(t) = empty]`.
- Complexity: `O(T*A)`.
- Inspiration: Ansible operational control, not a direct checklist criterion.
- Checklist: no direct item.
- Code status and gaps: operational. Small/internal playbooks may not need tag
  control, and role/application tags from outside the file can be invisible.

### 43. `missing-file-extension`

- Purpose: find file-looking references with no suffix.
- Code: `detectors/files_extensions.py`.
- Algorithm: inspect selected attributes such as `src`, `file`, `cmd`, and
  `path`; report strings that do not end in a dot extension.
- Mathematics: `sum(value) 1[target_attribute and not regex("\\.\\w+$", value)]`.
- Complexity: `O(B)` over inspected strings.
- Inspiration: checklist #15.
- Checklist: direct #15, marked Yes.
- Code status and gaps: operational but heuristic. `Dockerfile`, executables,
  directories, and shell command strings can be valid without extensions;
  several module-specific path fields are not covered.

### 44. `unnecessary-set-fact`

- Purpose: find a fact that is assigned but never visibly referenced.
- Code: `detectors/set_fact.py`.
- Algorithm: collect `set_fact` names, scan scalar strings for Jinja
  references, and subtract used names.
- Mathematics: `Unused = SetFactDefinitions - VisibleReferences`.
- Complexity: approximately `O(B + V)`.
- Inspiration: dead-code practice and checklist #18.
- Checklist: supports #18, Partial.
- Missing: indirect `hostvars` access, cross-file use, dynamic includes, and
  arbitrary unused tasks/comments/parameters.

### 45. `unused-include-vars`

- Purpose: find variables loaded from an included vars file but never used in
  the visible playbook.
- Code: `detectors/include_vars.py`.
- Algorithm: locate `include_vars`, load top-level keys from referenced files,
  collect visible Jinja references, and subtract them.
- Mathematics: `Unused = IncludedTopLevelKeys - VisibleReferences`.
- Complexity: `O(B + sum(size(included files)))`.
- Inspiration: dead-dependency practice and checklist #18.
- Checklist: supports #18, Partial.
- Missing: nested keys, indirect lookup, and cross-file references.

### 46. `unused-registered-variable`

- Purpose: find a task result saved with `register` but never referenced.
- Code: `partial_checklist.py::detect_unused_registered_variables`.
- Algorithm: collect register names and search every other scalar value for
  references.
- Mathematics: `Unused = Registers - OtherScalarReferences`.
- Complexity: approximately `O(B + V)`; implementation string scans can trend
  toward `O(number_of_registers * B)` in register-heavy files.
- Inspiration: checklist #18.
- Checklist: supports #18, Partial.
- Missing: cross-file and dynamic references and complete unreachable-code
  analysis.

### 47. `undocumented-complex-task`

- Purpose: require a nearby explanation for a structurally complex task.
- Code: `review_checklist.py::detect_undocumented_complex_tasks`.
- Algorithm: mark nested/deep or long-condition tasks as complex and check
  whether the immediately preceding source line is an explanatory comment.
- Mathematics: `sum(t) 1[complex(t) and not preceding_comment(t)]`.
- Complexity: `O(B + T)`.
- Inspiration: checklist #3.
- Checklist: direct #3, Partial.
- Missing: comment quality, distant documentation, and simple tasks whose
  business logic still needs explanation.

## Category 6 — idempotency, modules, compatibility, and reliability

### 48. `deprecated-modules`

- Purpose: find use of modules known to be obsolete or replaced.
- Code: `detectors/deprecated_modules.py`.
- Algorithm: identify task module keys and compare short/FQCN aliases with a
  curated deprecation map.
- Mathematics: `sum(t) 1[normalize(module(t)) in DeprecatedModules]`.
- Complexity: `O(T*A)` with average constant-time map lookup.
- Inspiration: compatibility practice and checklist #19/#30.
- Checklist: #19 is Yes for native DSL preference; #30 is Partial for all
  deprecated structures. It does not implement Puppet-specific criterion #16
  about setting parameters to `UNDEF`.
- Code status and gaps: operational; the curated map must track Ansible
  releases and collections.

### 49. `shell-instead-of-module`

- Purpose: recommend a native Ansible module when a common shell command has a
  safer declarative equivalent.
- Code: `detectors/shell_instead_of_module.py`.
- Algorithm: recognize `shell`/`command` tasks and match command families such
  as package, service, file, user, download, or archive operations.
- Mathematics: `sum(t) 1[command_like(t) and exists native_mapping(command_t)]`.
- Complexity: `O(B*K)` for a fixed command catalog.
- Inspiration: Ansible DSL best practice and checklist #19.
- Checklist: direct #19, marked Yes.
- Code status and gaps: operational; complex pipelines and uncommon commands
  remain unknown, while some suggested replacements need contextual review.

### 50. `deprecated-module-option`

- Purpose: find a still-recognized module option marked deprecated or scheduled
  for removal.
- Code: `missing_checklist.py::detect_deprecated_module_options`.
- Algorithm: identify unique modules, query cached `ansible-doc -j` metadata
  with a timeout, merge `.ansibleguard.yml` overrides, and compare supplied
  options with deprecation metadata.
- Mathematics: `sum(t,a) 1[a supplied and a in DeprecatedOptions(module(t))]`.
- Complexity: local matching `O(T*A)` plus one bounded external metadata lookup
  per uncached unique module.
- Inspiration: checklist #29.
- Checklist: direct #29, Partial.
- Missing: already-removed options absent from installed documentation,
  unavailable collections, target-environment version matrices, and runtime
  compatibility.

## Category 7 — semantic cohesion

### 51. `incohesive-playbook`

- Purpose: estimate whether names across a file appear to discuss unrelated
  concerns.
- Code: `detectors/sem_cohesion.py`.
- Algorithm: lemmatize play/task names with spaCy `en_core_web_lg`, compute
  pairwise cosine similarities, and compare the average with threshold 0.4.
- Mathematics: for vectors `v_i`,
  `cos(i,j)=(v_i dot v_j)/(|v_i||v_j|)` and
  `mean_similarity = 2/(n(n-1)) * sum(i<j) cos(i,j)`; report below threshold.
- Complexity: `O(N^2 * D)` for `N` names and embedding dimension `D`.
- Inspiration: semantic cohesion research and weakened-modularity ideas.
- Checklist: no direct criterion.
- Code status and gaps: operational but low-confidence. Short, non-English,
  and domain-specific names are noisy or unmeasurable; the large model is an
  extra dependency.

### 52. `incohesive-play`

- Purpose: apply the same semantic-cohesion idea inside one play.
- Code: `detectors/incohesive_plays.py`/semantic helpers.
- Algorithm and mathematics: pairwise cosine mean scoped to a play, compared
  with the play threshold 0.5.
- Complexity: `O(sum_p N_p^2 * D)`.
- Inspiration: semantic cohesion and single-responsibility ideas.
- Checklist: no direct criterion.
- Code status and gaps: operational with the same NLP validity risks as the
  file-level rule.

## Category 8 — external ansible-lint aggregation

### 53. `ansible-lint-issue`

- Purpose: keep official ansible-lint findings beside AnsibleGuard findings.
- Code: `external/ansible_lint.py` and `report/findings.py`.
- Algorithm: run ansible-lint once on the target with JSON output; normalize
  every native issue to this one rule ID while preserving message, file, and
  line.
- Mathematics: `count = number of issues returned by ansible-lint`.
- Complexity: external and rule-dependent, roughly `O(B*K)` plus Ansible parse,
  schema, plugin, and syntax-check costs.
- Inspiration: official ansible-lint, not the Puppet catalog.
- Checklist: supports #6, #19, #22, #25, #28, and #30. Criterion #25 is Yes;
  the broader criteria remain Partial.
- Code status and gaps: external-tool operational. The Python dependency is
  unpinned in `pyproject.toml`; behavior can change between environments. Most
  importantly for research, native IDs such as `name`, `yaml`,
  `no-changed-when`, and `risky-file-permissions` are collapsed into one
  category. It is excluded from source research profiles.

## Category 9 — Git review-range rules

These are not properties of a frozen YAML file. Their input is a Git range
`base...head`, chosen from `ANSIBLEGUARD_BASE_SHA` and
`ANSIBLEGUARD_HEAD_SHA` or the detector fallback. Complexity statements share
the cost of reading commit messages and diffs; the code computes the bundle
together rather than invoking Git seven independent times.

### 54. `missing-release-note`

- Purpose: require a release-note file when production YAML changes.
- Code: `review_metadata.py::detect_project_review_smells`.
- Algorithm: collect changed paths; report when production configuration
  changed but no file was added under recognized release-note directories.
- Mathematics: `1[ConfigChanged and not ReleaseNoteAdded]`.
- Complexity: shared review cost approximately `O(C + diff_bytes + F)`.
- Inspiration: checklist #1 and OpenStack review practice.
- Checklist: direct #1, Partial.
- Missing: determine whether this particular internal change is exempt and
  assess release-note content.

### 55. `missing-bug-reference`

- Purpose: require bug/fix commits to cite a bug number or recognized trailer.
- Code: `review_metadata.py`.
- Algorithm: scan every commit subject/body in the range; when bug/fix wording
  exists, require `Closes-Bug`, `Related-Bug`, `Partial-Bug`, or a numeric bug
  reference.
- Mathematics: `sum(c) 1[bug_like(message_c) and not bug_reference(message_c)]`.
- Complexity: `O(total commit-message bytes)` within the shared review cost.
- Inspiration: checklist #2 and OpenStack commit conventions.
- Checklist: direct #2, Partial.
- Missing: create the report, verify the external issue exists, and establish
  semantic relation to the change.

### 56. `invalid-depends-on-reference`

- Purpose: reject malformed `Depends-On:` trailers.
- Code: `review_metadata.py`.
- Algorithm: validate every present trailer as a review URL or 40-hex Gerrit
  Change-Id.
- Mathematics: `sum(trailer) 1[not valid_review_url and not valid_change_id]`.
- Complexity: `O(total commit-message bytes)`.
- Inspiration: checklist #4 and Gerrit review practice.
- Checklist: direct #4, Partial.
- Missing: infer when an absent dependency is needed and query Gerrit to prove
  the referenced review exists or is compatible.

### 57. `commit-message-format`

- Purpose: enforce readable review commit messages.
- Code: `review_metadata.py`.
- Algorithm: for every commit, require subject length at most 50, a blank
  separator before a body, and body lines at most 72.
- Mathematics: report violations of `|subject|<=50`, separator rule, and
  `forall body_line: |line|<=72`.
- Complexity: `O(total commit-message bytes)`.
- Inspiration: checklist #5/OpenStack review style.
- Checklist: direct #5, marked Yes.
- Code status and gaps: operational for the selected range; project-specific
  exceptions are not modeled.

### 58. `removed-copyright-notice`

- Purpose: detect removal of an existing copyright header.
- Code: `review_metadata.py`.
- Algorithm: compare the first 20 lines of each modified file at base and head;
  report when a copyright marker existed before and is absent after.
- Mathematics: `sum(f) 1[copyright(base,f) and not copyright(head,f)]`.
- Complexity: `O(F * header_size)` plus Git object access.
- Inspiration: checklist #26.
- Checklist: direct #26, marked Yes.
- Code status and gaps: operational. Renames and notices outside the first 20
  lines can escape this bounded comparison.

### 59. `missing-test-update`

- Purpose: require a test/Molecule co-change when production YAML changes.
- Code: `review_metadata.py`.
- Algorithm: classify changed paths and report `ConfigChanged` with no path
  under test/tests/Molecule.
- Mathematics: `1[ProductionYamlChanged and not TestPathChanged]`.
- Complexity: `O(F)` after the shared Git diff.
- Inspiration: checklist #33.
- Checklist: direct #33, marked Yes for the defined co-change requirement.
- Code status and gaps: operational, but a changed test is not proof that tests
  ran or meaningfully cover the configuration.

### 60. `untested-override-change`

- Purpose: specifically require test co-change for defaults, vars, group_vars,
  or host_vars modifications.
- Code: `review_metadata.py`.
- Algorithm: narrow changed configuration paths to override sources and apply
  the same test-path condition.
- Mathematics: `1[OverrideSourceChanged and not TestPathChanged]`.
- Complexity: `O(F)` after the shared Git diff.
- Inspiration: checklist #34.
- Checklist: direct #34, Partial.
- Missing: execute tests, map each changed option to assertions, and judge test
  adequacy.

## Important numbering note

The 60 numbered headings above correspond one-to-one with the 60 keys in
`src/ansibleguard/report/findings.py::RULE_CATALOG`.

## What the code-review checklist still does not automate

Five criteria are currently No:

1. #13 blank line before a configuration section;
2. #16 set deprecated Puppet parameters to `UNDEF`—this does not transfer
   safely to Ansible;
3. #21 follow current OpenStack IRC conventions;
4. #27 cross-service/cross-version parameter-value compatibility;
5. #35 prove that tests establish assigned values are correct.

The repository should not pretend that all five are ordinary static Ansible
smells. #27 can be improved with project schemas; #35 can gain test-execution
evidence; the others require project policy, a human, or are Puppet-specific.

## What must happen before calling the core “fully implemented research”

The eight code paths exist, but that is not the final scientific gate. The
project still needs to:

1. finish stratified human labels for positive and negative examples;
2. measure per-rule precision and agreement between reviewers;
3. refine context-sensitive `empty-abstraction`, `missing-abstraction`, and
   `unstructured-module` definitions;
4. freeze thresholds, code version, dependencies, and the core allowlist;
5. obtain the intended supervisor decision on the Puppet-to-Ansible mapping;
6. change `research_eligible` only after those gates pass;
7. preserve native external rule identity before using ansible-lint or
   GitLeaks categories in scientific tables;
8. add research occurrence keys and deduplication before prevalence analysis.

## Where to verify every statement

- Active IDs and severities: `src/ansibleguard/report/findings.py`
- Family/profile membership: `src/ansibleguard/profiles.py`
- Thresholds: `src/ansibleguard/thresholds.csv`
- Detector implementations: `src/ansibleguard/detectors/`
- External wrappers: `src/ansibleguard/external/`
- Checklist source audit: `CODE_REVIEW_CHECKLIST_COVERAGE.md`
- Compact canonical inventory: `ALL_DETECTED_SMELLS.md`
- Detailed limitations: `inventory.md`
- Tests: `tests/`
- Current research warning and next gates: `START_HERE.md` and
  `RESEARCH_PROFILE_AND_CALIBRATION_PLAN.md`
