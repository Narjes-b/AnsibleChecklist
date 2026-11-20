import pytest

from scripts.build_threshold_benchmark import (
    _candidate_rows,
    _band,
    _distribution_rows,
    _observation,
    _prediction,
    _review_sample,
)
from scripts.compare_threshold_reviewers import agreement
from scripts.build_threshold_agreement_pilots import _balanced_pilot
from scripts.score_threshold_candidates import _positive_prediction, score


def _large_task(project, value, line):
    return _observation(
        "large_task_loc", project, "abc", "Q1", "tasks/main.yml", "tasks",
        line, f"task-{line}", value,
    )


def test_candidate_sensitivity_is_monotonic_and_keeps_current_threshold():
    observations = [_large_task("a/repo", value, value) for value in range(1, 21)]
    candidates, candidate_map = _candidate_rows(observations)
    rows = [row for row in candidates if row["metric_id"] == "large_task_loc"]
    assert 15.0 in candidate_map["large_task_loc"]
    assert [int(row["predicted_positive_observations"]) for row in rows] == sorted(
        [int(row["predicted_positive_observations"]) for row in rows], reverse=True
    )


def test_lower_tail_candidates_stay_within_observed_support():
    observations = [
        _observation(
            "cohesion_playbook_score", "a/repo", "abc", "Q1", f"site-{index}.yml",
            "file", 1, f"site-{index}.yml", value,
        )
        for index, value in enumerate((0.5, 0.5, 0.5, 1.0), 1)
    ]
    _, candidate_map = _candidate_rows(observations)
    assert min(candidate_map["cohesion_playbook_score"]) == 0.4  # current cutoff
    assert all(value >= 0.4 for value in candidate_map["cohesion_playbook_score"])


def test_metric_bands_accept_duplicate_quartiles():
    assert _band(0, 0, 0, 0, 3) == "B1_low"
    assert _band(1, 0, 0, 0, 3) == "B4_high"
    assert _band(4, 0, 0, 0, 3) == "B5_current_positive_tail"


def test_lower_tail_metric_bands_put_current_predictions_first():
    assert _band(0.3, 0.5, 1, 1, 0.4, "<") == "B1_current_positive_lower_tail"
    assert _band(0.5, 0.5, 1, 1, 0.4, "<") == "B2_current_to_q1"


def test_missing_abstraction_applies_file_role_multiplier():
    row = _observation(
        "missing_abstraction_leaf_tasks", "a/repo", "abc", "Q1", "site.yml",
        "playbook", 1, "site.yml", 12, threshold_multiplier=1.5,
    )
    assert not _prediction(row, 10)
    assert _prediction(row, 7)


def test_expression_length_replays_its_score_modifier():
    row = _observation(
        "complex_expression_length_chars", "a/repo", "abc", "Q1", "tasks/main.yml",
        "tasks", 2, "condition", 120, base_score=4,
    )
    assert _prediction(row, 100)
    assert not _prediction(row, 150)


def test_undocumented_complex_replay_preserves_or_rule_and_comment_gate():
    row = _observation(
        "undocumented_complex_boolean_ops", "a/repo", "abc", "Q1", "tasks/main.yml",
        "tasks", 2, "condition", 2, boolean_ops=2, jinja_filters=4,
        nesting_depth=0, has_preceding_comment=False,
    )
    assert _prediction(row, 99)  # The unchanged filter branch still fires.
    documented = dict(row, has_preceding_comment="true")
    assert not _prediction(documented, 1)
    assert _positive_prediction(row, 99)
    assert not _positive_prediction(documented, 1)


def test_expression_length_scorer_replays_score_modifier():
    row = _observation(
        "complex_expression_length_chars", "a/repo", "abc", "Q1", "tasks/main.yml",
        "tasks", 2, "condition", 120, base_score=4,
    )
    assert _positive_prediction(row, 100)
    assert not _positive_prediction(row, 150)


def test_large_play_candidate_replays_complete_or_rule():
    row = _observation(
        "large_play_loc", "a/repo", "abc", "Q1", "site.yml", "playbook",
        1, "play", 10, play_loc=10, play_task_count=8, play_avg_task_size=2,
    )
    assert _prediction(row, 100)  # Task-count branch remains at its default.
    task_row = dict(row, metric_id="large_play_task_count", value="8")
    assert not _prediction(task_row, 20)


def test_high_coupling_candidate_replays_other_or_branch():
    row = _observation(
        "high_coupling_import_count", "a/repo", "abc", "Q1", "site.yml",
        "playbook", 1, "site.yml", 0, import_count=0, role_count=6,
    )
    assert _prediction(row, 99)


def test_naming_candidate_replays_task_and_parent_play_branches():
    row = _observation(
        "play_name_special_chars", "a/repo", "abc", "Q1", "site.yml",
        "task", 3, "task", 0, task_special_chars=4, play_special_chars=0,
    )
    assert _prediction(row, 99)


