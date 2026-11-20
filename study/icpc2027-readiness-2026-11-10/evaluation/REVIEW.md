# Independent source review

Review the frozen source before seeing model answers. Use condition supported / unsupported / insufficient-evidence, evidence_sufficient yes / no, and actionability actionable / not-actionable / context-dependent / not-assessed. Do not use engineering_expectation as a human label. Reviewer A and B work independently; preserve both forms and adjudicate disagreements in a separate file.

Real examples come from previously exposed calibration repositories. The convenience selection does not estimate population precision, recall, or developer benefit. After source review, separately judge explanation entailment and harmful/wrong suggestions for each model output.
