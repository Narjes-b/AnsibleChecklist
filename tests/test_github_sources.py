import io
import json
from contextlib import contextmanager
from pathlib import Path
import tarfile

import pytest
import requests

from ansibleguard.cli import analyze_path
from ansibleguard.file_manifest import classify_repository, write_file_manifest
from ansibleguard.sources.cache.filesystem import FileSystemCache
from ansibleguard.sources.local import LocalSource
from ansibleguard.sources.errors import SourceError
from ansibleguard.sources.github.archive import secure_extract_tar
from ansibleguard.sources.github.auth import (
    git_auth_environment,
    redact_secrets,
    resolve_github_token,
)
from ansibleguard.sources.github.client import GitHubClient
from ansibleguard.sources.github.comments import COMMENT_MARKER, GitHubCommentPublisher
from ansibleguard.sources.github.git import (
    diff_against_remote,
    find_lfs_pointers,
    validate_submodules,
)
from ansibleguard.sources.github.pr import resolve_pull_request
from ansibleguard.sources.github.provider import GitHubSource
from ansibleguard.sources.github.urls import parse_github_target
from ansibleguard.sources.secrets import SecretValue


class Response:
    def __init__(self, payload=None, status_code=200, chunks=()):
        self.payload = payload
        self.status_code = status_code
        self.chunks = chunks

    def json(self):
        return self.payload

    def iter_content(self, chunk_size):
        yield from self.chunks


class Session:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def _tar(path: Path, members):
    with tarfile.open(path, "w:gz") as archive:
        for name, kind, payload in members:
            info = tarfile.TarInfo(name)
            if kind == "file":
                data = payload.encode()
                info.size = len(data)
                archive.addfile(info, io.BytesIO(data))
            elif kind == "dir":
                info.type = tarfile.DIRTYPE
                archive.addfile(info)
            elif kind == "symlink":
                info.type = tarfile.SYMTYPE
                info.linkname = payload
                archive.addfile(info)
            elif kind == "fifo":
                info.type = tarfile.FIFOTYPE
                archive.addfile(info)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Owner/repo", ("Owner/repo", None, None, None)),
        ("https://github.com/Owner/repo", ("Owner/repo", None, None, None)),
        (
            "https://github.com/Owner/repo/tree/feature/security",
            ("Owner/repo", "feature/security", None, None),
        ),
        (
            "https://github.com/Owner/repo/commit/abc123",
            ("Owner/repo", None, "abc123", None),
        ),
        (
            "https://github.com/Owner/repo/pull/42",
            ("Owner/repo", None, None, 42),
        ),
    ],
)
def test_github_target_normalization(value, expected):
    target = parse_github_target(value)
    assert (
        target.full_name,
        target.ref,
        target.commit,
        target.pull_request,
    ) == expected


def test_github_enterprise_target_requires_matching_host():
    target = parse_github_target(
        "https://github.company.test/team/repo", host="github.company.test"
    )
    assert target.host == "github.company.test"
    with pytest.raises(SourceError, match="does not match"):
        parse_github_target("https://github.com/team/repo", host="github.company.test")
    with pytest.raises(SourceError, match="credentialed"):
        parse_github_target("https://secret@github.com/team/repo")


def test_github_auth_priority_and_git_environment(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "first-secret")
    monkeypatch.setenv("GH_TOKEN", "second-secret")
    assert resolve_github_token().reveal() == "first-secret"
    environment = git_auth_environment("first-secret", "github.com")
    assert environment["GIT_CONFIG_VALUE_0"] == "Authorization: Bearer first-secret"
    assert (
        redact_secrets("failed first-secret", ("first-secret",)) == "failed <redacted>"
    )
    secret = SecretValue("first-secret")
    assert repr(secret) == str(secret) == "<redacted>"
    assert "first-secret" not in repr(environment)


def test_github_client_resolves_ref_and_never_sends_token_in_url():
    session = Session([Response({"sha": "a" * 40})])
    client = GitHubClient(token="secret-token", session=session, retries=0)
    assert client.resolve_ref("owner/repo", "feature/name") == "a" * 40
    _, url, kwargs = session.calls[0]
    assert "secret-token" not in url
    assert "feature%2Fname" in url
    assert kwargs["headers"]["Authorization"] == "Bearer secret-token"


def test_github_client_error_does_not_expose_token():
    session = Session([requests.ConnectionError("secret-token")])
    client = GitHubClient(token="secret-token", session=session, retries=0)
    with pytest.raises(SourceError) as exc:
        client.get_repository("owner/repo")
    assert "secret-token" not in str(exc.value)


