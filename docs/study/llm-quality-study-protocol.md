# LLM quality and comprehension evaluation — protocol v1

This study does not edit manuscripts. It evaluates a frozen candidate, not a
promise that explanations are correct, edits are safe, or developers benefit.
All human forms start blank. Engineering expectations and automated predicates
are never human gold. Raw prompts, source, responses, assignments, blinding keys,
and participant data remain private until reviewed for publication.

## Candidate and case study

Use the installed local `qwen2.5-coder:7b`, temperature 0.1, context 8192, output
limit 1024, per-request timeout 120 seconds, and four-hour per-panel scheduling
budget. Freeze all analyzer Python sources, thresholds, harnesses, protocol,
settings, source-review packets, participant schedules, and model digest. Record
the Python environment separately. No model downloads or hosted calls occur.
Budget is scheduling/transport based, not a hard process cancellation guarantee.

The explanation panel is the original 48 cases: 24 controlled mechanisms and
24 real-source examples from five previously exposed calibration repositories.
Preserve the original manifest and raw-source/Git identities. This is a
convenience/challenge study, not an untouched repository test or probability
sample. Balance window-first/scoped-first execution, one request per condition,
96 scheduled outcomes. Compare **whole pipelines**, including schema/backend
constraints, not retrieval alone or independent model reasoning.

Source review can proceed while outputs are generated, but reviewers must finish
independent source review before seeing any output. Two reviewers judge condition
supported/unsupported/insufficient-evidence, evidence sufficiency yes/no, and
actionability actionable/not-actionable/context-dependent/not-assessed. The
`notes` field must justify the decision and identify relevant lines or missing
context. `acceptable_change` states the allowable behavior change (or none).
Adjudicate separately without overwriting either form. Reviewers must judge the
documented predicate, not whether a tool warning necessarily implies a runtime
failure. Treat developer intent as unavailable unless supplied explicitly.

Output packets contain exact supplied input plus delivered output, and are
shuffled under opaque identifiers. A facilitator keeps the case/condition key;
give each reviewer only their own blank form and packets. Pipeline metadata in
the supplied input may reveal condition indirectly: blinding is partial, not
guaranteed. Gold source labels remain withheld during independent output review.

For each output, grade these fields yes/no/not-assessable:

- `factually_correct`: all substantive summary/reasoning statements are correct
  given the frozen source and documented Ansible semantics.
- `evidence_supported`: substantive claims follow from evidence actually supplied
  to the model. Other repository knowledge cannot repair an unsupported claim.
- `contradiction`: any output contradicts source, its own structured state, or
  another substantive statement. A correct assessment cannot rescue wrong prose.
- `assessment_correct`: structured condition agrees with independently adjudicated
  source judgment.
- `uncertainty_appropriate`: avoids unjustified certainty and unjustified
  abstention; necessary unknowns remain explicit.

`fix_judgment` is correct/wrong-or-harmful/indeterminate/not-proposed. A returned
snippet absent from a failed or withheld output is not a delivered suggestion.
Inspect raw proposal counts separately. `notes` must support all judgments.
For unavailable output use not-assessable on the five quality fields and
not-proposed for fixes; failures stay unsuccessful in the primary denominator.
Adjudicate every row separately and preserve both reviewers' original judgments.

Primary success requires an available output, factual correctness, evidence
support, correct assessment, appropriate uncertainty, and no contradiction.
The denominator is **all scheduled cases**. Report paired success counts and
percentage-point differences; separate real/controlled results, decision errors,
false confirmation/dismissal, sufficient-context abstention, execution failures,
constrained states, proposal/withholding counts, token counts, and latency.
Report pre-adjudication agreement. No population confidence interval is claimed.
Retain all failed attempts; an interruption with unknown outcome becomes an
explicit unsuccessful scheduled outcome rather than a hidden favorable retry.

## Semantic repairs

The 12-case panel has six TLS and six credential-logging cases: four distinct
eligible leaf-task structures, one already-correct task, and one unknown-runtime
case per family. Review source and intended behavior **before repair inference**.
Independent reviewer approval is required, not engineering expectations alone.
Run the frozen scoped model once per case without forcing edits or favorable
retries. Human-approved intent and rubric files are hashed into an execution
record; subsequent changes require a separately identified analysis.

Only delivered TLS false-to-true or added no_log true edits can reach behavioral
execution. A separate validator rejects other modules, keys, destinations,
templates, and edit boundaries. It executes no arbitrary proposed playbooks.
The existing YAML/task/detector/lint validation remains a distinct mechanical
result; it is not evidence of semantic equivalence.

