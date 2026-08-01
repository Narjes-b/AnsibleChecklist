# Pull-request profiles, rollout, and validation plan

> **Implementation update:** Base/head occurrence comparison, observe/ratchet
> policies, GitLeaks history scanning, and schema-versioned output are now
> implemented. The workflow consumes `canonical/occurrences.json`, enriches
> `summary/summary.csv`, and uploads `canonical/findings.sarif`. See
> [OUTPUT_CONTRACT_V2_SIX_CHANGES.md](OUTPUT_CONTRACT_V2_SIX_CHANGES.md).

## Decision

AnsibleGuard can become a professional pull-request check, but the current
workflow should remain advisory until four blockers are fixed:

1. raw GitLeaks objects must never be written to uploaded artifacts;
2. ansible-lint must run from the scanned project's root;
3. external rule IDs, tool versions, configuration hashes, and safe
   fingerprints must be preserved;
4. the PR gate must distinguish new findings from debt already present on the
   base branch.

The recommended model is:

```text
developer commit
  └── optional fast local checks
pull request
  ├── unprivileged scan of untrusted PR code
  ├── base-versus-head finding comparison
  ├── commit-range secret scan
  ├── review-range policy
  └── artifacts/SARIF containing redacted evidence only
protected branch
  └── required status checks enforce the agreed policy
nightly/scheduled
  ├── full-tree technical scan
  ├── full-history secret scan
  └── performance and drift monitoring
research pipeline
  └── frozen manifests and research profiles; never the mutable PR baseline
```

This document interprets “toy repo” as a small purpose-built Git repository
whose commits and expected results are controlled. A toy repository is useful
for end-to-end workflow tests, but it must be combined with frozen real
repositories and manually labeled findings.

The detector-level evidence and limitations behind this decision are in
[`ANSIBLE_LINT_GITLEAKS_OVERLAP.md`](ANSIBLE_LINT_GITLEAKS_OVERLAP.md).

## Definitions

| Term | Meaning in this plan |
|---|---|
| Pull request (PR) | the complete proposed change from a base commit to a head commit |
| Base | the protected-branch commit against which the PR is evaluated |
| Head | the contributor's proposed commit |
| Changed file | a path added, modified, renamed, or deleted in `base...head` |
| Finding | one detector result with tool/rule identity, location, evidence, and policy severity |
| Fingerprint | a stable, secret-free identity used to compare the same occurrence across runs |
| New finding | a head finding whose canonical fingerprint is absent from the base result |
| Fixed finding | a base fingerprint absent from the head result |
| Baseline | the immutable result for the exact base commit, not a hand-edited list of whatever should pass |
| Ratchet | allow known base debt but reject newly introduced debt |
| Blocking | the status check fails and branch protection prevents merge |
| Advisory | results are visible but do not prevent merge |
| Suppression | a reviewed, scoped exception with reason, owner, and ideally expiry |
| Tool error | the scanner did not complete; it is not the same as a clean scan |
| Parse error | source could not be read/parsed; it is not the same as no findings |
| Toy repository | a controlled Git fixture with known commits, branches, files, and expected outcomes |
| Golden result | a reviewed expected output used by a regression test |

## What exists now

### Implemented execution profiles

| Existing profile | Intended population | External tools | Suitable as a PR gate? |
|---|---|---:|---|
| `technical-full` | all internal, review, ansible-lint, and GitLeaks results | yes | engine for the main PR scan, after blockers are fixed |
| `snapshot-source` | all internal source rules at one classified commit | no | no; research/calibration use |
| `research-core` | provisional paper-derived source allowlist | no | no; not yet research-eligible and too narrow for engineering |
| `extended-ansible` | remaining internal source rules | no | advisory research/diagnostic use only |
| `review-range` | seven base-to-head Git/review rules | no | yes, either as a separate check or a distinct section of `technical-full` |

These profiles define analysis populations. They should not be renamed
“junior,” “senior,” or “developer” profiles. Developer experience and merge
policy are a second dimension.

### Current GitHub workflow

`.github/workflows/ansibleguard.yml` already:

- runs on pushes to `main`/`master` and on pull requests;
- checks out full history;
- installs the package and GitLeaks;
- supplies PR base/head SHAs;
- runs the default `technical-full` profile;
- uploads SARIF and detailed artifacts;
- blocks error-severity findings and external tool errors.