def test_private_or_missing_repository_error_is_not_misreported_as_missing():
    client = GitHubClient(
        token="secret-token",
        session=Session([Response({}, status_code=404)]),
        retries=0,
    )
    with pytest.raises(SourceError, match="authentication failed or repository/ref"):
        client.get_repository("owner/private")


def test_secure_archive_extracts_regular_files_and_safe_symlink(tmp_path):
    archive = tmp_path / "source.tar.gz"
    _tar(
        archive,
        [
            ("owner-repo/", "dir", ""),
            ("owner-repo/tasks/", "dir", ""),
            ("owner-repo/tasks/main.yml", "file", "- debug: {msg: ok}\n"),
            ("owner-repo/main.yml", "symlink", "tasks/main.yml"),
        ],
    )
    destination = secure_extract_tar(archive, tmp_path / "tree")
    assert (destination / "tasks" / "main.yml").is_file()
    assert (destination / "main.yml").is_symlink()


@pytest.mark.parametrize(
    "members",
    [
        [("owner/../../escape", "file", "bad")],
        [("owner/link", "symlink", "../../escape")],
        [("owner/device", "fifo", "")],
        [("one/a", "file", "a"), ("two/b", "file", "b")],
    ],
)
def test_secure_archive_rejects_traversal_links_special_files_and_multiple_roots(
    tmp_path, members
):
    archive = tmp_path / "source.tar.gz"
    _tar(archive, members)
    destination = tmp_path / "tree"
    with pytest.raises(SourceError):
        secure_extract_tar(archive, destination)
    assert not destination.exists()


def test_secure_archive_enforces_file_count_and_size_limits(tmp_path):
    archive = tmp_path / "source.tar.gz"
    _tar(archive, [("owner/a", "file", "12345")])
    with pytest.raises(SourceError, match="file-count"):
        secure_extract_tar(archive, tmp_path / "count", max_files=0)
    with pytest.raises(SourceError, match="uncompressed-size"):
        secure_extract_tar(archive, tmp_path / "size", max_uncompressed_bytes=4)


class ArchiveClient:
    token = "must-not-appear"

    def __init__(self, source_archive: Path):
        self.source_archive = source_archive
        self.downloads = 0

    def get_repository(self, repository):
        return {"default_branch": "main"}

    def resolve_ref(self, repository, ref):
        return "b" * 40

    def download_archive(self, repository, sha, destination, max_bytes):
        self.downloads += 1
        destination.write_bytes(self.source_archive.read_bytes())


def test_github_archive_source_resolves_default_branch_and_cleans_up(tmp_path):
    archive = tmp_path / "source.tar.gz"
    _tar(archive, [("owner-repo/tasks/main.yml", "file", "- debug: {msg: ok}\n")])
    source = GitHubSource("owner/repo", client=ArchiveClient(archive))

    with source.materialize() as snapshot:
        root = snapshot.root
        provenance = snapshot.provenance()
        assert (root / "tasks" / "main.yml").is_file()
        assert provenance["requested_ref"] == "main"
        assert provenance["resolved_sha"] == "b" * 40
        assert provenance["acquisition"] == "archive"
        assert "must-not-appear" not in json.dumps(provenance)
    assert not root.exists()


def test_exact_commit_is_separate_from_requested_ref_in_provenance(tmp_path):
    archive = tmp_path / "source.tar.gz"
    _tar(archive, [("owner-repo/site.yml", "file", "- hosts: all\n")])
    source = GitHubSource("owner/repo", commit="abc123", client=ArchiveClient(archive))
    with source.materialize() as snapshot:
        assert snapshot.requested_ref is None
        assert snapshot.metadata["requested_commit"] == "abc123"
        assert snapshot.resolved_sha == "b" * 40


def test_github_cache_reuses_verified_full_sha_snapshot(tmp_path):
    archive = tmp_path / "source.tar.gz"
    _tar(archive, [("owner-repo/site.yml", "file", "- hosts: all\n")])
    client = ArchiveClient(archive)
    cache = FileSystemCache(tmp_path / "cache")

    with GitHubSource("owner/repo", client=client, cache=cache).materialize() as first:
        first_hash = first.tree_sha256
        assert first.metadata["cache"]["status"] == "miss"
    with GitHubSource("owner/repo", client=client, cache=cache).materialize() as second:
        assert second.tree_sha256 == first_hash
        assert second.metadata["cache"]["status"] == "hit"

    assert client.downloads == 1


