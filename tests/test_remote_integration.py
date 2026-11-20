"""Opt-in live equivalence gate pinned to a permanent public commit."""

import json
import os

import pytest

from ansibleguard.cli import analyze_path
from ansibleguard.sources.github.provider import GitHubSource
from ansibleguard.sources.github.client import GitHubClient
from ansibleguard.sources.local import LocalSource

PUBLIC_REPOSITORY = "geerlingguy/ansible-role-nginx"
PUBLIC_COMMIT = "5ff0b235006390a0d5666fd4cce7477410982cdf"


@pytest.mark.skipif(
    os.environ.get("ANSIBLEGUARD_RUN_REMOTE_INTEGRATION") != "1",
    reason="set ANSIBLEGUARD_RUN_REMOTE_INTEGRATION=1 for the pinned live gate",
)
def test_public_exact_sha_local_archive_and_git_are_equivalent(tmp_path):
    anonymous = GitHubClient(token="")
    with GitHubSource(
        PUBLIC_REPOSITORY,
        commit=PUBLIC_COMMIT,
        acquisition="git",
        client=anonymous,
    ).materialize() as git_snapshot:
        with LocalSource(git_snapshot.root).materialize() as local_snapshot:
            local_result = analyze_path(
                local_snapshot.root,
                tmp_path / "local",
                profile="developer-fast",
                source_snapshot=local_snapshot,
            )
            local_tree = local_snapshot.tree_sha256
    with GitHubSource(
        PUBLIC_REPOSITORY,
        commit=PUBLIC_COMMIT,
        acquisition="archive",
        client=anonymous,
    ).materialize() as archive_snapshot:
        archive_result = analyze_path(
            archive_snapshot.root,
            tmp_path / "archive",
            profile="developer-fast",
            source_snapshot=archive_snapshot,
        )
        archive_tree = archive_snapshot.tree_sha256

    assert local_tree == archive_tree
    assert local_result == archive_result
    for relative in (
        "raw/findings.json",
        "canonical/occurrences.json",
    ):
        assert json.loads((tmp_path / "local" / relative).read_text()) == json.loads(
            (tmp_path / "archive" / relative).read_text()
        )
    local_metadata = json.loads((tmp_path / "local/run_metadata.json").read_text())
    archive_metadata = json.loads((tmp_path / "archive/run_metadata.json").read_text())
    assert local_metadata["symbol_index"] == archive_metadata["symbol_index"]


@pytest.mark.skipif(
    not all(
        os.environ.get(name)
        for name in (
            "ANSIBLEGUARD_PRIVATE_TEST_REPOSITORY",
            "ANSIBLEGUARD_PRIVATE_TEST_COMMIT",
            "ANSIBLEGUARD_PRIVATE_TEST_TOKEN",
        )
    ),
    reason="set the three ANSIBLEGUARD_PRIVATE_TEST_* variables for this manual gate",
)
def test_private_exact_sha_materializes_without_credential_provenance():
    client = GitHubClient(token=os.environ.get("ANSIBLEGUARD_PRIVATE_TEST_TOKEN"))
    source = GitHubSource(
        os.environ["ANSIBLEGUARD_PRIVATE_TEST_REPOSITORY"],
        commit=os.environ["ANSIBLEGUARD_PRIVATE_TEST_COMMIT"],
        acquisition="archive",
        client=client,
    )
    with source.materialize() as snapshot:
        provenance = snapshot.provenance()
        assert snapshot.root.is_dir()
        assert provenance["provider"] == "github"
        assert (
            provenance["resolved_sha"] == os.environ["ANSIBLEGUARD_PRIVATE_TEST_COMMIT"]
        )
        assert not any(
            key in provenance for key in ("token", "authorization", "headers")
        )
