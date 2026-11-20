# Recovery progress

Branch: `fix/recovery-2026-10-23`

This is the running implementation log for the [recovery plan](recovery-plan-2026-10-23.md). Each completed repair records its cause, changes, validation and remaining limits. All model work must run locally.

Current review: selection/source/canonical metadata are linked for all four calibration draws; structural task metrics are versioned; LLM transport, response validation and head/staged context are repaired. The [current explanation contract](verified-claims-v82.md) has no independent accuracy estimate. Human labels/final-population eligibility have not been generated or promoted. Later sections record automatic continuation and remaining gates.

## 2026-10-23 — Step 1: correct provider-overlap accounting

Status: implemented and validated.

### Problem

`scripts/compare_with_ansible_lint.py` used an export filename and occurrence ID as its matching identity. IDs recur across repositories containing shared files. The matching dictionaries therefore overwrote or collapsed independent repository evidence. A lint occurrence could also be reused for multiple findings at one location, and repeated export rows were counted repeatedly.

### Changes

- Scope occurrence identity to run ID, repository, source commit and occurrence ID.
- Scope location matching to the same run and repository revision.
- Count repeated exports of one canonical occurrence once per native rule.
- Reserve shared canonical matches before matching remaining occurrences at the same file/line.
- Consume each location candidate once, in deterministic order; both tools' totals reconcile as matched plus unmatched.
- Reject conflicting locations for one snapshot occurrence identity.
- Describe the result as evidence overlap between related rules; semantic equivalence and recall require separate validation.

Files: [comparison implementation](../../scripts/compare_with_ansible_lint.py), [regressions](../../tests/test_compare_with_ansible_lint.py).

### Validation

- `.venv/bin/python -m pytest -q tests/test_compare_with_ansible_lint.py tests/test_rq_scripts.py`: **16 passed**.
- Recomputed all nine pairs using the original aggregate files extracted from the archived `v0071-rerun-2026-10-22` run: **171 provider-complete repositories**.
- Checked that `both + tool_only == tool_total` for each tool and pair.
- Compared every field with the historical CSV: exactly two values changed, both `ansible_lint_only`:

| AnsibleGuard rule | Historical | Corrected |
|---|---:|---:|
| `non-idempotent-command` | 3,188 | 3,187 |
| `unnamed-task` | 751 | 736 |

- `git diff --check`: passed.

Corrected output and reproduction details: [comparison evidence](../../study/ansible-lint-comparison-v0071-rerun-2026-10-22/README.md). The historical CSV remains a record of the earlier computation; the corrected CSV has its own filename and provenance manifest.

### Limits

Same-line matching remains a heuristic. This step fixes identity and accounting, and does not establish equivalent rule predicates, activated-rule coverage, precision or recall. Existing detector outputs were reused; no detector scan or LLM run was needed.

## 2026-10-23 — Step 2: separate adjudication from evaluation eligibility

Status: implemented and validated.

- `rq1_precision.py` now reads the sample manifest and pilot/exclusion flags in the master. Those exclusions survive completed adjudication.
- Every precision table carries evidence scope and `eligible_for_performance_scoring=false`. Filenames identify calibration or descriptive scope; settled labels no longer produce unqualified precision tables.
- Even a manifest declaring sample eligibility cannot promote this legacy, unweighted diagnostic script into a population estimator.
- `report-status.json` records adjudication separately from eligibility and hashes its inputs.
- Regenerated a separate [calibration diagnostic snapshot](../../study/rq1-agreement-pilot/recovery-2026-10-23/README.md) from the original evidence: 119 semantic disagreements remain; population precision is explicitly not estimated.
- Regression coverage verifies completed pilots remain excluded and unknown/declared-eligible inputs remain descriptive.
- Focused RQ/comparison checks: **22 passed**. Historical labels and analysis files were not rewritten.

The next sampling implementation needs design probabilities and an exposure-reviewed population; changing report labels alone does not create those.

## 2026-10-23 — Step 3: inventory partitions and specify the sampling design

Status: frame audit implemented and validated; methodology proposed; sampler and evidence builder pending.

