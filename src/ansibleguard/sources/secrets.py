"""Secret values whose repr/str cannot leak through tracebacks or logs."""

from __future__ import annotations


class SecretValue:
    __slots__ = ("_value",)

    def __init__(self, value: str):
        self._value = str(value)

    def reveal(self) -> str:
        return self._value

    def __bool__(self):
        return bool(self._value)

    def __repr__(self):
        return "<redacted>"

    def __str__(self):
        return "<redacted>"


def as_secret(value) -> SecretValue | None:
    if value is None:
        return None
    if isinstance(value, SecretValue):
        return value
    return SecretValue(str(value))


class RedactedEnvironment(dict):
    """A subprocess environment that does not render credential values."""

    def __repr__(self):
        return "<redacted subprocess environment>"
