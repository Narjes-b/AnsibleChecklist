# Independent reviewer instructions

Your initial packet contains frozen source evidence and one blank source-review
CSV. Work independently; do not see the other reviewer's form or any model output
until you have returned your source judgments. Do not use an LLM to produce labels.

For each assigned case, read source-review/CASE-ID.json and the documented rule
condition. Review the full supplied source, scope and relevant definitions, not
just the flagged line. Mark missing runtime or repository context explicitly.
The source snippets are bounded; no snippet set certifies all runtime behavior.

Complete condition, evidence_sufficient, actionability and notes. For repair cases,
also specify acceptable_change consistent with the explicit intent. For the
comprehension cases, write condition_rubric, evidence_rubric and action_rubric:
each must state exactly what earns one point, with acceptable alternatives.
Do not infer hidden deployment intent or treat a warning as proof of runtime harm.

Allowed values and the full output-review rubric are in
docs/study/llm-quality-study-protocol.md in your packet. Keep a semantic condition
judgment separate from whether changing it is desirable.

The facilitator preserves original forms, resolves differences with reviewers,
and fills source-adjudication.csv separately. After this, you will receive shuffled
output packets and a new form. Independently review all summary/reasoning claims,
not just the structured assessment. Exact citations do not establish correctness.
Unavailable answers stay not-assessable, and failures remain in the denominator.

For proposed fixes, distinguish correctness, harm and indeterminate deployment
assumptions. Passing the behavioral fixture is supporting evidence about that
scenario, not a general equivalence certificate. Explain your judgments in notes.

When grading developer answers, use the frozen per-task rubric, one point each
for condition, supporting evidence/missing context, and appropriate action. Mark
harmful decisions separately. Do not see study condition, participant identity,
time or confidence while grading. Preserve both grading forms before adjudication.