- Added [audit_sampling_partitions.py](../../scripts/audit_sampling_partitions.py). It checks repository/source identities, duplicate occurrences, static/core scope and single-run inputs, then builds repository, decision-cell, marginal and rule-feasibility tables without selecting examples or opening source files.
- [The refreshed frame](../../study/sampling-design-2026-10-23/README.md) reconciles 264,704 occurrences into **121 nonempty split/rule/policy/certainty/resolution cells**. Calibration has 59,891 required occurrences; old heldout has 22,876.
- Only **31 of 49** old-heldout rules with required output have ≥20 occurrences across ≥8 repositories. This is an availability screen, not an interval guarantee.
- The exposure join identifies examples in 55 of 62 old-heldout repositories from the two listed samples. Missing membership remains unknown exposure; no current repository is certified as final evaluation data. Failed core measurements remain unavailable.
- Wrote [sampling-methodology-2026-10-23.md](sampling-methodology-2026-10-23.md): separate instruments, repository/decision/evidence partitions, exact two-stage probabilities, weights, source-first recall, threshold bands, local LLM acceptance sets and design-aware simulation.
- Identified two additional legacy sampler mechanisms to repair: first-occurrence-per-repository preference and cap-then-probability calculation. They are documented leads; this batch does not replace those samplers.
- Focused partition/RQ/comparison checks: **30 passed**. Real frame and diagnostic output were regenerated; counts and input/output provenance were checked.

## 2026-10-23 — Step 4: implement calibration probability sampling and point-estimator checks

Status: implemented and validated for development draws; final design/interval gates pending.

### Sampler

- Added [sample_partitioned_occurrences.py](../../scripts/sample_partitioned_occurrences.py), with verified frame/source hashes, separate required/uncertainty/optional-policy instruments, fixed calibration scope and no heldout override.
- Selects repository groups within rule/decision/size strata, then occurrences uniformly within each group. Small cells are censused. Input ordering cannot privilege the first occurrence.
- Stores both stage probabilities, inverse weights, all selected IDs, source identities, and pending retrieval/label states. Sparse bins and achieved workload remain explicit.
- Supports explicit group maps by pooling member occurrences; rejects cross-partition groups. Default repository clusters do not certify shared-content independence.
- Refuses to overwrite a draw. Prior item reuse is explicitly unfiltered; these are development draws, not fresh agreement pilots.

### Real-population draws

[Recorded draws and reproduction](../../study/sampling-draws-2026-10-23/README.md):

| Instrument/configuration | Population | Selected IDs | Repositories | Rules |
|---|---:|---:|---:|---:|
| Required, up to 3 groups per size stratum | 59,891 | 861 | 125 | 51 |
| Required, up to 5 groups per size stratum | 59,891 | 1,266 | 131 | 51 |
| Uncertainty | 38,000 | 88 | 41 | 4 |
| Optional policies | 90,542 | 116 | 48 | 6 |

The required configurations are alternatives. No source context or labels were generated; every selected ID remains in its ledger.

### Simulation and validation

- Added [simulate_partitioned_sampling.py](../../scripts/simulate_partitioned_sampling.py). Compared four point estimators over six planted finite binary populations, with 400 draws per scenario for each required design.
- Naive pooling has roughly 15 percentage points of observed bias under size/validity correlation. Global product weights reduce this bias, but produce substantial variance. Normalizing ratios within sparse strata reintroduces up to 7.60 percentage points of observed bias. The larger group allocation improves variance at higher review cost.
- [SIMULATION.md](../../study/sampling-draws-2026-10-23/SIMULATION.md) records the full results and unfavorable cases, including HT estimates outside [0,1]. No estimator or final workload is approved by this point check.
- Confidence intervals, nonresponse, reviewer error and final-population independence remain unvalidated. These results are synthetic design diagnostics, not measured tool accuracy.
- Focused checks: **54 passed**, including exact enumeration of the product-weight expectation, seed replay, census behavior, size-stratum probabilities, instrument separation, hash checks and refusal to overwrite.
- Verified every ledger against its plan: probabilities and inverse weights reconcile, IDs are unique, scope is calibration-only, and retrieval/label states are pending. Manifest hashes match the actual inputs, outputs and implementations.
- Replayed the real 861-ID required draw into a separate directory: selection ledger, sampling plan and manifest match byte for byte.

