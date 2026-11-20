from datetime import datetime, timezone
import subprocess

import pytest

from scripts.enrich_ansible_prs import (
    _atomic_write_json,
    _eligible_rows,
    _git_changed_files,
    _graphql_changed_files,
    _project_evidence_path,
    _read_project_evidence,
    _read_project_progress,
    _write_project_evidence,
    enrich_rows,
    evaluate_project_prs,
    evaluate_project_prs_graphql,
    is_production_ansible_path,
)
from scripts.select_study_candidates import (
    apply_final_tie_breaker,
    build_attrition,
    build_sensitivity,
    evaluate_rows,
    merge_rows,
)
from scripts.prepare_manual_validation import (
    build_ledgers,
    build_repository_reviews,
    summarize_validation,
)


AS_OF = datetime(2026, 8, 1, tzinfo=timezone.utc)


def candidate(project="example/ansible", **overrides):
    row = {
        "project": project,
        "private": "false",
        "disabled": "false",
        "fork": "false",
        "archived": "false",
        "mirror_url": "",
        "pushed_at": "2026-07-01T00:00:00Z",
        "total_prs": "80",
        "merged_ansible_changing_prs": "60",
        "production_ansible_files": "12",
        "total_commits": "1500",
        "stars": "0",
    }
    row.update(overrides)
    return row


def test_primary_protocol_ignores_stars_and_keeps_every_candidate():
    rows = evaluate_rows(
        [candidate(stars="0"), candidate("example/old", pushed_at="2019-01-01T00:00:00Z")],
        AS_OF,
    )
    assert len(rows) == 2
    assert rows[0]["final_eligible"] == "true"
    assert rows[0]["stars_used_for_selection"] == "false"
    assert rows[0]["descriptive_evidence_used_for_selection"] == "false"
    assert rows[1]["final_eligible"] == "false"
    assert "last_commit_within_6_years" in rows[1]["all_exclusion_reasons"]


def test_descriptive_evidence_is_reported_but_does_not_become_a_gate():
    row = evaluate_rows([candidate(
        project_purpose_auto="example-or-training-candidate",
        source_host="github",
        discovery_query="topic:ansible fork:false archived:false",
    )], AS_OF)[0]
    assert row["final_eligible"] == "true"
    assert row["evidence_project_purpose_status"] == "recorded"
    assert row["descriptive_evidence_status"] == "partial"
    assert "ansible_history" in row["descriptive_evidence_missing"]
    assert row["evidence_discovery_coverage_status"] == "recorded"
    assert row["discovery_coverage_scope"] == "historical-prefiltered-github-search"


def test_missing_expensive_evidence_is_pending_not_rejected():
    row = candidate(total_commits="", merged_ansible_changing_prs="")
    evaluated = evaluate_rows([row], AS_OF)[0]
    assert evaluated["final_eligible"] == "not-evaluated"
    assert "at_least_1000_commits" in evaluated["pending_evaluations"]


def test_template_repository_is_gated_out():
    row = evaluate_rows([candidate(is_template="true")], AS_OF)[0]
    assert row["gate_not_template"] == "false"
    assert row["final_eligible"] == "false"
    assert "not_template" in row["all_exclusion_reasons"]


def test_generated_repository_is_gated_out():
    row = evaluate_rows([candidate(generated_repository_match="true")], AS_OF)[0]
    assert row["gate_not_generated"] == "false"
    assert row["final_eligible"] == "false"
    assert "not_generated" in row["all_exclusion_reasons"]


def test_rows_without_template_or_generated_signal_still_pass():
    # Legacy/non-GitHub rows carry neither field -- absence must not
    # regress final_eligible to not-evaluated for every pre-existing row.
    row = evaluate_rows([candidate()], AS_OF)[0]
    assert row["gate_not_template"] == "true"
    assert row["gate_not_generated"] == "true"
    assert row["final_eligible"] == "true"


