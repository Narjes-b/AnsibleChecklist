from scripts.build_stratified_sample import build_sample


def _row(identifier, project="repo", concept="hardcoded-secret", category="security"):
    return {
        "occurrence_id": identifier,
        "project": project,
        "concept_id": concept,
        "finding_category": category,
        "validation_unit": "occurrence",
    }


def test_stratified_sample_records_reproducibility_fields():
    sample = build_sample([_row("one"), _row("two", project="other")], seed=7)

    assert sample
    assert all(item["sampling_seed"] == 7 for item in sample)
    assert all(float(item["inclusion_probability"]) > 0 for item in sample)
    assert all(item["sampling_stratum"] == "concept:hardcoded-secret" for item in sample)


def test_stratified_sample_is_deterministic_for_seed():
    rows = [_row("one"), _row("two", project="other")]
    first = build_sample(rows, seed=9)
    second = build_sample(rows, seed=9)

    assert [item["occurrence_id"] for item in first] == [item["occurrence_id"] for item in second]
