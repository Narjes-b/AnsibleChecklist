import json
import hashlib

from ansibleguard.cli import _annotate_finding_populations, analyze_path
from ansibleguard.external.gitleaks import ToolResult
from ansibleguard.file_manifest import classify_repository, write_file_manifest
from ansibleguard.analysis_context import build_repository_analysis_context
from ansibleguard.document import PARSER_CACHE_VERSION


def test_parse_failure_still_emits_gitleaks_finding(tmp_path, monkeypatch):
    target = tmp_path / "project"
    target.mkdir()
    broken = target / "vars.yaml"
    broken.write_text('password: "AKIAIOSFODNN7EXAMPLE"\nbroken: [yaml\n')

    fake = ToolResult(
        "completed",
        [{"File": "vars.yaml", "StartLine": 1, "Description": "AWS key"}],
    )
    monkeypatch.setattr(
        "ansibleguard.external.gitleaks.scan_with_gitleaks", lambda *a, **k: fake
    )
    monkeypatch.setattr(
        "ansibleguard.external.ansible_lint.scan_with_ansible_lint",
        lambda *a, **k: ToolResult("completed"),
    )

    output = tmp_path / "output"
    run = analyze_path(target, output)

    assert run["discovered"] == 1
    assert run["structurally_analyzed"] == 0
    findings = json.loads((output / "findings.json").read_text())
    assert findings[0]["rule_id"] == "hardcoded-credentials"
    assert findings[0]["analysis_population"] == "analysis_failed"
    summary = (output / "summary.csv").read_text()
    assert "invalid,unknown,skipped,completed,completed" in summary
    report = json.loads((output / "summary" / "report.json").read_text())
    metadata = json.loads((output / "run_metadata.json").read_text())
    assert report["status"] == "partial"
    assert report["analysis_health"]["parse_failed_files"] == 1
    assert metadata["analysis_health"]["complete"] is False


def test_analysis_health_records_unresolved_include_classes(tmp_path, monkeypatch):
    target = tmp_path / "tasks.yml"
    target.write_text(
        "- include_vars: '{{ platform }}.yml'\n"
        "- include_vars: missing.yml\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "ansibleguard.external.gitleaks.scan_with_gitleaks",
        lambda *a, **k: ToolResult("completed"),
    )
    monkeypatch.setattr(
        "ansibleguard.external.ansible_lint.scan_with_ansible_lint",
        lambda *a, **k: ToolResult("completed"),
    )

    output = tmp_path / "output"
    analyze_path(target, output)

    health = json.loads((output / "run_metadata.json").read_text())[
        "analysis_health"
    ]
    assert health["include_resolutions"] == {
        "DYNAMIC": 1,
        "STATIC_MISSING": 1,
    }
    assert health["unresolved_dynamic_includes"] == 1
    report = json.loads((output / "summary" / "report.json").read_text())
    assert set(report["timings"]) >= {
        "parse_seconds",
        "symbol_index_seconds",
        "internal_detectors_seconds",
        "providers_seconds",
    }
    assert report["performance"]["yaml_parse_operations"] == 1
    assert report["performance"]["peak_memory_mb"] > 0
    assert report["timings"]["cpu_seconds"] >= 0
    assert report["performance"]["symbol_queries"] >= 0
    assert report["performance"]["yaml_files_per_second"] > 0
    assert report["performance"]["tasks_per_second"] >= 0
    assert report["performance"]["symbol_queries_per_second"] >= 0


def test_nonfatal_parse_diagnostic_preserves_complete_health(tmp_path, monkeypatch):
    target = tmp_path / "vars.yml"
    target.write_text("value: one\nvalue: two\n", encoding="utf-8")
    monkeypatch.setattr(
        "ansibleguard.external.gitleaks.scan_with_gitleaks",
        lambda *a, **k: ToolResult("completed"),
    )
    monkeypatch.setattr(
        "ansibleguard.external.ansible_lint.scan_with_ansible_lint",
        lambda *a, **k: ToolResult("completed"),
    )

    output = tmp_path / "output"
    run = analyze_path(target, output)
    health = json.loads((output / "run_metadata.json").read_text())[
        "analysis_health"
    ]

    assert run["status"] == "completed_with_diagnostics"
    assert health["status"] == "completed_with_diagnostics"
    assert health["complete"] is True
    assert health["diagnostic_count"] >= 1
    assert health["fault_count"] == 0


