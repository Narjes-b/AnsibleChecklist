from ansibleguard.external.gitleaks import scan_with_gitleaks_file_output
from ansibleguard.report.text_writer import write_GitLeaks_results_to_txt


def test_noise_filter_reads_interleaved_files_once_and_preserves_both_output_orders(tmp_path, monkeypatch):
    from collections import Counter
    from pathlib import Path
    from ansibleguard.external.gitleaks import _filter_known_noise

    first, second = tmp_path / "a.yml", tmp_path / "b.yml"
    first.write_text("api_token: active\n# api_token: your_token\n")
    second.write_text("api_token: your_api_key\napi_token: active\n")
    findings = [{"File": file, "StartLine": line, "RuleID": "generic-api-key", "Fingerprint": str(i)}
                for i, (file, line) in enumerate([("b.yml", 2), ("a.yml", 2), ("b.yml", 1), ("a.yml", 1)])]
    reads = Counter()
    original = Path.read_text

    def counted(path, *args, **kwargs):
        reads[path] += 1
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", counted)
    kept, suppressed = _filter_known_noise(findings, tmp_path)
    assert [row["Fingerprint"] for row in kept] == ["0", "3"]
    assert [row["native_fingerprint"] for row in suppressed] == ["1", "2"]
    assert reads == {first: 1, second: 1}
    # Operation-local source reads must not hide later source edits.
    first.write_text("api_token: your_token\n")
    assert _filter_known_noise([findings[-1]], tmp_path)[0] == []
    assert reads[first] == 2


def test_noise_filter_caches_missing_and_invalid_encoding_per_call(tmp_path, monkeypatch):
    from collections import Counter
    from pathlib import Path
    from ansibleguard.external.gitleaks import _filter_known_noise

    invalid = tmp_path / "invalid.yml"
    invalid.write_bytes(b"api_token: your_token\n\xff")
    findings = [{"File": file, "StartLine": 1, "RuleID": "generic-api-key"}
                for file in ["missing.yml", "invalid.yml", "missing.yml", "invalid.yml"]]
    reads, original = Counter(), Path.read_text

    def counted(path, *args, **kwargs):
        reads[path] += 1
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", counted)
    assert _filter_known_noise(findings, tmp_path) == (findings, [])
    assert reads == {tmp_path / "missing.yml": 1, invalid: 1}


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


def test_gitleaks_timeout_is_not_clean(tmp_path, monkeypatch):
    import subprocess
    from ansibleguard.external.gitleaks import scan_with_gitleaks

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            subprocess.TimeoutExpired(args[0], kwargs.get("timeout"))
        ),
    )

    result = scan_with_gitleaks(tmp_path, "/fake/gitleaks", timeout=0.01)

    assert result.status == "timeout"
    assert result.metadata["failure_category"] == "TIMEOUT"


def test_gitleaks_output_limit_is_not_clean(tmp_path, monkeypatch):
    import subprocess

    monkeypatch.setenv("ANSIBLEGUARD_PROVIDER_MAX_OUTPUT_BYTES", "10")

    def write_large_report(command, **kwargs):
        report_path = command[command.index("--report-path") + 1]
        with open(report_path, "w", encoding="utf-8") as stream:
            stream.write("12345678901")
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(subprocess, "run", write_large_report)

    from ansibleguard.external.gitleaks import scan_with_gitleaks
    result = scan_with_gitleaks(tmp_path, "/fake/gitleaks")

    assert result.status == "tool-error"
    assert result.metadata["failure_category"] == "OUTPUT_LIMIT"


def test_gitleaks_history_output_limit_is_not_clean(tmp_path, monkeypatch):
    import subprocess
    from ansibleguard.external.gitleaks import scan_git_range_with_gitleaks

    monkeypatch.setenv("ANSIBLEGUARD_PROVIDER_MAX_OUTPUT_BYTES", "10")

    def write_large_report(command, **kwargs):
        report_path = command[command.index("--report-path") + 1]
        with open(report_path, "w", encoding="utf-8") as stream:
            stream.write("12345678901")
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(subprocess, "run", write_large_report)

    result = scan_git_range_with_gitleaks(
        tmp_path, "/fake/gitleaks", "a" * 40, "b" * 40
    )

    assert result.status == "tool-error"
    assert result.metadata["failure_category"] == "OUTPUT_LIMIT"


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


