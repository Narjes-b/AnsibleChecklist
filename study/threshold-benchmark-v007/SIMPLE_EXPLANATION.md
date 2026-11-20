# Threshold benchmark — simple explanation

For the complete file map, every threshold studied, values not yet eligible for study, and the exact next human-labeling plan, read [START_HERE_FILE_MAP_AND_PLAN.md](START_HERE_FILE_MAP_AND_PLAN.md) first.

## What was measured

The frozen 207-project corpus was examined. For the `large-task` rule, 128,220 executable tasks were found in 193 eligible projects. The other 14 projects did not contain an executable task in the admitted Ansible files.

Most tasks are small:

- 25% have 4 lines or fewer;
- 50% have 6 lines or fewer;
- 75% have 10 lines or fewer;
- 90% have 15 lines or fewer.

The current AnsibleGuard threshold is 15. In other words, the current rule approximately selects the largest 10% of tasks.

## Why Q3 cannot be selected automatically

Q3 is 10 lines. Using it would produce 27,158 warnings, compared with 12,202 warnings at the current threshold of 15. It would therefore create approximately 2.23 times as many warnings.

The box plot tells us which thresholds are statistically interesting. It does not tell us which warnings are correct. Manual labels are required for that decision.

## Manual sample

A weighted sample of 944 tasks was created. It contains small, medium, near-threshold, and very large tasks from all 193 eligible projects, separated by whether the current detector fires. Each row contains the task location, expanded source context, selection probability, and sampling weight. Across all 24 metrics there are 16,971 primary review rows; rare positive cases are fully included when there are at most 200.

Two humans must independently label each reviewed task:

- `positive`: genuinely too large and should be decomposed;
- `negative`: large or detailed, but still one clear and appropriate operation;
- `uncertain`: more context is required.

Python then calculates human agreement. The main target is Cohen's kappa of at least 0.80, with Gwet's AC1 and label-specific agreement reported as checks when positives are rare. If the target is not reached, the reviewers discuss the disagreements, improve the guide, and label a new pilot. The primary test labels must not be repeatedly changed merely to increase agreement.

## What happens after agreement

Python tests every candidate threshold against the same adjudicated labels and calculates precision, recall, F1, and F0.5 with repository-cluster confidence intervals. Only then can a threshold be selected responsibly.

Claude is not needed for the threshold calculations. After human labels are frozen, Claude or another model can review the same source code without seeing the human answer. Human consensus is then compared with the AI answer.

## Current state

All automated measurements, plots, sensitivity calculations, samples, and scoring programs are complete. Human-to-human agreement and final precision/recall scores remain unavailable because two independent human label sets do not yet exist. They must not be fabricated.
