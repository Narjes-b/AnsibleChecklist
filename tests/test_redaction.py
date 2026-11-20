from ansibleguard.external.ansible_lint import _validate_lint_payload
from ansibleguard.external.gitleaks import ToolResult
from ansibleguard.redaction import redact_sensitive_text
from ansibleguard.runtime import diagnostic


def test_sensitive_operational_text_is_redacted():
    raw = (
        "password=hunter2 token: abc123 "
        '"client_secret": "quoted-value" '
        "Authorization: Bearer eyJ.secret.signature "
        "https://user:pass@example.invalid/path"
    )

    redacted = redact_sensitive_text(raw)

    for secret in ("hunter2", "abc123", "quoted-value", "eyJ.secret.signature", "user:pass"):
        assert secret not in redacted
    assert redacted.count("[REDACTED]") >= 5


def test_tool_result_redacts_message_and_nested_diagnostic_metadata():
    result = ToolResult(
        "tool-error",
        message="provider failed with api_key=live-key",
        metadata={"provider_diagnostics": [{"message": "password: leaked"}]},
    )

    assert "live-key" not in result.message
    assert "leaked" not in result.metadata["provider_diagnostics"][0]["message"]


def test_internal_ansible_lint_error_message_is_redacted():
    _findings, diagnostics = _validate_lint_payload(
        [{"check_name": "internal-error", "message": "token=provider-token"}]
    )

    assert diagnostics[0]["message"] == "token=[REDACTED]"


def test_runtime_diagnostic_redacts_exception_text():
    item = diagnostic("site.yml", "detector", "analysis-error", "password: nope")

    assert item["message"] == "password: [REDACTED]"
