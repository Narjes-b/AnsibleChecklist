import numpy as np

from scripts import v007_sampling_simulation as sim


def test_wilson_known_values():
    low, high = sim.wilson(0, 10)
    assert low == 0.0 and 0.25 < high < 0.31
    low, high = sim.wilson(10, 10)
    assert abs(high - 1.0) < 1e-9 and 0.69 < low < 0.75
    assert sim.wilson(0, 0) == (0.0, 1.0)


def test_plan_tiers_census_and_cap_relaxation():
    assert sim.plan_for(np.array([1, 2, 3]))["census"] is True            # 6 <= 30
    mid = sim.plan_for(np.array([40, 30, 20, 10, 5, 5, 5, 5]))              # 120 occurrences
    assert mid["tier"] == "mid" and mid["target"] == 30 and mid["cap"] >= 2
    large = sim.plan_for(np.full(10, 100))                                  # 1000 occurrences
    assert large["tier"] == "large" and large["target"] == 40 and large["cap"] == 4
    # few repositories force the cap up so the target is reachable
    # 300 occurrences = mid tier, target 30: min(200,c) + min(100,c) >= 30 first holds at c = 15
    assert sim.plan_for(np.array([200, 100]))["cap"] == 15


def test_hajek_weights_repositories_by_size():
    # repository A: 90 occurrences, 100 % correct in the sample; B: 10, 0 % correct
    cluster_y = np.array([90 * 1.0, 10 * 0.0])
    weights = np.array([90.0, 10.0])
    assert sim.hajek(cluster_y, weights) == 0.9           # the naive pooled mean would be 0.5


def test_effective_n_interval_never_narrower_than_labelled_items():
    narrow = sim.effective_n_wilson(0.9, 1e-9, 40)       # tiny variance cannot beat n = 40
    assert narrow == sim.wilson(0.9 * 40, 40)
    wide = sim.effective_n_wilson(0.9, 0.02, 40)         # large variance widens it
    assert wide[1] - wide[0] > narrow[1] - narrow[0]
    assert sim.effective_n_wilson(1.0, 0.0, 40) == sim.wilson(40, 40)
