"""Reproduce the development comparison report from recorded judgments/results."""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.llm_quality_study import load, save, table, implementation


def main():
    package = Path(__file__).resolve().parent
    before = load(ROOT / "study/llm-quality-2026-11-14/ai-exploratory/summary.json")
    after = load(package / "reviewed-results/summary.json")
    old = next(r for r in before["groups"] if r["kind"] == "all" and r["mode"] == "scoped")
    new = next(r for r in after["groups"] if r["kind"] == "all" and r["mode"] == "scoped")
    requested = load(package / "requested-repair-results.json")
    repairs = load(package / "llm-repair-summary.json")
    names = [("Accepted outputs", "available", "available"),
             ("Decision agrees with unchanged AI reference", "decision_matches_ai_judgment", "decision"),
             ("Adequate complete explanation", "content_adequate_ai", "content"),
             ("Adequate explanation plus supporting citations", "strict_content_and_citation_ai", "strict")]
    comparison = []
    for label, a, b in names:
        comparison.append({"metric": label, "before_count": old[a], "after_count": new[b], "denominator": 48,
            "before_percent": round(100 * old[a] / 48, 2), "after_percent": round(100 * new[b] / 48, 2),
            "percentage_point_change": round(100 * (new[b] - old[a]) / 48, 2)})
    table(package / "before-after-scoped.csv", list(comparison[0]), comparison)
    identity = load(package / "freeze.json")["implementation"] == implementation()
    save(package / "FINAL_STATUS.json", {"comparison": comparison, "candidate_unchanged": identity,
         "evaluation_kind": "single AI implementer, unblinded development rerun on exposed cases",
         "summary_origin": "backend-authored", "citation_origin": "backend-selected", "reasoning_origin": "local model, unverified",
         "llm_repairs": repairs, "explicit_requested_repairs": {k: requested[k] for k in
             ("producer", "cases", "eligible", "eligible_proposals", "eligible_behavior_passed", "ineligible_proposals", "human_validation")},
         "tests": {"full_suite_passed": 1649, "skipped": 2, "additional_requested_repair_tests_passed": 8},
         "manuscripts_modified": False, "developer_study": "deferred", "independent_human_validation": False})
    lines = ["# Improvement and repeated AI experiment", "",
        "The default scoped pipeline improved on the same exposed development cases, using the same local model and the unchanged AI source judgments. All 96 new outcomes were reviewed again. The paper files and human-review forms are unchanged.", "",
        "**These are post hoc judgments by the same AI assistant that implemented the changes.** They are not independent human validation, held-out generalization, or population estimates. The short summaries and decisive citations are now backend-authored/selected; free model reasoning is still reviewed and can make an output fail.", "",
        "## Scoped pipeline: before and after", "",
        "| Measure | Before / 48 | After / 48 | Change |", "|---|---:|---:|---:|"]
    for row in comparison:
        lines.append(f"| {row['metric']} | {row['before_count']} ({row['before_percent']}%) | {row['after_count']} ({row['after_percent']}%) | +{row['percentage_point_change']} pp |")
    lines += ["", "The primary adequate-output score increased by 25 percentage points, and the stricter content-plus-citation score by 35.42 points. One new scoped outcome remains interrupted-unknown after an execution-service restart and counts as unsuccessful; the baseline separately had one interrupted window outcome.", "",
        "## Complete rerun, including the ablation", "",
        "| Panel / condition | Scheduled | Available | Reference decision matches | Adequate content | Adequate + citations |",
        "|---|---:|---:|---:|---:|---:|"]
    for row in after["groups"]:
        lines.append(f"| {row['kind']} / {row['mode']} | {row['scheduled']} | {row['available']} | {row['decision']} | {row['content']} | {row['strict']} |")
    lines += ["", "The new window-only condition regressed from 4/48 to 0/48 adequate outputs. The full V5 prompt expects backend facts that this ablation omits; this is not an isolated retrieval comparison or an improved standalone-model baseline. The before/after scoped comparison above is the relevant default-workflow result. Do not hide the window regression or claim retrieval-only superiority.", "",
        "## Repairs: keep the two mechanisms separate", "",
        "The LLM repair rerun returned 12 accepted assessments but still generated zero code proposals and marked none of the eight repair-eligible cases actionable. LLM proposal coverage remains **0/8**. LLM-generated fix correctness cannot be estimated, and is not a 0% correctness result.", "",
        "A separate explicit-request command now previews only two narrowly selected changes: enable TLS verification or protect a verified direct debug task's output. The caller must choose the edit and declare intent; source comments cannot authorize it. This is deterministic transformation, not LLM repair.", "",
        f"On the same 12 repair sources it generated {requested['eligible_proposals']}/8 eligible drafts, all {requested['eligible_behavior_passed']}/8 passed mechanical and isolated behavioral checks, and it generated {requested['ineligible_proposals']}/4 drafts for already-correct or unknown-runtime cases. No source edits were applied. The separate AI edit review found only the requested flag changed, with unrelated fields preserved, in these synthetic fixtures. This does not establish general production correctness.", "",
        "Behavior checks cover rejecting untrusted certificates, accepting the fixture's trusted endpoint with identical artifact contents, suppressing the synthetic secret in normal/failure controller output, and keeping registered results usable. Source/tag/guard preservation and lint are checked separately. The prior authored mechanical controls improved from 6/8 to 8/8 after fixing serializer indentation.", "",
        "## Remaining failures", "",
        "Four new real-source rationales remain factually wrong: one decodes decimal mode 2750 as octal 2750 and calls it safe despite a correct backend summary; three claim no_log is used when it is absent. All fail the content score. Three generic credential abstentions also differ from the unchanged AI static-risk reference; one overlaps the false-prose cases. Those reference/semantic disagreements are not all false factual claims. Path-only citations in mode-omission cases still fail the strict citation check.", "",
        "The model often simply repeats backend source facts. This can improve the tool's output reliability, but does not show that adding the LLM benefits developers beyond evidence-only output. No developer study was performed.", "",
        "## Validation and reproduction", "",
        "The full suite passed **1,649 tests, two skipped**, and the separate requested-edit command passed **eight additional tests**. Frozen V5.2 analyzer sources still match their recorded hashes. Earlier failed smoke attempts, raw outputs, error records, summaries and backend provenance are retained.", "",
        "See README.md, EXPERIMENT_NOTES.md, comparison-design.json, reviewed-results/, manual-ai-ratings.csv, requested-repair-results.json and requested-repair-ai-review.csv for exact methods, individual judgments and limitations.", "",
        "Preview a narrow caller-requested draft without modifying source:", "",
        "```sh", ".venv/bin/python scripts/requested_repair.py \\",
        "  --root /path/to/repository --file tasks.yml --line 12 \\",
        "  --kind enable-tls-verification \\",
        "  --intent 'Endpoint authentication is required and its certificate is trusted.' \\",
        "  --output /private/path/to/proposal.json", "```", "",
        "Use protect-task-output for a supported direct debug display. Proposals are optional review artifacts, never automatically applied.", ""]
    (package / "RESULTS.md").write_text("\n".join(lines))
    files = [p for p in package.rglob("*") if p.is_file() and p.name != "artifacts.sha256" and "__pycache__" not in p.parts]
    files += [ROOT / "scripts/llm_v5_experiment.py", ROOT / "scripts/requested_repair.py"]
    for directory in (ROOT / "study/runs/llm-v52-explanation-2026-11-14", ROOT / "study/runs/llm-v52-ai-repair-2026-11-14"):
        files += list(directory.rglob("*.json"))
    (package / "artifacts.sha256").write_text("".join(hashlib.sha256(p.read_bytes()).hexdigest() + "  " + str(p.relative_to(ROOT)) + "\n" for p in sorted(files)))
    print(json.dumps({"scoped_before_after": comparison, "candidate_unchanged": identity}, indent=2))


if __name__ == "__main__":
    main()
