from ansibleguard.external.gitleaks import scan_with_gitleaks_file_output
from ansibleguard.report.text_writer import write_GitLeaks_results_to_txt


def test_missing_gitleaks_binary_degrades_gracefully(fixtures_dir):
    """Regression test: a missing/misconfigured gitleaks binary path used
    to raise an unguarded FileNotFoundError from subprocess.run(). Matters
    specifically for a CI/PR-bot context — a runner without gitleaks
    pre-installed must not crash the whole check, just skip this one
    finding gracefully."""
    fixture = fixtures_dir / "gitleaks_dummy_playbook.yml"
    result = scan_with_gitleaks_file_output(
        str(fixture), "/nonexistent/path/to/gitleaks"
    )
    assert result == []


def test_nonexistent_target_path_does_not_crash(fixtures_dir):
    """A bad --source path was already handled before this session's fixes
    (gitleaks itself exits non-zero, existing 'else' branch returns []) —
    locking that in so a future edit can't silently regress it."""
    import shutil

    gitleaks_path = shutil.which("gitleaks") or "./gitleaks-bin/gitleaks"
    result = scan_with_gitleaks_file_output("/nonexistent/playbook.yml", gitleaks_path)
    assert result == []


def test_target_local_gitleaks_config_is_passed_to_binary(tmp_path, monkeypatch):
    import subprocess
    from ansibleguard.external.gitleaks import scan_with_gitleaks

    target = tmp_path / "project"
    target.mkdir()
    config = target / ".gitleaks.toml"
    config.write_text("title = 'validation'\n")
    captured = {}

    def fake_run(command, **kwargs):
        captured["command"] = command
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = scan_with_gitleaks(target, "/fake/gitleaks")
    assert result.status == "completed"
    assert captured["command"][-2:] == ["--config", str(config)]
    assert "--redact=100" in captured["command"]


def test_fingerprints_are_stable_across_checkout_roots(tmp_path, monkeypatch):
    import json
    import subprocess
    from ansibleguard.external.gitleaks import scan_with_gitleaks

    target = tmp_path / "separate-worktree"
    target.mkdir()
    secret_file = target / "vars.yml"
    secret_file.write_text("password: synthetic\n", encoding="utf-8")

    def fake_run(command, **kwargs):
        report = command[command.index("--report-path") + 1]
        with open(report, "w", encoding="utf-8") as stream:
            json.dump(
                [
                    {
                        "File": str(secret_file),
                        "StartLine": 1,
                        "RuleID": "generic-api-key",
                        "Fingerprint": (
                            f"{secret_file}:generic-api-key:1"
                        ),
                    }
                ],
                stream,
            )
        return subprocess.CompletedProcess(command, 1, "", "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    finding = scan_with_gitleaks(target, "/fake/gitleaks").findings[0]

    assert finding["File"] == "vars.yml"
    assert finding["Fingerprint"] == "vars.yml:generic-api-key:1"
    assert finding["_scan_mode"] == "dir"


def test_git_range_scan_uses_validated_shas_and_marks_provenance(
    tmp_path, monkeypatch
):
    import json
    import subprocess
    from ansibleguard.external.gitleaks import scan_git_range_with_gitleaks

    captured = {}
    base = "a" * 40
    head = "b" * 40

    def fake_run(command, **kwargs):
        captured["command"] = command
        report = command[command.index("--report-path") + 1]
        with open(report, "w", encoding="utf-8") as stream:
            json.dump([{"File": "vars.yml", "StartLine": 2}], stream)
        return subprocess.CompletedProcess(command, 1, "", "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = scan_git_range_with_gitleaks(tmp_path, "/fake/gitleaks", base, head)

    assert result.status == "completed"
    assert captured["command"][:3] == ["/fake/gitleaks", "git", str(tmp_path)]
    assert captured["command"][
        captured["command"].index("--log-opts") + 1
    ] == f"{base}..{head}"
    assert result.findings[0]["_scan_mode"] == "git-range"


def test_git_range_scan_rejects_untrusted_revision_expression(tmp_path):
    from ansibleguard.external.gitleaks import scan_git_range_with_gitleaks

    result = scan_git_range_with_gitleaks(
        tmp_path, "/fake/gitleaks", "main; touch /tmp/no", "HEAD"
    )
    assert result.status == "tool-error"
    assert "full hexadecimal" in result.message


def test_legacy_gitleaks_output_never_persists_secret_or_match(tmp_path):
    canary = "SECRET-CANARY-MUST-NOT-BE-WRITTEN"
    output = tmp_path / "gitleaks.txt"
    write_GitLeaks_results_to_txt(
        [
            {
                "RuleID": "generic-api-key",
                "Description": "Generic key",
                "File": "vars.yml",
                "StartLine": 4,
                "Secret": canary,
                "Match": f"token={canary}",
                "Fingerprint": "safe-fingerprint",
            }
        ],
        output,
    )
    rendered = output.read_text(encoding="utf-8")
    assert canary not in rendered
    assert '"Secret"' not in rendered
    assert '"Match"' not in rendered
    assert "safe-fingerprint" in rendered
