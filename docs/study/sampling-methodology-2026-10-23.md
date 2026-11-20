# Sampling and evidence methodology based on the observed results

Status: development implementation and diagnostics now exist for the frame, probability draws, frozen source/metadata/construct retrieval and variance/interval stress tests. **No final design, interval, workload or population-performance score is accepted.** Human labels are not generated; separate synthetic local-LLM diagnostics remain development evidence. Model inference remains local only.

Current findings: [construct/lexical gaps by partition](../../study/evidence-constructs-2026-10-23/README.md), [normal interval failure](../../study/sampling-uncertainty-2026-10-23/README.md), and [conservative width/stratum benchmark](../../study/sampling-bounds-2026-10-23/README.md). The current draws use the frozen baseline frame; rebuild the final frame after detector/metric code freeze. The dependency sequence below remains the protocol proposal; completion states are recorded in the [running log](recovery-progress.md).

## 1. Start from the result we want to estimate

The next sample should answer explicit questions about defined populations. A family such as “security” is a useful reporting group, but does not describe how an example can fail, what evidence it needs, or its probability of selection.

Use six separate instruments:

| Instrument | Population/unit | Question |
|---|---|---|
| Required-finding validity | Emitted required occurrence, with its exact subject and predicate | Is the reported claim supported, and is it actionable? |
| Resolution accuracy | Occurrence with an uncertainty/resolution state | Is the uncertainty justified, and was the right missing-context class assigned? |
| Policy conformance | Optional policy occurrence | Does the source violate the stated applicable policy? Is that useful to its maintainer? |
| Threshold calibration | Source task/play/role in metric bands, including detector-negative units | Is the codebook-defined maintainability condition present independently of the existing cutoff? |
| Supported recall | Source unit selected independently of findings | Which supported smells exist, and which did the tool miss? |
| Review/PR validity | Actual comparable change and its findings | Does the diff support introduced/fixed attribution, and is the underlying claim valid? |

Keep a seventh, **diagnostic challenge panel**, for known failure mechanisms and local LLM development. Its purposive examples help repair code and retrieval. They do not estimate prevalence or precision.

Define two counting views before sampling. The current audit uses occurrences **assigned to AnsibleGuard after canonical provider merging**. It reproduces the existing report's 264,704 static-source total. An internal-detector capability study instead needs all internal native evidence, including evidence assigned to another provider. The next frozen internal-only source scan can supply that population without provider arbitration; an integrated developer-output study can retain canonical allocation. Do not switch between these frames after sampling or weight one using counts from the other.

## 2. What the current partition audit establishes

The new [frame audit](../../scripts/audit_sampling_partitions.py) joins the exact source population to the frozen repository split, execution status, rule metadata and the two explicitly listed exploratory samples. Its [artifacts](../../study/sampling-design-2026-10-23/README.md) contain counts and metadata, not source excerpts.

| Existing partition | Repositories | Required occurrences | Optional occurrences | Required rules present | Rules with ≥20 required occurrences in ≥8 repositories |
|---|---:|---:|---:|---:|---:|
| Calibration | 144 | 59,891 | 128,542 | 51 | 37 |
| Old heldout | 62 | 22,876 | 53,395 | 49 | 31 |
| Core timeout, outside the analyzable split | 1 | unavailable | unavailable | unavailable | unavailable |

There are **121 nonempty cells** when grouped by split, rule, policy, certainty, resolution status and resolution scope. Only 31 of the 49 old-heldout required rules meet the simple availability screen. That screen is not a guarantee of narrow intervals; several rules have substantial counts in very few repositories. For example, old-heldout excessive-nesting has 49 findings in two repositories and deprecated-modules has 47 in four.

The decision-state breakdown is:

