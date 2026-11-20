"""Evaluate actual model-written explicit-request edits, separately from triage."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.requested_repair import propose, KINDS
from scripts.llm_quality_study import read_package, save, table, load, implementation, case_root, write_checkpoint
from scripts.llm_behavior_checks import container_check, IMAGE


def main():
    package = Path(__file__).resolve().parent
    output = ROOT / "study/runs/llm-v6-model-requested-edits-2026-11-14"
    frozen = load(package / "freeze.json")
    if frozen["implementation"] != implementation():
        raise ValueError("frozen candidate changed")
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    image = subprocess.run(["docker", "image", "inspect", IMAGE, "--format", "{{.Id}}"], capture_output=True, text=True, check=True).stdout.strip()
    cases = read_package(package)["panels"]["repair"]
    header = {"status": "in-progress", "completed": 0, "freeze_sha256": frozen["sha256"], "image": image,
              "harness_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "task": "explicit requested code generation, not autonomous actionability/repair triage",
              "reference_after_task_supplied_to_model": False, "retry_policy": "one attempt; never replace failures"}
    write_checkpoint(output, "run-manifest", header)
    rows = []
    for case in cases:
        kind = next(k for k, family in KINDS.items() if family == case["family"])
        with case_root(case, ROOT / "study/repositories") as root:
            before = (root / "tasks.yml").read_bytes()
            proposal = propose(root, case["occurrence"], kind, caller_intent=case["intent"], generator="local-model")
            assert before == (root / "tasks.yml").read_bytes()
        behavior = None
        if proposal["status"] == "proposal-ready":
            behavior = container_check({"before": case["files"]["tasks.yml"], "after": proposal["snippet"], "family": case["family"]}, image)
        record = {"case_id": case["case_id"], "stratum": case["repair_stratum"], "proposal": proposal, "behavior": behavior}
        write_checkpoint(output, case["case_id"], record)
        row = {"case_id": case["case_id"], "eligible": case["repair_stratum"] == "eligible",
               "model_called": "model_attempt" in proposal, "proposal_ready": proposal["status"] == "proposal-ready",
               "mechanical": proposal.get("validation", {}).get("status"), "behavior_passed": bool(behavior and behavior.get("passed")),
               "reason": proposal.get("reason", ""), "origin": proposal["origin"]}
        rows.append(row)
        header["completed"] += 1
        write_checkpoint(output, "run-manifest", header)
        print(json.dumps(row), flush=True)
    table(package / "model-requested-edits.csv", list(rows[0]), rows)
    save(package / "model-requested-edits-summary.json", {"rows": rows, "eligible": 8,
         "eligible_drafts": sum(r["eligible"] and r["proposal_ready"] for r in rows),
         "eligible_behavior_passed": sum(r["eligible"] and r["behavior_passed"] for r in rows),
         "ineligible_drafts": sum(not r["eligible"] and r["proposal_ready"] for r in rows),
         "source_applied": False, "independent_human_validation": False,
         "task_change": "Caller explicitly selects the transformation; model is not asked to discover whether repair is actionable.",
         "not_a_spontaneous_fix_rate": True, "AI_semantic_review": "pending inspection of raw generated tasks and behavior"})
    header["status"] = "completed"
    write_checkpoint(output, "run-manifest", header)


if __name__ == "__main__":
    main()