def test_corrupt_parse_cache_is_explicit_partial_not_clean(tmp_path, monkeypatch):
    target = tmp_path / "project"
    target.mkdir()
    source = target / "tasks.yml"
    source.write_text("- debug: {msg: ready}\n", encoding="utf-8")
    output = tmp_path / "output"
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    cache_key = hashlib.sha256(
        f"{PARSER_CACHE_VERSION}:{source.resolve()}:{source_hash}".encode()
    ).hexdigest()
    cache_file = output / ".cache/parsed" / f"{cache_key}.json"
    cache_file.parent.mkdir(parents=True)
    cache_file.write_text("not-json", encoding="utf-8")
    monkeypatch.setattr(
        "ansibleguard.external.gitleaks.scan_with_gitleaks",
        lambda *a, **k: ToolResult("completed"),
    )
    monkeypatch.setattr(
        "ansibleguard.external.ansible_lint.scan_with_ansible_lint",
        lambda *a, **k: ToolResult("completed"),
    )

    run = analyze_path(target, output, profile="developer-fast")
    metadata = json.loads((output / "run_metadata.json").read_text())
    diagnostics = json.loads((output / "diagnostics.json").read_text())

    assert run["status"] == "partial"
    assert metadata["analysis_health"]["complete"] is False
    assert metadata["performance"]["cache_errors"] == 1
    assert any(item.get("category") == "CACHE_ERROR" for item in diagnostics)


def test_output_serialization_failure_persists_failed_health(tmp_path, monkeypatch):
    target = tmp_path / "project"
    target.mkdir()
    (target / "tasks.yml").write_text(
        "- debug: {msg: ready}\n", encoding="utf-8"
    )
    output = tmp_path / "output"
    monkeypatch.setattr(
        "ansibleguard.external.gitleaks.scan_with_gitleaks",
        lambda *a, **k: ToolResult("completed"),
    )
    monkeypatch.setattr(
        "ansibleguard.external.ansible_lint.scan_with_ansible_lint",
        lambda *a, **k: ToolResult("completed"),
    )
    monkeypatch.setattr(
        "ansibleguard.report.output_contract.write_rollups_v3",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            OSError("simulated report failure")
        ),
    )

    run = analyze_path(target, output, profile="developer-fast")
    metadata = json.loads((output / "metadata/run.json").read_text())
    emergency = json.loads((output / "analysis-failure.json").read_text())

    assert run["status"] == "failed"
    assert run["analysis_failures"] == 1
    assert metadata["analysis_health"]["complete"] is False
    assert metadata["analysis_health"]["status"] == "failed"
    assert emergency["terminal_failure"]["category"] == (
        "OUTPUT_SERIALIZATION_ERROR"
    )


def test_source_permission_failure_uses_filesystem_fault_taxonomy(
    tmp_path, monkeypatch
):
    target = tmp_path / "project"
    target.mkdir()
    source = target / "tasks.yml"
    source.write_text("- debug: {msg: ready}\n", encoding="utf-8")
    output = tmp_path / "output"
    original_read_text = type(source).read_text

    def guarded_read_text(path, *args, **kwargs):
        if path.resolve() == source.resolve():
            raise PermissionError("simulated permission failure")
        return original_read_text(path, *args, **kwargs)

    monkeypatch.setattr(type(source), "read_text", guarded_read_text)
    monkeypatch.setattr(
        "ansibleguard.external.gitleaks.scan_with_gitleaks",
        lambda *a, **k: ToolResult("completed"),
    )
    monkeypatch.setattr(
        "ansibleguard.external.ansible_lint.scan_with_ansible_lint",
        lambda *a, **k: ToolResult("completed"),
    )

    run = analyze_path(target, output, profile="developer-fast")
    diagnostics = json.loads((output / "diagnostics.json").read_text())

    assert run["status"] == "partial"
    assert any(
        item.get("category") == "FILESYSTEM_PERMISSION_ERROR"
        for item in diagnostics
    )


def test_repository_index_memory_failure_persists_failed_health(
    tmp_path, monkeypatch
):
    target = tmp_path / "project"
    target.mkdir()
    (target / "tasks.yml").write_text(
        "- debug: {msg: ready}\n", encoding="utf-8"
    )
    output = tmp_path / "output"
    monkeypatch.setattr(
        "ansibleguard.analysis_context.build_repository_analysis_context",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            MemoryError("simulated memory limit")
        ),
    )

    run = analyze_path(target, output, profile="developer-fast")
    metadata = json.loads((output / "metadata/run.json").read_text())
    emergency = json.loads((output / "analysis-failure.json").read_text())

    assert run["status"] == "failed"
    assert metadata["analysis_health"]["faults_by_category"] == {
        "MEMORY_ERROR": 1
    }
    assert emergency["terminal_failure"]["failure_nature"] == "ENVIRONMENT"


