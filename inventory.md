# AnsibleChecklist — Implemented Smell Inventory

> **Branch:** `sarif-validation-support`
> **Last updated:** 2026-07-18
> **Total smells:** 60 (58 internal rules + GitLeaks + ansible-lint)
> **Profiles:** all 60 rules are assigned to core, extended, review, or external families; see `RESEARCH_PROFILES_IMPLEMENTATION.md`.
>
> **Test suite:** 163 passing; no environment failures

---

## Overview

This document catalogs every IaC code smell and security smell currently implemented in the AnsibleChecklist static analysis tool. Each entry includes the detection strategy, evidence source, confidence level, and known false positive risks — intended as a reference for research validation and future extension.

Smells are organized by category, matching the severity classification used in the SARIF output and findings pipeline.

---

## Severity Legend

| Severity | Meaning | Use in Pipeline |
|----------|---------|-----------------|
| **error** | Active security vulnerability or correctness bug. Should block CI/deployment. | Red in SARIF; blocks PR if configured |
| **warning** | Likely maintainability or correctness issue. Should be reviewed. | Yellow in SARIF; surfaced in summary.csv |
| **note** | Style recommendation or informational finding. Low consequence. | Blue in SARIF; informational only |

---

## 🔴 SECURITY SMELLS (5)

These detect active security vulnerabilities — hardcoded secrets, credential exposure, disabled TLS validation, insecure file permissions, and broken handler references.

### 1. Hardcoded Credentials

| Field | Value |
|-------|-------|
| **Detector** | `external/gitleaks.py` (GitLeaks wrapper) |
| **Severity** | error |
| **Evidence** | GitLeaks rule set (G001–G010); OWASP A07:2021 (Identification and Authentication Failures); CIS Benchmark §3.1 |
| **Strategy** | Runs `gitleaks detect --no-git` as a subprocess against the target file. GitLeaks uses entropy analysis and pattern matching (regex) to find API keys, tokens, private keys, database passwords, etc. |
| **Confidence** | High — GitLeaks is a mature, widely-adopted tool |
| **FP Risk** | Low — entropy thresholds + pattern matching reduce noise; false positives on example/test values possible |
| **Limitations** | Binary must be installed; per-file scanning is slower than repo-level; Windows binary path fix applied |

### 2. Credentials Leaking in Log

| Field | Value |
|-------|-------|
| **Detector** | `detectors/credentials_leaking_in_log.py` |
| **Severity** | error |
| **Evidence** | Ansible `no_log` parameter documentation; Red Hat Ansible security best practices; OWASP A04:2021 (Insecure Design) |
| **Strategy** | Walks all leaf tasks (block/rescue/always recursion). Serializes each task to YAML. Checks for 14 sensitive keywords (`password`, `secret`, `api_key`, `token`, `access_key`, `client_secret`, `passwd`, `credential`, `private_key`, `ssh_key`, `pwd`, `auth_token`, `db_password`, `admin_password`). Flags if keyword present AND `no_log` not set (task-level or inherited from enclosing play). |
| **Confidence** | High — structural keyword search + per-play no_log inheritance |
| **FP Risk** | Low — only flags when sensitive keyword present AND no_log absent; variable values containing keyword may trigger |
| **Limitations** | String-match on YAML dump; play-level `no_log` inheritance tracked per-task via `_inherited_no_log` marker |

### 3. Missing validate_certs

| Field | Value |
|-------|-------|
| **Detector** | `detectors/missing_validate_certs.py` |
| **Severity** | warning |
| **Evidence** | Ansible `uri` module docs (parameter `validate_certs`); Ansible `get_url` module docs; CIS TLS/SSL best practices |
| **Strategy** | Walks all leaf tasks. Checks for `uri:` or `get_url:` modules (including `ansible.builtin.*` FQCN forms). If `validate_certs` is explicitly set to `false`, `"false"`, `no`, `False`, `No`, or `NO`, flags the task. |
| **Confidence** | High — exact match on documented parameter |
| **FP Risk** | Low — only flags explicit disable; variable-based values like `"{{ verify_ssl }}"` are not flagged (cannot statically determine) |
| **Limitations** | Internal self-signed certificates are a legitimate use case but still flagged; variable-based values not resolved |

