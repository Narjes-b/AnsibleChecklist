#!/usr/bin/env python3
"""Preview a caller-requested narrow edit; never apply it or claim LLM origin."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import textwrap

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import yaml
from ansibleguard.report.llm_evidence import build_packet, digest
from ansibleguard.report.llm_explain import _read_source_lines
from ansibleguard.report.llm_suggestions import _task, _TaskDumper, validate_suggestion

KINDS = {"enable-tls-verification": "missing-validate-certs",
         "protect-task-output": "credential-log-exposure"}


def propose(root, occurrence, requested_kind, *, caller_intent, timeout=15):
    result = {"origin": "backend explicit-request transformation, not LLM-generated",
              "requested_kind": requested_kind, "status": "withheld", "applied": False,
              "limitations": ["Mechanical checks do not establish general behavioral equivalence or deployment suitability.",
                              "TLS requires an appropriate trust store; no_log reduces controller visibility.",
                              "The caller selects the change and declares intent; the tool does not infer authorization from source text."]}
    if requested_kind not in KINDS or not isinstance(caller_intent, str) or not caller_intent.strip() or len(caller_intent) > 4000:
        result["reason"] = "explicit recognized change selection and bounded caller intent required"
        return result
    rule = (occurrence.get("concept_id") or occurrence.get("rule_id") or "").removeprefix("ansibleguard/")
    if rule == "credentials-leaking-in-log":
        rule = "credential-log-exposure"
    if rule != KINDS[requested_kind]:
        result["reason"] = "requested change does not match the finding family"
        return result
    root = Path(root)
    lines = _read_source_lines(root, occurrence.get("file"))
    if not lines:
        result["reason"] = "valid source within the selected root required"
        return result
    packet = build_packet(occurrence, lines, lambda f: _read_source_lines(root, f), lambda: None)
    if not packet.get("complete") or packet.get("unit", {}).get("kind") != "task" \
            or packet.get("predicate_check", {}).get("status") != "verified" \
            or packet.get("predicate_check", {}).get("assessment") != "supported":
        result["reason"] = "complete leaf evidence and verified supported condition required"
        result["missing"] = packet.get("missing", [])
        return result
    try:
        unit = packet["unit"]
        before = textwrap.dedent("\n".join(lines[unit["start"] - 1:unit["end"]]))
        task = _task(before)
        if requested_kind == "enable-tls-verification":
            modules = [k for k, v in task.items() if k.rsplit(".", 1)[-1] in {"get_url", "uri"}
                       and isinstance(v, dict) and v.get("validate_certs") is False]
            if len(modules) != 1 or "args" in task or "action" in task or "local_action" in task:
                raise ValueError("one direct uri/get_url literal false setting required")
            task[modules[0]]["validate_certs"] = True
        else:
            modules = [k for k in task if k.rsplit(".", 1)[-1] == "debug"]
            if len(modules) != 1:
                raise ValueError("only a verified direct debug display can receive this requested proposal")
            task["no_log"] = True
        snippet = yaml.dump([task], Dumper=_TaskDumper, sort_keys=False)
        checks = validate_suggestion(packet, snippet, lines, timeout=timeout)
        result.update(validation=checks, source_sha256=digest(lines), packet_sha256=packet["sha256"],
                      source_span={"file": occurrence["file"], "start": unit["start"], "end": unit["end"]},
                      caller_intent=caller_intent)
        if checks["status"] != "passed":
            result["reason"] = checks.get("reason", "mechanical validation failed")
        else:
            result.update(status="proposal-ready", before=before, snippet=snippet)
    except (ValueError, TypeError, yaml.YAMLError) as exc:
        result["reason"] = str(exc)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--file", required=True)
    parser.add_argument("--line", type=int, required=True)
    parser.add_argument("--kind", choices=KINDS, required=True)
    parser.add_argument("--intent", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("refusing to overwrite an existing proposal")
    result = propose(args.root, {"file": args.file, "line": args.line, "rule_id": KINDS[args.kind]},
                     args.kind, caller_intent=args.intent)
    result["tool_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    args.output.chmod(0o600)
    print(json.dumps({"status": result["status"], "output": str(args.output), "applied": False}))


if __name__ == "__main__":
    main()
