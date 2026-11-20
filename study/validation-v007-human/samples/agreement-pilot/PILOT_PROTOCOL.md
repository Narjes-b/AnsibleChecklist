# V007 agreement-pilot protocol

## Purpose and gate

This pilot calibrates the seven family codebooks and measures reviewer agreement. It is not a precision/recall sample and cannot support detector-performance claims. It uses calibration repositories only. Every selected row is permanently marked `is_agreement_pilot=true` and `eligible_for_performance_scoring=false`.

## Target and selection

Target 50 unique review items per family (about 350 total), or a census of the family’s usable calibration items when fewer than 50 remain after required source-context checks and the rare-rule protection below.

The deterministic selection procedure is:

1. Join immutable source identities to the frozen 144/62 repository split and rule-family map.
2. Discard heldout rows before candidate ranking or context generation. No heldout occurrence sample or context is emitted.
3. For static-source families, rank candidate IDs by `SHA256("v007-human-pilot-v1|<family_id>|<rule_id>|<occurrence_id>")`.
4. Prefer rules with at least five eligible calibration candidates. Do not consume a rule’s fewer-than-five remaining cases merely to fill the pilot when that would compromise later primary validation.
5. Round-robin in lexical rule-ID order. First pass selects no more than one row per repository across the family; only a second pass may add a second item from a repository if needed.
6. Stop at 50 or census the remaining usable family population. Record selected/excluded counts by family, rule, and repository in the manifest.

Review/history candidates require the exact target commit. The actual first parent is additionally required only for the diff-dependent rules `missing-release-note`, `missing-test-update`, and `untested-override-change`. The message-only rules `commit-message-format` and `missing-bug-reference` use the exact target commit message and remain eligible when the parent object is absent; their context must say no diff was used. Diff-dependent cases without the exact parent are not usable until that parent is recovered. Detector fallback details with `base: null` are never accepted as a substitute. If the usable review/history pool is below 50, report the pool as a context-limited census rather than padding it with invalid ranges.

## Reviewer forms and blinding

Generate one master and two reviewer forms with identical item order and immutable source/context columns. The reviewer files contain blank semantic/actionability/context/reason fields only. They do not include the other reviewer’s decisions, AI answers, severity, confidence, prevalence, selection weights, or current threshold/prediction values.

Both reviewers label every row independently. The pilot must be closed before either file is compared. Do not use pilot rows in later performance estimates, even if no codebook edits were needed.

## Pilot closeout

After both human files are returned:

- validate that immutable columns, IDs, and row order match the frozen master;
- calculate raw agreement, Cohen’s kappa, Gwet’s AC1, positive/negative/uncertain-specific agreement, label prevalence, and the confusion matrix;
- inspect disagreements using only this pilot round;
- if the predeclared agreement target is not met or the error pattern is systematic, revise the codebook and draw a new pilot with new occurrence IDs;
- preserve every round and both original reviewer files; never silently replace a file or call AI adjudication human consensus.

The primary agreement target is Cohen’s kappa at least 0.80, interpreted alongside AC1, prevalence, label-specific agreement, and reviewability. No agreement statistic exists until two human files are returned.
