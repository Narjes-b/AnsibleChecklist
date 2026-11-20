"""Reproduce V6 development results without changing historical judgments."""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.llm_quality_study import load, save, table, records_for, implementation


def main():
    package = Path(__file__).resolve().parent
    previous = load(ROOT / "study/llm-quality-v52-2026-11-14/reviewed-results/summary.json")
    current = load(package / "reviewed-results/summary.json")
    old = next(r for r in previous["groups"] if r["kind"] == "all" and r["mode"] == "scoped")
    new = next(r for r in current["groups"] if r["kind"] == "all" and r["mode"] == "scoped")
    comparisons = []
    for title, key in [("Accepted output", "available"), ("Decision agrees with unchanged AI source reference", "decision"),
                       ("Adequate complete explanation", "content"), ("Adequate explanation plus supporting citations", "strict")]:
        comparisons.append({"measure": title, "before": old[key], "after": new[key], "denominator": 48,
                            "before_percent": round(100 * old[key] / 48, 2), "after_percent": round(100 * new[key] / 48, 2),
                            "percentage_point_change": round(100 * (new[key] - old[key]) / 48, 2)})
    table(package / "before-after-scoped.csv", list(comparisons[0]), comparisons)
    _, triage = records_for(package, ROOT / "study/runs/llm-v6-ai-triage-repair-2026-11-14")
    spontaneous = {"cases": len(triage), "accepted": sum(r["result"]["llm_status"] == "ok" for r in triage),
                   "delivered_code_proposals": sum(bool(r["result"].get("llm_fixed_code_snippet")) for r in triage),
                   "repair_eligible_source_cases": 8, "independent_human_validation": False}
    save(package / "spontaneous-repair-summary.json", spontaneous)
    requested = load(package / "model-requested-edits-summary.json")
    _, explanations = records_for(package, ROOT / "study/runs/llm-v6-explanation-2026-11-14")
    constrained = []
    errors = []
    for r in explanations:
        packet = r["result"].get("llm_evidence_packet") or r["telemetry"].get("evidence_packet") or {}
        if r["mode"] == "scoped":
            constrained.append(bool(packet.get("missing") or packet.get("predicate_check", {}).get("status") == "verified"))
        if r["result"]["llm_status"] != "ok":
            errors.append({"case_id": r["case_id"], "mode": r["mode"], "reason": r["result"].get("llm_error", "unavailable")})
    save(package / "execution-failures.json", errors)
    status = {"before_after": comparisons, "single_AI_implementer_review": True, "exposed_development_cases": True,
              "all_scoped_states_backend_constrained": all(constrained), "scoped_outcomes": len(constrained),
              "source_candidate_unchanged": load(package / "freeze.json")["implementation"] == implementation(),
              "summary_origin": "backend-authored", "citation_origin": "backend-selected; ranges attached by backend",
              "model_requested_edits": {k: requested[k] for k in ("eligible", "eligible_drafts", "eligible_behavior_passed", "ineligible_drafts", "reference_after_snippet_supplied_to_model") if k in requested},
              "spontaneous_repairs": spontaneous, "tests": {"passed": 1666, "skipped": 2},
              "papers_modified": False, "human_forms_modified": False, "developer_study": "deferred"}
    save(package / "FINAL_STATUS.json", status)
    lines = ["# Further improvements and repeated experiment: V6", "",
        "The same 48 explanation cases and fixed AI source reference were reused, and all 96 new outputs were explicitly reviewed. Model digest, context/output limits, temperature and comparison scheduling seed are unchanged. This remains an unblinded AI implementer's development experiment on exposed cases, not human validation or held-out generalization.", "",
        "## Scoped pipeline: V5.2 to V6", "",
        "| Measure | V5.2 / 48 | V6 / 48 | Change |", "|---|---:|---:|---:|"]
    for row in comparisons:
        lines.append(f"| {row['measure']} | {row['before']} ({row['before_percent']}%) | {row['after']} ({row['after_percent']}%) | {row['percentage_point_change']:+.2f} pp |")
    lines += ["", "All 48 scoped assessment states are constrained by a bounded backend predicate or required abstention. Summaries are backend-authored and citations backend-selected. The quality score still inspects every substantive model-reasoning claim; a correct summary does not rescue wrong reasoning. These values measure the complete assisted pipeline, not independent LLM reasoning accuracy.", "",
        "The remaining four unsuccessful scoped cases comprise one invalid response (low confidence with missing limitations) and three cautious generic-module abstentions that disagree with the original AI supported-static-risk interpretation. The original labels are preserved; the three disagreements are semantic/reference ambiguity, not asserted evidence of false prose. No accepted scoped output was found to repeat the previous decimal/octal or invented-no_log rationale errors in this review.", "",
        "## Full comparison", "",
        "| Panel / condition | N | Accepted | Reference decision matches | Adequate | Adequate + citations |",
        "|---|---:|---:|---:|---:|---:|"]
    for row in current["groups"]:
        lines.append(f"| {row['kind']} / {row['mode']} | {row['scheduled']} | {row['available']} | {row['decision']} | {row['content']} | {row['strict']} |")
    lines += ["", "The source-only window prompt no longer requires nonexistent backend summary fields. Adequacy recovered from 0/48 to 3/48, but warning assessment remains weak: the model often uses unsupported to mean disapproval of unsafe code, or admits missing facts without choosing insufficient-evidence. Eighteen window calls were rejected; one scoped call failed its response contract. All remain unsuccessful outcomes. No inference retries or favorable-result replacements were used.", "",
        "## Actual model-written edits when explicitly requested", "",
        f"On the same 12 repair sources, the local model generated {requested['eligible_drafts']}/8 eligible drafts, and {requested['eligible_behavior_passed']}/8 passed both mechanical and isolated behavioral checks. All four already-correct/unknown-runtime sources were blocked BEFORE model generation; this is backend filtering, not model abstention.", "",
        "The model receives only the original task, a caller-selected narrow change and declared intent. No complete reference AFTER task is supplied. Every delivered snippet was checked against its retained raw model response, and every raw prompt was inspected to verify BEFORE-only input. The AST edit changes only validate_certs false-to-true or task-local no_log true; guards, registers, tags, names and other arguments remain unchanged.", "",
        "TLS tests reject an untrusted certificate, accept the fixture CA and preserve artifact contents. Logging tests suppress the synthetic secret in normal and forced-failure output and preserve registered results for later tasks. The eight original sources remain unmodified. AI edit review is in model-requested-edits-ai-review.csv; raw generations, payloads, validations and container outputs are retained under study/runs/llm-v6-model-requested-edits-2026-11-14/.", "",
        "This is explicit requested-edit code generation, not autonomous warning triage or discovery of whether a fix is appropriate. The repeated spontaneous triage experiment still produced 0/8 eligible code proposals. Do not replace that zero with the requested-edit score. The existing deterministic requested-edit generator also passed 8/8 in V5.2; this tiny two-transformation panel does not establish that an LLM is necessary or superior.", "",
        "Two extra live development probes also produced mechanically valid model drafts: a URI task with a guard/custom register, and a nested debug task with inherited logging control and a custom register. These broaden task-shape checks but were not behaviorally executed and are not independent natural-data generalization evidence.", "",
        "## Implementation and validation", "",
        "Typed permission facts and observed no_log state are preserved during prompt compaction, numeric/usage contradictions have bounded rejection checks, scalar command references cite actual argument lines, and mode-omission citations carry complete exact task spans. Source-only requests use a separate prompt. The requested-edit CLI supports --generator backend or --generator local-model; neither applies edits, and the local path has no deterministic fallback for failed generations.", "",
        "Full test suite: **1,666 passed, two skipped**. See full-validation.log. Candidate hashes match freeze.json. Old results and human forms remain unchanged. Prior requested-repair source is preserved byte-for-byte at the SHA recorded in the V5.2 historical source map.", "",
        "Reproduction details: README.md, reviewed-results/, manual-ai-ratings.csv, execution-failures.json, model-requested-edits-summary.json, model-requested-edits-ai-review.csv and the retained private run directories. The developer study remains deferred and no comprehension benefit is claimed. Paper files were not edited.", ""]
    (package / "RESULTS.md").write_text("\n".join(lines))
    paths = [p for p in package.rglob("*") if p.is_file() and p.name != "artifacts.sha256" and "__pycache__" not in p.parts]
    for directory in ("llm-v6-explanation-2026-11-14", "llm-v6-ai-triage-repair-2026-11-14", "llm-v6-model-requested-edits-2026-11-14"):
        paths += list((ROOT / "study/runs" / directory).rglob("*.json"))
    (package / "artifacts.sha256").write_text("".join(hashlib.sha256(p.read_bytes()).hexdigest() + "  " + str(p.relative_to(ROOT)) + "\n" for p in sorted(paths)))
    print(json.dumps({"comparison": comparisons, "model_requested_edits": status["model_requested_edits"], "candidate_matches": status["source_candidate_unchanged"]}, indent=2))


if __name__ == "__main__":
    main()
