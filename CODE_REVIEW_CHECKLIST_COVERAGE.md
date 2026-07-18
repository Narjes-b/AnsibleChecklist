# Coverage of the IaC code-review checklist

Source reviewed: *Towards Understanding Code Review Practices for
Infrastructure-as-Code: An Empirical Study on OpenStack Projects* (Empirical
Software Engineering, 2025), especially Table 7.

Local source: [the reviewed PDF](Literature_review/Towards_understanding_code_review_practices_for_in.pdf).

The paper presents 38 review criteria grouped into seven topics. This document
compares those criteria with the code that is actually active under
`src/ansibleguard/`. Documentation claims alone are not counted as an
implementation.

## Status legend

| Status | Meaning |
|---|---|
| **Yes** | A live detector or integrated external tool directly checks the criterion. |
| **Partial** | Existing checks cover a useful subset, but cannot establish the full criterion. |
| **No** | No active check currently implements the criterion. |

## Summary

| Coverage | Criteria |
|---|---:|
| **Yes** | 15 |
| **Partial** | 18 |
| **No** | 5 |
| **Total** | 38 |

Therefore, the complete paper checklist is **not yet implemented**. Fifteen
items have direct coverage, eighteen have partial coverage, and five are
missing.

> Note: the prose surrounding Table 7 numbers Logic as T1, while Table 7 starts
> with Documentation as T1. This report uses the topic names, not those
> inconsistent topic numbers.

## Complete mapping

