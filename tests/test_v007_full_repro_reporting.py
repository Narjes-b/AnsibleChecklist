import csv
from pathlib import Path

from scripts.v007_full_repro import _charts, _tables


def _write_csv(path: Path, rows: list[dict], fields: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = fields or list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def _report_fixture(destination: Path) -> None:
    aggregate = destination / "aggregate"
    status = destination / "status"
    projects = ["example/complete", "example/partial", "example/timeout"]
    _write_csv(aggregate / "all-canonical-occurrences.csv", [
        {"project": projects[0], "occurrence_id": "one", "provider": "ansibleguard"},
        {"project": projects[0], "occurrence_id": "two", "provider": "ansibleguard"},
    ])
    _write_csv(aggregate / "all-raw-findings.csv", [
        {"project": projects[0], "provider": "ansibleguard", "rule_id": "missing-tags"},
        {"project": projects[0], "provider": "ansibleguard", "rule_id": "missing-tags"},
    ])
    _write_csv(aggregate / "repository-summary.csv", [
        {"project": projects[0], "commit_sha": "a" * 40, "selected_files": 2, "selected_loc": 20, "raw_findings": 2, "canonical_occurrences": 2, "canonical_per_1000_loc": 100},
        {"project": projects[1], "commit_sha": "b" * 40, "selected_files": 1, "selected_loc": 10, "raw_findings": 0, "canonical_occurrences": 0, "canonical_per_1000_loc": 0},
        {"project": projects[2], "commit_sha": "c" * 40, "selected_files": 3, "selected_loc": 30, "raw_findings": 0, "canonical_occurrences": 0, "canonical_per_1000_loc": 0},
        {"project": "__ALL__", "commit_sha": "", "selected_files": 6, "selected_loc": 60, "raw_findings": 2, "canonical_occurrences": 2, "canonical_per_1000_loc": 0},
    ])
    _write_csv(aggregate / "all-internal-source-occurrences.csv", [
        {"project": projects[0], "provider": "ansibleguard", "source_population": "production_ansible", "rule_id": "ansibleguard/missing-tags", "certainty": "CONFIRMED", "confidence": "high", "actionability": "direct-fix", "severity": "warning"},
        {"project": projects[0], "provider": "ansibleguard", "source_population": "production_ansible", "rule_id": "ansibleguard/missing-tags", "certainty": "UNCERTAIN", "confidence": "low", "actionability": "review", "severity": "note"},
    ])
    _write_csv(aggregate / "rule-summary-internal.csv", [
        {"rule_id": "ansibleguard/missing-tags", "findings": 2, "repositories_affected": 1, "repository_prevalence_percent": 50, "median_per_repository": 2},
    ])
    _write_csv(aggregate / "provider-summary.csv", [
        {"provider": "ansibleguard", "findings": 2},
    ])
    _write_csv(status / "validation.csv", [
        {"project": projects[0], "status": "complete", "ansible_lint_status": "completed", "gitleaks_status": "completed"},
        {"project": projects[1], "status": "partial", "ansible_lint_status": "partial", "gitleaks_status": "completed"},
        {"project": projects[2], "status": "failed", "ansible_lint_status": "missing", "gitleaks_status": "missing"},
    ])
    _write_csv(status / "repository-status.csv", [
        {"project": projects[0], "status": "completed", "duration_seconds": 5, "error": ""},
        {"project": projects[1], "status": "completed", "duration_seconds": 4, "error": ""},
        {"project": projects[2], "status": "timeout", "duration_seconds": 1800, "error": "timed out"},
    ])


def test_reporting_uses_internal_static_population_and_preserves_missing_results(tmp_path):
    _report_fixture(tmp_path)

    data = _tables(tmp_path, {"run": {"profile": "technical-full"}})

    rule = data["findings-by-rule.csv"][0]
    assert rule["rule_id"] == "ansibleguard/missing-tags"
    assert rule["canonical_occurrences"] == 2
    assert rule["raw_ansibleguard_findings"] == 2
    rows = {row["repository"]: row for row in data["repository-execution-status.csv"]}
    assert rows["example/timeout"]["canonical_occurrences"] == ""
    repository_rows = {row["project"]: row for row in data["findings-by-repository.csv"]}
    assert repository_rows["example/partial"]["internal_source_occurrences"] == 0
    assert repository_rows["example/timeout"]["internal_source_occurrences"] == ""
    assert len(data["findings-density.csv"]) == 2
    assert {row["actionability"] for row in data["actionability.csv"]} == {"direct-fix", "review"}
    assert sum(row["repositories"] for row in data["provider-completeness.csv"]) == 3
    assert data["external-tool-overlap.csv"][0]["mapped_overlap"] == ""

    chart_paths = _charts(tmp_path, data, {"report": {"top_rules": 5}})
    assert len(chart_paths) == 17
    assert (tmp_path / "charts" / "svg" / "11-actionability-distribution.svg").is_file()
    assert "overlap is not estimated" in (tmp_path / "charts" / "svg" / "16-external-tool-overlap.svg").read_text(encoding="utf-8")
    assert not (tmp_path / "charts" / "data" / "10-uncertain-vs-actionable.csv").exists()
    assert not (tmp_path / "tables" / "uncertain-vs-actionable.csv").exists()
