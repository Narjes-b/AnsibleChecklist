from set_fact import set_fact


def test_unused_fact_detected(fixtures_dir):
    fixture = fixtures_dir / "set_fact_unused.yml"
    assert set_fact(str(fixture)) == 1


def test_used_fact_not_flagged(fixtures_dir):
    fixture = fixtures_dir / "set_fact_used.yml"
    assert set_fact(str(fixture)) == 0
