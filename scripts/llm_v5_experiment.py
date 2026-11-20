#!/usr/bin/env python3
"""Development rerun on exposed cases; retain AI-only manual review provenance."""
from __future__ import annotations

import argparse
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import sys
import time

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.llm_quality_study import (ROOT, llm, load, save, table, read_package, implementation,
    schedule, case_root, records_for, keyed_rows, write_checkpoint, digest)


def repairs(package, output):
    package, output = Path(package), Path(output)
    manifest, frozen = read_package(package), load(package / "freeze.json")
    if frozen["implementation"] != implementation() or frozen["manifest_sha256"] != manifest["sha256"]:
        raise ValueError("frozen candidate changed")
    model = llm.llm_runtime.model_identity(llm.DEFAULT_HOST, llm.DEFAULT_MODEL, llm._open_local, llm._local_chat_url)
    if model != frozen["model_digest"]:
        raise ValueError("installed model changed")
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    entries = schedule(manifest["panels"]["repair"], False)
    header = {"panel": "repair", "freeze_sha256": frozen["sha256"],
              "schedule": [[case["case_id"], mode] for case, mode in entries],
              "authority": "AI-only exploratory development experiment; not human validation",
              "intent_change": "Same authored intent is now a typed caller field rather than only embedded in detector text.",
              "harness_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "status": "in-progress", "completed": 0}
    write_checkpoint(output, "run-manifest", header)
    for case, mode in entries:
        occurrence = {**case["occurrence"], "review_intent": case["intent"]}
        telemetry = {}
        with case_root(case, ROOT / "study/repositories") as root:
            token = llm._CALL_RECORD.set(telemetry)
            started = time.monotonic()
            try:
                result = llm.explain_occurrence(occurrence, root, evidence_mode=mode, timeout=120)
            except Exception as exc:
                result = {"llm_status": "runner-error", "llm_error": f"{type(exc).__name__}: {exc}"}
            finally:
                llm._CALL_RECORD.reset(token)
        record = {"case_id": case["case_id"], "mode": mode, "freeze_sha256": frozen["sha256"],
                  "input_occurrence": occurrence, "result": result, "telemetry": telemetry,
                  "wall_seconds": time.monotonic() - started}
        write_checkpoint(output, case["case_id"] + "-" + mode, record)
        header["completed"] += 1
        write_checkpoint(output, "run-manifest", header)
        print(json.dumps({"case_id": case["case_id"], "status": result["llm_status"],
                          "fix": bool(result.get("llm_fixed_code_snippet"))}), flush=True)
    header["status"] = "completed"
    write_checkpoint(output, "run-manifest", header)
    return {"scheduled": len(entries), "completed": header["completed"]}


def form(package, run_dir, baseline_review, output):
    cases, records = records_for(package, run_dir)
    gold = keyed_rows(Path(baseline_review) / "ai-source-judgments.csv", ("case_id",))
    if set(cases) != {key[0] for key in gold}:
        raise ValueError("rerun must use exactly the previously AI-reviewed cases")
    if Path(output).exists():
        raise FileExistsError("never overwrite manual ratings")
    rows = [{"case_id": r["case_id"], "mode": r["mode"], "content_adequate": "",
             "decisive_citation_support": "", "notes": ""} for r in records]
    table(output, list(rows[0]), rows)
    return {"blank_AI_review_rows": len(rows), "human_forms_modified": False}


def summarize(package, run_dir, baseline_review, ratings, output):
    cases, records = records_for(package, run_dir)
    baseline_review, output = Path(baseline_review), Path(output)
    gold = keyed_rows(baseline_review / "ai-source-judgments.csv", ("case_id",))
    judgments = keyed_rows(ratings, ("case_id", "mode"))
    if len(judgments) != len(records) or {key[0] for key in gold} != set(cases):
        raise ValueError("case/condition identities must match baseline and complete rerun")
    rows = []
    for r in records:
        cid, mode = r["case_id"], r["mode"]
        j, result = judgments.get((cid, mode)), r["result"]
        if not j or j["content_adequate"] not in ("yes", "no") or j["decisive_citation_support"] not in ("yes", "no") or not j["notes"].strip():
            raise ValueError("every output needs an explicit AI judgment and rationale")
        available = result["llm_status"] == "ok"
        decision = available and result.get("llm_assessment") == gold[(cid,)]["condition"]
        content = available and j["content_adequate"] == "yes"
        citation = available and j["decisive_citation_support"] == "yes"
        if j["content_adequate"] == "yes" and not decision:
            raise ValueError("adequate content must include agreement with the unchanged AI source judgment")
        rows.append({"case_id": cid, "mode": mode, "kind": cases[cid]["kind"], "available": available,
                     "decision": decision, "content": content, "citation": citation,
                     "strict": content and citation, "notes": j["notes"]})
    groups = []
    for kind in ("all", "controlled", "real"):
        for mode in ("window", "scoped"):
            chosen = [r for r in rows if r["mode"] == mode and (kind == "all" or r["kind"] == kind)]
            groups.append({"kind": kind, "mode": mode, "scheduled": len(chosen),
                           **{field: sum(r[field] for r in chosen) for field in ("available", "decision", "content", "citation", "strict")}})
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    table(output / "reviewed-records.csv", list(rows[0]), rows)
    table(output / "summary.csv", list(groups[0]), groups)
    save(output / "summary.json", {"groups": groups, "baseline": load(baseline_review / "summary.json"),
         "human_validation": False, "development_exposure": True,
         "ratings_sha256": hashlib.sha256(Path(ratings).read_bytes()).hexdigest(),
         "source_labels_sha256": hashlib.sha256((baseline_review / "ai-source-judgments.csv").read_bytes()).hexdigest(),
         "limits": ["Same AI implementer judged outputs after seeing them; not blinded or independent.",
                    "Cases were exposed during improvements: development improvement, not held-out generalization.",
                    "New decisive citations are backend-selected, not model-selected.",
                    "Whole pipelines differ in facts, prompts, source binding and guards; no isolated LLM/retrieval causal claim."]})
    return groups


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("repair", "form", "summarize"))
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--run", type=Path)
    parser.add_argument("--baseline-review", type=Path)
    parser.add_argument("--ratings", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "repair":
        result = repairs(args.package, args.output)
    elif args.command == "form":
        result = form(args.package, args.run, args.baseline_review, args.output)
    else:
        result = summarize(args.package, args.run, args.baseline_review, args.ratings, args.output)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
