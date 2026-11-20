import csv
import itertools
import json

import pytest

from scripts.sample_partitioned_occurrences import (
    Design, build_strata, load_verified_strata, main, sample_strata, sha256, write_csv,
)


def population():
    repositories = {
        name: {"commit_sha": "sha", "split": split, "size_quartile": "1", "core_complete": "True"}
        for name, split in [("o/small", "calibration"), ("o/large", "calibration"), ("o/held", "heldout")]
    }
    rows = []
    for project, count in [("o/small", 2), ("o/large", 5), ("o/held", 3)]:
        for index in range(count):
            rows.append({
                "run_id": "run", "project": project, "commit_sha": "sha", "occurrence_id": f"id-{index}",
                "file": "tasks.yml", "line": str(index + 1), "rule_id": "ansibleguard/example",
                "provider": "ansibleguard", "scan_mode": "source", "policy": "required",
                "certainty": "CONFIRMED", "resolution_status": "DETECTOR_RESULT", "resolution_scope": "rule-static",
            })
    return rows, repositories


def make_strata(design=Design(1, 1, 0)):
    rows, repositories = population()
    return build_strata(rows, repositories, "run", "required", design)


def test_two_stage_probabilities_include_group_and_within_group_selection():
    strata = make_strata()
    seen = set()
    for seed in range(100):
        selected, _ = sample_strata(strata, str(seed), "required")
        assert len(selected) == 1
        row = selected[0]
        n = 2 if row["repository"] == "o/small" else 5
        assert row["stage1_probability"] == 1 / 2
        assert row["stage2_probability"] == 1 / n
        assert row["inclusion_probability"] == 1 / (2 * n)
        assert row["sampling_weight"] == 2 * n
        assert row["dataset_role"] == "calibration"
        assert row["eligible_for_performance_scoring"] is False
        assert row["retrieval_status"] == "pending"
        assert row["label_status"] == "not-started"
        seen.add((row["repository"], row["occurrence_id"]))
    # Every occurrence, including those after the first row in a repository,
    # appears in this fixed-seed regression set.
    assert len(seen) == 7


def test_exact_enumeration_recovers_population_total_with_product_weights():
    stratum = make_strata(Design(1, 2, 0))[0]
    expected_ht = 0.0
    true_total = 0
    for group, units in stratum.groups.items():
        values = [int(unit["occurrence_id"] in {"id-0", "id-2"}) for unit in units]
        true_total += sum(values)
        m, n = stratum.draw_size(group), len(units)
        choices = list(itertools.combinations(values, m))
        probability = stratum.selected_groups / len(stratum.groups) * m / n
        for choice in choices:
            expected_ht += (1 / len(stratum.groups)) * (1 / len(choices)) * sum(choice) / probability
    assert expected_ht == pytest.approx(true_total)


def test_seed_replay_is_invariant_to_input_order():
    rows, repositories = population()
    a = build_strata(rows, repositories, "run", "required", Design(1, 2, 0))
    b = build_strata(list(reversed(rows)), dict(reversed(list(repositories.items()))),
                     "run", "required", Design(1, 2, 0))
    assert sample_strata(a, "fixed", "required") == sample_strata(b, "fixed", "required")


def test_size_bins_use_their_own_stage_one_denominators():
    rows, repositories = population()
    repositories["o/large"]["size_quartile"] = "4"
    strata = build_strata(rows, repositories, "run", "required", Design(1, 1, 0))
    selected, plan = sample_strata(strata, "fixed", "required")
    assert len(selected) == len(plan) == 2
    assert {row["size_quartile"] for row in selected} == {"1", "4"}
    assert all(row["stage1_probability"] == 1 for row in selected)


def test_empty_instrument_cannot_produce_a_draw():
    rows, repositories = population()
    with pytest.raises(ValueError, match="empty calibration"):
        build_strata(rows, repositories, "run", "uncertainty", Design())


def test_small_cell_census_has_unit_weights_and_seed_independence():
    strata = make_strata(Design(1, 1, 7))
    selected, plan = sample_strata(strata, "first", "required")
    assert len(selected) == 7
    assert all(row["inclusion_probability"] == row["sampling_weight"] == 1 for row in selected)
    assert sample_strata(strata, "second", "required")[0] == selected
    assert plan[0]["census_cell"] is True