## 2026-10-23 — Step 5a: retrieve exact source from primary clones

Status: base-source retrieval implemented; primary pass complete; local cache recovery and rule-specific evidence pending.

- Added [retrieve_sample_evidence.py](../../scripts/retrieve_sample_evidence.py). Reads immutable Git objects with replacement objects/lazy fetching disabled; verifies commit, literal path, file mode, blob ID, byte limit, UTF-8 and anchor bounds. No worktree fallback or line clamping.
- Reuses full-file line-preserving redaction and the independent residual scan before writing local packets. Packet output is ignored by Git; tracked reports hold statuses and hashes.
- Preserves each selected ID and weight, including failures. Original selection ledgers remain pending immutable inputs; derived ledgers record retrieval results separately.
- [Primary pass reports](../../study/evidence-retrieval-2026-10-23/README.md): required 834/861 source-retrieved, alternative 1,230/1,266, uncertainty 86/88, optional policies 116/116. All failures are commits absent from the primary clone directory in three projects. Their exact commits were subsequently located in existing local caches; recovery will use the same IDs.
- Reports distinguish line bounds from semantic subject verification. All rule-specific evidence remains incomplete. Redaction affects 13 required anchors and one alternative packet is explicitly windowed.
- Regression checks cover changed HEAD/worktree, Git replacement refs, literal pathspec characters, symlinks, unavailable commits/paths, invalid anchors, redaction failures, hash changes, retained rows and output separation.
- Focused checks: **89 passed**. Verified all 2,266 primary-pass packet hashes and residual scans, report hashes and the ignored local packet tree.

## 2026-10-23 — Step 5b: recover exact selected snapshots from existing local caches

Status: base source retrieved for every selected ID; semantic/rule-specific completeness remains pending.

- The three missing commits were already in the local frozen-run cache. Added ordered explicit local stores, same-SHA/path verification, controlled attempt history and trusted cache-link resolution.
- Recovering an ID never changes its selection probability or weight. Previous report hash, selected identities and weights are checked before recording recovery. Original primary reports remain intact.
- [Recovery reports](../../study/evidence-retrieval-2026-10-23/local-cache-recovery/README.md): required **861/861**, alternative **1,266/1,266**, uncertainty **88/88**, optional policies **116/116** source-retrieved. Recovered primary failures: 27 / 36 / 2 / 0 respectively. The required alternatives overlap and are not additive workloads.
- All 2,266 previous-success packet hashes are unchanged. Verified all 2,331 current packet hashes/residual scans and unchanged selected identities/weights. All 4,597 local packet files across attempts are ignored by Git.
- Focused checks: **95 passed**, including missing-commit cache recovery, trusted links, all-store failure history, no fallback around size limits, and previous-report identity/provenance.
- Zero semantic subjects or complete rule-specific packets are certified. Redacted-anchor and truncated-window flags remain; no labels or model calls were made.

## 2026-10-23 — Step 5c: join frozen canonical metadata

Status: provenance joined for every selected ID; semantic grounding remains pending.

- Added [join_sample_metadata.py](../../scripts/join_sample_metadata.py). Independently verified the full frozen archive checksum before streaming canonical records; no archive extraction or link following.
- Join identity includes run, repository, exact commit and occurrence. File, line, internal provider/native rule and all decision-cell fields must also match. Missing/ambiguous/invalid sources remain recorded failures, never replacement samples.
- [Reports and reproduction](../../study/evidence-metadata-2026-10-23/README.md): all **861 / 1,266 / 88 / 116** selected IDs joined. Source/selection identities and weights remain unchanged. Original member and normalized item hashes are recorded; redacted detector text stays local and ignored by Git.
- Required draw subjects: **553 location-only, 170 tasks, 113 variables, 25 attributes**. These are unweighted packet counts, not population estimates. Location-only identity needs construct grounding; named subjects still need independent matching. Message-derived canonical names may have lost identifier case.
- Corrected a development issue before committing: line-based redaction of compact JSON discarded the rest of a record after a sensitive field. Metadata display now puts fields on separate lines and keeps a separately screened subject. All 2,331 final packet hashes/residual scans pass; no selected subject was changed by redaction.
- Focused checks: **114 passed**, including cross-repository ID collisions, duplicate archive members, ambiguous occurrences, decision-cell mismatches, archived links/limits, checksum rejection, same-file checksum/traversal and preservation of non-sensitive context during redaction.
- All subject/completeness flags remain false. Zero labels or model calls. Automatic continuation is enabled by the user's instruction: complete tested, documented batches and proceed to the next independent engineering repair.

