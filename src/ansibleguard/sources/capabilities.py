"""Make unsupported source/profile combinations explicit."""

from __future__ import annotations

from ..profiles import profile_definition
from .errors import SourceCapabilityError


def validate_profile_capabilities(snapshot, profile: str) -> None:
    definition = profile_definition(profile)
    if definition["review_analysis"] and not snapshot.capabilities.git_history:
        raise SourceCapabilityError(
            f"profile {profile} requires Git history, but source acquisition "
            f"{snapshot.acquisition} provides only a working tree"
        )


def validate_diff_capabilities(snapshot) -> None:
    if not snapshot.capabilities.diff:
        raise SourceCapabilityError(
            f"source acquisition {snapshot.acquisition} does not support Git diff"
        )
