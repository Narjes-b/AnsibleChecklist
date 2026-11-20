import csv
import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from scripts.study_pipeline import (
    aggregate,
    build_identity,
    compare_runs,
    load_config,
    preflight,
    prepare,
    read_csv,
    report,
    run_dir,
    validate,
)
import scripts.study_pipeline as study_pipeline


def _git(args, cwd):
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout.strip()


def _repository(path):
    path.mkdir(parents=True)
    _git(["init"], path)
    _git(["config", "user.name", "Pipeline Test"], path)
    _git(["config", "user.email", "pipeline@example.com"], path)
    (path / "tasks.yml").write_text("- name: Test\n  debug:\n    msg: ok\n", encoding="utf-8")
    _git(["add", "."], path)
    _git(["commit", "-m", "fixture"], path)
    return _git(["rev-parse", "HEAD"], path)


def _write_config(tmp_path, manifest, classifications, expected=1, require_lint=True):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump({
        "run": {
            "id": "test-run", "profile": "technical-full",
            "workers": 1, "resume": True,
        },
        "tool": {
            "mode": "current-worktree", "version": __import__("ansibleguard").__version__,
            # CI must use the interpreter running pytest rather than a
            # developer-specific repository-local virtualenv.
            "git_ref": "HEAD", "python": sys.executable,
            "allow_dirty": True,
        },
        "repositories": {
            "manifest": str(manifest), "file_manifests_dir": str(classifications),
            "expected_count": expected,
        },
        "output": {"root": str(tmp_path / "runs")},
        "providers": {"require_ansible_lint": require_lint, "require_gitleaks": True},
        "report": {"formats": ["svg"], "top_rules": 10, "top_repositories": 10},
    }, sort_keys=False), encoding="utf-8")
    return load_config(config_path)


def _classification(path, project, sha):
    output = path / f"{project.replace('/', '__')}__{sha}.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "path,loc,parse_status,document_type,file_class,ansible_artifact_kind,included,primary_ansibleguard_cohort,paper_comparable_cohort\n"
        "tasks.yml,3,parsed,tasks,production_ansible,tasks,true,true,true\n",
        encoding="utf-8",
    )
    return output


def _manifest(path, project, repository, sha):
    path.write_text(
        "project,repository_path,commit_sha,status\n"
        f"{project},{repository},{sha},collected\n",
        encoding="utf-8",
    )


def _snapshot(
    config, project, sha, occurrence_id="one", category="security",
    provider="ansibleguard", ansible_lint_status="completed",
):
    path = run_dir(config) / "repositories" / project.replace("/", "__") / sha
    (path / "raw").mkdir(parents=True, exist_ok=True)
    (path / "canonical").mkdir()
    (path / "summary").mkdir()
    with (run_dir(config) / "input" / "repositories.csv").open(newline="", encoding="utf-8") as stream:
        classification_hash = next(csv.DictReader(stream))["classification_manifest_sha256"]
    (path / "run_metadata.json").write_text(json.dumps({
        "profile": {"name": "technical-full"},
        "file_selection": {"manifest_sha256": classification_hash},
        "source": {"resolved_sha": sha},
        "tools": {"ansible_lint": ansible_lint_status, "gitleaks": "completed"},
        "analysis_scope": {"internal": {"processed_files": 1, "structurally_analyzed_files": 1}},
        "file_states": {"analyzed": 1},
    }), encoding="utf-8")
    (path / "raw" / "findings.json").write_text(json.dumps({"items": [{
        "finding_id": f"finding-{occurrence_id}", "provider": "ansibleguard",
        "rule_id": "hardcoded-credentials", "file": "tasks.yml", "line": 2,
        "severity": "error", "message": "credential",
    }]}), encoding="utf-8")
    (path / "canonical" / "occurrences.json").write_text(json.dumps({"items": [{
        "occurrence_id": occurrence_id, "concept_id": "hardcoded-secret",
        "semantic_key": f"semantic-{occurrence_id}", "native_rules": ["ansibleguard/hardcoded-credentials"],
        "file": "tasks.yml", "line": 2, "scan_mode": "source", "severity": "error",
        "message": "credential", "canonical_provider": provider,
        "finding_category": category, "semantic_status": "CONFIRMED", "confidence": "high",
        "resolution_status": "PROVEN_EXPOSED", "resolution_scope": "task-static",
        "uncertainty_sources": [],
        "resolution_evidence": {"proved": ["direct_display"], "blockers": []},
    }]}), encoding="utf-8")
    (path / "summary" / "summary.csv").write_text(
        "file,parse_status,document_type,structural_status\n"
        "tasks.yml,parsed,tasks,analyzed\n", encoding="utf-8",
    )
    (path / "summary" / "diagnostics.json").write_text(
        json.dumps({"items": []}), encoding="utf-8"
    )
    return path