That is a useful prototype, not yet a safe final design.

### Current policy behavior

- Every GitLeaks result is an AnsibleGuard error and therefore blocks.
- Every ansible-lint result is normalized as a warning and does not block the
  workflow's final enforcement script.
- Internal error-severity findings block whether old or new.
- Warning/note findings are advisory.
- Parse failures do not block the workflow's manual enforcement step.
- A GitLeaks or ansible-lint execution failure blocks.
- The full output directory is uploaded even after failures.

The intended policy must be written down explicitly before branch protection
requires the check.

## Design principle: keep analysis profiles and CI policy separate

Add an orthogonal policy mode rather than modifying the scientific profiles:

| Proposed policy mode | Decision rule | Use |
|---|---|---|
| `observe` | never fail on findings; fail only on installation/contract corruption | first rollout and data collection |
| `changed` | evaluate findings whose source locations intersect the PR change | fast feedback, but insufficient alone |
| `ratchet` | fail on canonical findings present at head but absent at base | normal PR enforcement |
| `strict` | fail on all configured head findings, including old debt | clean repositories or later maturity |

`changed` and `ratchet` are not equivalent. A changed line can move an old
finding, and a new project-level finding may not have a single changed line.
The canonical policy should be `ratchet`; changed-line filtering is a user
interface view.

## Proposed developer experience

### Level 1 — local fast feedback

Provide one documented command or pre-commit configuration:

```text
ansible-lint using the repository's pinned configuration
gitleaks on staged content with redacted output
AnsibleGuard internal checks on staged/changed Ansible files
```

Local hooks are helpful, but the server-side PR job remains authoritative
because hooks can be skipped and developer environments differ.

No local check should require production credentials, inventory access, or
target-host execution.

### Level 2 — every pull request

Run on the GitHub `pull_request` event with:

- untrusted PR code;
- read-only repository permissions for the scan job;
- no repository/environment secrets;
- a GitHub-hosted ephemeral runner initially;
- complete base and head objects;
- pinned dependencies and action commit SHAs;
- network disabled during analysis after dependencies/tools are provisioned,
  where practicable.

