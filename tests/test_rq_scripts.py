import csv
import json
import math

import pytest

from scripts import rq1_precision as rq1
from scripts import rq2_cooccurrence as rq2


def test_kappa_and_ac1_perfect_and_chance():
    perfect = [("positive", "positive"), ("negative", "negative")] * 5
    assert rq1.cohen_kappa(perfect) == 1
    assert rq1.gwet_ac1(perfect, rq1.SEMANTIC) == 1
    # Reviewer B always says "positive": agreement equals chance, kappa 0.
    chance = [("positive", "positive"), ("negative", "positive")] * 5
    assert abs(rq1.cohen_kappa(chance)) < 1e-12


def test_wilson_interval_contains_estimate():
    low, high = rq1.wilson(8, 10)
    assert 0 < low < 0.8 < high < 1
    assert all(math.isnan(v) for v in rq1.wilson(0, 0))


def test_precision_row_counts_and_bounds():
    items = [{"final_semantic": label, "repository": repo} for label, repo in
             [("positive", "a"), ("positive", "b"), ("negative", "a"), ("uncertain", "c"), ("unreviewable", "c")]]
    row = rq1.precision_row("x", items)
    assert (row["positive"], row["negative"], row["uncertain"], row["unreviewable"]) == (2, 1, 1, 1)
    assert row["precision"] == 2 / 3
    assert row["bound_uncertain_as_negative"] == 2 / 4
    assert row["bound_uncertain_as_positive"] == 3 / 4


def _labels(path):
    rows = [
        ("I-1", "positive", "positive", "advisory", "advisory"),
        ("I-2", "positive", "negative", "advisory", "not-applicable"),
        ("I-3", "negative", "negative", "not-applicable", "uncertain"),
    ]
    with path.open("w", newline="") as target:
        writer = csv.writer(target)
        writer.writerow(["issue_id", "review_family", "rule_id", "repository", "commit_sha", "path", "line_start",
                         "reviewer_a_label_semantic", "reviewer_b_label_semantic", "reviewer_a_label_actionability",
                         "reviewer_b_label_actionability", "reviewer_a_reason_code", "reviewer_b_reason_code",
                         "reviewer_a_explanation", "reviewer_b_explanation"])
        for issue, a, b, aa, ba in rows:
            writer.writerow([issue, "Security", "ansibleguard/r", "o/r", "sha", "f.yml", "1", a, b, aa, ba, "", "", "", ""])


def test_adjudication_sheet_is_kept_and_used(tmp_path):
    labels, master, out = tmp_path / "labels.csv", tmp_path / "master.csv", tmp_path / "out"
    _labels(labels)
    master.write_text("sample_id,occurrence_id\nI-1,x\nI-2,y\nI-3,z\n")
    args = ["--labels", str(labels), "--master", str(master), "--output-dir", str(out)]
    rq1.main(args)
    sheet = list(csv.DictReader((out / "adjudication-sheet.csv").open()))
    assert [(r["issue_id"], r["priority"]) for r in sheet] == [
        ("I-2", "required (semantic)"), ("I-3", "optional (actionability only)")]
    assert "provisional" in (out / "RQ1_RESULTS.md").read_text()

    sheet[0]["final_semantic_label"] = "negative"
    with (out / "adjudication-sheet.csv").open("w", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=list(sheet[0]))
        writer.writeheader()
        writer.writerows(sheet)
    rq1.main(args)
    kept = list(csv.DictReader((out / "adjudication-sheet.csv").open()))
    assert kept[0]["final_semantic_label"] == "negative"
    report = (out / "RQ1_RESULTS.md").read_text()
    assert "Adjudication status: complete" in report
    family = list(csv.DictReader((out / "precision-by-family-descriptive.csv").open()))
    assert family[0]["positive"] == "1" and family[0]["negative"] == "2"
    status = json.loads((out / "report-status.json").read_text())
    assert status["adjudication_complete"] is True
    assert status["eligible_for_performance_scoring"] is False
    assert "Population precision: not estimated" in report


@pytest.mark.parametrize("master,manifest,expected", [
    ([{"eligible_for_performance_scoring": "false"}], {}, "calibration-only"),
    ([{"is_pilot": "true"}], {"eligible_for_performance_scoring": True}, "calibration-only"),
    ([], {"eligible_for_performance_scoring": False}, "calibration-only"),
    ([], {}, "descriptive-only"),
    ([], {"eligible_for_performance_scoring": True}, "descriptive-only"),
])
def test_sample_eligibility_cannot_promote_descriptive_estimator(master, manifest, expected):
    scope = rq1.sample_scope(master, manifest)
    assert scope["evidence_scope"] == expected
    assert scope["eligible_for_performance_scoring"] is False
    assert scope["population_precision_status"] == "not-estimated"


def test_complete_pilot_labels_keep_manifest_exclusion(tmp_path):
    labels, master, out = tmp_path / "labels.csv", tmp_path / "pilot-master.csv", tmp_path / "out"
    _labels(labels)
    rows = list(csv.DictReader(labels.open()))
    for row in rows:
        row["reviewer_b_label_semantic"] = row["reviewer_a_label_semantic"]
    with labels.open("w", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    master.write_text("sample_id,occurrence_id\nI-1,x\nI-2,y\nI-3,z\n")
    (tmp_path / "pilot-manifest.json").write_text(json.dumps({"eligible_for_performance_scoring": False}))
    rq1.main(["--labels", str(labels), "--master", str(master), "--output-dir", str(out)])
    status = json.loads((out / "report-status.json").read_text())
    assert status["adjudication_complete"] is True
    assert status["evidence_scope"] == "calibration-only"
    assert status["eligible_for_performance_scoring"] is False
    table = list(csv.DictReader((out / "precision-by-family-calibration.csv").open()))
    assert table[0]["evidence_scope"] == "calibration-only"
    assert table[0]["eligible_for_performance_scoring"] == "False"
    assert not (out / "precision-by-family.csv").exists()


def test_chi2_phi_and_bh():
    chi2, p = rq2.chi2_2x2(10, 0, 0, 10)
    assert chi2 == 20 and p < 1e-4
    assert rq2.phi(10, 0, 0, 10) == 1
    assert rq2.benjamini_hochberg([0.01, 0.04, 0.03]) == [0.03, 0.04, 0.04]


def test_mantel_haenszel_removes_size_confounding():
    # Within each stratum the two rules are independent (OR = 1), but the
    # second stratum has far more of both, so the pooled table looks associated.
    small, large = (1, 9, 9, 81), (81, 9, 9, 1)
    odds, low, high, _ = rq2.mantel_haenszel([small, large])
    assert abs(odds - 1) < 1e-9 and low < 1 < high
    a, b, c, d = (x + y for x, y in zip(small, large))
    assert rq2.phi(a, b, c, d) > 0.5


def test_mantel_haenszel_nested_pair_is_infinite():
    odds, *_ = rq2.mantel_haenszel([(5, 0, 3, 10), (4, 0, 2, 20)])
    assert odds == float("inf")
    row = {"q_value": 0.001, "lift": 3.0, "mh_odds_ratio": odds, "cramers_v": 0.4}
    assert rq2.classify(row) == "nested"
