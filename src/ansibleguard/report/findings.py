"""
Flattens one file's analysis output (the raw `metrics` dict from
parser_playbook.mainn(), the post-threshold `result` dict from
smellsDetector.assess_code_smells(), plus the raw GitLeaks `findings` and
ansible-lint `lint_results`) into one flat list of findings:

    {"file": str, "line": int, "rule_id": str, "severity": str, "message": str}

This is the single shape both the plain-JSON output and the SARIF writer
consume -- keeping the flattening logic in one place means both stay in
sync automatically.

Severity/rule-id catalog lives in RULE_CATALOG below rather than scattered
through this file's logic, so it's a data change, not a code change, to
retune later (e.g. once thresholds.csv gets an empirical calibration pass,
or against the project's own Literature_review/ sources).
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import re


# level: SARIF's three practical severities -- "error", "warning", "note".
# category: informal grouping, not part of SARIF itself, just useful when
# eyeballing findings.json directly.
RULE_CATALOG = {
    "hardcoded-credentials": {
        "level": "error",
        "category": "security",
        "description": "A hardcoded secret was detected by GitLeaks.",
    },
    "credentials-leaking-in-log": {
        "level": "error",
        "category": "security",
        "description": "A task handles a sensitive value without no_log: true.",
    },
    "overriden-keys": {
        "level": "error",
        "category": "correctness",
        "description": "A duplicate mapping key silently discards a value.",
    },
    "missing-bool-filters": {
        "level": "warning",
        "category": "correctness",
        "description": "A when: condition compares against a quoted boolean string.",
    },
    "overriding-facts": {
        "level": "warning",
        "category": "correctness",
        "description": "A set_fact variable is reassigned with a different value.",
    },
    "duplicated-code": {
        "level": "warning",
        "category": "maintainability",
        "description": "Duplicate task blocks detected.",
    },
    "high-coupling": {
        "level": "warning",
        "category": "maintainability",
        "description": "High number of imports/roles.",
    },
    "large-playbook": {
        "level": "warning",
        "category": "maintainability",
        "description": "Playbook exceeds size thresholds.",
    },
    "complex-playbook": {
        "level": "warning",
        "category": "maintainability",
        "description": "Playbook exceeds complexity thresholds.",
    },
    "insufficient-modularization": {
        "level": "warning",
        "category": "maintainability",
        "description": "Playbook is large with many plays -- consider splitting.",
    },
    "large-play": {
        "level": "warning",
        "category": "maintainability",
        "description": "A play exceeds size thresholds.",
    },
    "large-task": {
        "level": "warning",
        "category": "maintainability",
        "description": "A task exceeds size thresholds.",
    },
    "ansible-lint-issue": {
        "level": "warning",
        "category": "lint",
        "description": "ansible-lint reported an issue.",
    },
    "unnamed-play": {
        "level": "note",
        "category": "style",
        "description": "A play has no name:.",
    },
    "unnamed-task": {
        "level": "note",
        "category": "style",
        "description": "A task has no name:.",
    },
    "long-task-name": {
        "level": "note",
        "category": "style",
        "description": "A task name exceeds the length threshold.",
    },
    "inconsistent-naming-convention": {
        "level": "note",
        "category": "style",
        "description": "A task or play name has excessive special characters.",
    },
    "missing-file-extension": {
        "level": "note",
        "category": "style",
        "description": "A file reference is missing a file extension.",
    },
    "unnecessary-abstraction": {
        "level": "note",
        "category": "style",
        "description": "A block: wraps exactly one task.",
    },
    "unnecessary-set-fact": {
        "level": "note",
        "category": "style",
        "description": "A set_fact variable is never used.",
    },
    "unused-include-vars": {
        "level": "note",
        "category": "style",
        "description": "An include_vars file's variables are never used.",
    },
    "duplicate-task-names": {
        "level": "note",
        "category": "style",
        "description": "Multiple tasks share the same name.",
    },
    "incohesive-playbook": {
        "level": "note",
        "category": "cohesion",
        "description": "A playbook's tasks span multiple unrelated module domains (high module-domain entropy).",
    },
    "incohesive-play": {
        "level": "note",
        "category": "cohesion",
        "description": "A play's tasks span multiple unrelated module domains (high module-domain entropy).",
    },
    "missing-validate-certs": {
        "level": "warning",
        "category": "security",
        "description": "TLS certificate validation is disabled on an HTTPS module (uri/get_url).",
    },
    "deprecated-modules": {
        "level": "warning",
        "category": "maintainability",
        "description": "A deprecated Ansible module is in use and may break in future versions.",
    },
    "redirected-module": {
        "level": "note",
        "category": "compatibility",
        "description": "A legacy module name should use its current collection FQCN.",
    },
    "missing-tags": {
        "level": "note",
        "category": "style",
        "policy": "optional",
        "description": "Optional style policy: a task has no explicit or inherited tags.",
    },
    "shell-instead-of-module": {
        "level": "warning",
        "category": "maintainability",
        "description": "A shell/command task could be replaced by a native Ansible module.",
    },
    "missing-handler": {
        "level": "error",
        "category": "correctness",
        "description": "A notify references a handler that does not exist.",
    },
    "unused-handler": {
        "level": "warning",
        "category": "maintainability",
        "description": "A handler is defined but never notified.",
    },
    "complex-expression": {
        "level": "warning",
        "category": "maintainability",
        "description": "A Jinja or conditional expression is excessively complex.",
    },
    "incomplete-task": {
        "level": "warning",
        "category": "maintainability",
        "description": "An unresolved TODO/FIXME marker remains in configuration code.",
    },
    "long-statement": {
        "level": "note",
        "category": "style",
        "description": "A YAML source line exceeds the configured length threshold.",
    },
    "unstructured-module": {
        "level": "warning",
        "category": "structure",
        "description": "An Ansible role does not follow the conventional directory layout.",
    },
    "empty-abstraction": {
        "level": "warning",
        "category": "structure",
        "description": "A task file or nested task abstraction is empty.",
    },
    "excessive-nesting": {
        "level": "warning",
        "category": "maintainability",
        "description": "Nested block/rescue/always structures exceed the depth threshold.",
    },
    "missing-abstraction": {
        "level": "warning",
        "category": "structure",
        "description": "A large task collection is not split into roles or included task files.",
    },
    "broken-role-dependency": {
        "level": "error",
        "category": "correctness",
        "description": "A local role dependency is missing, cyclic, or self-referential.",
    },
    "unguarded-variable": {
        "level": "warning",
        "category": "correctness",
        "policy": "optional",
        "description": "A Jinja variable lacks a visible definition or safety guard.",
    },
    "insecure-permissions": {
        "level": "error",
        "category": "security",
        "description": "A managed resource grants unsafe permissions to other users.",
    },
    "unsafe-file-write": {
        "level": "warning",
        "category": "reliability",
        "description": "A file operation disables Ansible's atomic-write protection.",
    },
    "default-credentials": {
        "level": "error",
        "category": "security",
        "description": "A credential uses a well-known default value.",
    },
    "plaintext-sensitive-variable": {
        "level": "warning",
        "category": "security",
        "description": "A sensitive variable is stored as a plaintext literal.",
    },
    "unpinned-ansible-dependency": {
        "level": "warning",
        "category": "dependencies",
        "description": "An Ansible role or collection dependency has no fixed version.",
    },
    "role-variable-precedence-collision": {
        "level": "warning",
        "category": "correctness",
        "description": "A role variable is defined in both defaults and vars.",
    },
    "non-idempotent-command": {
        "level": "warning",
        "category": "correctness",
        "description": "A mutating command lacks an idempotency guard.",
    },
    "read-only-command-change": {
        "level": "note",
        "category": "reliability",
        "description": "A read-only command may report a change on every run.",
    },
    "silent-error-suppression": {
        "level": "warning",
        "category": "reliability",
        "description": "A task suppresses failure without retaining its result.",
    },
    "redundant-default-value": {
        "level": "note",
        "category": "maintainability",
        "description": "An assignment repeats a value already supplied by role defaults.",
    },
    "shell-environment-export": {
        "level": "warning",
        "category": "correctness",
        "description": "A shell export is used instead of Ansible's environment mapping.",
    },
    "undocumented-complex-task": {
        "level": "note",
        "category": "documentation",
        "description": "A complex task lacks a nearby explanatory comment.",
    },
    "unused-registered-variable": {
        "level": "note",
        "category": "maintainability",
        "description": "A registered task result is never referenced.",
    },
    "unscoped-shell-variable": {
        "level": "warning",
        "category": "correctness",
        "description": "A shell variable is not declared in Ansible's environment mapping.",
    },
    "invalid-task-attribute-type": {
        "level": "error",
        "category": "correctness",
        "description": "A common Ansible task attribute has the wrong YAML type.",
    },
    "invalid-numeric-value": {
        "level": "error",
        "category": "correctness",
        "description": "A numeric task/module value is outside its valid range.",
    },
    "missing-release-note": {
        "level": "note",
        "category": "documentation",
        "description": "The latest configuration change has no release note.",
    },
    "missing-bug-reference": {
        "level": "note",
        "category": "documentation",
        "description": "A bug-fix commit message has no bug reference.",
    },
    "invalid-depends-on-reference": {
        "level": "warning",
        "category": "dependencies",
        "description": "A Depends-On trailer is malformed.",
    },
    "commit-message-format": {
        "level": "note",
        "category": "documentation",
        "description": "The latest commit message violates the review format.",
    },
    "removed-copyright-notice": {
        "level": "warning",
        "category": "legal",
        "description": "A copyright notice was removed by the latest commit.",
    },
    "missing-test-update": {
        "level": "warning",
        "category": "testing",
        "description": "Configuration changed without a corresponding test change.",
    },
    "untested-override-change": {
        "level": "warning",
        "category": "testing",
        "description": "Defaults or variables changed without an override test change.",
    },
    "variable-use-before-definition": {
        "level": "warning",
        "category": "correctness",
        "description": "A task uses a registered result or fact before a later task defines it.",
    },
    "unexpected-task-location": {
        "level": "warning",
        "category": "structure",
        "description": "An Ansible document or handler-only task is placed in the wrong role directory.",
    },
    "deprecated-module-option": {
        "level": "warning",
        "category": "compatibility",
        "description": "A task uses a deprecated Ansible module option.",
    },
    "loop-legacy-syntax": {
        "level": "warning",
        "category": "compatibility",
        "description": "A task uses deprecated with_* loop syntax; use loop: instead.",
    },
    "become-scope-too-broad": {
        "level": "warning",
        "category": "security",
        "description": "become: true is applied at play level, granting all tasks root access.",
    },
    "molecule-test-absent": {
        "level": "note",
        "category": "testing",
        "policy": "optional",
        "description": "Optional testing policy: an Ansible role has no Molecule test scenario.",
    },
    "yaml-formatting": {
        "level": "note",
        "category": "style",
        "description": "A YAML formatting issue (indentation, trailing spaces, line endings).",
    },
    "fqcn-migration": {
        "level": "note",
        "category": "compatibility",
        "description": "A task uses a short module name instead of the fully-qualified collection name.",
    },
    "yaml-truthy-value": {
        "level": "warning",
        "category": "correctness",
        "description": "A YAML value uses 'yes'/'no' instead of the canonical 'true'/'false'.",
    },
    "role-readme-absent": {
        "level": "note",
        "category": "documentation",
        "policy": "optional",
        "description": "Optional documentation policy: an Ansible role has no README.md file.",
    },
    "galaxy-meta-incomplete": {
        "level": "note",
        "category": "documentation",
        "policy": "optional",
        "description": "Optional Galaxy-publication policy: a role's meta/main.yml is missing galaxy_info fields.",
    },
    "variable-naming-convention": {
        "level": "note",
        "category": "style",
        "policy": "optional",
        "description": "Optional naming policy: a role variable is not prefixed with the role name.",
    },
    "vault-inline-overload": {
        "level": "note",
        "category": "security",
        "policy": "optional",
        "description": "Optional organization policy: a role has many inline !vault | values.",
    },
}


# Developer guidance is kept separate from detector messages so every output
# format can explain a stable correction without individual detectors copying
# prose. Confidence describes static-detector certainty, not security impact.
RULE_REMEDIATION = {
    "hardcoded-credentials": "Remove the literal secret, rotate it if live, and load it from Ansible Vault or an approved secret manager.",
    "credentials-leaking-in-log": "Set effective no_log: true on the sensitive task or block and avoid printing the sensitive result.",
    "overriden-keys": "Keep one mapping entry for the key and merge the intended values explicitly.",
    "missing-bool-filters": "Convert the value explicitly with | bool or use a native boolean expression.",
    "overriding-facts": "Use one authoritative assignment or rename facts whose values represent different states.",
    "duplicated-code": "Extract the repeated task body into an included task file or role when the duplication is intentional reuse.",
    "high-coupling": "Review whether imports and roles can be grouped behind a smaller, cohesive role interface.",
    "large-playbook": "Split independent responsibilities into roles or imported playbooks after confirming the threshold is appropriate.",
    "complex-playbook": "Separate unrelated responsibilities and reduce deeply connected imports, roles, or task groups.",
    "insufficient-modularization": "Move cohesive play groups into roles or imported playbooks with explicit interfaces.",
    "large-play": "Split the play into cohesive task files or roles if doing so improves ownership and reuse.",
    "large-task": "Replace a monolithic task with a native module or smaller named tasks where semantics permit.",
    "ansible-lint-issue": "Follow the native ansible-lint rule documentation identified by native_rule_id and help_url.",
    "unnamed-play": "Add a concise, action-oriented name to the play.",
    "unnamed-task": "Add a concise task name that describes the intended state or action.",
    "long-task-name": "Shorten the name while preserving the operational intent developers need in Ansible output.",
    "inconsistent-naming-convention": "Use the project's agreed task/play naming style and avoid decorative punctuation.",
    "duplicate-task-names": "Give each task a name that distinguishes its purpose or target.",
    "missing-tags": "Add an explicit or inherited tag only if the project needs selective execution; otherwise disable this optional rule.",
    "missing-file-extension": "Use the complete referenced filename, including .yml/.yaml or the actual resource suffix.",
    "unnecessary-abstraction": "Remove the one-child block unless it intentionally supplies shared conditions, privilege, or error handling.",
    "unnecessary-set-fact": "Remove the unused fact or reference it through a visible, documented data flow.",
    "unused-include-vars": "Remove unused included variables or make their intended references explicit.",
    "incohesive-playbook": "Review whether unrelated responsibilities should move into separate playbooks or roles.",
    "incohesive-play": "Group related tasks together or split unrelated responsibilities after manually checking the semantic signal.",
    "missing-validate-certs": "Enable certificate validation and configure the trusted CA; document and narrowly suppress only justified bootstrap exceptions.",
    "deprecated-modules": "Replace the deprecated module with the reported supported module/FQCN and test behavior on the target Ansible version.",
    "redirected-module": "Use the reported current collection FQCN to make resolution explicit.",
    "shell-instead-of-module": "Replace the recognized command with the suggested native Ansible module when its semantics match.",
    "missing-handler": "Define the notified handler or correct the notify/listen name so repository-wide resolution succeeds.",
    "unused-handler": "Remove the handler or add the intended notify edge from the task that changes its resource.",
    "complex-expression": "Extract intermediate variables or split the condition into named, independently understandable checks.",
    "incomplete-task": "Complete the marked work, link it to tracked work, or remove the stale marker.",
    "long-statement": "Wrap or restructure the YAML/Jinja expression when possible; suppress only unavoidable generated values or URLs.",
    "unstructured-module": "Add the conventional role entry point or document/configure the intentional custom layout.",
    "empty-abstraction": "Remove the empty file/block or add the intended tasks before enabling it.",
    "excessive-nesting": "Extract nested blocks into named task files or roles and simplify shared conditions/error handling.",
    "missing-abstraction": "Split the large task collection along cohesive responsibilities when that improves navigation and reuse.",
    "broken-role-dependency": "Correct the local role name, remove self/cyclic edges, or declare the external dependency explicitly.",
    "unguarded-variable": "Define the variable in visible scope or use default()/d()/is defined when absence is valid.",
    "insecure-permissions": "Use the least-permissive mode required and protect private or sensitive material from group/other access.",
    "unsafe-file-write": "Remove unsafe_writes: true unless the target filesystem cannot support atomic replacement; document the exception.",
    "default-credentials": "Replace the default credential, rotate it if deployed, and retrieve the replacement from a protected source.",
    "non-idempotent-command": "Use a native module or add creates/removes/changed_when/check_mode evidence that models the real state change.",
    "read-only-command-change": "Add changed_when: false to the read-only command or use a read-only Ansible information module.",
    "silent-error-suppression": "Handle the failure explicitly: register and inspect the result, add recovery, or remove blanket suppression.",
    "redundant-default-value": "Remove the identical override and rely on the role default unless the repetition is intentional policy documentation.",
    "shell-environment-export": "Move environment values to the task/play environment mapping instead of a standalone shell export.",
    "undocumented-complex-task": "Add a nearby comment explaining the non-obvious reason, constraint, or ordering—not a restatement of syntax.",
    "unused-registered-variable": "Remove register or inspect the result in a later condition, assertion, recovery, or diagnostic task.",
    "unscoped-shell-variable": "Declare the variable through environment, an inline assignment, or an explicit Ansible variable expansion.",
    "invalid-task-attribute-type": "Use the YAML type required by the reported task attribute rather than a quoted or structurally incompatible value.",
    "invalid-numeric-value": "Replace the literal with a value inside the reported valid range or validate a templated value before use.",
    "variable-use-before-definition": "Move the defining register/set_fact earlier or restructure the task order and guards.",
    "unexpected-task-location": "Move executable content to tasks/handlers and data to defaults/vars/meta according to the role layout.",
    "deprecated-module-option": "Replace or remove the option using the reported collection metadata and test against the target version.",
    "loop-legacy-syntax": "Replace with_* loops with the unified loop: keyword introduced in Ansible 2.5 and use the corresponding Jinja2 filter or lookup.",
    "become-scope-too-broad": "Move become: true to the specific tasks that require privilege escalation; use become_user for fine-grained control.",
    "molecule-test-absent": "Create a molecule/ directory with at least one scenario to verify role behavior in an isolated environment.",
    "plaintext-sensitive-variable": "Encrypt the value with Ansible Vault or replace it with a lookup from an approved secret manager.",
    "unpinned-ansible-dependency": "Pin the external role/collection to an immutable version or reviewed commit according to project policy.",
    "role-variable-precedence-collision": "Keep overrideable values in defaults and reserve vars for deliberately fixed internal values.",
    "missing-release-note": "Add the project-standard release-note fragment or configure/document why this change is exempt.",
    "missing-bug-reference": "Add the project-standard bug/issue reference to the relevant commit message.",
    "invalid-depends-on-reference": "Replace the trailer value with a valid review URL or Gerrit Change-Id.",
    "commit-message-format": "Rewrite the commit message to satisfy the configured subject/body length and separation policy.",
    "removed-copyright-notice": "Restore the notice unless its removal is intentional and legally reviewed.",
    "missing-test-update": "Add or update a test/Molecule scenario that exercises the changed production behavior.",
    "untested-override-change": "Add an override-focused test that supplies the changed option and asserts the resulting behavior.",
    "yaml-formatting": "Fix YAML formatting issues; use a linter or autoformatter with the project's configured style.",
    "fqcn-migration": "Use the fully-qualified collection name (FQCN) such as 'ansible.builtin.copy' instead of the legacy short form.",
    "yaml-truthy-value": "Replace 'yes'/'no' with 'true'/'false' for YAML 1.2 compatibility and explicit intent.",
    "role-readme-absent": "Add a README.md at the role root documenting inputs, outputs, and example usage.",
    "galaxy-meta-incomplete": "Populate the required galaxy_info fields (author, description, min_ansible_version) in meta/main.yml.",
    "variable-naming-convention": "Prefix role variables with the role name (e.g. myrole_varname) to avoid cross-role collisions.",
    "vault-inline-overload": "Move inline vault values to a dedicated vars/vault.yml or defaults/vault.yml and load it with include_vars.",
}

# Fix A5: Maps ansible-lint noqa tag names to AnsibleGuard rule/concept IDs.
# When a source line has "# noqa <tag>", findings on that line whose rule_id,
# native_rule_id, or concept_id matches are suppressed.
NOQA_MAP = {
    "no-changed-when": {"non-idempotent-command"},
    "command-instead-of-module": {"shell-module-migration", "shell-instead-of-module"},
    "ignore-errors": {"unhandled-failure-suppression", "silent-error-suppression"},
    "no-log-password": {"credential-log-exposure", "credentials-leaking-in-log"},
    "yaml[line-length]": {"long-yaml-line", "long-statement"},
    "yaml[key-duplicates]": {"duplicate-mapping-key", "overriden-keys"},
    "risky-file-permissions": {"insecure-permissions"},
    "name[casing]": {"unnamed-task", "inconsistent-naming-convention"},
    # fqcn rules now promote to fqcn-migration concept
    "fqcn[action-core]": {"ansible-lint-issue", "fqcn-migration"},
    "fqcn[action]": {"ansible-lint-issue", "fqcn-migration"},
    "fqcn[builtins]": {"ansible-lint-issue", "fqcn-migration"},
    # partial-become promotes to become-scope-too-broad
    "partial-become": {"ansible-lint-issue", "become-scope-too-broad"},
    # yaml[truthy] promotes to yaml-truthy-value
    "yaml[truthy]": {"ansible-lint-issue", "yaml-truthy-value"},
    # yaml formatting rules promote to yaml-formatting concept
    "yaml[indentation]": {"ansible-lint-issue", "yaml-formatting"},
    "yaml[trailing-spaces]": {"ansible-lint-issue", "yaml-formatting"},
    "yaml[empty-lines]": {"ansible-lint-issue", "yaml-formatting"},
    "yaml[colons]": {"ansible-lint-issue", "yaml-formatting"},
    "yaml[comments]": {"ansible-lint-issue", "yaml-formatting"},
    "yaml[new-line-at-end-of-file]": {"ansible-lint-issue", "yaml-formatting"},
    "var-naming": {"inconsistent-naming-convention", "variable-naming-convention"},
}


def _parse_noqa_suppressions(yaml_text):
    """Extract {line_number: frozenset(rule_ids)} for # noqa annotated lines."""
    suppressions = {}
    if not yaml_text:
        return suppressions
    for i, line in enumerate(yaml_text.splitlines(), 1):
        match = re.search(r"#\s*noqa:?\s*(.*)", line, re.IGNORECASE)
        if not match:
            continue
        raw = match.group(1).strip()
        tags = {tag.strip() for tag in re.split(r"[,\s]+", raw) if tag.strip()}
        suppressed = set()
        for tag in tags:
            if tag in NOQA_MAP:
                suppressed.update(NOQA_MAP[tag])
            suppressed.add(tag)  # also keep raw tag for direct matching
        suppressions[i] = frozenset(suppressed)
    return suppressions