def test_fault_taxonomy_is_aggregated_in_analysis_health(tmp_path, monkeypatch):
    target = tmp_path / "broken.yml"
    target.write_text("broken: [yaml\n", encoding="utf-8")
    monkeypatch.setattr(
        "ansibleguard.external.gitleaks.scan_with_gitleaks",
        lambda *a, **k: ToolResult("tool-error", message="missing"),
    )
    monkeypatch.setattr(
        "ansibleguard.external.ansible_lint.scan_with_ansible_lint",
        lambda *a, **k: ToolResult("completed"),
    )

    output = tmp_path / "output"
    run = analyze_path(target, output)
    health = json.loads((output / "run_metadata.json").read_text())[
        "analysis_health"
    ]

    assert run["status"] == "partial"
    assert health["complete"] is False
    assert health["faults_by_category"] == {
        "PARSER_ERROR": 1,
        "PROVIDER_ERROR": 1,
    }
    assert health["faults_by_nature"] == {
        "DETERMINISTIC_INPUT": 1,
        "ENVIRONMENT": 1,
    }


def test_partial_provider_makes_overall_health_partial_with_reason(
    tmp_path, monkeypatch
):
    target = tmp_path / "tasks.yml"
    target.write_text("- debug: {msg: ok}\n", encoding="utf-8")
    monkeypatch.setattr(
        "ansibleguard.external.gitleaks.scan_with_gitleaks",
        lambda *a, **k: ToolResult("completed"),
    )
    monkeypatch.setattr(
        "ansibleguard.external.ansible_lint.scan_with_ansible_lint",
        lambda *a, **k: ToolResult(
            "partial", message="unsupported project configuration",
            metadata={"returncode": 3},
        ),
    )

    output = tmp_path / "output"
    analyze_path(target, output)
    metadata = json.loads((output / "run_metadata.json").read_text())
    diagnostics = json.loads((output / "diagnostics.json").read_text())

    assert metadata["analysis_health"]["status"] == "partial"
    assert metadata["analysis_health"]["overall_status"] == "partial"
    assert metadata["analysis_health"]["provider_status"] == "partial"
    assert metadata["analysis_health"]["complete"] is False
    assert any(
        item["stage"] == "ansible-lint"
        and "unsupported project configuration" in item["message"]
        for item in diagnostics
    )


def test_tool_failure_is_not_reported_as_clean_scan(tmp_path, monkeypatch):
    target = tmp_path / "vars.yml"
    target.write_text("safe_value: true\n")
    monkeypatch.setattr(
        "ansibleguard.external.gitleaks.scan_with_gitleaks",
        lambda *a, **k: ToolResult("tool-error", message="binary missing"),
    )
    monkeypatch.setattr(
        "ansibleguard.external.ansible_lint.scan_with_ansible_lint",
        lambda *a, **k: ToolResult("completed"),
    )
    output = tmp_path / "output"
    run = analyze_path(target, output)
    assert run["tool_errors"] == 1
    diagnostics = json.loads((output / "diagnostics.json").read_text())
    assert diagnostics[-1]["status"] == "tool-error"


def test_repository_without_yaml_still_keeps_gitleaks_findings(tmp_path, monkeypatch):
    target = tmp_path / "project"
    target.mkdir()
    (target / ".env").write_text("TOKEN=secret\n")
    monkeypatch.setattr(
        "ansibleguard.external.gitleaks.scan_with_gitleaks",
        lambda *a, **k: ToolResult(
            "completed",
            [{"File": ".env", "StartLine": 1, "Description": "Token"}],
        ),
    )
    monkeypatch.setattr(
        "ansibleguard.external.ansible_lint.scan_with_ansible_lint",
        lambda *a, **k: ToolResult("completed"),
    )
    output = tmp_path / "output"
    run = analyze_path(target, output)
    assert run["discovered"] == 0
    findings = json.loads((output / "findings.json").read_text())
    assert findings[0]["file"].endswith(".env")


