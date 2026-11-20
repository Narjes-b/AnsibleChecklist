"""Compact, explicitly backend-authored source facts for local explanations.

These facts and selected citations are bounded static policy, not LLM reasoning
or independent judgments of deployment correctness.
"""
from __future__ import annotations

import re
from yaml.nodes import ScalarNode


def attach_facts(packet, unit, occurrence, lines):
    from .llm_evidence import module_arguments, referenced_names
    rule = packet["rule"]
    module, args = module_arguments(unit["fields"])
    facts, citations = [], []
    summary = None
    file = packet["file"]

    def cite(node, path=file):
        if node is not None:
            item = {"file": path, "line": node.start_mark.line + 1}
            if item not in citations:
                citations.append(item)

    if rule == "missing-validate-certs":
        node = args.get("validate_certs")
        if isinstance(node, ScalarNode):
            cite(node)
            if node.tag == "tag:yaml.org,2002:bool":
                disabled = node.value.lower() in {"false", "no", "off"}
                summary = f"The task explicitly configures validate_certs: {'false' if disabled else 'true'}; certificate checking is configured {'off' if disabled else 'on'} through this setting."
                facts.append(f"validate_certs is the explicit literal {'false' if disabled else 'true'}: certificate checking is configured {'off' if disabled else 'on'}.")
                facts.append("This is a configuration fact, not proof of active HTTPS, task execution, exploitability, or deployment harm.")
            else:
                summary = "The runtime value of validate_certs is unavailable, so certificate-checking behavior is unknown."
                facts.append(f"validate_certs is the expression {node.value!r}; its runtime value is UNKNOWN. Do not describe checking as disabled or enabled.")
        else:
            summary = "No explicit validate_certs value is established; defaults and runtime behavior require additional context."
            facts.append("No explicit validate_certs value is supplied; defaults/runtime behavior are not established.")
    elif rule == "insecure-permissions":
        cite(args.get("mode"))
        cite(args.get("path") or args.get("dest"))
        cite(args.get("state"))
        cite(args.get("group"))
        if packet.get("permissions") and args.get("mode") is None:
            unit_span = packet["unit"]
            start, end = unit_span["start"], unit_span["end"]
            packet["supporting_spans"] = [{"file": file, "start": start, "end": end,
                "purpose": "complete leaf mapping establishes that mode is omitted",
                "quote": "\n".join(lines[start - 1:end])}]
            citations.insert(0, {"file": file, "line": start})
        for value in packet.get("permissions", []):
            bits = value["mode_bits"]
            if bits is None:
                summary = "Actual permission bits are not established; existing destination permissions and runtime policy require additional context."
                facts.append("Actual permission bits are UNKNOWN. With absent mode, an existing destination may preserve its mode; do not assert a default 0644 or reliance on umask.")
            else:
                summary = f"The source specifies octal permission bits {bits:04o} (parsed decimal {bits}); world-write is {str(value['world_writable']).lower()}."
                facts.append(f"Parsed mode is decimal {bits}, octal {bits:04o}; world-write={value['world_writable']}, setuid={value['setuid']}, setgid={value['setgid']}.")
                facts.append("Group-write alone is not an insecure-permissions violation. Intended group-shared setgid directories may be allowed by this bounded policy.")
    elif rule in {"credential-log-exposure", "credentials-leaking-in-log"}:
        node = unit["inherited"].get("no_log")
        packet["output_control"] = {
            "state": "not-shown" if node is None else "literal" if isinstance(node, ScalarNode) and node.tag == "tag:yaml.org,2002:bool" else "runtime-unknown",
            "literal_value": node.value.lower() in {"true", "yes", "on"} if isinstance(node, ScalarNode) and node.tag == "tag:yaml.org,2002:bool" else None,
        }
        cite(node)
        # Cite the module value/body, not merely the task's name.
        for key, value in unit["fields"].items():
            if key == module or key in ("action", "local_action"):
                from ..detectors.credentials_leaking_in_log import _is_sensitive_key
                for name in sorted(referenced_names(value)):
                    if _is_sensitive_key(name):
                        facts.append(f"The task references sensitive-looking name {name!r}; this is not proof of an actual secret leak.")
                cite(value)
                # Scalar command bodies need citations to their actual Jinja
                # reference lines, not just the block-scalar header.
                if isinstance(value, ScalarNode):
                    from .llm_evidence import span
                    a, b = span(value)
                    for line in range(a, min(b, len(lines)) + 1):
                        if any(name in lines[line - 1] for name in referenced_names(value) if _is_sensitive_key(name)):
                            citations.append({"file": file, "line": line})
                if args.get("msg") is not None:
                    cite(args["msg"])
                # Include direct scalar entries that actually contain a Jinja use.
                for arg in args.values():
                    if isinstance(arg, ScalarNode) and referenced_names(arg):
                        cite(arg)
                        from .llm_evidence import span
                        a, b = span(arg)
                        for line in range(a, min(b, len(lines)) + 1):
                            if any(name in lines[line - 1] for name in referenced_names(arg)):
                                citations.append({"file": file, "line": line})
        if node is None:
            summary = "Sensitive-value handling and module redaction require additional context; actual output exposure is not established."
            facts.append("No explicit task/ancestor no_log setting is shown; module argument redaction and actual secret flow are not generally certified.")
        elif isinstance(node, ScalarNode) and node.tag == "tag:yaml.org,2002:bool":
            protected = node.value.lower() in {"true", "yes", "on"}
            summary = ("Effective no_log is true, so the task result is censored in controller output." if protected else
                       "Effective no_log is false; the sensitive-looking display is a static output-risk pattern, not proof of a deployed secret leak.")
            if not protected and packet.get("missing"):
                summary = "Effective no_log is false, but module redaction and sensitive-value flow require additional context."
            facts.append(f"Effective no_log is literal {'true' if protected else 'false'}, including inheritance/overrides. " +
                         ("It censors the task result in controller output; do not say protection is absent. It does not certify redaction of literal source excerpts or other tasks." if protected else "It does not censor controller output."))
        else:
            summary = "The effective no_log runtime value is unavailable, so output protection is unknown."
            facts.append("Effective no_log is UNKNOWN at runtime; do not claim either protection or an unprotected display.")
        facts.append("no_log hides controller output; it does NOT erase registered values or prevent subsequent tasks from using them.")
    elif packet.get("variable"):
        name = packet["variable"]["name"]
        # Use the exact reported reference, plus any verified visible definition.
        anchor = int(occurrence["line"])
        citations.append({"file": file, "line": anchor})
        definitions = [d for d in packet["dependencies"] if d.get("visibility") == "scoped-candidate" and not d.get("conditional")]
        if packet["variable"].get("visibility") == "must" and definitions and not packet["missing"]:
            summary = "The referenced variable has an established scope-visible source definition; the missing-definition claim is contradicted."
            facts.append(f"{name!r} HAS an established scope-visible definition. The missing-definition claim is contradicted. Do not deny that definition or reinterpret must-visible as missing.")
            for definition in definitions[:4]:
                citations.append({"file": definition["file"], "line": definition["start"]})
                facts.append(f"Definition: {definition['file']}:{definition['start']} ({definition['relation']}); visible to this use.")
        else:
            summary = "The reference is visible, but runtime definedness cannot be decided without the missing input contracts."
            facts.append(f"Runtime definedness of {name!r} is UNKNOWN. No complete inventory/extra-vars contract is supplied; lack of a visible definition is not runtime undefinedness.")
    if not citations:
        citations.append({"file": file, "line": packet["unit"]["start"]})
    # Minimal local proof: task/module binding plus every relevant explicit
    # parameter span. This never certifies an omission from a partial window.
    if rule in {"missing-validate-certs", "insecure-permissions"}:
        from .llm_evidence import span
        required = [{"file": file, "start": packet["unit"]["start"], "end": packet["unit"]["start"]}]
        module_keys = [key for key, _ in unit["node"].value
                       if isinstance(key, ScalarNode) and key.value in {module, "action", "local_action"}]
        required += [{"file":file, "start":key.start_mark.line+1, "end":key.start_mark.line+1} for key in module_keys]
        if "action" in unit["fields"] or "local_action" in unit["fields"]:
            from .llm_evidence import pairs
            action = pairs(unit["fields"].get("action") or unit["fields"].get("local_action"))
            if action.get("module") is not None:
                a,b=span(action["module"]);required.append({"file":file,"start":a,"end":b})
        keys = ("validate_certs",) if rule == "missing-validate-certs" else ("mode", "path", "dest", "state", "group", "src", "content", "name")
        for key in keys:
            if args.get(key) is not None:
                a,b=span(args[key]);required.append({"file":file,"start":a,"end":b})
        decisive_key = "validate_certs" if rule == "missing-validate-certs" else "mode"
        if module_keys and args.get(decisive_key) is not None:
            packet["local_fact_support"] = required
    packet["facts"] = facts
    if summary:
        packet["summary_text"] = summary
        packet["prose_origin"] = {"summary": "backend-authored source facts", "reasoning": "local model, unverified"}
    packet["decisive_citations"] = list({(c["file"], c["line"]): c for c in citations}.values())[:16]
    packet["citation_policy"] = "backend-selected source facts; not independently model-selected citations"


