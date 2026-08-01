import ast
from pathlib import Path


def test_package_parses_with_minimum_supported_python_grammar():
    """Reject syntax newer than the Python version promised by pyproject."""
    source_root = Path(__file__).parents[1] / "src" / "ansibleguard"

    for source_file in source_root.rglob("*.py"):
        ast.parse(
            source_file.read_text(encoding="utf-8"),
            filename=str(source_file),
            feature_version=(3, 10),
        )
