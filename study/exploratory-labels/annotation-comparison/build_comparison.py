# -*- coding: utf-8 -*-
"""Phase 1: consolidate and compare two independent AI reviewers' annotations of
the same 350-item agreement-pilot sample.

Reviewer A: ai-shadow-review/agreement-pilot-ai-shadow-completed.csv
Reviewer B: teammate-review/REVIEWER_C_AI_PRECHECK.csv

Both files share the exact same schema and row identity (sample_id), since both
reviewers labeled the same frozen agreement-pilot master. Reviewer identity is
deliberately generic (A/B) rather than naming which underlying model produced
each pass — that detail is not material to the agreement statistics and is kept
out of this deliverable by request.

This script does NOT reconcile disagreements or pick a winner — it only
classifies *how* the two records relate (agreement / partial agreement /
disagreement / insufficient information), using a documented, mechanical rule,
and leaves `final_validated_label` empty for every row.
"""
import csv
from pathlib import Path

REVIEWER_A = Path("../ai-shadow-review/agreement-pilot-ai-shadow-completed.csv")
REVIEWER_B = Path("../teammate-review/REVIEWER_C_AI_PRECHECK.csv")
OUT_CSV = Path("consolidated-comparison.csv")

UNCERTAIN_LABELS = {"uncertain", "unreviewable"}


def load(path):
    with open(path, newline="", encoding="utf-8") as f:
        return {row["sample_id"]: row for row in csv.DictReader(f)}


def classify(a, b):
    """Returns (agreement_status, disagreement_category) using a fixed,
    documented rule — never an LLM judgment call, so it's fully reproducible."""
    al, bl = a["ai_semantic_label"], b["ai_semantic_label"]
    aa, ba = a["ai_actionability_label"], b["ai_actionability_label"]
    ar, br = a["ai_reason_code"], b["ai_reason_code"]

    a_unc = al in UNCERTAIN_LABELS
    b_unc = bl in UNCERTAIN_LABELS

    if a_unc or b_unc:
        if al == bl:
            # both landed on the same uncertain/unreviewable call
            if ar == br:
                return "Agreement", ""
            return "Partial agreement", "interpretation (same uncertainty call, different reason_code)"
        # one side called it definitively, the other said the evidence wasn't enough
        return "Insufficient information", "evidence-sufficiency (one reviewer found the context sufficient to decide, the other did not)"

    if al != bl:
        return "Disagreement", "classification (different semantic_label: %s vs %s)" % (al, bl)

    # same semantic_label, both confident (non-uncertain) calls
    if aa != ba and ar != br:
        return "Partial agreement", "severity/remediation and interpretation (actionability: %s vs %s; reason_code: %s vs %s)" % (aa, ba, ar, br)
    if aa != ba:
        return "Partial agreement", "severity/remediation (actionability: %s vs %s)" % (aa, ba)
    if ar != br:
        return "Partial agreement", "interpretation (reason_code: %s vs %s)" % (ar, br)
    return "Agreement", ""


def code_snippet(row):
    ctx = row.get("source_context", "")
    # keep the full frozen context — it IS the evidence record; do not trim it,
    # since trimming could hide the exact line a human reviewer needs to see.
    return ctx


def main():
    a_rows = load(REVIEWER_A)
    b_rows = load(REVIEWER_B)

    a_ids = set(a_rows)
    b_ids = set(b_rows)
    assert a_ids == b_ids, f"ID set mismatch: a-only={a_ids - b_ids}, b-only={b_ids - a_ids}"

    rows = []
    for sid in sorted(a_rows, key=lambda s: (a_rows[s]["review_family"], s)):
        a, b = a_rows[sid], b_rows[sid]
        status, category = classify(a, b)
        rows.append({
            "issue_id": sid,
            "review_family": a["review_family"],
            "rule_id": a["rule_id"],
            "repository": a["repository"],
            "commit_sha": a["commit_sha"],
            "path": a["path"],
            "line_start": a["line_start"],
            "line_end": a["line_end"],
            "review_question": a["review_question"],
            "original_code_or_issue": code_snippet(a),
            "reviewer_a_label_semantic": a["ai_semantic_label"],
            "reviewer_a_label_actionability": a["ai_actionability_label"],
            "reviewer_a_reason_code": a["ai_reason_code"],
            "reviewer_b_label_semantic": b["ai_semantic_label"],
            "reviewer_b_label_actionability": b["ai_actionability_label"],
            "reviewer_b_reason_code": b["ai_reason_code"],
            "reviewer_a_explanation": a["ai_notes"],
            "reviewer_b_explanation": b["ai_notes"],
            "reviewer_a_confidence": a["ai_confidence"],
            "reviewer_b_confidence": b["ai_confidence"],
            "agreement_status": status,
            "disagreement_category": category,
            "validation_status": "Initially unreviewed",
            "final_validated_label": "",
        })

    fieldnames = list(rows[0].keys())
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    print(f"wrote {len(rows)} rows to {OUT_CSV}")

    # quick sanity tallies for the report script to reuse / cross-check
    from collections import Counter
    status_counts = Counter(r["agreement_status"] for r in rows)
    print("status counts:", dict(status_counts))


if __name__ == "__main__":
    main()