def test_github_provider_holds_cache_lock_through_acquisition(tmp_path):
    archive = tmp_path / "source.tar.gz"
    _tar(archive, [("owner-repo/site.yml", "file", "- hosts: all\n")])
    events = []

    class LockedCache(FileSystemCache):
        @contextmanager
        def lock(self, key, wait_seconds=60):
            events.append(("enter", key.commit))
            yield
            events.append(("exit", key.commit))

    cache = LockedCache(tmp_path / "cache")
    with GitHubSource(
        "owner/repo", client=ArchiveClient(archive), cache=cache
    ).materialize():
        pass
    assert events == [("enter", "b" * 40), ("exit", "b" * 40)]


def test_local_and_github_archive_same_bytes_have_same_analysis(tmp_path):
    repository = tmp_path / "local"
    (repository / "roles" / "web" / "defaults").mkdir(parents=True)
    (repository / "roles" / "web" / "tasks").mkdir(parents=True)
    (repository / "roles" / "web" / "defaults" / "main.yml").write_text(
        "web_port: 8080\n", encoding="utf-8"
    )
    (repository / "roles" / "web" / "tasks" / "main.yml").write_text(
        "- name: Show port\n  debug:\n    msg: '{{ web_port }}'\n",
        encoding="utf-8",
    )
    archive = tmp_path / "source.tar.gz"
    _tar(
        archive,
        [
            ("owner-repo/roles/web/defaults/main.yml", "file", "web_port: 8080\n"),
            (
                "owner-repo/roles/web/tasks/main.yml",
                "file",
                "- name: Show port\n  debug:\n    msg: '{{ web_port }}'\n",
            ),
        ],
    )

    with LocalSource(repository).materialize() as local:
        local_result = analyze_path(
            local.root,
            tmp_path / "local-output",
            profile="developer-fast",
            source_snapshot=local,
        )
        local_tree = local.tree_sha256
    with GitHubSource(
        "owner/repo", client=ArchiveClient(archive)
    ).materialize() as remote:
        remote_result = analyze_path(
            remote.root,
            tmp_path / "remote-output",
            profile="developer-fast",
            source_snapshot=remote,
        )
        remote_tree = remote.tree_sha256

    assert local_tree == remote_tree
    assert local_result == remote_result
    for relative in (
        "raw/findings.json",
        "canonical/occurrences.json",
    ):
        local_payload = json.loads((tmp_path / "local-output" / relative).read_text())
        remote_payload = json.loads((tmp_path / "remote-output" / relative).read_text())
        assert local_payload == remote_payload
    local_metadata = json.loads(
        (tmp_path / "local-output" / "run_metadata.json").read_text()
    )
    remote_metadata = json.loads(
        (tmp_path / "remote-output" / "run_metadata.json").read_text()
    )
    assert local_metadata["symbol_index"] == remote_metadata["symbol_index"]


def test_remote_manifest_selection_matches_local_population(tmp_path):
    repository = tmp_path / "local"
    (repository / "roles" / "web" / "tasks").mkdir(parents=True)
    (repository / "tests").mkdir()
    task = "- name: Configure\n  debug:\n    msg: ready\n"
    test_play = "- hosts: localhost\n  tasks: []\n"
    (repository / "roles/web/tasks/main.yml").write_text(task, encoding="utf-8")
    (repository / "tests/integration.yml").write_text(test_play, encoding="utf-8")
    manifest = write_file_manifest(
        classify_repository(repository, "owner/repo", "b" * 40),
        tmp_path / "files.csv",
    )
    archive = tmp_path / "source.tar.gz"
    _tar(
        archive,
        [
            ("owner-repo/roles/web/tasks/main.yml", "file", task),
            ("owner-repo/tests/integration.yml", "file", test_play),
        ],
    )
    with LocalSource(repository).materialize() as local:
        local_run = analyze_path(
            local.root,
            tmp_path / "local-output",
            file_manifest=manifest,
            profile="developer-fast",
            source_snapshot=local,
        )
    with GitHubSource(
        "owner/repo", client=ArchiveClient(archive)
    ).materialize() as remote:
        remote_run = analyze_path(
            remote.root,
            tmp_path / "remote-output",
            file_manifest=manifest,
            profile="developer-fast",
            source_snapshot=remote,
        )
    assert local_run == remote_run
    local_metadata = json.loads(
        (tmp_path / "local-output/run_metadata.json").read_text()
    )
    remote_metadata = json.loads(
        (tmp_path / "remote-output/run_metadata.json").read_text()
    )
    assert (
        local_metadata["analysis_scope"]["internal"]
        == remote_metadata["analysis_scope"]["internal"]
    )
    assert local_metadata["file_selection"] == remote_metadata["file_selection"]
    assert local_metadata["symbol_index"] == remote_metadata["symbol_index"]


