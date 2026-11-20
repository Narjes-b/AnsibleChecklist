# Adjudication guide (Reviewer A and Reviewer B)

Precision for RQ1 needs one final label per pilot item. Where A and B already
gave the same semantic label, that label is final. The other items are in
`adjudication-sheet.csv`.

## What to do

1. Open `adjudication-sheet.csv` (spreadsheet or text editor; keep it as CSV, UTF-8, same columns).
2. For every row with `priority = required (semantic)`:
   - open the item's source in `context_file` and the rule's codebook in
     `study/validation-v007-human/codebooks-v2/`;
   - read both reviewers' labels, reason codes and explanations;
   - decide together and fill:
     - `final_semantic_label`: exactly one of `positive`, `negative`, `uncertain`, `unreviewable`;
     - `adjudication_reason`: one short sentence on why (e.g. "definition is in role defaults, visible in context");
     - `adjudicated_by`: who decided (e.g. `A+B`, or `A+B+supervisor` if you needed a third opinion);
     - `adjudication_date`: `YYYY-MM-DD`.
3. Rows with `priority = optional (actionability only)` already have a final semantic label; fill
   `final_actionability_label` only if you also want adjudicated actionability.
4. Commit the sheet and rerun:

```bash
python scripts/rq1_precision.py --later-label "v0.0.7.1 (rerun 2026-10-22)" \
  --rule-profile study/analysis-v0071-rerun-2026-10-22/rule-profile.csv
```

The script keeps everything already filled in, marks the results as final once
no required row is left, and stops calling them provisional.

## Rules for a fair decision

- Decide from the frozen source and the codebook, not from what the detector or either first label said.
- `uncertain` is a valid final answer when the frozen context really cannot decide; do not force a call.
- If you change your mind about the codebook itself, write it down in the reason; do not silently reinterpret a rule.
- Keep the first labels unchanged; the sheet records the decision next to them.
