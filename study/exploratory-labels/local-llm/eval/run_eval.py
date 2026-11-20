# -*- coding: utf-8 -*-
"""Task 2.6: run the local model over the hand-selected evaluation cases and
record what actually happened — this script does not itself declare pass/fail;
it runs the cases and writes the raw results for manual inspection against the
rubric in EVAL_RESULTS.md, per the brief's "do not claim accuracy merely because
it produces convincing explanations" instruction.
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
EXPLAIN = HERE.parent / "scripts" / "explain.py"
EVAL_CASES = HERE / "eval_cases.csv"
EVAL_OUT_DIR = HERE / "eval_outputs"


def main():
    EVAL_OUT_DIR.mkdir(exist_ok=True)
    cmd = [
        sys.executable, str(EXPLAIN),
        "--input", str(EVAL_CASES),
        "--id-col", "issue_id",
        "--out-dir", str(EVAL_OUT_DIR),
    ]
    print("Running:", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print("STDERR:", result.stderr, file=sys.stderr)
        print(f"\nexplain.py exited with code {result.returncode} — this usually means "
              f"Ollama isn't reachable at the configured host. Check `ollama serve` is "
              f"running and the model is pulled (`ollama list`).")
        return result.returncode

    # Summarize what came back, per-case, for manual rubric scoring
    summary = []
    for record_path in sorted(EVAL_OUT_DIR.glob("*.json")):
        record = json.loads(record_path.read_text(encoding="utf-8"))
        summary.append({
            "issue_id": record["issue_id"],
            "rule_id": record["source_location"]["rule_id"],
            "status": record["execution"]["status"],
            "warnings": record["execution"]["warnings"],
            "duration_s": record["execution"]["duration_seconds"],
            "existing_label": record["original_detector_annotation"].get("my_label_semantic"),
            "model_confidence": (record.get("explanation") or {}).get("confidence"),
        })
    (HERE / "eval_run_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nWrote per-case summary to eval_run_summary.json ({len(summary)} cases).")
    print("Next: manually score each case against the Task 3 rubric and fill in EVAL_RESULTS.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