## 2026-10-23 — Step 7a: enforce local LLM transport and strict answer/source checks

Status: safeguards implemented; semantic answer quality remains unevaluated.

- Local inference is enforced with loopback-only endpoints, no environment proxies and no redirects. CLI help reflects the restriction.
- Exact source anchors replace line clamping. Invalid/missing/unreadable/outside-root/binary/oversized source produces `insufficient-context` without a model call.
- Runtime validation now enforces the response schema's types, enum, required/unknown fields and limits, rejects duplicate/non-finite JSON, and requires limitations below high confidence. Invalid/incomplete/oversized transport envelopes cannot become successful explanations.
- Added generation and prompt/response size limits. Whole-run deadlines, neutral assessment/abstention schema and source-complete semantic evidence remain pending.
- **166 tests passed**, including actual loopback HTTP/proxy/redirect regressions plus output contracts, SARIF and diff workflows. No live model or hosted inference was used; no accuracy improvement is claimed.
- Proceeding automatically to snapshot lifetime/context correctness, then shared metric traversal and evidence construction. Human evaluation gates remain separate from code completion.

## 2026-10-23 — Step 7b: explain the analyzed head/index snapshot

Status: head/staged source lifetime and graph cache isolation repaired.

- The diff CLI keeps exact head/staged trees alive through comparison/enrichment/reporting, uses them for explanation/documentation/playbook context, and then cleans up. Report locations still target the user's repository.
- Saved result folders no longer cause explanations to read an unrelated current checkout. Their source context is explicitly unavailable; per-item explanation status and the Markdown summary state insufficiency. Occurrence comparison still runs.
- Replaced process-global root-only graph caching with reuse limited to one enrichment operation; direct calls rebuild, and exceptions discard the operation cache.
- Added integration fixtures with different committed/staged/unstaged markers, sequential and parallel head analysis, dirty worktree/index preservation and cleanup on success/failure. Models are stubbed.
- Source/explanation/diff/output/SARIF/annotation checks: **185 passed**. No model accuracy claim. Ordinary working-tree concurrency, verified saved-source reattachment and graph reachability evidence remain open.

## 2026-10-23 — Step 8a: share and version structural task traversal

Status: task population and summary consistency repaired; historical rerun/threshold validation pending.

- Added one iterative traversal for raw mappings and YAML nodes. Counts declared leaves across pre/tasks/post/handlers and every block/rescue/always branch; excludes wrappers consistently in task-only files and plays. Aliases at distinct positions remain separate; cycles fail explicitly.
- Task/play/playbook metrics and report counts now use this shared population. Changed-task counts exclude wrappers and handle block/flow end boundaries. Counts describe declarations, not runtime execution or include expansion.
- New run provenance records `structural_metrics_version=declared-leaf-tasks-v2`; semantic comparison rejects mismatched/legacy-missing versions unless explicitly overridden. Existing metadata-free legacy comparison behavior remains marked unverified.
- **134 focused tests passed**, including all-section/branch parity, task-only wrappers, parsed-document parity, source lines/play IDs, aliases/cycles/deep nesting, changed-line spans, output consumers and version rejection.
- [Metric definition, affected rules and research limits](structural-metrics-repair-2026-10-23.md). Normalized LOC definitions, frozen results and threshold labels were not changed. A fresh impact diagnostic/pilot is still required before accuracy/frequency claims.

## 2026-10-23 — Step 7c: neutral LLM assessments and checked quotations

