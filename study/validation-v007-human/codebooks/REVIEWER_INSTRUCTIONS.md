# V0.0.7 human review instructions

These instructions apply to the independent agreement-pilot reviewers. Use only your assigned copy of `agreement-pilot.csv`, the family codebook and any rule override referenced by that row, and the frozen context bundle named in the row. Paths such as `codebooks/FAMILY_SECURITY.md` and `samples/agreement-pilot/context/<sample_id>.md` are relative to `study/validation-v007-human/`.

## Before deciding a row

1. Confirm the sample ID, rule, family, repository, commit, and path/commit anchor.
2. Read the row's family codebook and the applicable entry in `codebooks/RULE_OVERRIDES.md`.
3. Open the exact `context_bundle_path`. Treat that bundle—not a current checkout—as the evidence record. `source_context` is a convenience excerpt; the bundle may include additional frozen source, reference-search, tree, or Git-diff evidence.
4. For a static-source item, judge the source blob at the recorded commit. For review/history, use the evidence type stated in the bundle: `commit-message-format` and `missing-bug-reference` use the exact target commit message only; the other three history rules require the actual first-parent diff. Never substitute detector `base: null`, a root-diff, current branch, or arbitrary merge base. If required evidence is missing, label `unreviewable` or `uncertain` and explain why.
5. Do not infer correctness from a detector message, rule name, severity, confidence, or prevalence. The detector's assertion is the claim to test, not evidence that it is true.

Do not use web search, a current repository checkout, a fresh tool run, another reviewer's answer, or AI output. Do not use ansible-lint or GitLeaks as the answer unless a family/rule codebook explicitly asks for a separate comparison; external tools do not determine the AnsibleGuard semantic label.

## Semantic label

Enter exactly one value in `semantic_label`:

- `positive` — the documented condition is present in the frozen evidence.
- `negative` — the documented condition is absent or contradicted by the frozen evidence.
- `uncertain` — the evidence is available but materially ambiguous or incomplete for a defensible binary decision.
- `unreviewable` — required evidence is missing, corrupt, or invalid for this item.

Do not force an uncertain/unreviewable item into a positive or negative answer. Explain the uncertainty briefly in `reviewer_notes`.

## Actionability and context

Choose `actionability_label` separately from semantic correctness:

- `blocking` — material correctness, security, or reliability risk requires correction before normal use.
- `actionable` — a concrete, proportionate improvement is justified here.
- `advisory` — potentially useful, but not a required change.
- `not-actionable` — no useful or proportionate change is supported here.
- `uncertain` — context is insufficient to judge actionability.
- `not-applicable` — semantic label is `negative` or `unreviewable`.

Set `context_sufficient` to `yes`, `no`, or `uncertain`. Set `requires_external_context` to `yes`, `no`, or `uncertain`; if `yes`, select the closest `external_context_type` (for example inventory/runtime inputs, role caller, external dependency, repository policy, deployment environment, or Git parent/diff). Use `none` when no external context is needed.

Repository-wide search is limited to evidence explicitly included in the frozen bundle. Some variable/reference bundles include a bounded frozen-commit search. Do not open the checkout or perform a new search. If the provided evidence cannot establish the caller, inventory, runtime input, dependency behavior, or repository policy needed by the codebook, use `uncertain` or `unreviewable` and record what is missing.

## Reason and notes

- Choose `reason_code` from the controlled list in the row's family codebook. Use `other` only with a short explanation.
- Put a concise, evidence-based location or observation in `evidence_notes`; this is not another label.
- Use `reviewer_notes` for ambiguity or an explanation of an uncertain/unreviewable decision.
- Never copy credential values, private-key material, or other secrets into notes. Contexts are redacted, but report any suspected residual secret without repeating it.

## Independence and file integrity

- Work only on your assigned Reviewer A or Reviewer B copy. Do not view, discuss, or compare answers until both files are returned and the round is closed.
- Leave sample IDs, occurrence IDs, rule/family assignments, repository/commit/path fields, source context, and row order unchanged.
- Edit only these blank decision fields: `semantic_label`, `actionability_label`, `context_sufficient`, `requires_external_context`, `external_context_type`, `reason_code`, `evidence_notes`, and `reviewer_notes`.
- Preserve CSV quoting, UTF-8 encoding, every row, and its order. Do not add columns or sort/filter the file.
- Return the completed CSV as a separate copy; keep the frozen blank template unchanged.

This is a codebook-calibration and agreement pilot, not a precision/recall sample. Every pilot row is permanently excluded from performance scoring. No agreement statistic exists until both independent files are returned and validated.
