# Family v2: structure and reuse
Question: does the frozen organization exhibit the reported structure condition, and would another structure be appropriate?

Operational definitions:
- The bundle must name the flagged construct (role, task file, block); an anchor at line 1 with no construct is `unreviewable` / `bundle-defect`.
- `unstructured-module`: positive when the role/module directory has no `tasks/main.{yml,yaml}`; needs a complete listing.
- `role-readme-absent`: positive when no README at the role root in a complete listing (true positive by definition); actionability usually `advisory`.
- `unnecessary-abstraction`: block with exactly one task and none of the justifying block keys (`rescue`, `always`, `when`, `tags`, `become`, `become_user`, `no_log`, `environment`, `loop`, `with_items`, `vars`). If any is present: negative. Nested blocks are counted separately.
- `missing-abstraction`: more than 10 leaf tasks (tasks that are not containers of nested blocks) in one playbook/tasks/handlers file, with no `include_tasks`/`import_tasks`/`include_role`/`import_role` and no play-level `roles`. That is the predicate (semantic). Whether a role or include would really help is actionability, not the semantic label.
- `duplicated-code`: semantically equivalent blocks, not merely similar text; intentional environment-specific duplication is negative (`intentional-duplication`).
- `insufficient-modularization`: a playbook file with more than 110 lines and more than 4 plays (the rule's size thresholds). Negative when the plays are small imports/role lists, or the file is an examples/documentation playbook; the semantic question is whether the file actually mixes many plays inline.
- `unexpected-task-location`: a role `tasks/`/`handlers/` file holds a mapping instead of a task list or a play (`hosts`), or `defaults/`/`vars/`/`meta/main.yml` holds a list. Name the section and the shape found.
- `duplicated-code`: two or more blocks with equivalent behaviour that differ only by parameters (id, name, path, message) are duplicates; two similar blocks with different conditions or behaviour are negative. The rule measures textual similarity, so the human question is real behavioural equivalence; there is no repetition-count threshold, so mark close calls `uncertain` with `codebook-ambiguous`.
- `high-coupling`: see maintainability (strictly greater than 4 imports or 5 roles).

Computed facts: when the bundle has a "Computed facts" section (single-task blocks with their lines and keys; leaf-task count and include/role presence), use it as the parser's fact and judge it; it replaces locating the construct from a line-1 anchor.

Positive semantic reasons: `structure-condition-present`, `confirmed-reuse-benefit`.
Negative: `structure-condition-absent`, `intentional-duplication`, `valid-extension-point`, `repository-convention`.
Uncertain: `dynamic-include-or-caller`, `architecture-context-needed`.
