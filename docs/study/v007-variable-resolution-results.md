# v0.0.7 Variable Resolution Corpus Results

> **Caveat on precision figures in this document**: the precision numbers
> below (e.g. "84/84 = 100%") come from a single-AI-agent labeling pass and
> are calibration evidence only, not independent human gold-standard
> labels — see the "Labeling caveat" section near the end of this document
> before citing these figures as validated precision.

## Outcome

The post-implementation scan confirms that required role argument contracts
remove false-positive `unguarded-variable` occurrences without changing the
frozen corpus, selected files, profile, or external-provider scope.

Across the 206 analyzable repositories, the change suppressed **247**
`ansibleguard/unguarded-variable` occurrences. The total canonical occurrence
count fell from 376,271 to 376,024. Ansible-lint and GitLeaks totals were
unchanged.

## Reproducible runs

| Property | Baseline | Candidate |
|---|---:|---:|
| Run ID | `v007-207` | `v007-variable-resolution-207` |
| Frozen repositories | 207 | 207 |
| Analyzable repositories | 206 | 206 |
| Failed repositories | 1 | 1 |
| Canonical occurrences | 376,271 | 376,024 |
| Internal occurrences | 266,080 | 265,833 |
| Uncertain occurrences | 54,443 | 54,196 |
| Ansible-lint occurrences | 108,757 | 108,757 |
| GitLeaks occurrences | 1,434 | 1,434 |

The built-in comparison accepted the runs as comparable after checking their
repository projects, commit SHAs, classification-manifest hashes, profile, and
ansible-lint scope.

One repository, `encapsulate-xyz/cosmos-ansible`, timed out in both runs. The
baseline allowed 1,800 seconds and the candidate allowed 3,600 seconds. The
candidate therefore reproduces the baseline's single-repository failure even
with twice the execution allowance. Aggregation and reporting cover the same
206 analyzable repositories. The validation status remains `failed` solely
because a complete 207-of-207 run is a hard gate.

## Occurrence comparison

The raw comparison reports:

| Status | Occurrences |
|---|---:|
| Fixed | 568 |
| Introduced | 321 |
| Moved | 6 |
| Unchanged | 375,697 |

For `unguarded-variable`, 567 occurrences are labeled fixed and 320 introduced.
All 320 introduced occurrences have a fixed occurrence at the same repository,
file, and line. They are existing findings reclassified from
`unresolved-runtime-input` to `undeclared-input-contract`, not newly emitted
findings. Removing these one-for-one reclassifications leaves **247 actually
suppressed occurrences**.

The remaining non-detector pair is one ansible-lint `warning[outdated-tag]`
occurrence fixed and one introduced. External-provider totals are identical,
so it does not affect the internal detector result.

## Suppressed required-argument findings

| Repository | Suppressed occurrences |
|---|---:|
| Linuxfabrik/lfops | 121 |
| redhatci/ansible-collection-redhatci-ocp | 44 |
| dell/dellemc-openmanage-ansible-modules | 33 |
| Alfresco/alfresco-ansible-deployment | 32 |
| JenswBE/setup | 10 |
| ansible-collections/ibm_zos_core | 6 |
| ansible-collections/azure | 1 |
| **Total** | **247** |

The semantic concept totals explain both effects:

| Concept | Baseline | Candidate | Change |
|---|---:|---:|---:|
| `missing-internal-variable` | 997 | 997 | 0 |
| `undeclared-input-contract` | 34,006 | 34,326 | +320 |
| `unresolved-runtime-input` | 17,718 | 17,151 | -567 |

The net change is -247, while 320 surviving occurrences receive a more precise
external-input classification.

## Candidate resolution classes

| Resolution status | Findings | Share |
|---|---:|---:|
| `DETECTOR_RESULT` | 314,402 | 83.61% |
| `EXTERNAL_INPUT_UNCERTAIN` | 34,326 | 9.13% |
| `RUNTIME_CONTEXT_UNCERTAIN` | 17,161 | 4.56% |
| `PROVEN_EXPOSED` | 6,251 | 1.66% |
| `BOUNDED_GRAPH_UNKNOWN` | 2,106 | 0.56% |
| `CANDIDATE_MISSING` | 997 | 0.27% |
| `DYNAMIC_PROTECTION_UNKNOWN` | 603 | 0.16% |
| `PROVEN_ORDERED_CONFLICT` | 178 | 0.05% |

The most common explicit uncertainty source is
`possible_required_role_input` (26,185 occurrences). Optional role arguments
remain visible rather than being incorrectly treated as guaranteed inputs.

## Manual spot checks

- In Alfresco's `java` role, `java_keystore` is explicitly `required: true` in
  `meta/argument_specs.yml`. Its former findings in `tasks/keystores.yml` are
  among the suppressed occurrences.
- In Dell's `idrac_attributes` role, `hostname` is required while `username`
  and `password` are declared without `required: true`. The candidate correctly
  retains the latter findings with the
  `declared_optional_role_argument` blocker.
- Candidate-missing examples, such as `__sudo_installed` in Nextcloud's backup
  role, remain emitted because no visible definition, runtime producer,
  default, or guard was established.

These checks support the intended conservative boundary: required direct-entry
role inputs are suppressed, while optional, externally supplied, and genuinely
unresolved inputs remain explicit.

## Primary agent-labeled review

The frozen primary review is stored under
`study/validation-v007-variable-resolution/`. It contains 847 primary units:

| Sample | Size | Outcome |
|---|---:|---|
| Removed required-argument census | 247 | 247 verified-safe suppressions |
| `CANDIDATE_MISSING` occurrences | 150 | 84 TP, 66 uncertain, 0 FP |
| `EXTERNAL_INPUT_UNCERTAIN` occurrences | 150 | 150 correct uncertainty classifications |
| `RUNTIME_CONTEXT_UNCERTAIN` occurrences | 150 | 132 correct and 18 unclear classifications |
| Source-first files | 150 | 133 TN, 3 with supported issues, 14 unresolved-context blocks |

Among decided `CANDIDATE_MISSING` labels, observed precision is 84/84 (100%;
naive Wilson 95% interval 95.6%–100%). Treating all uncertain labels as
non-TP gives a conservative TP yield of 84/150 (56.0%). Resolution-class
accuracy is 366/366 among decided labels, with 366/450 (81.3%) decision
coverage.

Source-first review found 11 supported issue occurrences and matched 10,
giving 90.9% occurrence-level supported recall (naive Wilson 95% interval
62.3%–98.4%). These occurrences occur in only two repositories: one matched
and one missed. Repository-level supported recall is therefore 1/2 and highly
uncertain.

The missed case is `tarzan_proj_dir` in
`NationalGenomicsInfrastructure/miarka-provision`'s
`roles/tarzan/defaults/main.yml`. The same defaults file defines
`tarzan_root_dir`, making the unresolved name a likely typo and a detector
false negative.

These labels were produced by a single agent using source context, definition
indexes, argument contracts, and post-selection detector matching. They are
calibration evidence, not independent human gold-standard labels. Naive
occurrence intervals also understate repository clustering.

## Remaining work

The remaining validation requirement is an independent second reviewer for
agreement and adjudication, followed by a genuinely unseen repository sample
for final generalization claims. The persistent `cosmos-ansible` timeout
should also be profiled independently; it is not caused by the
required-argument change and should not be hidden by increasing the corpus
timeout again.