Status: versioned answer contract and report propagation implemented; live semantic acceptance pending.

- Response schema 2 / prompt `local-review-v2` requires supported / unsupported / insufficient-evidence outcomes. Supported/unsupported require source citations; insufficiency requires missing dependencies, low confidence and limitations. Contradicted/unproven findings cannot carry fixes.
- Validate citation file, line and exact quote against only context lines supplied for that call, including retrieved candidate definitions. Real but omitted source and fabricated/moved quotations are rejected. Quote matching is not semantic validation.
- Preserve assessment, evidence, missing dependencies and versions through all output formats. Unsupported/insufficient results are visible without a fix, remain unverified opinions, and do not override detector policy/counts. Failed re-enrichment discards old LLM fixes and fields.
- **253 tests passed** across LLM, reporting, snapshot/diff and finding suites; a final focused check additionally rejects silent legacy-answer promotion. No inference is included in those test results. A read-only local probe confirms the already-installed Qwen model is available; proceeding to a separate synthetic live acceptance diagnostic.

## 2026-10-23 — Step 5d: locate frozen constructs and audit lexical subjects

Status: structural context diagnostic complete for all selected IDs; rule completeness remains uncertified.

- Added [ground_sample_constructs.py](../../scripts/ground_sample_constructs.py): verifies selection/metadata/packet hashes, rereads exact SHA/blob source, composes bounded non-executing YAML nodes, locates candidate task/play/mapping context and screens lexical subject identity. No labels or model calls.
- [Reports and methodology changes](../../study/evidence-constructs-2026-10-23/README.md): required **661 construct candidates / 185 file-only / 8 alias / 7 duplicate-key review** across all 861 retained IDs. Alternative: 963 / 283 / 11 / 9 across 1,266. Uncertainty: 86 + 2 aliases; optional: 59 constructs + 57 file-only.
- Required subjects: 142 exact tokens, 119 case-fold-only task names, 22 placeholders, 546 no named subject, 6 unmatched tokens, 4 without anchored constructs, 4 unsupported shapes, 3 template parse gaps, 15 unexamined because YAML needs review. These are lexical/context outcomes, not tool correctness labels.
- During development, added duplicate/complex-key guards to avoid last-key-wins context, register/loop literal tokens, canonical display-name whitespace handling and explicit placeholder statuses. Final outputs were regenerated after these changes; no historical frozen outputs were rewritten.
- Outcome cells cross instrument/rule/policy/certainty/resolution/size and retain repository/group counts, instead of only category summaries. All original selection columns, probabilities, weights and pending labels reconcile. All 2,331 packet hashes, line ranges/display bounds, output hashes and residual scans checked; local source packets remain ignored.
- **109 focused tests passed**. All semantic-subject/applicability/completeness flags remain false. Full-unit truncation/redaction and alias/duplicate failures remain explicit. Named `Unknown` is distinguished in lexical review from generated placeholders; detector consumers' display-sentinel conflation is the next concrete bug to fix.

## 2026-10-23 — Step 8b: distinguish literal names from display placeholders

Status: name-presence fix implemented; focused and full-suite verification complete.

- The construct audit exposed `Unknown` sentinel conflation. Added shared `task_has_name` semantics and explicit `has_name` task metrics. Literal `Unknown` names are named, have length seven, and participate in duplicate checks; absent/null/blank/non-string names retain the existing unnamed behavior and display compatibility.
- Structural metric provenance advances to `declared-leaf-tasks-v3`; comparison tests reject both V2 and absent legacy versions against V3. V2 leaf traversal itself is unchanged. Historical runs/labels/IDs/construct reports were not rewritten.
- Four regressions cover parsed/standalone loading × task-only/play shapes. A broader parser test exposed an assertion still expecting old global wrapper counts; it now verifies the documented leaf population and preserves play-ID separation coverage.
- **168 focused tests passed** across metrics, naming/parser consumers, findings, provenance/profiles, diffs and construct evidence. Full repository suite: **1,478 passed, 2 skipped** in 197.99 seconds, including all earlier repair tests. No population accuracy claim.

## 2026-10-23 — Step 4b: verify variance and reject unreliable normal intervals

