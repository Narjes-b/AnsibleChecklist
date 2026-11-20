# Family codebook: structure/reuse

## Review question

Does the frozen repository/task organization actually exhibit the reported structure, placement, abstraction, or reuse condition, and would a different structure be appropriate here?

## What to inspect

Use repository tree excerpts plus the cited task/role files and their local relationships. The package should identify the frozen commit and provide any relevant role layout, include/import, or duplicate-block context. Do not use the current checkout as a substitute.

## Semantic labels

- `positive`: the documented organization/placement/reuse condition is present in the repository evidence.
- `negative`: the referenced structure is valid, the supposed duplicate/abstraction is not equivalent, or the rule’s repository premise is false.
- `uncertain`: the intended role boundary, external repository convention, dynamic include graph, or project architecture is not visible.
- `unreviewable`: required tree/file context is missing or corrupt.

## Family-specific cautions

- Missing abstraction is not established by size alone; consider repetition, cohesion, ownership, and whether extraction creates a useful unit.
- Duplicated code must be semantically equivalent enough that reuse is appropriate; repeated syntax can encode intentional differences.
- An unnecessary or empty abstraction may still serve an interface, extension point, or generator contract; inspect visible callers before judging.
- An absent role README is a structure/documentation observation, not automatically a correctness failure.
- Conventional directory-layout and task-placement rules should be interpreted in the frozen repository’s actual conventions.

## Reason codes

`structure-condition-present`, `structure-condition-absent`, `reuse-benefit`, `intentional-duplication`, `valid-extension-point`, `repository-convention`, `dynamic-include-or-caller`, `insufficient-source-context`, `other`.
