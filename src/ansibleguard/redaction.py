"""Conservative redaction for diagnostics, logs, and provider failures."""

from __future__ import annotations

import re


_KEY = (
    r"password|passwd|pwd|secret|token|api[_-]?key|access[_-]?key|"
    r"private[_-]?key|client[_-]?secret|authorization"
)
_QUOTED_ASSIGNMENT = re.compile(
    rf"(?i)([\"']?(?:{_KEY})[\"']?\s*[:=]\s*)([\"'])(.*?)(\2)"
)
_PLAIN_ASSIGNMENT = re.compile(
    rf"(?i)(\b(?:{_KEY})\b\s*[:=]\s*)([^\s,;}}\]]+)"
)
_BEARER = re.compile(r"(?i)(\bBearer\s+)[A-Za-z0-9._~+/=-]+")
_URL_CREDENTIAL = re.compile(
    r"(?i)(\b[a-z][a-z0-9+.-]*://)([^\s/@:]+):([^\s/@]+)@"
)


def redact_sensitive_text(value) -> str:
    """Return operational text with credential-shaped values removed."""
    text = str(value or "")
    text = _URL_CREDENTIAL.sub(r"\1[REDACTED]@", text)
    text = _BEARER.sub(r"\1[REDACTED]", text)
    text = _QUOTED_ASSIGNMENT.sub(r"\1\2[REDACTED]\4", text)
    return _PLAIN_ASSIGNMENT.sub(r"\1[REDACTED]", text)


def redact_diagnostic(value):
    """Recursively sanitize diagnostic/provider metadata structures."""
    if isinstance(value, dict):
        return {key: redact_diagnostic(item) for key, item in value.items()}
    if isinstance(value, list):
        return [redact_diagnostic(item) for item in value]
    if isinstance(value, tuple):
        return tuple(redact_diagnostic(item) for item in value)
    return redact_sensitive_text(value) if isinstance(value, str) else value