def test_prepare_and_preflight_accept_any_manifest_count(tmp_path):
    repository = tmp_path / "repository"
    sha = _repository(repository)
    manifest = tmp_path / "manifest.csv"
    project = "example/role"
    _manifest(manifest, project, repository, sha)
    classifications = tmp_path / "classifications"
    _classification(classifications, project, sha)
    config = _write_config(tmp_path, manifest, classifications)

    prepared = prepare(config)
    checks = preflight(config)

    assert prepared["repository_count"] == 1
    assert len(checks) == 1
    assert checks[0]["status"] == "passed"
    assert (run_dir(config) / "input" / "repositories.csv").is_file()


def test_v007_full_config_uses_active_interpreter_and_tracked_population():
    config = load_config(Path("study/configs/v007-207.yaml"))

    assert config["run"]["id"] == "v007-full-repro-2026"
    assert config["run"]["workers"] == 4
    assert "python" not in config["tool"]
    assert config["repositories"]["manifest"] == "study/manifests/github-v2-final-eligible.csv"
    rows = study_pipeline.selected_rows(config)
    assert len(rows) == 207
    assert all("study/cache/v007-full-repro-2026/repositories" in row["repository_path"] for row in rows)
    # The frozen v0.0.7 config names a tool version this worktree no longer has.
    assert str(config["tool"]["version"]) == "0.0.7"
    # The active virtualenv executable must be preserved, not resolved through
    # its symlink to a base interpreter that lacks the installed package.
    current = load_config(Path("study/configs/v0071-207.yaml"))
    assert current["run"]["id"] == "v0071-full-2026" and current["run"]["workers"] == 4
    assert current["repositories"]["manifest"] == config["repositories"]["manifest"]
    current["tool"]["allow_dirty"] = True
    assert Path(build_identity(current)["python"]) == Path(sys.executable)


def test_validate_aggregate_and_report_create_complete_artifacts(tmp_path):
    repository = tmp_path / "repository"
    sha = _repository(repository)
    manifest = tmp_path / "manifest.csv"
    project = "example/role"
    _manifest(manifest, project, repository, sha)
    classifications = tmp_path / "classifications"
    _classification(classifications, project, sha)
    config = _write_config(tmp_path, manifest, classifications)
    prepare(config)
    _snapshot(config, project, sha)

    validation = validate(config)
    summary = aggregate(config)
    report_path = report(config)

    assert validation["status"] == "passed"
    assert summary == {
        **summary,
        "repositories": 1,
        "raw_findings": 1,
        "canonical_occurrences": 1,
        "categories": 1,
        "rules": 1,
    }
    aggregate_dir = run_dir(config) / "aggregate"
    assert (aggregate_dir / "repository-rule-matrix.csv").is_file()
    assert (aggregate_dir / "concept-summary.csv").is_file()
    assert (aggregate_dir / "concept-summary-internal.csv").is_file()
    assert (aggregate_dir / "resolution-summary.csv").is_file()
    assert (aggregate_dir / "provider-health.csv").is_file()
    assert (run_dir(config) / "charts" / "findings-by-category.svg").is_file()
    assert (run_dir(config) / "charts" / "top-internal-concepts.svg").is_file()
    occurrence = read_csv(aggregate_dir / "all-canonical-occurrences.csv")[0]
    assert occurrence["resolution_status"] == "PROVEN_EXPOSED"
    assert occurrence["resolution_scope"] == "task-static"
    assert json.loads(occurrence["resolution_evidence"])["proved"] == [
        "direct_display"
    ]
    assert "example/role" in report_path.read_text(encoding="utf-8")


def test_compare_requires_same_population_and_reports_semantic_move(tmp_path):
    repository = tmp_path / "repository"
    sha = _repository(repository)
    manifest = tmp_path / "manifest.csv"
    project = "example/role"
    _manifest(manifest, project, repository, sha)
    classifications = tmp_path / "classifications"
    _classification(classifications, project, sha)

    base = _write_config(tmp_path, manifest, classifications)
    prepare(base)
    _snapshot(base, project, sha, occurrence_id="base")
    validate(base)
    aggregate(base)

    candidate_path = tmp_path / "candidate.yaml"
    candidate_payload = yaml.safe_load(Path(base["_config_path"]).read_text(encoding="utf-8"))
    candidate_payload["run"]["id"] = "candidate-run"
    candidate_path.write_text(yaml.safe_dump(candidate_payload, sort_keys=False), encoding="utf-8")
    candidate = load_config(candidate_path)
    prepare(candidate)
    snapshot = _snapshot(candidate, project, sha, occurrence_id="candidate")
    occurrence_path = snapshot / "canonical" / "occurrences.json"
    occurrence = json.loads(occurrence_path.read_text(encoding="utf-8"))
    occurrence["items"][0]["semantic_key"] = "semantic-base"
    occurrence_path.write_text(json.dumps(occurrence), encoding="utf-8")
    validate(candidate)
    aggregate(candidate)

    result = compare_runs(run_dir(base), run_dir(candidate), tmp_path / "comparison")

    assert result["status_counts"] == {"moved": 1}
    assert (tmp_path / "comparison" / "COMPARISON_REPORT.md").is_file()


