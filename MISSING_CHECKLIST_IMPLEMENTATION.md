# Implementation of three formerly missing checklist criteria

This iteration adds conservative automation for criteria 8, 10, and 29 from
the 2025 IaC code-review checklist. The implementation lives in
`src/ansibleguard/detectors/missing_checklist.py`.

## Variable use before definition

- Rule: `variable-use-before-definition` (`error`)
- Metric: `variable_use_before_definition`
- Criterion: keep statements in the correct logical order.
- Method: examines linear `pre_tasks`, `tasks`, `post_tasks`, handler, and role
  task sections. It reports Jinja or condition references to a registered
  result or `set_fact` value when only a later task defines that name.
- False-positive controls: visible play/task/role/inventory definitions,
  configured runtime variables, Ansible magic variables, and guarded
  `default`/`d`/`is defined` references are excluded.
- Limit: it deliberately does not infer execution order across
  `block`/`rescue`/`always`, dynamic includes, or arbitrary resources.

## Unexpected task location

- Rule: `unexpected-task-location` (`warning`)
- Metric: `unexpected_task_locations`
- Criterion: put code in the correct file.
- Method: validates objective role structure: defaults/vars/meta files must be
  mappings; tasks/handlers files must be task lists; plays do not belong under
  roles; and the handler-only `listen` attribute does not belong in tasks.
- Limit: static analysis cannot determine the intended business-purpose file
  for every otherwise valid task.

## Deprecated module option

- Rule: `deprecated-module-option` (`warning`)
- Metric: `deprecated_module_options`
- Criterion: avoid deprecated options or parameters.
- Method: identifies each task module, reads its installed `ansible-doc -j`
  option metadata through a bounded cached subprocess, and reports supplied
  options marked deprecated or scheduled for removal.
- Project metadata: `.ansibleguard.yml` can supplement or override installed
  metadata under `rules.deprecated_module_options` using a short or fully
  qualified module name.
- Reliability: a writable `ANSIBLE_LOCAL_TEMP` is supplied, missing tools or
  collections degrade to no metadata finding, and each metadata lookup has a
  ten-second timeout.
- Limit: an option already removed from the installed collection may no longer
  appear in its documentation; project overrides cover known compatibility
  matrices.

## Pipeline and verification

All three count/detail pairs flow through `parser.py`, `smells.py`, the legacy
per-file CSV, `findings.py`, and normalized JSON/CSV/text/SARIF reports. Safe
role-location checks also run for structurally skipped YAML documents.

`tests/test_missing_checklist.py` covers positive and negative ordering cases,
role-file placement, configured deprecation metadata, parser integration, and
finding normalization. The complete suite passes with 163 tests.
