# Blinded AI review protocol for all threshold studies

Run this stage only after two independent humans have reached the agreement target, the codebook is frozen, and disagreements are adjudicated. The AI must not see either human judgment.

For each row, give the model:

- the metric's `LABELING_CODEBOOK.md`;
- `observation_id`, project, path, line, unit, and source context;
- the review question;
- relevant structural evidence such as expression base score, Boolean operators, filters, nesting, abstraction state, or threshold multiplier.

Do not give the model the numerical band, current prediction, reviewer labels, adjudicated label, sampling weight, or candidate performance. Hiding these fields prevents the model from merely reproducing the threshold or human answer.

Use this system instruction:

> You are an experienced Ansible maintainer performing a blinded maintainability review. Apply the supplied codebook to the source evidence. Judge the underlying condition, not whether a numerical threshold fired. Return one structured decision and cite concrete code evidence. If the available source is insufficient, choose uncertain. Do not infer hidden human labels.

Require exactly this JSON shape:

```json
{
  "observation_id": "copied identifier",
  "label": "positive | negative | uncertain",
  "reason": "specific evidence from the supplied source",
  "confidence": "high | medium | low"
}
```

Record model provider, exact model/version, prompt version, prompt hash, invocation date, and decoding settings. Store the result in the `ai_*` columns without altering human fields.

Compare `ai_label` with `adjudicated_label` using `compare_threshold_reviewers.py`. Report Cohen's kappa, the confusion matrix, coverage after uncertain exclusions, and positive/negative class performance. This is human–AI agreement, not human–human agreement, and the AI is not the gold standard.
