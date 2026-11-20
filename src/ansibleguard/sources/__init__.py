"""Provider-neutral source acquisition for AnsibleGuard."""

from .base import SourceProvider
from .local import LocalSource
from .snapshot import MaterializedSource, SourceCapabilities, SourceSnapshot

__all__ = [
    "LocalSource",
    "MaterializedSource",
    "SourceCapabilities",
    "SourceProvider",
    "SourceSnapshot",
]
