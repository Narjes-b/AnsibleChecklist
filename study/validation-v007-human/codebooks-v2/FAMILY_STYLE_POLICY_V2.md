# Family v2: style and policy
Question: is the stated predicate true in the frozen source (semantic), and separately is following the policy useful here (actionability)?

Operational definitions (use the rule's configured threshold; measure with the rule's own unit):
- `long-task-name`: literal name longer than 75 characters (count the characters as written, do not evaluate Jinja). `long-statement`: a physical line longer than the configured length (160 by default; an ansible-lint project config can override it, and the bundle may not show that) after expanding tabs to 2 columns; comment lines, lines containing a URL (any scheme such as `postgres://` counts) and base64 blobs are exempt by the rule. The length limit comes from an ansible-lint/yamllint config the bundle may not show: use 160 and state that. State the measured length. `inconsistent-naming-convention`: special-character count above the rule's threshold of 3 in a task or play name; count the characters of the name after removing Jinja `{{ }}`/`{% %}` that are neither alphanumeric, whitespace, nor in the allowed set `- _ . / : ( ) [ ] ' " & | , +`; state the count and which characters.
- `variable-naming-convention`: positive when a variable name violates the role-prefix / snake_case convention the rule documents; role-scoped variables without the role prefix are positive.
- `missing-file-extension`: a static `import_tasks`/`include_tasks`/`include_vars`/`import_playbook` reference (no Jinja) whose file name lacks `.yml`/`.yaml` (`.json` is also valid for `include_vars`). Not violations: directory references ending `/`, `namespace.collection.playbook` targets of `import_playbook`, templated paths. The finding anchor may be line 1; look for the reference.
- `duplicate-task-names`: the same non-empty task name occurs more than once within one play (or one task list for task files). Same names in different plays are not duplicates. Duplicates in mutually exclusive `when` branches are positive with `low-value` actionability.
- `missing-tags`: positive when the task has no tags and none are inherited from a play or block.
- `unnamed-task` / `unnamed-play`: positive when no `name` key; **only for Ansible content**. A Kustomize/Helm/mkdocs/Taskfile YAML file is `negative`, reason `out-of-scope` (non-Ansible YAML).
- `molecule-test-absent`: needs the full tree; a bundle without a tree is `unreviewable` / `bundle-defect`.
- `galaxy-meta-incomplete`: positive only when required keys are absent; optional unless publication is in scope (actionability).

Positive semantic reasons: `predicate-present`.
Negative: `predicate-absent`, `inherited-policy-satisfies`, `out-of-scope`, `source-anchor-mismatch`.
Uncertain: `policy-unknown`, `repository-policy-evidence-missing`.
Actionability reasons: `policy-optional`, `fix-is-proportionate`, `repository-policy-evidence`.