LOW_CONFIDENCE_RULES = frozenset({
    "complex-playbook", "high-coupling", "incohesive-play",
    "incohesive-playbook", "insufficient-modularization", "large-play",
    "large-playbook", "large-task", "long-task-name", "missing-abstraction",
    "missing-tags", "unguarded-variable", "unnecessary-abstraction",
    "unnecessary-set-fact", "unused-include-vars", "undocumented-complex-task",
})

# Lifecycle is part of the public output contract.  Disabled rules remain in
# the catalog so historical SARIF and stored results stay readable, but new
# scans must not present them as active capabilities.  Experimental rules are
# emitted only as low-confidence research signals until held-out validation
# supports promotion.
DISABLED_RULES = frozenset()
EXPERIMENTAL_RULES = frozenset({
    "default-credentials",
    "high-coupling",
    "incohesive-play",
    "incohesive-playbook",
    "insecure-permissions",
    "shell-instead-of-module",
    "silent-error-suppression",
    "undocumented-complex-task",
    "unnecessary-set-fact",
    "unstructured-module",
    "unused-include-vars",
    "variable-use-before-definition",
})
CANDIDATE_RULES = frozenset({
    # The 15-repository pilot exposed substantial cross-role/runtime context.
    # Keep the rule non-stable until the prescribed stratified review of
    # UNRESOLVED cases has been completed.
    "unguarded-variable",
    # These policy rules were unreachable in v0.0.6 repository scans. Keep
    # them non-stable until their newly visible populations are calibrated.
    "galaxy-meta-incomplete",
    "variable-naming-convention",
})
HIGH_CONFIDENCE_RULES = frozenset({
    "commit-message-format", "invalid-depends-on-reference",
    "invalid-numeric-value", "invalid-task-attribute-type",
    "missing-file-extension", "overriden-keys", "read-only-command-change",
    "removed-copyright-notice", "unsafe-file-write",
})
STYLE_POLICY_RULES = frozenset({
    "fqcn-migration", "missing-tags", "yaml-formatting",
    "ansible-lint-issue",
})

