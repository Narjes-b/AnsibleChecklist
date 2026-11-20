from ansibleguard.detectors.detect_large_playbook import calculate_metrics_playbook
from ansibleguard.detectors.detect_large_play import calculate_metrics_play
from ansibleguard.detectors.large_task import calculate_metrics_task
from ansibleguard.detectors.high_coupling import high_coupling
from ansibleguard.detectors.duplicate_code import duplicate_code

# from include_vars import detect_unnecessary_include_vars

from ansibleguard.detectors.set_fact import unnecessary_set_fact_details

from ansibleguard.detectors.overriding_facts import overriding_facts

from ansibleguard.detectors.unnecessary_abs import unecessary_abs

from ansibleguard.detectors.unnamed_play import unnamed_play
from ansibleguard.detectors.is_unnamed import is_unnamed


from ansibleguard.detectors.unnamed_tasks import unnamed_tasks


from ansibleguard.detectors.overriden_keys import detect_duplicate_keys_per_task
from itertools import zip_longest

from ansibleguard.detectors.sem_cohesion import calculate_similarity
from ansibleguard.detectors.duplicate_task_names import repeated_task_names
from ansibleguard.detectors.files_extensions import extract_tasks_from_playbook

from ansibleguard.detectors.incohesive_plays import (
    calculate_similarity as calculate_similarity_plays,
)

# new
from pathlib import Path

from ansibleguard.detectors.filters_for_comparison import get_when_conditions
from ansibleguard.detectors.credentials_leaking_in_log import (
    detect_credentials_leaking_in_log,
)

from ansibleguard.detectors.include_vars import detect_unused_include_vars
from ansibleguard.detector_config import load_detector_config
from ansibleguard.detectors.missing_validate_certs import detect_missing_validate_certs
from ansibleguard.detectors.deprecated_modules import (
    detect_deprecated_modules,
    detect_redirected_modules,
)
from ansibleguard.detectors.missing_tags import detect_missing_tags
from ansibleguard.detectors.shell_instead_of_module import (
    detect_shell_instead_of_module,
)
from ansibleguard.detectors.handler_issues import detect_handler_issues
from ansibleguard.detectors.paper_candidates import detect_paper_candidates
from ansibleguard.detectors.review_checklist import detect_review_checklist_smells
from ansibleguard.detectors.partial_checklist import detect_partial_checklist_smells
from ansibleguard.detectors.missing_checklist import detect_missing_checklist_smells
from ansibleguard.detectors.file_kinds import detect_file_kind_smells
from ansibleguard.detectors.become_scope import detect_become_scope_too_broad
from ansibleguard.detectors.loop_legacy_syntax import detect_loop_legacy_syntax
from ansibleguard.detectors.molecule_test import detect_molecule_test_absent
from ansibleguard.detectors.role_documentation import detect_role_readme_absent
from ansibleguard.detectors.galaxy_meta import detect_galaxy_meta_incomplete
from ansibleguard.detectors.variable_naming import detect_variable_naming_convention
from ansibleguard.detectors.vault_structure import detect_vault_inline_overload
import pandas as pd
import csv
import json
import yaml
import time
import inspect
from ansibleguard.document import inspect_document
from ansibleguard.redaction import redact_sensitive_text


