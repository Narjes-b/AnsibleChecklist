import json
import subprocess

import pytest

from ansibleguard.cli import analyze_path
from ansibleguard.file_manifest import (
    FileManifestError,
    classify_repository,
    write_file_manifest,
)
from ansibleguard.profiles import (
    ALL_RULES,
    EXTERNAL_RULES,
    EXTENDED_ANSIBLE,
    EXTENDED_RULES,
    RESEARCH_CORE,
    RESEARCH_CORE_RULES,
    REVIEW_RANGE,
    REVIEW_RULES,
    SNAPSHOT_RULES,
    SNAPSHOT_SOURCE,
    filter_profile_findings,
    profile_metadata,
    rule_family,
)


def _must_not_run(*args, **kwargs):
    raise AssertionError("component excluded by the selected profile was executed")


def _git(repository, *args):
    return subprocess.run(
        ["git", *args],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def test_every_catalog_rule_has_one_research_family():
    families = RESEARCH_CORE_RULES | EXTENDED_RULES | REVIEW_RULES | EXTERNAL_RULES
    assert families == ALL_RULES
    assert not (RESEARCH_CORE_RULES & EXTENDED_RULES)
    assert not (SNAPSHOT_RULES & REVIEW_RULES)
    assert not (SNAPSHOT_RULES & EXTERNAL_RULES)
    assert all(rule_family(rule_id) for rule_id in ALL_RULES)


def test_profile_filters_are_explicit_and_disjoint():
    findings = [
        {"rule_id": "complex-expression"},
        {"rule_id": "unguarded-variable"},
        {"rule_id": "missing-release-note"},
        {"rule_id": "ansible-lint-issue"},
    ]
    assert filter_profile_findings(findings, RESEARCH_CORE) == [findings[0]]
    assert filter_profile_findings(findings, EXTENDED_ANSIBLE) == [findings[1]]
    assert filter_profile_findings(findings, REVIEW_RANGE) == [findings[2]]
    assert filter_profile_findings(findings, SNAPSHOT_SOURCE) == findings[:2]


def test_snapshot_profile_skips_external_and_review_execution(tmp_path, monkeypatch):
    target = tmp_path / "project"
    tasks = target / "roles" / "web" / "tasks"
    tasks.mkdir(parents=True)
    (tasks / "main.yml").write_text("", encoding="utf-8")
    monkeypatch.setattr(
        "ansibleguard.external.gitleaks.scan_with_gitleaks", _must_not_run
    )
    monkeypatch.setattr(
        "ansibleguard.external.ansible_lint.scan_with_ansible_lint", _must_not_run
    )
    monkeypatch.setattr(
        "ansibleguard.detectors.review_metadata.detect_project_review_smells",
        _must_not_run,
    )

    output = tmp_path / "output"
    with pytest.raises(FileManifestError, match="requires --file-manifest"):
        analyze_path(target, output, profile=SNAPSHOT_SOURCE)
    manifest = write_file_manifest(
        classify_repository(target, "openstack/example", "a" * 40),
        tmp_path / "files.csv",
    )
    run = analyze_path(
        target, output, file_manifest=manifest, profile=SNAPSHOT_SOURCE
    )

    assert run["profile"] == SNAPSHOT_SOURCE
    assert run["processed"] == 1
    findings = json.loads((output / "findings.json").read_text(encoding="utf-8"))
    assert {finding["rule_id"] for finding in findings} == {"empty-abstraction"}
    assert json.loads((output / "review_metrics.json").read_text()) == {}
    metadata = json.loads((output / "run_metadata.json").read_text())
    assert metadata["profile"]["name"] == SNAPSHOT_SOURCE
    assert metadata["tools"] == {
        "gitleaks": "not-requested",
        "ansible_lint": "not-requested",
    }
    assert metadata["profile"]["rules_sha256"] == profile_metadata(
        SNAPSHOT_SOURCE
    )["rules_sha256"]


def test_review_range_processes_git_evidence_without_source_or_external_tools(
    tmp_path, monkeypatch
):
    repository = tmp_path / "repository"
    repository.mkdir()
    _git(repository, "init", "-q")
    _git(repository, "config", "user.name", "Profile Test")
    _git(repository, "config", "user.email", "profile@example.com")
    source = repository / "roles" / "web" / "tasks" / "main.yml"
    source.parent.mkdir(parents=True)
    source.write_text("- debug:\n    msg: first\n", encoding="utf-8")
    _git(repository, "add", ".")
    _git(repository, "commit", "-q", "-m", "Initial state")
    source.write_text("- debug:\n    msg: changed\n", encoding="utf-8")
    _git(repository, "add", ".")
    _git(repository, "commit", "-q", "-m", "Fix role behavior")
    monkeypatch.setattr(
        "ansibleguard.external.gitleaks.scan_with_gitleaks", _must_not_run
    )
    monkeypatch.setattr(
        "ansibleguard.external.ansible_lint.scan_with_ansible_lint", _must_not_run
    )

    output = tmp_path / "review-output"
    run = analyze_path(repository, output, profile=REVIEW_RANGE)

    assert run["discovered"] == 1
    assert run["processed"] == 0
    assert run["structurally_analyzed"] == 0
    findings = json.loads((output / "findings.json").read_text(encoding="utf-8"))
    assert findings
    assert {finding["rule_id"] for finding in findings} <= REVIEW_RULES
    assert "missing-release-note" in {finding["rule_id"] for finding in findings}
    metadata = json.loads((output / "run_metadata.json").read_text())
    assert metadata["profile"]["review_analysis"] is True
    assert metadata["profile"]["source_analysis"] is False
