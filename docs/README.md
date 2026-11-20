# AnsibleGuard documentation

Current documentation for AnsibleGuard 0.0.7.1. Frozen study evidence (manifests,
run outputs, validation samples, codebooks) lives under `study/` and is never
edited to match later code.

## Using the tool

| Document | What it covers |
|---|---|
| [../README.md](../README.md) | Overview, installation, CLI usage, configuration |
| [how-it-works.md](how-it-works.md) | Pipeline walkthrough: discovery, parsing, rules, providers, canonicalization, reports |
| [../ARCHITECTURE.md](../ARCHITECTURE.md) | Package boundaries, call flow, failure behaviour, verification matrix |
| [pr-scan.md](pr-scan.md) | **How the pull-request scan works**: base/head snapshots, matching, policies, safeguards |
| [commands-and-pr-guide.md](commands-and-pr-guide.md) | Command cookbook: scans, profiles, tests, studies, local and GitHub PR mode |
| [output-formats.md](output-formats.md) | Output layers, schemas, SARIF, severities, provenance |
| [remote-sources.md](remote-sources.md) | Remote Git acquisition, authentication boundaries, checkout safety |

## Rules

| Document | What it covers |
|---|---|
| [../RULE_REFERENCE.generated.md](../RULE_REFERENCE.generated.md) | Generated rule inventory (`scripts/generate_docs.py`; CI rejects drift) |
| [../PROFILE_REFERENCE.generated.md](../PROFILE_REFERENCE.generated.md) | Generated profile membership and default thresholds |
| [rules/detected-smells.md](rules/detected-smells.md) | Canonical explanatory catalog of active rules |
| [rules/smell-catalog.md](rules/smell-catalog.md) | Beginner-friendly per-rule explanation: problem, implementation, examples |
| [rules/external-tool-overlap.md](rules/external-tool-overlap.md) | What ansible-lint and GitLeaks detect and where AnsibleGuard overlaps |

## Empirical study (v0.0.7)

