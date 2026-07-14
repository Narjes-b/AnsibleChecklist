# Paper-derived smell implementation

This document explains the nine detectors added from the candidate list in
`AnsibleInternship - Does Your Configuration Code Smell Paper.csv`. The goal
was to implement only checks that have a defensible static Ansible mapping.
All nine checks live in
`src/ansibleguard/detectors/paper_candidates.py` because they share safe YAML
loading, recursive task traversal, source-line lookup, role discovery, and
variable extraction. Each check still has its own public function, metric,
detail list, finding rule, severity, and CSV column.

## Integration

For every structurally analyzable playbook or task file:

1. `parser.py::mainn()` calls `detect_paper_candidates()`.
2. The detector returns a count and a `*_details` list for every smell.
3. `smells.py::assess_code_smells()` copies the counts into final metrics.
4. `report/findings.py` creates line-addressable JSON/SARIF findings.
5. `report/csv_writer.py` writes one column per smell.

For empty, metadata, vars, or otherwise structurally skipped YAML documents,
the CLI runs the same safe detector bundle only for project rollups. This lets
source and role-layout findings survive without misclassifying the document as
a playbook or incrementing the structurally-analyzed count.

Role-wide checks choose a single anchor YAML file to prevent the same role or
dependency problem from being emitted once for every file in the role. The
preferred anchor is `tasks/main.yml`, followed by `handlers/main.yml`, then the
first YAML file in the role.

## Implemented checks

### Complex Expression

- Metric: `complex_expressions`
- Rule: `complex-expression` (`warning`)
- Algorithm: scans Jinja blocks plus `when`, `changed_when`, `failed_when`, and
  `until` values. Its score counts boolean operators, comparisons, filters,
  parentheses, indexing, and long-expression penalties.
- Default threshold: score `6`.
- Limitation: complexity is syntactic; a long expression can still be clear.

### Incomplete Task

- Metric: `incomplete_tasks`
- Rule: `incomplete-task` (`warning`)
- Algorithm: scans source lines for `TODO`, `FIXME`, `HACK`, and `XXX`, keeping
  the real source line.
- Limitation: an intentionally documented marker is still reported.

### Long Statement

- Metric: `long_statements`
- Rule: `long-statement` (`note`)
- Algorithm: expands tabs and reports physical source lines longer than 120
  characters.
- Limitation: generated strings and unavoidable URLs may be legitimate.

### Unstructured Module

- Metric: `unstructured_modules`
- Rule: `unstructured-module` (`warning`)
- Algorithm: recognizes files under `roles/<role>/`; requires a
  `tasks/main.yml` or `tasks/main.yaml` entry point and requires every existing
  standard role directory (`handlers`, `defaults`, `vars`, `meta`) to have its
  own main entry point.
- Limitation: deliberately nonstandard role layouts are reported.

### Empty Abstraction

- Metric: `empty_abstractions`
- Rule: `empty-abstraction` (`warning`)
- Algorithm: reports empty YAML documents and explicit empty `block`, `rescue`,
  or `always` task sections.
- Limitation: empty placeholders used during scaffolding are still incomplete
  production abstractions and are intentionally reported.

### Excessive Nesting

- Metric: `excessive_nesting`
- Rule: `excessive-nesting` (`warning`)
- Algorithm: recursively follows every `block`, `rescue`, and `always` branch
  and reports tasks deeper than three wrapper levels.
- Default threshold: depth `3`.
- Limitation: depth is structural and does not measure the semantic difficulty
  of each branch.

### Missing Abstraction

- Metric: `missing_abstractions`
- Rule: `missing-abstraction` (`warning`)
- Algorithm: reports a file with more than ten leaf tasks when it uses no
  `roles`, `include_role`, `import_role`, `include_tasks`, or `import_tasks`.
- Default threshold: `10` leaf tasks.
- Limitation: small, intentionally self-contained playbooks can cross the
  threshold; calibration against a corpus is recommended.

### Broken Role Dependency

- Metric: `broken_role_dependencies`
- Rule: `broken-role-dependency` (`error`)
- Algorithm: builds a graph from every local role's `meta/main.yml`
  dependencies. It detects self-dependencies, missing unqualified local roles,
  and dependency cycles. Qualified Galaxy/collection role names are treated as
  external and are not required to exist under the local `roles/` directory.
- Limitation: availability of external roles cannot be proven without resolving
  installed collections and Galaxy requirements.

### Unguarded Variable

- Metric: `unguarded_variables`
- Rule: `unguarded-variable` (`warning`)
- Algorithm: collects visible definitions from play/task `vars`, `vars_files`,
  role `defaults` and `vars`, `set_fact`, `register`, loop variables, and known
  Ansible magic variables. Jinja references not found in that symbol table are
  reported unless protected by `default`, `d`, or `is defined`.
- Limitation: dynamic inventory, facts gathered at runtime, lookup plugins,
  included files, and variables supplied with `--extra-vars` may be invisible.
  This is therefore a warning, not an error.

## Verification

`tests/test_paper_candidates.py` covers every new algorithm, including nested
task traversal, a role dependency cycle, a missing role, a missing role entry
point, a guarded-variable negative case, and parser-to-finding integration.
The complete suite currently has 134 passing tests; the remaining local failure
requires the `ansible-lint` executable, which is absent from the active virtual
environment.
