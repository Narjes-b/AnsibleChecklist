# Changelog

All notable AnsibleGuard changes, newest first. Each version section preserves
the facts recorded for that release; empirical numbers belong to the version
and corpus they name and are not restated for later versions.

## Unreleased

- Console progress lines use plain prefixes (`[ok]`, `[error]`, `warning:`)
  instead of symbols, so logs stay readable in CI and plain terminals.
  Report files are unchanged.
- The GitHub Actions workflow scans the pull-request head and pushed commits
  from a detached worktree. Previously the report directory was created inside
  the scanned checkout, so a head scan could include its own cache files and
  report spurious introduced secrets.
- Added `docs/demo/` with the tool demonstration video and reproduction
  commands, and reorganized the README.

## 0.0.7.1

Fixes from the 2026-10-15 audit (`docs/study/v007-audit-2026-10-15.md`). They
change detector output, so results produced with them are a new version and
are not comparable to the frozen `v007-full-repro-2026` run without a rerun.

### Detection

- Git review rules no longer treat the whole repository as the change on a
  shallow snapshot. When the head commit records a parent that is not present,
  `missing-release-note`, `missing-test-update`, `untested-override-change`,
  and `removed-copyright-notice` are not evaluated, and a `not-evaluated`
  `review-range-detectors` diagnostic is emitted. A genuine root commit keeps
  its full-tree range. Message-only rules still use the exact head message.
- `missing-release-note` recognizes `CHANGELOG`/`CHANGES`/`NEWS`/`HISTORY`/
  `RELEASE_NOTES` documents, Ansible collection `changelogs/fragments/` and
  `changelogs/changelog.yaml`, `changelog.d/`, `.changes/`, and
  `newsfragments/`, in addition to reno `releasenotes/notes/`.

- `missing-release-note` and `missing-test-update` ignore Kubernetes-style
  manifests (every document has `apiVersion` and `kind`) and changelog files
  when collecting configuration changes; commit-message rules skip merge
  commits.
- `missing-bug-reference` recognizes `Fixes|Closes|Resolves #n` (optionally `owner/repo#n`), issue/bug/ticket URLs and
  tracker keys (`ABC-123`; `UTF-8`, `SHA-256` and similar are excluded); a pull-request number alone is still not a
  reference. Commit-message rules skip bot authors (dependabot, renovate, github-actions, `[bot]`).
- `missing-file-extension` no longer flags `namespace.collection.playbook` targets of `import_playbook`, `.json` files
  or directories in `include_vars`, or file names followed by free-form arguments.
- `unscoped-shell-variable` ignores the body of heredocs with a quoted delimiter (`<<'EOF'`), which the shell does not expand.
- `read-only-command-change` no longer treats a pipeline that ends in `umount`, `mount`, `kill`, `pkill` or `rm` as read-only.
- The unresolved-work marker no longer matches a path such as `hack/`.
- `missing-handler`/`unused-handler` follow static `import_tasks`/
  `include_tasks` handler imports, `listen:` topics in imported files, local
  role handlers, and notifies from statically included task files. When a
  handler or notify source cannot be resolved statically, the corresponding
  claim is not made.
- `non-idempotent-command` and `read-only-command-change`: `-o`/`--output`
  means "writes a file" only for curl; `kubectl get -o json`, `kubectl ...
  --output jsonpath`, and similar read-only queries are no longer mutating.
  The read-only message no longer says "curl" for every command.
- `incomplete-task` no longer treats a marker joined to an identifier
  (`containerd-hack`, `todo_list`) as TODO/HACK.
- `broken-role-dependency` no longer reports a Galaxy role such as
  `DavidWittman.redis` as a self-dependency of a local `redis` role, and only
  local roles enter cycle detection.
- `invalid-task-attribute-type` accepts `environment` as a list of mappings,
  as Ansible defines it (`vars` must still be a mapping).
- `high-coupling` messages report the threshold actually used (previously
  `threshold=None` when the project config did not set it).

### Pull-request scans

- Local `ansibleguard diff` reviews exactly `base..head` on the head side and
  an empty range on the base side (per thread, also with
  `--parallel-base-head`), matching the GitHub workflow. Previously only the
  last head commit was reviewed and base-side history findings could appear as
  "fixed".
- A PR comparison no longer aborts when an external provider is incomplete:
  if AnsibleGuard's own analysis completed and every fault is a provider
  fault, that provider's findings are excluded from both sides and the report
  says so. Incomplete internal analysis is still refused.
- ansible-lint 26.x task-level findings are moved from the line after the task
  (where ansible-lint reports them) to the task's first line, so findings,
  changed-line mapping, deduplication, and read-only suppression refer to the
  right task. `yaml[...]` findings keep their exact line.
- A single unparseable file (for example an `mkdocs.yml` with a
  `!!python/name:` tag) no longer aborts the PR comparison. Files that fail
  to parse on either side are excluded from both and listed as "Not
  compared"; a change that makes a file it touches unparseable fails the
  policy as a parse regression. Other internal faults are still refused.
- ansible-lint messages that embed Python sets are normalized to a sorted
  order, so fingerprints and occurrence IDs no longer change between runs.
- The workspace guard also removes new files created inside a pre-existing
  (often gitignored) `.ansible/` cache.
- Moved findings are matched through the diff: base lines are mapped through
  `git diff -U0` hunks, so groups of identical findings (for example many
  `yaml[truthy]` lines) shifted by an edit are reported as moved instead of
  fixed + introduced, and an identical identity at the same line number is no
  longer paired with a different task. On 21 replayed real pull requests this
  reduced introduced/fixed from 462/422 to 60/20, with 638 moves recognized.
- Optional-policy findings never block a pull request; secrets always do.
- New guide: `docs/pr-scan.md`.

### Providers

