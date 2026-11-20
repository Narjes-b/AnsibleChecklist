import math

import numpy as np

from scripts import study_reporting as charts
from scripts import v007_results_analysis as analysis
from scripts import v007_verification_plan as plan


def test_gini_bounds():
    assert analysis.gini([5, 5, 5, 5]) == 0.0
    assert analysis.gini([0, 0, 0, 100]) > 0.7
    assert analysis.gini([]) == 0.0


def test_spearman_handles_ties_and_direction():
    assert math.isclose(analysis.spearman([1, 2, 3, 4], [10, 20, 30, 40]), 1.0)
    assert math.isclose(analysis.spearman([1, 2, 3, 4], [4, 3, 2, 1]), -1.0)
    assert math.isnan(analysis.spearman([1, 1, 1], [1, 2, 3]))
    xs, ys = [1, 2, 2, 3, 4], [1, 3, 2, 5, 4]
    assert math.isclose(charts.spearman(xs, ys), analysis.spearman(xs, ys))


def test_tier_boundaries():
    assert analysis.tier(0) == "none"
    assert analysis.tier(30) == "census"
    assert analysis.tier(31) == "mid"
    assert analysis.tier(499) == "mid"
    assert analysis.tier(500) == "large"


def test_nice_ticks_cover_the_range_with_round_steps():
    ticks = charts.nice_ticks(8618)
    step = ticks[1] - ticks[0]
    assert ticks[0] == 0 and step in (1000, 2000, 5000)
    assert ticks[-1] <= 8618 < ticks[-1] + step          # last round value at or below the maximum
    assert all(b - a == step for a, b in zip(ticks, ticks[1:]))
    assert charts.nice_ticks(0) == [0.0]


def test_allocation_follows_the_mode():
    assert plan.allocation(plan.A, 1647)[0] == 10        # audit only
    assert plan.allocation(plan.A, 4)[0] == 4
    assert plan.allocation(plan.B, 3857)[0] == 30        # banded
    assert plan.allocation(plan.C, 1797)[0] == 40        # large semantic
    assert plan.allocation(plan.C, 269)[0] == 30         # mid semantic
    assert plan.allocation(plan.C, 24) == (24, "census")
    assert plan.allocation(plan.C, 0)[0] == 0


def test_every_mode_assignment_is_a_known_mode():
    assert {mode for mode, _ in plan.MODES.values()} == {plan.A, plan.B, plan.C}
    assert len(plan.MODES) == 60