Status: two-stage variance/interval diagnostic complete; normal candidate rejected.

- Added [sampling_uncertainty.py](../../scripts/sampling_uncertainty.py). Includes finite-population corrections at both stages, exact-census handling, unavailable variance for non-census singletons, HT known-N variance and plug-in residual linearization for the global Hájek fraction. No real labels or scoring API.
- **41 focused tests passed**, including exact enumeration of total and unbiased variance over an unequal-size two-stage toy population for three fixed residual constants, census/singletons, invalid binary counts, retained unavailable intervals and point-simulation parity.
- [Both allocations / full results](../../study/sampling-uncertainty-2026-10-23/README.md): six fixed planted populations × 400 draws × two estimators × two allocations; all 9,600 estimator/draw rows retained. Output hashes checked; all 24 estimator/scenario point summaries match the earlier point study.
- Nominal 95% normal intervals **fail**: near-boundary global-Hájek coverage **51% (204/400)** at three groups and **66.25% (265/400)** at five. Heterogeneous high-positive coverage is 80.75% / 86.50%. Increasing groups narrows many intervals and helps some scenarios, but does not make the method reliable.
- All near-boundary misses are on the optimistic side; zero-SE draws explain only 8 of 196 misses at three groups. Mean point bias is small and all variances are estimable in these allocations, so neither fact justifies final confidence statements.
- Normal candidate/final estimator/workload/performance eligibility stays false. Next: boundary-aware or conservative finite-design interval benchmarks, within-group allocation alternatives, then correlated nonresponse/reviewer-error checks. No historical point results or draw ledgers changed.

## 2026-10-23 — Step 4c: conservative finite-design interval and allocation benchmark

Status: design-conditional coverage benchmark verified; width is impractical; final method remains unaccepted.

- Added [finite_population_bounds.py](../../scripts/finite_population_bounds.py): known-size binary within-group bounds, bounded exact vertex DP for between-group totals, declared analytic fallback, both-stage variance envelope and Chebyshev confidence sets for unbiased known-N HT fractions. No normality assumption, real labels or scoring API.
- **54 focused tests passed** across bounds/variance/sampling: exhaustive vertex and binary-population comparisons, exact toy design variance/coverage, census, memory fallback and retained empty sets. Both assumptions and proof are in the [report](../../study/sampling-bounds-2026-10-23/README.md).
- Reused all 4,800 earlier HT draws across both allocations; observed coverage is 100% in every scenario. Width is uninformative: constant-scenario mean **99.51 / 94.41 percentage points** at three/five groups. Untrimmed radii: 73.4924 / 54.9600 pp. This conservative envelope does not establish a minimum possible width for other methods.
- Six rule/certainty/scope cells in size quartile 4 contribute **78.91% / 78.94%** of the bound. Largest-size strata contribute 88.52% / 88.56%; between-group components dominate. This guides alternative-allocation comparisons, not claims about error prevalence or an optimal design.
- Hashes and all interval rows retained; no final estimator/workload/performance eligibility promoted. Next compare both-stage allocation/width, then stronger boundary-aware methods and nonresponse/reviewer error; the final output frame must follow code freeze.

## 2026-10-23 — Step 4d: specify both-stage allocation comparisons

Status: plan fixed; four new development comparisons follow automatically.

- [Configuration matrix and expected workload](../../study/sampling-allocation-2026-10-23/README.md) recorded before the new runs: existing 3×2 / 5×2, plus 3×5 / 5×5 / 10×2 / 10×5. Expected IDs: 850.62 / 1,274.70 / 1,450.28 / 2,256.88 / 2,220.39 / 4,095.36.
- Keep census cutoff 30, same metadata frame/seed/six truth populations and 400 replications. Compare both stages, including similarly priced 5×5 vs. 10×2, rather than changing a category quota or accepting a workload from point bias alone.
- This is adaptive development, not final-design preregistration or an independent evaluation. No labels, reviewer-hours claim, normal-interval acceptance or scoring eligibility are generated.

## 2026-10-23 — Step 9a: bounded frozen-source timeout triage

Status: current context/symbol probe complete; original timeout remains open.

