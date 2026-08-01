from datetime import datetime, timezone
import json

from scripts.discover_github_ansible import (
    _request_json,
    discover,
    enrich_pull_request_counts,
    repository_row,
)


AS_OF = datetime(2026, 8, 1, tzinfo=timezone.utc)


def repository(**overrides):
    item = {
        "full_name": "example/ansible-role-web",
        "html_url": "https://github.com/example/ansible-role-web",
        "clone_url": "https://github.com/example/ansible-role-web.git",
        "description": "Production Ansible role",
        "topics": ["ansible", "infrastructure-as-code"],
        "default_branch": "main",
        "created_at": "2020-01-01T00:00:00Z",
        "updated_at": "2026-07-01T00:00:00Z",
        "pushed_at": "2026-07-01T00:00:00Z",
        "archived": False,
        "disabled": False,
        "fork": False,
        "mirror_url": None,
        "private": False,
        "license": {"spdx_id": "MIT"},
        "stargazers_count": 150,
        "forks_count": 20,
        "size": 1000,
        "open_issues_count": 4,
    }
    item.update(overrides)
    return item


def test_repository_row_records_context_without_auto_selection():
    row = repository_row(repository(), "topic:ansible", AS_OF.isoformat(), AS_OF)
    assert row["source_host"] == "github"
    assert row["license_spdx"] == "MIT"
    assert row["star_band"] == "100-999"
    assert row["preclone_eligible"] == "true"
    assert row["collect_for_screening"] == "false"
    assert row["selected"] == "false"
    assert row["selection_as_of_utc"] == AS_OF.isoformat()


def test_preclone_gates_explain_every_rejection():
    row = repository_row(
        repository(
            archived=True,
            fork=True,
            mirror_url="https://example.invalid/mirror.git",
            license=None,
            pushed_at="2020-01-01T00:00:00Z",
        ),
        "query",
        AS_OF.isoformat(),
        AS_OF,
    )
    reasons = set(row["preclone_reasons"].split(";"))
    assert {"archived", "fork", "mirror", "license-needs-review", "stale"} <= reasons
    assert row["preclone_eligible"] == "false"


def test_discovery_deduplicates_queries_and_preserves_reasons(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "scripts.discover_github_ansible._request_json",
        lambda *args, **kwargs: {"items": [repository()]},
    )
    rows = discover(
        ("topic:ansible", "ansible in:readme"),
        cache_dir=tmp_path,
        pages=1,
        as_of=AS_OF,
    )
    assert len(rows) == 1
    assert set(rows[0]["discovery_query"].split(";")) == {
        "topic:ansible",
        "ansible in:readme",
    }


def test_pr_enrichment_uses_bounded_candidate_population(monkeypatch, tmp_path):
    rows = [
        repository_row(repository(full_name=f"example/role-{index}"), "q", AS_OF.isoformat(), AS_OF)
        for index in range(2)
    ]
    calls = []

    def fake_count(project, qualifier, **kwargs):
        calls.append((project, qualifier))
        return 7

    monkeypatch.setattr(
        "scripts.discover_github_ansible._search_count", fake_count
    )
    enrich_pull_request_counts(rows, cache_dir=tmp_path, limit=1, as_of=AS_OF)
    assert rows[0]["total_prs"] == 7
    assert rows[0]["merged_prs_last_24_months"] == 7
    assert rows[1]["total_prs"] == ""
    assert len(calls) == 4


def test_pr_enrichment_can_target_an_explicit_shortlist(monkeypatch, tmp_path):
    rows = [
        repository_row(
            repository(full_name=f"example/role-{index}"),
            "q",
            AS_OF.isoformat(),
            AS_OF,
        )
        for index in range(3)
    ]
    monkeypatch.setattr(
        "scripts.discover_github_ansible._search_count",
        lambda project, qualifier, **kwargs: 3,
    )

    enrich_pull_request_counts(
        rows,
        cache_dir=tmp_path,
        projects=["example/role-2", "example/role-0"],
        as_of=AS_OF,
    )

    assert rows[0]["total_prs"] == 3
    assert rows[1]["total_prs"] == ""
    assert rows[2]["total_prs"] == 3


def test_offline_request_reads_cache_without_network(tmp_path, monkeypatch):
    cache = tmp_path / "response.json"
    cache.write_text(json.dumps({"items": [1]}), encoding="utf-8")
    monkeypatch.setattr(
        "scripts.discover_github_ansible.requests.get",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("network called")),
    )
    assert _request_json(
        "https://api.github.com/search/repositories",
        params={},
        cache_path=cache,
        offline=True,
    ) == {"items": [1]}


def test_online_request_reuses_cache_unless_refresh_is_requested(tmp_path, monkeypatch):
    cache = tmp_path / "response.json"
    cache.write_text(json.dumps({"items": [1]}), encoding="utf-8")
    monkeypatch.setattr(
        "scripts.discover_github_ansible.requests.get",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("network called")),
    )
    assert _request_json(
        "https://api.github.com/search/repositories",
        params={},
        cache_path=cache,
    ) == {"items": [1]}