def test_prepare_rejects_reusing_run_id_for_another_tool_commit(
    tmp_path, monkeypatch
):
    repository = tmp_path / "repository"
    sha = _repository(repository)
    manifest = tmp_path / "manifest.csv"
    project = "example/role"
    _manifest(manifest, project, repository, sha)
    classifications = tmp_path / "classifications"
    _classification(classifications, project, sha)
    config = _write_config(tmp_path, manifest, classifications)
    prepare(config)

    original = study_pipeline.build_identity

    def changed_identity(value):
        identity = original(value)
        identity["commit_sha"] = "f" * 40
        return identity

    monkeypatch.setattr(study_pipeline, "build_identity", changed_identity)

    with pytest.raises(ValueError, match="already belongs to tool commit"):
        prepare(config)


def test_partial_optional_provider_is_explicitly_excluded_from_comparisons(tmp_path):
    repository = tmp_path / "repository"
    sha = _repository(repository)
    manifest = tmp_path / "manifest.csv"
    project = "example/role"
    _manifest(manifest, project, repository, sha)
    classifications = tmp_path / "classifications"
    _classification(classifications, project, sha)
    config = _write_config(
        tmp_path, manifest, classifications, require_lint=False
    )
    prepare(config)
    _snapshot(
        config, project, sha, provider="ansible-lint",
        ansible_lint_status="partial",
    )

    validation = validate(config)
    summary = aggregate(config)

    assert validation["status"] == "passed"
    assert validation["publication_ready"] is False
    assert summary["provider_comparable_occurrences"] == 0
    assert summary["excluded_incomplete_provider_occurrences"] == 1


def test_current_flat_output_layout_is_backward_compatible(tmp_path):
    repository = tmp_path / "repository"
    sha = _repository(repository)
    manifest = tmp_path / "manifest.csv"
    project = "example/role"
    _manifest(manifest, project, repository, sha)
    classifications = tmp_path / "classifications"
    _classification(classifications, project, sha)
    config = _write_config(tmp_path, manifest, classifications)
    prepare(config)
    snapshot = _snapshot(config, project, sha)
    (snapshot / "raw" / "findings.json").replace(snapshot / "findings.json")
    (snapshot / "canonical" / "occurrences.json").replace(snapshot / "occurrences.json")

    validation = validate(config)
    summary = aggregate(config)

    assert validation["status"] == "passed"
    assert summary["canonical_occurrences"] == 1
    assert summary["internal_source_occurrences"] == 1


def test_review_findings_are_separate_from_static_source_population(tmp_path):
    repository = tmp_path / "repository"
    sha = _repository(repository)
    manifest = tmp_path / "manifest.csv"
    project = "example/role"
    _manifest(manifest, project, repository, sha)
    classifications = tmp_path / "classifications"
    _classification(classifications, project, sha)
    config = _write_config(tmp_path, manifest, classifications)
    prepare(config)
    snapshot = _snapshot(config, project, sha)
    occurrence_path = snapshot / "canonical" / "occurrences.json"
    payload = json.loads(occurrence_path.read_text(encoding="utf-8"))
    payload["items"][0].update({
        "concept_id": "missing-release-note",
        "native_rules": ["ansibleguard/missing-release-note"],
    })
    occurrence_path.write_text(json.dumps(payload), encoding="utf-8")

    summary = aggregate(config)

    assert summary["review_occurrences"] == 1
    assert summary["internal_source_occurrences"] == 0
    assert summary["provider_comparable_occurrences"] == 0
    assert len(read_csv(run_dir(config) / "aggregate" / "all-review-occurrences.csv")) == 1


def test_aggregate_rule_uses_canonical_provider_namespace():
    item = {
        "canonical_provider": "ansibleguard",
        "native_rules": [
            "ansible-lint/ignore-errors",
            "ansibleguard/silent-error-suppression",
        ],
    }
    assert study_pipeline._native_rule(item) == "ansibleguard/silent-error-suppression"

    external = {
        "canonical_provider": "ansible-lint",
        "native_rules": ["ansibleguard/silent-error-suppression", "ansible-lint/ignore-errors"],
    }
    assert study_pipeline._native_rule(external) == "ansible-lint/ignore-errors"


def test_provider_comparable_population_requires_every_provider_complete(tmp_path):
    repository = tmp_path / "repository"
    sha = _repository(repository)
    manifest = tmp_path / "manifest.csv"
    project = "example/role"
    _manifest(manifest, project, repository, sha)
    classifications = tmp_path / "classifications"
    _classification(classifications, project, sha)
    config = _write_config(tmp_path, manifest, classifications, require_lint=False)
    prepare(config)
    _snapshot(config, project, sha, provider="ansibleguard", ansible_lint_status="partial")

    summary = aggregate(config)

    # The internal finding stays in the internal population ...
    assert summary["internal_source_occurrences"] == 1
    # ... but a repository without complete ansible-lint evidence is a missing
    # observation for cross-provider tables, not a zero.
    assert summary["provider_comparable_occurrences"] == 0
    rows = read_csv(run_dir(config) / "aggregate" / "category-summary-provider-comparable.csv")
    assert all(int(row["eligible_repositories"]) == 0 for row in rows)
