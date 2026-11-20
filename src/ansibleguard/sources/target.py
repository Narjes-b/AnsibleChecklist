"""Provider-neutral remote target primitives."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RemoteTarget:
    provider: str
    repository: str
    host: str
    ref: str | None = None
    commit: str | None = None
    pull_request: int | None = None
