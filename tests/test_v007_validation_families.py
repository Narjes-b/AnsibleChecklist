import csv
import json
from pathlib import Path

from scripts.v007_validation_families import (
    FAMILIES,
    _assign_family,
    build_family_mapping,
)


ROOT = Path(__file__).resolve().parents[1]


def test_family_assignment_keeps_review_panel_separate():
    family, _basis = _assign_family(
        "missing-release-note",
        "review-history",
        {"category": "documentation", "taxonomy": "MAINTAINABILITY_SIGNAL"},
    )
    assert family == "review_history"


def test_semantic_overrides_are_explicit_and_stable():
    cases = {
        "unguarded-variable": "variable_reference_reasoning",
        "role-readme-absent": "structure_reuse",
        "unsafe-file-write": "security",
        "unnecessary-abstraction": "structure_reuse",
        "missing-bool-filters": "variable_reference_reasoning",
    }
    for rule_key, expected in cases.items():
        family, basis = _assign_family(
            rule_key,
            "static",
            {"category": "misc", "taxonomy": "DEFECT"},
        )
        assert family == expected
        assert basis


def test_mapping_covers_matrix_and_all_seven_families_without_occurrence_inputs(tmp_path):
    # The mapping generator intentionally accepts only the matrix and catalog.
    output_dir = tmp_path / "validation"
    (output_dir / "mappings").mkdir(parents=True)
    matrix = ROOT / "study/validation-v007-human/mappings/source-rule-allocation-matrix.csv"
    (output_dir / "mappings/source-rule-allocation-matrix.csv").write_bytes(matrix.read_bytes())

    manifest = build_family_mapping(ROOT, output_dir)
    mapping_path = output_dir / "mappings/rule-family-map.csv"
    rows = list(csv.DictReader(mapping_path.open(newline="", encoding="utf-8")))
    assert len(rows) == 65
    assert len({row["rule_id"] for row in rows}) == 65
    assert {row["family_id"] for row in rows} == set(FAMILIES)
    assert sum(manifest["mapping"]["family_counts"].values()) == 65
    assert manifest["scope_note"].startswith("Rule-definition mapping only")

    saved_manifest = json.loads(
        (output_dir / "mappings/rule-family-map.manifest.json").read_text(encoding="utf-8")
    )
    assert saved_manifest["mapping"]["rows"] == 65
    assert saved_manifest["source_matrix"]["rows"] == 65
    assert saved_manifest["mapping"]["family_counts"] == {
        "maintainability_complexity": 12,
        "objective_correctness": 11,
        "review_history": 5,
        "security": 8,
        "structure_reuse": 8,
        "style_policy": 11,
        "variable_reference_reasoning": 10,
    }
