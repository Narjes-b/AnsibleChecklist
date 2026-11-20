from scripts.v007_agreement_v2 import family_report


def row(sem="positive", act="actionable", reason="confirmed-defect", bundle="none"):
    return {"semantic_label": sem, "actionability_label": act, "semantic_reason": reason, "bundle_issue": bundle}


def test_perfect_agreement_passes_all_gates():
    rows = [row("positive") if i % 2 else row("negative", "not-applicable", "out-of-scope") for i in range(20)]
    report = family_report(rows, [dict(r) for r in rows])
    assert report["decided_kappa"] == 1.0
    assert (report["gate_kappa"], report["gate_uncertain"], report["gate_bundle"]) == ("target", "pass", "pass")


def test_gates_fail_on_uncertainty_and_bundle_issues():
    a = [row("uncertain", "uncertain", "other") for _ in range(8)] + [row() for _ in range(12)]
    b = [row(bundle="truncated") for _ in range(8)] + [row() for _ in range(12)]
    report = family_report(a, b)
    assert report["gate_uncertain"] == "FAIL" and report["gate_bundle"] == "FAIL"


def test_disagreement_lowers_kappa():
    a = [row("positive") for _ in range(10)] + [row("negative", "not-applicable", "out-of-scope") for _ in range(10)]
    b = [row("negative", "not-applicable", "out-of-scope") for _ in range(10)] + [row("positive") for _ in range(10)]
    assert family_report(a, b)["gate_kappa"] == "FAIL"
