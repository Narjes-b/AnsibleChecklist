import itertools
import math

import pytest

from scripts.sample_partitioned_occurrences import Design, build_strata
from scripts.sampling_uncertainty import GroupCount, population_estimates, simulate_uncertainty, stratum_total
from scripts.simulate_partitioned_sampling import simulate
from tests.test_sample_partitioned_occurrences import population


@pytest.mark.parametrize("ratio", [0.0, 0.4, 1.0])
def test_exact_enumeration_recovers_total_and_unbiased_variance_with_both_sampling_stages(ratio):
    groups = [[0, 1], [1, 0, 1], [1, 1, 1, 0]]
    M, k, m = 3, 2, 2
    truth = sum(map(sum, groups)) - ratio * sum(map(len, groups))
    records = []
    for chosen in itertools.combinations(range(M), k):
        possibilities = [list(itertools.combinations(groups[index], m)) for index in chosen]
        probability = 1 / math.comb(M, k) / math.prod(map(len, possibilities))
        for within in itertools.product(*possibilities):
            observed = [GroupCount(str(index), len(groups[index]), m, sum(values)) for index, values in zip(chosen, within)]
            result = stratum_total(M, observed, residual_ratio=ratio)
            records.append((probability, result))
    assert sum(p for p, _ in records) == pytest.approx(1)
    assert sum(p * r["estimated_residual_total"] for p, r in records) == pytest.approx(truth)
    actual_variance = sum(p * (r["estimated_residual_total"] - truth) ** 2 for p, r in records)
    estimated_variance = sum(p * r["estimated_variance"] for p, r in records)
    assert actual_variance > 0
    assert estimated_variance == pytest.approx(actual_variance)


def test_census_has_exact_total_and_zero_variance_including_singletons():
    result = population_estimates([("census", 2, [GroupCount("a", 1, 1, 1), GroupCount("b", 3, 3, 1)])], 4)
    assert all(row["estimate"] == 0.5 and row["standard_error"] == 0 for row in result)
    assert all(row["complete_census"] and not row["zero_variance_non_census"] for row in result)


@pytest.mark.parametrize("M,groups,reason", [
    (2, [GroupCount("a", 4, 2, 1)], "between-group-singleton"),
    (1, [GroupCount("a", 4, 1, 1)], "within-group-singleton"),
])
def test_non_census_singletons_never_get_zero_variance(M, groups, reason):
    result = stratum_total(M, groups)
    assert result["estimated_variance"] is None and reason in result["variance_unavailable_reasons"]
    combined = population_estimates([("h", M, groups)], 8)
    assert all(row["standard_error"] is None and row["unavailable_strata"] == ["h"] for row in combined)


def test_zero_observed_variance_is_flagged_when_population_is_not_censused():
    result = population_estimates([("h", 2, [GroupCount("a", 20, 2, 2), GroupCount("b", 30, 2, 2)])], 50)
    assert all(row["estimate"] == 1 and row["standard_error"] == 0 for row in result)
    assert all(row["zero_variance_non_census"] and not row["complete_census"] for row in result)


@pytest.mark.parametrize("values", [(2, 3, 1), (2, 0, 0), (2, 2, 3), (2, 1, -1), (True, 1, 1), (2, 1, 0.5)])
def test_group_counts_require_complete_valid_binary_samples(values):
    with pytest.raises(ValueError, match="binary group sample"):
        GroupCount("g", *values)


def test_population_rejects_duplicate_strata_groups_and_wrong_census_size():
    group = GroupCount("g", 2, 2, 1)
    with pytest.raises(ValueError):
        stratum_total(2, [group, group])
    with pytest.raises(ValueError):
        population_estimates([("h", 1, [group]), ("h", 1, [group])], 4)
    with pytest.raises(ValueError, match="census does not reconcile"):
        population_estimates([("h", 1, [group])], 3)


def frame(design):
    rows, repositories = population()
    return build_strata(rows, repositories, "run", "required", design)


def test_variance_adapter_preserves_the_original_draws_and_point_estimates():
    strata = frame(Design(2, 2, 0))
    expected = {row["estimator"]: row for row in simulate(strata, "size-negative-60", 40, "fixed")}
    summaries, draws = simulate_uncertainty(strata, "size-negative-60", 40, "fixed")
    assert len(draws) == 80
    for row in summaries:
        for key in ("synthetic_population_fraction", "mean_estimate", "bias", "rmse", "mean_selected_occurrences"):
            assert row[key] == pytest.approx(expected[row["estimator"]][key])
        assert not row["candidate_interval_accepted"] and not row["measured_tool_accuracy"]


def test_census_simulation_intervals_cover_exact_truth_and_replay():
    strata = frame(Design(1, 1, 7))
    summaries, draws = simulate_uncertainty(strata, "constant-60", 10, "fixed")
    assert simulate_uncertainty(strata, "constant-60", 10, "fixed") == (summaries, draws)
    assert all(row["normal_95_coverage_all_draws"] == 1 and row["normal_95_mean_width"] == 0 for row in summaries)


def test_unavailable_variance_is_not_dropped_from_coverage_denominator():
    summaries, draws = simulate_uncertainty(frame(Design(1, 1, 0)), "constant-60", 10, "fixed")
    assert all(row["interval_available_fraction"] == row["normal_95_coverage_all_draws"] == 0 for row in summaries)
    assert len(draws) == 20 and all(row["standard_error"] is None for row in draws)