def test_identity_suffix_separates_repeated_names_at_one_reported_line():
    first = _observation(
        "undocumented_complex_boolean_ops", "a/repo", "abc", "Q1",
        "tasks/main.yml", "tasks", 3, "Repeated", 0, identity_suffix="task:1",
    )
    second = _observation(
        "undocumented_complex_boolean_ops", "a/repo", "abc", "Q1",
        "tasks/main.yml", "tasks", 3, "Repeated", 0, identity_suffix="task:2",
    )
    assert first["observation_id"] != second["observation_id"]


def test_lower_than_metric_prediction_is_preserved_by_scorer():
    sample = [{
        "metric_id": "cohesion_playbook_score", "value": "0", "comparator": "<",
        "sampling_weight": "1", "eligible": "true", "adjudicated_label": "positive",
    }]
    candidates = [{
        "metric_id": "cohesion_playbook_score", "candidate_sources": "current",
        "threshold": "0.4",
    }]
    result = score(sample, candidates)[0]
    assert result["tp"] == 1


def test_review_sample_draws_one_item_per_project_and_band():
    observations = [
        _large_task(project, value, index)
        for project in ("a/repo", "b/repo")
        for index, value in enumerate((1, 2, 5, 10, 20, 30), 1)
    ]
    distributions = _distribution_rows(observations)
    repositories = [
        {"project": "a/repo", "repository_path": "/does/not/exist"},
        {"project": "b/repo", "repository_path": "/does/not/exist"},
    ]
    sample = _review_sample(observations, distributions, repositories)
    strata = {(row["project"], row["metric_band"]) for row in sample}
    assert len(sample) == len(strata)
    assert {row["project"] for row in sample} == {"a/repo", "b/repo"}
    assert all(float(row["sampling_weight"]) >= 1 for row in sample)


def test_agreement_calculates_kappa_and_reports_missing_labels():
    empty = agreement([{"reviewer_1_label": "", "reviewer_2_label": ""}])
    assert empty["cohens_kappa"] is None
    assert empty["gwet_ac1"] is None
    result = agreement([
        {"reviewer_1_label": "positive", "reviewer_2_label": "positive"},
        {"reviewer_1_label": "positive", "reviewer_2_label": "negative"},
        {"reviewer_1_label": "negative", "reviewer_2_label": "negative"},
        {"reviewer_1_label": "negative", "reviewer_2_label": "negative"},
    ])
    assert result["raw_agreement"] == pytest.approx(0.75)
    assert result["cohens_kappa"] == pytest.approx(0.5)
    assert result["gwet_ac1"] is not None


def test_threshold_score_uses_sampling_weights():
    sample = [
        {"metric_id": "large_task_loc", "value": "20", "comparator": ">", "sampling_weight": "2", "adjudicated_label": "positive"},
        {"metric_id": "large_task_loc", "value": "18", "comparator": ">", "sampling_weight": "1", "adjudicated_label": "negative"},
        {"metric_id": "large_task_loc", "value": "5", "comparator": ">", "sampling_weight": "3", "adjudicated_label": "positive"},
    ]
    candidates = [{"metric_id": "large_task_loc", "candidate_sources": "current", "threshold": "15"}]
    result = score(sample, candidates)[0]
    assert result["tp"] == 2
    assert result["fp"] == 1
    assert result["fn"] == 3
    assert result["precision"] == pytest.approx(2 / 3)
    assert result["recall"] == pytest.approx(2 / 5)


def test_threshold_score_preserves_missing_abstraction_logic():
    sample = [
        {
            "metric_id": "missing_abstraction_leaf_tasks", "value": "12",
            "comparator": ">", "sampling_weight": "1", "eligible": "true",
            "threshold_multiplier": "1", "has_existing_abstraction": "true",
            "adjudicated_label": "negative",
        },
        {
            "metric_id": "missing_abstraction_leaf_tasks", "value": "12",
            "comparator": ">", "sampling_weight": "1", "eligible": "true",
            "threshold_multiplier": "1.5", "has_existing_abstraction": "false",
            "adjudicated_label": "positive",
        },
    ]
    candidates = [{
        "metric_id": "missing_abstraction_leaf_tasks",
        "candidate_sources": "current", "threshold": "10",
    }]
    result = score(sample, candidates)[0]
    assert result["tn"] == 1
    assert result["fn"] == 1
    assert result["tp"] == 0


def test_agreement_pilot_balances_available_metric_bands():
    rows = [
        {
            "observation_id": f"{band}-{index}",
            "metric_band": band,
            "project": f"owner/repo-{index}",
        }
        for band in ("B1_low", "B3_upper_middle", "B5_current_positive_tail")
        for index in range(10)
    ]
    pilot = _balanced_pilot(rows, "large_task_loc", 15)
    counts = {
        band: sum(row["metric_band"] == band for row in pilot)
        for band in {row["metric_band"] for row in pilot}
    }
    assert counts == {
        "B1_low": 5,
        "B3_upper_middle": 5,
        "B5_current_positive_tail": 5,
    }
