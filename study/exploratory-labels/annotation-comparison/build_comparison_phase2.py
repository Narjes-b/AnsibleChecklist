# -*- coding: utf-8 -*-
"""Phase 2: consolidate and compare two independent AI reviewers' annotations of
the same 400-item impact-weighted stratified sample.

Reviewer A: ../stratified-sample/stratified-sample-completed.csv
Reviewer C: ../stratified-sample/stratified-sample-chatgpt-reviewer-c.csv

(Reviewer "B" is reserved for the Phase 1 pairing and does not appear in this
sample; this is a new, third independent pass, hence "C" — see Phase 1's
build_comparison.py for the numbering rationale.)

Both files share the exact same schema and row identity (sample_id). Same
mechanical classification rule as Phase 1 (see classify()); no reconciliation,
no winner picked, `final_validated_label` left empty for every row.
"""
import csv
from pathlib import Path

REVIEWER_A = Path("../stratified-sample/stratified-sample-completed.csv")
REVIEWER_C = Path("../stratified-sample/stratified-sample-chatgpt-reviewer-c.csv")
OUT_CSV = Path("consolidated-comparison-phase2.csv")

UNCERTAIN_LABELS = {"uncertain", "unreviewable"}


def load(path):
    with open(path, newline="", encoding="utf-8") as f:
        return {row["sample_id"]: row for row in csv.DictReader(f)}


def classify(a, c):
    """Identical rule to Phase 1's classify() — kept as a literal copy rather
    than a shared import so each phase's comparison is self-contained and
    independently auditable."""
    al, cl = a["ai_semantic_label"], c["ai_semantic_label"]
    aa, ca = a["ai_actionability_label"], c["ai_actionability_label"]
    ar, cr = a["ai_reason_code"], c["ai_reason_code"]

    a_unc = al in UNCERTAIN_LABELS
    c_unc = cl in UNCERTAIN_LABELS

    if a_unc or c_unc:
        if al == cl:
            if ar == cr:
                return "Agreement", ""
            return "Partial agreement", "interpretation (same uncertainty call, different reason_code)"
        return "Insufficient information", "evidence-sufficiency (one reviewer found the context sufficient to decide, the other did not)"

    if al != cl:
        return "Disagreement", "classification (different semantic_label: %s vs %s)" % (al, cl)

    if aa != ca and ar != cr:
        return "Partial agreement", "severity/remediation and interpretation (actionability: %s vs %s; reason_code: %s vs %s)" % (aa, ca, ar, cr)
    if aa != ca:
        return "Partial agreement", "severity/remediation (actionability: %s vs %s)" % (aa, ca)
    if ar != cr:
        return "Partial agreement", "interpretation (reason_code: %s vs %s)" % (ar, cr)
    return "Agreement", ""


def main():
    a_rows = load(REVIEWER_A)
    c_rows = load(REVIEWER_C)

    a_ids = set(a_rows)
    c_ids = set(c_rows)
    assert a_ids == c_ids, f"ID set mismatch: a-only={a_ids - c_ids}, c-only={c_ids - a_ids}"

    rows = []
    for sid in sorted(a_rows, key=lambda s: (a_rows[s]["review_family"], s)):
        a, c = a_rows[sid], c_rows[sid]
        status, category = classify(a, c)
        rows.append({
            "issue_id": sid,
            "review_family": a["review_family"],
            "rule_id": a["rule_id"],
            "tier": a["tier"],
            "repository": a["repository"],
            "commit_sha": a["commit_sha"],
            "path": a["path"],
            "line": a["line"],
            "severity": a["severity"],
            "message": a["message"],
            "original_code_or_issue": a.get("source_context", ""),
            "reviewer_a_label_semantic": a["ai_semantic_label"],
            "reviewer_a_label_actionability": a["ai_actionability_label"],
            "reviewer_a_reason_code": a["ai_reason_code"],
            "reviewer_c_label_semantic": c["ai_semantic_label"],
            "reviewer_c_label_actionability": c["ai_actionability_label"],
            "reviewer_c_reason_code": c["ai_reason_code"],
            "reviewer_a_explanation": a["ai_notes"],
            "reviewer_c_explanation": c["ai_notes"],
            "reviewer_a_confidence": a["ai_confidence"],
            "reviewer_c_confidence": c["ai_confidence"],
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

    from collections import Counter
    status_counts = Counter(r["agreement_status"] for r in rows)
    print("status counts:", dict(status_counts))


if __name__ == "__main__":
    main()