# Known static-analysis boundaries are executable catalog data, not prose-only
# caveats.  Empty tuples are intentional for rules whose contract has no
# identified semantic uncertainty beyond ordinary source correctness.
RULE_LIMITATIONS = {
    "ansible-lint-issue": ("provider_environment_and_configuration",),
    "broken-role-dependency": ("external_roles_are_not_resolved",),
    "credentials-leaking-in-log": (
        "custom_action_plugin_redaction_may_be_unknown",
        "indirect_secret_flow_is_bounded",
    ),
    "deprecated-module-option": ("module_metadata_may_be_unavailable",),
    "missing-tags": ("importing_file_or_role_call_tags_require_graph_context",),
    "overriding-facts": ("runtime_branch_intent_is_not_symbolically_executed",),
    "plaintext-sensitive-variable": (
        "secret_classification_is_static_and_contextual",
    ),
    "redundant-default-value": (
        "runtime_precedence_and_branch_transitions_are_bounded",
    ),
    "unexpected-task-location": (
        "dynamic_import_call_sites_cannot_be_resolved_exactly",
    ),
    "unguarded-variable": (
        "dynamic_inventory_is_not_executed",
        "undeclared_custom_module_facts_may_be_unknown",
    ),
    "unused-include-vars": (
        "dynamic_variable_names_force_conservative_abstention",
    ),
    "variable-use-before-definition": (
        "dynamic_inventory_is_not_executed",
        "runtime_generated_definitions_are_conservative",
    ),
}
RULE_UNCERTAINTY_SOURCES = {
    "credentials-leaking-in-log": (
        "dynamic_no_log", "missing_module_metadata", "custom_action_plugin",
    ),
    "plaintext-sensitive-variable": (
        "example_or_fixture_context", "placeholder_value",
    ),
    "unguarded-variable": (
        "dynamic_include", "custom_module_fact", "inventory_not_resolved",
    ),
    "unused-include-vars": (
        "dynamic_include", "dynamic_vars_lookup", "external_population",
    ),
    "variable-use-before-definition": (
        "dynamic_include", "custom_module_fact", "inventory_not_resolved",
    ),
}

