"""Versioned source units for local explanations, without executing Ansible.

YAML nodes retain original coordinates. Ambiguous aliases, duplicate mappings,
and unknown runtime inputs are evidence limitations, never proof of a defect.
"""
from __future__ import annotations

import hashlib
import json
import re
import textwrap
from types import SimpleNamespace

import yaml
from jinja2 import Environment, TemplateSyntaxError, nodes as jinja_nodes
from yaml.nodes import MappingNode, ScalarNode, SequenceNode

from ..task_semantics import TASK_META_KEYS

PACKET_VERSION = 3
DEEP_RULES = frozenset({
    "missing-validate-certs", "insecure-permissions", "credential-log-exposure",
    "credentials-leaking-in-log", "unguarded-variable", "variable-use-before-definition",
    "undeclared-input-contract", "unresolved-runtime-input",
})


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode()).hexdigest()


def pairs(node):
    return {key.value: value for key, value in node.value
            if isinstance(key, ScalarNode)} if isinstance(node, MappingNode) else {}


def span(node):
    return [node.start_mark.line + 1,
            max(node.start_mark.line + 1, node.end_mark.line + bool(node.end_mark.column))]


def numbered(lines, start, end):
    return "\n".join(f"{n:5d} | {lines[n - 1]}" for n in range(start, end + 1))


def module_arguments(fields):
    """Bind arguments to the actual action, excluding vars/environment maps."""
    for key in ("action", "local_action"):
        if key in fields:
            args = pairs(fields[key])
            module = args.pop("module", None)
            return (module.value if isinstance(module, ScalarNode) else None), args
    modules = [(key, pairs(value)) for key, value in fields.items() if key not in TASK_META_KEYS]
    if len(modules) != 1:
        return None, {}
    module, args = modules[0]
    extra = pairs(fields.get("args"))
    if any(key in args for key in extra):
        return None, {}  # Conflicting argument sources require explicit resolution.
    return module, {**args, **extra}


def referenced_names(node):
    """Find case-sensitive Jinja load nodes without evaluating any expression."""
    environment, names = Environment(), set()
    stack = [(None, node)]
    while stack:
        key, current = stack.pop()
        if isinstance(current, MappingNode):
            stack.extend((field.value, value) for field, value in current.value if isinstance(field, ScalarNode))
        elif isinstance(current, SequenceNode):
            stack.extend((key, child) for child in current.value)
        elif isinstance(current, ScalarNode):
            text = current.value
            if key in {"when", "failed_when", "changed_when", "until"} and "{{" not in text:
                text = "{{ " + text + " }}"
            if "{{" not in text and "{%" not in text:
                continue
            try:
                names.update(item.name for item in environment.parse(text).find_all(jinja_nodes.Name) if item.ctx == "load")
            except TemplateSyntaxError:
                continue
    return names


def definition_span(document, definition, name):
    """Bind through typed containers even when the graph has a wrapper line."""
    container = None
    if definition.kind in {"defaults-file", "role-vars-file", "group_vars-file", "host_vars-file", "env_vars-file", "included-vars"}:
        container = document
    elif definition.kind == "play-vars" and isinstance(document, SequenceNode):
        if definition.play is not None and definition.play < len(document.value):
            container = pairs(document.value[definition.play]).get("vars")
    elif definition.task is not None:
        units = [unit for unit in task_units(document) if unit["task"] == definition.task
                 and (definition.play is None or unit["play"] == definition.play)
                 and (definition.task_path is None or unit["task_path"] == definition.task_path)]
        if len(units) == 1:
            fields = units[0]["fields"]
            if definition.kind == "task-vars":
                container = fields.get("vars")
            elif definition.kind == "set-fact":
                container = next((value for key, value in fields.items() if key.rsplit(".", 1)[-1] == "set_fact"), None)
            elif definition.kind == "register":
                node = fields.get("register")
                if isinstance(node, ScalarNode) and node.value == name:
                    return span(node)
    if isinstance(container, MappingNode):
        matches = [(key, value) for key, value in container.value if isinstance(key, ScalarNode) and key.value == name]
        if len(matches) == 1:
            key, value = matches[0]
            return [key.start_mark.line + 1, span(value)[1]]
    return None


