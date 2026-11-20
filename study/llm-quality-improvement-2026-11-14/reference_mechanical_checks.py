"""Reproduce authored-control mechanical validation, not model repair accuracy."""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import tempfile
import yaml
from scripts.llm_quality_study import repair_cases, packet_for, save
from ansibleguard.report.llm_suggestions import validate_suggestion


def main():
    target = Path(__file__).with_name("reference-mechanical-results.json")
    if target.exists():
        raise FileExistsError("keep prior control results")
    records = []
    for case in repair_cases():
        if case["repair_stratum"] != "eligible":
            continue
        source = case["files"]["tasks.yml"]
        replacement = yaml.safe_load(source)[0]
        if case["family"] == "missing-validate-certs":
            replacement["ansible.builtin.get_url"]["validate_certs"] = True
        else:
            replacement["no_log"] = True
        with tempfile.TemporaryDirectory(prefix="reference-mechanical-") as temporary:
            root = Path(temporary)
            (root / "tasks.yml").write_text(source)
            packet = packet_for(case, root)
            outcome = validate_suggestion(packet, yaml.safe_dump([replacement], sort_keys=False), source.splitlines())
        records.append({"case_id": case["case_id"], "producer": "authored-reference-control", **outcome})
    save(target, {"script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "records": records,
                  "model_fix_quality": "not measured by authored controls"})
    print(json.dumps({"cases": len(records), "passed": sum(r["status"] == "passed" for r in records)}))


if __name__ == "__main__":
    main()
