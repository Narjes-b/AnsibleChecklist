# ICPC readiness and local LLM plan — 2026-10-31

Status: evidence-backed planning review, not a completed evaluation. Assumption: ICPC means the IEEE/ACM International Conference on Program Comprehension, targeting the upcoming 2027 edition. No inference, model download, benchmark, human labeling or submission occurred in this review. The existing local-only requirement remains in force.

## 1. Recommendation and venue timing

The strongest direction to investigate is **helping developers understand Ansible findings through scope-aware evidence and local explanations**. A working analyzer and many output counts provide an engineering foundation; they do not establish explanation quality, human comprehension benefit or scientific novelty. Proposed contribution and title remain hypotheses until the related-work and evaluation checks below are complete.

Official dates checked on 2026-10-31:

| ICPC 2027 track | Deadline / format | Assessment for this project |
|---|---|---|
| Research | Abstract October 29; paper November 5, AoE; 10 main-text pages + 2 reference pages | Abstract deadline has passed. If already registered, assess whether a tightly bounded defensible study exists. Otherwise verify eligibility with the chairs before relying on this route; no exception is assumed. Current evidence does not support a broad validated-LLM claim. |
| Tool Demonstration | November 19; 4+1 pages | Candidate for a working evidence-navigation/explanation workflow with demonstrated maturity. Source/binary availability is required; a 3–5 minute video is encouraged, optional. |
| Early Research Achievements | Optional abstract November 19; paper November 26; 4+1 pages | Candidate for a focused new idea with preliminary results. Explicitly distinguish it from its closest related paper. A small honest study is preferable to unsupported mature-system claims. |

