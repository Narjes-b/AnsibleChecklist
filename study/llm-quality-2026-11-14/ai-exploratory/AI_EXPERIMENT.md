# AI-only exploratory review

These are post hoc judgments by the same AI assistant that helped implement the tool, not human validation.
All 96 scheduled outputs were inspected. Unavailable outputs count as unsuccessful. Original human forms are unchanged.

| Panel | Condition | N | Decision matches AI source judgment | Adequate content | Content plus decisive citations |
|---|---|---:|---:|---:|---:|
| all | window | 48 | 8 (16.67%) | 4 (8.33%) | 2 (4.17%) |
| all | scoped | 48 | 41 (85.42%) | 29 (60.42%) | 21 (43.75%) |
| controlled | window | 24 | 8 (33.33%) | 4 (16.67%) | 2 (8.33%) |
| controlled | scoped | 24 | 24 (100.0%) | 16 (66.67%) | 9 (37.5%) |
| real | window | 24 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| real | scoped | 24 | 17 (70.83%) | 13 (54.17%) | 12 (50.0%) |

## Interpretation

The scoped pipeline improves bounded decision consistency in this experiment, but correct structured states still accompany wrong prose.
Examples: inherited no_log:true is ignored; visible set_fact definitions are denied; unknown TLS flags are described as disabled.
Several citations name the task, URL or path instead of the decisive setting. A valid source location does not establish support.
The real JDBC case has a source-unit binding defect: the flagged task starts at line 188 but the scoped packet selects its preceding sibling.
Unquoted numeric mode 2750 is decimal (octal 05276); it really includes unsafe bits. Do not confuse it with quoted octal '2750'.

The full-panel decision value depends on provisional source interpretations. The controlled 24-case row has fewer module/policy ambiguities.
See provenance.json for scope, dependence and ambiguity limits. Do not call these human precision or LLM reasoning accuracy.

No code snippets were delivered in this comparison, so semantic repair success is not measured by these ratings.
The developer study remains deferred, and no developer benefit is estimated.

## Separate 12-case AI-only repair experiment

All 12 cases returned accepted outputs and matched the AI reference structured decision (backend-constrained). Eight cases were judged repair-eligible by the assistant, but the pipeline marked none actionable and proposed no textual or code fix. Proposal coverage was 0/8 eligible cases. Semantic fix correctness is not estimable because no code fixes were generated. This is not a 0% correctness result.

The logging explanation for case 3 wrongly says hiding controller output would compromise registered results; the authored behavior controls preserve the registered msg. The already-correct TLS case invents a verify_tls dependency despite literal true. These are additional explanation failures, not evidence of harmful edits, since no edits were produced.