### 4. Insecure File Permissions

| Field | Value |
|-------|-------|
| **Detector** | `detectors/review_checklist.py::detect_insecure_permissions()` |
| **Severity** | error |
| **Evidence** | CIS Benchmark §6.1 (file permissions); OWASP A05:2021 (Security Misconfiguration); POSIX file permission model (`stat.S_IWOTH`, `stat.S_IROTH`) |
| **Strategy** | Walks all tasks. Checks `mode` on common file-managing modules, including FQCN forms. Parses octal modes to permission bits and recognizes symbolic grants to `other`/`all`. World-write is always reported; world-read is reported for sensitive tasks. |
| **Confidence** | Medium — octal parsing robust; sensitive-keyword heuristic for world-readable detection |
| **FP Risk** | Low — bitmask and supported symbolic-mode analysis are deterministic |
| **Limitations** | Variable-computed modes cannot be resolved; module coverage focuses on common file-managing modules. |

### 5. Missing Handlers (notify → missing)

| Field | Value |
|-------|-------|
| **Detector** | `detectors/handler_issues.py` |
| **Severity** | error |
| **Evidence** | Ansible handlers documentation: `notify` must reference an existing handler name; notification to missing handler silently fails at runtime |
| **Strategy** | Collects all handler names from `handlers:` sections. Collects all `notify:` values (strings and lists) from all tasks (including handlers that notify other handlers). Cross-references: any notify not in handlers → missing. Builtin patterns (`Restart X`, `Reload X`) are excluded (likely from included roles). |
| **Confidence** | High — exact name matching |
| **FP Risk** | Medium — handlers defined in included task files or imported playbooks are invisible to single-file analysis |

---

## 🟡 CORRECTNESS SMELLS (3)

These detect logic issues that silently produce wrong behavior — duplicate keys discarding data, missing boolean filters causing truthiness bugs, and facts silently overwritten.

### 6. Overridden Keys

| Field | Value |
|-------|-------|
| **Detector** | `detectors/overriden_keys.py` |
| **Severity** | error |
| **Evidence** | YAML specification §3.2.1: duplicate mapping keys; Ansible YAML silently keeps last value |
| **Strategy** | Uses ruamel.yaml round-trip loader for real parse tree. Walks structure to find task boundaries via line numbers. Within each task span, tracks `(indent_depth, key)` pairs from the source text. Keys at the same depth appearing multiple times are flagged. Depth-awareness prevents cross-depth false positives (e.g., a task's `name:` vs a nested module's `name:`). |
| **Confidence** | High — structural detection via ruamel parse tree |
| **FP Risk** | Low — depth-bucketing eliminates the most common false positive (same key name at different nesting levels) |
| **Limitations** | Text-based line scanning within task span; YAML comments or blank lines between duplicates handled correctly |

### 7. Missing Bool Filter

| Field | Value |
|-------|-------|
| **Detector** | `detectors/filters_for_comparison.py` |
| **Severity** | warning |
| **Evidence** | Ansible Jinja2 truthiness documentation: `"false"` (string) is truthy; `| bool` filter ensures correct boolean evaluation |
| **Strategy** | Extracts all `when:` conditions (recursing into block/rescue/always). Splits on `and`/`or` operators. For each sub-expression: if not a comparison (`==`, `!=`, `<`, `>`), not a literal (`true`/`false`), and doesn't contain `| bool` → flagged. |
| **Confidence** | Medium — regex-based condition parsing |
| **FP Risk** | Medium — `re.split()` approach fragile for complex Jinja2 expressions with nested parentheses, filters, and multiline `when:`; bare-boolean `when: true` handled correctly |
| **Limitations** | Does not parse full Jinja2 expression tree; may miss or misclassify complex conditional expressions |

