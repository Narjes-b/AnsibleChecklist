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
| **Yes** | 9 |
| **Partial** | 9 |
| **No** | 20 |
| **Total** | 38 |

Therefore, the complete paper checklist is **not yet implemented**. Nine items
have direct coverage, nine have partial coverage, and twenty are missing.

## Complete mapping

| # | Paper topic | Checklist criterion | Implemented? | Current coverage or gap |
|---:|---|---|---|---|
| 1 | Documentation | Add a release note for the change | **No** | The analyzer does not inspect release-note files or change metadata. |
| 2 | Documentation | Add a bug report for newly detected bugs | **No** | No issue-tracker or bug-reference validation exists. |
| 3 | Documentation | Add explanatory inline comments | **No** | `incomplete-task` finds TODO-style markers, but it does not require explanations. |
| 4 | Documentation | Record `Depends-On` information in the commit message | **No** | The current pipeline analyzes files, not Git commit messages. |
| 5 | Documentation | Follow the standard commit-message format | **No** | No commit-message linter is integrated. |
| 6 | Logic | Verify assigned parameter values | **Partial** | `ansible-lint`, `missing-validate-certs`, and other specific rules validate some values, but generic semantic correctness cannot be proven. |
| 7 | Logic | Initialize variables before use | **Yes** | `unguarded-variable` builds a visible-definition table and recognizes `default`, `d`, and `is defined` guards. Runtime variables remain a documented limitation. |
| 8 | Logic | Put code in the correct file | **No** | `unstructured-module` validates role entry points, but it cannot determine the intended file for a particular task. |
| 9 | Logic | Encapsulate environment variables correctly | **No** | Variable existence is checked, but environment-variable scope and export boundaries are not modeled. |
| 10 | Logic | Keep statements in the correct logical order | **No** | No execution-order or task-precedence analysis exists. |
| 11 | Logic | Do not restate values already provided by defaults | **No** | Duplicate keys/code are detected, but redundant assignment of an inherited default is not. |
| 12 | Logic | Use boolean filters in Ansible comparisons | **Yes** | `filters_for_comparison.py` produces the `missing-bool-filters` rule. |
| 13 | Logic | Put a blank line before a configuration section | **No** | This source-format convention is not checked. |
| 14 | Logic | Make command execution idempotent | **Partial** | `shell-instead-of-module` recommends idempotent native modules and `ansible-lint` can flag some command/idempotency problems, but general idempotency is not proven. |
| 15 | Logic | Include file extensions in Ansible task references | **Yes** | `files_extensions.py` produces the `missing-file-extension` rule. |
| 16 | Logic | Set deprecated parameters to `UNDEF` | **No** | `deprecated-modules` checks module names, not whether deprecated parameters are reset to `UNDEF`. |
| 17 | Logic | Check playbook task names | **Yes** | Unnamed, duplicated, overly long, and inconsistent task/play names are checked. |
| 18 | Best practices | Remove unused tasks, variables, comments, and parameters | **Partial** | Unused `set_fact`, included variables, and handlers are checked; arbitrary dead tasks, comments, and module parameters are not. |
| 19 | Best practices | Prefer DSL/native built-in functions | **Yes** | `shell-instead-of-module`, deprecated-module/FQCN checks, and `ansible-lint` cover this practice. |
| 20 | Best practices | Use coherent naming conventions | **Yes** | Naming punctuation, missing names, long names, and duplicates are checked. |
| 21 | Best practices | Follow current OpenStack IRC conventions | **No** | This is a changing project/process convention rather than a static Ansible property. |
| 22 | Best practices | Respect standard DSL/YAML notation | **Partial** | `ansible-lint` covers many syntax and notation rules, but the checklist criterion is broader than the integrated rules. |
| 23 | Best practices | Emit warnings for exceptional situations | **No** | The analyzer does not infer where runtime exception handling requires a warning. |
| 24 | Best practices | Do not duplicate code | **Yes** | `duplicate_code.py` detects repeated task bodies. |
| 25 | Best practices | Avoid lint failures such as bad whitespace or indentation | **Yes** | The integrated `ansible-lint` scan covers syntax, whitespace, and formatting violations when its executable is installed. |
| 26 | Best practices | Preserve copyright notices | **No** | This requires change/diff-aware license-header validation, which is not present. |
| 27 | Compatibility | Check parameter-value compatibility | **No** | Some invalid values may be caught externally, but cross-service and cross-version value compatibility is not modeled. |
| 28 | Compatibility | Check parameter-type compatibility | **Partial** | `ansible-lint`/Ansible module argument validation catches some type errors, but templated and runtime values remain unresolved. |
| 29 | Compatibility | Avoid deprecated options or parameters | **No** | The live deprecated detector covers modules and aliases, not module-option deprecations. |
| 30 | Compatibility | Avoid deprecated code structures | **Partial** | Deprecated modules, FQCN guidance, boolean-condition rules, and `ansible-lint` cover some structures, not a complete version-aware syntax model. |
| 31 | Dependencies | Check configuration dependencies and ordering | **Partial** | `high-coupling` and `broken-role-dependency` identify dependency quantity, missing roles, self-dependencies, and cycles, but not correct runtime ordering. |
| 32 | Dependencies | Notify handlers between dependent tasks | **Partial** | Missing and unused handler references are checked; the tool cannot always determine that a service-changing task should notify a particular handler. |
| 33 | Test | Update tests when configuration changes | **No** | The analyzer is not diff-aware and has no production-file-to-test mapping. |
| 34 | Test | Test option overrides | **No** | `overriding-facts` finds conflicting assignments but does not measure test coverage for overrides. |
| 35 | Test | Test whether assigned values are correct | **No** | No test-suite execution or coverage-to-configuration mapping is integrated. |
| 36 | Security | Do not leave default credentials | **Partial** | GitLeaks and credential-keyword checks catch many hardcoded secrets, but they do not reliably distinguish every vendor/default credential from intentional test data. |
| 37 | Security | Prevent credentials from leaking into logs | **Yes** | `credentials_leaking_in_log.py` checks sensitive tasks and inherited `no_log` behavior. |
| 38 | Security | Check resource permissions | **No** | `inventory.md` describes an insecure-permissions detector, but no live `src/ansibleguard/detectors/insecure_permissions.py` exists on this branch. It is therefore not implemented. |

## Directly covered checklist items

The nine directly covered criteria are variable initialization, boolean
filters, file extensions, task naming, native DSL/module preference, coherent
naming, duplicate-code avoidance, lint cleanliness, and credential-log
protection.

## Important interpretation

Several paper criteria require information outside a YAML file: commit
messages, release notes, issue trackers, code diffs, test coverage, runtime
values, installed service versions, or human intent. They should not be marked
implemented merely because a loosely related smell exists. The **Partial**
status is used only where the current detector provides concrete, useful
coverage of part of the criterion.