def _audit(node, active=None, seen=None, depth=0):
    active, seen = active or set(), seen if seen is not None else set()
    if depth > 80:
        raise ValueError("YAML nesting exceeds evidence limit")
    if id(node) in seen:
        raise ValueError("YAML aliases need occurrence-specific source identity")
    seen.add(id(node))
    if isinstance(node, MappingNode):
        keys = [key.value for key, _ in node.value if isinstance(key, ScalarNode)]
        if len(set(keys)) != len(keys) or "<<" in keys:
            raise ValueError("duplicate or merged mapping needs specialized evidence")
        children = [child for pair in node.value for child in pair]
    elif isinstance(node, SequenceNode):
        children = node.value
    else:
        children = []
    for child in children:
        _audit(child, active, seen, depth + 1)


def task_units(document):
    """Yield units in the symbol graph's wrapper-inclusive declaration order."""
    entries = document.value if isinstance(document, SequenceNode) else [document]
    ordinal = 0

    def walk(sequence, play, inherited, prefix=()):
        nonlocal ordinal
        for position, task in enumerate(sequence):
            if not isinstance(task, MappingNode):
                continue
            fields = pairs(task)
            path = (*prefix, position)
            context = dict(inherited)
            for key in ("no_log", "when", "module_defaults", "vars", "environment"):
                if key in fields:
                    if key == "when" and key in context:
                        context[f"ancestor-when-{span(context[key])[0]}"] = context[key]
                    context[key] = fields[key]
            start, end = span(task)
            # A YAML collection's end mark can point at the next sibling's
            # indented first line. That line belongs to the next task.
            if position + 1 < len(sequence):
                following = sequence[position + 1]
                if following.start_mark.line > task.start_mark.line:
                    end = min(end, following.start_mark.line)
            unit = {"node": task, "fields": fields, "play": play, "source_span": [start, end],
                    "task": ordinal, "task_path": path, "inherited": context}
            ordinal += 1
            yield unit
            for branch, key in enumerate(("block", "rescue", "always")):
                child = fields.get(key)
                if isinstance(child, SequenceNode):
                    yield from walk(child.value, play, context, (*path, branch))

    for play, entry in enumerate(entries):
        fields = pairs(entry)
        is_play = "hosts" in fields or any(key in fields for key in ("tasks", "pre_tasks", "post_tasks", "handlers"))
        if is_play:
            sequence = [task for key in ("pre_tasks", "tasks", "post_tasks", "handlers")
                        for task in (fields[key].value if isinstance(fields.get(key), SequenceNode) else [])]
            inherited = {key: fields[key] for key in ("no_log", "when", "module_defaults", "vars", "environment") if key in fields}
            yield from walk(sequence, play, inherited)
        else:
            # Task files are one sequence, not one separate play per entry.
            yield from walk(entries, 0, {})
            return


