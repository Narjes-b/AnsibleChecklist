# -*- coding: utf-8 -*-
"""Task 3: build the side-by-side comparison of the existing agent's label/
explanation against the local model's explanation, for the same evaluation
cases, with a rubric scoring template a human fills in.

This script does NOT compute a verdict. It assembles the raw material
(original issue, existing agent label+explanation, local model's explanation)
into one row per case, with the six rubric dimensions as empty columns for a
human (or a documented, separate scoring pass) to fill in — exactly the same
"don't silently resolve, preserve for human review" posture as Task 1.
"""
import csv
import json
from pathlib import Path

EVAL_CASES = Path("eval/eval_cases.csv")
EVAL_OUTPUTS = Path("eval/eval_outputs")
OUT_CSV = Path("task3-comparison.csv")

RUBRIC_COLUMNS = [
    "technical_correctness",     # does it match the code and applicable Ansible behavior?
    "contextual_grounding",      # does it rely on evidence actually in the supplied context?
    "diagnostic_clarity",        # root cause, not just restating the warning?
    "remediation_quality",       # is the fix appropriate, valid, justified?
    "uncertainty_calibration",   # does it acknowledge missing info appropriately?
    "actionability",             # could a developer act on this?
]


def main():
    with open(EVAL_CASES, newline="", encoding="utf-8") as f:
        cases = list(csv.DictReader(f))

    rows = []
    for case in cases:
        issue_id = case["issue_id"]
        record_path = EVAL_OUTPUTS / f"{issue_id}.json"
        if record_path.is_file():
            record = json.loads(record_path.read_text(encoding="utf-8"))
            explanation = record.get("explanation") or {}
            exec_status = record["execution"]["status"]
            exec_warnings = "; ".join(record["execution"]["warnings"])
        else:
            explanation = {}
            exec_status = "not_run"
            exec_warnings = "local model was not run for this case in this session"

        row = {
            "issue_id": issue_id,
            "rule_id": case["rule_id"],
            "repository": case["repository"],
            "path": case["path"],
            "line_start": case["line_start"],
            "original_code_snippet": case["original_code_or_issue"][:2000],
            # existing agent (mine, from Task 1's consolidated file)
            "existing_agent_label": case["my_label_semantic"],
            "existing_agent_actionability": case["my_label_actionability"],
            "existing_agent_explanation": case["my_explanation"],
            # teammate's agent, for three-way context (not the primary Task 3 comparison,
            # but useful since Task 1 already shows where the two agents diverge)
            "teammate_agent_label": case["teammate_label_semantic"],
            "teammate_agent_explanation": case["teammate_explanation"],
            # local model
            "local_model_status": exec_status,
            "local_model_warnings": exec_warnings,
            "local_model_what_is_wrong": explanation.get("what_is_wrong", ""),
            "local_model_why_it_is_wrong": explanation.get("why_it_is_wrong", ""),
            "local_model_why_in_context": explanation.get("why_in_this_context", ""),
            "local_model_consequences": explanation.get("potential_consequences", ""),
            "local_model_recommended_fix": explanation.get("recommended_fix", ""),
            "local_model_fixed_snippet": explanation.get("fixed_code_snippet", ""),
            "local_model_why_fix_works": explanation.get("why_fix_works", ""),
            "local_model_trade_offs": explanation.get("trade_offs_and_assumptions", ""),
            "local_model_confidence": explanation.get("confidence", ""),
            "local_model_limitations": explanation.get("limitations", ""),
            # agreement between existing agent and local model's bottom-line read
            "labels_agree": "",  # fill in: does the local model's narrative agree the issue is real/not real, matching existing_agent_label?
        }
        for col in RUBRIC_COLUMNS:
            row[col] = ""  # 1-5 or short note; left blank, human/review pass fills in
        row["unsupported_claims_or_errors"] = ""
        row["human_review_notes"] = ""
        rows.append(row)

    fieldnames = list(rows[0].keys())
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    print(f"wrote {len(rows)} rows to {OUT_CSV}")
    not_run = sum(1 for r in rows if r["local_model_status"] == "not_run")
    if not_run:
        print(f"NOTE: {not_run}/{len(rows)} cases have no local-model output yet "
              f"(not_run) — run eval/run_eval.py against a live Ollama instance, "
              f"then re-run this script to fill those rows in.")


if __name__ == "__main__":
    main()