def test_relative_repository_target_does_not_duplicate_gitleaks_path(
    tmp_path, monkeypatch,
):
    target = tmp_path / "relative-project"
    target.mkdir()
    secret_file = target / ".env"
    secret_file.write_text("SYNTHETIC=value\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "ansibleguard.external.gitleaks.scan_with_gitleaks",
        lambda *a, **k: ToolResult(
            "completed",
            [{"File": ".env", "StartLine": 1, "Description": "Synthetic"}],
        ),
    )
    monkeypatch.setattr(
        "ansibleguard.external.ansible_lint.scan_with_ansible_lint",
        lambda *a, **k: ToolResult("completed"),
    )

    output = tmp_path / "output"
    analyze_path("relative-project", output)

    findings = json.loads((output / "findings.json").read_text())
    assert findings[0]["file"] == ".env"


def test_pr_shas_add_history_scan_without_merging_scan_modes(tmp_path, monkeypatch):
    target = tmp_path / "project"
    target.mkdir()
    (target / ".env").write_text("TOKEN=secret\n")
    monkeypatch.setenv("ANSIBLEGUARD_BASE_SHA", "a" * 40)
    monkeypatch.setenv("ANSIBLEGUARD_HEAD_SHA", "b" * 40)
    monkeypatch.setattr(
        "ansibleguard.external.gitleaks.scan_with_gitleaks",
        lambda *a, **k: ToolResult(
            "completed",
            [{"File": ".env", "StartLine": 1, "Description": "Tree token"}],
        ),
    )
    monkeypatch.setattr(
        "ansibleguard.external.gitleaks.scan_git_range_with_gitleaks",
        lambda *a, **k: ToolResult(
            "completed",
            [
                {
                    "File": ".env",
                    "StartLine": 1,
                    "Description": "History token",
                    "_scan_mode": "git-range",
                }
            ],
        ),
    )
    monkeypatch.setattr(
        "ansibleguard.external.ansible_lint.scan_with_ansible_lint",
        lambda *a, **k: ToolResult("completed"),
    )

    output = tmp_path / "output"
    analyze_path(target, output)

    occurrences = json.loads((output / "occurrences.json").read_text())
    assert {item["scan_mode"] for item in occurrences} == {"dir", "git-range"}
    metadata = json.loads((output / "run_metadata.json").read_text())
    assert set(metadata["tool_details"]["gitleaks"]) >= {
        "tree",
        "git_range",
    }


def test_empty_yaml_keeps_source_detector_finding_without_structural_analysis(
    tmp_path, monkeypatch
):
    target = tmp_path / "empty.yml"
    target.write_text("")
    monkeypatch.setattr(
        "ansibleguard.external.gitleaks.scan_with_gitleaks",
        lambda *a, **k: ToolResult("completed"),
    )
    monkeypatch.setattr(
        "ansibleguard.external.ansible_lint.scan_with_ansible_lint",
        lambda *a, **k: ToolResult("completed"),
    )

    output = tmp_path / "output"
    run = analyze_path(target, output)

    assert run["structurally_analyzed"] == 0
    findings = json.loads((output / "findings.json").read_text())
    assert {finding["rule_id"] for finding in findings} == {"empty-abstraction"}
    assert ",empty,skipped," in (output / "summary.csv").read_text()


def test_metadata_and_vars_rules_run_without_structural_analysis(
    tmp_path, monkeypatch
):
    target = tmp_path / "project"
    meta = target / "roles" / "web" / "meta" / "main.yml"
    meta.parent.mkdir(parents=True)
    meta.write_text("dependencies: []\n")
    defaults = target / "roles" / "web" / "defaults" / "main.yml"
    defaults.parent.mkdir(parents=True)
    defaults.write_text("port: 8080\n")
    monkeypatch.setattr(
        "ansibleguard.external.gitleaks.scan_with_gitleaks",
        lambda *a, **k: ToolResult("completed"),
    )
    monkeypatch.setattr(
        "ansibleguard.external.ansible_lint.scan_with_ansible_lint",
        lambda *a, **k: ToolResult("completed"),
    )

    output = tmp_path / "output"
    run = analyze_path(target, output)

    assert run["structurally_analyzed"] == 0
    findings = json.loads((output / "findings.json").read_text())
    assert {
        "galaxy-meta-incomplete", "variable-naming-convention",
    } <= {finding["rule_id"] for finding in findings}
    assert any("no galaxy_info" in finding["message"] for finding in findings)
    assert any("Variable 'port'" in finding["message"] for finding in findings)


