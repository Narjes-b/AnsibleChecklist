import ast
from pathlib import Path

from ansibleguard.compat import StrEnum


def test_package_parses_with_minimum_supported_python_grammar():
    """Reject syntax newer than the Python version promised by pyproject."""
    source_root = Path(__file__).parents[1] / "src" / "ansibleguard"

    for source_file in source_root.rglob("*.py"):
        ast.parse(
            source_file.read_text(encoding="utf-8"),
            filename=str(source_file),
            feature_version=(3, 10),
        )


def test_strenum_is_provided_by_the_python_310_compatibility_layer():
    class Example(StrEnum):
        VALUE = "value"

    assert isinstance(Example.VALUE, str)
    assert str(Example.VALUE) == "value"

    source_root = Path(__file__).parents[1] / "src" / "ansibleguard"
    direct_imports = [
        source_file
        for source_file in source_root.rglob("*.py")
        if source_file.name != "compat.py"
        and "from enum import StrEnum" in source_file.read_text(encoding="utf-8")
    ]
    assert direct_imports == []
