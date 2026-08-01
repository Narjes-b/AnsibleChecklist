import json

from ansibleguard.report.comparison import compare_occurrences, evaluate_policy


def occurrence(
    occurrence_id,
    *,
    concept="unsafe-file-permission",
    file="tasks/main.yml",
    line=1,
    severity="warning",
    fingerprints=(),
    semantic_key="semantic",
    native_rules=("ansibleguard/unsafe-file-permission",),
):
    return {
        "occurrence_id": occurrence_id,
        "concept_id": concept,
        "file": file,
        "line": line,
        "scan_mode": "source",
        "severity": severity,
        "evidence_fingerprints": list(fingerprints),
        "semantic_key": semantic_key,
        "native_rules": list(native_rules),
    }


def test_comparison_classifies_exact_moved_introduced_and_fixed():
    exact = occurrence("exact")
    moved_base = occurrence("old", line=3, fingerprints=("stable",))
    moved_head = occurrence("new", line=30, fingerprints=("stable",))
    fixed = occurrence("fixed", file="old.yml", semantic_key="fixed")
    introduced = occurrence("introduced", file="new.yml", semantic_key="introduced")

    result = compare_occurrences(
        [exact, moved_base, fixed], [exact.copy(), moved_head, introduced]
    )

    assert len(result["unchanged"]) == 1
    assert result["moved"][0]["match"] == "native-fingerprint"
    assert result["introduced"] == [introduced]
    assert result["fixed"] == [fixed]


def test_comparison_marks_single_detector_shape_match_as_uncertain():
    base = occurrence("base", semantic_key="old")
    head = occurrence("head", line=40, semantic_key="new")

    result = compare_occurrences([base], [head])

    assert result["uncertain"][0]["head"] == head
    assert result["introduced"] == []


def test_observe_and_ratchet_policy_are_deliberately_different():
    comparison = {
        "introduced": [
            occurrence("warning"),
            occurrence(
                "error",
                concept="role-variable-precedence-collision",
                severity="error",
            ),
            occurrence(
                "secret",
                concept="hardcoded-secret",
                severity="error",
            ),
        ],
        "unchanged": [],
        "fixed": [],
        "moved": [],
        "uncertain": [],
    }

    observe = evaluate_policy(comparison, "observe")
    ratchet = evaluate_policy(comparison, "ratchet")

    assert observe["blocking_occurrence_ids"] == ["secret"]
    assert ratchet["blocking_occurrence_ids"] == ["error", "secret"]


def test_changed_secret_is_never_downgraded_to_uncertain():
    base = occurrence(
        "old-secret",
        concept="hardcoded-secret",
        severity="error",
        semantic_key="old",
        fingerprints=("old",),
    )
    head = occurrence(
        "new-secret",
        concept="hardcoded-secret",
        severity="error",
        semantic_key="new",
        fingerprints=("new",),
    )
    comparison = compare_occurrences([base], [head])
    assert comparison["introduced"] == [head]
    assert evaluate_policy(comparison, "observe")["conclusion"] == "failure"


def test_compare_script_writes_machine_readable_decision(tmp_path):
    from scripts.compare_pr_results import main

    base = tmp_path / "base.json"
    head = tmp_path / "head.json"
    output = tmp_path / "decision.json"
    base.write_text("[]", encoding="utf-8")
    head.write_text(
        json.dumps(
            [
                occurrence(
                    "secret",
                    concept="hardcoded-secret",
                    severity="error",
                )
            ]
        ),
        encoding="utf-8",
    )

    assert main([str(base), str(head), "-o", str(output)]) == 1
    assert json.loads(output.read_text(encoding="utf-8"))["policy"][
        "conclusion"
    ] == "failure"


def test_compare_script_accepts_v2_envelopes_and_enriches_head_summary(tmp_path):
    from scripts.compare_pr_results import main

    base = tmp_path / "base.json"
    head = tmp_path / "head.json"
    decision = tmp_path / "decision.json"
    head_output = tmp_path / "head-output"
    (head_output / "summary").mkdir(parents=True)
    columns = (
        "file,errors,warnings,notes,total,new_pr_findings,"
        "pr_comparison_status\n"
    )
    values = "tasks/main.yml,0,1,0,1,,not-compared\n"
    for path in (
        head_output / "summary.csv",
        head_output / "summary" / "summary.csv",
    ):
        path.write_text(columns + values, encoding="utf-8")
    (head_output / "summary" / "report.json").write_text(
        json.dumps(
            {
                "schema_version": 2,
                "contract": "ansibleguard://schemas/output-v2.json",
                "kind": "run-report",
                "status": "completed",
                "profile": "pr",
                "counts": {},
                "artifacts": {},
                "pr_comparison": {"status": "not-compared"},
            }
        ),
        encoding="utf-8",
    )
    base.write_text(
        json.dumps(
            {
                "schema_version": 2,
                "kind": "canonical-occurrences",
                "items": [],
            }
        ),
        encoding="utf-8",
    )
    introduced = occurrence("new", file="tasks/main.yml", semantic_key="new")
    head.write_text(
        json.dumps(
            {
                "schema_version": 2,
                "kind": "canonical-occurrences",
                "items": [introduced],
            }
        ),
        encoding="utf-8",
    )

    assert (
        main(
            [
                str(base),
                str(head),
                "-o",
                str(decision),
                "--head-output",
                str(head_output),
            ]
        )
        == 0
    )
    payload = json.loads(decision.read_text())
    assert payload["schema_version"] == 2
    assert payload["kind"] == "pr-comparison"
    summary = (head_output / "summary/summary.csv").read_text()
    assert "tasks/main.yml,0,1,0,1,1,compared" in summary
    report = json.loads((head_output / "summary/report.json").read_text())
    assert report["pr_comparison"]["introduced"] == 1