def _verify_local_predicate(packet, unit, lines):
    """Reuse existing rules on the supplied leaf, with no source-file reread.

    Certify only direct module mappings with explicit literal controls. Opaque
    value flow, dynamic settings, action syntax and cross-task effects remain
    outside this bounded check. This is the tool's policy, not human defect gold.
    """
    if packet["missing"] or packet["unit"]["kind"] != "task":
        return
    module, _arguments = module_arguments(unit["fields"])
    if not module or module not in unit["fields"] or "args" in unit["fields"]:
        return
    source = textwrap.dedent("\n".join(lines[packet["unit"]["start"] - 1:packet["unit"]["end"]]))
    from ..document import AnsibleSafeLoader
    document = yaml.load(source, Loader=AnsibleSafeLoader)
    if not isinstance(document, list) or len(document) != 1 or not isinstance(document[0], dict):
        return
    parsed = SimpleNamespace(document=document, source_text=source)
    kind, matched = None, None
    if packet["rule"] == "insecure-permissions" and packet.get("permissions"):
        from ..detectors.review_checklist import detect_insecure_permissions
        matched = bool(detect_insecure_permissions("__packet__.yml", parsed_document=parsed)[0])
        kind = "static-permission-policy"
    elif packet["rule"] in {"credential-log-exposure", "credentials-leaking-in-log"} and module.rsplit(".", 1)[-1] == "debug":
        node = unit["inherited"].get("no_log")
        if not isinstance(node, ScalarNode) or node.tag != "tag:yaml.org,2002:bool":
            return
        protected = node.value.lower() in {"true", "yes", "on"}
        from ..detectors.credentials_leaking_in_log import (
            _display_sensitive_references, detect_credentials_leaking_in_log,
        )
        # Without protection, only a direct sensitive-name reference is closed
        # under this unit. A generic register alias may require another task.
        if not protected and not _display_sensitive_references(document[0].get(module)):
            return
        document[0]["no_log"] = protected  # Explicit fact from the supplied ancestor/task.
        matched = bool(detect_credentials_leaking_in_log("__packet__.yml", module_metadata={},
            parsed_document=parsed, repository_context=SimpleNamespace(parsed_documents={}))[1])
        kind = "static-direct-display-policy"
    if kind is not None:
        packet["condition_hint"] = "supported" if matched else "unsupported"
        packet["predicate_check"] = {"status": "verified", "kind": kind,
                                     "assessment": packet["condition_hint"]}