### 8. Overriding Facts

| Field | Value |
|-------|-------|
| **Detector** | `detectors/overriding_facts.py` |
| **Severity** | warning |
| **Evidence** | Ansible `set_fact` documentation: variable reassignment silently overwrites prior value |
| **Strategy** | Collects all `(fact_name, fact_value)` pairs from `set_fact` calls in order. Compares each against every later occurrence via upper-triangular pairwise comparison: same name + different value → flagged. |
| **Confidence** | Medium — correct pairwise comparison; same value reassignment not flagged |
| **FP Risk** | Low — two `set_fact` with different values for the same name is almost always unintentional |
| **Limitations** | Does not consider conditional execution paths; facts in mutually exclusive `when:` branches both flagged |

---

## 🟠 MAINTAINABILITY SMELLS (7)

These detect structural issues that make playbooks harder to maintain, test, and reuse over time.

### 9. Large Playbook

| Field | Value |
|-------|-------|
| **Detector** | `detectors/detect_large_playbook.py` → `smells.py::assess_code_smells()` |
| **Severity** | warning |
| **Evidence** | Ansible best practices: split large playbooks into smaller, role-based ones; `ansiblemetrics` library (`LinesCode`, `LinesComment`) |
| **Strategy** | Computes `LOC_playbook` (code + comment lines), `num_plays`, `avg_play_size`, `num_nested_tasks_playbook`. Any metric exceeding its threshold in `thresholds.csv` triggers the smell. Threshold: `LOC_playbook > 110`, `num_plays > 4`, etc. |
| **Confidence** | High — threshold-based with configurable values |
| **FP Risk** | Low — thresholds are adjustable via `thresholds.csv` |

### 10. Large Play

| Field | Value |
|-------|-------|
| **Detector** | `detectors/detect_large_play.py` → `smells.py::assess_code_smells()` |
| **Severity** | warning |
| **Evidence** | Ansible best practices: focused plays; each play should address one concern |
| **Strategy** | Per-play metrics: `LOC_play` (YAML dump line count), `num_tasks_in_play` (recursing into block/rescue/always), `avg_task_play`. Flagged if any exceeds threshold. Threshold: `LOC_play > 50`, `num_tasks_play > 7`. |
| **Confidence** | High — uses ruamel.yaml for accurate line numbers |
| **FP Risk** | Low — threshold-based |

### 11. Large Task

| Field | Value |
|-------|-------|
| **Detector** | `detectors/large_task.py` → `smells.py::assess_code_smells()` |
| **Severity** | warning |
| **Evidence** | Single-responsibility principle applied to Ansible tasks; a task should do one thing |
| **Strategy** | Serializes each leaf task to YAML, counts lines. Block/rescue/always wrappers are NOT counted — only their children. Recurses into all nested sections. Threshold: `LOC_task > 15`. |
| **Confidence** | High — uses ruamel.yaml for line tracking |
| **FP Risk** | Low — threshold-based |

### 12. Complex Playbook

| Field | Value |
|-------|-------|
| **Detector** | `smells.py::assess_code_smells()` (composite rule) |
| **Severity** | warning |
| **Evidence** | Ansible architecture guide: composite size + coupling complexity metric |
| **Strategy** | Logical OR of four conditions: (large LOC AND many plays), (large LOC AND many tasks), (many imports > `Num_Imports` threshold), (many roles > `Num_Roles` threshold). |
| **Confidence** | Medium — composite rule has multiple thresholds; empirically calibrated |
| **FP Risk** | Low — composite check reduces single-metric false positives |

### 13. Insufficient Modularization

