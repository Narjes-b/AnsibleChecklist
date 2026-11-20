"""Rebuild the operational report without inventing semantic or human results."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.llm_quality_study import diagnostics, implementation, load, read_package, save, table


def quantile(values, fraction):
    values = sorted(values)
    if not values:
        return None
    index = (len(values) - 1) * fraction
    lower = int(index)
    upper = min(lower + 1, len(values) - 1)
    return values[lower] + (values[upper] - values[lower]) * (index - lower)


def main():
    package = Path(__file__).resolve().parent
    run = ROOT / "study/runs/llm-quality-2026-11-14-explanation"
    manifest, frozen = read_package(package), load(package / "freeze.json")
    progress = load(run / "run-manifest.json")
    behavior = load(ROOT / "study/runs/llm-quality-2026-11-14-reference-controls-v3.json")
    mechanical = load(package / "reference-mechanical-results.json")
    state = {"scope": "explanation and semantic-repair evaluation; developer recruitment deferred by owner",
             "papers_modified": False, "frozen_implementation_matches": implementation() == frozen["implementation"],
             "manifest_sha256": manifest["sha256"], "freeze_sha256": frozen["sha256"],
             "explanation": {"scheduled": 96, "recorded": progress["completed"], "execution": progress["status"],
                             "independent_source_review": "pending", "independent_output_review": "pending"},
             "semantic_repairs": {"source_cases": 12, "model_inference": "waiting for independent source/intent review",
                "human_semantic_review": "pending", "authored_behavior_controls_passed": sum(r["passed"] for r in behavior["results"]),
                "authored_behavior_controls_total": len(behavior["results"]),
                "authored_mechanical_controls_passed": sum(r["status"] == "passed" for r in mechanical["records"]),
                "authored_mechanical_controls_total": len(mechanical["records"]),
                "model_fix_quality": "unmeasured; authored controls are not generated repairs"},
             "developer_comprehension": {"status": "deferred-by-owner", "participants": 0, "benefit": "unmeasured"}}
    summaries = []
    if progress["status"] == "completed":
        diagnostics(package, run, package / "explanation-operational-records.json")
        rows = load(package / "explanation-operational-records.json")["rows"]
        for kind in ("all", "controlled", "real"):
            for mode in ("window", "scoped"):
                selected = [r for r in rows if r["mode"] == mode and (kind == "all" or r["kind"] == kind)]
                times = [r["wall_seconds"] for r in selected if isinstance(r["wall_seconds"], (int, float))]
                prompt_tokens = [r["tokens"]["prompt_eval_count"] for r in selected
                                 if r["tokens"] and isinstance(r["tokens"].get("prompt_eval_count"), int)]
                generation_tokens = [r["tokens"]["eval_count"] for r in selected
                                     if r["tokens"] and isinstance(r["tokens"].get("eval_count"), int)]
                summaries.append({"kind": kind, "mode": mode, "scheduled": len(selected),
                    "available_outputs": sum(r["status"] == "ok" for r in selected),
                    "failures_or_missing": sum(r["status"] != "ok" for r in selected),
                    "predicate_verified_packets": sum(r["backend_predicate"] for r in selected),
                    "missing_required_evidence_packets": sum(r["required_abstention"] for r in selected),
                    "raw_code_proposals": sum(r["raw_fix_proposed"] for r in selected),
                    "delivered_code_suggestions": sum(r["returned_fix"] for r in selected),
                    "timed_records": len(times), "latency_p50_seconds": quantile(times, .5),
                    "latency_p95_seconds": quantile(times, .95),
                    "prompt_token_records": len(prompt_tokens), "prompt_tokens_total": sum(prompt_tokens),
                    "generation_token_records": len(generation_tokens), "generation_tokens_total": sum(generation_tokens)})
        table(package / "explanation-operational-summary.csv", list(summaries[0]), summaries)
        state["explanation"]["operational_summary"] = summaries
        state["explanation"]["status_counts"] = dict(Counter(r["status"] for r in rows))
        errors = []
        for case_id, mode in progress["schedule"]:
            record = load(run / f"{case_id}-{mode}.json")
            if record["result"]["llm_status"] != "ok":
                errors.append({"case_id": case_id, "mode": mode, "status": record["result"]["llm_status"],
                               "reason": record["result"].get("llm_error", "Interrupted runtime; in-flight outcome unknown, not retried.")})
        save(package / "execution-failures.json", errors)
    state["analysis_script_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    save(package / "STATUS.json", state)
    lines = ["# Automated evaluation status", "", "Paper files are unchanged. Developer recruitment is deferred by the owner.", "",
             f"Frozen comparison: {progress['completed']}/96 scheduled records; execution {progress['status']}.", "",
             "These are output availability and operational counts, not explanation correctness or model accuracy.", ""]
    if summaries:
        lines += ["| Condition | Scheduled | Available output | Failed/missing | Code suggestions delivered |",
                  "|---|---:|---:|---:|---:|"]
        for row in summaries:
            if row["kind"] == "all":
                lines.append(f"| {row['mode']} | {row['scheduled']} | {row['available_outputs']} | {row['failures_or_missing']} | {row['delivered_code_suggestions']} |")
        lines += ["", "See explanation-operational-summary.csv for real/controlled breakdowns, bounded backend checks, latency and tokens.", ""]
    lines += ["## Repair controls", "",
              "Eight authored reference edits pass the bounded behavioral scenarios; six pass the existing mechanical gate.",
              "The other two are withheld because the validator reserializes task tag lists with indentation rejected by ansible-lint.",
              "Keep this limitation; do not tune the frozen candidate on evaluation outputs.", "",
              "The first two harness runs are retained under study/runs/. They exposed temporary-directory, inline-secret error-excerpt,",
              "and TLS trust-configuration problems before the final successful reference-control run.", "",
              "Authored-control success is not model-generated repair correctness. The 12-case repair inference remains gated on human source/intent review.", "",
              "## Remaining human work", "",
              "Use the separate reviewer A/B source ZIPs (60 active cases each). Reviewers judge independently before seeing outputs.",
              "After source adjudication, export shuffled output packets, obtain both independent output reviews and adjudicate separately.",
              "Repair sources need approved intent before inference; proposed edits then need behavioral checks and independent semantic review.",
              "No independent explanation correctness, generated-fix semantic correctness, or developer benefit has yet been established.", "",
              "## Runtime interruption", "",
              "The execution service restarted during the comparison. Completed outputs were retained; the one unknown in-flight outcome",
              "was recorded as interrupted-unknown and was not retried. The installed model digest and frozen implementation remained unchanged.", ""]
    (package / "AUTOMATED_RESULTS.md").write_text("\n".join(lines))
    print(json.dumps({"recorded": progress["completed"], "execution": progress["status"], "independent_quality": "pending"}))


if __name__ == "__main__":
    main()
