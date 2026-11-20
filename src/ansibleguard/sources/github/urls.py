"""Normalize GitHub names and URLs without leaking parsing across the codebase."""

from __future__ import annotations

from dataclasses import dataclass
import re
from urllib.parse import unquote, urlparse

from ..errors import SourceError

_COMPONENT_RE = re.compile(r"^[A-Za-z0-9_.-]+$")


@dataclass(frozen=True)
class GitHubTarget:
    owner: str
    repository: str
    host: str = "github.com"
    ref: str | None = None
    commit: str | None = None
    pull_request: int | None = None

    @property
    def full_name(self) -> str:
        return f"{self.owner}/{self.repository}"


def _validated(owner: str, repository: str, **values) -> GitHubTarget:
    repository = repository.removesuffix(".git")
    if not owner or not repository:
        raise SourceError("GitHub target must contain owner/repository")
    if not _COMPONENT_RE.fullmatch(owner) or not _COMPONENT_RE.fullmatch(repository):
        raise SourceError("GitHub owner/repository contains unsupported characters")
    return GitHubTarget(owner=owner, repository=repository, **values)


def parse_github_target(value: str, *, host: str | None = None) -> GitHubTarget:
    """Parse owner/repo and repository/tree/commit/pull URLs into one target."""

    raw = str(value).strip()
    if not raw:
        raise SourceError("GitHub target is empty")
    if "://" not in raw:
        parts = raw.strip("/").split("/")
        if len(parts) != 2:
            raise SourceError(
                "GitHub target must be owner/repository or a repository URL"
            )
        return _validated(parts[0], parts[1], host=host or "github.com")

    parsed = urlparse(raw)
    if parsed.username or parsed.password or parsed.query:
        raise SourceError("credentialed or query-bearing GitHub URLs are not supported")
    parsed_host = (parsed.hostname or "").lower()
    expected_host = (host or parsed_host or "github.com").lower()
    if not parsed_host or parsed_host != expected_host:
        raise SourceError(
            f"GitHub URL host {parsed_host or '<missing>'!r} does not match "
            f"configured host {expected_host!r}"
        )
    parts = [unquote(item) for item in parsed.path.strip("/").split("/") if item]
    if len(parts) < 2:
        raise SourceError("GitHub repository URL must contain owner/repository")
    values = {"host": expected_host}
    if len(parts) >= 4 and parts[2] == "tree":
        values["ref"] = "/".join(parts[3:])
    elif len(parts) >= 4 and parts[2] == "commit":
        values["commit"] = parts[3]
    elif len(parts) >= 4 and parts[2] == "pull":
        try:
            values["pull_request"] = int(parts[3])
        except ValueError as exc:
            raise SourceError("GitHub pull request number must be an integer") from exc
    elif len(parts) > 2:
        raise SourceError("unsupported GitHub repository URL")
    return _validated(parts[0], parts[1], **values)