| Field | Value |
|-------|-------|
| **Detector** | `smells.py::assess_code_smells()` (AND condition) |
| **Severity** | warning |
| **Evidence** | Ansible roles documentation; Red Hat reference architectures recommend splitting large monolithic playbooks |
| **Strategy** | AND of two conditions: `LOC_playbook > threshold` AND `num_plays > threshold`. Flags the "everything in one file" anti-pattern. |
| **Confidence** | Medium — two-condition AND reduces false positives |
| **FP Risk** | Low — requires both conditions simultaneously |

### 14. Duplicated Code

| Field | Value |
|-------|-------|
| **Detector** | `detectors/duplicate_code.py` |
| **Severity** | warning |
| **Evidence** | DRY principle; code clone detection literature; Ansible `import_tasks` for shared task files |
| **Strategy** | Collects all leaf tasks (block/rescue/always recursion). Strips the `name` field. Serializes remaining parameters to canonical string (`str(sorted(task_params.items()))`). Counts duplicates via `collections.Counter`. |
| **Confidence** | Medium — string serialization is sensitive to dict key ordering |
| **FP Risk** | Medium — two tasks with identical module+params but different intent flagged; dict/list ordering differences may create false negatives |
| **Limitations** | Unnamed tasks now handled (fixed); fuzzy matching not implemented |

### 15. High Playbook Coupling

| Field | Value |
|-------|-------|
| **Detector** | `detectors/high_coupling.py` → `smells.py::assess_code_smells()` |
| **Severity** | warning |
| **Evidence** | Ansible architecture guide: minimize imports and role dependencies |
| **Strategy** | Counts `import_playbook`, `import_tasks`, `include_tasks`, `include_role`, `import_role` (including FQCN forms like `ansible.builtin.include_tasks`) at both play level and nested in tasks. Counts `roles:` entries. Flagged if imports > threshold or roles > threshold. |
| **Confidence** | Medium — structural key matching; FQCN forms now covered |
| **FP Risk** | Low — counts are objective; threshold determines sensitivity |

---

## 🟢 STYLE SMELLS (9)

These are maintainability recommendations — not bugs, but practices that improve readability, debuggability, and operational control.

### 16. Unnamed Play

| Field | Value |
|-------|-------|
| **Detector** | `detectors/unnamed_play.py` |
| **Severity** | note |
| **Evidence** | Ansible output readability: unnamed plays show as `PLAY [hosts:...]` instead of `PLAY [Descriptive name]` |
| **Strategy** | Iterates all plays (dicts with `hosts:` or `tasks:`). Checks if `name` is None, empty, or whitespace-only. Uses ruamel.yaml for real line numbers. |
| **Confidence** | High — direct check |
| **FP Risk** | Low |

### 17. Unnamed Task

| Field | Value |
|-------|-------|
| **Detector** | `detectors/unnamed_tasks.py` |
| **Severity** | note |
| **Evidence** | Ansible output: unnamed tasks show module path instead of descriptive name |
| **Strategy** | Uses `large_task.py::calculate_metrics_task()` full task list. Any task with `task_name == "Unknown"` flagged. |
| **Confidence** | High |
| **FP Risk** | Low |

### 18. Long Task Name

| Field | Value |
|-------|-------|
| **Detector** | `smells.py::assess_code_smells()` from `large_task.py` metrics |
| **Severity** | note |
| **Evidence** | Ansible output formatting: long names truncate in terminal; concise names improve scanability |
| **Strategy** | Task name length > `task_name_len` threshold (default: 75 characters). |
| **Confidence** | High — length-based threshold |
| **FP Risk** | Low — some descriptive names legitimately exceed threshold |

### 19. Inconsistent Naming Convention

| Field | Value |
|-------|-------|
| **Detector** | `smells.py::assess_code_smells()` from task/play `special_chars` metric |
| **Severity** | note |
| **Evidence** | Team convention consistency; Unicode-aware special character count |
| **Strategy** | Counts non-letter, non-digit, non-whitespace characters in task/play names. Flagged if `special_chars > 3` (threshold in `thresholds.csv`). |
| **Confidence** | Medium — heuristic; some characters may be intentional (version numbers, separators) |
| **FP Risk** | Medium — names with hyphens, dots, or version numbers legitimately contain special chars |

