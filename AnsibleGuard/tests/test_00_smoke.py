def test_pytest_itself_works():
    """If this fails, something's wrong with discovery/config, not our code."""
    assert 1 + 1 == 2


def test_fixtures_dir_fixture_resolves(fixtures_dir):
    """Confirms conftest.py's fixture is being injected correctly."""
    assert fixtures_dir.name == "fixtures"
    assert fixtures_dir.parent.name == "tests"