if set(RULE_REMEDIATION) != set(RULE_CATALOG):
    missing = sorted(set(RULE_CATALOG) - set(RULE_REMEDIATION))
    extra = sorted(set(RULE_REMEDIATION) - set(RULE_CATALOG))
    raise RuntimeError(f"invalid rule guidance; missing={missing}; extra={extra}")
for _rule_id, _metadata in RULE_CATALOG.items():
    _metadata["remediation"] = RULE_REMEDIATION[_rule_id]
    _metadata["confidence"] = (
        "low" if _rule_id in LOW_CONFIDENCE_RULES or _rule_id in EXPERIMENTAL_RULES
        else "high" if _rule_id in HIGH_CONFIDENCE_RULES
        else "medium"
    )
    _metadata["status"] = (
        "deprecated" if _rule_id in DISABLED_RULES
        else "experimental" if _rule_id in EXPERIMENTAL_RULES
        else "candidate" if _rule_id in CANDIDATE_RULES
        else "stable"
    )
    _category = _metadata.get("category", "uncategorized")
    _policy = _metadata.get("policy", "required")
    _metadata["taxonomy"] = (
        "RISK" if _category == "security"
        else "STYLE_POLICY"
        if _category in {"style", "lint"} or _rule_id in STYLE_POLICY_RULES
        else "OPTIONAL_PRACTICE" if _policy == "optional"
        else "MAINTAINABILITY_SIGNAL"
        if _category in {"maintainability", "cohesion", "structure", "documentation"}
        else "DEFECT"
    )
    _metadata["actionability"] = (
        "blocking"
        if _metadata["level"] == "error" and _category == "security"
        else "informational" if _policy == "optional"
        else "actionable" if _metadata["level"] in {"error", "warning"}
        else "advisory"
    )
    _metadata["known_limitations"] = list(
        RULE_LIMITATIONS.get(_rule_id, ())
    )
    _metadata["uncertainty_sources"] = list(
        RULE_UNCERTAINTY_SOURCES.get(_rule_id, ())
    )


