from scripts.v007_bundle_secret_scan import scan_text


def kinds(text):
    return {kind for _, kind, _ in scan_text(text)}


def test_clean_text_has_no_findings():
    assert scan_text("- name: Install nginx\n  password: [REDACTED_LITERAL]\n  mail: admin@example.com\n") == []


def test_detects_email_token_and_base64_line():
    text = "contact: dev.person@corp.io\nkey: " + "ghp_" + "a1B2c3D4e5F6g7H8i9J0k1L2m3" + "\n" + "QUJD" * 20 + "\n"
    assert kinds(text) == {"email", "token-prefix", "long-base64-line"}


def test_hashes_and_paths_are_ignored():
    assert scan_text("sha: " + "a" * 40 + "\npath: /usr/lib/python3/dist-packages/ansible/modules/x/y/z\n") == []


def test_values_are_never_returned():
    assert all(isinstance(item[2], int) for item in scan_text("x@corp.io"))


def test_line_number_gutter_is_ignored_for_base64_lines():
    assert kinds("  238 |   " + "QUJD" * 20) == {"long-base64-line"}


def test_slug_identifiers_are_not_entropy_hits():
    assert scan_text("V007PILOT-SECURITY-013 and a_very_long_snake_case_identifier_with_numbers_123456789\n") == []
