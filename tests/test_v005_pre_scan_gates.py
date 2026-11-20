import csv
import json
from pathlib import Path
import subprocess

from ansibleguard import __version__


def test_validation_readiness_uses_package_version():
    from scripts.audit_validation_readiness import build_audit

    assert build_audit(None, None)["tool_version"] == __version__


def test_compare_script_accepts_strict_policy(tmp_path):
    from scripts.compare_pr_results import main

    base = tmp_path / "base.json"
    head = tmp_path / "head.json"
    output = tmp_path / "decision.json"
    base.write_text("[]", encoding="utf-8")
    head.write_text("[]", encoding="utf-8")

    assert main([
        str(base),
        str(head),
        "-o",
        str(output),
        "--policy",
        "strict",
    ]) == 0
    assert json.loads(output.read_text(encoding="utf-8"))["policy"]["mode"] == "strict"


def test_v005_research_runner_uses_isolated_default_destinations():
    import scripts.run_v005_research_scan as runner

    assert runner.DEFAULT_CLASSIFICATIONS == Path(
        "study/manifests/file-classification-v005"
    )
    assert runner.DEFAULT_SNAPSHOTS == Path(
        "study/snapshots/technical-full-v005"
    )
    assert runner.DEFAULT_LOGS == Path("study/logs/technical-full-v005")
    assert runner.DEFAULT_OUTPUT == Path(
        "study/results/v005/all-repositories-summary.csv"
    )


def test_v005_research_runner_records_unexpected_repository_exception(
    tmp_path, monkeypatch
):
    import scripts.run_v005_research_scan as runner

    manifest = tmp_path / "frozen.csv"
    manifest.write_text(
        "project,commit_sha,repository_path,status\n"
        "example/repo,abc123,/does/not/matter,collected\n",
        encoding="utf-8",
    )
    classifications = tmp_path / "classifications"
    classifications.mkdir()
    expected_classification = (
        classifications / "example__repo__abc123.csv"
    )
    expected_classification.write_text("placeholder\n", encoding="utf-8")

    def fail_repository(*_args, **_kwargs):
        raise subprocess.CalledProcessError(
            128, ["git", "rev-parse", "HEAD"]
        )

    monkeypatch.setattr(runner, "run_row", fail_repository)
    output = tmp_path / "summary.csv"

    assert runner.main([
        str(manifest),
        "--output",
        str(output),
        "--output-root",
        str(tmp_path / "snapshots"),
        "--logs-dir",
        str(tmp_path / "logs"),
        "--file-manifests-dir",
        str(classifications),
        "--jobs",
        "1",
    ]) == 1

    with output.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    assert rows[0]["project"] == "example/repo"
    assert rows[0]["scan_status"] == "failed"
    assert "CalledProcessError" in rows[0]["scan_error"]
    assert rows[-1]["project"] == "__ALL__"

    assert runner.main([
        str(manifest),
        "--output", str(tmp_path / "allowed.csv"),
        "--output-root", str(tmp_path / "snapshots-allowed"),
        "--logs-dir", str(tmp_path / "logs-allowed"),
        "--file-manifests-dir", str(classifications),
        "--jobs", "1",
        "--allow-failed-repositories",
    ]) == 0
