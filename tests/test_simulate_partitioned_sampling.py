import pytest

from scripts.sample_partitioned_occurrences import Design, build_strata
from scripts.simulate_partitioned_sampling import planted_population, simulate
from tests.test_sample_partitioned_occurrences import population


def strata(design):
    rows, repositories = population()
    return build_strata(rows, repositories, "run", "required", design)


def test_full_census_recovers_finite_truth_in_every_replication():
    result = simulate(strata(Design(1, 1, 7)), "size-negative-60", 10, "fixed")
    for row in result:
        assert row["bias"] == pytest.approx(0)
        assert row["rmse"] == pytest.approx(0)
        assert row["min_selected_occurrences"] == row["max_selected_occurrences"] == 7
        assert row["confidence_interval_status"] == "not-evaluated"
        assert row["measured_tool_accuracy"] is False


def test_simulation_replays_and_does_not_mutate_population():
    frame = strata(Design(1, 1, 0))
    first = simulate(frame, "size-positive-60", 20, "fixed")
    assert simulate(frame, "size-positive-60", 20, "fixed") == first
    assert sum(stratum.population for stratum in frame) == 7


def test_all_positive_ratio_is_exact_but_ht_keeps_design_variability():
    result = {row["estimator"]: row for row in simulate(strata(Design(1, 1, 0)), "all-positive", 100, "fixed")}
    assert result["hajek-product-weights"]["mean_estimate"] == 1
    assert result["hajek-product-weights"]["rmse"] == 0
    assert result["stratified-hajek"]["mean_estimate"] == 1
    assert result["stratified-hajek"]["rmse"] == 0
    assert result["ht-known-population"]["outside_zero_one_fraction"] > 0


def test_planted_counts_are_finite_and_deterministic():
    frame = strata(Design())
    for _, sizes, positives in planted_population(frame, "heterogeneous-95", "fixed"):
        assert all(0 <= positive <= size for size, positive in zip(sizes, positives))


def test_single_replication_cannot_report_monte_carlo_error():
    with pytest.raises(ValueError, match="two replications"):
        simulate(strata(Design()), "constant-60", 1, "fixed")
