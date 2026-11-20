# Family codebook: variable/reference reasoning

## Review question

Given the available frozen repository evidence, what is the strongest supported conclusion about the variable, reference, scope, precedence, or runtime-input condition reported by the detector?

## What to inspect

Start with the cited use/definition, then inspect related role defaults/vars, task order, registered results, `set_fact`, `vars_files`, role/task includes, and explicit environment mappings included in the context bundle. The bundle cannot prove that every inventory, caller, dynamic include, custom fact, or runtime input is absent.

## Semantic labels

- `positive`: the documented misuse/absence/collision is supported by the available evidence and no relevant visible definition, guard, ordering, or contract resolves it.
- `negative`: a visible definition, guard, valid earlier assignment, scope, or contract resolves the report.
- `uncertain`: a legitimate runtime source or dynamic path may resolve the value, or scope/precedence cannot be established from the frozen evidence.
- `unreviewable`: required cited source or linked context is missing/corrupt.

## Family-specific cautions

- `unguarded-variable` is not automatically a missing-variable defect. Separate visible missing definitions from undeclared input contracts and runtime-supplied values.
- Variable precedence is contextual: role defaults, role vars, inventory, play/task vars, facts, and caller inputs have different precedence and scope.
- For use-before-definition, compare execution order and scope; a same-name definition in a different scope is not sufficient.
- For “unused” or “redundant” assignments, search the supplied relevant references, but do not claim whole-repository absence if the bundle is partial or generated/dynamic access is plausible.
- A quoted Boolean string or shell/environment pattern must be judged by actual expression/expansion semantics, not just spelling.
- Record uncertainty explicitly; static visibility is not proof of runtime absence.

## Reason codes

`visible-definition`, `visible-guard`, `valid-precedence`, `runtime-input-possible`, `dynamic-reference`, `scope-mismatch`, `order-mismatch`, `unused-value-supported`, `insufficient-source-context`, `other`.