| # | Paper topic | Checklist criterion | Implemented? | Current coverage or gap |
|---:|---|---|---|---|
| 1 | Documentation | Add a release note for the change | **Partial** | Git-aware `missing-release-note` requires a release-note file when the review range changes production YAML; it cannot know whether an internal change is intentionally exempt. |
| 2 | Documentation | Add a bug report for newly detected bugs | **Partial** | `missing-bug-reference` requires bug/fix commits to reference a tracker number, but it cannot create or verify the external report. |
| 3 | Documentation | Add explanatory inline comments | **Partial** | `undocumented-complex-task` requires a nearby comment for structurally complex tasks, but comment quality and simple-task documentation remain human judgments. |
| 4 | Documentation | Record `Depends-On` information in the commit message | **Partial** | Present `Depends-On` trailers are validated as review URLs or Gerrit Change-Ids; whether a missing trailer was required cannot be inferred. |
| 5 | Documentation | Follow the standard commit-message format | **Yes** | `commit-message-format` checks 50-character subjects, blank body separation, and 72-character body lines. |
| 6 | Logic | Verify assigned parameter values | **Partial** | `invalid-numeric-value`, `ansible-lint`, `missing-validate-certs`, and security rules validate objective subsets; service-specific semantic correctness remains runtime/context dependent. |
| 7 | Logic | Initialize variables before use | **Yes** | `unguarded-variable` builds a visible-definition table and recognizes `default`, `d`, and `is defined` guards. Runtime variables remain a documented limitation. |
| 8 | Logic | Put code in the correct file | **Partial** | `unexpected-task-location` detects task lists in role defaults/vars/meta files, mappings in tasks/handlers files, plays inside roles, and handler-only `listen` attributes under tasks. Semantic intent remains a human/project-policy question. |
| 9 | Logic | Encapsulate environment variables correctly | **Partial** | `shell-environment-export` and `unscoped-shell-variable` catch subprocess exports and undeclared shell references; host-provided runtime environments remain unknown. |
| 10 | Logic | Keep statements in the correct logical order | **Partial** | `variable-use-before-definition` detects a registered result or `set_fact` value referenced before a later task defines it in the same linear task section. Arbitrary resource precedence and block control flow remain unresolved. |
| 11 | Logic | Do not restate values already provided by defaults | **Yes** | `redundant-default-value` compares role defaults with exact play/task vars and `set_fact` assignments. |
| 12 | Logic | Use boolean filters in Ansible comparisons | **Yes** | `filters_for_comparison.py` produces the `missing-bool-filters` rule. |
| 13 | Logic | Put a blank line before a configuration section | **No** | This source-format convention is not checked. |
| 14 | Logic | Make command execution idempotent | **Partial** | `non-idempotent-command` requires guards for recognized mutating commands; native-module and lint rules add coverage, but arbitrary shell semantics cannot be proven. |
| 15 | Logic | Include file extensions in Ansible task references | **Yes** | `files_extensions.py` produces the `missing-file-extension` rule. |
| 16 | Logic | Set deprecated parameters to `UNDEF` | **No** | `deprecated-modules` checks module names, not whether deprecated parameters are reset to `UNDEF`. |
| 17 | Logic | Check playbook task names | **Yes** | Unnamed, duplicated, overly long, and inconsistent task/play names are checked. |
| 18 | Best practices | Remove unused tasks, variables, comments, and parameters | **Partial** | Unused `set_fact`, included vars, handlers, and registered results are checked; arbitrary unreachable tasks, comments, and parameters are not. |
| 19 | Best practices | Prefer DSL/native built-in functions | **Yes** | `shell-instead-of-module`, deprecated-module/FQCN checks, and `ansible-lint` cover this practice. |
| 20 | Best practices | Use coherent naming conventions | **Yes** | Naming punctuation, missing names, long names, and duplicates are checked. |
| 21 | Best practices | Follow current OpenStack IRC conventions | **No** | This is a changing project/process convention rather than a static Ansible property. |
| 22 | Best practices | Respect standard DSL/YAML notation | **Partial** | `ansible-lint` covers many syntax and notation rules, but the checklist criterion is broader than the integrated rules. |
| 23 | Best practices | Emit warnings for exceptional situations | **Partial** | `silent-error-suppression` reports ignored/disabled failures whose results are not registered, but cannot prove whether another warning path exists. |
| 24 | Best practices | Do not duplicate code | **Yes** | `duplicate_code.py` detects repeated task bodies. |
| 25 | Best practices | Avoid lint failures such as bad whitespace or indentation | **Yes** | The integrated `ansible-lint` scan covers syntax, whitespace, and formatting violations when its executable is installed. |
| 26 | Best practices | Preserve copyright notices | **Yes** | `removed-copyright-notice` compares modified file headers at the committed review base and head. |
| 27 | Compatibility | Check parameter-value compatibility | **No** | Some invalid values may be caught externally, but cross-service and cross-version value compatibility is not modeled. |
| 28 | Compatibility | Check parameter-type compatibility | **Partial** | `invalid-task-attribute-type` validates universal task attributes and ansible-lint validates module schemas; templated/runtime values remain unresolved. |
| 29 | Compatibility | Avoid deprecated options or parameters | **Partial** | `deprecated-module-option` reads option deprecations from installed `ansible-doc` metadata and project overrides in `.ansibleguard.yml`. Removed options absent from installed metadata and unavailable collections remain unresolved. |
| 30 | Compatibility | Avoid deprecated code structures | **Partial** | Deprecated modules, FQCN guidance, boolean-condition rules, and `ansible-lint` cover some structures, not a complete version-aware syntax model. |
| 31 | Dependencies | Check configuration dependencies and ordering | **Partial** | `high-coupling` and `broken-role-dependency` identify dependency quantity, missing roles, self-dependencies, and cycles, but not correct runtime ordering. |
| 32 | Dependencies | Notify handlers between dependent tasks | **Partial** | Missing and unused handler references are checked; the tool cannot always determine that a service-changing task should notify a particular handler. |
| 33 | Test | Update tests when configuration changes | **Yes** | Git-aware `missing-test-update` requires a test/tests/Molecule co-change when the review range changes production YAML. |
| 34 | Test | Test option overrides | **Partial** | `untested-override-change` requires tests when defaults/vars change and `overriding-facts` checks conflicts; test assertion quality is not measured. |
| 35 | Test | Test whether assigned values are correct | **No** | No test-suite execution or coverage-to-configuration mapping is integrated. |
| 36 | Security | Do not leave default credentials | **Yes** | `default-credentials` detects conservative well-known credential values; GitLeaks adds broader hardcoded-secret coverage. |
| 37 | Security | Prevent credentials from leaking into logs | **Yes** | `credentials_leaking_in_log.py` checks sensitive tasks and inherited `no_log` behavior. |
| 38 | Security | Check resource permissions | **Yes** | `insecure-permissions` detects world-writable modes, symbolic world-write, and world-readable sensitive resources. |

## Directly covered checklist items

The fifteen directly covered criteria remain commit-message format, variable
initialization, redundant defaults, boolean filtering, file extensions, task
naming, native DSL/module preference, coherent naming, duplicate-code
avoidance, lint cleanliness, copyright preservation, test co-changes, default
credentials, credential-log protection, and resource permissions.

## Important interpretation

Several paper criteria require information outside a YAML file: commit
messages, release notes, issue trackers, code diffs, test coverage, runtime
values, installed service versions, or human intent. They should not be marked
implemented merely because a loosely related smell exists. The **Partial**
status is used only where the current detector provides concrete, useful
coverage of part of the criterion.

## Newly implemented from the former eight-item gap

