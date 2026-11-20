# Missing-abstraction threshold — simple results

## What this rule measures

This rule examines one Ansible file at a time and counts its leaf tasks. A leaf task is an executable task rather than a `block`, `rescue`, or `always` container.

The rule asks whether a file contains too many tasks without using meaningful roles or task includes.

The corpus contains **21,457 file observations** from **197 eligible repositories**.

## Distribution

- Q1: 1 leaf task
- Median: 3 leaf tasks
- Q3: 7 leaf tasks
- Current base threshold: 10 leaf tasks
- P90: 13 leaf tasks
- Tukey upper fence: 16 leaf tasks
- Maximum observed: 289 leaf tasks

The production detector adjusts the base threshold according to file role. Handler files use a lower effective threshold, ordinary task files use the base threshold, and top-level playbooks use a higher effective threshold. The sensitivity calculation preserved those adjustments.

## What each threshold would produce

| Candidate | Base threshold | Files flagged | File rate | Repositories affected |
|---|---:|---:|---:|---:|
| Q1 | 1 | 6,862 | 31.98% | 190/197 |
| Median | 3 | 6,569 | 30.61% | 189/197 |
| Q3 | 7 | 2,911 | 13.57% | 176/197 |
| P80 | 8 | 2,369 | 11.04% | 175/197 |
| Current | 10 | 1,648 | 7.68% | 163/197 |
| P90 | 13 | 997 | 4.65% | 142/197 |
| Tukey upper fence | 16 | 638 | 2.97% | 122/197 |
| P95 | 19 | 420 | 1.96% | 102/197 |

Changing from the current base threshold of 10 to Q3 = 7 would produce **2,911 rather than 1,648 findings**, approximately **1.77 times** as many.

This is less extreme than the `large-task` Q3 result, but it still does not prove that 7 is better. Human reviewers must decide whether the extra files genuinely need decomposition.

## Review sample

A frozen sample of **1,077 files** was created, covering all **197 eligible repositories**. It contains one deterministic selection per available repository × numerical-band × current-prediction stratum.

The sample contains:

- 185 low-band files;
- 184 lower-middle files;
- 207 upper-middle files;
- 180 high files;
- 321 files above the current numerical boundary.

It deliberately includes 334 files that already contain some role/include abstraction. These cases are important for recall and detector-logic analysis: a file may contain one include but still be insufficiently decomposed. The current detector automatically suppresses those files, so manual review can reveal whether that logic causes false negatives.

Every sample row contains numbered source context, population count, inclusion probability, and sampling weight. Small files are included completely; long files use first/middle/last excerpts with explicit context metadata. There are no duplicate observations, no duplicate sampling strata, no missing source context, and all weights passed validation.

## Current state

The working human-label file is `review-labels.csv`. Human agreement is currently unavailable because no independent human labels have been entered. `agreement-status.json` correctly reports `insufficient-independent-labels`.

No missing-abstraction threshold or detector-logic change has been made. After two humans label and adjudicate the sample, the same threshold scorer used for `large-task` can calculate weighted precision, recall, F1, and F0.5 with project-cluster confidence intervals for this rule.