CONCEPT_IDS = {
    "hardcoded-credentials": "hardcoded-secret",
    "plaintext-sensitive-variable": "hardcoded-secret",
    "credentials-leaking-in-log": "credential-log-exposure",
    "overriden-keys": "duplicate-mapping-key",
    "deprecated-modules": "module-deprecation",
    "shell-instead-of-module": "shell-module-migration",
    "silent-error-suppression": "unhandled-failure-suppression",
    # long-statement and ansible-lint/yaml[line-length] detect the same
    # condition; share a concept so they deduplicate in build_occurrences.
    "long-statement": "long-yaml-line",
}

# Canonical semantic classes emitted by the compatibility
# ``unguarded-variable`` detector in v0.0.6.1. These are concepts rather than
# independently selectable detectors, so they intentionally do not enter
# RULE_CATALOG or profile rule populations.
VARIABLE_CLASSIFICATION_CATALOG = {
    "missing-internal-variable": {
        "level": "warning",
        "category": "correctness",
        "policy": "required",
        "confidence": "medium",
        "taxonomy": "DEFECT",
        "actionability": "actionable",
        "status": "candidate",
        "remediation": (
            "Define the internal variable before use, or add an explicit "
            "default/defined guard when absence is valid."
        ),
    },
    "undeclared-input-contract": {
        "level": "note",
        "category": "correctness",
        "policy": "optional",
        "confidence": "low",
        "taxonomy": "OPTIONAL_PRACTICE",
        "actionability": "advisory",
        "status": "candidate",
        "remediation": (
            "Declare the expected role, playbook, or task-fragment input and "
            "validate each concrete caller rather than adding a masking default."
        ),
    },
    "unresolved-runtime-input": {
        "level": "note",
        "category": "correctness",
        "policy": "optional",
        "confidence": "low",
        "taxonomy": "OPTIONAL_PRACTICE",
        "actionability": "informational",
        "status": "candidate",
        "remediation": (
            "Supply inventory, caller, fact, dependency, or runtime input "
            "evidence to close the analysis context."
        ),
    },
}

EXTERNAL_CONCEPT_IDS = {
    "deprecated-module": "module-deprecation",
    "command-instead-of-module": "shell-module-migration",
    "no-log-password": "credential-log-exposure",
    "ignore-errors": "unhandled-failure-suppression",
    "yaml[key-duplicates]": "duplicate-mapping-key",
    "yaml[line-length]": "long-yaml-line",
    # Fix 2: risky-file-permissions promoted to insecure-permissions concept
    "risky-file-permissions": "insecure-permissions",
    # Fix 4: yaml-formatting stratum (whitespace/indentation issues)
    "yaml[indentation]": "yaml-formatting",
    "yaml[trailing-spaces]": "yaml-formatting",
    "yaml[new-line-at-end-of-file]": "yaml-formatting",
    "yaml[empty-lines]": "yaml-formatting",
    "yaml[colons]": "yaml-formatting",
    "yaml[comments]": "yaml-formatting",
    "yaml[comments-indentation]": "yaml-formatting",
    "yaml[octal-values]": "yaml-formatting",
    "yaml[brackets]": "yaml-formatting",
    "yaml[braces]": "yaml-formatting",
    "yaml[commas]": "yaml-formatting",
    "yaml[document-start]": "yaml-formatting",
    # Fix 4: fqcn-migration stratum
    "fqcn[action-core]": "fqcn-migration",
    "fqcn[action]": "fqcn-migration",
    "fqcn[builtins]": "fqcn-migration",
    # Fix D2: partial-become → become-scope-too-broad
    "partial-become": "become-scope-too-broad",
    # Fix D3: yaml[truthy] → yaml-truthy-value
    "yaml[truthy]": "yaml-truthy-value",
    # Native role-prefix policy and the internal fallback detect the same
    # condition. Keep one canonical concept when ansible-lint is available.
    "var-naming[no-role-prefix]": "variable-naming-convention",
    "redhat-ci[no-role-prefix]": "variable-naming-convention",
    # Fix 5: no-changed-when → non-idempotent-command (deduplication)
    "no-changed-when": "non-idempotent-command",
}


# Developer-facing ordering is deliberately risk-first. Optional policy
# findings are sorted after actionable findings separately, so this list only
# controls category order within the same policy group.
CATEGORY_PRIORITY = (
    "security",
    "correctness",
    "reliability",
    "testing",
    "dependencies",
    "compatibility",
    "legal",
    "lint",
    "maintainability",
    "documentation",
    "structure",
    "cohesion",
    "style",
    "uncategorized",
)
_CATEGORY_RANK = {
    category: index for index, category in enumerate(CATEGORY_PRIORITY)
}
_SEVERITY_RANK = {"error": 0, "warning": 1, "note": 2}


def finding_catalog_metadata(item):
    """Resolve catalog metadata for a finding or canonical occurrence.

    Canonical concept IDs can differ from native detector rule IDs. Preserve
    that indirection while ensuring every PR and repository report uses the
    same category and optional-policy decision.
    """
    candidates = [item.get("concept_id"), item.get("rule_id")]
    for detector in item.get("detectors", []) or []:
        candidates.extend(
            (detector.get("rule_id"), detector.get("native_rule_id"))
        )
    candidates.extend(
        str(native_rule).split("/", 1)[-1]
        for native_rule in item.get("native_rules", []) or []
    )
    for rule_id in candidates:
        metadata = (
            VARIABLE_CLASSIFICATION_CATALOG.get(rule_id)
            or RULE_CATALOG.get(rule_id)
        )
        if metadata:
            return metadata
        # Canonical occurrences intentionally use stable concept IDs while
        # the catalog is keyed by the native rule that produced them.
        native_rule_ids = (
            native_rule
            for native_rule, concept_id in (
                *CONCEPT_IDS.items(),
                *EXTERNAL_CONCEPT_IDS.items(),
            )
            if concept_id == rule_id
        )
        for native_rule_id in native_rule_ids:
            metadata = RULE_CATALOG.get(native_rule_id)
            if metadata:
                return metadata
    return {}


def finding_category(item):
    return finding_catalog_metadata(item).get("category", "uncategorized")


def finding_policy(item):
    return finding_catalog_metadata(item).get("policy", "required")


def finding_taxonomy(item):
    return finding_catalog_metadata(item).get("taxonomy", "MAINTAINABILITY_SIGNAL")


def finding_actionability(item):
    return finding_catalog_metadata(item).get("actionability", "advisory")


def finding_maturity(item):
    return finding_catalog_metadata(item).get("status", "experimental")


def is_optional_finding(item):
    return finding_policy(item) == "optional"