- Added [profile_frozen_context.py](../../scripts/profile_frozen_context.py): immutable Git-blob mirror, fresh Git boundary, separate worker, 75-second deadline, 2 GiB address-space limit, flushed stage events, cProfile and periodic stacks. No target programs/providers/model calls.
- [Retained report](../../study/timeout-context-2026-10-23/README.md): classification recovers all 148 YAML paths / 145 selected files; repository context takes 4.486 seconds and symbol indexing 0.758 seconds. Worker total **6.281 seconds**; current implementation only, not the archived commit.
- 403/417 regular blobs copied. Fourteen oversized genesis JSON files remain explicit omissions; no YAML omitted. This excludes a claim of complete reproduction and may matter for whole-tree provider scanning. Original timeout log has no stage evidence.
- **142 focused tests passed** across probe, immutable retrieval, context and symbol indexing. Generated output/source/dependency hashes checked. Controlled inventory tracked; raw source/logs ignored. Next isolate file detectors and examine provider input sizes before changing deadlines.

## 2026-10-23 — Step 4e: complete both-stage allocation comparison

Status: six configurations compared; more sampling does not repair the normal candidate.

- [Full comparison](../../study/sampling-allocation-2026-10-23/README.md) retains 72 estimator/scenario summaries and 36 conservative-bound summaries, referencing 28,800 estimator/draw and 14,400 bound/draw rows. Four new allocations plus two unchanged baselines; fixed pre-execution matrix, identical frame/seed/truths and 400 replications verified.
- Expected workload rises from **850.62 to 4,095.36 IDs**. Near-boundary global-Hájek normal coverage improves from 51% to **75.75%**, still far below nominal 95%. Point RMSE improves, but 97/400 largest-allocation intervals still miss. No interval/workload/final accuracy gate passes.
- Similar-cost 5×5 vs. 10×2 has mixed point/coverage outcomes. More groups reduce the conservative bound more strongly; even 10×5 has 32.868 pp radius / 65.596 pp constant-scenario mean width. All conservative coverage is 100% on these fixed populations, with assumptions and impractical width retained.
- All source output hashes, plan/configuration inputs, identical truths, complete unique draw identities and derived CSV hashes checked. Existing tested scripts run without code changes. No human/model labels, reviewer-hours estimate or historical data rewrite.
- Next: boundary-aware methods and targeted size-cell allocations, fresh stress populations, correlated nonresponse/reviewer error and human effort/agreement before final design selection.

## 2026-10-23 — Step 9b: isolate current file metric detectors

Status: bounded probe complete; no detector stall reproduced.

- Extended the frozen context probe with explicit optional file-metric execution. [New retained report](../../study/timeout-file-metrics-2026-10-23/README.md): **10.996 seconds total**, 145 file completions, 67 structural analyses / 78 parser skips, zero caught detector exceptions. File stages total 4.191 seconds. CLI fallback/threshold/reporting, module docs and providers remain untested.
- **5 probe tests passed**, including both separate-process modes. Original and derived report hashes checked. Original context-only outputs remain unchanged and identify the earlier code hash.
- Exact-tree size is **470,774,640 bytes**; omitted JSON files dominate. This is a candidate provider-workload mechanism, not historical timeout attribution. Next isolate whole-tree provider and postprocessing against complete immutable source; do not raise old limits or declare the missing repository complete.

## 2026-10-23 — Step 9c: complete-tree provider isolation

Status: first bounded native GitLeaks scan times out; no historical attribution.

- Added [profile_frozen_gitleaks.py](../../scripts/profile_frozen_gitleaks.py): complete verified regular-blob mirror, separate native/filter checkpoints, native deadline plus process-group worker deadline, stacks/profile, controlled counts/hashes only. No source/finding values published.
- [Retained 30-second result](../../study/timeout-gitleaks-2026-10-23/README.md): all **417 blobs / 470,774,640 bytes** present; native provider times out before postprocessing. Returned zero findings means missing provider outcome, not clean source. Binary version string is a build placeholder; executable digest is recorded instead of inventing a version.
- **25 focused tests passed** across both probes and GitLeaks behavior. One further diagnostic is fixed before execution: 120-second native / 150-second worker, identical source/binary/current adapter. Both outcomes retained; study deadlines/population results unchanged.