| State | Calibration | Old heldout | Meaning for sampling |
|---|---:|---:|---|
| Required / CONFIRMED | 54,570 | 20,771 | Predicate result to verify; not human-confirmed truth |
| Required / EXPOSED | 4,454 | 1,797 | Security exposure claim; needs relevant protection/logging evidence |
| Required / UNRESOLVED | 728 | 269 | Candidate missing definition; absence must be checked at its actual scope |
| Required / ORDERED_CONFLICT | 139 | 39 | Execution/order claim; needs a path and ordering evidence |
| Optional / UNCERTAIN | 38,000 | 16,196 | Resolution-quality instrument, not a pool of confirmed defects |
| Optional / CONFIRMED | 90,542 | 37,199 | Policy/predicate instrument |

The 54,196 uncertain occurrences have materially different causes: external-input uncertainty (34,326), runtime-context uncertainty (17,161), bounded-graph unknown (2,106), and dynamic-protection unknown (603). These require different evidence packets and should not receive one shared “variable” sample allocation.

The current [verification-mode map](../../scripts/v007_verification_plan.py) provisionally places 45,677 required occurrences in threshold rules, 22,650 in deterministic rules and 14,440 in semantic rules. This map is an existing proposal requiring rule-by-rule review. An independent predicate check does not establish that the predicate expresses a meaningful defect.

### Independence status

The two listed exploratory samples contain examples from 55 of 62 old-heldout repositories. Seven are absent from those files, which does not establish they were untouched elsewhere. The audit therefore certifies **none** of the current repositories as final evaluation data. It preserves the original split as historical metadata and reports exposure separately.

Use the current population for calibration and descriptive replication. Review the exposure chronology. For a strong final validation, freeze a new repository cohort after the tool, codebooks and sampling protocol are fixed. If future continuous development needs multiple new partitions, assign repository groups to development, instrument pilot and final evaluation before their examples are inspected. Sample size and partition proportions should follow the intended claims and available independent repositories, not an automatic 70/30 convention.

## 3. Partition on the causes of error

Record these axes in the frame; their purposes differ:

| Axis | Concrete fields | Use |
|---|---|---|
| Development/evaluation role | `dataset_role`, `exposure_status`, `split_version` | Hard boundary; never fill a final-evaluation quota from development examples |
| Repository identity and dependence | project, SHA, fork lineage, substantial shared-content group | Prevent leakage and account for related repositories |
| Repository structure | selected-LOC quartile; role/collection/playbook layout; inventory/plugin presence | Repository-stage strata and balance diagnostics |
| Provider execution | core complete, all-provider complete, provider partial, timeout | Claim eligibility; failed observations remain unavailable |
| Decision policy | required, optional, unresolved advisory | Separate instruments and denominators |
| Rule and verification mode | stable native rule, predicate version, provisional A/B/C mode | Primary allocation; family/category is a reporting annotation |
| Certainty/resolution | CONFIRMED/EXPOSED/UNRESOLVED/ORDERED_CONFLICT/UNCERTAIN plus resolution reason | Primary decision cells; reserve appropriate evidence effort |
| Evidence requirement | local construct, complete file, role graph, inventory/runtime contract, version metadata, real diff | Retrieval strategy and packet QA |
| Metric region | below/near/above cutoff; sparse extreme; relevant composite branch | Threshold instrument; sample both triggered and untriggered units |
| Artifact/applicability | tasks, handlers, defaults/vars, metadata, inventory, non-Ansible YAML, vendor/generated | Eligibility and classification audit |

Do not create the full Cartesian product of all axes. Most cells would be empty or too small. Use disjoint primary cells, repository-size strata inside them, and prespecified marginal checks for structure, provider state, artifact and evidence requirement. Merge sparse design strata only under a rule defined before labeling; keep the original analysis tags. Final-evaluation boundaries and required/optional/uncertain instruments are never merged to meet a quota.

Repository groups need a careful definition. The overlap bug showed identical files in different repositories. Fork lineage and substantial overlap of executable task trees are stronger leakage evidence than one shared boilerplate file. Do not join all projects into one group because they share a common role or license. Record copied-role clusters separately and use them in sensitivity analyses; prespecify the grouping criterion and review its components without using final labels.

