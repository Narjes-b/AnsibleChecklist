# Agreement-pilot reviewer checklist

Use this checklist for every assigned pilot row. Follow the shared instructions and the row's family codebook; this checklist does not replace either.

1. [ ] Confirm the sample ID, rule, review family, repository, commit, and reported path/anchor.
2. [ ] Read the family codebook and any rule-specific override before judging.
3. [ ] Open the frozen context bundle. Confirm it identifies the same repository/commit and contains the evidence needed for this rule.
4. [ ] For review/history, check the stated evidence type: message-only rules need the exact target commit message; diff-dependent rules need the actual first parent and exact range. Never substitute a `base: null` fallback.
5. [ ] Decide `semantic_label` from the documented predicate and supplied evidence—not the detector's assertion, another tool, severity, frequency, or your style preference.
6. [ ] If required context is missing or ambiguous, use `uncertain` or `unreviewable`; do not guess. Record what is missing.
7. [ ] Decide actionability separately. Use `not-applicable` for negative/unreviewable cases; do not let actionability change semantic truth.
8. [ ] Set `context_sufficient`, `requires_external_context`, and `external_context_type` consistently with the decision.
9. [ ] Select a controlled `reason_code`; add concise evidence notes pointing to the relevant frozen lines/diff. Do not copy any secret value.
10. [ ] Before returning the file, confirm every row remains present and in original order; IDs and evidence are unchanged; only the eight decision columns were edited.
11. [ ] Keep your judgments independent. Do not view/discuss the other reviewer’s file or any AI output before both files are returned and the pilot is closed.