def build_packet(occurrence, lines, read_lines, graph_factory):
    file = occurrence.get("file")
    rule = (occurrence.get("concept_id") or occurrence.get("rule_id") or "").removeprefix("ansibleguard/")
    packet = {"version": PACKET_VERSION, "rule": rule, "contract_version": 5,
              "file": file, "source_lines_sha256": digest(lines), "coverage": "specialized" if rule in DEEP_RULES else "generic",
              "unit": None, "dependencies": [], "missing": [], "limitations": [],
              "truncated": False, "condition_hint": None, "snippets": []}
    try:
        anchor = occurrence.get("line")
        if type(anchor) not in (int, str) or not re.fullmatch(r"[1-9][0-9]*", str(anchor)):
            raise ValueError("invalid source anchor")
        anchor = int(anchor)
        if not 1 <= anchor <= len(lines):
            raise ValueError("source anchor outside supplied file")
        documents = list(yaml.compose_all("\n".join(lines)))
        if len(documents) != 1 or documents[0] is None:
            raise ValueError("expected one YAML document")
        if not isinstance(documents[0], SequenceNode):
            raise ValueError("source is not a declared task or play sequence")
        _audit(documents[0])
        candidates = [unit for unit in task_units(documents[0]) if unit["source_span"][0] <= anchor <= unit["source_span"][1]]
        if not candidates:
            raise ValueError("anchor does not identify an Ansible task")
        minimum = min(item["source_span"][1] - item["source_span"][0] for item in candidates)
        nearest = [item for item in candidates if item["source_span"][1] - item["source_span"][0] == minimum]
        if len(nearest) != 1:
            raise ValueError("multiple tasks share the source anchor; exact task identity unavailable")
        unit = nearest[0]
        start, end = unit["source_span"]
        packet["unit"] = {"start": start, "end": end, "play": unit["play"], "task": unit["task"],
                          "task_path": unit["task_path"], "kind": "task",
                          "id": digest([file, packet["source_lines_sha256"], start, end])}
        if any(key in unit["fields"] for key in ("block", "rescue", "always")):
            packet["unit"]["kind"] = "block"
            packet["missing"].append("anchor identifies a block wrapper rather than the affected leaf task")
        context = numbered(lines, start, end)
        packet["snippets"].append({"file": file, "text": context})
        for key, node in unit["inherited"].items():
            a, b = span(node)
            if a < start or b > end:
                # Include the mapping key as well as its value.
                snippet = numbered(lines, a, b)
                packet["dependencies"].append({"file": file, "start": a, "end": b, "relation": f"inherited-{key}"})
                packet["snippets"].append({"file": file, "text": snippet})
                context += f"\nInherited {key}:\n{snippet}"
        if rule in {"unguarded-variable", "variable-use-before-definition", "undeclared-input-contract", "unresolved-runtime-input"}:
            _variables(packet, unit, occurrence, lines, read_lines, graph_factory)
            for dependency in packet["dependencies"]:
                if "source" in dependency:
                    snippet = dependency.pop("source")
                    context += f"\nScoped definition ({dependency['visibility']}) in {dependency['file']}:\n{snippet}"
                    packet["snippets"].append({"file": dependency["file"], "text": snippet})
        if rule == "missing-validate-certs":
            # Do not assume module_defaults or default behavior for absent values.
            module, arguments = module_arguments(unit["fields"])
            value = arguments.get("validate_certs")
            packet["module"] = module
            if module and isinstance(value, ScalarNode) and value.tag == "tag:yaml.org,2002:bool":
                packet["condition_hint"] = "supported" if value.value.lower() in {"false", "no", "off"} else "unsupported"
                packet["predicate_check"] = {"status": "verified", "kind": "literal-tls-setting",
                                             "assessment": packet["condition_hint"]}
            else:
                packet["missing"].append("literal validate_certs value and applicable module/defaults contract")
        if rule in {"credential-log-exposure", "credentials-leaking-in-log"}:
            packet["condition_question"] = (
                "Does this task handle or display sensitive-looking material without effective no_log:true? "
                "This is a static risk pattern, not proof of a deployed secret leak."
            )
            packet["limitations"].append("sensitive-value flow and custom module redaction are not certified")
            node = unit["inherited"].get("no_log")
            packet["effective_no_log"] = node.value if isinstance(node, ScalarNode) else None
            if node is not None and (not isinstance(node, ScalarNode) or node.tag != "tag:yaml.org,2002:bool"):
                packet["missing"].append("runtime value of effective no_log")
            if isinstance(node, ScalarNode) and node.tag == "tag:yaml.org,2002:bool" and node.value.lower() in {"true", "yes", "on"}:
                packet["condition_hint"] = "unsupported"
        if rule == "insecure-permissions":
            packet["condition_question"] = "Does the task match the declared insecure-permissions bit policy?"
            packet["predicate_policy"] = (
                "World-write; setuid on non-directories; or setgid unless a directory has a declared group "
                "and no world-write. Group-write alone does not match. Read-bit checks require supplied "
                "evidence of private/sensitive material, not a hypothetical sensitive use. Deployment harm is separate."
            )
            from ..detectors.review_checklist import _mode_to_int, MODE_MODULES
            module, arguments = module_arguments(unit["fields"])
            values = [(module, arguments)] if module and module.rsplit(".", 1)[-1] in MODE_MODULES else []
            packet["permissions"] = []
            for module, fields in values:
                mode = fields.get("mode")
                value = mode.value if isinstance(mode, ScalarNode) else None
                # Preserve YAML scalar typing for the detector's octal conversion.
                typed = yaml.safe_load(value) if mode is not None and mode.tag == "tag:yaml.org,2002:int" else value
                number = _mode_to_int(typed)
                packet["permissions"].append({"module": module, "mode": value,
                    "mode_tag": mode.tag if mode else None, "mode_bits": number,
                    "world_writable": bool(number & 0o002) if number is not None else None,
                    "setuid": bool(number & 0o4000) if number is not None else None,
                    "setgid": bool(number & 0o2000) if number is not None else None,
                    "state": fields["state"].value if isinstance(fields.get("state"), ScalarNode) else None,
                    "explicit_group": "group" in fields})
                if number is None:
                    packet["missing"].append("literal permission bits or runtime mode contract")
            if not values:
                packet["missing"].append("recognized file-permission module and arguments")
            packet["limitations"].append("permission risk depends on file sensitivity and intended sharing policy")
        if rule not in DEEP_RULES:
            packet["limitations"].append("generic source unit; no specialized decision-completeness contract")
        if rule in {"insecure-permissions", "credential-log-exposure", "credentials-leaking-in-log"}:
            _verify_local_predicate(packet, unit, lines)
        if rule in {"credential-log-exposure", "credentials-leaking-in-log"} and not packet.get("predicate_check"):
            node = unit["inherited"].get("no_log")
            if isinstance(node, ScalarNode) and node.tag == "tag:yaml.org,2002:bool" and node.value.lower() in {"true", "yes", "on"}:
                packet["predicate_check"] = {"status": "verified", "kind": "literal-output-protection", "assessment": "unsupported"}
            else:
                packet["missing"].append("module argument redaction and sensitive-value flow contract")
        variable = packet.get("variable") or {}
        if (not packet["missing"] and variable.get("visibility") == "must"
                and any(dependency.get("visibility") == "scoped-candidate" and not dependency.get("conditional")
                        for dependency in packet["dependencies"])):
            packet["condition_hint"] = "unsupported"
            packet["predicate_check"] = {"status": "verified", "kind": "visible-source-definition",
                                         "assessment": "unsupported"}
        from .llm_facts import attach_facts
        attach_facts(packet, unit, occurrence, lines)
        packet["context"] = context
    except (yaml.YAMLError, ValueError, TypeError, RecursionError) as exc:
        packet["missing"].append(str(exc))
        packet["context"] = ""
    packet["complete"] = not packet["missing"] and packet["unit"] is not None
    packet["sha256"] = digest(packet)
    return packet