Docker uses a pinned local image ID, no external network, no privileges, no host
checkout or Docker socket mount, an unprivileged user, read-only root, resource
limits, and disposable writable temporary storage. TLS probes serve a synthetic
artifact over loopback HTTPS: before accepts an untrusted certificate, after
rejects it, and after succeeds with the fixture CA and identical artifact.
Logging probes compare synthetic secret visibility in normal and forced-failure
output and assert that the registered task result remains usable. Harness-only
CA injection, destination rebinding, and result instrumentation are explicit;
these test bounded scenarios, not arbitrary production deployments.
Supply the synthetic secret through a separate runtime-vars file, not inline
beside a task where error source excerpts can expose the literal independently
of no_log result censoring. Preserve initial harness failures and their diagnosis.

First execute authored reference controls to validate the harness. Mark their
producer as reference-control, never model. Preserve container errors, output,
image ID, and worker hash. Human reviewers judge intent preservation, correctness,
and harm independently; unresolved deployment assumptions are indeterminate.
Report attempted cases, proposal coverage, mechanical validity, behavioral checks,
human semantic correctness and harm as separate denominators. No proposals means
no measured fix quality. Never equate lack of proposals with safe repairs.

## Developer study

Recruit 18 adult developers with Ansible authoring/review experience; minimum
12 complete sessions for the exploratory study, otherwise feasibility-only.
Gold reviewers are excluded from participation. Before recruitment opens, the
owner records the institution's applicable review determination and fixed closing
date in recruitment.json, finalizes consent/contact/retention details, and
confirms participant eligibility. No messages or invitations are sent by tooling.
Stop at 18 or the closing date, never based on favorable results. Preserve partial
sessions and withdrawals separately; do not silently count them as completions.

Each session: consent, experience and practice (about 10 minutes); 12 tasks at
150 seconds each (at most 30 minutes); debrief (about 5 minutes). The facilitator
uses an unrelated practice example and explains condition/evidence/action, not
the study's answers. External assistants are prohibited. Participants can stop
without penalty. Do not require names, employers, or confidential source.

Three conditions: ordinary finding and all supplied source files; the same source
plus scoped evidence; identical evidence plus the frozen delivered LLM output.
Both evidence conditions also show the same bounded backend evidence contract,
so deterministic condition checks are not exclusive to the LLM condition.
The UI is otherwise identical. No model is queried during a session. Failures
are displayed honestly. Cases comprise three mechanisms per family across TLS,
logging, permissions, and variables: 12 tasks, separate from the evaluation IDs
but related to development mechanisms. This limits generalization.

Each participant receives four tasks per condition, one per family, without
repeating a task. Six condition permutations are assigned in round-robin order;
three matched task variants rotate between blocks in subsequent groups of six.
The facilitator allocates sequential pseudonymous IDs; do not select a favorable
schedule. Each task appears in every condition over each group of six sessions.

Two reviewers finalize a per-task condition/evidence/action rubric before
comprehension inference or participant sessions. Score each dimension 0/1
(total 0–3), with explicit criteria in the three source-adjudication rubric
fields. Then two graders independently score shuffled response packets without
participant ID, condition, time or confidence; adjudicate separately. Empty tasks
score zero. Partial timeout answers may earn justified rubric credit. Record
harmful decisions yes/no with reasons. Confidence and experience are descriptive.

Primary contrast: LLM-plus-evidence versus evidence alone on correctness (0–3).
Report time and correctness together, timeouts, harmful decisions and incomplete
sessions. Display participant-level paired contrasts and task-level contrasts;
do not treat 12 tasks from one participant as 12 independent participants.
Use descriptive distributions/ranges rather than an underpowered independent-task
significance test or a claimed population benefit. Comparisons with ordinary
findings are secondary. The 12–18 recruitment target is a feasibility choice,
not a power calculation. An inconclusive or negative result remains valid.

Offline HTML collects a pseudonymous ID, consent timestamp/version, experience,
answers, monotonic elapsed time, confidence and timeout. It makes no network
requests. Participants download JSON and return it privately. Browser timing is
not tamper-proof; facilitators log deviations. Reloading loses unsaved responses;
preserve partials via facilitator records and never secretly rerun tasks.

## Completion gates

Automated capability: checked protocol/harness, frozen candidate, retained model
attempts, reference behavior controls, blank review packets and participant
materials. Scientific completion: independently adjudicated explanation and fix
reviews, approved recruitment/consent, actual developer responses, blinded grading,
and final analyses. Tooling refuses to turn blank forms into quality results.
Do not state these studies are completed before their human gates pass.
