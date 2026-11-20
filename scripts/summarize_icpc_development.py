#!/usr/bin/env python3
"""Audit development outputs against engineering contracts, never human gold.

Every selected case stays in the denominator. Raw model choices, validated
pipeline choices, constrained abstentions, and execution failures are separate.
Only development IDs are read; evaluation outputs are not inspected.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path

MODES = ("window", "scoped")


def _raw_object(record):
    try:
        value = json.loads(record.get("raw_response") or "")
        return value if isinstance(value, dict) else {}
    except (ValueError, TypeError):
        return {}


def summarize(manifest_path, run_dir, output):
    manifest = json.loads(Path(manifest_path).read_text())
    actual = hashlib.sha256(json.dumps([manifest["development"], manifest["evaluation"]],
        sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()
    if actual != manifest.get("cases_sha256"):
        raise ValueError("case manifest checksum mismatch")
    run_dir, output = Path(run_dir), Path(output)
    run = json.loads((run_dir / "run-manifest.json").read_text())
    if run.get("panel") != "development" or run.get("status") != "completed" or run.get("pending"):
        raise ValueError("a completed development run is required")
    if run.get("cases_sha256") != manifest.get("cases_sha256"):
        raise ValueError("case identity differs from the recorded run")
    rows, models, prompts = [], set(), set()
    for case in manifest["development"]:
        for mode in MODES:
            path = run_dir / f"{case['case_id']}-{mode}.json"
            record = json.loads(path.read_text())
            if (record.get("case_id") != case["case_id"] or record.get("mode") != mode
                    or record.get("cases_sha256") != manifest["cases_sha256"]):
                raise ValueError(f"record identity mismatch: {path.name}")
            models.add(record["model_digest"])
            prompts.add(record["prompt_version"])
            result, raw = record["result"], _raw_object(record)
            packet = result.get("llm_evidence_packet") or record.get("evidence_packet") or {}
            validation = result.get("llm_suggestion_validation") or {}
            required_context = packet.get("coverage") == "specialized" and bool(packet.get("missing"))
            verified = (packet.get("coverage") == "specialized" and not required_context
                        and (packet.get("predicate_check") or {}).get("status") == "verified")
            expected = case["engineering_expectation"]
            rows.append({
                "case_id": case["case_id"], "family": case["family"], "mode": mode,
                "engineering_expectation": expected, "status": result["llm_status"],
                "raw_assessment": raw.get("assessment", ""),
                "raw_expectation_match": raw.get("assessment") == expected,
                "returned_assessment": result.get("llm_assessment", ""),
                "pipeline_expectation_match": result["llm_status"] == "ok" and result.get("llm_assessment") == expected,
                "schema_requires_abstention": required_context,
                "schema_constrained_predicate": verified,
                "decision_basis": "required-context" if required_context else "backend-predicate" if verified else "model",
                "raw_suggestion_proposed": any(raw.get(key) is not None for key in ("recommended_fix", "fixed_code_snippet")),
                "suggestion_validation": validation.get("status", "not-returned"),
                "suggestion_reason": validation.get("reason", ""),
                "error": result.get("llm_error", ""),
                "duration_seconds": record.get("duration_seconds", result.get("llm_duration_seconds")),
                "prompt_tokens": (result.get("llm_token_usage") or record.get("token_usage") or {}).get("prompt_eval_count"),
                "output_tokens": (result.get("llm_token_usage") or record.get("token_usage") or {}).get("eval_count"),
            })
    if len(models) != 1 or len(prompts) != 1 or models != {run.get("model_digest")}:
        raise ValueError("model or prompt identities changed within the run")

    def counts(selected):
        return {"selected": len(selected), "status_counts": dict(Counter(row["status"] for row in selected)),
                "engineering_expectation_matches": sum(row["pipeline_expectation_match"] for row in selected),
                "validated_mismatches": sum(row["status"] == "ok" and not row["pipeline_expectation_match"] for row in selected),
                "unanswered": sum(row["status"] != "ok" for row in selected),
                "raw_expectation_matches": sum(row["raw_expectation_match"] for row in selected),
                "schema_constrained_abstentions": sum(row["schema_requires_abstention"] for row in selected),
                "schema_constrained_predicates": sum(row["schema_constrained_predicate"] for row in selected),
                "unconstrained_decisions": sum(row["decision_basis"] == "model" for row in selected),
                "unconstrained_raw_matches": sum(row["decision_basis"] == "model" and row["raw_expectation_match"] for row in selected),
                "returned_abstentions": sum(row["returned_assessment"] == "insufficient-evidence" for row in selected),
                "suggestion_validation": dict(Counter(row["suggestion_validation"] for row in selected))}

    summary = {"purpose": "controlled development diagnostics; not human accuracy or population scoring",
               "model_digest": next(iter(models)), "prompt_version": next(iter(prompts)),
               "cases_sha256": manifest["cases_sha256"], "run": str(run_dir),
               "modes": {mode: counts([row for row in rows if row["mode"] == mode]) for mode in MODES},
               "families": {family: {mode: counts([row for row in rows if row["family"] == family and row["mode"] == mode])
                                     for mode in MODES} for family in sorted({row["family"] for row in rows})},
               "limitations": ["Engineering expectations are not human gold labels.",
                   "Scoped mode includes backend eligibility, predicate and generation constraints; this is not a retrieval-only or model-only comparison.",
                   "Suggestion checks depend on packet availability; mechanical checks are not human safety judgments.",
                   "Modes ran window then scoped with one attempt each; timings are not a controlled speed benchmark.",
                   "The evaluation panel and reviewer judgments were not scored."]}
    output.mkdir(parents=True, exist_ok=False)
    with (output / "decisions.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    failures = [row for row in rows if not row["pipeline_expectation_match"]]
    (output / "failures.json").write_text(json.dumps(failures, indent=2) + "\n")
    files = [run_dir / f"{case['case_id']}-{mode}.json" for case in manifest["development"] for mode in MODES]
    (output / "input-checksums.json").write_text(json.dumps(
        {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in files}, indent=2) + "\n")
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(summarize(args.manifest, args.run, args.output)["modes"], indent=2))


if __name__ == "__main__":
    main()
