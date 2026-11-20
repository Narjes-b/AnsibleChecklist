import csv
import json

from scripts.scan_and_summarize_repositories import (
    resolve_jobs,
    run_repository_jobs,
    summarize_snapshot,
    write_summary,
)


def _write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def test_summarizes_files_findings_categories_and_symbols(tmp_path):
    classification = tmp_path / "classification.csv"
    classification.write_text(
        "project,commit_sha,path,file_class,document_type,parse_status,loc,"
        "ansible_artifact_kind,primary_ansibleguard_cohort,"
        "paper_comparable_cohort,included\n"
        "example/role,abc,tasks/main.yml,production_ansible,tasks,parsed,10,"
        "tasks,true,true,true\n"
        "example/role,abc,defaults/main.yml,production_ansible,vars,parsed,5,"
        "defaults,true,false,true\n"
        "example/role,abc,.github/workflow.yml,ci_yaml,vars,parsed,7,vars,"
        "false,false,false\n",
        encoding="utf-8",
    )
    snapshot = tmp_path / "snapshot"
    _write_json(
        snapshot / "run_metadata.json",
        {
            "profile": {"name": "technical-full"},
            "tools": {"ansible_lint": "completed", "gitleaks": "completed"},
            "analysis_scope": {
                "internal": {
                    "processed_files": 2,
                    "structurally_analyzed_files": 1,
                }
            },
            "file_states": {"analyzed": 1, "skipped": 1},
            "symbol_index": {
                "definition_count": 4,
                "variable_count": 3,
                "kinds": {"register": 2, "vars-file": 2},
            },
        },
    )
    _write_json(
        snapshot / "raw" / "findings.json",
        {
            "items": [
                {"provider": "ansibleguard"},
                {"provider": "ansible-lint"},
                {"provider": "ansibleguard"},
            ]
        },
    )
    _write_json(
        snapshot / "canonical" / "occurrences.json",
        {
            "items": [
                {
                    "concept_id": "missing-handler",
                    "severity": "error",
                    "file": "tasks/main.yml",
                },
                {
                    "concept_id": "missing-tags",
                    "severity": "note",
                    "file": "tasks/main.yml",
                    "semantic_status": "UNCERTAIN",
                },
            ]
        },
    )
    _write_json(
        snapshot / "summary" / "diagnostics.json",
        {"items": [{"status": "analysis-error"}]},
    )
    (snapshot / "summary" / "summary.csv").write_text(
        "file,parse_status,document_type,structural_status\n"
        "tasks/main.yml,parsed,tasks,analyzed\n"
        "defaults/main.yml,parsed,vars,skipped\n"
        "external.yml,not-applicable,ansible-lint,not-applicable\n",
        encoding="utf-8",
    )

    row = summarize_snapshot(
        {
            "project": "example/role",
            "commit_sha": "abc",
            "repository_path": "/repos/example/role",
        },
        snapshot,
        classification,
        "completed",
    )

    assert row["manifest_yaml_files"] == 3
    assert row["manifest_yaml_loc"] == 22
    assert row["selected_files"] == 2
    assert row["selected_loc"] == 15
    assert row["selected_artifact_tasks"] == 1
    assert row["selected_artifact_defaults"] == 1
    assert row["selected_document_vars"] == 1
    assert row["processed_files"] == 2
    assert row["file_state_analyzed"] == 1
    assert row["scan_parse_parsed"] == 2
    assert row["scan_document_tasks"] == 1
    assert row["scan_document_vars"] == 1
    assert row["diagnostic_status_analysis_error"] == 1
    assert row["raw_findings"] == 3
    assert row["canonical_occurrences"] == 2
    assert row["canonical_uncertain_occurrences"] == 1
    assert row["canonical_non_uncertain_occurrences"] == 1
    assert row["finding_semantic_status_uncertain"] == 1
    assert row["finding_semantic_status_not_applicable"] == 1
    assert row["confirmed_finding_concept_missing_handler"] == 1
    assert "confirmed_finding_concept_missing_tags" not in row
    assert row["provider_ansibleguard"] == 2
    assert row["severity_error"] == 1
    assert row["finding_category_correctness"] == 1
    assert row["finding_category_style"] == 1
    assert row["finding_concept_missing_handler"] == 1
    assert row["finding_artifact_tasks"] == 2
    assert row["symbol_variables"] == 3
    assert row["symbol_kind_register"] == 2


def test_writes_per_repository_rows_and_numeric_total(tmp_path):
    rows = [
        {
            "project": "one/role",
            "scan_status": "completed",
            "repositories": 1,
            "selected_files": 2,
            "canonical_occurrences": 3,
            "finding_category_style": 2,
        },
        {
            "project": "two/role",
            "scan_status": "skipped",
            "repositories": 1,
            "selected_files": 4,
            "canonical_occurrences": 5,
            "finding_category_security": 1,
        },
    ]
    output = tmp_path / "summary.csv"

    write_summary(rows, output)

    with output.open(newline="", encoding="utf-8") as stream:
        written = list(csv.DictReader(stream))
    assert [row["project"] for row in written] == [
        "one/role",
        "two/role",
        "__ALL__",
    ]
    assert written[-1]["repositories"] == "2"
    assert written[-1]["selected_files"] == "6"
    assert written[-1]["canonical_occurrences"] == "8"
    assert written[-1]["finding_category_style"] == "2"
    assert written[-1]["finding_category_security"] == "1"


def test_auto_jobs_respects_cpu_memory_and_workload():
    assert resolve_jobs(
        "auto", 20, 1024, cpu_count=8, memory_mb=3500
    ) == 3
    assert resolve_jobs(
        "auto", 2, 1024, cpu_count=8, memory_mb=32000
    ) == 2
    assert resolve_jobs("4", 2) == 2


def test_repository_jobs_return_input_order_independent_of_completion_order():
    items = [3, 1, 2]

    results = run_repository_jobs(
        items,
        3,
        lambda value: {"input": value, "result": value * 10},
    )

    assert results == [
        {"input": 3, "result": 30},
        {"input": 1, "result": 10},
        {"input": 2, "result": 20},
    ]


def test_one_and_many_repository_workers_return_identical_results():
    items = [
        {"repository": "c", "occurrences": [3, 1]},
        {"repository": "a", "occurrences": []},
        {"repository": "b", "occurrences": [2]},
    ]

    def canonical(item):
        return {
            "repository": item["repository"],
            "occurrences": sorted(item["occurrences"]),
        }

    assert run_repository_jobs(items, 1, canonical) == run_repository_jobs(
        items, 4, canonical
    )
