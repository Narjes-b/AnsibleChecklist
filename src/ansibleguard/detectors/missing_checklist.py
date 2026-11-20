"""Conservative detectors for previously missing review-checklist criteria."""

from __future__ import annotations

from bisect import bisect_right
from pathlib import Path
import re

from ansibleguard.detector_config import load_detector_config
from ansibleguard.detectors.paper_candidates import (
    COMMON_VARIABLES,
    JINJA_RE,
    JINJA_WORDS,
    META_KEYS,
    VAR_RE,
    _collect_defined_variables,
    _line_for,
    _load,
    _module_keys,
    _runtime_uncertainty_sources,
)
from ansibleguard.role_context import resolve_role_context
from ansibleguard.jinja_semantics import conjunctive_defined_guards
from ansibleguard.detectors.source_lines import source_line


CONDITION_KEYS = {"changed_when", "failed_when", "until", "when"}
SET_FACT_MODULES = {"ansible.builtin.set_fact", "set_fact"}


def _task_sequences(document):
    """Yield linear task sequences whose order is statically meaningful."""
    if not isinstance(document, list):
        return
    for entry in document:
        if not isinstance(entry, dict):
            continue
        found_play_section = False
        for section in ("pre_tasks", "tasks", "post_tasks", "handlers"):
            tasks = entry.get(section)
            if isinstance(tasks, list):
                found_play_section = True
                yield [task for task in tasks if isinstance(task, dict)]
        if not found_play_section and "hosts" not in entry:
            yield [task for task in document if isinstance(task, dict)]
            return


def _task_sequence_contexts(document):
    """Yield linear sequences with their play-scoped static variables."""
    if not isinstance(document, list):
        return
    is_playbook = any(
        isinstance(entry, dict)
        and any(key in entry for key in ("hosts", "tasks", "pre_tasks", "post_tasks"))
        for entry in document
    )
    if not is_playbook:
        yield [task for task in document if isinstance(task, dict)], 0, set()
        return
    for play_index, entry in enumerate(document):
        if not isinstance(entry, dict):
            continue
        play_vars = set(entry.get("vars", {})) if isinstance(entry.get("vars"), dict) else set()
        for section in ("pre_tasks", "tasks", "post_tasks", "handlers"):
            tasks = entry.get(section)
            if isinstance(tasks, list):
                yield [task for task in tasks if isinstance(task, dict)], play_index, play_vars


def _task_definitions(task):
    definitions = set()
    if task.get("register"):
        definitions.add(str(task["register"]))
    for module in SET_FACT_MODULES:
        if isinstance(task.get(module), dict):
            definitions.update(str(key) for key in task[module])
    return definitions


def _expression_references(expression):
    body = expression[2:-2] if expression.startswith(("{{", "{%")) else expression
    guarded = set(
        re.findall(
            r"([A-Za-z_][\w]*)\s*(?:\|\s*(?:(?:[A-Za-z_][\w]*\.)*default|d)\b|"
            r"\bis\s+(?:(?:not\s+)?defined|undefined)\b)",
            body,
        )
    )
    references = set()
    for variable in VAR_RE.findall(body):
        if (
            variable in COMMON_VARIABLES
            or variable in JINJA_WORDS
            or variable in guarded
            or variable.startswith("ansible_")
        ):
            continue
        if re.search(
            rf"\|\s*{re.escape(variable)}\b"
            rf"|\b{re.escape(variable)}\s*\("
            rf"|\b{re.escape(variable)}\s*="
            rf"|\bis\s+(?:not\s+)?{re.escape(variable)}\b",
            body,
        ):
            continue
        references.add(variable)
    return references


def _task_references(task):
    references = set()

    def walk(value, key=None):
        if isinstance(value, dict):
            for child_key, child in value.items():
                if child_key in {"register", "name"}:
                    continue
                walk(child, child_key)
        elif isinstance(value, list):
            for child in value:
                walk(child, key)
        elif isinstance(value, str):
            expressions = JINJA_RE.findall(value)
            if key in CONDITION_KEYS:
                expressions.append(value)
            for expression in expressions:
                references.update(_expression_references(expression))

    walk(task)
    return references