def test_stars_are_a_pure_tie_breaker_and_never_affect_eligibility():
    rows = evaluate_rows(
        [
            candidate("example/low-stars", stars="5"),
            candidate("example/high-stars", stars="500"),
            candidate("example/ineligible", stars="9000", fork="true"),
        ],
        AS_OF,
    )
    apply_final_tie_breaker(rows)
    by_project = {row["project"]: row for row in rows}
    assert by_project["example/high-stars"]["final_eligible_rank"] == 1
    assert by_project["example/low-stars"]["final_eligible_rank"] == 2
    assert by_project["example/ineligible"]["final_eligible_rank"] == ""
    assert by_project["example/ineligible"]["final_eligible"] == "false"


def test_attrition_reports_cumulative_removed_percent():
    rows = evaluate_rows(
        [candidate(), candidate("example/fork", fork="true")],
        AS_OF,
    )
    report = build_attrition(rows)
    fork_stage = next(item for item in report if item["criterion"] == "not_fork")
    assert fork_stage["cumulative_removed_percent"] == 50.0


def test_attrition_reports_removed_pending_and_remaining_sequentially():
    rows = evaluate_rows(
        [candidate(), candidate("example/fork", fork="true"), candidate("example/pending", total_prs="")],
        AS_OF,
    )
    report = build_attrition(rows)
    fork_stage = next(item for item in report if item["criterion"] == "not_fork")
    assert fork_stage["removed"] == 1
    pr_stage = next(item for item in report if item["criterion"] == "more_than_50_total_prs")
    assert pr_stage["pending"] == 1
    assert pr_stage["remaining"] == 1


def test_sensitivity_marks_primary_values_and_changes_retention():
    rows = evaluate_rows([candidate(total_commits="750")], AS_OF)
    report = build_sensitivity(rows, AS_OF)
    commits = {item["value"]: item for item in report if item["criterion"] == "minimum_commits"}
    assert commits[500]["repositories_retained"] == 1
    assert commits[1000]["repositories_retained"] == 0
    assert commits[1000]["primary_value"] == "true"


def test_frozen_metrics_merge_without_losing_candidate_metadata():
    rows = merge_rows(
        [candidate(total_commits="")],
        [{"project": "example/ansible", "total_commits": "1234", "commit_sha": "abc"}],
    )
    assert rows[0]["stars"] == "0"
    assert rows[0]["total_commits"] == "1234"
    assert rows[0]["commit_sha"] == "abc"


def test_atomic_write_json_retries_transient_permission_error(tmp_path, monkeypatch):
    # Path.replace() can raise WinError 5 "Access is denied" when another
    # process (antivirus, indexing) briefly holds the target file open, even
    # though nothing here holds a lasting lock -- a single occurrence
    # previously aborted an entire checkpoint-heavy enrichment run.
    from pathlib import Path

    target = tmp_path / "checkpoint.json"
    calls = []
    real_replace = Path.replace

    def flaky_replace(self, other):
        calls.append(1)
        if len(calls) < 3:
            raise PermissionError("Access is denied")
        return real_replace(self, other)

    monkeypatch.setattr(Path, "replace", flaky_replace)
    monkeypatch.setattr("scripts.enrich_ansible_prs.time.sleep", lambda seconds: None)

    _atomic_write_json(target, {"ok": True})

    assert len(calls) == 3
    assert target.is_file()


def test_atomic_write_json_raises_after_exhausting_retries(tmp_path, monkeypatch):
    from pathlib import Path

    def always_denied(self, other):
        raise PermissionError("Access is denied")

    monkeypatch.setattr(Path, "replace", always_denied)
    monkeypatch.setattr("scripts.enrich_ansible_prs.time.sleep", lambda seconds: None)

    with pytest.raises(PermissionError):
        _atomic_write_json(tmp_path / "checkpoint.json", {"ok": True}, retries=3)


def test_ansible_pr_path_classification_excludes_ci_and_tests():
    assert is_production_ansible_path("roles/web/tasks/main.yml")
    assert is_production_ansible_path("playbooks/deploy.yaml")
    assert is_production_ansible_path("custom/site.yml", {"custom/site.yml"})
    assert not is_production_ansible_path(".github/workflows/ansible.yml")
    assert not is_production_ansible_path("roles/web/molecule/default/converge.yml")
    assert not is_production_ansible_path("README.md")


