"""Explain retained mechanical-control rejections without changing the candidate."""
from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import yaml
from scripts.llm_quality_study import repair_cases, save


def main():
    output = Path(__file__).with_name("reference-lint-diagnostics.json")
    if output.exists():
        raise FileExistsError(output)
    mechanical = json.loads(Path(__file__).with_name("reference-mechanical-results.json").read_text())
    rejected = {r["case_id"] for r in mechanical["records"] if r["status"] != "passed"}
    results = []
    for case in repair_cases():
        if case["case_id"] not in rejected:
            continue
        task = yaml.safe_load(case["files"]["tasks.yml"])[0]
        if case["family"] == "missing-validate-certs":
            task["ansible.builtin.get_url"]["validate_certs"] = True
        else:
            task["no_log"] = True
        with tempfile.TemporaryDirectory(prefix="retained-lint-diagnostic-") as directory:
            root = Path(directory)
            target = root / "tasks.yml"
            target.write_text(yaml.safe_dump([task], sort_keys=False))
            (root / "lint.yml").write_text("offline: true\n")
            (root / "ansible.cfg").write_text("[defaults]\n")
            result = subprocess.run([str(ROOT / ".venv/bin/ansible-lint"), "--offline", "--nocolor", "-f", "json",
                "-c", str(root / "lint.yml"), str(target)], cwd=root, env={**os.environ,
                "ANSIBLE_CONFIG": str(root / "ansible.cfg"), "ANSIBLE_HOME": str(root / "ansible"),
                "ANSIBLE_LOCAL_TEMP": str(root / "ansible/tmp")}, capture_output=True, text=True, timeout=30)
            results.append({"case_id": case["case_id"], "returncode": result.returncode,
                            "stdout": result.stdout, "stderr": result.stderr})
    save(output, {"purpose": "diagnose existing authored-control rejections; no retries or model result replacement", "results": results})
    print(json.dumps({"diagnosed": len(results), "output": str(output)}))


if __name__ == "__main__":
    main()