## 4. Use probability sampling for estimation

### Define the frame before opening source contexts

For each selected population view, store a unique identity `(run, repository, SHA, native rule, occurrence/subject)`, artifact kind, source span, decision state, repository group and all design fields. Reconcile the frame with execution counts. Reject stale SHAs, duplicate identities, missing rule definitions and mixed runs. Freeze the frame hash, selection seed, codebook and script identity.

Avoid the existing “first occurrence per repository” behavior in `build_v007_stratified_sample.py`: when that branch is used, remaining occurrences in a repository have no chance of being selected. Also avoid estimating a file's probability as `total / len(capped_pool)` after a random repository cap; that omits the first-stage cap probability, as in the current `build_source_first_recall_sample.py`. These legacy samplers remain calibration tools until repaired.

### A concrete two-stage design

For emitted-finding instruments, begin with cells `h = rule × policy × decision/resolution state` within one permitted dataset partition. Some rules have one cell; others have several. For each h:

1. Partition repositories carrying h into a small, frozen set of structure/size strata b. Use a prespecified sparse-stratum merge rule.
2. In each b, let `M_hb` be the number of eligible repository groups. Select `k_hb` groups uniformly without replacement using a seeded random selection. If groups contain multiple repositories, explicitly add that selection stage or enumerate their members; do not pretend a group is one repository.
3. Within a selected repository/group, sample `m_hbj = min(q_hb, N_hbj)` occurrences uniformly without replacement. The quota q is set before drawing or seeing labels. Prefer more independent groups and a small within-group quota, initially two, where the population permits it.
4. Record the probability and its inverse for every selected occurrence. For a one-repository group:

   `π_i = (k_hb / M_hb) × (m_hbj / N_hbj)` and `w_i = 1 / π_i`.

5. Census a genuinely small finite cell when feasible. A census has π=1 and removes sampling error for that cell; it does not remove annotation error or establish generalization to other repositories.

Example: selecting 10 of 20 repository groups and two of a repository's 100 occurrences gives π=0.01 and weight 100. For a repository with 10 occurrences, the same design gives π=0.10 and weight 10. Equal reviewer effort per repository therefore cannot be analyzed with an unweighted pooled fraction.

Because `min(q, N_hbj)` varies by repository, achieved sample size can vary. Plan against expected cost and simulated precision; do not keep changing repository quotas until an exact total is reached unless the resulting adaptive design has explicit probabilities. A deterministic hash rank is reproducible, but needs a prespecified random seed and a defined sampling frame to act as a randomized selection design; ranking alone does not make arbitrary exclusions unbiased.

### Allocation and feasibility

- Establish minimum coverage for each rule/decision cell that supports an intended claim, then allocate remaining budget using population size, calibration-only variance and review cost. Do not interpret square-root allocation as population weighting.
- Compare candidate budgets such as 800, 1,000 and 1,200 required-finding reviews in simulation on the final population. These are planning scenarios, not selected workloads.
- On the current old-heldout frame, `sum(min(N_rule, 20)) = 797` even before separating decision states. Thus 400 items cannot provide 20 cases for every rule, and 20 is itself a modest screening minimum, not a power guarantee.
- Require the predeclared minimum independent groups as well as a sample size for reportable intervals. The existing ≥20 items / ≥8 repositories convention can screen sparse estimates, but must be assessed in simulation. For fewer groups, label results as a finite-case/census description and show the support.
- Keep every eligible item at positive probability within a claim population. When budget cannot cover the intended rules, reduce the stated claim set before selection and publish the uncovered rules.