# Conservative dependency declarations. A legacy family is omitted until all
# of its emitted rules have been audited; omitted detectors continue to run.
DETECTOR_RULE_REQUIREMENTS = {
    "large-playbook": frozenset({
        "large-playbook", "complex-playbook", "insufficient-modularization",
    }),
    "large-play": frozenset({"large-play"}),
    "large-task": frozenset({
        "large-task", "long-task-name", "inconsistent-naming-convention",
    }),
    "high-coupling": frozenset({"high-coupling"}),
    "duplicated-code": frozenset({"duplicated-code"}),
    "unnecessary-set-fact": frozenset({"unnecessary-set-fact"}),
    "overriding-facts": frozenset({"overriding-facts"}),
    "unnecessary-abstraction": frozenset({"unnecessary-abstraction"}),
    "incohesive-playbook": frozenset({"incohesive-playbook"}),
    "missing-file-extension": frozenset({"missing-file-extension"}),
    "unnamed-play": frozenset({"unnamed-play"}),
    "unnamed-task": frozenset({"unnamed-task"}),
    "duplicate-mapping-key": frozenset({"overriden-keys"}),
    "duplicate-task-name": frozenset({"duplicate-task-names"}),
    "missing-bool-filters": frozenset({"missing-bool-filters"}),
    "incohesive-play": frozenset({"incohesive-play"}),
    "credential-log-exposure": frozenset({"credentials-leaking-in-log"}),
    "unused-include-vars": frozenset({"unused-include-vars"}),
    "missing-validate-certs": frozenset({"missing-validate-certs"}),
    "deprecated-modules": frozenset({"deprecated-modules"}),
    "redirected-module": frozenset({"redirected-module"}),
    "missing-tags": frozenset({"missing-tags"}),
    "shell-module-migration": frozenset({"shell-instead-of-module"}),
    "handler-issues": frozenset({"missing-handler", "unused-handler"}),
    "file-kind-family": frozenset({
        "plaintext-sensitive-variable", "unpinned-ansible-dependency",
    }),
    "become-scope-too-broad": frozenset({"become-scope-too-broad"}),
    "loop-legacy-syntax": frozenset({"loop-legacy-syntax"}),
    "molecule-test-absent": frozenset({"molecule-test-absent"}),
    "role-readme-absent": frozenset({"role-readme-absent"}),
    "galaxy-meta-incomplete": frozenset({"galaxy-meta-incomplete"}),
    "variable-naming-convention": frozenset({"variable-naming-convention"}),
    "vault-inline-overload": frozenset({"vault-inline-overload"}),
    "paper-candidate-family": frozenset({
        "complex-expression", "incomplete-task", "long-statement",
        "unstructured-module", "empty-abstraction", "excessive-nesting",
        "missing-abstraction", "broken-role-dependency", "unguarded-variable",
    }),
    "review-checklist-family": frozenset({
        "insecure-permissions", "unsafe-file-write", "default-credentials",
        "non-idempotent-command", "read-only-command-change",
        "silent-error-suppression", "redundant-default-value",
        "shell-environment-export", "undocumented-complex-task",
    }),
    "partial-checklist-family": frozenset({
        "unused-registered-variable", "unscoped-shell-variable",
        "invalid-task-attribute-type", "invalid-numeric-value",
    }),
    "missing-checklist-family": frozenset({
        "variable-use-before-definition", "unexpected-task-location",
        "deprecated-module-option",
    }),
}

DETECTOR_SERVICE_REQUIREMENTS = {
    detector: frozenset({"parsed_yaml"})
    for detector in DETECTOR_RULE_REQUIREMENTS
}
DETECTOR_SERVICE_REQUIREMENTS.update({
    "unnecessary-set-fact": frozenset({"parsed_yaml", "symbol_graph"}),
    "unused-include-vars": frozenset({"parsed_yaml", "repository_context"}),
    "incohesive-play": frozenset({"parsed_yaml", "cohesion_model"}),
    "incohesive-playbook": frozenset({"parsed_yaml", "cohesion_model"}),
    "paper-candidate-family": frozenset({"parsed_yaml", "symbol_graph", "repository_context"}),
    "review-checklist-family": frozenset({"parsed_yaml", "symbol_graph", "repository_context"}),
    "partial-checklist-family": frozenset({"parsed_yaml", "symbol_graph"}),
    "missing-checklist-family": frozenset({"parsed_yaml", "symbol_graph", "repository_context", "module_metadata"}),
})

##def read_specific_values():
##  specific_values = {}
# with open(
#   "/Users/narjes/Documents/Research/Contrib_AnsibleSmells/AnsibleCodeSmells-master/CodeSmellsTool/thresholds.csv",
#  "r",
# ) as f:
#   csvreader = csv.reader(f)
#  next(csvreader)
# for row in csvreader:
#    key, value = row[0], int(row[1])
#   specific_values[key] = value
#  return specific_values