| Document | What it covers |
|---|---|
| [study/icpc2027-tool-readiness-2026-11-10.md](study/icpc2027-tool-readiness-2026-11-10.md) | Current Tool Track engineering changes, bounded evaluation instrument, demo reproduction, and outstanding gates |
| [Development model results](../study/icpc2027-development-2026-11-10/README.md) | Retained model attempts, backend constraints, prose failures, and release validation |
| [study/recovery-progress.md](study/recovery-progress.md) | **Current repair log:** completed fixes, validation evidence and next steps |
| [study/icpc-readiness-and-local-llm-plan-2026-10-31.md](study/icpc-readiness-and-local-llm-plan-2026-10-31.md) | ICPC 2027 timing/track assessment, local LLM evidence improvements, paper gaps, proposed comparisons and human validation gates |
| [study/recovery-plan-2026-10-23.md](study/recovery-plan-2026-10-23.md) | Diagnosis of the current results, LLM workflow and evaluation integrity; staged repair plan |
| [study/sampling-methodology-2026-10-23.md](study/sampling-methodology-2026-10-23.md) | Proposed sampling by repository partitions, rule decisions and evidence requirements; probability weights and retrieval protocol |
| [../study/sampling-design-2026-10-23/README.md](../study/sampling-design-2026-10-23/README.md) | Refreshed population inventory: 121 decision cells, repository exposure and rule feasibility |
| [../study/sampling-draws-2026-10-23/README.md](../study/sampling-draws-2026-10-23/README.md) | Calibration probability draws and simulation: exact stage weights, alternative workloads, point-estimator bias and remaining gates |
| [../study/sampling-uncertainty-2026-10-23/README.md](../study/sampling-uncertainty-2026-10-23/README.md) | Both-stage variance and interval stress tests: normal 95% candidate rejected, with near-boundary coverage only 51% / 66.25% |
| [../study/sampling-bounds-2026-10-23/README.md](../study/sampling-bounds-2026-10-23/README.md) | Conservative finite-design benchmark: honest coverage but very wide intervals; six rule/decision/size cells dominate the bound |
| [../study/sampling-allocation-2026-10-23/README.md](../study/sampling-allocation-2026-10-23/README.md) | Both-stage allocation comparison: group diversity, within-group quotas, coverage and workload |
| [../study/timeout-context-2026-10-23/README.md](../study/timeout-context-2026-10-23/README.md) | Bounded frozen-source timeout triage: current context/symbol stages finish; original failure remains open |
| [../study/timeout-file-metrics-2026-10-23/README.md](../study/timeout-file-metrics-2026-10-23/README.md) | Current file metric detectors finish; provider/full-tree and reporting stages still require isolation |
| [../study/timeout-gitleaks-2026-10-23/README.md](../study/timeout-gitleaks-2026-10-23/README.md) | Reproduced GitLeaks postprocessing stall, one-read-per-file repair and successful full-tree provider probe |
| [../study/timeout-source-cli-2026-10-23/README.md](../study/timeout-source-cli-2026-10-23/README.md) | Complete source-only CLI/fallback/reporting path finishes; include limitations and remaining combined-profile checks |
| [../study/evidence-retrieval-2026-10-23/local-cache-recovery/README.md](../study/evidence-retrieval-2026-10-23/local-cache-recovery/README.md) | Exact-SHA source retrieval, local cache recovery, source/packet hashes, redaction and remaining evidence limits |
| [../study/evidence-metadata-2026-10-23/README.md](../study/evidence-metadata-2026-10-23/README.md) | Checksum-verified canonical metadata join, semantic subject inventory and construct/rule evidence requirements |
| [../study/evidence-constructs-2026-10-23/README.md](../study/evidence-constructs-2026-10-23/README.md) | Frozen candidate units, lexical subject audit, alias/duplicate/placeholder gaps and outcome cells by rule/decision/size partitions |
| [study/local-llm-repair-2026-10-23.md](study/local-llm-repair-2026-10-23.md) | Local-only LLM safeguards, strict source/answer checks, measured limits and remaining repairs |
| [study/structural-metrics-repair-2026-10-23.md](study/structural-metrics-repair-2026-10-23.md) | Shared declared-task traversal, metric versioning, source-unit semantics and threshold validation limits |
| [../study/local-llm-acceptance-2026-10-23/README.md](../study/local-llm-acceptance-2026-10-23/README.md) | Live local synthetic acceptance: retained HTTP grammar failures, no-call gate and reproduction |
| [study/v007-audit-2026-10-15.md](study/v007-audit-2026-10-15.md) | Historical audit of the v0.0.7 run and validation state, the reproduction, and the fixes |
| [../study/pr-replay-v007-2026-10-15/README.md](../study/pr-replay-v007-2026-10-15/README.md) | Replay of 21 real merged pull requests through PR mode (CSV results) |
| [../study/validation-design-v007/README.md](../study/validation-design-v007/README.md) | Simulation of the heldout sampling design on the real rule populations |
| [study/v007-results-analysis.md](study/v007-results-analysis.md) | **Results of the full run by category**, verified figures, charts verdict, what the results cannot say |
| [study/v007-validation-protocol.md](study/v007-validation-protocol.md) | **Validation, sampling and human-labelling protocol** (verification modes, designs, pilot gate, estimation, effort) |
| [../study/analysis-v007-2026-10-16/](../study/analysis-v007-2026-10-16/) | CSV tables behind the analysis and the 17 corrected charts |
| [study/v007-validation-research-prompt.md](study/v007-validation-research-prompt.md) | The deep research brief for the validation and its status |
| [../study/fp-precheck-v007-2026-10-15/README.md](../study/fp-precheck-v007-2026-10-15/README.md) | AI precheck of 101 calibration findings for false-positive mechanisms |
| [study/v007-validation-plan-v2.md](study/v007-validation-plan-v2.md) | **Validation plan v2**: claims, gates, labelling protocol, decision rules, importance-weighted allocation |
| [study/v007-pilot2-and-v0071-runbook.md](study/v007-pilot2-and-v0071-runbook.md) | Runbook: what is ready, the disk blocker, order of steps to v0.0.7.1 and pilot 2 |
| [study/v007-cleanup-for-next-runs.md](study/v007-cleanup-for-next-runs.md) | What to clean before the next runs |
| [../study/validation-v007-human/ai-precheck/claude-reference-2026-10-16/README.md](../study/validation-v007-human/ai-precheck/claude-reference-2026-10-16/README.md) | AI reference labels for the 350-item pilot (drift baseline, not gold) |
| [study/v007-reproduce-full-run.md](study/v007-reproduce-full-run.md) | Reproduce the frozen 207-repository run, and its architecture |
| [study/v007-full-run-investigation.md](study/v007-full-run-investigation.md) | Investigation report for the v0.0.7 full run |
| [../study/validation-v007-human/README.md](../study/validation-v007-human/README.md) | Human-validation split, pilot, codebooks, and protocols |
| [study/selection-protocol-v2.md](study/selection-protocol-v2.md) | Repository selection protocol behind the frozen manifest |
| [study/what-is-a-snapshot-study.md](study/what-is-a-snapshot-study.md) | Boundary between frozen source state and review/history evidence |
| [study/pipeline-design.md](study/pipeline-design.md) | Generic N-repository study pipeline design |
| [study/runbook.md](study/runbook.md) | Operational commands for running and resuming studies |
| [study/scripts-reference.md](study/scripts-reference.md) | Behaviour, schemas, and limits of the study scripts |
| [study/threshold-calibration-plan.md](study/threshold-calibration-plan.md) | Numeric threshold calibration and agreement plan |
| [study/v007-pre-benchmark-readiness.md](study/v007-pre-benchmark-readiness.md) | Readiness report before the v0.0.7 threshold benchmark |
| [study/v007-variable-certainty-implementation.md](study/v007-variable-certainty-implementation.md) | Variable-certainty implementation report |
| [study/v007-variable-resolution-results.md](study/v007-variable-resolution-results.md) | Variable-resolution corpus results |
| [study/v0071-run-summary.md](study/v0071-run-summary.md) | v0.0.7.1 full run summary and per-rule delta against v0.0.7 |
| [study/v0071-rerun-2026-10-22-full-report.md](study/v0071-rerun-2026-10-22-full-report.md) | **Full results report of the 2026-10-22 rerun**: every category, family and rule, distributions, repositories, all 17 charts, comparison |
| [study/v0071-rerun-2026-10-22-summary.md](study/v0071-rerun-2026-10-22-summary.md) | Full rerun on the consolidated branch: health, deviations, comparison (identical AnsibleGuard results) |
| [../study/analysis-v0071-rerun-2026-10-22/](../study/analysis-v0071-rerun-2026-10-22/) | Tables and 17 charts of the 2026-10-22 rerun |
| [../study/rq1-agreement-pilot/RQ1_RESULTS.md](../study/rq1-agreement-pilot/RQ1_RESULTS.md) | **RQ1**: Reviewer A/B agreement, adjudication sheet and guide, precision with intervals (provisional until adjudicated) |
| [../study/rq2-v0071-rerun-2026-10-22/RQ2_RESULTS.md](../study/rq2-v0071-rerun-2026-10-22/RQ2_RESULTS.md) | **RQ2**: rule co-occurrence at file and repository level, size-adjusted, on the 2026-10-22 rerun |
| [study/RQ1-RQ2-draft.md](study/RQ1-RQ2-draft.md) | Paper draft: RQ1 precision, RQ2 rule co-occurrence |
| [study/tool-performance-report.md](study/tool-performance-report.md) | Tool performance report (precision, recall) |
| [study/validation-structure-reconciliation.md](study/validation-structure-reconciliation.md) | How the two validation-tree structures fit together |

