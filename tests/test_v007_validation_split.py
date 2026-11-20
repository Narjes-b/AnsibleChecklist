from collections import Counter

from scripts.v007_validation_split import iterative_split, rank_quartiles


def test_split_is_deterministic_and_respects_exact_capacities():
    repositories = [f"org/repo-{index:03d}" for index in range(206)]
    tokens = {
        repository: {
            f"SIZE_Q{index % 4 + 1}",
            f"DENSITY_Q{(index * 3) % 4 + 1}",
            *( {"RULE_PRESENT_rule-a"} if index % 2 == 0 else set() ),
            *( {"RULE_PRESENT_rule-b"} if index % 5 == 0 else set() ),
        }
        for index, repository in enumerate(repositories)
    }
    first = iterative_split(tokens, "split-test-seed", heldout_capacity=62)
    second = iterative_split(tokens, "split-test-seed", heldout_capacity=62)
    assert first == second
    assert Counter(first.values()) == {"calibration": 144, "heldout": 62}
    assert set(first) == set(repositories)


def test_rank_quartiles_are_deterministic_and_cover_all_four_bins():
    values = {f"repo-{index}": float(index // 3) for index in range(20)}
    first = rank_quartiles(values, "quartile-test")
    second = rank_quartiles(values, "quartile-test")
    assert first == second
    assert set(first.values()) == {1, 2, 3, 4}
    assert max(Counter(first.values()).values()) - min(Counter(first.values()).values()) <= 1
