from datetime import datetime, timezone
import json

import pytest

from scripts.discover_github_ansible import (
    DEFAULT_QUERIES,
    _discover_complete_query,
    _request_json,
    discover,
    enrich_pull_request_counts,
    enrich_commit_counts,
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
    assert row["discovery_sources"] == "github"
    assert "github-topic-search" in row["discovery_methods"]
    assert row["discovery_coverage_warning"].startswith("not-all-ansible-repositories")
    assert row["collect_for_screening"] == "false"
    assert row["selected"] == "false"
    assert row["selection_as_of_utc"] == AS_OF.isoformat()
    assert row["selection_protocol_version"] == "2"
    assert row["stars"] == 150
    assert row["stars_used_for_selection"] == "false"
    assert all("fork:true" in query for query in DEFAULT_QUERIES)


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
    assert {"archived", "fork", "mirror", "last-commit-older-than-6-years"} <= reasons
    assert "license-needs-review" not in reasons
    assert row["preclone_eligible"] == "false"


def test_template_repository_is_excluded_with_reason():
    row = repository_row(repository(is_template=True), "query", AS_OF.isoformat(), AS_OF)
    assert "template" in row["preclone_reasons"].split(";")
    assert row["preclone_eligible"] == "false"
    assert row["pass_not_template"] == "false"
    assert row["is_template"] == "true"


def test_generated_repository_name_is_excluded_with_reason():
    row = repository_row(
        repository(full_name="example/ansible-role-generated"), "query", AS_OF.isoformat(), AS_OF,
    )
    assert "generated" in row["preclone_reasons"].split(";")
    assert row["preclone_eligible"] == "false"
    assert row["pass_not_generated"] == "false"
    assert row["generated_repository_match"] == "true"


def test_ordinary_repository_is_not_flagged_as_template_or_generated():
    row = repository_row(repository(), "query", AS_OF.isoformat(), AS_OF)
    assert row["is_template"] == "false"
    assert row["generated_repository_match"] == "false"
    assert row["pass_not_template"] == "true"
    assert row["pass_not_generated"] == "true"


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
    rows[0]["pass_commits_ge_1000"] = "true"
    rows[1]["pass_commits_ge_1000"] = "true"
    calls = []

    def fake_count(project, qualifier, **kwargs):
        calls.append((project, qualifier))
        return 7

    monkeypatch.setattr(
        "scripts.discover_github_ansible._search_count", fake_count
    )
    enrich_pull_request_counts(rows, cache_dir=tmp_path, limit=1, as_of=AS_OF)
    assert rows[0]["total_prs"] == 7
    assert rows[0]["merged_prs_last_24_months"] == ""
    assert rows[1]["total_prs"] == ""
    assert len(calls) == 1


def test_pr_enrichment_skips_unsearchable_repository_and_continues(monkeypatch, tmp_path):
    # A repository renamed/transferred/removed between discovery and
    # enrichment time returns HTTP 422 from GitHub search -- this must not
    # abort enrichment for every project after it in the population.
    rows = [
        repository_row(repository(full_name=f"example/role-{index}"), "q", AS_OF.isoformat(), AS_OF)
        for index in range(2)
    ]
    rows[0]["pass_commits_ge_1000"] = "true"
    rows[1]["pass_commits_ge_1000"] = "true"

    def fake_count(project, qualifier, **kwargs):
        return None if project == "example/role-0" else 60

    monkeypatch.setattr("scripts.discover_github_ansible._search_count", fake_count)
    enrich_pull_request_counts(rows, cache_dir=tmp_path, as_of=AS_OF)

    assert rows[0]["total_prs"] == ""
    assert rows[0]["pass_total_prs_gt_50"] == "not-evaluated"
    assert rows[0]["total_prs_scan_status"] == "unsearchable-repository-renamed-or-removed"
    assert rows[1]["total_prs"] == 60
    assert rows[1]["pass_total_prs_gt_50"] == "true"


def test_search_count_returns_none_on_422_instead_of_raising(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "scripts.discover_github_ansible.requests.get",
        lambda *args, **kwargs: _FakeResponse(422, {"message": "Validation Failed"}),
    )
    from scripts.discover_github_ansible import _search_count

    assert _search_count(
        "example/renamed", "", cache_dir=tmp_path, token=None, offline=False,
    ) is None


def test_commit_enrichment_runs_concurrently_and_covers_every_row(monkeypatch, tmp_path):
    rows = [
        repository_row(repository(full_name=f"example/role-{index}"), "q", AS_OF.isoformat(), AS_OF)
        for index in range(25)
    ]
    calls = []

    def fake_count(project, branch, **kwargs):
        calls.append(project)
        return 1500

    monkeypatch.setattr("scripts.discover_github_ansible._commit_count", fake_count)
    enrich_commit_counts(rows, cache_dir=tmp_path, jobs=8)

    assert sorted(calls) == sorted(row["project"] for row in rows)
    assert all(row["total_commits"] == 1500 for row in rows)
    assert all(row["pass_commits_ge_1000"] == "true" for row in rows)


def test_commit_enrichment_round_robins_multiple_tokens(monkeypatch, tmp_path):
    rows = [
        repository_row(repository(full_name=f"example/role-{index}"), "q", AS_OF.isoformat(), AS_OF)
        for index in range(4)
    ]
    start_indices = []

    def fake_count(project, branch, *, tokens, start_index, **kwargs):
        start_indices.append(start_index)
        assert tokens == ["tok-a", "tok-b"]
        return 1200

    monkeypatch.setattr("scripts.discover_github_ansible._commit_count", fake_count)
    enrich_commit_counts(
        rows, cache_dir=tmp_path, tokens=["tok-a", "tok-b"], jobs=1,
    )

    # Each row starts on a different token round-robin by index; the pool
    # itself (not one pre-selected token) is handed to _commit_count so a
    # retry can fail over to another token instead of sleeping on this one.
    assert sorted(start_indices) == [0, 1, 2, 3]


def test_pr_enrichment_runs_concurrently_and_covers_every_row(monkeypatch, tmp_path):
    rows = [
        repository_row(repository(full_name=f"example/role-{index}"), "q", AS_OF.isoformat(), AS_OF)
        for index in range(20)
    ]
    for row in rows:
        row["pass_commits_ge_1000"] = "true"
    calls = []

    def fake_count(project, qualifier, **kwargs):
        calls.append(project)
        return 60

    monkeypatch.setattr("scripts.discover_github_ansible._search_count", fake_count)
    enrich_pull_request_counts(rows, cache_dir=tmp_path, jobs=8, as_of=AS_OF)

    assert sorted(calls) == sorted(row["project"] for row in rows)
    assert all(row["total_prs"] == 60 for row in rows)
    assert all(row["pass_total_prs_gt_50"] == "true" for row in rows)


def test_commit_count_fails_over_to_another_token_instead_of_sleeping(monkeypatch, tmp_path):
    # If the token this row started on happens to be exhausted, the row
    # must fail over to another token in the pool immediately rather than
    # sleeping for that one token's ~hour-long reset window while the rest
    # of the pool still has spare quota.
    from scripts.discover_github_ansible import _commit_count

    exhausted = _FakeResponse(403, {"message": "API rate limit exceeded"})
    exhausted.headers = {"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "99999999999"}
    ok = _FakeResponse(200, [{"sha": "a"}])
    ok.headers = {"Link": '<https://api.github.com/x?page=7>; rel="last"'}

    seen_tokens = []

    def fake_get(url, params, headers, timeout):
        seen_tokens.append(headers.get("Authorization"))
        return exhausted if headers.get("Authorization") == "Bearer tok-a" else ok

    monkeypatch.setattr("scripts.discover_github_ansible.requests.get", fake_get)
    slept = []
    monkeypatch.setattr("scripts.discover_github_ansible.time.sleep", lambda s: slept.append(s))

    count = _commit_count(
        "example/role", "main", cache_dir=tmp_path,
        tokens=["tok-a", "tok-b"], start_index=0, offline=False,
    )

    assert count == 7
    assert seen_tokens == ["Bearer tok-a", "Bearer tok-b"]
    # Failed over on the very next attempt -- never slept waiting on tok-a.
    assert slept == []


def test_commit_count_retries_secondary_rate_limit_and_succeeds(monkeypatch, tmp_path):
    # A 403 with no X-RateLimit-Remaining=0 but a "secondary rate limit"
    # message is GitHub's abuse-detection throttle -- it can trigger from
    # request concurrency even while primary quota is nonzero, and must be
    # retried with backoff rather than treated as a permanent failure.
    from scripts.discover_github_ansible import _commit_count

    secondary_limited = _FakeResponse(403, {"message": "You have exceeded a secondary rate limit"})
    ok = _FakeResponse(200, [{"sha": "a"}])
    ok.headers = {"Link": '<https://api.github.com/x?page=42>; rel="last"'}
    responses = [secondary_limited, ok]

    monkeypatch.setattr(
        "scripts.discover_github_ansible.requests.get",
        lambda *args, **kwargs: responses.pop(0),
    )
    monkeypatch.setattr("scripts.discover_github_ansible.time.sleep", lambda seconds: None)

    count = _commit_count(
        "example/role", "main", cache_dir=tmp_path, token=None, offline=False,
    )
    assert count == 42
    assert not responses


def test_commit_count_raises_immediately_on_non_rate_limit_403(monkeypatch, tmp_path):
    from scripts.discover_github_ansible import _commit_count

    calls = []

    def fake_get(*args, **kwargs):
        calls.append(1)
        return _FakeResponse(403, {"message": "Must have admin rights to Repository"})

    monkeypatch.setattr("scripts.discover_github_ansible.requests.get", fake_get)
    monkeypatch.setattr("scripts.discover_github_ansible.time.sleep", lambda seconds: None)

    import requests

    with pytest.raises(requests.HTTPError):
        _commit_count("example/role", "main", cache_dir=tmp_path, token=None, offline=False)
    # Fails on the first non-rate-limit 403 instead of burning through the
    # whole retry budget on an error retrying will never fix.
    assert len(calls) == 1


def test_commit_enrichment_precedes_pr_enrichment(monkeypatch, tmp_path):
    rows = [repository_row(repository(), "q", AS_OF.isoformat(), AS_OF)]
    monkeypatch.setattr(
        "scripts.discover_github_ansible._commit_count", lambda *args, **kwargs: 1200
    )
    enrich_commit_counts(rows, cache_dir=tmp_path)
    assert rows[0]["total_commits"] == 1200
    assert rows[0]["total_commits_source"] == "github-default-branch-rest"
    assert rows[0]["pass_commits_ge_1000"] == "true"


def test_commit_enrichment_records_unavailable_repository_and_continues(
    monkeypatch, tmp_path
):
    rows = [
        repository_row(
            repository(full_name=f"example/role-{index}"),
            "q",
            AS_OF.isoformat(),
            AS_OF,
        )
        for index in range(2)
    ]
    counts = iter((None, 1200))
    monkeypatch.setattr(
        "scripts.discover_github_ansible._commit_count",
        lambda *args, **kwargs: next(counts),
    )

    enrich_commit_counts(rows, cache_dir=tmp_path)

    assert rows[0]["total_commits"] == ""
    assert rows[0]["commit_count_status"] == "unavailable-http-404"
    assert rows[0]["pass_commits_ge_1000"] == "false"
    assert rows[1]["total_commits"] == 1200
    assert rows[1]["commit_count_status"] == "completed"


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


def test_incomplete_results_are_retried_and_never_cached(tmp_path, monkeypatch):
    # GitHub search can time out server-side and still return HTTP 200 with
    # incomplete_results=true. Previously this got cached like any other
    # successful response and the caller raised immediately -- a resume
    # would replay the same incomplete payload from cache forever, never
    # actually retrying against GitHub.
    cache = tmp_path / "response.json"
    responses = [
        _FakeResponse(200, {"incomplete_results": True, "items": []}),
        _FakeResponse(200, {"incomplete_results": False, "items": [1, 2]}),
    ]

    def fake_get(*args, **kwargs):
        return responses.pop(0)

    monkeypatch.setattr("scripts.discover_github_ansible.requests.get", fake_get)
    monkeypatch.setattr("scripts.discover_github_ansible.time.sleep", lambda seconds: None)

    payload = _request_json(
        "https://api.github.com/search/repositories", params={}, cache_path=cache,
    )
    assert payload == {"incomplete_results": False, "items": [1, 2]}
    assert not responses
    assert json.loads(cache.read_text(encoding="utf-8")) == payload


def test_incomplete_results_exhausting_retries_raises(tmp_path, monkeypatch):
    cache = tmp_path / "response.json"
    monkeypatch.setattr(
        "scripts.discover_github_ansible.requests.get",
        lambda *args, **kwargs: _FakeResponse(200, {"incomplete_results": True, "items": []}),
    )
    monkeypatch.setattr("scripts.discover_github_ansible.time.sleep", lambda seconds: None)

    try:
        _request_json(
            "https://api.github.com/search/repositories", params={}, cache_path=cache, retries=2,
        )
    except RuntimeError as exc:
        assert "incomplete_results" in str(exc)
    else:
        raise AssertionError("expected a RuntimeError after exhausting retries")
    assert not cache.exists()


class _FakeResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload
        self.headers = {}
        self.text = json.dumps(payload)

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            import requests

            raise requests.HTTPError(f"HTTP {self.status_code}", response=self)


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


def test_request_json_waits_for_secondary_limit(monkeypatch, tmp_path):
    class Response:
        def __init__(self, status, payload, headers=None):
            self.status_code = status
            self._payload = payload
            self.headers = headers or {}
            self.text = json.dumps(payload)

        def json(self):
            return self._payload

        def raise_for_status(self):
            if self.status_code >= 400:
                raise RuntimeError(f"HTTP {self.status_code}")

    responses = iter(
        [
            Response(
                403,
                {"message": "You have exceeded a secondary rate limit."},
                {"X-RateLimit-Remaining": "4999"},
            ),
            Response(200, {"items": [1]}),
        ]
    )
    waits = []
    monkeypatch.setattr(
        "scripts.discover_github_ansible.requests.get",
        lambda *args, **kwargs: next(responses),
    )
    monkeypatch.setattr("scripts.discover_github_ansible.time.sleep", waits.append)

    result = _request_json(
        "https://api.github.com/example",
        params={},
        cache_path=tmp_path / "secondary.json",
    )

    assert result == {"items": [1]}
    assert waits == [60]


def test_complete_discovery_partitions_oversized_queries(monkeypatch, tmp_path):
    calls = []

    def fake_request(url, *, params, **kwargs):
        calls.append(params["q"])
        if len(calls) == 1:
            return {"total_count": 1001, "items": [], "incomplete_results": False}
        return {
            "total_count": 1,
            "items": [repository(full_name=f"example/role-{len(calls)}")],
            "incomplete_results": False,
        }

    monkeypatch.setattr("scripts.discover_github_ansible._request_json", fake_request)
    items = _discover_complete_query(
        "topic:ansible",
        cache_dir=tmp_path,
        token=None,
        offline=False,
        refresh_cache=False,
        per_page=100,
        start=datetime(2026, 1, 1, tzinfo=timezone.utc),
        end=datetime(2026, 1, 3, tzinfo=timezone.utc),
    )
    assert len(items) == 2
    assert len(calls) == 3