## Exploratory label passes

Earlier label passes over the pilot and stratified samples, and the
comparisons built on them, under
[../study/exploratory-labels/](../study/exploratory-labels/). Each folder's own
README or report records who or what produced its labels; see
[PROVENANCE.md](../study/exploratory-labels/PROVENANCE.md) for the owner's statement on
the Reviewer A and B passes. They are separate
from the formal human validation in `study/validation-v007-human/`.

| Folder | What it holds |
|---|---|
| `ai-shadow-review/`, `teammate-review/` | Reviewer labels for the 350-item agreement pilot |
| `annotation-comparison/` | Reviewer-agreement comparisons, phases 1 and 2 |
| `stratified-sample/`, `stratified-sample-v0071/` | Impact-weighted samples (v0.0.7 and v0.0.7.1) with their labels |
| `local-llm/` | Optional local-LLM explanations (`--explain`): setup, prompt, evaluation |

## Research and paper

| Document | What it covers |
|---|---|
| [research/saner24-approach.md](research/saner24-approach.md) | The SANER'24 smells paper and how AnsibleGuard relates to it |
| [research/checklist-coverage.md](research/checklist-coverage.md) | Mapping to the 38 code-review criteria |
| [research/article-approach.md](research/article-approach.md) | Article-ready approach section (build, test, evaluate) |
| [../report/](../report/) | University report (LaTeX) |