def developer_priority_key(item):
    """Sort actionable, high-risk occurrences before optional style noise."""
    category = finding_category(item)
    return (
        1 if is_optional_finding(item) else 0,
        _CATEGORY_RANK.get(category, len(_CATEGORY_RANK)),
        _SEVERITY_RANK.get(str(item.get("severity", "warning")).lower(), 1),
        str(item.get("file", "")),
        int(item.get("line") or 1),
        str(item.get("concept_id") or item.get("rule_id") or ""),
    )


def _finding(
    file,
    line,
    rule_id,
    message,
    *,
    provider="ansibleguard",
    native_rule_id=None,
    native_severity=None,
    native_categories=None,
    native_fingerprint=None,
    help_url=None,
    scan_mode=None,
):
    catalog_entry = RULE_CATALOG.get(rule_id, {"level": "warning"})
    native_rule_id = native_rule_id or rule_id
    concept_id = EXTERNAL_CONCEPT_IDS.get(
        native_rule_id, CONCEPT_IDS.get(rule_id, rule_id)
    )
    finding = {
        "file": str(file),
        "line": int(line) if line else 1,
        "rule_id": rule_id,
        "severity": catalog_entry["level"],
        "message": message,
        "provider": provider,
        "native_rule_id": native_rule_id,
        "concept_id": concept_id,
        "confidence": catalog_entry.get("confidence", "medium"),
        "taxonomy": catalog_entry.get("taxonomy", "MAINTAINABILITY_SIGNAL"),
        "actionability": catalog_entry.get("actionability", "advisory"),
        "rule_maturity": catalog_entry.get("status", "experimental"),
        "remediation": catalog_entry.get("remediation", "Review the finding in project context."),
        "known_limitations": list(catalog_entry.get("known_limitations", ())),
        "rule_uncertainty_sources": list(
            catalog_entry.get("uncertainty_sources", ())
        ),
    }
    if native_severity:
        finding["native_severity"] = str(native_severity)
    if native_categories:
        finding["native_categories"] = list(native_categories)
    if native_fingerprint:
        finding["native_fingerprint"] = str(native_fingerprint)
    if help_url:
        finding["help_url"] = str(help_url)
    if scan_mode:
        finding["scan_mode"] = str(scan_mode)
    return _with_finding_identity(finding)


def _with_finding_identity(finding):
    """Return *finding* with an identity derived from portable fields."""
    identity = "|".join(
        (
            finding["provider"],
            finding["native_rule_id"],
            finding["file"].replace("\\", "/"),
            str(finding["line"]),
            finding["message"],
        )
    )
    finding["finding_id"] = hashlib.sha256(identity.encode("utf-8")).hexdigest()
    return finding


def normalize_finding_paths(findings, repo_root):
    """Make raw findings independent of the acquisition directory.

    Provider adapters historically emitted absolute paths.  Temporary remote
    snapshots therefore produced different raw finding IDs from a local
    checkout of the same bytes.  The output contract is repository scoped, so
    store repository-relative POSIX paths and rebuild the identity after the
    normalization.  Paths outside the repository retain only their basename;
    this mirrors canonical occurrence normalization without exposing a host
    filesystem path.
    """
    root = Path(repo_root).resolve()
    normalized = []
    for original in findings:
        finding = dict(original)
        path = Path(str(finding.get("file") or "."))
        try:
            relative = path.resolve().relative_to(root)
        except ValueError:
            relative = Path(path.name)
        finding["file"] = relative.as_posix().removeprefix("./") or "."
        message = str(finding.get("message") or "")
        for spelling in {str(root), root.as_posix()}:
            message = message.replace(spelling, "<repo>")
        finding["message"] = message
        normalized.append(_with_finding_identity(finding))
    return normalized


def deduplicate_findings(findings):
    """Preserve first-seen order while removing identical detector evidence."""
    unique = {}
    for finding in findings:
        unique.setdefault(finding["finding_id"], finding)
    return list(unique.values())


