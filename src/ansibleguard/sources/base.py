"""Abstract source-provider interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .snapshot import MaterializedSource


class SourceProvider(ABC):
    @abstractmethod
    def materialize(self) -> MaterializedSource:
        """Return a context-managed working tree and immutable provenance."""