Sources: [official important dates](https://conf.researchr.org/dates/icpc-2027), [research call](https://conf.researchr.org/track/icpc-2027/icpc-2027-research-track), [Tool Demonstration call](https://conf.researchr.org/track/icpc-2027/icpc-2027-tool-demonstration), [ERA call](https://conf.researchr.org/track/icpc-2027/icpc-2027-early-research-achievements--era-). Dates/formats can change; recheck before submission. Research review is double-anonymous; Tool Demonstration explicitly is not. Follow the chosen track's template, AI-use disclosure and human-participant requirements. These are venue requirements; the study recommendations below are our assessment, not mandated experimental designs.

**Recommendation:** prioritize ERA if the new evidence method is central, or Tool Demonstration if the implemented workflow is central. Choose one primary story and resolve its novelty before committing. Neither route guarantees acceptance or bypasses sound evidence. A broad research paper combining all rules, prevalence, causal impact, an LLM method and a user study is not a realistic five-day completion plan on the current evidence.

## 2. What is established, and what is missing

| Area | Evidence currently available | Gap before the corresponding paper claim |
|---|---|---|
| Engineering | Last recorded full suite: 1,520 passed / 2 skipped; immutable retrieval, contract checks, metric V3 and GitLeaks I/O repair | Tests do not establish detector precision, LLM reasoning quality or comprehension benefit. This review did not rerun the suite. |
| Corpus execution | Archived 207 repositories: 206 core-complete; 171 all-provider-complete / 35 partial / 1 failed | Preserve provider-specific denominators. Focused repaired probes do not replace the historical failed repository or certify the full combined run. Freeze and rerun the claimed version. |
| Labeling | Calibration material, owner-attested human A/B pilot provenance, separate AI exploratory passes | 119/350 pilot semantic disagreements remain pending in the reviewed recovery report. Adjudicate for calibration; this pilot stays ineligible for population scoring. Preserve producer identity by dataset. |
| Evaluation independence | Existing splits and sample histories | 55/62 old heldout repositories have examples in exploratory labeled samples. Exposure is not proof every item influenced tuning, but an untouched evaluation cannot be assumed. Use a documented new independent set or narrow the claim to development evidence. |
| Evidence packets | All 2,331 selected IDs across alternative panels retain source/metadata; candidate constructs and lexical outcomes audited | Alternatives overlap. Typed unit identity, scope, applicability and rule-dependent completeness are not certified. Required panel: 661 construct candidates, 185 file-only, 8 aliases, 7 duplicate-key cases; lexical matches alone are not semantic grounding. |
| LLM | Local transport, schema 3 / prompt `local-review-v3.1`, checked citation locations/backend quotes, no-fix abstention rules | Current semantic accuracy remains unvalidated. The most recent live V3 missing-runtime-input answer was wrong; V3.1 rejected its declared contradiction only in replay. No new live V3.1 acceptance result is established. |
| Estimation | Exact two-stage weights, variance checks, six allocation comparisons | Normal intervals are rejected: even about 4,095 expected reviews yield only 75.75% near-boundary coverage for a nominal 95% global-Hájek interval. Conservative bounds remain too wide. Final interval/design/workload is unaccepted. |
| Recall / useful findings | Detector occurrences and overlap diagnostics | Need source-first audits including zero-output units, rule eligibility and matching subjects. Extra output or disagreement with ansible-lint is not automatically added defect coverage. |
| Thresholds | Versioned metrics, repeated 75-item threshold calibration | Repeated items are development exposures; the last recorded agreement 0.754 misses the existing 0.80 gate. Need fresh calibration and validated units/thresholds, or exclude those rules from final claims. |
| Comprehension | A working explanation/reporting interface | No established human study showing more correct understanding, safer decisions or reduced effort. A participant study is needed if claiming those effects; a tooling paper can instead make a narrower demonstrable capability claim. |
| RQ2 | Descriptive output co-occurrence tables | Repository dependence, file-kind applicability, shared predicates, size sensitivity and multiple-testing choices need review. Associations are not causal impacts or validated defect associations. |
| Paper narrative | An old RQ1/RQ2 draft and extensive technical documentation | Rewrite around one contribution and a claim/evidence ledger. Old precision tables and superseded provenance descriptions must not become current results. |

Evidence: [repair log](recovery-progress.md), [recovery diagnosis](recovery-plan-2026-10-23.md), [RQ1 recovery status](../../study/rq1-agreement-pilot/recovery-2026-10-23/RQ1_RESULTS.md), [scoped owner provenance](../../study/exploratory-labels/PROVENANCE.md), [construct audit](../../study/evidence-constructs-2026-10-23/README.md), [allocation comparison](../../study/sampling-allocation-2026-10-23/README.md), [local LLM repair record](local-llm-repair-2026-10-23.md). These are inspected records, not newly generated semantic judgments.

## 3. LLM improvement: evidence first, then controlled model selection

Current production limitations verified in `src/ansibleguard/report/llm_explain.py`:

- Primary source uses ±6 lines. This can omit the actual task, inheritance, a guard, a paired duplicate or an include.
- Cross-file variable context uses repository-wide `possible_definitions_of(name)` and stops after three candidates. The prompt asks the model to determine scope. Candidate absence/truncation and graph failure are not a complete account of missing evidence.
- Definition anchoring searches forward for a `name:` substring rather than using a verified exact identifier node. Names/types and enclosing task ordinals need reliable source identities before binding graph evidence.
- A valid citation proves supplied text/location membership, not relevance, correct binding or entailment.
- Production enrichment has per-item timeouts and an item cap; whole-operation budgeting, resumable incremental persistence and actual token-fit checks remain incomplete. The engineering acceptance harness's budget is not a production-wide guarantee.

Target pipeline:

```text
frozen occurrence + rule contract
  -> typed source-unit identity and exact identifier span
  -> rule-specific dependency retrieval
  -> structured evidence packet, ambiguity and missingness
  -> deterministic applicability/predicate checks where justified
  -> bounded local explanation/assessment
  -> citation + consistency + proposed-edit validation
  -> human-visible evidence, limitations and optional suggestion
```

### A. Define evidence by rule and decision partition

Start with a small set of mature rules, approximately 4–6 after predicate/codebook review, rather than promising all rules. Include a local explicit-setting condition and a cross-file/runtime-input condition. Expand to handlers/security/thresholds only when their evidence is ready.

| Evidence partition | Retrieve / establish | Explicit failure state |
|---|---|---|
| Local explicit setting | Full task, action/module, exact field/value/type, relevant inherited setting, rule predicate/version | Wrong unit/type or decisive redaction => insufficient evidence |
| Variable/runtime input | Exact case-sensitive reference, role/include path, order, guards, candidate definitions and must/may/unknown visibility, input contracts/inventory availability | Unresolved external input is not proof of undefinedness; an unrelated same-name default is not proof of safety |
| Handler/register | Referenced name, `listen` aliases, notification/use sites, scope, imported definitions and order | Missing or conditional edges remain visible; do not infer reachability from proximity |
| Security/logging | Relevant module argument metadata, effective no-log inheritance/overrides, value provenance and audited non-secret facts | A hidden decisive value cannot support a forced verdict |
| Size/duplication/policy | Whole typed source unit, metric definition/version, both duplicate units where relevant, explicit project-policy applicability | Parser ranges or normalized LOC alone do not validate maintainability thresholds |

Emit a versioned packet containing source SHA/blob hashes, unit ID, rule/predicate version, exact spans, supplied evidence IDs, dependency edges, scope/ordering facts, truncation/redaction, unavailable dependencies and retrieval status. Keep **source integrity, anchor correctness, subject identity, applicability and decision completeness as separate fields**. Certify only the subset that a reviewed rule contract supports; general Ansible runtime completeness is not assumed.

Preserve selection identity and both-stage probabilities across every packet revision. Keep alias/duplicate-key/parse/oversize/unknown cases in their original cells; do not replace them with easy cases. Rank definitions by verified relation to the use, and explicitly report omitted candidates instead of treating the first three as complete evidence. Semantic/vector search, if later useful, is an adjunct to scope-aware retrieval rather than a substitute for it.

### B. Keep condition, uncertainty and advice separate

Retain `supported` / `unsupported` / `insufficient-evidence`, plus separate actionability. A deterministic rule check may establish a narrowly documented literal predicate; it does not prove a deployment failure. Missing required evidence must block a decisive answer. Evidence location checking must not be presented as semantic verification.

Do not auto-dismiss findings or apply edits from the LLM. Keep fixes optional and limited to supported, actionable conditions with adequate context. Validate suggested YAML structure and the documented condition afterward in a safe local check; syntactic validity is not proof of behavioral preservation. Record harmful/wrong fixes and overconfident false confirmations/dismissals. Confidence labels remain model self-reports until independently calibrated.

### C. Compare local models on the same evidence

Read-only inventory on 2026-10-31:

| Component | Observed value |
|---|---|
| GPU | NVIDIA GeForce RTX 3050 6GB Laptop GPU, 6,144 MiB |
| Local server | Ollama 0.31.1 |
| Installed baseline | `qwen2.5-coder:7b`, Q4_K_M, digest `dae161e27b0e90dd1856c8bb3209201fd6736d8eb66298e75ed87571486f4364` |
| Installed comparison candidate | `qwen3:8b`, Q4_K_M, digest `500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41` |

No request generated text. Two installed models allow a comparison without downloading anything. This does not imply the larger candidate is better or fits entirely in VRAM. Measure CPU/GPU offload, actual prompt/generation tokens, context fit, latency and peak memory on this 6 GiB device. The existing 8,192-token setting and a 64 KiB byte limit are not a token-fit guarantee.

First use development cases for compatibility and error diagnosis, preserving every attempt. Pin prompts, schemas, evidence-builder hashes, model digests, quantization, server/options and any candidate-specific reasoning settings. Keep the context/prompt budget comparable and report model-specific limits. Tune only on development data; choose the model before opening sealed evaluation labels. Do not fine-tune on old exploratory labels and then claim independent improvement on the same repositories.

### D. Add operational controls

Add a whole-run deadline, bounded per-call budget, token-aware packet assembly, cancellation, per-item atomic persistence, resume by exact source/model/prompt/packet identity, and explicit timeout/invalid/insufficient states. Record failed attempts rather than retrying until a favorable answer appears. Keep everything local; no hosted fallback.

## 4. Proposed research questions and comparisons

These are proposed experiments, not existing results.

| Question | Comparison | Required measurement |
|---|---|---|
| RQ1: Does scope-aware evidence improve condition assessment and explanation support? | Same local model: fixed window, full unit, same-budget generic repository retrieval, rule/scope-aware packet | Correct decisions, false confirmation/dismissal, sufficient-context abstention, evidence relevance/entailment and packet defect rate |
| RQ2: Where does the method help or fail? | Decision/evidence partitions and important failure mechanisms | Per-partition coverage/quality, unreviewable/missing cases, useful evidence retrieved, truncation/redaction and runtime cost |
| RQ3: Does it help developers understand and judge findings? | Existing analyzer + normal source browsing; grounded evidence without LLM; same evidence plus local LLM | Correct answers/decisions, effort/time, unjustified trust, harmful decisions and usability |

The generic retrieval comparator should receive a comparable token/retrieval budget. Add an ablation of completeness/abstention handling if making that a core contribution. A different model with the same context separates model choice from retrieval changes. A static evidence-only baseline tests whether the LLM adds value beyond better navigation. Fine-tuning and multi-model voting are later options, not prerequisites or independent judges of truth.

The minimum credible story for a short submission is narrower: one important comprehension problem, implemented evidence method, demonstrated before/after mechanism, and a transparent preliminary evaluation. A full user-benefit or population-quality claim needs the corresponding evidence above.

## 5. Labeling, sampling and statistical plan

Maintain separate instruments:

1. **Development challenge set:** manually curated mechanisms spanning supported/contradicted/insufficient conditions, cross-role same-name traps, dynamic inputs, guards, aliases, duplicate mappings, policy dependence and redaction. Useful for debugging; no natural-population accuracy claim.
2. **Independent explanation evaluation:** frozen eligible repositories/role groups, rule contracts and packets; two independent human judgments with disagreements adjudicated. Separate condition, evidence support, actionability and context sufficiency. Model output never supplies gold labels.
3. **Detector precision panel:** probability draw of eligible detector occurrences, with original two-stage probabilities and missingness. Explanation correctness is a separate estimand.
4. **Source-first recall panel:** blind review of eligible source, including zero-output units, then match supported human-found conditions to tool outputs. Do not infer recall from provider overlap.
5. **Comprehension experiment:** participants and tasks selected for the claimed developer population. Prevent the same participant from learning the same task across conditions; use counterbalanced distinct matched tasks, record experience, training, allotted budget and all assigned outcomes.

Within relevant instruments, stratify by **rule × policy × certainty/resolution × evidence scope × repository/role group × size**, with file kind and difficult YAML mechanisms accounted for. Avoid a full Cartesian design with one item per cell: choose primary strata, ensure feasible coverage, and treat smaller domains as diagnostics. Separate occurrence-weighted, repository-balanced and macro-rule estimands; balancing challenge cases does not estimate natural prevalence.

Before collecting final labels: freeze the primary outcome, practical effect of interest, sample-size rationale, exclusions, missingness, stopping rules and analysis. Choose sample size using pilot variance/cluster behavior and reviewer effort, not a convenient round quota. Validate proposed intervals in simulation; do not reuse the rejected normal interval or assume a generic repository bootstrap works. Include correlated nonresponse, reviewer error, rare negatives and duplicate-role sensitivity. Report all originally selected cases, not only decisive answers.

For LLM evaluation, report a three-way decision matrix, decisive-answer error versus coverage, false confirmation on negatives, false dismissal on positives, unjustified abstention on sufficient cases, behavior on truly insufficient cases, citation provenance separately from semantic support, harmful edits, format/time failures, p50/p95 latency, tokens and memory. An all-abstaining system must not look successful. Predeclare whether fixes are evaluated at all; explanation-only is a legitimate first scope.

For a human comprehension claim, analyze correctness and time jointly and account for participant/task/repository dependence. Do not count fast wrong answers or dropped timeouts as improved comprehension. Satisfaction is supplementary. Resolve institutional review/consent requirements before recruitment; no participants were recruited here.

## 6. Related-work worklist and novelty gate

This is a starting list, not a systematic literature review or a claim that our idea is new.

| Primary source | What the checked source establishes | What we must distinguish |
|---|---|---|
| [Bessghaier et al., SANER 2024](https://pure.etsmtl.ca/en/publications/on-the-prevalence-co-occurrence-and-impact-of-infrastructure-as-c/) | Existing Puppet IaC smell prevalence/co-occurrence/impact study | Reusing its study shape or changing IaC language is not by itself a comprehension-method contribution. |
| [Opdebeeck, Ansible static-analysis thesis](https://ropdeb.ee/files/ropdebee-phdthesis.pdf) | Existing substantial Ansible analysis research; identified from the primary author source, full comparison still pending | Read the relevant analyses and associated papers before claiming a new scope/variable/role model. |
| [Chapman et al., SOAP 2024](https://web.cs.ucdavis.edu/~rubio/includes/soap24.pdf) | Interleaves static-analysis facts and LLM queries for C error-specification inference | Hybrid static analysis + prompting already exists; articulate Ansible-specific evidence semantics and comprehension objectives. |
| [Zhang et al., 2026 actionable-warning study](https://journal.hep.com.cn/fcs/EN/10.1007/s11704-026-60299-1) | Evaluates models/prompts for static-warning actionability and discusses context extraction | A prompt/model comparison alone needs positioning against existing warning-triage work. |
| [Evident preprint, v2 October 2026](https://arxiv.org/abs/2606.15122v2) | Uses LLMs to assemble targeted analysis context, with analyzer validation before warning dismissal | Evidence assembly and keeping the model away from final dismissal are also prior directions. Inspect differences and cite as a preprint; no acceptance status is assumed. |

Build a matrix: task, Ansible semantics, unit/graph, deterministic guarantees, LLM role, local-resource constraints, abstention, evaluation population, human comprehension evidence and artifacts. Select the closest paper only after full-text comparison. The candidate novelty is a **specific, evaluated Ansible evidence/comprehension method**, not “we added an LLM,” rule count, local inference alone or a citation checker.

## 7. Delivery order and acceptance evidence

| Order | Concrete deliverable | Completion evidence |
|---|---|---|
| 1 | Choose primary track, contribution, narrow rule scope and claim ledger | Every intended sentence about effectiveness maps to an instrument and current/pending evidence; registration feasibility established |
| 2 | Rule contracts and typed scope-aware packets on development cases | Source/unit/subject identity checked; dependencies/unknowns explicit; aliases/redaction/truncation retained; fresh independent packet QA meets the existing ≤5% defect gate |
| 3 | Runtime controls and compatibility diagnostic for both installed models | Every attempted item persisted; limits and model identities recorded; no speculative fix/decisive incomplete answer promoted |
| 4 | Frozen development comparison and evidence ablations | Same cases/budgets across configurations; failures retained; model/prompt choice made without final evaluation labels |
| 5 | Fresh human pilot, then independent sealed evaluation | Codebook agreement gates met or scope narrowed; independent labels, adjudication, provenance and exposure ledger complete |
| 6 | Chosen paper's validated result tables / demonstration | Analysis respects weights, dependence and missingness; capability vs effectiveness claims separated; demo reproduces ordinary, contradicted and insufficient cases |
| 7 | Paper and artifact package | Pinned release/environment, source licenses and redaction, reproducible commands, machine-readable provenance/limits, appropriate anonymization, AI-use disclosure and track checks |

Engineering work and human review time must be planned separately. Reviewer availability and pilot results currently prevent a defensible calendar promise. First time a small calibration run on the actual hardware; estimate total calls as `cases × configurations × repetitions`, rather than launching all 861/1,266 selected items. Reserve time for independent review before any submission date.

## 8. Claims to use and avoid

- Established: the tool has substantial tested engineering; exact-source retrieval and provenance repairs exist; observed development failures motivate a better evidence method.
- Proposed: scope-aware packets may improve judgments and comprehension; test these hypotheses rather than state them as findings.
- Not established: current model accuracy, superiority of `qwen3:8b`, population precision/recall, developer time savings, reduced defects, causal co-occurrence impact, complete semantic grounding, or an untouched old heldout population.
- Do not turn the historical 59.2/71.2/75.2% exploratory draft numbers into human-validated final accuracy. Adjudicating the old pilot does not change its scoring exclusion.
- Do not describe `CONFIRMED` as human confirmation, source citation membership as proof, absence of output as cleanliness, or a successful focused provider probe as a complete repaired population run.

Next engineering milestone: a small, independently checked set of typed source/evidence packets for the chosen rules, followed by an auditable local-only comparison. Next paper milestone: a contribution/related-work/claim matrix and a track-appropriate outline. No detector/model behavior or historical labels/results were modified in this review.