### 20. Duplicated Task Names

| Field | Value |
|-------|-------|
| **Detector** | `detectors/duplicate_task_names.py` |
| **Severity** | note |
| **Evidence** | Ansible output: identical task names make it impossible to distinguish which instance ran |
| **Strategy** | Collects all task names from `calculate_metrics_task()`. Counts frequencies via `collections.Counter`. Returns count of names appearing >1. |
| **Confidence** | High — exact string match |
| **FP Risk** | Low — identical names in different plays may be intentional but still reduce clarity |

### 21. Missing File Extension

| Field | Value |
|-------|-------|
| **Detector** | `detectors/files_extensions.py` |
| **Severity** | note |
| **Evidence** | Ansible module behavior: file extension determines template rendering, copy behavior, etc. |
| **Strategy** | Checks `src`, `file`, `cmd`, `path` attributes on all leaf tasks (block/rescue/always recursion). Strings not matching `\.\w+$` (no file extension) flagged. |
| **Confidence** | Medium — limited attribute coverage |
| **FP Risk** | Medium — `cmd` attribute often contains shell commands, not file paths; `Dockerfile` (no extension) flagged correctly but module attributes may be non-file strings |
| **Limitations** | Only checks 4 attribute names; misses `creates`, `removes`, `dest`, and module-specific attributes |

### 22. Unnecessary Abstraction

| Field | Value |
|-------|-------|
| **Detector** | `detectors/unnecessary_abs.py` |
| **Severity** | note |
| **Evidence** | Code readability: single-task `block:` wrappers add nesting without structural benefit |
| **Strategy** | Recursively walks all `block`/`rescue`/`always` sections. Any block with exactly 1 child flagged. |
| **Confidence** | Medium — flag is correct but legitimate use cases exist (block for `delegate_to`, `run_once`) |
| **FP Risk** | Low — single-task blocks used for attribute inheritance are intentionally flagged |

### 23. Unnecessary set_fact

| Field | Value |
|-------|-------|
| **Detector** | `detectors/set_fact.py` |
| **Severity** | note |
| **Evidence** | Dead code detection: unused variables suggest incomplete refactoring |
| **Strategy** | Finds all `set_fact` assignments. Scans all string values for Jinja2 references (`{{ var }}`, `{{var}}`, `{{ var | filter }}`). Unused = `set_facts - used_facts`. |
| **Confidence** | Medium — Jinja2 string-matching |
| **FP Risk** | Medium — indirect references (`hostvars[var]`) not detected; variables used in included files invisible |

### 24. Unused Include Vars

| Field | Value |
|-------|-------|
| **Detector** | `detectors/include_vars.py` |
| **Severity** | note |
| **Evidence** | Dead dependency: `include_vars` loading unused data |
| **Strategy** | Finds `include_vars` directives, loads referenced vars files, extracts top-level keys. Scans playbook for Jinja2 references with filter chain support. Unreferenced vars flagged. |
| **Confidence** | Medium — regex-based variable detection with filter chain support |
| **FP Risk** | Medium — nested variable keys not tracked; vars used via `hostvars` or indirect lookup not detected |

---

## 🔵 SEMANTIC SMELLS (2)

These use NLP (spaCy word vectors) to detect semantic cohesion issues. Confidence is lower than structural detectors.

### 25. Incohesive Playbook

