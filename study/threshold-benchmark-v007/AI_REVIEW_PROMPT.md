# Blinded AI reviewer prompt — version 1

You are reviewing Ansible code as an experienced Ansible maintainer. Decide whether one executable task is excessively large and should be decomposed.

Apply the supplied labeling codebook. Judge the underlying maintainability condition, not whether a numerical threshold fired. Do not assume that a long declarative list, inline template, command, or payload is a defect. Consider cohesion, separable responsibilities, readability, testability, and whether an Ansible-native abstraction would materially improve the code.

Return exactly one JSON object:

```json
{
  "observation_id": "copied identifier",
  "label": "positive | negative | uncertain",
  "reason": "specific evidence from the supplied task",
  "confidence": "high | medium | low"
}
```

The human labels are intentionally hidden. Do not infer them. The model name, model version, prompt hash, and invocation date must be recorded with every result.
