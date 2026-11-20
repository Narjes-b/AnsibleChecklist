from scripts.v007_bundle_redact_v2 import redact_text
from scripts.v007_bundle_secret_scan import scan_text


def test_removes_everything_the_scanner_finds():
    text = "Author: dev.person@corp.io\n  238 |   " + "QUJD" * 20 + "\nkey: ghp_" + "a1B2c3D4e5F6g7H8i9J0k1L2m3" + "\n"
    out = redact_text(text)
    assert scan_text(out) == []
    assert "[REDACTED_EMAIL]" in out and "[REDACTED_BASE64_BLOCK]" in out and "[REDACTED_TOKEN]" in out


def test_keeps_gutter_placeholders_and_clean_text():
    text = "  12 | admin@example.com\n  13 | name: Install nginx\n"
    assert redact_text(text) == text


def test_is_idempotent():
    once = redact_text("a@corp.io " + "QUJD" * 20)
    assert redact_text(once) == once