| Criterion | New rule | Coverage gained |
|---:|---|---|
| 8 — correct file | `unexpected-task-location` | Objective Ansible role-file and handler-placement errors are now detected. |
| 10 — logical order | `variable-use-before-definition` | Linear use-before-`register`/`set_fact` errors are now detected. |
| 29 — deprecated options | `deprecated-module-option` | Installed collection metadata and configured project deprecations are now checked. |

All three rules produce raw metrics, per-file CSV columns, and normalized JSON,
CSV, text, and SARIF findings. Their algorithms and limits are documented in
`MISSING_CHECKLIST_IMPLEMENTATION.md`.

## Remaining work that is practical to implement

The following backlog is limited to checks that fit AnsibleGuard's current
static-analysis and Git-review architecture. The criterion numbers refer to the
complete mapping above.

| Priority | Criteria improved | Proposed rule or feature | Concrete implementation | Expected result |
|---:|---|---|---|---|
| **P0** | 27, 28, 6 | Project value/type schemas | Extend `.ansibleguard.yml` with optional variable and module-option schemas: type, enum, range, mutually exclusive values, and version constraints. Validate literal values and skip unresolved Jinja expressions. | Makes project-specific value compatibility actionable and improves assigned-value checking. |
| **P0** | 10, 31, 32 | Resource-order graph | Extend the new linear variable-order rule with conservative repository/package-before-install, template/config-before-restart, handler, and dependency-cycle relationships. | Strengthens ordering/dependency coverage without claiming arbitrary runtime ordering is solved. |
| **P1** | 8 | Configurable path policies | Extend `unexpected-task-location` with project mappings from role paths/file patterns to permitted modules or task purposes. | Adds project-specific placement evidence without guessing intent by default. |
| **P1** | 18, 23 | Cross-file symbol/data-flow index | Index variables, `register`, `set_fact`, handlers, includes/imports, and references across the repository. Detect unused definitions and distinguish swallowed failures from registered results that are actually checked or logged. | Strengthens unused-code and exception-warning coverage beyond the current single-file heuristics. |
| **P1** | 33, 34, 35 | Optional test-evidence integration | Add a CLI option for a project test command or JUnit input. Associate changed defaults/vars/tasks with changed or executed Molecule/test scenarios and record pass/fail/tool-error separately. | Verifies that tests ran; semantic correctness of every assigned value remains a test-quality question. |
| **P2** | 1, 2, 4 | Configurable review policy | Let `.ansibleguard.yml` define when release notes, bug trailers, and `Depends-On` trailers are required by path, label, or commit-message pattern. Optionally validate referenced issue/review URLs in CI. | Converts current general heuristics into enforceable project policy while retaining offline operation. |
| **P2** | 14 | Richer idempotency checks | Add module-aware checks for `command`/`shell` alternatives, unsafe unconditional service/file mutations, and user-configured mutating commands; preserve the current escape hatches for `creates`, `removes`, and `changed_when`. | Improves the current partial idempotency coverage with bounded false positives. |

### Recommended first implementation slice

The best next slice is the two remaining **P0** features:

1. configurable value/type compatibility schemas; and
2. conservative resource-order and notification graphs.

They address the highest-value remaining missing criterion and strengthen five
partial criteria. They also fit the existing source-level finding pipeline.

## Missing items that should not be presented as generic Ansible checks

| Criterion | Why it should not be a default AnsibleGuard rule | Appropriate treatment |
|---:|---|---|
| 13 — blank line before a configuration group | This is primarily a source-format convention for configuration formats shown in the OpenStack/Puppet study, not an Ansible semantic defect. YAML formatting is already delegated to linting. | Add only as an opt-in formatter/style rule if a target project requires it. |
| 16 — set deprecated parameters to `UNDEF` | `undef` is a Puppet-specific convention in the paper. Applying it mechanically to Ansible variables would be incorrect. | Do not implement for Ansible; use the new version-aware deprecated-option rule for the applicable Ansible behavior. |
| 21 — follow current OpenStack IRC conventions | This is a changing OpenStack community/process requirement and cannot be inferred from Ansible YAML. | Keep it as a human review item or a project-owned policy file, not a built-in detector. |
| 35 — test assigned values are correct | Static analysis can require or execute tests, but it cannot prove that test assertions establish service-level correctness. | Integrate test evidence and report its status; keep assertion adequacy as a review responsibility. |

## Implementation boundary

Even after the proposed work, the checklist cannot honestly become 38 fully
automated checks. Correct file placement, external dependencies, runtime
values, cross-version service compatibility, bug-report existence, and test
adequacy all depend on project context or external systems. The target should
be stronger evidence and configurable policy, with **Partial** retained where
human intent or runtime behavior is still required.