def test_fork_pull_request_keeps_distinct_head_repository():
    class Client:
        def get_pull_request(self, repository, number):
            return {
                "base": {"repo": {"full_name": "company/base"}, "sha": "a" * 40},
                "head": {"repo": {"full_name": "person/fork"}, "sha": "b" * 40},
            }

    pull = resolve_pull_request(Client(), "company/base", 42)
    assert pull.base_repository == "company/base"
    assert pull.head_repository == "person/fork"
    assert pull.base_sha != pull.head_sha


def test_remote_git_diff_uses_tokenless_remote_and_ephemeral_header(
    tmp_path, monkeypatch
):
    calls = []

    class Completed:
        stdout = "diff --git a/site.yml b/site.yml\n"
        stderr = ""

    def run(command, **kwargs):
        calls.append((command, kwargs))
        return Completed()

    monkeypatch.setattr("ansibleguard.sources.github.git.subprocess.run", run)
    result = diff_against_remote(
        base_tree=tmp_path,
        head_repository="person/fork",
        head_sha="b" * 40,
        host="github.com",
        token="secret-token",
    )

    assert result.startswith("diff --git")
    assert all("secret-token" not in " ".join(command) for command, _ in calls)
    assert all(
        kwargs["env"]["GIT_CONFIG_VALUE_0"] == "Authorization: Bearer secret-token"
        for _, kwargs in calls
    )


def test_pr_comment_publisher_redacts_token_and_marks_comment():
    class Client:
        token = "secret-token"

        def create_issue_comment(self, repository, number, body):
            self.call = (repository, number, body)
            return {"id": 1}

    client = Client()
    GitHubCommentPublisher(client, "owner/repo").publish(
        42, "Analysis mentions secret-token"
    )
    assert client.call[0:2] == ("owner/repo", 42)
    assert client.call[2].startswith(COMMENT_MARKER)
    assert "secret-token" not in client.call[2]


def test_submodule_policy_accepts_same_host_https_and_relative_urls(tmp_path):
    (tmp_path / ".gitmodules").write_text(
        '[submodule "one"]\n'
        "  path = vendor/one\n"
        "  url = https://github.com/owner/one.git\n"
        '[submodule "two"]\n'
        "  path = vendor/two\n"
        "  url = ../two.git\n",
        encoding="utf-8",
    )
    rows = validate_submodules(tmp_path, "github.com")
    assert [row["path"] for row in rows] == ["vendor/one", "vendor/two"]


@pytest.mark.parametrize(
    "body",
    [
        '[submodule "x"]\n path = ../../escape\n url = ../repo.git\n',
        '[submodule "x"]\n path = vendor/x\n url = file:///tmp/repo\n',
        '[submodule "x"]\n path = vendor/x\n url = https://token@github.com/a/b\n',
        '[submodule "x"]\n path = vendor/x\n url = https://gitlab.com/a/b\n',
        '[submodule "x"]\n path = vendor/x\n url = ../repo\n update = !bad\n',
    ],
)
def test_submodule_policy_rejects_escaping_credentials_transports_and_commands(
    tmp_path, body
):
    (tmp_path / ".gitmodules").write_text(body, encoding="utf-8")
    with pytest.raises(SourceError):
        validate_submodules(tmp_path, "github.com")


def test_lfs_pointers_are_detected_without_fetching(tmp_path):
    (tmp_path / "artifact.bin").write_text(
        "version https://git-lfs.github.com/spec/v1\n"
        f"oid sha256:{'a' * 64}\n"
        "size 12345\n",
        encoding="utf-8",
    )
    assert find_lfs_pointers(tmp_path) == ("artifact.bin",)


def test_archive_mode_rejects_submodule_or_lfs_materialization(tmp_path):
    archive = tmp_path / "source.tar.gz"
    _tar(archive, [("owner-repo/site.yml", "file", "- hosts: all\n")])
    source = GitHubSource("owner/repo", client=ArchiveClient(archive), include_lfs=True)
    with pytest.raises(SourceError, match="requires Git acquisition"):
        source.materialize()
