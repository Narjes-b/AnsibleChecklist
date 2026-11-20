from scripts.v007_validation_plan_v2 import C_CAP, items_for, tier


def test_zero_population_gets_no_items():
    assert items_for("C-semantic", 0, "security") == 0


def test_mode_a_and_b_caps():
    assert items_for("A-deterministic", 500, "style") == 8
    assert items_for("A-deterministic", 3, "style") == 3
    assert items_for("B-threshold", 500, "style") == 20


def test_mode_c_census_and_consequence_bonus():
    assert items_for("C-semantic", 14, "correctness") == 14
    assert items_for("C-semantic", 269, "correctness") == 40
    assert items_for("C-semantic", 127, "maintainability") == 30
    assert items_for("C-semantic", 1797, "security") == C_CAP


def test_tiers():
    assert tier("security") == 1 and tier("dependencies") == 2 and tier("style") == 3
