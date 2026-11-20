import json

from ansibleguard.cli import analyze_path
from ansibleguard.external.gitleaks import ToolResult
from ansibleguard.profiles import (
    DEVELOPER_FAST,
    LINT,
    SECURITY,
    filter_profile_findings,
    profile_metadata,
)


def test_developer_profiles_expose_explicit_providers():
    assert profile_metadata(DEVELOPER_FAST)["providers"] == ["internal"]
    assert profile_metadata(LINT)["providers"] == ["ansible-lint"]
    assert profile_metadata(SECURITY)["providers"] == [
        "ansible-lint",
        "gitleaks",
        "internal",
    ]


def test_security_profile_filters_native_lint_rules():
    risky = {
        "rule_id": "ansible-lint-issue",
        "provider": "ansible-lint",
        "native_rule_id": "risky-file-permissions",
    }
    style = {
        "rule_id": "ansible-lint-issue",
        "provider": "ansible-lint",
        "native_rule_id": "name[casing]",
    }
    assert filter_profile_findings([risky, style], SECURITY) == [risky]


def test_lint_profile_skips_internal_and_gitleaks_but_keeps_native_identity(
    tmp_path, monkeypatch
):
    target = tmp_path / "project"
    target.mkdir()
    (target / "site.yml").write_text("- debug:\n    msg: ok\n", encoding="utf-8")

    def internal_must_not_run(*args, **kwargs):
        raise AssertionError("internal detector executed for lint-only profile")

    monkeypatch.setattr(
        "ansibleguard.external.gitleaks.scan_with_gitleaks", internal_must_not_run
    )
    monkeypatch.setattr(
        "ansibleguard.smells.execute_for_single_file", internal_must_not_run
    )
    monkeypatch.setattr(
        "ansibleguard.external.ansible_lint.scan_with_ansible_lint",
        lambda *args, **kwargs: ToolResult(
            "completed",
            [
                {
                    "check_name": "name[casing]",
                    "severity": "major",
                    "description": "Name should start with uppercase.",
                    "location": {
                        "path": "site.yml",
                        "positions": {"begin": {"line": 1}},
                    },
                }
            ],
        ),
    )

    output = tmp_path / "output"
    analyze_path(target, output, profile=LINT)
    findings = json.loads((output / "findings.raw.json").read_text())
    assert len(findings) == 1
    assert findings[0]["provider"] == "ansible-lint"
    assert findings[0]["native_rule_id"] == "name[casing]"
    assert json.loads((output / "occurrences.json").read_text())