def test_pr_enrichment_requires_fifty_merged_ansible_changing_prs():
    rows = [candidate()]
    evidence = {
        "example/ansible": [
            {"qualifies": "true" if index < 50 else "false"}
            for index in range(70)
        ]
    }
    enrich_rows(rows, evidence)
    assert rows[0]["merged_ansible_changing_prs"] == "50"
    assert rows[0]["pass_merged_ansible_prs_ge_50"] == "true"


def test_threshold_progress_reports_lower_bound_not_exact_count():
    rows = [candidate()]
    progress = {
        "example/ansible": {
            "status": "threshold_reached",
            "requested_mode": "threshold",
            "merged_prs_examined": 70,
            "merged_prs_seen": 70,
            "merged_pr_total": 9000,
            "merged_pr_total_as_of": None,
            "pages_completed": 3,
            "as_of_utc": "2026-08-05T00:00:00+00:00",
            "evidence": [
                {"qualifies": "true", "paper_comparable_qualifies": "false"}
                for _ in range(50)
            ],
        }
    }

    enrich_rows(rows, progress)

    assert rows[0]["merged_ansible_changing_prs"] == "50"
    assert rows[0]["merged_ansible_pr_count_lower_bound"] == "50"
    assert rows[0]["merged_ansible_pr_count_is_exact"] == "false"
    assert rows[0]["pass_merged_ansible_prs_ge_50"] == "true"


def test_failed_progress_does_not_become_a_false_exclusion():
    rows = [candidate()]
    progress = {
        "example/ansible": {
            "status": "failed",
            "requested_mode": "threshold",
            "merged_prs_examined": 10,
            "merged_prs_seen": 10,
            "merged_pr_total": 100,
            "merged_pr_total_as_of": None,
            "pages_completed": 0,
            "as_of_utc": "2026-08-05T00:00:00+00:00",
            "evidence": [
                {"qualifies": "false", "paper_comparable_qualifies": "false"}
            ],
        }
    }

    enrich_rows(rows, progress)

    assert rows[0]["ansible_pr_scan_status"] == "failed"
    assert rows[0]["pass_merged_ansible_prs_ge_50"] == "not-evaluated"


def test_detailed_pr_enrichment_builds_real_eligible_shortlist():
    rows = [
        candidate("example/eligible", metadata_eligible="true"),
        candidate("example/few-prs", metadata_eligible="true", total_prs="50"),
        candidate("example/no-content", metadata_eligible="true", production_ansible_files="0"),
        candidate("example/metadata-failed", metadata_eligible="false"),
    ]

    eligible = _eligible_rows(rows)

    assert [row["project"] for row in eligible] == ["example/eligible"]


def test_project_pr_evidence_checkpoint_round_trip(tmp_path):
    row = {
        "project": "example/ansible",
        "commit_sha": "a" * 40,
    }
    evidence = [{"project": row["project"], "pr_number": 7, "qualifies": "true"}]
    checkpoint = _project_evidence_path(tmp_path, row)

    _write_project_evidence(checkpoint, row, evidence)

    assert checkpoint.is_file()
    assert _read_project_evidence(checkpoint) == evidence


def test_legacy_exact_checkpoint_is_filtered_at_study_cutoff(tmp_path):
    row = {"project": "example/ansible", "commit_sha": "e" * 40}
    evidence = [
        {
            "project": row["project"],
            "pr_number": 1,
            "merged_at": "2026-08-04T00:00:00Z",
            "qualifies": "true",
        },
        {
            "project": row["project"],
            "pr_number": 2,
            "merged_at": "2026-08-06T00:00:00Z",
            "qualifies": "true",
        },
    ]
    checkpoint = _project_evidence_path(tmp_path, row)
    _write_project_evidence(checkpoint, row, evidence)

    progress = _read_project_progress(
        checkpoint,
        row,
        as_of=datetime(2026, 8, 5, tzinfo=timezone.utc),
    )

    assert progress["status"] == "complete_exact"
    assert progress["merged_pr_total"] == 2
    assert progress["merged_pr_total_as_of"] == 1
    assert progress["legacy_prs_after_as_of_excluded"] == 1
    assert [item["pr_number"] for item in progress["evidence"]] == [1]