def prompt_contract(packet):
    """Omit opaque hashes/identities from the prompt; retain them in telemetry."""
    compact = {key: packet[key] for key in ("predicate_check", "summary_text",
               "decisive_citations", "missing", "limitations", "variable", "output_control") if key in packet}
    facts = packet.get("facts", [])
    if packet["rule"] in {"credential-log-exposure", "credentials-leaking-in-log", "insecure-permissions"}:
        compact["explanatory_notes"] = facts[-1:]
        if packet["rule"] == "insecure-permissions":
            compact["parsed_permissions"] = [{"source": p["mode"], "yaml_type": p["mode_tag"],
                "decimal": p["mode_bits"], "octal": f"{p['mode_bits']:04o}" if p["mode_bits"] is not None else None,
                "world_write": p["world_writable"], "setuid": p["setuid"], "setgid": p["setgid"]}
                for p in packet.get("permissions", [])]
        elif packet.get("output_control", {}).get("state") == "not-shown":
            compact["explanatory_notes"] = ["No no_log setting is shown in this task or supplied ancestors. Do not claim it is set or used; runtime/module redaction remains unknown."] + facts[-1:]
    elif packet.get("variable"):
        compact["explanatory_notes"] = facts[1:]
    return compact


def contradiction(parsed, packet):
    """Reject a few closed, explicit factual contradictions, not certify prose."""
    expected = packet.get("decisive_citations")
    if expected and parsed["evidence"] != expected:
        return "citations must identify the backend's decisive source facts"
    summary = parsed["summary"].lower()
    text = summary + " " + parsed["reasoning"].lower()
    reasoning = parsed["reasoning"].lower().replace("`", "")
    for permissions in packet.get("permissions", []):
        bits = permissions.get("mode_bits")
        if bits is not None:
            for match in re.finditer(r"\boctal(?: permission bits)?\s+['\"]?([0-7]{3,6})", reasoning):
                prefix = reasoning[max(0, match.start() - 25):match.start()]
                if re.search(r"not\s+$|rather than\s+$|instead of\s+$", prefix):
                    continue
                if int(match[1], 8) != bits:
                    return "reasoning contradicts the parsed YAML permission bits"
            if permissions.get("world_writable") and re.search(r"not (?:an? )?insecure[- ]permissions violation", reasoning):
                return "reasoning denies the verified world-write predicate"
    if packet.get("output_control", {}).get("state") == "not-shown":
        for sentence in re.split(r"[.;]\s+", reasoning):
            if re.search(r"\bif\b|\bwhen\b|\bwhether\b|\bmay\b|\bmight\b|\bunknown\b", sentence):
                continue
            attributed = re.search(r"(?:task|source(?: code)?|backend (?:facts|evidence))[^.]*no_log(?: parameter| setting)? (?:is|was) (?:used|set|enabled)", sentence)
            standalone = re.search(r"^the no_log (?:parameter|setting) is (?:used|set|enabled)(?! to (?:hide|censor|suppress))", sentence)
            if attributed or standalone:
                return "reasoning invents a no_log setting absent from supplied source"
    if packet.get("variable", {}).get("visibility") == "must" and not packet.get("missing"):
        if re.search(r"(?:has no|has not|is not|isn't|no visible)\s+(?:visible\s+)?(?:definition|defined)|not defined anywhere", text):
            return "summary denies an established visible definition"
    if packet.get("effective_no_log") in ("true", "yes", "on"):
        if re.search(r"without (?:effective )?(?:no_log|protection)|no_log[^.]*?(?:does not apply|ineffective)", text):
            return "summary denies effective literal no_log protection"
    if packet.get("missing"):
        if packet["rule"] == "insecure-permissions" and re.search(r"(?:task|mode|permissions?) (?:grants?|sets?|is|are) (?:the )?unsafe", summary):
            return "summary asserts unsafe permissions despite unknown actual bits"
        for sentence in re.split(r"[.;]\s+", summary):
            if re.search(r"whether|cannot|unknown|may |might |could |not established|undetermined", sentence):
                continue
            if packet["rule"] == "missing-validate-certs" and re.search(r"\bdisables?\b|verification is disabled", sentence):
                return "summary asserts disabled TLS despite an unknown runtime value"
            if packet["rule"] in {"credential-log-exposure", "credentials-leaking-in-log"} and "without effective no_log" in sentence:
                return "summary asserts absent protection despite unknown effective no_log"
            if packet["rule"] == "insecure-permissions" and re.search(r"rel(?:y|ies|ying) on (?:the )?system umask", sentence):
                return "summary assumes umask rather than unknown existing permissions"
    if "no_log" in text and re.search(r"registered (?:result|value).*would be compromised", text):
        return "explanation incorrectly treats output censoring as erasing a registered value"
    if packet.get("summary_text") and parsed["summary"] != packet["summary_text"]:
        return "fact summary must preserve its declared backend-authored text"
    return None


def quoted_evidence(citations, catalog, packet):
    """Attach exact source ranges for omission claims, leaving line quotes intact."""
    result = []
    for citation in citations:
        entry = {**citation, "quote": catalog[citation["file"], citation["line"]]}
        for span in (packet or {}).get("supporting_spans", []):
            is_window = span.get("purpose", "").startswith("exact supplied window extent")
            matches = citation["line"] == span["start"] or (is_window and span["start"] <= citation["line"] <= span["end"])
            if citation["file"] == span["file"] and matches:
                entry["source_span"] = span
        result.append(entry)
    return result
