# Coverage of the IaC code-review checklist

Source reviewed: *Towards Understanding Code Review Practices for
Infrastructure-as-Code: An Empirical Study on OpenStack Projects* (Empirical
Software Engineering, 2025), especially Table 7.

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
| **Partial** | 15 |
| **No** | 8 |
| **Total** | 38 |

Therefore, the complete paper checklist is **not yet implemented**. Fifteen
items have direct coverage, fifteen have partial coverage, and eight are
missing.

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
| 8 | Logic | Put code in the correct file | **No** | `unstructured-module` validates role entry points, but it cannot determine the intended file for a particular task. |
| 9 | Logic | Encapsulate environment variables correctly | **Partial** | `shell-environment-export` and `unscoped-shell-variable` catch subprocess exports and undeclared shell references; host-provided runtime environments remain unknown. |
| 10 | Logic | Keep statements in the correct logical order | **No** | No execution-order or task-precedence analysis exists. |
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
| 29 | Compatibility | Avoid deprecated options or parameters | **No** | The live deprecated detector covers modules and aliases, not module-option deprecations. |
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

The fifteen directly covered criteria are commit-message format, variable
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
