# Additional code-review checklist detectors

This document explains the seven static checks added from the 2025 IaC
code-review checklist after the initial 38-item coverage audit. They live in
`src/ansibleguard/detectors/review_checklist.py` and share the safe parser and
recursive task walker from `paper_candidates.py`.

The implementation deliberately targets criteria that have observable source
evidence. Commit-message policy, bug reports, test coverage, runtime value
correctness, service compatibility, and human intent remain outside the claim.

## Insecure Permissions

- Rule: `insecure-permissions` (`error`)
- Metrics: `insecure_permissions` and `insecure_permissions_details`
- Method: inspects `mode` on common file-managing modules, including FQCN
  forms. Octal modes are converted to permission bits. World-write is always
  reported; world-read is reported when the task contains sensitive context.
  Symbolic modes that grant write to `other` or `all` are also reported.
- Why: unsafe resource permissions are an explicit security checklist item.
- Limits: variable-computed modes cannot be resolved statically.

## Default Credentials

- Rule: `default-credentials` (`error`)
- Metrics: `default_credentials` and `default_credentials_details`
- Method: recursively finds credential-like keys and compares literal values
  with a conservative set of well-known defaults such as `admin`, `changeme`,
  `password`, `root`, and `123456`. Jinja and Vault values are excluded.
- Why: leaving vendor/example defaults is directly actionable and security
  critical.
- Limits: product-specific defaults outside the conservative list are missed;
  test fixtures may intentionally contain examples.

## Non-idempotent Command

- Rule: `non-idempotent-command` (`warning`)
- Metrics: `non_idempotent_commands` and details
- Method: examines `shell`, `command`, and `raw` tasks. Mutating command
  patterns—package installation, service changes, file mutation, user changes,
  downloads, and clones—must provide `creates`, `removes`, `changed_when`, or
  an explicit check-mode guard.
- Why: the paper explicitly asks reviewers to ensure command execution is
  idempotent.
- Limits: it recognizes common command families, not arbitrary shell semantics.

## Silent Error Suppression

- Rule: `silent-error-suppression` (`warning`)
- Metrics: `silent_error_suppressions` and details
- Method: reports tasks using `ignore_errors: true` or `failed_when: false`
  without registering the result for subsequent warning, recovery, or audit.
- Why: swallowed failures without retained evidence cannot support the paper's
  request to warn about exceptional situations.
- Limits: a later task may warn through another mechanism that has no explicit
  data dependency.

## Redundant Default Value

- Rule: `redundant-default-value` (`note`)
- Metrics: `redundant_default_values` and details
- Method: when analyzing a role, loads `defaults/main.yml` or `.yaml` and
  compares exact values with play/task `vars` and `set_fact` assignments.
- Why: restating an unchanged role default creates noise and makes future
  default changes harder to propagate.
- Limits: only exact, statically visible role-default values are compared.

## Shell Environment Export

- Rule: `shell-environment-export` (`warning`)
- Metrics: `shell_environment_exports` and details
- Method: recognizes `export NAME=value` inside command/shell/raw tasks and
  recommends Ansible's task-level `environment:` mapping.
- Why: a shell export is scoped to that subprocess and is commonly mistaken
  for durable environment-variable configuration.
- Limits: exporting inside a deliberately self-contained compound shell script
  can be valid.

## Undocumented Complex Task

- Rule: `undocumented-complex-task` (`note`)
- Metrics: `undocumented_complex_tasks` and details
- Method: considers nested task wrappers, tasks below deep nesting, and very
  long conditions complex. It checks for an immediately preceding source
  comment and reports the task when no explanation is present.
- Why: this provides objective partial automation for the checklist request to
  add explanatory inline comments.
- Limits: comment presence does not prove comment quality; distant design
  documentation is not associated with a task.

## Pipeline integration

`parser.py` adds all seven count/detail pairs to raw metrics. `smells.py`
propagates counts into assessed results. `csv_writer.py` exposes seven columns,
while `findings.py` assigns rule IDs and severity for JSON and SARIF. The CLI's
safe skipped-document fallback also runs these checks where applicable without
changing structural classification.

`tests/test_review_checklist.py` covers positive and negative cases plus
parser-to-finding integration. The local full-suite result after this addition
is 144 passing tests with no environment failure. ansible-lint executable
resolution and its writable temporary directory are covered separately.