def detect_variable_use_before_definition(
    path, symbol_index=None, repository_context=None, parsed_document=None
):
    """Report references to a result/fact that is only created by a later task.

    The rule intentionally ignores variables that have any visible static
    definition (play/task vars, role vars/defaults, inventory, or configured
    runtime variables). It also limits itself to linear task sections and does
    not guess across block/rescue/always control flow.
    """
    document, text = _load(path, parsed_document)
    known = load_detector_config(path)["rules"].get("known_variables", [])
    static_definitions = _collect_defined_variables(
        document,
        path,
        known,
        include_task_definitions=False,
        include_external_definitions=symbol_index is None,
        include_play_definitions=False,
    )
    details = []
    seen = set()
    task_offset = 0
    for sequence, play_index, play_vars in _task_sequence_contexts(document) or []:
        definitions_by_index = [_task_definitions(task) for task in sequence]
        definition_positions = {}
        for definition_index, definitions in enumerate(definitions_by_index):
            for variable in definitions:
                definition_positions.setdefault(variable, []).append(definition_index)
        defined_before = set()
        for index, task in enumerate(sequence):
            task_static = set(task.get("vars", {})) if isinstance(task.get("vars"), dict) else set()
            visible_static = set(static_definitions) | play_vars | task_static
            task_references = _task_references(task)
            if symbol_index is not None:
                visible_static.update(
                    variable for variable in task_references
                    if symbol_index.has_visible_static_definition(
                        variable, path, task_offset + index, play_index
                    )
                )
            same_task_guards = conjunctive_defined_guards(task.get("when"))
            for variable in sorted(task_references):
                positions = definition_positions.get(variable, ())
                future_position = bisect_right(positions, index)
                later_index = (
                    positions[future_position]
                    if future_position < len(positions)
                    else None
                )
                if (
                    variable in visible_static
                    or variable in defined_before
                    or variable in definitions_by_index[index]
                    or variable in same_task_guards
                    or later_index is None
                ):
                    continue
                identity = (id(task), variable)
                if identity in seen:
                    continue
                seen.add(identity)
                definition_task = sequence[later_index]
                detail = {
                        "line": source_line(
                            task, fallback=_line_for(text, task.get("name"))
                        ),
                        "task_name": task.get("name", "Unnamed task"),
                        "variable": variable,
                        "definition_line": source_line(
                            definition_task,
                            fallback=_line_for(text, definition_task.get("name")),
                        ),
                        "issue": (
                            f"Variable '{variable}' is used before the later task "
                            f"'{definition_task.get('name', 'Unnamed task')}' defines it."
                        ),
                    }
                uncertainty_sources = _runtime_uncertainty_sources(
                    repository_context, path, task_offset + index
                )
                if uncertainty_sources:
                    detail.update(
                        {
                            "semantic_status": "UNCERTAIN",
                            "resolution_status": "RUNTIME_CONTEXT_UNCERTAIN",
                            "resolution_scope": "repository-static",
                            "confidence": "low",
                            "uncertainty_sources": list(uncertainty_sources),
                            "resolution_evidence": {
                                "proved": ["later_static_definition"],
                                "blockers": list(uncertainty_sources),
                            },
                            "confidence_factors": {
                                "positive": ["later_static_definition"],
                                "negative": list(uncertainty_sources),
                            },
                        }
                    )
                else:
                    detail["semantic_status"] = "ORDERED_CONFLICT"
                    detail["resolution_status"] = "PROVEN_ORDERED_CONFLICT"
                    detail["resolution_scope"] = "repository-static"
                    detail["resolution_evidence"] = {
                        "proved": [
                            "use_precedes_definition",
                            "no_modeled_runtime_ambiguity",
                        ],
                        "blockers": [],
                    }
                details.append(detail)
            defined_before.update(definitions_by_index[index])
        task_offset += len(sequence)
    return len(details), details


def _role_location(path):
    context = resolve_role_context(path)
    if context is None:
        return None, None
    return context.root, context.section


def _imported_from_handler(path, repository_context):
    if repository_context is None:
        return False
    target = repository_context.file_context_for(path).relative_path
    for relationship in repository_context.include_relationships:
        if relationship.resolved_target != target:
            continue
        source = Path(repository_context.root) / relationship.source
        source_context = resolve_role_context(source, repository_context.root)
        if source_context is not None and source_context.section == "handlers":
            return True
    return False


def detect_unexpected_task_locations(
    path, repository_context=None, parsed_document=None
):
    """Detect document shapes or handler-only attributes in the wrong role file."""
    document, text = _load(path, parsed_document)
    role_root, section = _role_location(path)
    if role_root is None:
        return 0, []
    details = []
    # Only meta/main.yml is Ansible's role metadata contract. Custom
    # meta/*.yml files may intentionally contain list-shaped project data.
    is_role_meta_main = section == "meta" and Path(path).name in {
        "main.yml", "main.yaml",
    }
    if (
        section in {"defaults", "vars"} or is_role_meta_main
    ) and isinstance(document, list):
        details.append(
            {
                "line": 1,
                "section": section,
                "issue": f"Role {section}/ files must contain a mapping, not a task or play list.",
            }
        )
    if section in {"tasks", "handlers"} and isinstance(document, dict):
        details.append(
            {
                "line": 1,
                "section": section,
                "issue": f"Role {section}/ files must contain a task list, not a variable mapping.",
            }
        )
    if section in {"tasks", "handlers"} and isinstance(document, list):
        for entry in document:
            if isinstance(entry, dict) and "hosts" in entry:
                details.append(
                    {
                        "line": source_line(
                            entry,
                            fallback=_line_for(text, entry.get("name") or "hosts"),
                        ),
                        "section": section,
                        "issue": f"A play belongs in a playbook, not under a role's {section}/ directory.",
                    }
                )
            if (
                section == "tasks"
                and isinstance(entry, dict)
                and "listen" in entry
                and not _imported_from_handler(path, repository_context)
            ):
                details.append(
                    {
                        "line": source_line(
                            entry,
                            fallback=_line_for(text, entry.get("name") or "listen"),
                        ),
                        "section": section,
                        "issue": "A task using the handler-only 'listen' attribute belongs under handlers/.",
                    }
                )
    return len(details), details


