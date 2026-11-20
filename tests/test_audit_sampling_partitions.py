import pytest

from scripts.audit_sampling_partitions import audit_partitions


def frame_inputs():
    splits = {project: {"repository": project, "commit_sha": "sha", "split": partition,
                        "size_quartile": quartile}
              for project, partition, quartile in [
                  ("o/cal", "calibration", "1"), ("o/held", "heldout", "4")
              ]}
    statuses = {project: {"repository": project, "commit_sha": "sha",
                          "ansibleguard_status": "missing" if project == "o/failed" else "completed",
                          "overall_status": state}
                for project, state in [("o/cal", "complete"), ("o/held", "partial"), ("o/failed", "failed")]}
    rules = {"ansibleguard/unguarded-variable": {"family": "variable_reference_reasoning", "taxonomy": "RISK"}}

    def occurrence(project, key, policy, certainty, resolution):
        return {"run_id": "run", "project": project, "commit_sha": "sha", "occurrence_id": key,
                "provider": "ansibleguard", "scan_mode": "source",
                "rule_id": "ansibleguard/unguarded-variable", "policy": policy, "certainty": certainty,
                "resolution_status": resolution, "resolution_scope": "repository"}

    rows = [
        occurrence("o/cal", "same-id", "required", "UNRESOLVED", "CANDIDATE_MISSING"),
        occurrence("o/held", "same-id", "optional", "UNCERTAIN", "EXTERNAL_INPUT_UNCERTAIN"),
    ]
    return rows, splits, statuses, {"o/held": 2}, rules


def test_frame_separates_decision_states_and_preserves_failed_repository():
    result = audit_partitions(*frame_inputs())
    repos = {row["repository"]: row for row in result["repository-frame.csv"]}
    assert repos["o/failed"]["core_complete"] is False
    assert repos["o/failed"]["occurrences"] == ""
    assert repos["o/failed"]["split"] == "not-assigned"
    assert repos["o/held"]["exposure_status"] == "listed-example-present"
    assert repos["o/cal"]["exposure_status"] == "not-in-listed-samples"
    assert all(row["eligible_for_performance_scoring"] is False for row in repos.values())
    cells = result["sampling-cells.csv"]
    assert {(row["split"], row["policy"], row["certainty"]) for row in cells} == {
        ("calibration", "required", "UNRESOLVED"), ("heldout", "optional", "UNCERTAIN")}
    assert sum(row["occurrences"] for row in cells) == 2
    assert sum(row["occurrences"] for row in result["partition-margins.csv"]) == 2


def test_no_exposure_in_supplied_files_does_not_certify_final_evaluation():
    rows, splits, statuses, _, rules = frame_inputs()
    result = audit_partitions(rows, splits, statuses, {}, rules)
    for row in result["repository-frame.csv"]:
        assert row["exposure_status"] == "not-in-listed-samples"
        assert row["eligible_for_performance_scoring"] is False


@pytest.mark.parametrize("error", ["duplicate", "revision", "failed", "mixed-runs", "review", "unknown-rule"])
def test_inconsistent_frames_are_rejected(error):
    rows, splits, statuses, exposures, rules = frame_inputs()
    if error == "duplicate":
        rows.append(dict(rows[0]))
    elif error == "revision":
        rows[0]["commit_sha"] = "another-sha"
    elif error == "failed":
        rows[0]["project"] = "o/failed"
    elif error == "mixed-runs":
        rows[0]["run_id"] = "another-run"
    elif error == "review":
        rows[0]["scan_mode"] = "review"
    elif error == "unknown-rule":
        rows[0]["rule_id"] = "ansibleguard/unknown"
    with pytest.raises(ValueError):
        audit_partitions(rows, splits, statuses, exposures, rules)