| Field | Value |
|-------|-------|
| **Detector** | `detectors/sem_cohesion.py` |
| **Severity** | note |
| **Evidence** | Software cohesion literature; semantic similarity as a proxy for logical grouping |
| **Strategy** | Lemmatizes all play names and task names. Loads spaCy `en_core_web_lg` model. Computes pairwise cosine similarity for all play-name pairs and all task-name pairs. Averages to one score. Below `similarity` threshold → incohesive. Non-English/OOV names result in `None` (unmeasurable), not false "perfectly cohesive". Tracks vector availability per-group (plays, tasks independently). |
| **Confidence** | Low — spaCy similarity on short technical names is inherently approximate |
| **FP Risk** | High — semantically cohesive but lexically diverse names score low; domain-specific terms may lack good vectors |
| **Limitations** | O(n²) pairwise comparisons; large model (~800MB) loaded at module level; per-group vector tracking prevents cross-group masking |

### 26. Incohesive Play

| Field | Value |
|-------|-------|
| **Detector** | `detectors/incohesive_plays.py` |
| **Severity** | note |
| **Evidence** | Play-level semantic cohesion; tasks within a play should be semantically related |
| **Strategy** | Same spaCy approach as Incohesive Playbook, but scoped per-play. For each play, compares its task names pairwise. Count of plays below `similarityPlays` threshold returned. OOV task names: play skipped (unmeasurable). |
| **Confidence** | Low — same NLP limitations |
| **FP Risk** | High — same reasons as Incohesive Playbook |

---

## 🟣 NEW DETECTORS (4 — refactoring branch)

These were added in the current development cycle and are not present on the `lemon` or `main` branches.

### 27. Deprecated Modules

| Field | Value |
|-------|-------|
| **Detector** | `detectors/deprecated_modules.py` |
| **Severity** | warning |
| **Evidence** | Ansible porting guides; Ansible module index; 40+ documented deprecation/alias mappings |
| **Strategy** | Walks all leaf tasks. Checks each task's module key (filtered from meta-keys) against a curated deprecated modules map. Provides actionable replacement suggestion. Separately flags short-name modules that should use FQCN (aliased, not deprecated). |
| **Confidence** | High — manual mapping curated from official docs |
| **FP Risk** | Low — only flags modules in the curated deprecated list |
| **Limitations** | Mapping must be manually updated for new Ansible releases; some short-name modules flagged as aliased that are still officially supported |

### 28. Missing Tags

| Field | Value |
|-------|-------|
| **Detector** | `detectors/missing_tags.py` |
| **Severity** | note |
| **Evidence** | Ansible tags documentation; `--tags`/`--skip-tags` for operational control |
| **Strategy** | Walks all leaf tasks. Flags tasks without `tags:` attribute. Respects tag inheritance: tasks inside a tagged `block:`/`rescue:`/`always:` wrapper are not flagged (tags propagate to children). |
| **Confidence** | High — structural check with inheritance |
| **FP Risk** | Low — simple playbooks legitimately untagged; this is a note, not a warning |

### 29. Shell Instead of Module

| Field | Value |
|-------|-------|
| **Detector** | `detectors/shell_instead_of_module.py` |
| **Severity** | warning |
| **Evidence** | Ansible best practices: "Always prefer modules over running raw commands"; module index |
| **Strategy** | Walks all leaf tasks using `shell:` or `command:`. Pattern-matches the command string against 25 known patterns (package managers, service control, file operations, downloads, version control, archives, user management, cron). Provides the recommended native Ansible module. Skips complex commands with pipes, redirects, `&&`, `||`, loops, or conditionals. |
| **Confidence** | Medium — string pattern matching is inherently heuristic |
| **FP Risk** | Medium — one-off admin tasks legitimately use shell; complex commands with pipes/redirects excluded; some module equivalents lack exact parameter parity |
| **Limitations** | Does not parse shell semantics; variable-interpolated commands may not match patterns; some patterns (e.g., `rm`) can match legitimate non-file-removal commands |

### 30. Unused Handlers