- ansible-lint can no longer modify the scanned tree. A project config's
  `write_list` makes ansible-lint rewrite YAML (including its own config) even
  without `--fix`, and the command line cannot disable it. AnsibleGuard now
  snapshots YAML files before the provider runs, restores any rewrite, removes
  `.ansible/`, `__pycache__/`, and `*.tmp.yml` artifacts the run created, sets
  `PYTHONDONTWRITEBYTECODE=1`, and records the intervention under
  `workspace_guard` in provider metadata.

### Study tooling

- Provider-comparable tables include only repositories where every provider
  completed and exclude review-range rules (previously review findings were
  mixed in and repositories without ansible-lint evidence counted as zero).
- `fetch_v007_review_history_parents.py` fetches first parents into bare side
  repositories (`study/cache/v007-review-history/`) that borrow the frozen
  objects read-only, without an object filter, and verifies an offline
  parent-to-target diff and an unchanged frozen checkout. The previous design
  converted frozen checkouts into `tree:0` partial clones whose diffs could not
  be computed offline.
- Pilot context generation lists the cited role (not an intermediate grouping
  directory) with paths beside the cited file first, and shows release-note
  files in release-note diffs using the detector's own definition.
- `SAMPLING_AUDIT.md` table separator matches its header.
- Scripts that import `scripts.*` run directly as `python scripts/<name>.py`.

### Charts

- No silent truncation: the occurrences-per-repository chart drew 25 of 139
  bins (76 of 206 repositories) and re-sorted bins by count; bins and runtime
  buckets now keep their order and every row is drawn (titles state any top-N
  limit).
- Severity and confidence charts are titled with the population they plot
  (AnsibleGuard static-source, not all canonical occurrences); ordinal scales
  use ordered, meaningful colours; counts are integers.
- Top-rule and prevalence charts mark optional-policy and mostly-uncertain
  rules; new `04b` chart excludes optional policy; the density chart is a
  distribution over all repositories instead of the 25 highest outliers.