def _variables(packet, unit, occurrence, lines, read_lines, graph_factory):
    subject = str(occurrence.get("semantic_subject") or "")
    name = subject.removeprefix("variable:").split("|", 1)[0] if subject.startswith("variable:") else None
    match = re.search(r"\bvariable ['\"]([^'\"]+)['\"]", str(occurrence.get("message") or ""), re.IGNORECASE)
    if match:
        name = match[1]
    if not name or name not in referenced_names(unit["node"]):
        packet["missing"].append("exact case-sensitive variable reference at the source unit")
        return
    graph = graph_factory()
    if graph is None:
        packet["missing"].append("repository scope graph unavailable")
        return
    try:
        kwargs = dict(task_index=unit["task"], play_index=unit["play"], task_path=unit["task_path"])
        visibility = graph.definition_visibility(name, packet["file"], **kwargs)
        definitions = graph.definitions_visible_at(name, packet["file"], **kwargs)
        packet["variable"] = {"name": name, "visibility": visibility, "candidate_count": len(definitions)}
        if visibility != "must":
            packet["missing"].append("complete inventory, extra-vars and dynamic input contract; absence of a visible definition is not undefinedness")
        for definition in definitions[:8]:
            other = read_lines(definition.file)
            # Anchor on an exact key, not an arbitrary substring or later task.
            candidates = []
            try:
                document = yaml.compose("\n".join(other))
                _audit(document)
                typed_span = definition_span(document, definition, name)
                stack, seen = [document], set()
                while stack:
                    node = stack.pop()
                    if node is None or id(node) in seen:
                        continue
                    seen.add(id(node))
                    if isinstance(node, MappingNode):
                        for key, value in node.value:
                            if isinstance(key, ScalarNode) and key.value == name:
                                candidates.append((key.start_mark.line + 1, span(value)[1]))
                            stack.append(value)
                    elif isinstance(node, SequenceNode):
                        stack.extend(node.value)
            except (yaml.YAMLError, RecursionError):
                candidates = []
                typed_span = None
            near = [typed_span] if typed_span else [item for item in candidates if item[0] == definition.line]
            if not near:
                # A wrapper anchor may be imprecise. Never bind to a later key by proximity.
                packet["missing"].append(f"exact definition anchor unavailable: {definition.file}:{definition.line}")
                continue
            start, end = near[0]
            packet["dependencies"].append({"file": definition.file, "start": start, "end": end,
                "source_lines_sha256": digest(other), "relation": definition.kind,
                "visibility": "may" if definition.conditional else "scoped-candidate",
                "precedence": definition.precedence, "conditional": definition.conditional,
                "source": numbered(other, start, end)})
        if len(definitions) > 8:
            packet["truncated"] = True
            packet["missing"].append(f"{len(definitions) - 8} scoped definitions omitted")
    except Exception as exc:
        packet["missing"].append(f"scope query unavailable: {type(exc).__name__}")
