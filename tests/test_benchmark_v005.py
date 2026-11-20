import json
from dataclasses import replace

from scripts.benchmark_v005 import (
    run_benchmark,
    run_benchmark_manifest,
    semantic_index_signature,
    validate_benchmark,
    validate_benchmark_manifest,
)
from ansibleguard.analysis_context import build_repository_analysis_context
from scripts.build_v005_benchmark_corpus import build_corpus, SHAPES


def test_benchmark_reports_parse_and_cache_metrics(tmp_path):
    source = tmp_path / "tasks.yml"
    source.write_text("- name: noop\n  debug: {msg: ok}\n", encoding="utf-8")
    cache = tmp_path / ".cache" / "parsed"

    result = run_benchmark(tmp_path, cache_dir=cache, repeat=2)

    assert result["schema"] == "ansibleguard-v005-benchmark-v1"
    assert result["yaml_files"] == 1
    assert result["runs"][0]["performance"]["cache_misses"] == 1
    assert result["runs"][1]["performance"]["cache_hits"] == 1
    assert (
        result["runs"][0]["semantic_index_sha256"]
        == result["runs"][1]["semantic_index_sha256"]
    )
    assert result["min_seconds"] >= 0


def test_benchmark_semantic_signature_handles_include_relationships(tmp_path):
    (tmp_path / "child.yml").write_text("- debug: {msg: child}\n", encoding="utf-8")
    (tmp_path / "other.yml").write_text("- debug: {msg: other}\n", encoding="utf-8")
    (tmp_path / "tasks.yml").write_text(
        "- include_tasks: child.yml\n- include_tasks: other.yml\n", encoding="utf-8"
    )

    result = run_benchmark(tmp_path)

    assert result["runs"][0]["semantic_index_sha256"]
    files = sorted(tmp_path.glob("*.yml"))
    context = build_repository_analysis_context(tmp_path, files)
    reversed_context = replace(
        context, include_relationships=tuple(reversed(context.include_relationships))
    )
    assert semantic_index_signature(context) == semantic_index_signature(
        reversed_context
    )


def test_benchmark_json_shape_is_serializable(tmp_path):
    (tmp_path / "vars.yaml").write_text("port: 8080\n", encoding="utf-8")
    result = run_benchmark(tmp_path)
    encoded = json.dumps(result)
    assert "ansibleguard-v005-benchmark-v1" in encoded


def test_benchmark_gate_checks_structural_and_timing_regressions(tmp_path):
    (tmp_path / "tasks.yml").write_text("- debug: {msg: ok}\n", encoding="utf-8")
    baseline = run_benchmark(tmp_path)
    candidate = run_benchmark(tmp_path)
    assert validate_benchmark(candidate, baseline, max_slowdown=100) == []

    changed = dict(candidate)
    changed["yaml_files"] = 2
    assert "yaml file population differs from baseline" in validate_benchmark(
        changed, baseline
    )
    assert any(
        "peak memory exceeds budget" in error
        for error in validate_benchmark(candidate, baseline, max_memory_mb=0)
    )
    changed_signature = dict(candidate)
    changed_runs = [dict(run) for run in candidate["runs"]]
    changed_runs[-1]["semantic_index_sha256"] = "different"
    changed_signature["runs"] = changed_runs
    assert "semantic index differs from baseline" in validate_benchmark(
        changed_signature, baseline
    )


def test_benchmark_manifest_runs_named_shapes(tmp_path):
    one = tmp_path / "one"
    two = tmp_path / "two"
    one.mkdir()
    two.mkdir()
    (one / "tasks.yml").write_text("- debug: {msg: one}\n", encoding="utf-8")
    (two / "vars.yml").write_text("port: 8080\n", encoding="utf-8")
    manifest = tmp_path / "corpus.json"
    manifest.write_text(
        json.dumps({"benchmarks": [
            {"name": "small-role", "root": "one"},
            {"name": "vars-project", "root": "two"},
        ]}),
        encoding="utf-8",
    )

    result = run_benchmark_manifest(manifest)

    assert result["schema"] == "ansibleguard-v005-benchmark-manifest-v1"
    assert [item["name"] for item in result["benchmarks"]] == [
        "small-role", "vars-project"
    ]
    assert validate_benchmark_manifest(result, result, max_slowdown=100) == []


def test_generated_permanent_corpus_contains_every_shape(tmp_path):
    root = tmp_path / "corpus"
    manifest_path = build_corpus(
        root,
        many_files=3,
        variable_count=4,
        large_task_count=5,
        target_lines=40,
    )
    manifest = json.loads(manifest_path.read_text())

    assert tuple(item["name"] for item in manifest["benchmarks"]) == SHAPES
    assert len((root / "pathological-large-task-file/tasks.yml").read_text().splitlines()) >= 40
    result = run_benchmark_manifest(manifest_path)
    assert [item["name"] for item in result["benchmarks"]] == list(SHAPES)