| Field | Value |
|-------|-------|
| **Detector** | `detectors/handler_issues.py` |
| **Severity** | warning |
| **Evidence** | Ansible handler documentation: handlers execute only when notified; un-notified handler is dead code |
| **Strategy** | Collects all handler names from `handlers:` sections across all plays. Collects all `notify:` values from all tasks. Cross-references: handler name not in notify set → unused. |
| **Confidence** | High — exact name matching |
| **FP Risk** | Low — handlers notified from included task files are invisible but that's a multi-file analysis limitation, not a false positive per se |

---

## PAPER-DERIVED STATIC DETECTORS (9)

These checks were selected from the configuration-smell paper mapping because
they have defensible static Ansible equivalents. Their shared implementation is
documented fully in `PAPER_SMELLS_IMPLEMENTATION.md`.

### 31. Complex Expression

Scores operators, comparisons, filters, grouping, indexing, and length in
Jinja/conditional expressions. A score of 6 or more produces a warning.

### 32. Incomplete Task

Reports source lines containing unresolved `TODO`, `FIXME`, `HACK`, or `XXX`
markers.

### 33. Long Statement

Reports physical YAML source lines longer than 120 characters as notes.

### 34. Unstructured Module

Checks role entry points and existing standard role directories for a
`main.yml`/`main.yaml` file. One anchor file represents each role.

### 35. Empty Abstraction

Reports empty YAML documents and explicit empty `block`, `rescue`, or `always`
sections.

### 36. Excessive Nesting

Reports tasks nested below more than three `block`/`rescue`/`always` wrappers.

### 37. Missing Abstraction

Reports files with more than ten leaf tasks and no role or task-include usage.

### 38. Broken Role Dependency

Builds the local `roles/*/meta/main.yml` dependency graph and reports missing
local dependencies, self-dependencies, and cycles as correctness errors.

### 39. Unguarded Variable

Reports Jinja references without a visible definition or `default`/`d`/`is
defined` guard. Runtime and externally supplied variables can cause false
positives, so this rule is a warning.

---

## ADDITIONAL CODE-REVIEW CHECKS (6)

The live insecure-permissions rule is already catalogued as smell 4. Six other
checks from the same implementation cycle are added here. Full algorithms and
limitations are in `REVIEW_CHECKLIST_IMPLEMENTATION.md`.

### 40. Default Credentials

Reports credential-like keys using conservative well-known default values.

### 41. Non-idempotent Command

Reports recognized mutating command tasks without `creates`, `removes`,
`changed_when`, or check-mode guards.

### 42. Silent Error Suppression

Reports ignored/disabled failures whose results are not registered for later
warning or recovery handling.

### 43. Redundant Default Value

Compares role defaults with exact play/task vars and `set_fact` assignments.

### 44. Shell Environment Export

Reports shell `export` statements that should use Ansible's `environment:`
mapping.

### 45. Undocumented Complex Task

Reports structurally complex tasks without an immediately preceding source
comment.

---

## PARTIAL-COVERAGE AND GIT REVIEW RULES (11)

These rules strengthen partially automatable criteria and add one-per-project
latest-commit checks. See `PARTIAL_AND_REVIEW_METADATA_IMPLEMENTATION.md`.

### 46. Unused Registered Variable

Reports `register` results never referenced elsewhere in the file.

### 47. Unscoped Shell Variable

Reports shell variable references absent from task/play environment mappings.

### 48. Invalid Task Attribute Type

Validates universal boolean, integer, mapping, and tag task attributes.

### 49. Invalid Numeric Value

Validates literal port ranges and nonnegative timing/retry controls.

### 50. Missing Release Note

Checks whether the complete base-to-head review range changes production YAML
without adding a release note.

### 51. Missing Bug Reference

Checks bug/fix commit messages for a recognized bug-number reference.

### 52. Invalid Depends-On Reference

Validates present dependency trailers as review URLs or Gerrit Change-Ids.

### 53. Commit Message Format

Checks subject length, blank separation, and body line length.

### 54. Removed Copyright Notice

Compares modified file headers at the committed review base and head.

### 55. Missing Test Update

