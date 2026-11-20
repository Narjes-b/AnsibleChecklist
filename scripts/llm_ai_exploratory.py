#!/usr/bin/env python3
"""Explicit single-assistant exploratory review; never independent human gold.

Ratings are manual judgments from this session, represented as case-specific
tables for reproducible arithmetic. They were made after seeing outputs and are
not blinded, preregistered, or an independent benchmark of model reasoning.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import time

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.llm_quality_study import (ROOT, load, save, table, read_package, records_for,
                                      implementation, case_root, llm, digest, write_checkpoint)

PRODUCER = "Single AI assistant in this conversation; also involved in implementing the tool"


def source_judgments(cases):
    rows = []
    for cid, case in cases.items():
        family = case["family"]
        n = int(cid.rsplit("-", 1)[1])
        controlled = case["kind"] == "controlled"
        if controlled:
            if family == "unguarded-variable":
                condition = "unsupported" if n in (1, 4) else "insufficient-evidence"
                reason = "Prior unconditional set_fact defines ServicePort." if n in (1, 4) else "Visible reference alone cannot exclude inventory/extra-vars; unrelated role defaults do not prove visibility."
            else:
                condition = ("supported", "unsupported", "insufficient-evidence")[n % 3]
                reason = {
                    "missing-validate-certs": ("Explicit false TLS validation setting.", "Explicit true TLS validation setting.", "verify_tls runtime value unavailable."),
                    "insecure-permissions": ("Literal world-write permission bits.", "No unsafe bits under the declared policy; no demonstrated private-file context.", "desired_mode runtime value unavailable."),
                    "credential-log-exposure": ("Sensitive-looking debug reference with effective no_log false.", "Task or inherited no_log true protects the debug result.", "Effective no_log runtime value unavailable."),
                }[family][n % 3]
        elif family == "missing-validate-certs":
            condition = "supported"
            reason = "Explicit false/no validate_certs configuration. This is a literal setting, not proof of active HTTPS, module compatibility, exploitability or a needed fix."
        elif family == "insecure-permissions":
            condition = "insufficient-evidence" if n in (2, 3, 5) else "supported"
            reason = ("Mode absent: existing destination permissions, umask and intended policy are unavailable; actual unsafe bits cannot be established. The mode-omission subpredicate itself is present."
                      if n in (2, 3, 5) else "Literal world-write bits; unquoted numeric 2750 is decimal (octal 05276), not quoted octal 02750." if n == 4
                      else "Literal 0777 permits other-user writes.")
        elif family == "credential-log-exposure":
            condition = "insufficient-evidence" if n in (1, 2, 5) else "supported"
            reason = ("Version-specific custom/legacy module argument redaction is not supplied; missing task-local no_log alone does not establish lack of effective protection."
                      if n in (1, 2, 5) else "Supplied complete source has sensitive material and no explicit/inherited no_log protection; static risk pattern, not proven leakage."
                      if n != 3 else "Occurrence names the JDBC-writing task at line 188, which contains default_database_password; scoped packet incorrectly binds the preceding XML-read task.")
        else:
            condition = "insufficient-evidence"
            reason = "No complete inventory/extra-vars/runtime-input contract; absence in supplied source does not establish runtime undefinedness."
        rows.append({"case_id": cid, "kind": case["kind"], "family": family, "condition": condition,
                     "producer": PRODUCER, "reason": reason})
    return rows


# Each set below is a manual case judgment, not a heuristic applied to prose.
# Successful content requires correct decision + grounded, noncontradictory prose.
CONTROLLED_GOOD = {
    "window": {"missing-validate-certs": {1, 4}, "insecure-permissions": set(),
               "credential-log-exposure": {1}, "unguarded-variable": {1}},
    "scoped": {"missing-validate-certs": {0, 1, 3, 4}, "insecure-permissions": set(range(6)),
               "credential-log-exposure": {0, 3}, "unguarded-variable": {0, 2, 3, 5}},
}
REAL_GOOD = {
    "window": {family: set() for family in ("missing-validate-certs", "insecure-permissions", "credential-log-exposure", "unguarded-variable")},
    "scoped": {"missing-validate-certs": {0, 1, 3, 5}, "insecure-permissions": {0, 1, 4},
               "credential-log-exposure": set(), "unguarded-variable": set(range(6))},
}
DIRECT_CITATIONS = {
    "window": {
        "controlled": {"missing-validate-certs": {1, 4}, "insecure-permissions": {3, 4},
                       "credential-log-exposure": set(), "unguarded-variable": {5}},
        "real": {"missing-validate-certs": {0, 2, 3}, "insecure-permissions": {0, 4},
                 "credential-log-exposure": {5}, "unguarded-variable": set()},
    },
    "scoped": {
        "controlled": {"missing-validate-certs": {2, 3, 5}, "insecure-permissions": {2, 3, 4, 5},
                       "credential-log-exposure": set(), "unguarded-variable": {0, 2, 3, 5}},
        "real": {"missing-validate-certs": {0, 2, 3, 5}, "insecure-permissions": {0, 1, 4},
                 "credential-log-exposure": {5}, "unguarded-variable": set(range(6))},
    },
}

FAILURE_NOTES = {
    "evaluation-missing-validate-certs-0/window": "Says verification is disabled but structured unsupported denies the literal predicate; cites mode instead of validate_certs.",
    "evaluation-missing-validate-certs-2/window": "Calls unknown verify_tls disabled while admitting value unknown; unsupported is not justified.",
    "evaluation-missing-validate-certs-2/scoped": "Correct abstention but summary nevertheless says task disables TLS using the unknown variable.",
    "evaluation-missing-validate-certs-3/window": "Literal false is visible but structured unsupported contradicts the explanation; wrong decisive citation.",
    "evaluation-missing-validate-certs-5/window": "Unknown variable value does not establish disabled validation or unsupported condition.",
    "evaluation-missing-validate-certs-5/scoped": "Correct abstention but summary nevertheless claims disabled validation.",
    "evaluation-insecure-permissions-0/window": "Correct bits and decision, but reasoning falsely locates the mode on line 6 (that is path); citation also wrong.",
    "evaluation-insecure-permissions-1/window": "Calls 0644 generally secure yet returns supported insecure-permissions.",
    "evaluation-insecure-permissions-2/window": "Admits unknown desired_mode but returns unsupported instead of insufficient-evidence.",
    "evaluation-insecure-permissions-3/window": "Blames group write/execute rather than unsafe other-user write; intended group sharing alone is not evidence of the reported insecurity.",
    "evaluation-insecure-permissions-4/window": "Treats intended 2775 group sharing as sufficient evidence of insecurity.",
    "evaluation-insecure-permissions-5/window": "Admits unknown desired_mode but returns unsupported instead of insufficient-evidence.",
    "evaluation-credential-log-exposure-1/scoped": "Summary denies effective no_log despite explicit no_log true; correct structured state does not fix the prose.",
    "evaluation-credential-log-exposure-2/window": "Definite unprotected-output claim conflicts with admitted unknown hide_output and unsupported decision.",
    "evaluation-credential-log-exposure-2/scoped": "Summary says no explicit no_log setting although a templated setting is explicit; structured abstention is correct.",
    "evaluation-credential-log-exposure-3/window": "Narrative asserts an unprotected sensitive display yet structured unsupported denies that predicate.",
    "evaluation-credential-log-exposure-4/window": "Incorrectly claims block-level no_log true does not apply to child tasks.",
    "evaluation-credential-log-exposure-4/scoped": "Denies effective protection despite inherited no_log true in supplied evidence.",
    "evaluation-credential-log-exposure-5/window": "Reverses no_log true semantics and overstates unprotected output for unknown runtime value.",
    "evaluation-credential-log-exposure-5/scoped": "Correct abstention but summary nevertheless asserts no effective protection for an unknown control.",
    "evaluation-unguarded-variable-1/scoped": "Denies a supplied prior set_fact definition at line 3 while returning unsupported.",
    "evaluation-unguarded-variable-4/scoped": "Denies supplied set_fact and misreads must-visible metadata as missing definition.",
    "evaluation-unguarded-variable-4/window": "Wrongly claims prior unconditional set_fact is not visible at the subsequent debug use.",
    "evaluation-unguarded-variable-5/window": "Unknown external inputs and unrelated defaults do not justify a decisive unsupported label.",
    "real-missing-validate-certs-1/window": "Unsupported contradicts explicit false; additionally asserts TLS MITM consequences for a supplied http:// URL without qualifying redirects.",
    "real-missing-validate-certs-2/scoped": "Correct literal predicate but asserts MITM vulnerability for a templated URL without supplied scheme/deployment context.",
    "real-missing-validate-certs-4/window": "Claims parameter absent and disabled although its own reasoning says default True; full source explicitly sets false outside the window.",
    "real-missing-validate-certs-5/window": "Claims validate_certs absent; complete task explicitly sets false outside the fixed window.",
    "real-insecure-permissions-0/window": "Explicit 0777 establishes the reported bits; unsupported is inconsistent with the visible mode and narrative.",
    "real-insecure-permissions-1/window": "Explains and cites the preceding directory task instead of the flagged file-copy task; unsupported also wrong.",
    "real-insecure-permissions-2/scoped": "Correct uncertainty about actual unsafe bits, but unconditionally says relies on umask and ignores preservation of an existing file's mode; sensitivity is actually explicit in source.",
    "real-insecure-permissions-3/scoped": "Correct uncertainty, but unconditional reliance on umask ignores existing file permissions.",
    "real-insecure-permissions-4/window": "Misreads unquoted decimal 2750 as octal and also incorrectly decodes octal 2750's owner/group bits.",
    "real-insecure-permissions-5/scoped": "Correct uncertainty, but unconditional reliance on umask ignores preservation of existing destination permissions.",
    "real-credential-log-exposure-0/scoped": "Complete command task shows sensitive-looking API key and no no_log; describes pattern yet returns unsupported rather than supported risk/appropriate uncertainty.",
    "real-credential-log-exposure-3/scoped": "Wrong source unit: packet describes preceding read-XML task rather than flagged JDBC-writing task; cannot justify unsupported.",
    "real-credential-log-exposure-4/scoped": "Narrative says sensitive material without proven no_log yet structured unsupported denies that static risk pattern.",
    "real-credential-log-exposure-5/scoped": "Decisive unsupported and speculative leakage are not established without legacy module redaction behavior.",
}


def analyze(package, run_dir, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    cases, records = records_for(package, run_dir)
    gold_rows = source_judgments(cases)
    gold = {row["case_id"]: row for row in gold_rows}
    table(output / "ai-source-judgments.csv", list(gold_rows[0]), gold_rows)
    ratings = []
    for record in records:
        cid, mode = record["case_id"], record["mode"]
        case, result = cases[cid], record["result"]
        n = int(cid.rsplit("-", 1)[1])
        kind, family = ("controlled" if case["kind"] == "controlled" else "real"), case["family"]
        available = result["llm_status"] == "ok"
        good = available and n in (CONTROLLED_GOOD if kind == "controlled" else REAL_GOOD)[mode][family]
        citation = available and n in DIRECT_CITATIONS[mode][kind][family]
        decision = available and result.get("llm_assessment") == gold[cid]["condition"]
        if good and not decision:
            raise ValueError("manual rating table contradicts AI source judgment: " + cid)
        key = cid + "/" + mode
        note = FAILURE_NOTES.get(key)
        if not available:
            note = "Unavailable output: " + result.get("llm_error", result["llm_status"])
        elif good:
            note = "Decision and substantive explanation are consistent with supplied evidence and bounded source judgment."
        elif not note:
            if family == "missing-validate-certs":
                note = "Narrative acknowledges explicit disabled validation but structured unsupported contradicts the literal predicate."
            elif family == "insecure-permissions":
                note = "Decisive unsupported is not justified for unknown actual permissions; default-umask speculation is not established."
            else:
                note = "Narrative describes a sensitive/no_log risk but decisive unsupported is not supported; module redaction or source context is incomplete."
        ratings.append({"case_id": cid, "kind": kind, "family": family, "mode": mode, "status": result["llm_status"],
                        "ai_source_condition": gold[cid]["condition"], "returned_assessment": result.get("llm_assessment"),
                        "decision_matches_ai_judgment": decision, "content_adequate_ai": good,
                        "decisive_citation_support_ai": citation, "strict_content_and_citation_ai": good and citation,
                        "producer": PRODUCER, "note": note})
    table(output / "ai-output-ratings.csv", list(ratings[0]), ratings)
    groups = []
    for kind in ("all", "controlled", "real"):
        for mode in ("window", "scoped"):
            chosen = [r for r in ratings if r["mode"] == mode and (kind == "all" or r["kind"] == kind)]
            row = {"kind": kind, "mode": mode, "scheduled": len(chosen), "available": sum(r["status"] == "ok" for r in chosen)}
            for field in ("decision_matches_ai_judgment", "content_adequate_ai", "decisive_citation_support_ai", "strict_content_and_citation_ai"):
                row[field] = sum(r[field] for r in chosen)
                row[field + "_percent"] = round(100 * row[field] / len(chosen), 2)
            groups.append(row)
    table(output / "ai-summary.csv", list(groups[0]), groups)
    save(output / "provenance.json", {"producer": PRODUCER, "human_labels": False, "blinded": False,
        "preregistered": False, "rating_source": "Manual review in this conversation, post hoc case-specific tables in script",
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "freeze_sha256": load(Path(package) / "freeze.json")["sha256"],
        "limitations": ["Same assistant helped implement the tool; not an independent reviewer.",
            "Real-source cases are convenience examples; case labels contain judgment and semantic ambiguity.",
            "Three mode-omission cases are assessed for actual unsafe permissions, not merely presence of the missing-mode subpredicate.",
            "TLS labels concern explicit configuration, not active HTTPS or correctness of legacy module parameters.",
            "No confidence intervals or population quality claims; many scoped decisions are backend constrained.",
            "Content adequacy includes substantive reasoning, uncertainty and structured decision; strict measure additionally requires decisive cited lines.",
            "Actionability is not separately scored; absence of a suggestion is not fix correctness."]})
    save(output / "summary.json", {"groups": groups, "producer": PRODUCER, "independent_human_validation": False})
    lines = ["# AI-only exploratory review", "", "These are post hoc judgments by the same AI assistant that helped implement the tool, not human validation.",
             "All 96 scheduled outputs were inspected. Unavailable outputs count as unsuccessful. Original human forms are unchanged.", "",
             "| Panel | Condition | N | Decision matches AI source judgment | Adequate content | Content plus decisive citations |",
             "|---|---|---:|---:|---:|---:|"]
    for row in groups:
        lines.append(f"| {row['kind']} | {row['mode']} | {row['scheduled']} | {row['decision_matches_ai_judgment']} ({row['decision_matches_ai_judgment_percent']}%) | {row['content_adequate_ai']} ({row['content_adequate_ai_percent']}%) | {row['strict_content_and_citation_ai']} ({row['strict_content_and_citation_ai_percent']}%) |")
    lines += ["", "## Interpretation", "",
        "The scoped pipeline improves bounded decision consistency in this experiment, but correct structured states still accompany wrong prose.",
        "Examples: inherited no_log:true is ignored; visible set_fact definitions are denied; unknown TLS flags are described as disabled.",
        "Several citations name the task, URL or path instead of the decisive setting. A valid source location does not establish support.",
        "The real JDBC case has a source-unit binding defect: the flagged task starts at line 188 but the scoped packet selects its preceding sibling.",
        "Unquoted numeric mode 2750 is decimal (octal 05276); it really includes unsafe bits. Do not confuse it with quoted octal '2750'.", "",
        "The full-panel decision value depends on provisional source interpretations. The controlled 24-case row has fewer module/policy ambiguities.",
        "See provenance.json for scope, dependence and ambiguity limits. Do not call these human precision or LLM reasoning accuracy.", "",
        "No code snippets were delivered in this comparison, so semantic repair success is not measured by these ratings.",
        "The developer study remains deferred, and no developer benefit is estimated.", ""]
    (output / "AI_EXPERIMENT.md").write_text("\n".join(lines))
    return {"outputs_reviewed": len(ratings), "all_panel": [r for r in groups if r["kind"] == "all"]}


def repair_experiment(package, output):
    package, output = Path(package), Path(output)
    manifest, frozen = read_package(package), load(package / "freeze.json")
    if frozen["implementation"] != implementation():
        raise ValueError("original frozen candidate changed")
    model = llm.llm_runtime.model_identity(llm.DEFAULT_HOST, llm.DEFAULT_MODEL, llm._open_local, llm._local_chat_url)
    if model != frozen["model_digest"]:
        raise ValueError("installed model changed; no downloads")
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    provenance = {"kind": "AI-only exploratory repair experiment", "producer": PRODUCER,
        "human_approval": False, "not_the_human_evaluation": True, "freeze_sha256": frozen["sha256"],
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "model_digest": model,
        "settings": manifest["settings"], "source_judgments": [], "status": "in-progress"}
    for case in manifest["panels"]["repair"]:
        n = int(case["case_id"].rsplit("-", 1)[1])
        provenance["source_judgments"].append({"case_id": case["case_id"], "producer": PRODUCER,
            "condition": "supported" if n < 4 else "unsupported" if n == 4 else "insufficient-evidence",
            "actionability": "actionable" if n < 4 else "not-actionable" if n == 4 else "context-dependent",
            "intent": case["intent"], "reason": "Explicit fixture setting and supplied intent; no independent human source review."})
    write_checkpoint(output, "run-manifest", provenance)
    for case in manifest["panels"]["repair"]:
        telemetry = {}
        with case_root(case, ROOT / "study/repositories") as root:
            token = llm._CALL_RECORD.set(telemetry)
            started = time.monotonic()
            try:
                result = llm.explain_occurrence(case["occurrence"], root, evidence_mode="scoped", timeout=120)
            except Exception as exc:
                result = {"llm_status": "runner-error", "llm_error": f"{type(exc).__name__}: {exc}"}
            finally:
                llm._CALL_RECORD.reset(token)
            record = {"case_id": case["case_id"], "mode": "scoped", "freeze_sha256": frozen["sha256"],
                      "producer": PRODUCER, "result": result, "telemetry": telemetry, "wall_seconds": time.monotonic() - started}
            write_checkpoint(output, case["case_id"], record)
            print(json.dumps({"case_id": case["case_id"], "status": result["llm_status"],
                              "delivered_fix": bool(result.get("llm_fixed_code_snippet"))}), flush=True)
    provenance["status"] = "completed"
    write_checkpoint(output, "run-manifest", provenance)
    return {"cases": 12, "status": "completed", "human_validation": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("analyze", "repair"))
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--run", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "analyze":
        if args.run is None:
            parser.error("--run is required")
        result = analyze(args.package, args.run, args.output)
    else:
        result = repair_experiment(args.package, args.output)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