def test_known_non_secret_gitleaks_artifacts_are_suppressed(tmp_path):
    from ansibleguard.external.gitleaks import _filter_known_noise

    (tmp_path / ".secrets.baseline").write_text("{}\n", encoding="utf-8")
    (tmp_path / "defaults.yml").write_text(
        "# For example:\n# api_token: example-value\n", encoding="utf-8"
    )
    (tmp_path / "dnscrypt.toml.j2").write_text(
        "minisign_key = 'public-verification-material'\n", encoding="utf-8"
    )
    (tmp_path / "vars.yml").write_text(
        "api_token: real-sensitive-value\n", encoding="utf-8"
    )
    (tmp_path / "example.sh").write_text(
        '# echo "-----BEGIN RSA PRIVATE KEY-----"\n', encoding="utf-8"
    )
    (tmp_path / "guide.md").write_text(
        'curl -H "X-Auth-Token: YOUR_TOKEN" https://example.invalid\n',
        encoding="utf-8",
    )
    (tmp_path / "example.env").write_text(
        "# Old plain text string\n# ADMIN_TOKEN=fixed-documentation-example\n",
        encoding="utf-8",
    )
    (tmp_path / "crypto.toml").write_text(
        '# Example for deterministic mode: key = "1234567890abcdef"\n',
        encoding="utf-8",
    )
    (tmp_path / "metadata.json").write_text(
        '{\n  "checksums": {\n'
        '    "templates/config.erb": "9878dbf34a4606d5ad613511a527d956"\n'
        "  }\n}\n",
        encoding="utf-8",
    )
    (tmp_path / "grafana.ini").write_text(
        "# default admin password\n"
        ";admin_password = admin\n"
        "# used for signing\n"
        ";secret_key = SW2YcwTIb9zpOOhoPsMm\n",
        encoding="utf-8",
    )
    findings = [
        {"File": ".secrets.baseline", "StartLine": 1, "RuleID": "generic-api-key"},
        {"File": "defaults.yml", "StartLine": 2, "RuleID": "generic-api-key"},
        {"File": "dnscrypt.toml.j2", "StartLine": 1, "RuleID": "generic-api-key"},
        {"File": "example.sh", "StartLine": 1, "RuleID": "private-key"},
        {"File": "guide.md", "StartLine": 1, "RuleID": "curl-auth-header"},
        {"File": "example.env", "StartLine": 2, "RuleID": "generic-api-key"},
        {"File": "crypto.toml", "StartLine": 1, "RuleID": "generic-api-key"},
        {"File": "metadata.json", "StartLine": 3, "RuleID": "generic-api-key"},
        {"File": "grafana.ini", "StartLine": 4, "RuleID": "generic-api-key"},
        {"File": "vars.yml", "StartLine": 1, "RuleID": "generic-api-key"},
    ]

    kept, suppressed = _filter_known_noise(findings, tmp_path)

    assert len(suppressed) == 9
    assert {item["reason"] for item in suppressed} >= {
        "known-secret-baseline-or-ignore-file",
        "documentation-placeholder",
        "checksum-value",
        "commented-private-key-marker",
    }
    assert all("Secret" not in item and "Match" not in item for item in suppressed)
    assert kept == [findings[-1]]


def test_scan_retains_redacted_suppression_evidence(tmp_path, monkeypatch):
    import json
    import subprocess
    from ansibleguard.external.gitleaks import scan_with_gitleaks

    source = tmp_path / "guide.md"
    source.write_text("token: YOUR_TOKEN\n", encoding="utf-8")

    def fake_run(command, **kwargs):
        report = command[command.index("--report-path") + 1]
        with open(report, "w", encoding="utf-8") as stream:
            json.dump([{
                "File": "guide.md", "StartLine": 1,
                "RuleID": "generic-api-key", "Secret": "must-not-survive",
                "Match": "token=must-not-survive",
            }], stream)
        return subprocess.CompletedProcess(command, 1, "", "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    result = scan_with_gitleaks(tmp_path, "/fake/gitleaks")

    assert result.findings == []
    assert result.metadata["suppressed_known_noise"] == 1
    assert result.suppressed_findings[0]["reason"] == "documentation-placeholder"
    assert "must-not-survive" not in json.dumps(result.suppressed_findings)


def test_v004_digest_uuid_and_kubernetes_noise_filters(tmp_path):
    from ansibleguard.external.gitleaks import _filter_known_noise

    (tmp_path / "vars.yml").write_text(
        f"artifact_sha256: {'a' * 64}\n"
        "trace_id: 123e4567-e89b-42d3-a456-426614174000\n"
        "api_token: live-token-material-X9z7\n",
        encoding="utf-8",
    )
    findings = [
        {
            "File": "vars.yml", "StartLine": 1, "RuleID": "generic-api-key",
            "Secret": "a" * 64,
        },
        {
            "File": "vars.yml", "StartLine": 2, "RuleID": "generic-api-key",
            "Secret": "123e4567-e89b-42d3-a456-426614174000",
        },
        {
            "File": "secret.yml", "StartLine": 1,
            "RuleID": "kubernetes-secret-yaml", "Secret": "redacted",
        },
        {
            "File": "vars.yml", "StartLine": 3, "RuleID": "generic-api-key",
            "Secret": "live-token-material-X9z7",
        },
    ]
    kept, suppressed = _filter_known_noise(findings, tmp_path)
    assert kept == [findings[-1]]
    assert {item["reason"] for item in suppressed} == {
        "cryptographic-digest-not-api-key",
        "uuid-not-api-key",
        "disabled-rule-not-ansible-signal",
    }


def test_unlabelled_hex_and_uuid_values_are_retained_for_secret_review(tmp_path):
    from ansibleguard.external.gitleaks import _filter_known_noise

    (tmp_path / "vars.yml").write_text(
        f"api_token: {'a' * 64}\n"
        "api_key: 123e4567-e89b-42d3-a456-426614174000\n",
        encoding="utf-8",
    )
    findings = [
        {"File": "vars.yml", "StartLine": 1, "RuleID": "generic-api-key", "Secret": "a" * 64},
        {"File": "vars.yml", "StartLine": 2, "RuleID": "generic-api-key", "Secret": "123e4567-e89b-42d3-a456-426614174000"},
    ]

    assert _filter_known_noise(findings, tmp_path) == (findings, [])


def test_generic_key_integrity_context_is_suppressed_but_real_token_is_kept(tmp_path):
    from ansibleguard.external.gitleaks import _filter_known_noise

    (tmp_path / "vars.yml").write_text(
        "artifact_sha256: release-signature-X9z7\n"
        "api_token: live-token-material-X9z7\n",
        encoding="utf-8",
    )
    findings = [
        {
            "File": "vars.yml", "StartLine": 1, "RuleID": "generic-api-key",
            "Secret": "release-signature-X9z7",
        },
        {
            "File": "vars.yml", "StartLine": 2, "RuleID": "generic-api-key",
            "Secret": "live-token-material-X9z7",
        },
    ]

    kept, suppressed = _filter_known_noise(findings, tmp_path)

    assert kept == [findings[1]]
    assert suppressed[0]["reason"] == "integrity-identifier-not-api-key"
