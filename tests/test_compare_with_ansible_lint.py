import csv
import json

import pytest

from scripts import compare_with_ansible_lint as comparison


AG_RULE = "ansibleguard/unnamed-task"
LINT_RULE = "ansible-lint/name[missing]"


def occurrence(project, occurrence_id, rules, *, run="run-1", sha="sha-1"):
    return {
        "run_id": run,
        "project": project,
        "commit_sha": sha,
        "occurrence_id": occurrence_id,
        "rule_id": rules[0],
        "native_rules": json.dumps(rules),
        "file": "tasks/main.yml",
        "line": "4",
    }


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run_comparison(tmp_path, internal, lint, *, partial=()):
    aggregate = tmp_path / "aggregate"
    aggregate.mkdir()
    projects = sorted({row["project"] for row in internal + lint})
    write_csv(aggregate / "repository-summary.csv", [
        {
            "project": project,
            "scan_status": "completed",
            "ansible_lint_status": "partial" if project in partial else "completed",
            "gitleaks_status": "completed",
        }
        for project in projects
    ])
    for name, rows in (
        ("all-internal-source-occurrences.csv", internal),
        ("all-ansible-lint-occurrences.csv", lint),
    ):
        if rows:
            write_csv(aggregate / name, rows)
        else:
            (aggregate / name).write_text(
                "run_id,project,commit_sha,occurrence_id,rule_id,native_rules,file,line\n",
                encoding="utf-8",
            )
    output = tmp_path / "pairs.csv"
    assert comparison.main(["--aggregate", str(aggregate), "--output", str(output)]) == 0
    rows = list(csv.DictReader(output.open(encoding="utf-8")))
    row = next(row for row in rows if row["ansibleguard_rule"] == "unnamed-task")
    counts = {key: int(value) for key, value in row.items() if key.endswith(
        ("_total", "_only", "_ansibleguard")
    ) or key == "both"}
    assert counts["ansibleguard_total"] == counts["both"] + counts["ansibleguard_only"]
    assert counts["ansible_lint_total"] == counts["both"] + counts["ansible_lint_only"]
    return counts


def test_shared_ids_in_different_repositories_count_as_distinct_matches(tmp_path):
    internal = [occurrence(project, "same-id", [AG_RULE, LINT_RULE])
                for project in ("owner/first", "owner/second")]
    counts = run_comparison(tmp_path, internal, [])
    assert counts == {
        "ansibleguard_total": 2, "ansible_lint_total": 2,
        "both": 2, "both_merged_by_ansibleguard": 2,
        "ansibleguard_only": 0, "ansible_lint_only": 0,
    }


def test_shared_id_does_not_overwrite_another_repositorys_native_rules(tmp_path):
    internal = [
        occurrence("owner/first", "same-id", [AG_RULE, LINT_RULE]),
        occurrence("owner/second", "same-id", [AG_RULE]),
    ]
    counts = run_comparison(tmp_path, internal, [])
    assert counts["both_merged_by_ansibleguard"] == 1
    assert counts["ansibleguard_only"] == 1


def test_location_match_cannot_reuse_one_lint_occurrence(tmp_path):
    internal = [occurrence("owner/repo", key, [AG_RULE]) for key in ("ag-1", "ag-2")]
    lint = [occurrence("owner/repo", "lint-1", [LINT_RULE])]
    counts = run_comparison(tmp_path, internal, lint)
    assert counts["both"] == 1
    assert counts["ansibleguard_only"] == 1
    assert counts["ansible_lint_only"] == 0


def test_canonical_matches_are_reserved_before_location_matching(tmp_path):
    internal = [
        occurrence("owner/repo", "a-location-candidate", [AG_RULE]),
        occurrence("owner/repo", "z-shared", [AG_RULE, LINT_RULE]),
    ]
    counts = run_comparison(tmp_path, internal, [])
    assert counts["both"] == counts["both_merged_by_ansibleguard"] == 1
    assert counts["ansibleguard_only"] == 1


@pytest.mark.parametrize("other_snapshot", [{"run": "run-2"}, {"sha": "sha-2"}])
def test_location_matching_respects_run_and_revision(tmp_path, other_snapshot):
    internal = [occurrence("owner/repo", "ag-1", [AG_RULE])]
    lint = [occurrence("owner/repo", "lint-1", [LINT_RULE], **other_snapshot)]
    counts = run_comparison(tmp_path, internal, lint)
    assert counts["both"] == 0
    assert counts["ansibleguard_only"] == counts["ansible_lint_only"] == 1


def test_duplicate_exports_of_one_canonical_occurrence_are_counted_once(tmp_path):
    row = occurrence("owner/repo", "shared", [AG_RULE, LINT_RULE])
    counts = run_comparison(tmp_path, [row, row], [row])
    assert counts["ansibleguard_total"] == counts["ansible_lint_total"] == 1
    assert counts["both"] == counts["both_merged_by_ansibleguard"] == 1


def test_partial_provider_repositories_are_excluded(tmp_path):
    internal = [occurrence(project, "same-id", [AG_RULE, LINT_RULE])
                for project in ("owner/complete", "owner/partial")]
    counts = run_comparison(tmp_path, internal, [], partial={"owner/partial"})
    assert counts["ansibleguard_total"] == counts["ansible_lint_total"] == 1


def test_conflicting_locations_for_one_snapshot_identity_are_rejected(tmp_path):
    row = occurrence("owner/repo", "same-id", [AG_RULE])
    conflict = {**row, "line": "99"}
    with pytest.raises(ValueError, match="conflicting locations"):
        run_comparison(tmp_path, [row, conflict], [])
