# v0.0.7 Variable Certainty Implementation Report

## Outcome

AnsibleGuard now resolves one additional class of previously uncertain
`unguarded-variable` findings and exposes machine-readable resolution evidence
for every internal rule that currently emits semantically uncertain results.

The implementation is intentionally conservative. It converts a result to a
proof only when the repository contains evidence that guarantees the property.
Dynamic or externally supplied Ansible state remains explicitly unknown rather
than being guessed into a true or false result.

## What became certain

### Required role arguments

Before this change, a variable declared as `required: true` in a role's
`meta/argument_specs.yml` was still reported as an uncertain unguarded
variable. Ansible validates required role arguments before executing the role,
so the role task cannot execute normally with that root variable undefined.

The detector now reads both `argument_specs.yml` and `argument_specs.yaml`,
separates required from optional root arguments, and treats required arguments
as MUST-defined in the directly matching role task entry point. Their
unguarded-variable findings are suppressed there.

Contracts are matched by entry-point name: for example, the `main` argument
spec applies to `tasks/main.yml`, while a `restore` spec applies to
`tasks/restore.yml`. A requirement from one entry point cannot suppress a
finding in another. Imported or nested task files remain uncertain unless the
execution graph independently proves the definition.

Optional declared arguments remain MAY-defined and are reported with the
blocker `declared_optional_role_argument`. Schema `default` metadata is not
treated as a runtime assignment because this implementation does not assume
that validation mutates the role variable environment.

This is relevant to the selected corpus: 314 role argument-specification files
are present across 25 of the 207 frozen repositories. Updated corpus counts
require a new scan; the existing v0.0.7 diagnostic run was generated before
this implementation.

## Resolution model

The existing `semantic_status` field remains unchanged for compatibility. New
additive fields explain what the analyzer established:

- `resolution_status`: the proof or remaining uncertainty class;
- `resolution_scope`: the static scope in which the conclusion was reached;
- `resolution_evidence.proved`: facts established by analysis;
- `resolution_evidence.blockers`: facts preventing a stronger conclusion;
- `uncertainty_sources`: stable machine-readable blocker names.

For `unguarded-variable`, the statuses are:

| Resolution status | Meaning |
|---|---|
| `CANDIDATE_MISSING` | No visible static definition, runtime producer, default, or defined guard was found in the modeled repository scope. This is a medium-confidence candidate, not a human-confirmed defect. |
| `EXTERNAL_INPUT_UNCERTAIN` | The value may be an undeclared role, playbook, or reusable task-fragment input. |
| `RUNTIME_CONTEXT_UNCERTAIN` | A dynamic or conditional runtime source may define the value. |

Findings prevented by a MUST-definition, including required role arguments,
are not emitted. This follows the existing behavior for role defaults, role
vars, unconditional visible definitions, safe defaults, and proven guards.

## Other rules updated

The same evidence contract was added wherever the current detector set emits
`UNCERTAIN`:

| Rule/concept | Statuses | Behavior |
|---|---|---|
| `unguarded-variable` semantic concepts | `CANDIDATE_MISSING`, `EXTERNAL_INPUT_UNCERTAIN`, `RUNTIME_CONTEXT_UNCERTAIN` | Distinguishes absence candidates from external-input and dynamic-runtime blockers. |
| `variable-use-before-definition` | `PROVEN_ORDERED_CONFLICT`, `RUNTIME_CONTEXT_UNCERTAIN` | Separates a proven later definition from cases where dynamic execution may supply an earlier value. |
| `unnecessary-set-fact` | `BOUNDED_GRAPH_UNKNOWN` | States that no use exists in the bounded graph without claiming global deadness. |
| `credential-log-exposure` | `PROVEN_EXPOSED`, `DYNAMIC_PROTECTION_UNKNOWN` | Separates statically exposed values from a dynamic `no_log` expression that cannot be evaluated. |

Credential-log findings now also expose `dynamic_no_log` through
`uncertainty_sources`, rather than only inside a confidence sub-object.

## Evidence propagation

Resolution metadata is preserved through:

1. detector detail records;
2. normalized raw findings;
3. canonical occurrences;
4. canonical findings reconstructed from occurrences;
5. study aggregate CSV output.

The study aggregate now serializes both `uncertainty_sources` and
`resolution_evidence`, and includes `resolution_status` and `resolution_scope`
as explicit columns. Existing field names, rule IDs, concept IDs, and semantic
statuses remain available, so existing consumers are not forced to migrate.

## What remains uncertain and why

Repository-only analysis still cannot prove values supplied by:

- extra variables or CI/CD parameters;
- AWX/Tower surveys and external credentials;
- dynamic inventory plugins;
- dynamic roles, includes, and `vars_files` paths;
- inaccessible or external includes;
- external role dependencies;
- custom modules that create facts;
- conditional producers whose path does not imply the consumer path;
- multiple callers with different variable contracts.

These cases must remain unknown unless a concrete inventory, caller, or runtime
configuration is supplied. Turning them into certain findings without that
evidence would increase false positives rather than improve the detector.

## Compatibility and safety

- The stable detector ID remains `ansibleguard/unguarded-variable`.
- Existing semantic concepts remain `missing-internal-variable`,
  `undeclared-input-contract`, and `unresolved-runtime-input`.
- Existing `semantic_status` values are unchanged.
- All new output fields are additive.
- Optional role inputs are not suppressed.
- Role argument contracts are restricted to their matching direct task entry
  point.
- Dynamic and external sources are never promoted to proofs.
- No historical scan artifacts were modified.

## Verification

- Focused detector/report/pipeline tests: 253 passed.
- Complete test suite: 1,011 passed, 2 skipped.
- Regression coverage verifies:
  - required role arguments suppress the former uncertain finding;
  - optional role arguments remain uncertain;
  - contracts from other entry points and imported subtasks do not suppress
    findings;
  - resolution metadata survives finding and occurrence normalization;
  - use-before-definition records dynamic blockers;
  - unused `set_fact` records its bounded-graph limitation;
  - dynamic `no_log` remains unknown while static exposure is proven.

## Follow-up status

The 207-repository corpus rescan and strict baseline comparison are complete.
See `docs/study/v007-variable-resolution-results.md` for the execution outcome,
count deltas, resolution-class totals, timeout caveat, and manual spot checks.

The frozen primary agent review now covers all 247 suppressed findings, 450
emitted occurrences (150 per resolution class), and 150 source-first files.
It is explicitly marked as agent review rather than independent human ground
truth; independent second-reviewer labels remain needed for agreement
statistics.

The remaining validation work is independent second-reviewer labeling,
adjudication, and a genuinely unseen repository sample for final
generalization claims.
