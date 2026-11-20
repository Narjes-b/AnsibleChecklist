# v0.0.7 Variable Resolution Sampling Protocol

## Objective

Evaluate three separate questions:

1. Were findings removed by required role arguments safe to suppress?
2. Are emitted `unguarded-variable` occurrences assigned to the correct
   resolution class, and which are actionable defects?
3. Does a source-first review find supported issues that the detector missed?

This protocol evaluates `ansibleguard/unguarded-variable`, not the precision
or recall of the entire tool.

## Frozen populations

- Candidate run: `v007-variable-resolution-207`.
- Repositories: 207 frozen projects and commits; 206 analyzable.
- Positive population: all internal canonical occurrences whose rule ID is
  `ansibleguard/unguarded-variable`.
- Source-first population: included, parsed, production-Ansible files from the
  frozen classification manifests.
- Sampling seed: `v007-variable-resolution-primary-20260917`.

Population and sample SHA-256 hashes are recorded in `sample-manifest.json`.

## Samples

### Suppression census

Review all 247 baseline occurrences removed without a same-location candidate
replacement. This is a census, not a sample.

### Emitted-positive sample

Select 150 occurrences from each resolution class:

- `CANDIDATE_MISSING`;
- `EXTERNAL_INPUT_UNCERTAIN`;
- `RUNTIME_CONTEXT_UNCERTAIN`.

Within each class, occurrences and repositories receive deterministic SHA-256
ranks. Selection proceeds round-robin by repository. The per-repository cap is
three, except `CANDIDATE_MISSING`, which uses five because its 997 occurrences
span only 49 repositories and a cap of four permits only 149 selections.

The design maximizes repository diversity and prevents the largest projects
from dominating. The recorded `naive_inclusion_probability` is the class-level
sample fraction; it is not an exact probability after repository capping.

### Source-first sample

Select 150 files before matching AnsibleGuard output. The sampler balances ten
artifact classes with 15 files each:

- defaults;
- group variables;
- handlers;
- host variables;
- import-only task fragments;
- inventory;
- metadata;
- playbooks;
- tasks;
- vars.

Files and artifact strata receive deterministic SHA-256 ranks. Selection is
round-robin across artifacts with a two-file cap per repository. Files with
existing findings are not excluded. Detector matching happens only after
source candidates are identified.

## Review evidence

For each emitted occurrence, review:

- source context around the reported line;
- root variable name;
- repository YAML definition sites;
- `register`, `set_fact`, and scoped `vars` definitions;
- applicable role `meta/argument_specs.yml` or `.yaml` contract;
- recorded resolution blockers.

For source-first files, extract Jinja and control-expression roots, remove
guarded and known Ansible-special variables, review definition and contract
evidence, identify supported issues, and only then match detector occurrences.

## Labels

Two axes are kept separate:

- `classification_correct`: `yes`, `no`, `unclear`, or `not-applicable`;
- `defect_label`: `TP`, `FP`, `UNCERTAIN`, or `TN` for source blocks.

Additional fields record root cause, runtime-failure judgment, actionability,
needed evidence, reviewer confidence, definition sites, argument contract,
source context, and rationale.

Required external inputs are safe suppressions when the applicable entry-point
contract has `required: true`. External and dynamic runtime states remain
`UNCERTAIN` unless source evidence proves a stronger conclusion.

## Statistics

Report:

- suppression safety for the 247-item census;
- decided precision and conservative all-sample TP yield for
  `CANDIDATE_MISSING`;
- resolution-class accuracy and decision coverage;
- source-first supported recall at occurrence and repository levels;
- naive Wilson 95% intervals.

Wilson intervals treat occurrences as independent and can understate
repository clustering. Repository-level recall is shown separately. Exact
population weighting is not claimed because repository caps alter the naive
class-level inclusion probability.

## Validity limits

Precision and recall estimates require independent human review and adjudication. Report the decision coverage and account for repository clustering.