Requires test/Molecule co-changes when production YAML changes.

### 56. Untested Override Change

Requires test co-changes when defaults or variable sources change.

---

## FORMERLY MISSING CHECKLIST RULES (3)

Full algorithms and limitations are in
`MISSING_CHECKLIST_IMPLEMENTATION.md`.

### 57. Variable Use Before Definition

Reports a Jinja/condition reference to a registered result or `set_fact` value
when a later task in the same linear section is its only visible definition.

### 58. Unexpected Task Location

Reports invalid role-file document shapes, plays embedded under roles, and
handler-only `listen` attributes placed under tasks.

### 59. Deprecated Module Option

Compares supplied module arguments with installed `ansible-doc` deprecation
metadata and configured project overrides.

---

## 🔧 EXTERNAL TOOLS (1)

### 60. Design Smells (ansible-lint)

| Field | Value |
|-------|-------|
| **Detector** | `external/ansible_lint.py` (ansible-lint wrapper) |
| **Severity** | warning |
| **Evidence** | Official ansible-lint rule set (ANSIBLE0001–ANSIBLE0017, experimental rules, custom rules) |
| **Strategy** | Runs `ansible-lint -f json` as a subprocess against the target file. Parses JSON output. Each lint finding becomes a SARIF result with the rule ID and message. |
| **Confidence** | High — delegates to established community linter |
| **FP Risk** | Low — ansible-lint rules are well-tested; platform-dependent (needs `grp` on Unix) |
| **Limitations** | Requires ansible-lint installed; on Windows, some rules fail due to missing Unix modules (`grp`) |

---

## Summary Statistics

### By Severity

| Severity | Count | Smells |
|----------|-------|--------|
| **error** | 10 | Security/correctness findings that can cause direct harm or silent failure |
| **warning** | 31 | Maintainability, reliability, and likely correctness risks |
| **note** | 19 | Style, documentation, naming, and lower-confidence semantic findings |

### By Category

| Category | Count |
|----------|-------|
| Security | 5 |
| Correctness | 12 |
| Maintainability | 15 |
| Style | 11 |
| Structure | 4 |
| Cohesion (NLP) | 2 |
| Reliability | 1 |
| Documentation | 4 |
| Testing | 2 |
| Dependencies | 1 |
| Legal | 1 |
| Compatibility | 1 |
| Lint (external) | 1 |

### By Confidence

| Level | Examples |
|-------|----------|
| **High** | Exact structural checks, dependency cycles, duplicate keys, explicit unsafe modes |
| **Medium** | Pattern matching for commands, variables, credentials, documentation, and file extensions |
| **Low** | NLP cohesion on short or out-of-vocabulary names |

### By False Positive Risk

| Level | Examples |
|-------|----------|
| **Low** | Exact-match, structural, and direct security-property detectors |
| **Medium** | Command, variable, default-value, and documentation heuristics |
| **High** | NLP semantic cohesion and intent-dependent interpretations |

---

## Detection Pipeline Integration

Every smell follows this integration path:

```
detector.py                  # Detection logic, returns (count, details)
  ↓
parser.py::mainn()           # Calls detector, stores in main_metrics dict
  ↓
smells.py::assess_code_smells()  # Applies thresholds, builds result dict
  ↓
report/findings.py           # RULE_CATALOG entry + build_findings_list()
  ↓
report/csv_writer.py         # CSV column + value
report/sarif_writer.py       # SARIF 2.1.0 document for GitHub Code Scanning
report/text_writer.py        # Human-readable TXT report
```

---

## Test Coverage

| Metric | Value |
|--------|-------|
| Test modules | 44 |
| Total tests | 153 |
| Passing | 153 |
| Environment failures | 0 |

---

*This inventory is maintained alongside the codebase. For implementation details, see each detector's source file in `src/ansibleguard/detectors/`. For integration details, see `ARCHITECTURE.md` and `PROJECT_STATUS.md`.*