## 2026-10-23 — Step 9d: repair reproduced GitLeaks postprocessing stall

Status: provider stall repaired and focused full-tree probe completes; full repository verification remains separate.

- Longer baseline native scan completes in **34.587 seconds** with **81,598 findings / 35 files**, then stalls in repeated full-file reads/decodes until the 150-second worker deadline. Stack evidence retained. The baseline adapter is byte-identical to the archived analyzer's adapter, although external environment equivalence and unique historical attribution remain unverified.
- [Mechanism, repair and all artifacts](../../study/timeout-gitleaks-2026-10-23/README.md): per-finding file reads project to **3.377 TB** if completed, not measured physical I/O. Group work by file with an invocation-local one-file cache; preserve native order, suppression predicates/version, and missing/invalid-source behavior.
- Two new read/order/cache regressions fail before and pass after; **27 focused tests passed**. Exact fixed 69-row subset spanning every native file preserves original findings/suppression evidence/order. Complete 81,598-row replay takes 35 source reads, retains 80,058 and suppresses 1,540 under unchanged public-key-context policy; no source/finding values published.
- Repaired complete-tree integrated provider probe: **75.874 seconds total**, native 36.777 / filter 29.706 seconds, same source/binary/limits and reconciled counts. Profile timings are development diagnostics, not a controlled performance benchmark.
- All **81,598 rows** also match the archived filter's policy/evidence by file when its source helper uses the same cached context; this conditional comparison deliberately avoids rerunning the stalled I/O. Global interleaved order is tested separately.
- Full repository suite: **1,520 passed, 2 skipped in 161.09 seconds**. Diff whitespace check passes. Historical run/denominators remain unchanged; ansible-lint, metadata, full CLI fallback/reporting and semantic quality still require separate validation.

## 2026-10-23 — Step 9e: verify complete source-only CLI and reporting

Status: source-only path completes; full-profile/environment/semantic gates remain separate.

- Continued automatically after the tested provider fix. [Retained diagnostic](../../study/timeout-source-cli-2026-10-23/README.md): complete `snapshot-source` CLI against the verified 417-blob mirror finishes in **8.089 seconds**, exit 0, 145 parsed/processed files, zero faults/partial/failed files. Includes fallback source checks, threshold evaluation and report writing beyond the earlier metric-only probe. Providers/history excluded; module docs disabled; no model calls.
- 1,128 raw internal findings / 1,127 canonical occurrences are unvalidated outputs. Preserve 49 static-missing and six dynamic include outcomes; operational completion is not dependency completeness or semantic correctness.
- All 417 source hashes / 470,774,640 bytes reverified after execution; generated output/log hashes recorded. An initial wrong CLI subcommand was rejected before analysis and retained as a launcher error, followed by the corrected direct-target command in a new directory.
- Diagnostic/documentation-only follow-up to the **1,520 passed / 2 skipped** production-fix suite. Next isolate module docs/lint and the combined provider/reporting path; historical timeout and study denominators remain unchanged.

## Next steps

1. Complete typed subject identities, specialized YAML/rule dependencies and source-first recall controls; construct/lexical diagnostics are complete but do not certify evidence. The named-task display-sentinel bug is repaired in V3.
2. Review the claim/exposure/group registry; normal intervals are rejected by the new coverage check. Compare boundary-aware/conservative intervals and within-group allocation, then nonresponse/reviewer error before accepting a final design.
3. Complete the neutral LLM assessment contract, rule-specific context and local acceptance evaluation; transport/validation/head-staged lifetime repairs are complete.
4. Audit the impact of versioned shared task traversal and validate source-unit/threshold definitions with a fresh instrument.
5. Complete combined-profile timeout verification: repeated GitLeaks file I/O is repaired, its provider probe and the complete source-only CLI finish; module docs/lint and combined large-provider reporting remain. Classify the other partial-provider causes.

These remain pending. The full plan records dependencies and the human review needed for final evaluation claims.