def _configured_option_deprecations(path, module_name):
    configured = load_detector_config(path)["rules"].get(
        "deprecated_module_options", {}
    )
    if not isinstance(configured, dict):
        return {}
    short_name = module_name.rsplit(".", 1)[-1]
    value = configured.get(module_name, configured.get(short_name, {}))
    return value if isinstance(value, dict) else {}


def _option_deprecation(option_spec):
    if not isinstance(option_spec, dict):
        return None
    deprecated = option_spec.get("deprecated")
    if deprecated:
        return deprecated if isinstance(deprecated, dict) else {"why": str(deprecated)}
    removal = (
        option_spec.get("removed_in_version")
        or option_spec.get("removed_in")
        or option_spec.get("removed_at_date")
    )
    return {"removed_in": removal} if removal else None


def _deprecation_message(module_name, option, deprecation):
    replacement = (
        deprecation.get("alternative")
        or deprecation.get("replacement")
        or deprecation.get("use_instead")
    )
    removal = (
        deprecation.get("removed_in")
        or deprecation.get("removed_in_version")
        or deprecation.get("version")
        or deprecation.get("removed_at_date")
    )
    reason = deprecation.get("why") or deprecation.get("description")
    message = f"Option '{option}' of module '{module_name}' is deprecated."
    if replacement:
        message += f" Use '{replacement}' instead."
    if removal:
        message += f" Removal: {removal}."
    if reason:
        message += f" {reason}"
    return message


def detect_deprecated_module_options(
    path, parsed_document=None, repository_context=None, module_metadata=None
):
    """Use installed Ansible metadata plus project overrides for option deprecations."""
    document, text = _load(path, parsed_document)
    details = []
    for sequence in _task_sequences(document) or []:
        for task in sequence:
            module_keys = _module_keys(task)
            if not module_keys:
                continue
            module_name = str(module_keys[0])
            module_value = task.get(module_name)
            supplied = dict(module_value) if isinstance(module_value, dict) else {}
            if isinstance(task.get("args"), dict):
                supplied.update(task["args"])
            if not supplied:
                continue
            metadata_index = (
                repository_context.module_metadata
                if repository_context is not None else module_metadata or {}
            )
            metadata = metadata_index.get(module_name, {})
            doc = metadata.get("doc", {}) if isinstance(metadata, dict) else {}
            options = doc.get("options", {}) if isinstance(doc, dict) else {}
            configured = _configured_option_deprecations(path, module_name)
            for option in supplied:
                deprecation = _option_deprecation(options.get(option))
                if option in configured:
                    override = configured[option]
                    deprecation = override if isinstance(override, dict) else {"why": str(override)}
                if not deprecation:
                    continue
                details.append(
                    {
                        "line": _line_for(text, task.get("name")),
                        "task_name": task.get("name", "Unnamed task"),
                        "module": module_name,
                        "option": str(option),
                        "issue": _deprecation_message(module_name, option, deprecation),
                    }
                )
    return len(details), details


def detect_missing_checklist_smells(
    path, symbol_index=None, repository_context=None, parsed_document=None,
    enabled_rules=None,
):
    detectors = {
        "variable_use_before_definition": ("variable-use-before-definition", lambda value: detect_variable_use_before_definition(
            value,
            symbol_index=symbol_index,
            repository_context=repository_context,
            parsed_document=parsed_document,
        )),
        "unexpected_task_locations": ("unexpected-task-location", lambda value: detect_unexpected_task_locations(
            value, repository_context=repository_context,
            parsed_document=parsed_document,
        )),
        "deprecated_module_options": ("deprecated-module-option", lambda value: detect_deprecated_module_options(
            value, parsed_document=parsed_document,
            repository_context=repository_context,
        )),
    }
    result = {}
    selected = set(enabled_rules) if enabled_rules is not None else None
    for metric, (rule_id, detector) in detectors.items():
        count, details = (
            (0, [])
            if selected is not None and rule_id not in selected
            else detector(path)
        )
        result[metric] = count
        result[f"{metric}_details"] = details
    return result
