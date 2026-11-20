"""Pull-request source resolution independent of analysis/comparison."""

from __future__ import annotations

from dataclasses import dataclass

from ..errors import SourceError
from .client import GitHubClient


@dataclass(frozen=True)
class GitHubPullRequest:
    number: int
    base_repository: str
    base_sha: str
    head_repository: str
    head_sha: str


def resolve_pull_request(
    client: GitHubClient, repository: str, number: int
) -> GitHubPullRequest:
    payload = client.get_pull_request(repository, number)
    try:
        base_repository = payload["base"]["repo"]["full_name"]
        base_sha = payload["base"]["sha"]
        head_repository = payload["head"]["repo"]["full_name"]
        head_sha = payload["head"]["sha"]
    except (KeyError, TypeError) as exc:
        raise SourceError("GitHub pull request metadata is incomplete") from exc
    if not all(
        isinstance(value, str) and value
        for value in (base_repository, base_sha, head_repository, head_sha)
    ):
        raise SourceError("GitHub pull request metadata is incomplete")
    return GitHubPullRequest(
        number=int(number),
        base_repository=base_repository,
        base_sha=base_sha,
        head_repository=head_repository,
        head_sha=head_sha,
    )