def test_explicit_group_enumerates_members_before_within_group_sampling():
    rows, repositories = population()
    groups = {"o/small": "related", "o/large": "related", "o/held": "held"}
    strata = build_strata(rows, repositories, "run", "required", Design(1, 2, 0), groups)
    selected, _ = sample_strata(strata, "fixed", "required")
    assert len(selected) == 2
    assert all(row["group_population"] == 7 and row["sampling_weight"] == 3.5 for row in selected)


def test_groups_cannot_cross_partitions():
    rows, repositories = population()
    with pytest.raises(ValueError, match="crosses dataset partitions"):
        build_strata(rows, repositories, "run", "required", Design(), {name: "shared" for name in repositories})


@pytest.mark.parametrize("design", [(0, 2, 30), (3, 0, 30), (3, 2, -1), (1.5, 2, 30)])
def test_invalid_design_is_rejected(design):
    with pytest.raises(ValueError):
        Design(*design)


def test_instruments_have_separate_populations():
    rows, repositories = population()
    uncertainty = {**rows[0], "occurrence_id": "unknown", "policy": "optional", "certainty": "UNCERTAIN"}
    policy = {**rows[0], "occurrence_id": "policy", "policy": "optional"}
    for instrument, expected in [("required", 7), ("uncertainty", 1), ("optional-policy", 1)]:
        strata = build_strata([*rows, uncertainty, policy], repositories, "run", instrument, Design())
        assert sum(stratum.population for stratum in strata) == expected


@pytest.mark.parametrize("fault", ["duplicate", "revision", "mixed-run"])
def test_stale_or_duplicate_occurrences_are_rejected(fault):
    rows, repositories = population()
    if fault == "duplicate":
        rows.append(dict(rows[0]))
    elif fault == "revision":
        rows[0]["commit_sha"] = "wrong"
    else:
        rows[0]["run_id"] = "another-run"
    with pytest.raises(ValueError):
        build_strata(rows, repositories, "run", "required", Design())


def verified_files(tmp_path):
    rows, repositories = population()
    frame = tmp_path / "frame"
    frame.mkdir()
    source = tmp_path / "all-internal-source-occurrences.csv"
    write_csv(source, rows)
    write_csv(frame / "repository-frame.csv", [{"repository": name, **row} for name, row in repositories.items()])
    for name in ("sampling-cells.csv", "partition-margins.csv", "rule-feasibility.csv"):
        (frame / name).write_text("metadata\n")
    manifest = {
        "schema_version": 1, "population_view": "canonical-provider-assigned internal static-source occurrences",
        "run_id": "run", "eligible_for_performance_scoring": False,
        "input_sha256": {str(source): sha256(source)},
        "output_sha256": {p.name: sha256(p) for p in frame.glob("*.csv")},
    }
    (frame / "frame-manifest.json").write_text(json.dumps(manifest))
    return frame, source


def test_cli_writes_private_ledger_and_refuses_to_overwrite(tmp_path):
    frame, source = verified_files(tmp_path)
    output = tmp_path / "draw"
    args = ["--frame-dir", str(frame), "--occurrences", str(source), "--instrument", "required",
            "--seed", "fixed", "--output-dir", str(output)]
    assert main(args) == 0
    manifest = json.loads((output / "selection-manifest.json").read_text())
    assert manifest["eligible_for_performance_scoring"] is False
    assert manifest["population_occurrences"] == manifest["selected_occurrences"] == 7
    selected = list(csv.DictReader((output / "selection-ledger.csv").open()))
    assert all(row["dataset_role"] == "calibration" for row in selected)
    assert "source_context" not in selected[0]
    with pytest.raises(SystemExit):
        main(args)


@pytest.mark.parametrize("tamper", ["source", "frame"])
def test_changed_inputs_fail_hash_verification(tmp_path, tamper):
    frame, source = verified_files(tmp_path)
    target = source if tamper == "source" else frame / "repository-frame.csv"
    target.write_text(target.read_text() + "\n")
    with pytest.raises(ValueError, match="hash"):
        load_verified_strata(frame, source, "required", Design())
