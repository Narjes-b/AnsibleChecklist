import pytest
from pathlib import Path


@pytest.fixture
def fixtures_dir():
    """Absolute path to tests/fixtures/ — every test asks for this instead
    of re-deriving Path(__file__).parent itself."""
    return Path(__file__).parent / "fixtures"
