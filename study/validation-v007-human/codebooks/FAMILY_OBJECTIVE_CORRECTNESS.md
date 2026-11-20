# Family codebook: objective correctness

## Review question

Does the frozen source violate the rule’s documented correctness, reliability, dependency, or compatibility condition in the stated Ansible context?

## What to inspect

Use the cited task/file plus enough frozen surrounding YAML, handlers, role metadata, dependency declarations, or nearby commands to establish the condition. Follow only references present in the packaged frozen context. Do not assume a parser warning proves a runtime defect.

## Semantic labels

- `positive`: the rule’s concrete condition is present and the stated behavior/compatibility issue follows from the source.
- `negative`: the source contradicts the condition, contains a valid guard/handler/reference, or the rule’s premise is not met.
- `uncertain`: validity depends on unavailable version support, dynamic behavior, custom modules, external dependency contracts, or ambiguous execution semantics.
- `unreviewable`: the required frozen source object is absent/corrupt.

## Family-specific cautions

- Distinguish an objectively wrong value/type/reference from a detector heuristic about style.
- For compatibility/deprecation rules, use the version/context supplied in the item; do not assume every old-looking form is invalid.
- For dependency pinning, inspect the declared source and constraint. Record reproducibility impact as actionability, not as proof that the predicate is true.
- For command/idempotency rules, inspect the operation and guard together. A command string alone is not enough.
- For suppressed errors, determine whether failure is actually swallowed without preserving or checking the result.
- “Positive” validates only the rule’s semantic condition; it does not certify the whole playbook.

## Reason codes

`condition-present`, `condition-absent`, `valid-guard-or-reference`, `version-compatibility`, `external-dependency`, `dynamic-execution`, `insufficient-source-context`, `other`.