- Rendering the charts (not only reading their SVG) found three more defects,
  now fixed: the rule × repository heatmap had clipped, overlapping column
  headers and one global colour scale dominated by a single cell (now per-rule
  colour scaling, a legend line and a column-maximum row); the size-versus-
  findings scatter had only end-point ticks and unlabelled outliers (now log
  axes with ticks, the Spearman correlation, and non-overlapping outlier
  labels); the provider chart mixed populations without saying so (now shows
  each provider's repository coverage and the 497 review-range occurrences).
- Legacy report charts no longer present a mixed-provider category
  composition; their titles state the population.

### Documentation

- Root documentation reduced to README, ARCHITECTURE, CHANGELOG, and the two
  generated references; current guides moved under `docs/`; historical
  reports removed from the working tree (preserved in Git history; see
  `docs/README.md`).

## AnsibleGuard 0.0.7

Frozen analysis commit for the full study run: `d1711f90b7ab45fe80f429927c310cf58a323f77`
(run identity `v007-full-repro-2026`).

### Analysis

- Evidence-backed variable resolution and three-way certainty
  (certain / review / suppressed) for variables, facts, and includes.
- Escaped and parenthesized Jinja expression locations are preserved across
  detector passes.
- Dynamic-include glob patterns that raise `NotImplementedError` are handled.

### Study infrastructure

- Reproducible full-run orchestration (`scripts/run_v007_full_repro.sh`) over the
  frozen 207-repository manifest with exactly four concurrent repository jobs,
  a disk-budget guard, exact-SHA shallow acquisition, and verified reuse of
  frozen local checkouts.
- Incomplete scan outcomes are preserved as missing observations; provider
  aggregation attribution and result reporting were repaired before packaging.
- Threshold benchmark and threshold-sensitivity audit for additional detector
  families; Cohen's kappa and F1 utilities.
- Human-validation tooling: stable namespaced validation identities, a
  deterministic 144/62 calibration/heldout repository split, rule-to-family
  mapping, a 350-item agreement pilot with frozen redacted contexts, blinded
  reviewer packets, and agreement analysis.
- GitHub discovery, enrichment, and cloning scripts gained checkpoint/resume,
  multi-token failover, and Windows robustness fixes.

## AnsibleGuard 0.0.6.1

### Variable certainty

- Divide `unguarded-variable` canonical output into
  `missing-internal-variable`, `undeclared-input-contract`, and
  `unresolved-runtime-input` while retaining the native rule ID for profile,
  suppression, and API compatibility.
- Preserve `legacy_concept_id: unguarded-variable` and expose
  `variable_classification` in JSON, canonical occurrences, and CSV.
- Treat underscore-prefixed role, playbook, and task-fragment values as
  possible inputs instead of strengthening them solely because of naming.
- Prove same-file conditional runtime definitions safe when a consumer has an
  identical or stronger supported conjunctive condition.
- Recognize bare `package_facts` and `service_facts` as built-in fact actions
  so they do not create generic custom-fact uncertainty.
- Correct namespaced `include_vars`: imported mapping keys are no longer
  exposed incorrectly as bare variables.
- Limit the built-in fact-module exemption to `ansible.builtin` and
  `ansible.legacy`; other collection fact modules remain schema-dependent.

### Documentation

- Add `V0061_VARIABLE_CERTAINTY_AND_FP_AUDIT.md` with the 149-repository
  evidence, the three-way model, current static guarantees, remaining runtime
  boundaries, and the proposed closed-world analysis path.
- Add `V0061_PRE_149_ALL_RULE_READINESS_AUDIT.md` with an all-76-rule audit,
  provider-completeness findings, threshold-labeling protocol, agentic
  correction gates, and the exact pre-scan go/no-go checklist.

### Pre-validation reliability

- Run metadata- and vars-specific detectors through the safe-source path so
  `galaxy-meta-incomplete` and `variable-naming-convention` are no longer
  unreachable in repository scans.
- Treat Galaxy metadata, role-prefix naming, Molecule presence, role README
  presence, and inline-vault organization as optional policies rather than
  universal defects; keep the newly reachable Galaxy/naming rules at
  candidate maturity pending calibration.
- Normalize punctuation in role names before checking variable prefixes and
  accept established compact prefixes such as `rhel8cis_`.
- Restrict role metadata shape enforcement to `meta/main.yml`; custom files
  such as `meta/variants.yml` may validly contain list-shaped project data.
- Use parser-retained source positions for excessive nesting, ordered variable
  conflicts, misplaced plays, and misplaced handler attributes.
- Remove repeated raw observations with the same `finding_id` from repository
  rollups while retaining first-seen detector evidence.
- Canonically map ansible-lint `var-naming[no-role-prefix]` and
  `redhat-ci[no-role-prefix]` evidence to `variable-naming-convention`.
- Preserve detector-specific `message` details when a detector does not use
  the older `issue` key.

## AnsibleGuard 0.0.6

### Correctness

- Preserve safe YAML mapping and key source coordinates through the shared
  parse cache, restoring distinct line identities for task-level findings.
- Use full Jinja undeclared-name extraction for `set_fact` liveness, including
  references that do not begin a Jinja expression and expressions containing
  Ansible-only filters or tests.
- Retain facts consumed by templates and other files in the same role without
  leaking same-named uses from disconnected roles.
- Classify bounded `unnecessary-set-fact` results as uncertain, experimental
  evidence instead of confirmed dead assignments.
- Track repeated `set_fact` assignments independently so a final dead write
  cannot be reported at the line of an earlier live assignment.
- Recognize fail-fast `assert`/`fail when: value is undefined` preconditions
  and distinguish declared role arguments, possible required role inputs, and
  inventory-precedence, playbook, and reusable task-fragment inputs from
  strict unresolved internal variables.
- Treat variable-file mappings as lazily evaluated so forward references are
  visible.

### Provider equivalence

- Resolve the nearest ancestor ansible-lint configuration for nested provider
  roots and pass it explicitly to ansible-lint.
- Preserve independent nested configurations.
- Exclude ansible-lint occurrences from version-delta claims when the two
  snapshots use different provider population scopes. A paired DebOps replay
  confirmed that its 63-versus-7,579 difference is project discovery versus
  explicit selected-file coverage, not configuration loss.

### Reporting and validation

- Document the provider/native-rule/AnsibleGuard-rule/canonical-concept
  taxonomy bridge for secret findings.
- Add regression tests for source coordinates, parse-cache round trips,
  same-file and template fact consumers, Ansible-filter expressions, repeated
  assignments, external role/inventory inputs, fail-fast guards, formerly
  zero-count rules, and ancestor ansible-lint configurations.

## AnsibleGuard 0.0.5

AnsibleGuard 0.0.5 changes the engine architecture while preserving the frozen
0.0.4 empirical corpus as historical evidence. No 0.0.5 correction is applied
retroactively to 0.0.4 results.

### Analysis core

- Parses each selected YAML file through one Ansible-aware boundary and shares
  the resulting `ParsedDocument` with all repository-scan detector families.
- Retains Ansible/custom tags, multiple YAML documents, duplicate-key evidence,
  source text and locations, classification, and parse diagnostics.
- Builds shared immutable repository, file, and task contexts plus include,
  role, project, dependency, and indexed variable relationships.
- Uses name-targeted variable visibility queries. The permanent 44,000-line,
  4,000-task benchmark parses once and completes the internal developer scan in
  seconds rather than the former quadratic multi-minute path.

### Correctness and health

- Classifies dynamic, missing, generated, external, and inaccessible includes
  without aborting the repository.
- Models same-task and inherited defined guards, bounded standard `default`
  filters, ordered runtime definitions, static inventory evidence, configured
  custom-module facts, and conservative uncertainty/abstention.
- Adds context-sensitive secret categories and credential-display evidence,
  including task/block/play `no_log` and cached module argument metadata.
- Corrects templated attribute types, include-connected handler context,
  included-variable use, runtime fact transitions, redundant defaults, and
  overriding facts.
- Makes parser, provider, detector, timeout, permission, memory, cache, and
  serialization failures explicit. Failed or partial analysis can never be
  represented as a clean zero-finding result.

### Providers and canonical results

- Keeps ansible-lint and Gitleaks as specialized provider engines under
  AnsibleGuard scope, root discovery, configuration, diagnostics, population,
  contextual filtering, and provenance control.
- Schema-validates provider payloads, separates internal/provider errors from
  smells, and marks environment-dependent syntax findings explicitly.
- Canonicalizes compatible overlapping concepts while retaining all provider
  evidence and protecting distinct same-line semantic subjects.

### Performance and workflows

- Adds repository-level `--jobs N`/CPU-RAM-aware scheduling, isolated immutable
  worker snapshots, deterministic parent aggregation, and optional concurrent
  provider/base-head execution.
- Adds content/version/config-keyed parse caching, cached module metadata,
  output guards, phase and per-detector timings, CPU/peak-memory/throughput and
  symbol-query counters.
- Adds stable semantic fingerprints, provenance and health compatibility gates,
  explicit Git rename matching, structured suppressions, and safe partial
  file-local PR acceleration.
- Adds a deterministic multi-shape benchmark generator and baseline gate,
  stratified and source-first sampling, review packets, and false-positive
  mechanism summaries.

### Verification contract

Performance-only modes must produce identical canonical occurrences for one or
many repository workers, cached or uncached execution, sequential or concurrent
providers, and different completion orders. Semantic corrections have explicit
before/after fixtures. Output is schema-versioned and deterministically sorted.

The detailed implementation state, bounded semantic limitations, verification
commands, and external validation blockers are maintained in
`V005_IMPLEMENTATION_LEDGER.md`; the type and pipeline design is documented in
`V005_SEMANTIC_ENGINE_ARCHITECTURE.md`.

## AnsibleGuard v0.0.4 — Precision Improvement Changelog

**Branch:** `version-0.0.4`  
**Base:** `version-0.0.3` (149-repository calibration corpus; 4,218 labelled
items; 72.6% unweighted occurrence precision)
**Controlled PR injection precision (v0.0.4):** 98.9% [94.2%, 99.8%] naive Wilson interval — 92/93 actionable, 10/10 negative controls passed; not natural-PR generalization precision

---

### Summary of Changes

All changes are precision-driven: every rule modified or disabled was identified in the
v0.0.3 empirical validation study as having a false-positive rate that degrades the
overall tool score. No behaviour-preserving refactors were made; only targeted fixes.

---

### P0 — Disabled or conservatively redesigned

#### `incohesive-play` and `incohesive-playbook`
- **Old precision:** ~8–9%
- **Root cause:** Shannon-entropy cohesion (`incohesive_plays.calculate_similarity`)
  fires on any standard three-phase role (install + configure + start) because the
  module-domain distribution of such a role always scores "low entropy".
  There is no static threshold that separates intentional structure from smell.
- **Fix:** Replaced the entropy-only trigger with an auditable evidence gate.
  A candidate now needs at least 8 known functional tasks, 4 domains, 3
  specialised domains, and no domain above 50%. Common service lifecycle
  domains are exempt. Unknown modules cannot create evidence. The playbook
  rule requires candidates in at least two plays, preventing duplicate
  file-level warnings for one anomalous play.
- **Status:** experimental, low confidence, pending held-out validation.
- **Files changed:** `module_domain.py`, `incohesive_plays.py`,
  `sem_cohesion.py`.

#### `undocumented-complex-task`
- **Old precision:** ~7%
- **Root cause:** The detector required an immediately-preceding YAML comment for any
  task using `block:`, having a `when:` condition longer than 80 chars, or being nested
  deeper than depth 2. In practice, 93% of such tasks are undocumented in real-world
  Ansible roles and that is normal practice, not a defect.
- **Fix:** Re-enabled conservatively. A candidate now requires at least three
  boolean operators, three Jinja filters, or nesting deeper than four; a nearby
  rationale comment suppresses it. Ordinary blocks and modest conditions do
  not fire.
- **Status:** experimental, low confidence.
- **File changed:** `src/ansibleguard/detectors/review_checklist.py`

#### `incomplete-task`
- **Old precision:** ~9%
- **Root cause:** `TODO_RE.search(line)` was applied to every raw source line,
  including YAML comments (`# TODO: upstream bug`). Comments are legitimate
  project notes and not incomplete task logic.
- **Fix:** Rewritten to scan only parsed task dict fields (task name string and
  non-control module argument values). YAML comments are never scanned.
- **File changed:** `src/ansibleguard/detectors/paper_candidates.py`

---

### P1 — High-impact detector rewrites

#### `broken-role-dependency`
- **Old precision:** ~0% (5 false positives on entire corpus)
- **Root cause:** The "local role not found under `roles/`" check flagged any
  Galaxy/collection dependency (e.g. `geerlingguy.docker`) that is installed to
  `~/.ansible/roles/` rather than a local `roles/` directory. The vast majority
  of real-world role dependencies are external.
- **Fix:** Removed the "missing local role" sub-check. Only **self-dependency**
  (role depends on itself) and **cycle detection** (A→B→A) are reliable static
  checks and are preserved.
- **File changed:** `src/ansibleguard/detectors/paper_candidates.py`

#### `gitleaks/kubernetes-secret-yaml`
- **Old precision:** 0%
- **Root cause:** This GitLeaks rule fires on any file containing
  `apiVersion: v1` + `kind: Secret` — i.e., legitimate Kubernetes manifests
  stored alongside Ansible roles in hybrid repositories. These are not Ansible
  quality signals.
- **Fix:** Added `kubernetes-secret-yaml` to `_DISABLED_GITLEAKS_RULES` in the
  `_filter_known_noise()` function. Findings from this rule are suppressed with
  reason `disabled-rule-not-ansible-signal` before reaching the canonical pipeline.
- **File changed:** `src/ansibleguard/external/gitleaks.py`

#### `plaintext-sensitive-variable`
- **Old precision:** ~4%
- **Root cause (1):** `_plaintext_literal()` accepted `int` and `float` values
  as potential secrets. Configuration values like `token_ttl: 3600`,
  `api_timeout: 30`, or `max_connections: 100` were flagged because the key
  matched `SENSITIVE_PARTS` and an integer was considered "plaintext".
  Secrets are always strings.
- **Root cause (2):** `NON_SECRET_SUFFIXES` was missing many common non-secret
  suffixes, causing keys like `*_backend`, `*_ttl`, `*_timeout`, `*_prefix`,
  `*_mode`, `*_size`, `*_format`, `*_dir` to be incorrectly flagged.
- **Fix 1:** `_plaintext_literal()` now returns `False` for `bool`, `int`, and
  `float` values immediately.
- **Fix 2:** Added 14 entries to `NON_SECRET_SUFFIXES`:
  `backend`, `count`, `dir`, `format`, `hash`, `header`, `limit`, `max`, `min`,
  `mode`, `prefix`, `size`, `suffix`, `timeout`, `ttl`.
- **File changed:** `src/ansibleguard/detectors/file_kinds.py`

#### `variable-use-before-definition` — repository-aware rehabilitation
- **Old precision:** 0% (all findings were false positives)
- **Root cause:** The detector cannot reliably see variables defined in inventory,
  imported roles, or collection defaults — so nearly every cross-file variable
  reference fires. The logic is architecturally sound but the scope is insufficient
  for real-world multi-file roles.
- **Fix:** Repository symbol definitions now suppress false ordering findings;
  the detector only reports same-sequence references whose `register` or
  `set_fact` definition occurs later and has no visible repository definition.
- **Status:** experimental, low confidence.
- **Files changed:** `missing_checklist.py`, `parser.py`, `findings.py`.

---

### P2 — Focused tightening

#### `duplicate-task-names`
- **Old precision:** ~41%
- **Root cause:** `repeated_task_names()` used a single `Counter` across all tasks
  in the entire file. Having the same task name (e.g., `Install packages`) in two
  different plays is intentional Ansible structure, not a defect.
- **Fix:** Rewritten to group tasks by `play_id` (from `calculate_metrics_task`)
  and count duplicates **per play**. Cross-play identical names no longer fire.
- **File changed:** `src/ansibleguard/detectors/duplicate_task_names.py`

#### `shell-instead-of-module`
- **Old precision:** ~39%
- **Root cause:** File-operation patterns (`cp`, `mv`, `rm`, `mkdir`, `chmod`,
  `chown`, `touch`, `find`) used `\b` word-boundary matching anywhere in the
  command string, causing them to match command arguments, path components, or
  option strings that happen to contain these words.
- **Fix:** Anchored all file-operation patterns to the start of the command
  string (`^(?:sudo\s+)?<command>\b`). Package-manager, service, and network
  patterns are not changed (they are already specific enough).
- **File changed:** `src/ansibleguard/detectors/shell_instead_of_module.py`

#### `unscoped-shell-variable`
- **Old precision:** ~29.7%
- **Root cause:** `COMMON_ENVIRONMENT` contained only 14 entries, missing many
  standard Linux/CI environment variables that are always available in Ansible
  shell tasks (`SUDO_USER`, `VIRTUAL_ENV`, `JAVA_HOME`, `CI`, proxy vars, XDG
  vars, locale variants, etc.).
- **Fix:** Expanded `COMMON_ENVIRONMENT` from 14 to 67 entries, covering POSIX
  core, locale/internationalisation, terminal, privilege-escalation, package
  managers, common CI platforms, proxy settings, and XDG base directories.
- **File changed:** `src/ansibleguard/detectors/partial_checklist.py`

#### `unnecessary-set-fact`
- **Fix:** Repository-aware analysis now searches cached YAML documents for
  semantic Jinja and conditional consumers before classifying a fact unused.
- **Status:** experimental, low confidence pending held-out labels.

---

### Test suite updates

Three test fixtures were updated to match the new, correct behaviour:

| Test file | Change |
|-----------|--------|
| `tests/test_paper_candidates.py` | `# TODO:` comment → task name `"TODO: …"` for `incomplete-task` fixture; removed `missing_role` assertion from `broken-role-dependency` test |
| `tests/test_review_checklist.py` | Updated `undocumented-complex-task` test to assert `count == 0` |
| `tests/test_sem_cohesion.py` | Updated `test_multiple_plays_mixed_result` to assert `count == 0` |

All 531 project tests pass.

---

### Supplementary P1/P2 fixes (added after initial plan)

#### Follow-up experimental-rule hardening (2026-08-14)

- Scoped repository symbols by inventory/file/role visibility and destination
  role parameters.
- Recognized explicit indirect variable consumers without guessing dynamic
  names.
- Followed registered-result inspection across task files within the same role.
- Unified read-only `command-instead-of-module` suppression across the internal
  detector and ansible-lint with auditable evidence.
- Required source-field integrity/identifier context before suppressing
  hex- or UUID-shaped GitLeaks findings, retaining unlabeled candidates.
- Generalized dispatcher recognition to import-only playbooks and task files.
- Made undocumented-complexity gates configurable and recorded a 3,197-file
  candidate-rate sensitivity audit under `study/validation-v7/`.

#### `unused-include-vars`
- **Old precision:** 19.2%
- **Root cause:** Cross-file analysis required — `include_tasks` consumers and role
  dependencies are invisible to single-file scanning.
- **Fix:** Re-enabled conservatively for static existing mapping includes only.
  It reports only when none of the included names is referenced in repository
  YAML; dynamic, unresolved, non-mapping, and partially used cases do not fire.
- **Status:** experimental, low confidence.
- **File changed:** `src/ansibleguard/detectors/include_vars.py`

#### `invalid-task-attribute-type`
- **Old precision:** 42.6%
- **Root cause:** `environment:` and `vars:` task attributes were type-checked even
  when the value is a Jinja template string (`"{{ env_map }}"`) — the template may
  resolve to a dict at runtime.
- **Fix:** Added early skip for any `isinstance(raw_val, str) and "{{" in raw_val`
  in the `detect_invalid_task_attribute_types()` loop.
- **File changed:** `src/ansibleguard/detectors/partial_checklist.py`

#### `unnecessary-abstraction`
- **Old precision:** 45.5%
- **Root cause:** Single-task blocks with `rescue:`, `always:`, `when:`, `tags:`,
  `become:`, `no_log:`, etc. are **semantically necessary** — those attributes can
  only be expressed at block level. The old code counted them as "unnecessary".
- **Fix:** Added `_BLOCK_JUSTIFYING_KEYS` frozenset. Any block containing at least
  one justifying key is not counted.
- **File changed:** `src/ansibleguard/detectors/unnecessary_abs.py`
- **Test updated:** `tests/test_unecessary_abs.py` — `test_rescue_nested_block_counted`
  asserts count == 1 (only the inner unjustified block), not 2.

#### `gitleaks/generic-api-key` — hex/UUID suppression
- **Old precision:** 42.6%
- **Root cause:** Pure hex strings of cryptographic digest lengths (32, 40, 56, 64,
  96, 128 hex chars = MD5, SHA-1, SHA-224, SHA-256, SHA-384, SHA-512) and UUID v4
  values were flagged as API keys. These are checksums, git SHAs, GPG fingerprints,
  and trace IDs, not secrets.
- **Fix:** Added `_HEX_ONLY_RE`, `_CRYPTO_HEX_LENGTHS`, and `_UUID_RE` to
  `_filter_known_noise()`. Matching hex strings are suppressed with reason
  `cryptographic-digest-not-api-key` or `uuid-not-api-key`.
- **File changed:** `src/ansibleguard/external/gitleaks.py`

---

### PR diff-mode validation study

A controlled PR validation study was conducted on 2026-08-13 to measure the
precision of `ansibleguard diff` mode. See `study/pr-validation-v1/` for full
methodology, per-finding labels, and raw results.

**Study design:** 5 forked real Ansible roles, controlled anti-pattern injections,
10 negative controls (integer values that must NOT fire).

**Results:**
- Controlled injection precision: **98.9%** [94.2%, 99.8%] naive Wilson 95% CI; clustered natural-PR validation remains required
- TP: 92, FP: 1 (large-playbook size threshold side effect)
- Negative controls: 10/10 passed
- SARIF uploaded to GitHub Code Scanning for all 5 repos

| Fork | PR | Precision |
|------|----|-----------|
| JedidiAymen/ansible-role-nginx | [PR #1](https://github.com/JedidiAymen/ansible-role-nginx/pull/1) | 95.0% (19/20) |
| JedidiAymen/ansible-role-docker | [PR #1](https://github.com/JedidiAymen/ansible-role-docker/pull/1) | 100.0% (20/20) |
| JedidiAymen/ansible-role-mysql | [PR #1](https://github.com/JedidiAymen/ansible-role-mysql/pull/1) | 100.0% (15/15) |
| JedidiAymen/ansible-role-security | [PR #1](https://github.com/JedidiAymen/ansible-role-security/pull/1) | 100.0% (23/23) |
| JedidiAymen/ansible-role-nodejs | [PR #1](https://github.com/JedidiAymen/ansible-role-nodejs/pull/1) | 100.0% (15/15) |

---

### Version bump

`pyproject.toml` and `src/ansibleguard.egg-info/PKG-INFO`: `0.0.2` → `0.0.4`

(Note: the egg-info had stale `0.0.2`; `version-0.0.3` was tracked in git history
and CHANGELOG only, not in `pyproject.toml`.)

## AnsibleGuard version 0.0.2

### Release purpose

Version 0.0.2 turns the earlier SARIF-validation prototype into a more
complete developer and empirical-validation tool. It keeps raw detector
evidence, adds overlap-aware canonical occurrences, makes repository and PR
selection auditable, improves false-positive behavior on real projects, and
presents findings consistently in files, summaries, diffs, SARIF, and GitHub
Actions.

### Main changes

- 66 catalogued rule IDs across 13 developer categories, with stable
  severity, confidence, remediation, provider, native-rule, and concept
  identity.
- Technical, fast developer, security, lint, quality, PR, frozen snapshot,
  research-core, extended, and review-range execution profiles.
- Versioned output contract with trust summary, diagnostics, raw findings,
  canonical occurrences, category/file-kind aggregation, collision-safe
  per-file bundles, reproducibility metadata, and redacted GitLeaks
  suppression evidence.
- Base/head comparison that distinguishes introduced, unchanged, fixed,
  moved, and uncertain occurrences; risk-first PR summaries; affected
  playbook rollups; actionable and complete SARIF views; and GitHub workflow
  annotations.
- Stronger Ansible parsing and file classification, nested task handling,
  repository-wide handler/variable/dependency evidence, deprecation metadata,
  and conservative fixes derived from real-repository false-positive review.
- Inclusive GitHub discovery, sequential attrition, frozen repository/file
  manifests, resumable GraphQL PR evidence, and final eligibility based on
  real production Ansible plus merged Ansible-changing PRs.
- Dual-review validation ledgers covering reported occurrences and clean-file
  negative units, with agreement and consensus summarization.

### Compatibility

The organized output under `summary/`, `raw/`, `canonical/`, `metadata/`,
`files/`, and `diff/` is the preferred contract. Root aliases and the original
mirrored per-file reports remain available as a migration surface. The
package and command remain named `ansibleguard`.

### Validation state

The implementation has automated unit/integration coverage and has been
exercised on real Ansible repositories and controlled PR comparisons. Static
findings remain review candidates, not automatically proven defects. Research
precision and false-negative claims require the frozen, stratified,
two-reviewer protocol documented in this repository. Hosted GitHub PR/SARIF
behavior is validated separately from local detector correctness.

### Primary references

- `OUTPUT_ARTIFACTS_CATEGORIES_AND_RULES_COMPLETE.md`
- `COMPLETE_RULE_REFERENCE_PROVENANCE_OVERLAP_AND_LIMITATIONS.md`
- `GITHUB_ZERO_TO_FINAL_SELECTION_AND_TEST_START.md`
- `PR_DEVELOPER_OUTPUT_AND_GITHUB_IMPLEMENTATION.md`
- `GITHUB_STUDY_PIPELINE_COMMANDS_AND_RESULTS.md`

## AnsibleGuard 0.0.1

This is the release note and technical decision record for the
`version-0.0.1` branch. It is intentionally the only new Markdown document
carried into this version; the refactoring branch's historical reports,
generated evaluation output, and overlapping design documents are not merged.

### Release goal

Version 0.0.1 keeps the SARIF-validation branch as the architectural base and
ports only detector fixes from `origin/refactoring` that are demonstrably
better and compatible with the current output contract.

The release remains a static-analysis CLI for Ansible repositories. It runs
AnsibleGuard detectors, GitLeaks, ansible-lint, and optional Git review checks,
then emits normalized raw findings, canonical occurrences, summaries,
diagnostics, metadata, text, CSV, JSON, and SARIF.

### Why SARIF validation is the base

The SARIF-validation line has the more complete platform:

- 66-rule catalog and explicit execution profiles;
- safe document classification;
- complete research file manifests;
- normalized raw findings and canonical occurrences;
- output contract v2 and JSON Schema validation;
- stable fingerprints and repository-relative SARIF paths;
- base/head PR comparison and annotations;
- GitLeaks and ansible-lint status separation;
- GitHub test, scan, SARIF upload, artifact, and policy workflows.

Merging the refactoring branch wholesale would remove or regress several of
these capabilities because the two branches evolved independently after their
common ancestor.

### Detector comparison

The refactoring branch contains several good ideas, but only three changes are
both clearly better and low-risk for this release.

#### Included: FQCN-aware coupling

The SARIF branch counted short-form `include_tasks` and `import_tasks` calls but
missed fully qualified forms such as:

```yaml
- ansible.builtin.include_tasks: setup.yml
- ansible.builtin.import_role:
    name: web
```

Version 0.0.1 recognizes short and `ansible.builtin` forms of playbook, task,
and role imports. Nested `block`, `rescue`, and `always` traversal remains
supported.

This improves the existing `high-coupling` rule without adding a new rule ID
or changing the output schema.

#### Included: rescue and always task metrics

The SARIF branch measured tasks under `block` but could omit executable leaf
tasks under `rescue` and `always`. Version 0.0.1 measures all three container
sections and preserves the enclosing play ID.

Compatibility is preserved for existing top-level task-file metrics: global
container entries retain their established representation, while containers
inside plays continue to report their executable leaf tasks.

This improves `large-task`, naming, and task-level metrics without changing
the rule catalog.

#### Included and strengthened: set_fact usage detection

The previous implementation treated a fact name appearing as any whitespace-
separated word as a use. For example, prose saying `my_var is documented here`
could hide a genuinely unused fact.

Version 0.0.1 recognizes:

- Jinja references such as `{{ my_var }}`;
- filters such as `{{ my_var | default(false) }}`;
- attribute access such as `{{ my_var.value }}`;
- bare Ansible condition expressions such as `when: my_var | bool`.

Ordinary prose no longer counts as a variable use. The port is stricter than
the refactoring implementation because it retains support for valid bare
conditional expressions.

#### Not included: separate insecure-permission subrules

The refactoring branch adds a large permission detector with separate rule IDs
for world-writable files/directories, SUID, SGID, recursive chmod, ACLs, shell
chmod, and combined risks.

The SARIF branch already has an `insecure-permissions` rule through its review
checklist detector. Importing the alternative now would duplicate concepts,
change profile membership and rule counts, and require new overlap policy and
manual calibration. The richer implementation is a useful future candidate,
but it should first be evaluated behind the existing concept ID or introduced
in a versioned catalog change.

#### Not included: dynamic deprecated-module cache/index

The refactoring branch dynamically indexes installed Ansible documentation and
caches deprecated module data. The SARIF branch already detects deprecated
module options using installed Ansible metadata plus project overrides.

The dynamic module detector may extend coverage, but it adds cache lifecycle,
environment-dependence, and reproducibility concerns. It should be compared
against the current implementation on a labeled corpus before integration.

#### Not included: new partially overlapping smells

The refactoring branch also contains rules for always-true/false conditions,
empty plays/tasks, loop guards, unused registrations, unsafe become, and other
checks. Several overlap the SARIF branch's checklist bundles or ansible-lint.
They are not included in 0.0.1 because this release is a compatibility and
quality release, not a catalog expansion.

#### Not included: generated evaluation campaign data

The refactoring checkpoint includes a very large 150-repository evaluation
tree and generated per-file reports. Generated scan output is not runtime code
and would make the release branch unnecessarily large. Reproducible scripts
and frozen manifests are preferable to committed bulk output.

### Trust and calibration implementation

The following five changes were implemented after the initial 0.0.1 detector
merge. This section is the exact implementation record.

#### 1. Structured failures and terminal states

The legacy per-file executor previously caught every `Exception`, printed a
message, and returned whatever partial objects happened to exist. A caller
could therefore count a file as structurally analyzed even when threshold
evaluation or legacy report generation had failed.

The implementation now:

- raises `FileAnalysisError` to the scan orchestrator in strict scan mode;
- records the exact failing stage, original cause, and whether metrics already
  existed;
- marks every source file `analyzed`, `skipped`, `partial`, or `failed`;
- writes internal failures as diagnostics with `status: analysis-error`;
- preserves independently collected GitLeaks/ansible-lint evidence when an
  internal file stage fails;
- catches failures in structural detectors, safe-source fallbacks, finding
  normalization, per-file reporting, review-range detectors, and repository
  source detectors;
- reports an all-failed run as `failed` and a mixed success/failure run as
  `partial` in `summary/report.json`;
- records terminal-state counts in `metadata/run.json` and the returned run
  result;
- adds `--fail-on analysis-error`;
- blocks GitHub scan policy on `analysis-error` as well as `tool-error`.

The legacy direct-call behavior remains available for compatibility, but the
CLI always enables strict propagation.

#### 2. Strict `.ansibleguard.yml` validation

Configuration loading no longer replaces malformed content with defaults.
Before providers or detectors run, every distinct nearest project
configuration used by selected files is validated.

Validation rejects:

- invalid YAML or a non-mapping root;
- unknown top-level, threshold, rule, or suppression keys;
- misspelled threshold names;
- non-numeric threshold values, including booleans;
- non-string values in credential, regex, known-variable, or suppression
  lists;
- invalid custom regular expressions;
- malformed deprecated-module option mappings;
- suppression IDs not present in the 66-rule catalog.

Configuration failures raise `DetectorConfigError`. The CLI prints the
actionable error and exits with code 2 before producing a misleading scan.

#### 3. Repository-wide symbol index

`src/ansibleguard/symbol_index.py` now builds one deterministic definition
index per source scan. It records variable name, provenance kind, repository-
relative source file, and line placeholder.

The index currently collects:

- role defaults and vars files;
- `group_vars`, `host_vars`, and environment variable files;
- play and task `vars`;
- `set_fact` definitions;
- registered result variables;
- custom loop variables;
- statically resolvable `vars_files` and `include_vars` mappings;
- configured runtime/extra variables from every effective project config.

`unguarded-variable` receives this index during both full structural analysis
and safe-source fallback analysis. Run metadata records definition count,
unique variable count, provenance-kind counts, and a deterministic SHA-256 of
the complete index.

The current resolver deliberately treats repository definitions as visible
across the repository. Provenance is retained so a later version can implement
role/play/include scope without changing the index format.

#### 4. Versioned labeled calibration workflow

The branch adds:

- `calibration/corpus-v1/` — small positive and negative Ansible fixtures;
- `calibration/labels-v1.csv` — eight versioned labels with case ID, file,
  stable rule ID, expected presence/absence, and rationale;
- `scripts/calibrate_detectors.py` — deterministic scan and scoring command;
- JSON and CSV calibration outputs containing individual case outcomes;
- per-rule and combined TP, FP, TN, FN, precision, recall, and specificity;
- a label-file SHA-256 in the report;
- CI execution of the labeled corpus after the unit suite.

The v1 corpus covers `high-coupling`, `unnecessary-set-fact`,
`unguarded-variable`, and `missing-tags`. Its current baseline is:

```text
TP=4  FP=0  TN=4  FN=0
precision=1.0  recall=1.0  specificity=1.0
```

This proves the calibration machinery and these eight controlled cases. It is
not evidence of general real-repository accuracy. The corpus must grow with
human-reviewed real examples before research publication.

#### 5. Typed orchestration stages

The CLI no longer owns target preparation and provider execution as anonymous
dictionary logic. `src/ansibleguard/runtime.py` introduces:

- `ScanContext` for normalized target, output, profile, and selected files;
- `ProviderResults` for external provider states;
- `FileStageResult` for terminal file state, parse/document status, findings,
  diagnostics, and structural completion;
- `RunResult` for the stable caller-facing run summary;
- `prepare_scan_context()` for selection/profile validation;
- `build_symbol_index_stage()` for configuration validation and indexing;
- `run_external_providers()` for GitLeaks/ansible-lint orchestration;
- a shared diagnostic constructor.

The remaining CLI function coordinates these explicit stages, project rules,
normalization, and the existing v2 writer. The output contract is preserved.

### Output contract

The developer workflow now adds first-class base/head and staged comparison.
`ansibleguard diff . --base origin/main` scans complete context, classifies
introduced/fixed/unchanged/moved/uncertain occurrences, records changed-line
metadata, groups the result by affected playbook, and emits
`diff/introduced.sarif` plus `diff/summary.md`. Normal scans also emit uniform
JSON under `files/<repository-relative-YAML-path>/`. Legacy per-file reports
remain for 0.0.1 compatibility. See `DIFF_PR_PLAYBOOK_IMPLEMENTATION.md` for
the exact implementation, policy, GitHub behavior, and limitations.

The supported integration entry point remains:

```text
ansibleguard-output/
├── summary/
│   ├── report.json
│   ├── summary.csv
│   └── diagnostics.json
├── raw/
│   ├── findings.json
│   ├── findings.csv
│   └── findings.txt
├── canonical/
│   ├── occurrences.json
│   ├── occurrences.csv
│   ├── occurrences.txt
│   └── findings.sarif
└── metadata/
    ├── run.json
    ├── file-selection.json
    └── review-metrics.json
```

Use raw findings for detector evaluation and provider audit. Use canonical
occurrences for developer-facing issue counts and SARIF. Always inspect
diagnostics before trusting a scan.

### Version scope

Version identifiers in package metadata and SARIF are set to `0.0.1`.

No rule ID, profile partition, output schema version, file-selection rule,
external provider identity, or PR comparison identity is changed. The failure
policy is extended with `analysis-error`, and run/file statuses are more
precise.

### Verification requirements

Before pushing the branch:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m ansibleguard.cli --help
git diff --check
```

The focused regression tests must cover:

- short and FQCN task/role imports;
- `block`, `rescue`, and `always` leaf-task metrics;
- plain-text fact-name false positives;
- Jinja and bare-condition fact uses;
- SARIF tool version;
- strict configuration rejection;
- failed and partial file/run states;
- symbol-index provenance and resolution;
- calibration label validation and scoring;
- CI blocking of internal analysis failures.

### Known limitations and next work

- Some individual legacy detectors still catch their own exceptions and return
  sentinel values before the orchestrator can observe the original cause. They
  should be converted incrementally to typed detector results.
- The symbol index has repository-wide visibility but not a complete Ansible
  precedence/scope graph for dynamic includes, inventory plugins, collections,
  or command-line extra-vars.
- The labeled corpus is intentionally small and synthetic; stratified manual
  real-repository calibration is still required.
- The provisional eight-rule research core is not a publishable conclusion
  until labeling and supervisor approval are complete.
- Heavy NLP dependencies should eventually load lazily or become optional.
- Detailed permission subcategories and dynamic module deprecation should be
  evaluated as candidates for the next version, not merged without evidence.

### Release decision

Version 0.0.1 is deliberately small: keep the proven SARIF/research platform,
take three focused detector correctness improvements, add regression coverage,
and exclude overlapping rules, generated datasets, and documentation bulk.
This gives the branch a reviewable change set and avoids turning a first
version into an untestable merge of two divergent architectures.
