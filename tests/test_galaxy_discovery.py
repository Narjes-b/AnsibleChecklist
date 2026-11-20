from scripts.discover_ansible_galaxy import deduplicate, discover_roles, github_project
from scripts.merge_study_candidates import merge_candidates


def test_github_project_normalizes_https_ssh_and_suffixes():
    assert github_project("https://github.com/Owner/repository.git") == "Owner/repository"
    assert github_project("git@github.com:Owner/repository.git") == "Owner/repository"
    assert github_project("https://gitlab.com/owner/repository") == ""


def test_role_discovery_preserves_unresolved_and_resolved_entries(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "scripts.discover_ansible_galaxy._get",
        lambda *args, **kwargs: {
            "next": None,
            "results": [
                {"id": 1, "name": "web", "github_user": "example", "github_repo": "role-web", "download_count": 2},
                {"id": 2, "name": "missing", "github_user": "", "github_repo": ""},
            ],
        },
    )
    rows = discover_roles(cache_dir=tmp_path)
    assert rows[0]["project"] == "example/role-web"
    assert rows[0]["repository_resolution_status"] == "github-resolved"
    assert rows[1]["repository_resolution_status"] == "unresolved"


def test_galaxy_deduplication_combines_role_identifiers():
    rows = [
        {"project": "example/role", "canonical_repository": "example/role", "galaxy_kind": "role", "galaxy_id": "1", "galaxy_name": "one", "source_url": "one"},
        {"project": "example/role", "canonical_repository": "example/role", "galaxy_kind": "role", "galaxy_id": "2", "galaxy_name": "two", "source_url": "two"},
    ]
    merged = deduplicate(rows)
    assert len(merged) == 1
    assert merged[0]["galaxy_id"] == "1;2"


def test_source_merge_deduplicates_galaxy_and_github_and_keeps_provenance(tmp_path):
    github = tmp_path / "github.csv"
    galaxy = tmp_path / "galaxy.csv"
    github.write_text(
        "project,source_host,source_url,discovery_sources,discovery_methods\n"
        "example/role,github,https://github.com/example/role,github,github-topic-search\n"
    )
    galaxy.write_text(
        "project,source_host,github_url,galaxy_id,galaxy_url,discovery_sources,discovery_methods\n"
        "example/role,galaxy,https://github.com/example/role,7,https://galaxy.example/7,ansible-galaxy,galaxy-role-registry\n"
    )
    rows = merge_candidates([galaxy, github])
    assert len(rows) == 1
    assert rows[0]["source_host"] == "github"
    assert rows[0]["galaxy_id"] == "7"
    assert rows[0]["discovery_sources"] == "ansible-galaxy;github"