Probability weights and design variables are necessary when subgroups are deliberately oversampled and observations are clustered. This is the general survey-design principle applied here, not a claim that the Ansible corpus is a representative sample of all GitHub projects. See [CDC sample-design guidance](https://wwwn.cdc.gov/nchs/nhanes/tutorials/SampleDesign.aspx) and [weighting guidance](https://wwwn.cdc.gov/nchs/nhanes/tutorials/weighting.aspx).

## 5. Retrieve enough evidence for the selected claim

Selection precedes source retrieval. Every selected ID receives a packet or an explicit retrieval-failure record. The packet builder reads `SHA:path` from a verified immutable snapshot and records content hashes. It must not silently substitute the working tree or clamp a wrong line to the nearest valid line.

| Evidence partition | Packet requirements |
|---|---|
| Local syntax/type/name | Complete parsed construct, exact attribute/subject span, applicability facts and target Ansible version |
| Whole-file structure/size | Correct file kind, complete file or complete relevant constructs, metric values/units, cited task/block members |
| Variable/default/input | Named use, visible definitions, must/may reachability, imports/includes, execution order, guards, role argument contracts, known inventory/runtime blockers |
| Handler/register | Handler and `listen` identities, notifications/uses, imported files, conditional paths and registered-result origin |
| Security/logging | Argument-spec metadata, effective/inherited/overridden no-log evidence, display/register chain, safe facts distinguishing placeholders, paths and real sensitive literals |
| Version/dependency | Resolved module and collection version, routing/deprecation facts, dependency kind and pinning policy |
| Duplication | Both candidate blocks and their source spans; one count at line 1 is insufficient |
| Review/PR | Actual base/head identities, verified parent/range, relevant YAML and non-YAML diffs, repository policy evidence |

Keep evidence availability separate from semantic judgment. A possible same-name definition in an unrelated role does not prove safety. A missing dynamic runtime input does not prove a defect. Packet metadata should say which relevant relationships are established, possible or unknown.

Redaction should preserve YAML types, guards and relationships. Where a decisive literal must be hidden, supply auditable safe facts, such as “path-shaped literal” or “recognized placeholder,” with the classifier and its version. Review those derived facts independently on a small local QA set. If the needed distinction remains unavailable, mark that limitation; do not require a forced positive/negative judgment.

Record `retrieval_status`, `anchor_verified`, `required_evidence_missing`, `truncated`, `redaction_effect`, packet version and hashes. Repair a defective packet for the same selected ID and retain its previous version. Report the initial defect rate as well as the repaired rate.

### Do not replace inconvenient examples silently

Unreadable files, unavailable SHAs, oversized roles and uncertain context are informative failure modes. Keep them in the selection ledger as unreviewable or missing. A secret/corrupt/unrecoverable case stays in the reporting denominator under the prespecified missingness policy.

If a genuine population-ineligibility error is discovered, record and review the frame correction, produce a new frame version, and recompute the design. Do not replace it with the next easy example while claiming the original probabilities. Reserve draws are acceptable only with a defined reserve/response design and corresponding probabilities; otherwise analyze the original draw and its nonresponse.

## 6. Allocate the other instruments separately

### Resolution and policy panels

Start a calibration resolution panel across the four uncertainty causes, for example 30 cases per cause where enough independent groups exist. The balanced 120-case workload is an instrument pilot, not a proportional population sample. Judge separately:

- Is the detector's uncertainty justified?
- Is the assigned resolution class supported?
- What missing evidence could settle it?
- Does the developer-facing wording avoid a stronger defect claim?

For policy conformance, sample optional confirmed output separately from uncertainty. Rare policies may be censused; dominant policies should not consume the required-defect budget merely because they produce many rows. Record whether the policy actually applies to this repository and distinguish conformance from actionability.

### Threshold panels

Use source units on both sides of the cutoff: clearly below, near below, near above, and far above, plus important composite-branch cases. Freeze the bands before human judgment. Review the maintainability condition with the production cutoff and current predicted label hidden, using a codebook that defines the condition independently of that cutoff. Store inclusion probabilities by repository and metric band.

Use fresh items after codebook revisions. The three existing large-task rounds on the same 75 examples support instrument development; they do not provide an independent third agreement study. Separate independent measurement-oracle checks from the question of whether a threshold is useful. Rebuild the metric frame after traversal/LOC definitions are repaired.

### Source-first recall and classification

Sample eligible source independently of findings, including source with zero output. Choose the primary unit for each rule class: task/file for local rules, role or bounded dependency neighborhood for cross-file rules. Reviewers enumerate supported issues before seeing detector results. Record a stable subject for each enumerated issue so both tools and humans can be matched without counting the same issue twice.

Also audit file classification: sample admitted and excluded YAML strata, including non-Ansible data, templates, vendor/generated content and uncertain classifications. Otherwise a detector can appear precise simply because the frame excludes difficult true Ansible content. Report classification error separately from smell recall.

Weight human-found supported defects using the source unit's selection probability; compute supported recall from weighted detected and missed counts. Report unresolved-context coverage separately. Synthetic seeded defects measure controlled sensitivity; they are not substitutes for naturally occurring source-first recall.

### PR and local LLM panels

PRs need verified history and a defined PR-selection population; snapshot repositories missing a parent are not clean negative reviews. Build from the existing replay as calibration, then sample independent comparable changes for final claims.

For the local LLM, keep development challenge cases, a prompt/model selection set and an unseen acceptance set separate at repository/role-cluster level. Balance supported, contradicted, insufficient-evidence and policy-dependent examples; include the observed cross-file and schema failures. Score decision correctness, support for cited evidence, harmful fixes, coverage, abstention and resource use. Balanced challenge-set accuracy is not the explainer's natural-population accuracy. Model labels never supply human gold or affect final sample selection.

## 7. Estimate with the design and all outcomes visible

For an eligible probability sample with weights w, let P, N, U, R and M be the weighted totals of positive, negative, uncertain, unreviewable and missing/pending items.

- Decided precision: `P / (P + N)`, explicitly conditional on decidability.
- Conservative supported yield: `P / (P + N + U + R + M)`.
- Unresolved-outcome upper bound: `(P + U + R + M) / (P + N + U + R + M)`.
- Report U, R and M rates, retrieval failure, review effort and actionability alongside precision.
- For rule/family/domain summaries, use the original inclusion probabilities. Category totals must not become a substitute for the sampling design. Preserve full design information when estimating subdomains.
- Report occurrence-weighted, repository-balanced and macro-rule summaries as separate estimands. One can improve while another worsens.
- Do not combine purpose-built challenge examples, extra threshold cases, repeated reviewer items and the probability sample into one naive fraction. If independent probability panels are combined, derive union inclusion probabilities and handle overlap explicitly.

Use design-aware variance estimation with the actual stages, strata and independent groups. Repeated files/roles and shared repository history require sensitivity analysis. Do not assume a percentile bootstrap is calibrated just because it resamples repositories: the [existing simulation](../../study/validation-design-v007/README.md) found substantial undercoverage, particularly with high precision or few groups. The survey principle that clustering and unequal probabilities affect variance is summarized in [CDC variance guidance](https://wwwn.cdc.gov/nchs/nhanes/tutorials/varianceestimation.aspx).

Before final labels, simulate the proposed design using the refreshed count frame: high/mixed/low precision; repository-size correlations; copied-role effects; sparse rules; all-positive samples; retrieval failures correlated with complexity; uncertainty and reviewer disagreement. Compare bias, interval coverage, width and cost. Select the interval/design under a preregistered simulation suite; increasing nominal confidence to fit one favorable scenario is not a general calibration strategy.

## 8. Human workflow and immutable artifacts

Two reviewers label independently from the same versioned evidence with randomized order. Hide other labels, AI output, selection weights and the production threshold when testing threshold meaningfulness. Preserve separate semantic truth, actionability, applicability, context sufficiency and resolution-class questions. Freeze both first passes before adjudication; the adjudicator should not have produced the disputed initial labels. Audit a small random portion of agreed cases for shared error, and treat repeat items as repeatability checks with zero additional population weight.

Freeze these artifacts:

1. Claim registry: each population, unit, eligibility, estimand and supported interpretation.
2. Repository/group registry: exact SHAs, old split, exposure evidence, new dataset role and group identity.
3. Source/occurrence frame: units and design metadata with no hidden exclusions.
4. Design configuration: strata, quotas, seed, stage probabilities, sparse-cell rules and budgets.
5. Selection ledger: every selected ID, π, weight and evidence/label status; retain failures.
6. Packet manifest: source/packet hashes, spans, retrieval results and redaction facts.
7. Independent label files and adjudication history.
8. Analysis manifest: frame/design/codebook/label hashes, estimator, simulation gate, execution coverage and claim eligibility.

The existing non-author sign-off decision remains in force; record its completion rather than reopening it. Final evaluation labels stay sealed until code, predicates, evidence builders and analysis are frozen. Any post-evaluation fix needs a new version and subsequent independent evaluation for improvement claims.

## 9. Practical implementation sequence

| Step | Deliverable | Acceptance criterion |
|---|---|---|
| Implemented now | Permanent RQ1 eligibility exclusion; scoped diagnostics | A completed pilot cannot become a final population precision report |
| Implemented now | Frame audit and four partition tables | Counts reconcile; failed result is unavailable; no source excerpts or sample draws created |
| Next | Reviewed claim/repository/exposure/group registry | Current data has explicit development scope; final evaluation route is agreed |
| Calibration prototype implemented | Rule/decision-cell two-stage sampler | Exact stage probabilities and seed replay checked; final registry and allocation remain pending |
| Development checks implemented; final method unaccepted | Simulation against refreshed cells | Six fixed populations × six allocations compare point error, both-stage variance, normal coverage, conservative bounds and cost; normal intervals rejected; fresh stresses/nonresponse/reviewer error remain pending |
| Source/metadata/construct diagnostics implemented | Evidence builder | Every selected ID retains exact source and verified metadata; candidate units/lexical outcomes audited by rule/decision/size cells; typed identity, applicability, rule dependencies and completeness remain uncertified |
| Next | Fresh calibration pilots | Existing agreement/uncertainty gates pass or claims are narrowed |
| After detector freeze | New final population and probability selection | No development tuning from final labels; independent review and design-aware estimation |

This design aims to reduce avoidable selection bias and make remaining uncertainty measurable.

Implementation evidence: [calibration draws](../../study/sampling-draws-2026-10-23/README.md) and [point-estimator checks](../../study/sampling-draws-2026-10-23/SIMULATION.md). The checks found substantial variance and sparse-stratum ratio bias, so neither workload is a final accepted design.

Follow-up evidence changes the next decision: [normal intervals](../../study/sampling-uncertainty-2026-10-23/README.md) fail near the boundary; a [conservative finite-design benchmark](../../study/sampling-bounds-2026-10-23/README.md) is too wide; [six both-stage allocations](../../study/sampling-allocation-2026-10-23/README.md) show that increasing expected review volume from 850.62 to 4,095.36 IDs still yields only 75.75% near-boundary coverage for a nominal 95% global-Hájek normal interval. More observations alone do not validate this interval. Keep groups and within-group quotas as separate decisions, compare boundary-aware methods and targeted size-cell allocations, and require fresh population/nonresponse/reviewer-error stress tests before selecting a final workload.

[Exact-source retrieval and local cache recovery](../../study/evidence-retrieval-2026-10-23/local-cache-recovery/README.md) now supplies base source for each selected ID. This establishes source identity, not semantic evidence completeness; the next packet layer must verify the subject, construct and dependencies.

[Verified canonical metadata](../../study/evidence-metadata-2026-10-23/README.md) and [construct/lexical diagnostics](../../study/evidence-constructs-2026-10-23/README.md) now preserve all 2,331 calibration IDs across the alternative panels, without treating overlapping panels as additive independent observations. Alias/duplicate-key failures, case-fold-only names, placeholders, truncation and redaction remain explicit outcomes. Shared metric traversal/name semantics have since advanced to `declared-leaf-tasks-v3`; the frozen diagnostics retain their original implementation hashes and the final frame must be rebuilt after freeze.