def _graphql_pr(number, path="roles/web/tasks/main.yml", cursor=None):
    return {
        "cursor": cursor or f"cursor-{number}",
        "node": {
            "number": number,
            "url": f"https://github.com/example/ansible/pull/{number}",
            "mergedAt": "2026-01-01T00:00:00Z",
            "baseRefOid": f"base-{number}",
            "headRefOid": f"head-{number}",
            "mergeCommit": {"oid": f"merge-{number}"},
            "files": {
                "totalCount": 1,
                "pageInfo": {"endCursor": "file", "hasNextPage": False},
                "nodes": [{"path": path, "changeType": "MODIFIED"}],
            },
        },
    }


def _graphql_payload(edges, *, total=3, has_next=False):
    return {
        "data": {
            "repository": {
                "pullRequests": {
                    "totalCount": total,
                    "pageInfo": {
                        "endCursor": edges[-1]["cursor"] if edges else None,
                        "hasNextPage": has_next,
                    },
                    "edges": edges,
                }
            },
            "rateLimit": {
                "cost": 2,
                "remaining": 4998,
                "resetAt": "2026-01-01T01:00:00Z",
            },
        }
    }


def test_graphql_threshold_checkpoint_stops_at_exact_edge_cursor(monkeypatch, tmp_path):
    row = {"project": "example/ansible", "commit_sha": "a" * 40}
    checkpoint = _project_evidence_path(tmp_path, row)
    payload = _graphql_payload(
        [_graphql_pr(3), _graphql_pr(2), _graphql_pr(1)],
        has_next=True,
    )
    monkeypatch.setattr(
        "scripts.enrich_ansible_prs._graphql_request",
        lambda *args, **kwargs: payload,
    )

    progress = evaluate_project_prs_graphql(
        row,
        checkpoint_path=checkpoint,
        cache_dir=tmp_path,
        threshold=2,
        mode="threshold",
    )

    assert progress["status"] == "threshold_reached"
    assert progress["cursor"] == "cursor-2"
    assert progress["merged_prs_examined"] == 2
    assert len(progress["evidence"]) == 2
    assert all(item["evidence_source"] == "graphql" for item in progress["evidence"])
    saved = _read_project_progress(checkpoint, row)
    assert saved["cursor"] == "cursor-2"
    assert saved["status"] == "threshold_reached"


def test_graphql_exact_mode_resumes_threshold_checkpoint(monkeypatch, tmp_path):
    row = {"project": "example/ansible", "commit_sha": "b" * 40}
    checkpoint = _project_evidence_path(tmp_path, row)
    first = _graphql_payload(
        [_graphql_pr(3), _graphql_pr(2), _graphql_pr(1)],
        has_next=True,
    )
    second = _graphql_payload([_graphql_pr(1)], has_next=False)

    monkeypatch.setattr(
        "scripts.enrich_ansible_prs._graphql_request",
        lambda *args, **kwargs: first,
    )
    evaluate_project_prs_graphql(
        row,
        checkpoint_path=checkpoint,
        cache_dir=tmp_path,
        threshold=2,
        mode="threshold",
    )

    def resume(variables, **kwargs):
        assert variables["cursor"] == "cursor-2"
        return second

    monkeypatch.setattr("scripts.enrich_ansible_prs._graphql_request", resume)
    progress = evaluate_project_prs_graphql(
        row,
        checkpoint_path=checkpoint,
        cache_dir=tmp_path,
        threshold=2,
        mode="exact",
    )

    assert progress["status"] == "complete_exact"
    assert progress["merged_prs_examined"] == 3
    assert [item["pr_number"] for item in progress["evidence"]] == [3, 2, 1]


