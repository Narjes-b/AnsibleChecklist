"""Separate explicit-request draft experiment, never LLM repair quality."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.requested_repair import propose, KINDS
from scripts.llm_behavior_checks import container_check, IMAGE
from scripts.llm_quality_study import read_package, save, case_root, table, load


def main():
    package = Path(__file__).resolve().parent
    target = package / "requested-repair-results.json"
    if target.exists():
        raise FileExistsError("never replace experiment records")
    image = subprocess.run(["docker", "image", "inspect", IMAGE, "--format", "{{.Id}}"],
                           capture_output=True, text=True, check=True).stdout.strip()
    rows, details = [], []
    for case in read_package(package)["panels"]["repair"]:
        requested = next(k for k, family in KINDS.items() if family == case["family"])
        with case_root(case, ROOT / "study/repositories") as root:
            before = (root / "tasks.yml").read_bytes()
            proposal = propose(root, case["occurrence"], requested, caller_intent=case["intent"])
            assert (root / "tasks.yml").read_bytes() == before
        behavior = None
        if proposal["status"] == "proposal-ready":
            behavior = container_check({"before": case["files"]["tasks.yml"], "after": proposal["snippet"],
                                        "family": case["family"]}, image)
        rows.append({"case_id": case["case_id"], "stratum": case["repair_stratum"],
                     "proposal_status": proposal["status"], "mechanical": proposal.get("validation", {}).get("status"),
                     "behavior_passed": behavior.get("passed") if behavior else None,
                     "applied_to_source": False, "producer": "deterministic caller-requested transformation, not LLM"})
        details.append({"case_id": case["case_id"], "proposal": proposal, "behavior": behavior})
        print(json.dumps(rows[-1]), flush=True)
    eligible = [r for r in rows if r["stratum"] == "eligible"]
    ineligible = [r for r in rows if r["stratum"] != "eligible"]
    result = {"producer": "deterministic explicit-request tool; NOT an improvement in LLM-generated repair",
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "tool_sha256": hashlib.sha256((ROOT / "scripts/requested_repair.py").read_bytes()).hexdigest(),
              "image_id": image, "cases": 12, "eligible": len(eligible),
              "eligible_proposals": sum(r["proposal_status"] == "proposal-ready" for r in eligible),
              "eligible_behavior_passed": sum(r["behavior_passed"] is True for r in eligible),
              "ineligible_proposals": sum(r["proposal_status"] == "proposal-ready" for r in ineligible),
              "human_validation": False, "ai_semantic_assessment": "pending inspection of recorded edit boundaries and behavioral results",
              "details": details}
    save(target, result)
    table(package / "requested-repair-summary.csv", list(rows[0]), rows)
    print(json.dumps({k: v for k, v in result.items() if k != "details"}, indent=2))


if __name__ == "__main__":
    main()