## Release history

[../CHANGELOG.md](../CHANGELOG.md) consolidates the former `VERSION_0.0.1.md`,
`VERSION_0.0.2.md`, and `CHANGELOG_0.0.4.md` … `CHANGELOG_0.0.6.1.md`.

## Removed historical documents

The 2026-10-15 cleanup removed about 80 historical root documents (session
handoffs, per-version status reports, OpenStack/Nova pilots, PR experiments,
v0.0.4–v0.0.6.1 audits and plans) and the `validation_process/` and
`study/validation-v4/` notes. They describe superseded versions and are
preserved unchanged in Git history. To read one, use the last commit that
still contains it:

```bash
git show 15ff61b9:PROJECT_STATUS.md          # any removed root document
git show 15ff61b9:validation_process/07-labels-regenerated.md
git log --diff-filter=D --name-only -- '*.md'   # list removed documents
```

Frozen study files that cite a document by its old root path (for example
`study/validation-v007-human/protocol/source/EXECUTION_PLAN.md` citing
`ANSIBLEGUARD_V007_FULL_RUN_INVESTIGATION_REPORT.md`) were not edited; the
moved copies are listed below.

| Former path | Current path |
|---|---|
| `HOW_IT_WORKS.md` | `docs/how-it-works.md` |
| `OUTPUT_FORMATS.md` | `docs/output-formats.md` |
| `ANSIBLEGUARD_COMMANDS_TESTING_AND_PR_GUIDE.md` | `docs/commands-and-pr-guide.md` |
| `REMOTE_SOURCE_ARCHITECTURE.md` | `docs/remote-sources.md` |
| `ALL_DETECTED_SMELLS.md` | `docs/rules/detected-smells.md` |
| `ULTIMATE_SMELL_CATALOG.md` | `docs/rules/smell-catalog.md` |
| `ANSIBLE_LINT_GITLEAKS_OVERLAP.md` | `docs/rules/external-tool-overlap.md` |
| `STUDY_PIPELINE_DESIGN.md` | `docs/study/pipeline-design.md` |
| `STUDY_RUNBOOK.md` | `docs/study/runbook.md` |
| `STUDY_SCRIPTS_REFERENCE.md` | `docs/study/scripts-reference.md` |
| `SELECTION_PROTOCOL_V2.md` | `docs/study/selection-protocol-v2.md` |
| `WHAT_IS_A_SNAPSHOT_STUDY.md` | `docs/study/what-is-a-snapshot-study.md` |
| `REPRODUCE_V007_FULL_RUN.md` + `V007_FULL_RUN_ARCHITECTURE.md` | `docs/study/v007-reproduce-full-run.md` |
| `ANSIBLEGUARD_V007_FULL_RUN_INVESTIGATION_REPORT.md` | `docs/study/v007-full-run-investigation.md` |
| `V007_207_PRE_BENCHMARK_READINESS_REPORT.md` | `docs/study/v007-pre-benchmark-readiness.md` |
| `V007_VARIABLE_CERTAINTY_IMPLEMENTATION_REPORT.md` | `docs/study/v007-variable-certainty-implementation.md` |
| `V007_VARIABLE_RESOLUTION_CORPUS_RESULTS.md` | `docs/study/v007-variable-resolution-results.md` |
| `NUMERIC_THRESHOLD_CALIBRATION_AND_AGREEMENT_PLAN.md` | `docs/study/threshold-calibration-plan.md` |
| `SANER24_PAPER_AND_ANSIBLEGUARD_APPROACH.md` | `docs/research/saner24-approach.md` |
| `CODE_REVIEW_CHECKLIST_COVERAGE.md` | `docs/research/checklist-coverage.md` |
| `ARTICLE_APPROACH_TOOL_BUILD_TESTING_PERFORMANCE.md` | `docs/research/article-approach.md` |
