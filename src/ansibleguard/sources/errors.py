"""Source-layer failures with messages safe for CLI presentation."""


class SourceError(RuntimeError):
    """A source could not be validated, resolved, or materialized."""


class SourceCapabilityError(SourceError):
    """The requested analysis needs a capability the source does not have."""