def test_skipped_file_fallback_preserves_manifest_symbol_graph(
    tmp_path, monkeypatch
):
    target = tmp_path / "project"
    tasks = target / "roles" / "web" / "tasks" / "main.yml"
    tasks.parent.mkdir(parents=True)
    tasks.write_text("")
    defaults = target / "roles" / "web" / "defaults" / "main.yml"
    defaults.parent.mkdir(parents=True)
    defaults.write_text("excluded_value: present\n")
    rows = classify_repository(target)
    for row in rows:
        if row["path"] == "roles/web/tasks/main.yml":
            row["included"] = "true"
            row["file_class"] = "production_ansible"
            row["exclusion_reason"] = ""
        else:
            row["included"] = "false"
            row["exclusion_reason"] = "test_exclusion"
    manifest = write_file_manifest(rows, tmp_path / "files.csv")
    observed = []

    def graph_required(_path, symbol_index=None, **_kwargs):
        assert symbol_index is not None
        assert symbol_index.input_files == ("roles/web/tasks/main.yml",)
        assert "excluded_value" not in symbol_index.names
        observed.append(True)
        return {}

    monkeypatch.setattr(
        "ansibleguard.detectors.partial_checklist.detect_partial_checklist_smells",
        graph_required,
    )
    monkeypatch.setattr(
        "ansibleguard.detectors.missing_checklist.detect_missing_checklist_smells",
        graph_required,
    )
    monkeypatch.setattr(
        "ansibleguard.external.gitleaks.scan_with_gitleaks",
        lambda *a, **k: ToolResult("completed"),
    )
    monkeypatch.setattr(
        "ansibleguard.external.ansible_lint.scan_with_ansible_lint",
        lambda *a, **k: ToolResult("completed"),
    )

    analyze_path(target, tmp_path / "output", file_manifest=manifest)

    assert observed == [True, True]


def test_internal_failure_is_structured_and_file_is_not_successful(
    tmp_path, monkeypatch
):
    target = tmp_path / "site.yml"
    target.write_text("- name: test\n  debug: {msg: ok}\n", encoding="utf-8")
    monkeypatch.setattr(
        "ansibleguard.external.gitleaks.scan_with_gitleaks",
        lambda *a, **k: ToolResult("completed"),
    )
    monkeypatch.setattr(
        "ansibleguard.external.ansible_lint.scan_with_ansible_lint",
        lambda *a, **k: ToolResult("completed"),
    )
    monkeypatch.setattr(
        "ansibleguard.smells.mainn",
        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("detector exploded")),
    )

    output = tmp_path / "output"
    run = analyze_path(target, output)

    assert run["analysis_failures"] == 1
    assert run["file_states"] == {"failed": 1}
    diagnostics = json.loads((output / "diagnostics.json").read_text())
    assert diagnostics[0]["status"] == "analysis-error"
    assert diagnostics[0]["stage"] == "internal-detectors"
    assert "detector exploded" in diagnostics[0]["message"]
    assert ",failed," in (output / "summary.csv").read_text()
    report = json.loads((output / "summary/report.json").read_text())
    assert report["status"] == "failed"


def test_mixed_success_and_failure_marks_run_partial(tmp_path, monkeypatch):
    import ansibleguard.smells as smells

    target = tmp_path / "project"
    target.mkdir()
    (target / "good.yml").write_text("- name: good\n  debug: {msg: ok}\n")
    (target / "bad.yml").write_text("- name: bad\n  debug: {msg: no}\n")
    monkeypatch.setattr(
        "ansibleguard.external.gitleaks.scan_with_gitleaks",
        lambda *a, **k: ToolResult("completed"),
    )
    monkeypatch.setattr(
        "ansibleguard.external.ansible_lint.scan_with_ansible_lint",
        lambda *a, **k: ToolResult("completed"),
    )
    original = smells.mainn

    def sometimes_fails(path, **kwargs):
        if str(path).endswith("bad.yml"):
            raise RuntimeError("selected failure")
        return original(path, **kwargs)

    monkeypatch.setattr("ansibleguard.smells.mainn", sometimes_fails)
    output = tmp_path / "output"
    run = analyze_path(target, output)

    assert run["file_states"] == {"analyzed": 1, "failed": 1}
    report = json.loads((output / "summary/report.json").read_text())
    assert report["status"] == "partial"


