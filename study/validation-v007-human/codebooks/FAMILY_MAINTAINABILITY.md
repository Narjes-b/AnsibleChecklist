# Family codebook: maintainability/complexity

## Review question

Does the source unit genuinely exhibit the described maintainability or complexity condition, independently of the detector’s numeric threshold or current finding decision?

## What to inspect

Read the full task/play/playbook or other source unit represented by the anchor, with neighboring tasks and role context where supplied. Review the real control/data flow and repetition rather than deciding from a count alone.

## Semantic labels

- `positive`: the cited unit has the described maintainability burden or complexity characteristic.
- `negative`: the unit is coherent/manageable in context, or the detector has measured the wrong unit/condition.
- `uncertain`: the evidence is reviewable but important use, runtime, ownership, or architectural context is unavailable.
- `unreviewable`: the relevant source unit is missing/corrupt or the anchor cannot be resolved.

## Family-specific cautions

- Ignore the threshold itself when judging the semantic condition; otherwise the review merely repeats the detector.
- Larger is not automatically harder to maintain. Consider cohesion, repetition, branching, dependencies, and local conventions visible in context.
- A shell/command-to-module suggestion is not positive merely because a native module exists; compare semantics, supported options, and portability.
- Deprecation rules require the applicable Ansible/module context. A future migration suggestion may be advisory even when the condition is true.
- TODO/FIXME markers indicate a stated concern, not necessarily incomplete production behavior.
- High coupling and unused-handler claims require the relevant local reference graph; external/dynamic references can make the result uncertain.

## Reason codes

`complexity-supported`, `cohesive-or-manageable`, `repetition-supported`, `threshold-only`, `wrong-analysis-unit`, `migration-context`, `dynamic-reference`, `architecture-context-needed`, `insufficient-source-context`, `other`.
