import io
import json
from pathlib import Path
import tarfile

from ansibleguard.cli import analyze_path
from ansibleguard.sources.gitlab.auth import (
    gitlab_git_auth_environment,
    resolve_gitlab_token,
)
from ansibleguard.sources.gitlab.client import GitLabClient
from ansibleguard.sources.gitlab.provider import GitLabSource
from ansibleguard.sources.gitlab.urls import parse_gitlab_target
from ansibleguard.sources.errors import SourceError
import pytest
from ansibleguard.sources.local import LocalSource


class Response:
    status_code = 200

    def __init__(self, payload):
        self.payload = payload

    def json(self):
        return self.payload


class Session:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return self.response


def _archive(path: Path):
    with tarfile.open(path, "w:gz") as archive:
        payload = b"- hosts: all\n"
        info = tarfile.TarInfo("group-project/site.yml")
        info.size = len(payload)
        archive.addfile(info, io.BytesIO(payload))


class ArchiveClient:
    token = "private-token"

    def __init__(self, archive):
        self.archive = archive

    def get_project(self, repository):
        return {"default_branch": "main"}

    def resolve_ref(self, repository, ref):
        return "c" * 40

    def download_archive(self, repository, sha, destination, max_bytes):
        destination.write_bytes(self.archive.read_bytes())


def test_gitlab_target_supports_nested_groups_and_self_managed_host():
    target = parse_gitlab_target("group/subgroup/project")
    assert target.full_name == "group/subgroup/project"
    enterprise = parse_gitlab_target(
        "https://gitlab.company.test/group/project",
        host="gitlab.company.test",
    )
    assert enterprise.host == "gitlab.company.test"
    with pytest.raises(SourceError, match="credentialed"):
        parse_gitlab_target("https://secret@gitlab.com/group/project")


def test_gitlab_auth_priority_and_git_header(monkeypatch):
    monkeypatch.setenv("GITLAB_TOKEN", "first")
    monkeypatch.setenv("GL_TOKEN", "second")
    assert resolve_gitlab_token().reveal() == "first"
    environment = gitlab_git_auth_environment("first", "gitlab.com")
    assert environment["GIT_CONFIG_KEY_0"].endswith("gitlab.com/.extraheader")
    assert "first" not in environment["GIT_CONFIG_VALUE_0"]


def test_gitlab_client_resolves_ref_without_token_in_url():
    session = Session(Response({"id": "d" * 40}))
    client = GitLabClient(token="secret-token", session=session, retries=0)
    assert client.resolve_ref("group/project", "feature/name") == "d" * 40
    url, kwargs = session.calls[0]
    assert "group%2Fproject" in url
    assert "feature%2Fname" in url
    assert "secret-token" not in url
    assert kwargs["headers"]["PRIVATE-TOKEN"] == "secret-token"


def test_gitlab_archive_source_records_provenance_and_cleans_up(tmp_path):
    archive = tmp_path / "source.tar.gz"
    _archive(archive)
    source = GitLabSource("group/project", client=ArchiveClient(archive))
    with source.materialize() as snapshot:
        root = snapshot.root
        assert snapshot.provider == "gitlab"
        assert snapshot.requested_ref == "main"
        assert snapshot.resolved_sha == "c" * 40
        assert "private-token" not in json.dumps(snapshot.provenance())
    assert not root.exists()


def test_local_and_gitlab_same_bytes_have_same_findings_and_graph(tmp_path):
    local_root = tmp_path / "local"
    local_root.mkdir()
    (local_root / "site.yml").write_text("- hosts: all\n", encoding="utf-8")
    archive = tmp_path / "source.tar.gz"
    _archive(archive)

    with LocalSource(local_root).materialize() as local:
        local_run = analyze_path(
            local.root,
            tmp_path / "local-output",
            profile="developer-fast",
            source_snapshot=local,
        )
        local_tree = local.tree_sha256
    with GitLabSource(
        "group/project", client=ArchiveClient(archive)
    ).materialize() as remote:
        remote_run = analyze_path(
            remote.root,
            tmp_path / "remote-output",
            profile="developer-fast",
            source_snapshot=remote,
        )
        remote_tree = remote.tree_sha256
    assert local_tree == remote_tree
    assert local_run == remote_run
    local_metadata = json.loads(
        (tmp_path / "local-output/run_metadata.json").read_text()
    )
    remote_metadata = json.loads(
        (tmp_path / "remote-output/run_metadata.json").read_text()
    )
    assert local_metadata["symbol_index"] == remote_metadata["symbol_index"]
    assert json.loads(
        (tmp_path / "local-output/canonical/occurrences.json").read_text()
    ) == json.loads((tmp_path / "remote-output/canonical/occurrences.json").read_text())
