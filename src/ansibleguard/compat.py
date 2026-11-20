"""Compatibility primitives for every supported Python runtime."""

from __future__ import annotations

try:
    from enum import StrEnum
except ImportError:  # pragma: no cover - executed on Python 3.10
    from enum import Enum

    class StrEnum(str, Enum):
        """Python 3.10-compatible subset of :class:`enum.StrEnum`."""

        def __str__(self):
            return self.value


__all__ = ["StrEnum"]
