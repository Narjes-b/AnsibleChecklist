"""GitLab project name/URL normalization."""

from __future__ import annotations

from dataclasses import dataclass
import re
from urllib.parse import unquote, urlparse

from ..errors import SourceError

_PART_RE = re.compile(r"^[A-Za-z0-9_.-]+$")


@dataclass(frozen=True)
class GitLabTarget:
    namespace: str
    repository: str
    host: str = "gitlab.com"

    @property
    def full_name(self) -> str:
        return f"{self.namespace}/{self.repository}"


def parse_gitlab_target(value: str, *, host: str | None = None) -> GitLabTarget:
    raw = str(value).strip()
    if not raw:
        raise SourceError("GitLab target is empty")
    configured_host = (host or "gitlab.com").lower()
    if "://" in raw:
        parsed = urlparse(raw)
        if parsed.username or parsed.password or parsed.query:
            raise SourceError(
                "credentialed or query-bearing GitLab URLs are not supported"
            )
        parsed_host = (parsed.hostname or "").lower()
        if host is None:
            configured_host = parsed_host
        if not parsed_host or parsed_host != configured_host:
            raise SourceError("GitLab URL host does not match the configured host")
        parts = [unquote(part) for part in parsed.path.strip("/").split("/") if part]
    else:
        parts = [part for part in raw.strip("/").split("/") if part]
    if len(parts) < 2:
        raise SourceError("GitLab target must contain namespace/repository")
    repository = parts[-1].removesuffix(".git")
    namespace_parts = parts[:-1]
    if not all(_PART_RE.fullmatch(part) for part in [*namespace_parts, repository]):
        raise SourceError("GitLab target contains unsupported characters")
    return GitLabTarget("/".join(namespace_parts), repository, configured_host)
