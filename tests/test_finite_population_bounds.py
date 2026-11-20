import itertools
import math
from statistics import variance

import pytest

from scripts.finite_population_bounds import apply_benchmark, between_group_bound, confidence_set, stratum_envelope, within_group_bound


@pytest.mark.parametrize("sizes", [(1, 2), (2, 3, 4), (1, 2, 4, 3, 5)])
def test_dynamic_bound_matches_exhaustive_vertex_maximum(sizes):
    actual = max(variance([n * flag for n, flag in zip(sizes, choices)])
                 for choices in itertools.product((0, 1), repeat=len(sizes)))
    bound, method = between_group_bound(sizes)
    assert method == "exact-vertex-dp" and bound == pytest.approx(actual)
    fallback, method = between_group_bound(sizes, max_dp_work=0)
    assert method == "analytic-upper-bound" and fallback >= actual - 1e-12


def test_large_frame_falls_back_instead_of_allocating_unbounded_dp_memory():
    bound, method = between_group_bound((10**9, 2, 3))
    assert method == "analytic-upper-bound" and math.isfinite(bound) and bound > 0


def test_within_bound_matches_worst_exact_binary_population():
    N, m, largest = 6, 2, 0
    for values in itertools.product((0, 1), repeat=N):
        draws = list(itertools.combinations(values, m))
        actual = sum((N / m * sum(draw) - sum(values)) ** 2 for draw in draws) / len(draws)
        largest = max(largest, actual)
        assert within_group_bound(N, m) >= actual - 1e-12
    assert within_group_bound(N, m) == pytest.approx(largest)
    assert within_group_bound(1, 1) == within_group_bound(6, 6) == 0


def test_envelope_dominates_exact_design_variance_for_every_toy_binary_population():
    sizes, M, k, m = (2, 3, 4), 3, 2, 2
    bound = stratum_envelope(sizes, k, (m, m, m))["total_variance_bound"]
    for labels in itertools.product((0, 1), repeat=sum(sizes)):
        groups = [labels[:2], labels[2:5], labels[5:]]
        true_total = sum(labels)
        actual_variance, coverage = 0.0, 0.0
        for chosen in itertools.combinations(range(M), k):
            choices = [list(itertools.combinations(groups[index], m)) for index in chosen]
            probability = 1 / math.comb(M, k) / math.prod(map(len, choices))
            for within in itertools.product(*choices):
                estimate_total = M / k * sum(sizes[index] / m * sum(values) for index, values in zip(chosen, within))
                actual_variance += probability * (estimate_total - true_total) ** 2
                interval = confidence_set(estimate_total / sum(sizes), sum(sizes), bound)
                coverage += probability * (interval["low"] <= true_total / sum(sizes) <= interval["high"])
        assert bound >= actual_variance - 1e-12
        assert coverage >= 0.95 - 1e-12


def test_complete_census_bound_is_zero_and_reconciles_with_exact_truth():
    bound = stratum_envelope((1, 3), 2, (1, 3))
    assert bound["total_variance_bound"] == 0
    interval = confidence_set(0.5, 4, 0)
    assert interval["low"] == interval["high"] == 0.5 and interval["width"] == 0


def test_empty_intersection_is_kept_as_a_miss_not_replaced_with_a_full_interval():
    interval = confidence_set(1.2, 100, 0.01)
    assert interval["empty_set"] and interval["width"] == 0


def test_benchmark_retains_every_ht_draw_and_does_not_apply_guarantee_to_ratio():
    draws = [{"scenario": "fixed", "replication": str(index), "estimator": estimator,
              "estimate": "0.5", "synthetic_population_fraction": "0.5"}
             for index in range(3) for estimator in ("ht-known-population", "hajek-product-weights")]
    summaries, records = apply_benchmark(draws, 100, 1, 0.05)
    assert len(records) == summaries[0]["replications"] == 3
    assert summaries[0]["coverage"] == 1 and not summaries[0]["final_method_accepted"]


@pytest.mark.parametrize("sizes", [(), (0, 1), (True, 2), (1.5, 2)])
def test_invalid_group_sizes_are_rejected(sizes):
    with pytest.raises(ValueError):
        between_group_bound(sizes)