def test_graphql_exhaustion_proves_repository_below_threshold(monkeypatch, tmp_path):
    row = {"project": "example/ansible", "commit_sha": "c" * 40}
    checkpoint = _project_evidence_path(tmp_path, row)
    payload = _graphql_payload(
        [_graphql_pr(1, path="README.md")], total=1, has_next=False
    )
    monkeypatch.setattr(
        "scripts.enrich_ansible_prs._graphql_request",
        lambda *args, **kwargs: payload,
    )

    progress = evaluate_project_prs_graphql(
        row,
        checkpoint_path=checkpoint,
        cache_dir=tmp_path,
        threshold=50,
    )

    assert progress["status"] == "exhausted_below_threshold"
    assert progress["merged_prs_examined"] == 1
    assert progress["evidence"][0]["qualifies"] == "false"


def test_graphql_as_of_skips_later_merges_without_losing_cursor(monkeypatch, tmp_path):
    row = {"project": "example/ansible", "commit_sha": "d" * 40}
    checkpoint = _project_evidence_path(tmp_path, row)
    later = _graphql_pr(2)
    later["node"]["mergedAt"] = "2026-08-06T00:00:00Z"
    earlier = _graphql_pr(1)
    earlier["node"]["mergedAt"] = "2026-08-04T00:00:00Z"
    payload = _graphql_payload([later, earlier], total=2, has_next=False)
    monkeypatch.setattr(
        "scripts.enrich_ansible_prs._graphql_request",
        lambda *args, **kwargs: payload,
    )

    progress = evaluate_project_prs_graphql(
        row,
        checkpoint_path=checkpoint,
        cache_dir=tmp_path,
        threshold=1,
        as_of=datetime(2026, 8, 5, tzinfo=timezone.utc),
    )

    assert progress["status"] == "threshold_reached"
    assert progress["merged_prs_seen"] == 2
    assert progress["merged_prs_examined"] == 1
    assert [item["pr_number"] for item in progress["evidence"]] == [1]
    assert progress["cursor"] == "cursor-1"


