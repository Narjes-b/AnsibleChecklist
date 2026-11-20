# Numerical-threshold benchmark protocol

## Frozen inputs

- Corpus: `207` repositories from `study/runs/v007-207/input/repositories.csv`.
- Source units: files with `included=true` and `parse_status=parsed` in each frozen classification manifest.
- Sampling seed: `v007-threshold-benchmark-20260917`.
- Extracted scalar observations: `2986459`.

## Analysis stages

1. **Distribution:** compute Q1, median, Q3, IQR, tail percentiles, Tukey fences, and repository-median quartiles. Lower-is-worse metrics use lower-tail rather than upper-tail candidates.
2. **Sensitivity:** replay every candidate threshold and report both occurrence-level and repository-level candidate rates.
3. **Manual review:** keep `large-task-review-sample.csv` frozen and enter independent labels in `large-task-review-labels.csv`. The sample contains `944` rows, normally one draw per repository×metric-band×current-prediction stratum, with inverse-probability weights. Rare current-positive populations are censused in metric-specific packets.
4. **Agreement pilot:** compare two independent reviewers. Report raw agreement, Cohen's kappa, Gwet's AC1, and label-specific agreement. Refine the codebook on new pilot rounds until kappa is at least 0.80; do not tune agreement on the primary or held-out evaluation set.
5. **Threshold scoring:** after adjudication, score each threshold using weighted precision, recall, F1 and F0.5 with project-cluster bootstrap confidence intervals. Precision alone is not a valid selection objective.
6. **AI comparison:** only after the human codebook and labels are frozen, obtain blinded structured AI judgments and compare those judgments with adjudicated human labels.

## Label vocabulary

Use `positive`, `negative`, or `uncertain`. A positive means the underlying code-quality condition is present, independent of whether the current numerical threshold fires. Reviewers must not see the other reviewer's answer or the AI answer.

## Important limitation

The automated stages do not create a human gold standard. Human-to-human agreement requires two genuinely independent people. Agent, heuristic, or Claude labels must be reported as AI-assisted labels and cannot be renamed human labels.
