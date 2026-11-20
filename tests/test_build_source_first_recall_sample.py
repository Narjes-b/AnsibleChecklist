from scripts.build_source_first_recall_sample import build_recall_sample


def _row(project, path, eligible="true", cohort="true"):
    return {
        "project": project, "path": path,
        "eligible_for_clean_review": eligible,
        "primary_ansibleguard_cohort": cohort,
        "canonical_occurrences": "99",
    }


def test_source_first_recall_sample_filters_and_hides_findings():
    rows = [
        _row("a", "one.yml"), _row("a", "two.yml"), _row("b", "three.yml"),
        _row("c", "broken.yml", eligible="false"),
        _row("d", "external.yml", cohort="false"),
    ]
    sample = build_recall_sample(rows, seed=3, total=3, per_project_cap=1)

    assert len(sample) == 2
    assert {item["project"] for item in sample} == {"a", "b"}
    assert all("canonical_occurrences" not in item for item in sample)
    assert all(item["validation_unit"] == "source-first-recall" for item in sample)


def test_source_first_recall_sample_is_deterministic():
    rows = [_row("a", "one.yml"), _row("b", "two.yml")]
    assert build_recall_sample(rows, seed=9) == build_recall_sample(rows, seed=9)
