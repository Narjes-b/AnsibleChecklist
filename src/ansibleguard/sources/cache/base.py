"""Source cache interfaces; blobs and metadata remain separable."""

from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .keys import SourceCacheKey


@dataclass(frozen=True)
class CacheRecord:
    key: SourceCacheKey
    tree_sha256: str
    storage_path: str
    created_at: str
    last_accessed_at: str
    verified: bool = True
    pinned: bool = False
    size_bytes: int = 0
    metadata: dict[str, Any] | None = None

    def as_dict(self) -> dict:
        payload = asdict(self)
        payload["key"] = self.key.canonical()
        return payload


class CacheBackend(ABC):
    @contextmanager
    def lock(self, key: SourceCacheKey, *, wait_seconds=60):
        """Serialize one key when supported; desktop backends are no-op."""
        yield

    @abstractmethod
    def lookup(self, key: SourceCacheKey) -> CacheRecord | None:
        pass

    @abstractmethod
    def store(
        self,
        key: SourceCacheKey,
        source_root: Path,
        tree_sha256: str,
        *,
        metadata: dict | None = None,
        pinned: bool = False,
    ) -> CacheRecord:
        pass

    @abstractmethod
    def materialize(self, record: CacheRecord, destination: Path) -> Path:
        pass

    @abstractmethod
    def invalidate(self, key: SourceCacheKey) -> None:
        pass