Do not use `pull_request_target` to check out and execute contributor code.
GitHub explicitly warns that this can expose write privileges and secrets:
[secure use reference](https://docs.github.com/en/actions/reference/security/secure-use)
and
[event documentation](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows).

### Level 3 — protected-branch and scheduled audit

On a successful merge and on a schedule:

- run `technical-full` against the complete tree;
- run `gitleaks git` over the agreed history boundary;
- validate that the base-result cache matches the protected-branch SHA;
- report newly appearing tool/rule/config versions;
- record p50/p95 duration and finding drift;
- open a maintenance issue when a tool upgrade or schema change is detected.

This scheduled job is the place for expensive full-history or large-repository
checks, not the latency-sensitive PR path.

### Level 4 — research runs

Continue using `snapshot-source`, `research-core`, `extended-ansible`, and
`review-range` with frozen commits and classified manifests. Do not use the
mutable developer baseline as research evidence.

Research output must record:

- repository and full commit SHA;
- classified file manifest and hash;
- profile rule list and hash;
- package lock/container digest;
- external tool versions and binary checksums when external tools are studied;
- effective configs and hashes;
- raw-versus-deduplicated counts;
- manual labels and adjudication;
- exact analysis script/workflow commit.

## PR analysis algorithm

### Step 1 — establish trustworthy inputs

1. Resolve the full base and head SHAs from the event payload.
2. Verify both are commits in the checked-out repository.
3. Record the merge base.
4. Reject missing or shallow history instead of silently falling back.
5. Enumerate added, modified, renamed, copied, and deleted paths with
   machine-readable Git output.
6. Treat filenames, branch names, and commit messages as untrusted data; never
   interpolate them directly into shell code.

### Step 2 — run head analysis

Run `technical-full` at head after:

- removing raw secret persistence;
- setting ansible-lint's working directory to the target root;
- moving GitLeaks to the explicit `dir` command;
- pinning versions and validating checksums;
- recording configuration provenance.

Generate redacted normalized JSON and SARIF.

### Step 3 — run or retrieve base analysis

Preferred order:

1. retrieve a signed/immutable result for the exact base SHA;
2. otherwise analyze a separate clean base worktree with exactly the same
   toolchain/configuration;
3. never reuse a result produced with a different rule-list or config hash.

Base and head analysis must not overwrite one another.

### Step 4 — compare canonical findings

The first fingerprint design should use:

```text
analysis family
native tool and rule
normalized repository path
semantic source anchor
safe evidence digest
```

Line number alone is unstable when lines move. Messages alone are unstable
when tools change wording. Secret values must never enter a fingerprint; use
the scanner's safe fingerprint or a one-way digest constructed in memory and
discard the value.

Output:

- introduced;
- unchanged;
- fixed;
- moved/renamed;
- uncertain match.

Uncertain matches should be visible and measured, not silently counted as new
or old.

### Step 5 — scan the commit range for secrets

Run a separate pinned `gitleaks git` protocol for `base..head`. This detects a
secret introduced and removed in an intermediate PR commit, which a head-tree
scan cannot see.

The tree scan and history scan must have different `scan_mode` values and
separate counts. GitLeaks documents the distinct `dir`, `git`, and `stdin`
modes and Git log options in its
[official repository](https://github.com/gitleaks/gitleaks).

### Step 6 — apply policy

Initial recommended blocking policy:

| Condition | Observe phase | Ratchet phase |
|---|---:|---:|
| new GitLeaks secret in tree or PR commits | block after redaction is proven | block |
| external tool did not run or output was invalid | block | block |
| missing/invalid base or head provenance | block | block |
| new internal error-severity finding | advisory while calibrated | block only validated rules |
| new ansible-lint finding | advisory | block selected stable rules; warn on others |
| new review-range finding | advisory | block supervisor-approved rules |
| warning/note finding | advisory | advisory unless promoted by written policy |
| pre-existing base finding | advisory inventory | do not block under ratchet |
| parse failure on a changed Ansible file | block | block |

Do not make all ansible-lint warnings fatal on day one. Select a versioned
allowlist of stable rules, measure the existing population, and promote rules
after false-positive review.

### Step 7 — publish safely

Publish:

- a concise check summary;
- redacted normalized JSON;
- SARIF with repository-relative paths and stable fingerprints;
- diagnostics;
- run metadata;
- a limited-retention artifact that has passed the no-secret canary test.

Never publish raw GitLeaks JSON, source excerpts containing a secret, Vault
plaintext, environment variables, or dependency credentials.

GitHub accepts third-party SARIF and can associate separate analyses using
categories. Private/internal repositories require GitHub Code Security:
[official SARIF upload documentation](https://docs.github.com/en/code-security/how-tos/find-and-fix-code-vulnerabilities/integrate-with-existing-tools/upload-sarif-file).

Fork PRs have a read-only `GITHUB_TOKEN` and receive no ordinary secrets. If
SARIF upload is not authorized, the scan must still complete and expose a
safe check/artifact rather than fail the analysis:
[fork event behavior](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows).
A later privileged publisher must never execute PR code and must validate any
artifact before use.

## Configuration and suppression policy

Use repository-owned, reviewed files:

```text
.ansible-lint
.gitleaks.toml
.gitleaksignore
.ansibleguard.yml
ansibleguard-policy.yml
dependency lock/container digest
```

Every suppression must contain:

- exact rule and smallest practical scope;
- reason;
- owner/reviewer;
- issue or decision reference;
- creation date;
- expiry/review date where supported.

The CI summary should report suppression count and expired suppressions.
Changing a scanner config, baseline, or policy file should request review from
the tool/security owners through `CODEOWNERS`.

For GitLeaks, explicitly choose whether the project config extends the default
rules or replaces them. Hash the effective config. The
[official GitLeaks configuration documentation](https://github.com/gitleaks/gitleaks)
explains that a custom configuration can replace defaults unless extension is
declared.

For ansible-lint, pin the profile and explicit enable/warn/skip choices.
Its
[official configuration documentation](https://docs.ansible.com/projects/lint/configuring/)
shows that opt-in rules, ignores, installed dependencies, and project
configuration affect the effective rule set.

## Professional test strategy

No single test repository is enough. Use four complementary evidence sets.

### A. Unit and contract tests

Test every wrapper without depending only on tool installations:

- command construction and target `cwd`;
- return-code mapping;
- missing binary;
- timeout and interrupted process;
- malformed, empty, and schema-changed output;
- path normalization on Linux/Windows-style paths;
- line/column extraction;
- native rule/subrule/severity preservation;
- version and config hash capture;
- secret-field redaction;
- checksum verification;
- deterministic fingerprints;
- no collision for distinct fixture findings;
- backward compatibility or explicit migration failure.

Contract fixtures should be captured from the exact pinned external versions
and checked for sensitive values before commit.

### B. Controlled toy Git repository

Create `tests/pr-repo/` through a deterministic builder script, or maintain a
separate private/public fixture repository if real GitHub events are required.
Use synthetic, provider-documented test tokens only—never live credentials.

Required commit/PR scenarios:

| Scenario | Expected result |
|---|---|
| clean base, clean head | pass |
| old base warning unchanged | pass under ratchet |
| new internal error | fail when that rule is enforced |
| internal error fixed by PR | pass and report fixed |
| secret added at head | fail without secret in output/log/artifact |
| secret added then deleted in an intermediate commit | history job fails; head tree is clean |
| renamed file with unchanged finding | report moved/unchanged, not new |
| changed lines near an old finding | fingerprint remains stable |
| changed `.ansible-lint` profile | invalidate/recompute comparable base |
| custom GitLeaks config replaces defaults | metadata says replacement and tests expected coverage |
| malformed YAML | parse/lint diagnostic, not clean |
| missing role/collection | distinguish environment/dependency failure from source finding |
| docs-only PR | fast pass; review rules still evaluate if applicable |
| deleted Ansible file | no head source finding; fixed findings are reported |
| malicious filename/commit message | no command or expression injection |
| fork PR/Dependabot-equivalent token | scan runs read-only; publication degrades safely |
| cancelled/restarted workflow | no stale base result is reused |
| large generated repository | completes within resource/time budget |

This repository validates Git history, event, baseline, and publication
behavior that ordinary unit fixtures cannot.

### C. Differential and mutation tests

For every external integration fixture:

1. run the external tool directly;
2. run it through AnsibleGuard;
3. require one-to-one preservation of safe native identities and locations;
4. explain every deliberate filtered/deduplicated result.

Mutation operators should add/remove or alter:

- duplicate YAML keys;
- shell versus module usage;
- `changed_when`;
- names;
- file modes;
- `no_log`;
- handler notifications;
- role dependencies;
- variable definitions/guards;
- provider-specific synthetic tokens;
- generic high-entropy non-secrets;
- Git review metadata.

Each seeded positive must be killed by the expected detector, and nearby
negative mutations must remain clean. Mutation score is a test-adequacy
measure, not detector precision.

### D. Frozen real-repository validation

Use:

- the existing controlled detector corpus;
- the frozen Nova project already in the study;
- the five-project OpenStack pilot;
- later, a stratified sample of the intended corpus.

Manually label a rule-stratified sample with at least two reviewers and an
adjudication process. Keep `true-positive`, `false-positive`, `uncertain`, and
`out-of-scope` distinct.

Report per rule/tool:

```text
TP, FP, FN
precision = TP / (TP + FP)
recall = TP / (TP + FN)
F1 = 2 * precision * recall / (precision + recall)
agreement and adjudication rate
unique findings contributed beyond other tools
```

Finding recall cannot be estimated by reviewing only reported findings; the
sample must also contain manually inspected negatives or deliberately seeded
positives.

## End-to-end GitHub validation

A sandbox GitHub repository is still required after local toy-repository
tests. Exercise:

1. same-repository PR;
2. public-fork PR;
3. first-time contributor approval;
4. Dependabot-like PR;
5. branch protection with required checks;
6. SARIF-enabled public repository;
7. private repository with and without GitHub Code Security;
8. rerun after base branch advances;
9. concurrent updates with cancellation;
10. artifact permissions and retention.

Record screenshots or API-exported check conclusions only as supporting
evidence. The reproducible evidence is the workflow YAML, event fixture,
commits, logs with secrets redacted, and output hashes.

## Performance evaluation

Measure separately:

- checkout/setup time;
- dependency installation;
- GitLeaks tree scan;
- GitLeaks commit-range scan;
- ansible-lint;
- internal source detectors;
- review-range detectors;
- normalization/deduplication;
- SARIF/artifact publication.

For toy-small, real-medium, and generated-large repositories, report:

- files and bytes scanned;
- base/head commit count;
- wall-clock p50/p95;
- CPU time where available;
- peak resident memory;
- output size;
- cache hit/miss;
- failure/timeout rate.

Use repeated warm and cold runs on a stated runner image. Do not report one
total time as if it measures detector algorithm complexity.

Initial service-level targets should be agreed after observation. A reasonable
starting hypothesis—not yet a measured promise—is:

- fast PR feedback p95 under 5 minutes;
- no individual scanner silently exceeding its timeout;
- zero secret canary occurrences in persisted output;
- deterministic policy conclusion for identical base/head/toolchain inputs;
- less than 1% infrastructure-related flaky runs over the observation period.

## Acceptance gates

### Gate 0 — security

- synthetic secret absent from every file, log, summary, SARIF, and artifact;
- no secrets available to untrusted PR scan;
- no `pull_request_target` execution of PR code;
- external binary/package checksums verified;
- action references and containers pinned by immutable digest/SHA.

### Gate 1 — correctness

- base/head provenance exact;
- head and base configurations comparable;
- direct-tool versus normalized identity/location parity;
- every failure mode distinguished from a clean scan;
- rename/move and pre-existing-debt scenarios pass golden tests.

### Gate 2 — detector evidence

- blocking internal rules have acceptable labeled precision agreed with the
  supervisor/team;
- secret fixtures cover provider-specific, generic, false-positive, encoded,
  and history-only cases;
- ansible-lint blocking allowlist is explicit and versioned.

### Gate 3 — workflow reliability

- same-repository, fork, and Dependabot-equivalent PRs tested;
- SARIF fallback works where upload is unavailable;
- cancellation/concurrency does not publish stale results;
- p95 latency and flake target met during the observation window.

### Gate 4 — governance

- policy owner and CODEOWNERS established;
- suppression schema/review/expiry established;
- branch protection names stable;
- incident process covers a real detected credential;
- version upgrade and rollback process documented.

## Rollout sequence

### Phase 0 — remove unsafe behavior

1. redact GitLeaks data before any write;
2. stop uploading legacy raw files;
3. add no-secret canary tests;
4. verify GitLeaks release checksum;
5. pin dependencies and action SHAs.

### Phase 1 — make evidence reproducible

1. fix ansible-lint `cwd`;
2. use explicit SARIF/native schemas;
3. preserve native identities and versions;
4. hash configs and rule lists;
5. introduce canonical fingerprints;
6. separate tree and history scan modes.

### Phase 2 — build the ratchet

1. analyze exact base and head;
2. implement introduced/unchanged/fixed comparison;
3. validate rename and config-change behavior;
4. expose a machine-readable policy decision;
5. keep all rules advisory except security/tool/provenance failures.

### Phase 3 — observe

Run for at least two representative development cycles. Measure:

- findings per rule;
- new versus old;
- reviewer-confirmed false positives;
- suppressions;
- runtime and flakes;
- developer resolution time.

Do not tune thresholds on the final evaluation set.

### Phase 4 — progressive enforcement

1. require infrastructure/tool/provenance correctness;
2. require redacted commit-range and tree secret checks;
3. promote validated internal error rules;
4. promote selected stable ansible-lint rules;
5. promote review-range rules only after policy approval;
6. retain warnings/notes as annotations until evidence supports promotion.

### Phase 5 — research evaluation

Freeze the implementation, configs, versions, manifests, and labeled corpus.
Run the predefined analysis once, produce raw and deduplicated tables, and
archive the replication package.

## Proposed implementation PRs

Keep changes reviewable and independently testable.

### PR 1 — secret-safe output

- remove/raw-redact GitLeaks persistence;
- add redaction/canary tests;
- stop artifact upload if sanitization validation fails;
- document credential response.

### PR 2 — external tool contract and provenance

- fix ansible-lint root execution;
- move GitLeaks `detect --no-git` to `dir`;
- preserve native IDs/severity/version;
- verify binary checksum;
- lock dependency versions;
- add output-schema contract tests.

### PR 3 — canonical finding schema

- add columns, safe evidence digest, scan mode, and config hash;
- update JSON/CSV/text/SARIF;
- add schema version and migration tests;
- define raw and canonical occurrence tables.

### PR 4 — base/head ratchet

- exact SHA validation;
- separate base/head outputs;
- comparison and policy decision;
- rename/move/config-drift handling;
- controlled toy-repository tests.

### PR 5 — hardened GitHub workflow

- read-only untrusted scan job;
- immutable action references;
- concurrency/cancellation;
- conditional SARIF publishing/fallback;
- stable required-check names;
- end-to-end sandbox-repository evidence.

### PR 6 — calibration and gradual enforcement

- labeled developer-PR sample;
- selected blocking allowlists;
- suppression governance;
- latency/flakiness dashboard;
- observation report and go/no-go decision.

## Paper-ready evaluation questions

Possible research questions:

- **RQ1:** Which AnsibleGuard rules overlap with ansible-lint and GitLeaks at
  construct and occurrence level?
- **RQ2:** How many unique confirmed findings does each detector family
  contribute?
- **RQ3:** What are the per-rule precision and recall on the labeled Ansible
  corpus?
- **RQ4:** How reliably does the PR ratchet distinguish introduced,
  pre-existing, fixed, and moved findings?
- **RQ5:** What runtime and memory overhead does each analysis stage add on
  repositories of different sizes?
- **RQ6:** How does progressive enforcement affect false-positive burden and
  developer remediation?

Do not answer RQ6 from a toy repository; it requires real development
observation and appropriate ethics/privacy treatment.

## Threats to validity

- **Construct validity:** similarly named rules may implement different
  predicates; smells are not proven defects.
- **Internal validity:** tool/config/version changes can cause apparent
  differences; base and head must use the same frozen environment.
- **External validity:** OpenStack and a toy repository may not represent
  private enterprise Ansible, other languages, or different role layouts.
- **Conclusion validity:** rare findings yield unstable precision/recall;
  report counts and uncertainty, not only percentages.
- **Label validity:** reviewers can disagree; preserve independent labels and
  adjudication.
- **Instrumentation:** normalization or path matching can lose external
  findings; differential tests are required.
- **Security:** test tokens, artifacts, and logs can themselves leak data;
  canary tests and least privilege are mandatory.
- **Performance:** GitHub-hosted runner variance and cache state confound time;
  use repeated, stratified measurements.

## Sources

Primary technical sources:

- [ansible-lint overview](https://docs.ansible.com/projects/lint/)
- [ansible-lint profiles](https://docs.ansible.com/projects/lint/profiles/)
- [ansible-lint configuration](https://docs.ansible.com/projects/lint/configuring/)
- [ansible-lint usage and output](https://docs.ansible.com/projects/lint/usage/)
- [GitLeaks usage, modes, baseline, and configuration](https://github.com/gitleaks/gitleaks)
- [GitLeaks 8.30.1 release and checksums](https://github.com/gitleaks/gitleaks/releases/tag/v8.30.1)
- [GitHub fork PR event and token behavior](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)
- [GitHub secure Actions use](https://docs.github.com/en/actions/reference/security/secure-use)
- [GitHub third-party SARIF upload](https://docs.github.com/en/code-security/how-tos/find-and-fix-code-vulnerabilities/integrate-with-existing-tools/upload-sarif-file)
- [GitHub push protection](https://docs.github.com/en/code-security/concepts/secret-security/push-protection)

Research foundations:

- Basak et al., *A Comparative Study of Software Secrets Reporting by Secret
  Detection Tools*, ESEM 2023:
  [DOI](https://doi.org/10.1109/ESEM56168.2023.10304853),
  [preprint](https://arxiv.org/abs/2307.00714)
- Rahman et al., *Security Smells in Ansible and Chef Scripts: A Replication
  Study*, ESEC/FSE 2020:
  [DOI](https://doi.org/10.1145/3408897)
- Saavedra and Ferreira, *GLITCH: Automated Polyglot Security Smell Detection
  in Infrastructure as Code*, ASE 2022:
  [preprint](https://arxiv.org/abs/2205.14371)
- Opdebeeck, Zerouali, and De Roover, *Control and Data Flow in Security Smell
  Detection for Infrastructure as Code: Is It Worth the Effort?*, MSR 2023:
  [DOI](https://doi.org/10.1109/MSR59073.2023.00079),
  [replication package](https://doi.org/10.6084/m9.figshare.21929856)

These sources justify definitions and methods. The final paper must still cite
the exact tool versions/configurations actually evaluated and archive the
replication artifacts.