def test_per_file_reporting_failure_marks_completed_analysis_partial(
    tmp_path, monkeypatch
):
    from ansibleguard.report import text_writer

    target = tmp_path / "site.yml"
    target.write_text("- name: test\n  debug: {msg: ok}\n", encoding="utf-8")
    monkeypatch.setattr(
        "ansibleguard.external.gitleaks.scan_with_gitleaks",
        lambda *a, **k: ToolResult("completed"),
    )
    monkeypatch.setattr(
        "ansibleguard.external.ansible_lint.scan_with_ansible_lint",
        lambda *a, **k: ToolResult("completed"),
    )
    original = text_writer.write_findings_to_txt

    def fail_only_per_file(findings, path, *args, **kwargs):
        if str(path).endswith("Play_Level_Analysis.txt"):
            raise OSError("per-file report unavailable")
        return original(findings, path, *args, **kwargs)

    monkeypatch.setattr(text_writer, "write_findings_to_txt", fail_only_per_file)
    output = tmp_path / "output"
    run = analyze_path(target, output)

    assert run["file_states"] == {"partial": 1}
    diagnostics = json.loads((output / "diagnostics.json").read_text())
    assert any(
        item["stage"] == "finding-normalization-and-reporting"
        and item["status"] == "analysis-error"
        for item in diagnostics
    )


def test_one_failed_detected_ansible_root_cannot_produce_clean_scan(
    tmp_path, monkeypatch
):
    target = tmp_path / "monorepo"
    for project in ("service_a", "service_b"):
        tasks = target / project / "roles" / "web" / "tasks" / "main.yml"
        tasks.parent.mkdir(parents=True)
        tasks.write_text("- debug: {msg: ok}\n")

    monkeypatch.setattr(
        "ansibleguard.external.ansible_lint.scan_with_ansible_lint",
        lambda root, files=None: ToolResult(
            "tool-error" if root.name == "service_b" else "completed",
            message="provider root failed" if root.name == "service_b" else "",
        ),
    )

    output = tmp_path / "output"
    run = analyze_path(target, output, profile="lint")

    report = json.loads((output / "summary" / "report.json").read_text())
    diagnostics = json.loads((output / "diagnostics.json").read_text())
    assert report["status"] == "partial"
    assert run["tool_errors"] == 1
    assert any(
        item.get("provider_root") == "service_b"
        and item["status"] == "provider-error"
        for item in diagnostics
    )


def test_isolated_detector_failure_marks_file_partial_and_keeps_scan(
    tmp_path, monkeypatch
):
    target = tmp_path / "site.yml"
    target.write_text("- name: test\n  debug: {msg: ok}\n")
    monkeypatch.setattr(
        "ansibleguard.external.gitleaks.scan_with_gitleaks",
        lambda *a, **k: ToolResult("completed"),
    )
    monkeypatch.setattr(
        "ansibleguard.external.ansible_lint.scan_with_ansible_lint",
        lambda *a, **k: ToolResult("completed"),
    )
    monkeypatch.setattr(
        "ansibleguard.parser.calculate_metrics_playbook",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("isolated")),
    )

    output = tmp_path / "output"
    run = analyze_path(target, output)

    assert run["file_states"] == {"partial": 1}
    assert run["analysis_failures"] == 1
    diagnostics = json.loads((output / "diagnostics.json").read_text())
    assert any(
        item.get("detector") == "large-playbook"
        and item.get("category") == "INTERNAL_DETECTOR_EXCEPTION"
        for item in diagnostics
    )


def test_gitleaks_production_literal_gets_likely_real_context(tmp_path):
    source = tmp_path / "tasks.yml"
    source.write_text(
        "- name: deploy\n  debug: {msg: ok}\n", encoding="utf-8"
    )
    context = build_repository_analysis_context(tmp_path, [source])
    finding = {
        "provider": "gitleaks",
        "file": "tasks.yml",
        "Secret": "not-a-placeholder-token",
    }

    annotated = _annotate_finding_populations([finding], context, tmp_path)[0]

    assert annotated["secret_context"] == "likely_real_secret"
    assert "production_ansible" in annotated["secret_context_factors"]["positive"]


def test_gitleaks_yaml_key_gets_variable_semantic_subject(tmp_path):
    source = tmp_path / "vars.yml"
    source.write_text("api_token: literal-value\n", encoding="utf-8")
    context = build_repository_analysis_context(tmp_path, [source])
    finding = {"provider": "gitleaks", "file": "vars.yml", "line": 1}

    annotated = _annotate_finding_populations([finding], context, tmp_path)[0]

    assert annotated["semantic_subject"] == "variable:api_token"
