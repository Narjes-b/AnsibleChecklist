import json

import pytest

from ansibleguard.report.output_contract import CONTRACT_URI, SCHEMA_VERSION

from ansibleguard.report.comparison import compare_occurrences, evaluate_policy


def occurrence(
    occurrence_id,
    *,
    concept="insecure-permissions",
    file="tasks/main.yml",
    line=1,
    severity="warning",
    fingerprints=(),
    semantic_key="semantic",
    content_semantic_key=None,
    native_rules=("ansibleguard/insecure-permissions",),
    semantic_subject="task:configure service",
    task_fingerprint="normalized-task-body",
):
    return {
        "occurrence_id": occurrence_id,
        "concept_id": concept,
        "file": file,
        "line": line,
        "scan_mode": "source",
        "severity": severity,
        "message": "Finding needs review",
        "evidence_fingerprints": list(fingerprints),
        "semantic_key": semantic_key,
        "content_semantic_key": (
            content_semantic_key
            if content_semantic_key is not None
            else f"content:{semantic_key}"
        ),
        "native_rules": list(native_rules),
        "semantic_subject": semantic_subject,
        **(
            {"task_fingerprint": task_fingerprint}
            if task_fingerprint is not None else {}
        ),
        "provider_evidence_fingerprint": "provider-evidence",
        "detectors": [{"provider": "ansibleguard"}],
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
    assert result["introduced"][0]["occurrence_id"] == introduced["occurrence_id"]
    assert result["introduced"][0]["finding_category"] == "security"
    assert result["introduced"][0]["policy"] == "required"
    assert result["fixed"] == [fixed]


def test_comparison_marks_single_detector_shape_match_as_uncertain():
    base = occurrence("base", semantic_key="old")
    head = occurrence("head", line=40, semantic_key="new")

    result = compare_occurrences([base], [head])

    assert result["uncertain"][0]["head"] == head
    assert result["introduced"] == []


def test_line_move_matches_stable_semantic_key_without_native_fingerprint():
    base = occurrence("base", line=4, semantic_key="stable-task")
    head = occurrence("head", line=40, semantic_key="stable-task")

    result = compare_occurrences([base], [head])

    assert result["moved"][0]["match"] == "semantic"
    assert result["introduced"] == []


def test_unique_content_semantics_survive_file_rename():
    base = occurrence(
        "base", file="roles/apache/tasks/main.yml",
        semantic_key="old-path", content_semantic_key="same-task",
    )
    head = occurrence(
        "head", file="roles/httpd/tasks/main.yml",
        semantic_key="new-path", content_semantic_key="same-task",
    )

    result = compare_occurrences([base], [head])

    assert result["moved"][0]["match"] == "semantic-rename"
    assert result["introduced"] == []


def test_generic_location_findings_do_not_match_across_files():
    base = occurrence(
        "base",
        concept="long-yaml-line",
        file="old.yml",
        semantic_key="old-path",
        content_semantic_key="generic-content",
        semantic_subject="location",
    )
    head = occurrence(
        "head",
        concept="long-yaml-line",
        file="new.yml",
        semantic_key="new-path",
        content_semantic_key="generic-content",
        semantic_subject="location",
    )

    result = compare_occurrences([base], [head])

    assert result["moved"] == []
    assert result["fixed"] == [base]
    assert [item["occurrence_id"] for item in result["introduced"]] == ["head"]


def test_same_variable_without_structural_fingerprint_does_not_cross_match():
    base = occurrence(
        "base", concept="unguarded-variable", file="roles/a/tasks/main.yml",
        semantic_key="old", content_semantic_key="variable-port",
        semantic_subject="variable:port", task_fingerprint=None,
    )
    head = occurrence(
        "head", concept="unguarded-variable", file="roles/b/tasks/main.yml",
        semantic_key="new", content_semantic_key="variable-port",
        semantic_subject="variable:port", task_fingerprint=None,
    )

    result = compare_occurrences([base], [head])

    assert result["moved"] == []
    assert result["fixed"] == [base]
    assert [item["occurrence_id"] for item in result["introduced"]] == ["head"]


def test_git_rename_metadata_matches_unique_semantic_subject_after_refactor():
    base = occurrence(
        "base", file="roles/apache/tasks/main.yml",
        semantic_key="old-shape", content_semantic_key="old-content",
    )
    head = occurrence(
        "head", file="roles/httpd/tasks/main.yml",
        semantic_key="new-shape", content_semantic_key="new-content",
    )

    result = compare_occurrences(
        [base], [head],
        renamed_files={
            "roles/apache/tasks/main.yml": "roles/httpd/tasks/main.yml"
        },
    )

    assert result["moved"][0]["match"] == "git-rename-subject"
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
    assert ratchet["counts"]["introduced_actionable"] == 3
    assert ratchet["counts"]["introduced_optional"] == 0
    assert ratchet["introduced_by_category"]["security"] == 2
    assert ratchet["introduced_by_category"]["correctness"] == 1


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
    assert comparison["introduced"][0]["occurrence_id"] == head["occurrence_id"]
    assert comparison["introduced"][0]["finding_category"] == "security"
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


def test_compare_script_accepts_versioned_envelopes_and_enriches_head_summary(tmp_path):
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
                "schema_version": SCHEMA_VERSION,
                "contract": CONTRACT_URI,
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
                "schema_version": SCHEMA_VERSION,
                "contract": CONTRACT_URI,
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
                "schema_version": SCHEMA_VERSION,
                "contract": CONTRACT_URI,
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
    assert payload["schema_version"] == SCHEMA_VERSION
    assert payload["kind"] == "pr-comparison"
    summary = (head_output / "summary/summary.csv").read_text()
    assert "tasks/main.yml,0,1,0,1,1,compared" in summary
    report = json.loads((head_output / "summary/report.json").read_text())
    assert report["pr_comparison"]["introduced"] == 1


@pytest.mark.parametrize(
    "payload",
    (
        {
            "schema_version": 2,
            "contract": "ansibleguard://schemas/output-v2.json",
            "kind": "canonical-occurrences",
            "items": [],
        },
        {
            "schema_version": SCHEMA_VERSION,
            "contract": "ansibleguard://schemas/wrong.json",
            "kind": "canonical-occurrences",
            "items": [],
        },
        {
            "schema_version": SCHEMA_VERSION,
            "kind": "canonical-occurrences",
            "items": [],
        },
        {
            "schema_version": SCHEMA_VERSION,
            "contract": CONTRACT_URI,
            "kind": "canonical-occurrences",
            "items": [{"banana": 42}],
        },
    ),
)
def test_compare_script_rejects_invalid_versioned_occurrence_envelopes(
    tmp_path, payload
):
    from scripts.compare_pr_results import _load_occurrences

    path = tmp_path / "occurrences.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError):
        _load_occurrences(path)


def test_compare_script_accepts_valid_v3_and_explicit_legacy_list(tmp_path):
    from scripts.compare_pr_results import _load_occurrences

    item = occurrence("valid", content_semantic_key="content")
    versioned = tmp_path / "versioned.json"
    legacy = tmp_path / "legacy.json"
    versioned.write_text(
        json.dumps({
            "schema_version": SCHEMA_VERSION,
            "contract": CONTRACT_URI,
            "kind": "canonical-occurrences",
            "items": [item],
        }),
        encoding="utf-8",
    )
    legacy.write_text(json.dumps([item]), encoding="utf-8")

    assert _load_occurrences(versioned) == [item]
    assert _load_occurrences(legacy) == [item]