def mainn(
    yaml_file_path,
    symbol_index=None,
    include_cohesion=True,
    enabled_rules=None,
    parsed_document=None,
    repository_context=None,
    fail_on_detector_error=False,
):
    document_info = parsed_document or inspect_document(yaml_file_path)
    if not document_info.structurally_analyzable:
        detail = "; ".join(document_info.diagnostics)
        print(
            f"Skipping structural analysis for {yaml_file_path}: "
            f"{document_info.parse_status}/{document_info.document_type}"
            + (f" ({detail})" if detail else "")
        )
        return None
    playbook = document_info.document
    detector_diagnostics = []
    detector_timings = {}
    detectors_skipped = []
    selected_rules = set(enabled_rules) if enabled_rules is not None else None

    def isolated(detector, operation, default):
        required_rules = DETECTOR_RULE_REQUIREMENTS.get(detector)
        if (
            selected_rules is not None
            and required_rules is not None
            and selected_rules.isdisjoint(required_rules)
        ):
            detectors_skipped.append(detector)
            return default
        started = time.perf_counter()
        try:
            return operation()
        except Exception as exc:
            if fail_on_detector_error:
                raise
            detector_diagnostics.append(
                {
                    "category": "INTERNAL_DETECTOR_EXCEPTION",
                    "detector": detector,
                    "stage": "internal-detectors",
                    "exception_type": type(exc).__name__,
                    "message": redact_sensitive_text(exc),
                    "file": str(yaml_file_path),
                }
            )
            return default
        finally:
            detector_timings[detector] = (
                detector_timings.get(detector, 0.0)
                + time.perf_counter() - started
            )

    is_task_only_playbook = isinstance(playbook, list) and all(
        isinstance(task, dict) and "hosts" not in task and "tasks" not in task
        for task in playbook
    )

    metrics_playbook = isolated(
        "large-playbook",
        lambda: calculate_metrics_playbook(yaml_file_path, parsed_document=document_info),
        {},
    )
    # print("metrics_playbook:", metrics_playbook)
    metrics_play = None

    if not is_task_only_playbook:
        metrics_play = isolated(
            "large-play", lambda: calculate_metrics_play(
                yaml_file_path, parsed_document=document_info
            ), None
        )
        # print("metrics_play:", metrics_play)
    metrics_task, taskss = isolated(
        "large-task", lambda: calculate_metrics_task(
            yaml_file_path, parsed_document=document_info
        ), ([], [])
    )
    # print("metrics_task:", metrics_task)
    metrics_high_coupling = isolated(
        "high-coupling",
        lambda: high_coupling(yaml_file_path, parsed_document=document_info),
        {},
    )
    configured_thresholds = load_detector_config(yaml_file_path)["thresholds"]
    duplicated_code = isolated(
        "duplicated-code",
        lambda: duplicate_code(yaml_file_path, parsed_document=document_info),
        0,
    )
    unnecessary_set_fact_rows = isolated(
        "unnecessary-set-fact",
        lambda: unnecessary_set_fact_details(
            yaml_file_path,
            symbol_index=symbol_index,
            repository_context=repository_context,
            parsed_document=document_info,
        ),
        [],
    )
    unecessary_set_fact = (
        len(unnecessary_set_fact_rows)
        if unnecessary_set_fact_rows is not None
        else None
    )
    overriding_fact = isolated(
        "overriding-facts",
        lambda: overriding_facts(yaml_file_path, parsed_document=document_info),
        0,
    )
    unecessary_abst = isolated(
        "unnecessary-abstraction",
        lambda: unecessary_abs(yaml_file_path, parsed_document=document_info),
        0,
    )
    similarityPlaybook = (
        isolated(
            "incohesive-playbook",
            lambda: calculate_similarity(
                yaml_file_path, parsed_document=document_info
            ),
            None,
        )
        if include_cohesion else None
    )
    extension = isolated(
        "missing-file-extension",
        lambda: extract_tasks_from_playbook(
            yaml_file_path, parsed_document=document_info
        ),
        0,
    )
    unnamedPlay, unnamedPlayDetails = isolated(
        "unnamed-play", lambda: unnamed_play(yaml_file_path, parsed_document=document_info), (0, [])
    )
    unnamedTasks, unnamedTasksDetails = isolated(
        "unnamed-task", lambda: unnamed_tasks(yaml_file_path, parsed_document=document_info), (0, [])
    )
    overridenKeys = isolated(
        "duplicate-mapping-key",
        lambda: detect_duplicate_keys_per_task(yaml_file_path, parsed_document=document_info),
        [],
    )
    duplicate_task_names = isolated(
        "duplicate-task-name", lambda: repeated_task_names(yaml_file_path, parsed_document=document_info), 0
    )
    missing_bool_filters = isolated(
        "missing-bool-filters",
        lambda: get_when_conditions(
            yaml_file_path, parsed_document=document_info
        ),
        0,
    )
    similarityPlays = (
        isolated(
            "incohesive-play",
            lambda: calculate_similarity_plays(
                yaml_file_path, parsed_document=document_info
            ),
            None,
        )
        if include_cohesion else None
    )
    warnings, nbLeaks, credentialsLeakDetails = isolated(
        "credential-log-exposure",
        lambda: (
            detect_credentials_leaking_in_log(
                yaml_file_path,
                module_metadata=(
                    repository_context.module_metadata
                    if repository_context is not None else None
                ),
                parsed_document=document_info,
                repository_context=repository_context,
            )
            if "parsed_document" in inspect.signature(
                detect_credentials_leaking_in_log
            ).parameters
            else detect_credentials_leaking_in_log(
                yaml_file_path,
                module_metadata=(
                    repository_context.module_metadata
                    if repository_context is not None else None
                ),
            )
        ),
        ([], 0, []),
    )
    unused_include_vars, WarningUnusedIncludeVars = isolated(
        "unused-include-vars",
        lambda: detect_unused_include_vars(
            yaml_file_path,
            vars_folder=None,
            symbol_index=symbol_index,
            repository_context=repository_context,
            parsed_document=document_info,
        ),
        (0, []),
    )
    missing_certs_count, missing_certs_details = isolated(
        "missing-validate-certs",
        lambda: detect_missing_validate_certs(yaml_file_path, parsed_document=document_info),
        (0, []),
    )
    deprecated_mod_count, deprecated_mod_details = isolated(
        "deprecated-modules", lambda: detect_deprecated_modules(
            yaml_file_path, parsed_document=document_info,
            repository_context=repository_context,
        ), (0, [])
    )
    redirected_mod_count, redirected_mod_details = isolated(
        "redirected-module", lambda: detect_redirected_modules(yaml_file_path, parsed_document=document_info), (0, [])
    )
    missing_tags_count, missing_tags_details = isolated(
        "missing-tags", lambda: detect_missing_tags(yaml_file_path, parsed_document=document_info), (0, [])
    )
    shell_mod_count, shell_mod_details = isolated(
        "shell-module-migration",
        lambda: detect_shell_instead_of_module(yaml_file_path, parsed_document=document_info),
        (0, []),
    )
    (
        missing_handler_count,
        missing_handler_details,
        unused_handler_count,
        unused_handler_details,
    ) = isolated(
        "handler-issues", lambda: detect_handler_issues(yaml_file_path, parsed_document=document_info),
        (0, [], 0, []),
    )
    paper_candidate_metrics = isolated(
        "paper-candidate-family",
        lambda: detect_paper_candidates(
            yaml_file_path,
            symbol_index=symbol_index,
            parsed_document=document_info,
            repository_context=repository_context,
            enabled_rules=enabled_rules,
        ),
        {},
    )
    review_checklist_metrics = isolated(
        "review-checklist-family",
        lambda: detect_review_checklist_smells(
            yaml_file_path, symbol_index=symbol_index,
            parsed_document=document_info,
            repository_context=repository_context,
            enabled_rules=enabled_rules,
        ),
        {},
    )
    partial_checklist_metrics = isolated(
        "partial-checklist-family",
        lambda: detect_partial_checklist_smells(
            yaml_file_path, enabled_rules=enabled_rules, symbol_index=symbol_index,
            parsed_document=document_info,
            repository_context=repository_context,
        ),
        {},
    )
    missing_checklist_metrics = isolated(
        "missing-checklist-family",
        lambda: detect_missing_checklist_smells(
            yaml_file_path,
            symbol_index=symbol_index,
            repository_context=repository_context,
            parsed_document=document_info,
            enabled_rules=enabled_rules,
        ),
        {},
    )
    file_kind_metrics = isolated(
        "file-kind-family",
        lambda: detect_file_kind_smells(
            yaml_file_path, parsed_document=document_info
        ),
        {},
    )
    become_scope_count, become_scope_details = isolated(
        "become-scope-too-broad",
        lambda: detect_become_scope_too_broad(yaml_file_path, parsed_document=document_info), (0, []),
    )
    loop_legacy_count, loop_legacy_details = isolated(
        "loop-legacy-syntax", lambda: detect_loop_legacy_syntax(yaml_file_path, parsed_document=document_info), (0, [])
    )
    molecule_test_count, molecule_test_details = isolated(
        "molecule-test-absent", lambda: detect_molecule_test_absent(yaml_file_path), (0, [])
    )
    role_readme_count, role_readme_details = isolated(
        "role-readme-absent", lambda: detect_role_readme_absent(yaml_file_path), (0, [])
    )
    galaxy_meta_count, galaxy_meta_details = isolated(
        "galaxy-meta-incomplete",
        lambda: detect_galaxy_meta_incomplete(
            yaml_file_path, parsed_document=document_info
        ),
        (0, []),
    )
    var_naming_count, var_naming_details = isolated(
        "variable-naming-convention",
        lambda: detect_variable_naming_convention(
            yaml_file_path, parsed_document=document_info
        ),
        (0, []),
    )
    vault_inline_count, vault_inline_details = isolated(
        "vault-inline-overload",
        lambda: detect_vault_inline_overload(
            yaml_file_path, repository_context=repository_context
        ),
        (0, []),
    )

    main_metrics = {
        "playbook_metrics": metrics_playbook,
        "high_coupling_metrics": metrics_high_coupling,
        # Report the threshold the detector actually compared against: the
        # project configuration when it sets one, otherwise thresholds.csv.
        "high_coupling_thresholds": {
            key: configured_thresholds.get(key)
            if configured_thresholds.get(key) is not None
            else _default_thresholds().get(key)
            for key in ("Num_Imports", "Num_Roles")
        },
        "similarity": similarityPlaybook,
        "duplicated_code": duplicated_code,
        "unecessary_set_fact": unecessary_set_fact,
        "unnecessary_set_fact_details": unnecessary_set_fact_rows or [],
        "overriding_facts": overriding_fact,
        "unecessary_abstraction": unecessary_abst,
        "missing_files_extension": extension,
        "unnamed_play": unnamedPlay,
        "unnamed_play_details": unnamedPlayDetails,
        "unnamed_tasks": unnamedTasks,
        "unnamed_tasks_details": unnamedTasksDetails,
        "overriden_keys": overridenKeys,
        "duplicate_task_names": duplicate_task_names,
        "missing_bool_filters": missing_bool_filters,
        "similarityPlays": similarityPlays,
        "credentials_leaking_in_log": nbLeaks,
        "credentials_leaking_in_log_warnings": warnings,
        "credentials_leaking_in_log_details": credentialsLeakDetails,
        "unused_include_vars": unused_include_vars,
        "WarningUnusedIncludeVars": WarningUnusedIncludeVars,
        "missing_validate_certs": missing_certs_count,
        "missing_validate_certs_details": missing_certs_details,
        "deprecated_modules": deprecated_mod_count,
        "deprecated_modules_details": deprecated_mod_details,
        "redirected_modules": redirected_mod_count,
        "redirected_modules_details": redirected_mod_details,
        "missing_tags": missing_tags_count,
        "missing_tags_details": missing_tags_details,
        "shell_instead_of_module": shell_mod_count,
        "shell_instead_of_module_details": shell_mod_details,
        "missing_handlers": missing_handler_count,
        "missing_handlers_details": missing_handler_details,
        "unused_handlers": unused_handler_count,
        "unused_handlers_details": unused_handler_details,
        **paper_candidate_metrics,
        **review_checklist_metrics,
        **partial_checklist_metrics,
        **missing_checklist_metrics,
        **file_kind_metrics,
        "become_scope_too_broad": become_scope_count,
        "become_scope_too_broad_details": become_scope_details,
        "loop_legacy_syntax": loop_legacy_count,
        "loop_legacy_syntax_details": loop_legacy_details,
        "molecule_test_absent": molecule_test_count,
        "molecule_test_absent_details": molecule_test_details,
        "role_readme_absent": role_readme_count,
        "role_readme_absent_details": role_readme_details,
        "galaxy_meta_incomplete": galaxy_meta_count,
        "galaxy_meta_incomplete_details": galaxy_meta_details,
        "variable_naming_convention": var_naming_count,
        "variable_naming_convention_details": var_naming_details,
        "vault_inline_overload": vault_inline_count,
        "vault_inline_overload_details": vault_inline_details,
        "plays": [],
        "_detector_diagnostics": detector_diagnostics,
        "_detector_timings": dict(sorted(detector_timings.items())),
        "_detectors_skipped": sorted(detectors_skipped),
        "_detector_service_requirements": {
            detector: sorted(DETECTOR_SERVICE_REQUIREMENTS[detector])
            for detector in sorted(set(detector_timings) | set(detectors_skipped))
            if detector in DETECTOR_SERVICE_REQUIREMENTS
        },
    }

    if metrics_play:
        # task_counts = [count_tasks_in_playbook(play) for play in playbook]

        tasks_by_play_id = {}
        for task in metrics_task:
            play_id = task.get("play_id")
            if play_id not in tasks_by_play_id:
                tasks_by_play_id[play_id] = []
            tasks_by_play_id[play_id].append(task)

        # detect_large_play.py substitutes the placeholder string "unknown"
        # for Play_name when a play has no real name (so downstream display
        # code always has something to show). Calling is_unnamed() on that
        # already-substituted placeholder is wrong -- "unknown" is a
        # non-empty string, so is_unnamed("unknown") always returns 0,
        # silently masking every genuinely unnamed play. Confirmed this
        # directly: a real hosts:-only play with no name: reported
        # unnamed_play == 0. Use unnamedPlayDetails instead (built by
        # unnamed_play.py from a fresh, correct check against the raw
        # YAML, unaffected by this placeholder), matched by real line
        # number, which unnamed_play.py's ruamel-based rewrite now provides.
        unnamed_play_lines = {
            d["line"] for d in unnamedPlayDetails if d.get("line") is not None
        }

        for play in metrics_play["Plays"]:
            play_id = play.get("play_id")
            tasks_for_this_play = tasks_by_play_id.get(play_id, [])

            is_unnamed_Play = int(play.get("line") in unnamed_play_lines)

            play_entry = {
                "play_metrics": play,
                "unnamed_play": is_unnamed_Play,
                "task_metrics": tasks_for_this_play,
            }
            main_metrics["plays"].append(play_entry)
        # 🔁 handle top-level tasks without plays
        if -1 in tasks_by_play_id:
            main_metrics["plays"].append(
                {
                    "play_metrics": None,
                    "unnamed_play": None,
                    "task_metrics": tasks_by_play_id[-1],
                }
            )
    else:
        play_entry = {
            "play_metrics": None,
            "unnamed_play": None,
            "task_metrics": metrics_task,
        }
        main_metrics["plays"].append(play_entry)
    # print("main_metrics:", main_metrics)

    return main_metrics


if __name__ == "__main__":
    from ansibleguard.config import TEST_PLAYBOOK

    metrics_playbook = mainn(TEST_PLAYBOOK)
    if metrics_playbook:
        print(metrics_playbook)


def _default_thresholds():
    """Thresholds shipped in ``thresholds.csv`` (the detector defaults)."""
    from .smells import read_thresholds

    return read_thresholds()
