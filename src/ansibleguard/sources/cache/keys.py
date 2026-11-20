"""Immutable, collision-resistant cache identities."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import re

from ..errors import SourceError

_FULL_SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")


@dataclass(frozen=True)
class SourceCacheKey:
    provider: str
    host: str
    repository: str
    commit: str
    acquisition: str
    include_submodules: bool = False
    include_lfs: bool = False

    def __post_init__(self):
        if not _FULL_SHA_RE.fullmatch(self.commit):
            raise SourceError("cache keys require a full 40-character commit SHA")

    def canonical(self) -> dict:
        values = asdict(self)
        values["provider"] = self.provider.lower()
        values["host"] = self.host.lower()
        values["repository"] = self.repository.lower()
        values["commit"] = self.commit.lower()
        return values

    @property
    def digest(self) -> str:
        encoded = json.dumps(
            self.canonical(), sort_keys=True, separators=(",", ":")
        ).encode()
        return hashlib.sha256(encoded).hexdigest()

    @property
    def redis_name(self) -> str:
        return f"ansibleguard:source:{self.digest}"
