from scripts.calibrate_detectors import load_labels, score_labels


def test_versioned_calibration_labels_are_complete():
    labels = load_labels("calibration/labels-v1.csv")
    assert len(labels) == 8
    assert {row["expected"] for row in labels} == {"present", "absent"}


def test_scoring_reports_tp_fp_tn_fn():
    labels = [
        {"case_id": "1", "file": "a.yml", "rule_id": "r", "expected": "present", "rationale": ""},
        {"case_id": "2", "file": "b.yml", "rule_id": "r", "expected": "absent", "rationale": ""},
        {"case_id": "3", "file": "c.yml", "rule_id": "r", "expected": "present", "rationale": ""},
        {"case_id": "4", "file": "d.yml", "rule_id": "r", "expected": "absent", "rationale": ""},
    ]
    findings = [{"file": "a.yml", "rule_id": "r"}, {"file": "b.yml", "rule_id": "r"}]
    result = score_labels(labels, findings)
    assert result["combined"] == {
        "tp": 1, "fp": 1, "tn": 1, "fn": 1,
        "precision": 0.5, "recall": 0.5, "specificity": 0.5, "f1": 0.5,
    }


def test_f1_distinguishes_zero_from_undefined():
    from scripts.calibrate_detectors import _f1

    # Real precision/recall of 0.0 (defined, just bad) -> a real F1 of 0.0.
    assert _f1(0.0, 0.5) == 0.0
    assert _f1(0.5, 0.0) == 0.0
    assert _f1(0.0, 0.0) == 0.0
    # Undefined precision or recall (no denominator at all) -> undefined F1.
    assert _f1(None, 0.5) is None
    assert _f1(0.5, None) is None
    # Ordinary case.
    assert _f1(0.5, 0.5) == 0.5