def test_local_git_diff_preserves_previous_path_for_rename(tmp_path):
    repository = tmp_path / "repository"
    repository.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repository, check=True)
    subprocess.run(
        ["git", "config", "user.email", "tests@example.invalid"],
        cwd=repository,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Tests"], cwd=repository, check=True
    )
    source = repository / "playbooks" / "site.yml"
    source.parent.mkdir()
    source.write_text("- hosts: all\n  tasks: []\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repository, check=True)
    subprocess.run(["git", "commit", "-qm", "base"], cwd=repository, check=True)
    base = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    destination = repository / "archive" / "site.yml"
    destination.parent.mkdir()
    subprocess.run(
        ["git", "mv", str(source), str(destination)], cwd=repository, check=True
    )
    subprocess.run(["git", "commit", "-qm", "rename"], cwd=repository, check=True)
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    files = _git_changed_files(repository, base, head, expected_count=1)

    assert files == [
        {
            "filename": "archive/site.yml",
            "previous_filename": "playbooks/site.yml",
            "status": "renamed",
        }
    ]


def test_graphql_oversized_file_list_uses_cached_rest_fallback(monkeypatch, tmp_path):
    node = _graphql_pr(7)["node"]
    node["files"] = {
        "totalCount": 101,
        "pageInfo": {"endCursor": "file-100", "hasNextPage": True},
        "nodes": [],
    }
    changed = {"filename": "playbooks/site.yml", "status": "modified"}
    monkeypatch.setattr(
        "scripts.enrich_ansible_prs._paged",
        lambda *args, **kwargs: iter([changed]),
    )

    files, source, complete = _graphql_changed_files(
        "example/ansible",
        node,
        repository=None,
        cache_dir=tmp_path,
        token="token",
        offline=False,
        refresh_cache=False,
    )

    assert files == [changed]
    assert source == "rest-files-fallback"
    assert complete is True


def test_pr_evidence_counts_renames_from_known_production_paths(monkeypatch, tmp_path):
    pull = {
        "number": 7,
        "merged_at": "2026-01-01T00:00:00Z",
        "merge_commit_sha": "merge",
        "head": {"sha": "head"},
        "base": {"sha": "base"},
    }
    changed = {
        "filename": "archive/site.yml",
        "previous_filename": "playbooks/site.yml",
        "status": "renamed",
    }

    def fake_paged(url, params, **kwargs):
        return iter([changed] if url.endswith("/pulls/7/files") else [pull])

    monkeypatch.setattr("scripts.enrich_ansible_prs._paged", fake_paged)
    evidence = evaluate_project_prs(
        "example/ansible", cache_dir=tmp_path,
        known_paths={"playbooks/site.yml"},
        paper_paths={"playbooks/site.yml"},
    )
    assert evidence[0]["qualifies"] == "true"
    assert evidence[0]["qualification_basis"] == "renamed-from-production-ansible-path"
    assert "playbooks/site.yml->archive/site.yml" in evidence[0]["renamed_or_previous_paths"]
    assert evidence[0]["primary_qualifies"] == "true"
    assert evidence[0]["paper_comparable_qualifies"] == "true"


def test_validation_ledger_includes_findings_and_clean_files(tmp_path):
    project = "example/ansible"
    sha = "a" * 40
    classifications = tmp_path / "classifications"
    classifications.mkdir()
    manifest = classifications / f"example__ansible__{sha}.csv"
    manifest.write_text(
        "path,file_class,document_type,loc,included\n"
        "playbooks/site.yml,production_ansible,playbook,20,true\n"
        "roles/web/tasks/main.yml,production_ansible,tasks,5,true\n",
        encoding="utf-8",
    )
    snapshot = tmp_path / "snapshots" / "example__ansible" / sha / "canonical"
    snapshot.mkdir(parents=True)
    (snapshot / "occurrences.json").write_text(
        '{"items":[{"occurrence_id":"one","concept_id":"missing-tags",'
        '"file":"playbooks/site.yml","line":4,"severity":"warning",'
        '"message":"missing"}]}',
        encoding="utf-8",
    )
    inventory, labels = build_ledgers(
        [{"project": project, "commit_sha": sha, "status": "collected"}],
        classifications,
        tmp_path / "snapshots",
    )
    assert len(inventory) == 2
    assert {row["validation_unit"] for row in labels} == {
        "occurrence", "clean-file-review"
    }
    assert all(row["project_size_quartile"].startswith("Q") for row in labels)


def test_validation_ledger_populates_analysis_status_fields(tmp_path):
    """inventory rows carry analysis_status, analysis_diagnostic, eligible_for_clean_review."""
    project = "example/ansible"
    sha = "b" * 40
    classifications = tmp_path / "classifications"
    classifications.mkdir()
    manifest = classifications / f"example__ansible__{sha}.csv"
    manifest.write_text(
        "path,file_class,document_type,loc,included\n"
        "tasks/main.yml,production_ansible,tasks,10,true\n",
        encoding="utf-8",
    )
    snapshot_root = tmp_path / "snapshots" / "example__ansible" / sha
    (snapshot_root / "canonical").mkdir(parents=True)
    (snapshot_root / "canonical" / "occurrences.json").write_text("[]", encoding="utf-8")
    inventory, labels = build_ledgers(
        [{"project": project, "commit_sha": sha, "status": "collected"}],
        classifications,
        tmp_path / "snapshots",
    )
    row = inventory[0]
    assert row["eligible_for_clean_review"] == "true"
    assert row["clean_for_manual_review"] == "true"
    assert row["analysis_status"] == "analyzed"
    assert row["analysis_diagnostic"] == ""
    assert any(label["validation_unit"] == "clean-file-review" for label in labels)


def test_validation_ledger_excludes_failed_files_from_clean_review(tmp_path):
    """Files with parse_status=invalid are not eligible as clean negative units."""
    project = "example/ansible"
    sha = "c" * 40
    classifications = tmp_path / "classifications"
    classifications.mkdir()
    manifest = classifications / f"example__ansible__{sha}.csv"
    manifest.write_text(
        "path,file_class,document_type,loc,included\n"
        "tasks/broken.yml,production_ansible,tasks,3,true\n"
        "tasks/clean.yml,production_ansible,tasks,5,true\n",
        encoding="utf-8",
    )
    snapshot_root = tmp_path / "snapshots" / "example__ansible" / sha
    (snapshot_root / "canonical").mkdir(parents=True)
    (snapshot_root / "canonical" / "occurrences.json").write_text("[]", encoding="utf-8")
    # Write per-file report for broken.yml marking it as failed.
    files_dir = snapshot_root / "files" / "tasks" / "broken.yml"
    files_dir.mkdir(parents=True)
    import json as _json
    (files_dir / "report.json").write_text(
        _json.dumps({"file": "tasks/broken.yml", "parse_status": "invalid", "status": "skipped"}),
        encoding="utf-8",
    )
    inventory, labels = build_ledgers(
        [{"project": project, "commit_sha": sha, "status": "collected"}],
        classifications,
        tmp_path / "snapshots",
    )
    by_path = {row["path"]: row for row in inventory}
    broken = by_path["tasks/broken.yml"]
    clean = by_path["tasks/clean.yml"]

    assert broken["eligible_for_clean_review"] == "false"
    assert broken["clean_for_manual_review"] == "false"
    assert broken["analysis_status"] == "invalid"
    assert broken["analysis_diagnostic"] == "invalid"

    assert clean["eligible_for_clean_review"] == "true"
    assert clean["clean_for_manual_review"] == "true"

    # No clean-file-review label row for the broken file, but one for the clean file.
    label_paths_by_unit = {}
    for label in labels:
        label_paths_by_unit.setdefault(label["validation_unit"], set()).add(label["path"])
    assert "tasks/broken.yml" not in label_paths_by_unit.get("clean-file-review", set())
    assert "tasks/clean.yml" in label_paths_by_unit.get("clean-file-review", set())


def test_repository_review_ledger_preserves_evidence_and_blank_independent_labels():
    reviews = build_repository_reviews(
        [{
            "project": "example/ansible", "commit_sha": "abc", "status": "collected",
            "project_purpose_auto": "ansible-role", "repository_owner": "example",
            "production_ansible_files": "12", "latest_ansible_commit_date_utc": "2026-01-01",
        }]
    )
    assert reviews[0]["project_purpose_auto"] == "ansible-role"
    assert reviews[0]["purpose_reviewer_1_category"] == ""
    assert reviews[0]["purpose_reviewer_2_category"] == ""
    assert reviews[0]["independence_consensus_status"] == ""


def test_manual_validation_summary_calculates_agreement_and_precision():
    rows = [
        {
            "validation_unit": "occurrence",
            "reviewer_1_label": "true-positive",
            "reviewer_2_label": "true-positive",
            "consensus_label": "true-positive",
        },
        {
            "validation_unit": "occurrence",
            "reviewer_1_label": "true-positive",
            "reviewer_2_label": "false-positive",
            "consensus_label": "false-positive",
        },
        {
            "validation_unit": "clean-file-review",
            "reviewer_1_label": "false-negative",
            "reviewer_2_label": "false-negative",
            "consensus_label": "false-negative",
        },
    ]
    summary = summarize_validation(rows)

    assert summary["independently_double_labeled"] == 3
    assert summary["initial_agreements"] == 2
    assert summary["occurrence_precision"] == 0.5
    assert summary["false_negative_clean_file_reviews"] == 1
    # Observed agreement 2/3; chance agreement 1/3 from each rater's own
    # marginal distribution over {true-positive, false-positive, false-negative}.
    assert summary["cohens_kappa"] == pytest.approx(0.5)


def test_manual_validation_kappa_is_none_without_double_labeled_rows():
    summary = summarize_validation([{
        "validation_unit": "occurrence",
        "reviewer_1_label": "",
        "reviewer_2_label": "",
        "consensus_label": "",
    }])

    assert summary["independently_double_labeled"] == 0
    assert summary["cohens_kappa"] is None


def test_manual_validation_kappa_is_none_when_only_one_category_used():
    # Both raters agree on every row using a single identical category --
    # chance agreement is 100%, so kappa is undefined (not "perfect 1.0").
    rows = [
        {
            "validation_unit": "occurrence",
            "reviewer_1_label": "true-positive",
            "reviewer_2_label": "true-positive",
            "consensus_label": "true-positive",
        }
        for _ in range(3)
    ]

    summary = summarize_validation(rows)

    assert summary["initial_percent_agreement"] == 1.0
    assert summary["cohens_kappa"] is None


def test_validation_ledger_rule_id_comes_from_native_rules_not_concept_id(tmp_path):
    """rule_id must be native_rules[0], not concept_id — critical for ansible-lint-issue rows."""
    import json as _json
    project = "example/ansible"
    sha = "d" * 40
    classifications = tmp_path / "classifications"
    classifications.mkdir()
    manifest = classifications / f"example__ansible__{sha}.csv"
    manifest.write_text(
        "path,file_class,document_type,loc,included\n"
        "tasks/main.yml,production_ansible,tasks,10,true\n",
        encoding="utf-8",
    )
    snapshot = tmp_path / "snapshots" / "example__ansible" / sha / "canonical"
    snapshot.mkdir(parents=True)
    (snapshot / "occurrences.json").write_text(
        _json.dumps({"items": [{
            "occurrence_id": "abc123",
            "concept_id": "ansible-lint-issue",
            "native_rules": ["ansible-lint/var-naming[read-only]"],
            "file": "tasks/main.yml",
            "line": 8,
            "severity": "warning",
            "message": "This special variable is read-only.",
            "canonical_provider": "ansible-lint",
        }]}),
        encoding="utf-8",
    )
    _, labels = build_ledgers(
        [{"project": project, "commit_sha": sha, "status": "collected"}],
        classifications,
        tmp_path / "snapshots",
    )
    occurrence_rows = [r for r in labels if r["validation_unit"] == "occurrence"]
    assert len(occurrence_rows) == 1
    row = occurrence_rows[0]
    assert row["rule_id"] == "ansible-lint/var-naming[read-only]", (
        f"rule_id should be native_rules[0], got {row['rule_id']!r}"
    )
    assert row["concept_id"] == "ansible-lint-issue"


def test_validation_ledger_rule_id_falls_back_gracefully_when_native_rules_empty(tmp_path):
    """When native_rules is absent or empty, rule_id should be empty string not an error."""
    import json as _json
    project = "example/ansible"
    sha = "e" * 40
    classifications = tmp_path / "classifications"
    classifications.mkdir()
    manifest = classifications / f"example__ansible__{sha}.csv"
    manifest.write_text(
        "path,file_class,document_type,loc,included\n"
        "tasks/main.yml,production_ansible,tasks,10,true\n",
        encoding="utf-8",
    )
    snapshot = tmp_path / "snapshots" / "example__ansible" / sha / "canonical"
    snapshot.mkdir(parents=True)
    (snapshot / "occurrences.json").write_text(
        _json.dumps({"items": [{
            "occurrence_id": "def456",
            "concept_id": "large-task",
            "native_rules": [],
            "file": "tasks/main.yml",
            "line": 1,
            "severity": "warning",
            "message": "Task is too large.",
            "canonical_provider": "ansibleguard",
        }]}),
        encoding="utf-8",
    )
    _, labels = build_ledgers(
        [{"project": project, "commit_sha": sha, "status": "collected"}],
        classifications,
        tmp_path / "snapshots",
    )
    occurrence_rows = [r for r in labels if r["validation_unit"] == "occurrence"]
    assert occurrence_rows[0]["rule_id"] == ""


def test_manual_validation_summary_rejects_invalid_or_one_sided_labels():
    import pytest

    with pytest.raises(ValueError, match="both independent"):
        summarize_validation([{
            "reviewer_1_label": "true-positive",
            "reviewer_2_label": "",
            "consensus_label": "",
        }])