def build_findings_list(
    metrics, result, gitleaks_findings, lint_results, yaml_file_path
):
    """
    metrics: the raw dict from parser_playbook.mainn() (has real line data
             for overriden_keys, and the real per-task warning strings for
             credentials_leaking_in_log, before assess_code_smells()
             collapses both down to bare counts).
    result:  the post-threshold dict from assess_code_smells() (has the
             per-play/per-task pass/fail breakdown).
    gitleaks_findings / lint_results: the raw external-tool outputs,
             already returned by execute_for_single_file() today.
    """
    out = []
    file = yaml_file_path

    # --- GitLeaks: real file+line data already present in its own output ---
    for f in gitleaks_findings or []:
        line = f.get("StartLine") or f.get("startLine") or 1
        desc = f.get("Description") or f.get("RuleID") or "Hardcoded secret detected"
        out.append(
            _finding(
                file,
                line,
                "hardcoded-credentials",
                desc,
                provider="gitleaks",
                native_rule_id=(
                    f.get("RuleID") or f.get("ruleID") or "gitleaks-secret"
                ),
                native_severity="error",
                native_fingerprint=f.get("Fingerprint") or f.get("fingerprint"),
                scan_mode=f.get("_scan_mode") or f.get("ScanMode") or "dir",
            )
        )
        # E4: Pass GitLeaks entropy score through for confidence ranking
        entropy = f.get("Entropy") or f.get("entropy")
        if entropy is not None:
            try:
                out[-1]["native_entropy"] = float(entropy)
            except (TypeError, ValueError):
                pass

    # ansible-lint is also target-level and may produce useful load/syntax
    # findings for documents our structural detector cannot analyze.
    from ansibleguard.external.ansible_lint import lint_issue_line

    for issue in lint_results or []:
        native_rule = (
            issue.get("check_name")
            or issue.get("rule_id")
            or issue.get("ruleId")
            or "ansible-lint-issue"
        )
        # Fix 1: Filter load-failure — YAML syntax errors, not actionable smells
        if str(native_rule).startswith("load-failure"):
            continue
        line = lint_issue_line(issue)
        message = (
            issue.get("message") or issue.get("description") or "ansible-lint issue"
        )
        out.append(
            _finding(
                file,
                line,
                "ansible-lint-issue",
                message,
                provider="ansible-lint",
                native_rule_id=native_rule,
                native_severity=issue.get("severity") or issue.get("level"),
                native_categories=issue.get("categories") or (),
                native_fingerprint=issue.get("fingerprint"),
                help_url=issue.get("url"),
            )
        )
        if issue.get("warn_list_suppressed"):
            out[-1]["native_policy"] = "warn-list"
            out[-1]["policy_adjusted"] = True
            out[-1]["confidence"] = "low"
        if issue.get("analysis_population"):
            out[-1]["analysis_population"] = issue["analysis_population"]
        if issue.get("environment_dependent"):
            out[-1]["environment_dependent"] = True

    if not metrics or not result:
        return out

    pm = result["playbook"]["metrics"]

    # --- credentials_leaking_in_log: use the new details list (real line
    # per task, from credentials_leaking_in_log.py's own ruamel-based
    # rewrite) -- this makes the pipeline's single most security-relevant
    # finding point at the actual task instead of just "somewhere in this
    # file". credentials_leaking_in_log_warnings (plain strings, no line
    # data) stays available for backward-compatible consumers but is no
    # longer what findings.py builds from.
    for detail in metrics.get("credentials_leaking_in_log_details", []) or []:
        finding = _finding(
                file,
                detail.get("line", 1),
                "credentials-leaking-in-log",
                detail.get("message", ""),
            )
        for evidence_key in (
            "evidence_level", "semantic_status", "uncertainty_sources",
            "confidence_factors", "resolution_status", "resolution_scope",
            "resolution_evidence",
        ):
            if evidence_key in detail:
                finding[evidence_key] = detail[evidence_key]
        if detail.get("confidence"):
            finding["confidence"] = detail["confidence"]
        out.append(finding)

    # --- overriden_keys: use the RAW list from metrics (real start_line
    # per task), not result's collapsed count.
    for dup_task in metrics.get("overriden_keys", []) or []:
        task_name = dup_task.get("task_name", "Unknown")
        start_line = dup_task.get("start_line", 1)
        for key, lines in dup_task.get("duplicates", {}).items():
            out.append(
                _finding(
                    file,
                    lines[0] if lines else start_line,
                    "overriden-keys",
                    f"Task '{task_name}': key '{key}' duplicated on lines {lines}",
                )
            )

    # --- unused_include_vars warnings: file-level, no line data available ---
    for warning in pm.get("WarningUnusedIncludeVars", []) or []:
        out.append(_finding(file, 1, "unused-include-vars", warning))

    # --- missing_validate_certs: per-task details ---
    for detail in metrics.get("missing_validate_certs_details", []) or []:
        out.append(
            _finding(
                file,
                detail.get("line", 1),
                "missing-validate-certs",
                f"Task '{detail.get('task_name', 'Unknown')}': "
                f"{detail.get('issue', 'validate_certs disabled')} "
                f"(module={detail.get('module', '?')})",
            )
        )

    # --- deprecated_modules: per-task details ---
    for detail in metrics.get("deprecated_modules_details", []) or []:
        out.append(
            _finding(
                file,
                detail.get("line", 1),
                "deprecated-modules",
                f"Task '{detail.get('task_name', 'Unknown')}': "
                f"{detail.get('issue', 'deprecated module')}",
            )
        )
    for detail in metrics.get("redirected_modules_details", []) or []:
        out.append(
            _finding(
                file,
                detail.get("line", 1),
                "redirected-module",
                f"Task '{detail.get('task_name', 'Unknown')}': "
                f"{detail.get('issue', 'legacy module redirect')}",
            )
        )

    # --- missing_tags: per-task details ---
    for detail in metrics.get("missing_tags_details", []) or []:
        out.append(
            _finding(
                file,
                detail.get("line", 1),
                "missing-tags",
                f"Task '{detail.get('task_name', 'Unknown')}': "
                f"{detail.get('issue', 'no tags')}",
            )
        )

    # --- shell_instead_of_module: per-task details ---
    for detail in metrics.get("shell_instead_of_module_details", []) or []:
        out.append(
            _finding(
                file,
                detail.get("line", 1),
                "shell-instead-of-module",
                f"Task '{detail.get('task_name', 'Unknown')}': "
                f"{detail.get('issue', 'shell instead of module')} "
                f"(module: {detail.get('module', '?')}, "
                f"command: {detail.get('command', '?')})",
            )
        )

    # --- handler_issues: per-handler details ---
    for detail in metrics.get("missing_handlers_details", []) or []:
        out.append(
            _finding(
                file,
                detail.get("line", 1),
                "missing-handler",
                f"Notify '{detail.get('handler_name', '?')}': "
                f"{detail.get('issue', 'missing handler')}",
            )
        )
    for detail in metrics.get("unused_handlers_details", []) or []:
        out.append(
            _finding(
                file,
                detail.get("line", 1),
                "unused-handler",
                f"Handler '{detail.get('handler_name', '?')}': "
                f"{detail.get('issue', 'unused handler')}",
            )
        )

    paper_detail_rules = (
        ("complex_expressions_details", "complex-expression"),
        ("incomplete_tasks_details", "incomplete-task"),
        ("long_statements_details", "long-statement"),
        ("unstructured_modules_details", "unstructured-module"),
        ("empty_abstractions_details", "empty-abstraction"),
        ("excessive_nesting_details", "excessive-nesting"),
        ("missing_abstractions_details", "missing-abstraction"),
        ("broken_role_dependencies_details", "broken-role-dependency"),
        ("unguarded_variables_details", "unguarded-variable"),
        ("insecure_permissions_details", "insecure-permissions"),
        ("unsafe_file_writes_details", "unsafe-file-write"),
        ("default_credentials_details", "default-credentials"),
        ("non_idempotent_commands_details", "non-idempotent-command"),
        ("read_only_command_changes_details", "read-only-command-change"),
        ("silent_error_suppressions_details", "silent-error-suppression"),
        ("redundant_default_values_details", "redundant-default-value"),
        ("shell_environment_exports_details", "shell-environment-export"),
        ("undocumented_complex_tasks_details", "undocumented-complex-task"),
        ("unused_registered_variables_details", "unused-registered-variable"),
        ("unscoped_shell_variables_details", "unscoped-shell-variable"),
        ("invalid_task_attribute_types_details", "invalid-task-attribute-type"),
        ("invalid_numeric_values_details", "invalid-numeric-value"),
        ("missing_release_notes_details", "missing-release-note"),
        ("missing_bug_references_details", "missing-bug-reference"),
        ("invalid_depends_on_references_details", "invalid-depends-on-reference"),
        ("commit_message_format_issues_details", "commit-message-format"),
        ("removed_copyright_notices_details", "removed-copyright-notice"),
        ("missing_test_updates_details", "missing-test-update"),
        ("untested_override_changes_details", "untested-override-change"),
        ("variable_use_before_definition_details", "variable-use-before-definition"),
        ("unexpected_task_locations_details", "unexpected-task-location"),
        ("deprecated_module_options_details", "deprecated-module-option"),
        ("plaintext_sensitive_variables_details", "plaintext-sensitive-variable"),
        ("unpinned_ansible_dependencies_details", "unpinned-ansible-dependency"),
        (
            "role_variable_precedence_collisions_details",
            "role-variable-precedence-collision",
        ),
        ("become_scope_too_broad_details", "become-scope-too-broad"),
        ("loop_legacy_syntax_details", "loop-legacy-syntax"),
        ("molecule_test_absent_details", "molecule-test-absent"),
        ("role_readme_absent_details", "role-readme-absent"),
        ("galaxy_meta_incomplete_details", "galaxy-meta-incomplete"),
        ("variable_naming_convention_details", "variable-naming-convention"),
        ("vault_inline_overload_details", "vault-inline-overload"),
    )
    for details_key, rule_id in paper_detail_rules:
        for detail in metrics.get(details_key, []) or []:
            finding = _finding(
                    detail.get("file", file),
                    detail.get("line", 1),
                    rule_id,
                    detail.get(
                        "issue",
                        detail.get("message", RULE_CATALOG[rule_id]["description"]),
                    ),
                )
            for evidence_key in (
                "variable",
                "variable_classification",
                "legacy_concept_id",
                "attribute",
                "semantic_status",
                "uncertainty_sources",
                "confidence_factors",
                "resolution_status",
                "resolution_scope",
                "resolution_evidence",
                "sensitive_class",
                "evidence_level",
            ):
                if evidence_key in detail:
                    finding[evidence_key] = detail[evidence_key]
            if rule_id == "unguarded-variable":
                classification = detail.get("variable_classification")
                classification_metadata = VARIABLE_CLASSIFICATION_CATALOG.get(
                    classification
                )
                if classification_metadata:
                    finding["concept_id"] = classification
                    finding["legacy_concept_id"] = "unguarded-variable"
                    finding["severity"] = classification_metadata["level"]
                    finding["confidence"] = classification_metadata["confidence"]
                    finding["taxonomy"] = classification_metadata["taxonomy"]
                    finding["actionability"] = classification_metadata[
                        "actionability"
                    ]
                    finding["rule_maturity"] = classification_metadata["status"]
                    finding["remediation"] = classification_metadata["remediation"]
            if detail.get("confidence"):
                finding["confidence"] = detail["confidence"]
            out.append(finding)

    # --- playbook-level boolean/count smells: file-level (line 1) ---
    if pm.get("high_coupling"):
        coupling = metrics.get("high_coupling_metrics") or {}
        thresholds = metrics.get("high_coupling_thresholds") or {}
        out.append(
            _finding(
                file,
                1,
                "high-coupling",
                "Coupling evidence: "
                f"imports={coupling.get('Num_Imports', 0)} "
                f"(threshold={thresholds.get('Num_Imports', '?')}), "
                f"roles={coupling.get('Num_Roles', 0)} "
                f"(threshold={thresholds.get('Num_Roles', '?')}).",
            )
        )
    playbook_level_simple = [
        ("large_playbook", "large-playbook", "Playbook exceeds size thresholds"),
        (
            "complex_playbook",
            "complex-playbook",
            "Playbook exceeds complexity thresholds",
        ),
        (
            "insufficient_modularization",
            "insufficient-modularization",
            "Large playbook with many plays",
        ),
        ("duplicated_code", "duplicated-code", "Duplicate task blocks detected"),
        (
            "overriding_facts",
            "overriding-facts",
            "A set_fact variable is reassigned with a different value",
        ),
        (
            "unecessary_abstraction",
            "unnecessary-abstraction",
            "block: wraps exactly one task",
        ),
        (
            "missing_files_extension",
            "missing-file-extension",
            "File reference missing an extension",
        ),
        (
            "duplicate_task_names",
            "duplicate-task-names",
            "Multiple tasks share the same name",
        ),
        (
            "missing_bool_filters",
            "missing-bool-filters",
            "when: condition compares against quoted 'true'/'false'",
        ),
        (
            "similarityPlays",
            "incohesive-play",
            "A play's tasks span multiple unrelated module domains (high module-domain entropy)",
        ),
    ]
    for key, rule_id, label in playbook_level_simple:
        count = pm.get(key, 0)
        if count:
            out.append(_finding(file, 1, rule_id, f"{label} (count={count})"))

    for detail in metrics.get("unnecessary_set_fact_details", []):
        finding = _finding(
                file,
                detail.get("line", 1),
                "unnecessary-set-fact",
                detail.get("issue", "Unused set_fact variable detected"),
            )
        for evidence_key in (
            "variable", "semantic_status", "uncertainty_sources",
            "confidence_factors", "resolution_status", "resolution_scope",
            "resolution_evidence",
        ):
            if evidence_key in detail:
                finding[evidence_key] = detail[evidence_key]
        if detail.get("confidence"):
            finding["confidence"] = detail["confidence"]
        out.append(finding)

    if pm.get("incohesive_playbook") == 1:
        out.append(
            _finding(
                file,
                1,
                "incohesive-playbook",
                "A playbook's tasks span multiple unrelated module domains (high module-domain entropy)",
            )
        )

    # --- unnamed_play / unnamed_tasks: use the dedicated *_details lists
    # from metrics (real line numbers, from unnamed_play.py's/
    # unnamed_tasks.py's own ruamel-based checks) rather than trying to
    # infer this while walking result's play/task structure, where the
    # line field doesn't survive assess_code_smells()'s play_result/
    # task_result construction anyway (see the zip below for why that
    # matters for large-play/large-task instead).
    for detail in metrics.get("unnamed_play_details", []) or []:
        out.append(
            _finding(file, detail.get("line", 1), "unnamed-play", "A play has no name:")
        )
    for detail in metrics.get("unnamed_tasks_details", []) or []:
        out.append(
            _finding(file, detail.get("line", 1), "unnamed-task", "A task has no name:")
        )

    # --- play-level and task-level size/naming findings: result's
    # play_result/task_result dicts don't carry the real "line" field
    # through (assess_code_smells() drops it when building them), even
    # though the raw metrics["plays"] entries do. Zip the two structures
    # by index -- they're built one-to-one, in the same order, by
    # assess_code_smells()'s own loop over metrics["plays"] -- so real
    # line numbers can still be recovered instead of falling back to
    # line 1 for these two finding types now.
    result_plays = result["playbook"].get("plays", [])
    raw_plays = metrics.get("plays", [])
    for result_play, raw_play in zip(result_plays, raw_plays):
        play_name = result_play.get("play_name", "Unknown")
        raw_play_metrics = raw_play.get("play_metrics") or {}
        play_line = raw_play_metrics.get("line", 1)

        if result_play.get("metrics", {}).get("large_play"):
            out.append(
                _finding(
                    file,
                    play_line,
                    "large-play",
                    f"Play '{play_name}' exceeds size thresholds",
                )
            )

        result_tasks = result_play.get("tasks", [])
        raw_tasks = raw_play.get("task_metrics", [])
        for result_task, raw_task in zip(result_tasks, raw_tasks):
            task_name = result_task.get("task_name", "Unknown")
            task_line = raw_task.get("line", 1)
            tm = result_task.get("metrics", {})
            if tm.get("large_task"):
                out.append(
                    _finding(
                        file,
                        task_line,
                        "large-task",
                        f"Task '{task_name}' exceeds size thresholds",
                    )
                )
            if tm.get("long_task_name"):
                out.append(
                    _finding(
                        file,
                        task_line,
                        "long-task-name",
                        f"Task '{task_name}' name is too long",
                    )
                )
            if tm.get("inconsistent_naming_convention"):
                out.append(
                    _finding(
                        file,
                        task_line,
                        "inconsistent-naming-convention",
                        f"Task '{task_name}' or its play has excessive special characters",
                    )
                )

    # Fix A5: Apply # noqa suppressions from source file
    try:
        import pathlib
        yaml_text = pathlib.Path(yaml_file_path).read_text(encoding="utf-8")
        noqa_suppressions = _parse_noqa_suppressions(yaml_text)
        if noqa_suppressions:
            def _is_noqa_suppressed(finding):
                line = finding.get("line", 0)
                suppressed = noqa_suppressions.get(line)
                if not suppressed:
                    return False
                identifiers = {
                    finding.get("rule_id", ""),
                    finding.get("native_rule_id", ""),
                    finding.get("concept_id", ""),
                }
                return bool(suppressed & identifiers)
            out = [f for f in out if not _is_noqa_suppressed(f)]
    except (OSError, UnicodeDecodeError):
        pass

    return out
