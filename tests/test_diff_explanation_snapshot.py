"""Explanations and summaries must use the head/index tree that was scanned."""

import json
from pathlib import Path
import subprocess

import pytest

from ansibleguard import cli, diff_workflow
from ansibleguard.report import llm_explain


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True).stdout


def source(marker):
    return f"- hosts: all\n  tasks:\n    - name: {marker}\n      debug: {{msg: {marker}}}\n"


@pytest.fixture
def repository(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "fixture@example.invalid")
    git(repo, "config", "user.name", "Fixture")
    (repo / "site.yml").write_text(source("BASE_MARKER"))
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "Base")
    return repo


def write_output(output, introduced):
    target = Path(output) / "canonical"
    target.mkdir(parents=True)
    items = [{"occurrence_id": "head-id", "concept_id": "example", "file": "site.yml", "line": 3,
              "scan_mode": "source", "severity": "warning", "message": "Check task", "policy": "required",
              "semantic_key": "head-id", "native_rules": ["ansibleguard/example"], "detectors": []}] if introduced else []
    (target / "occurrences.json").write_text(json.dumps({"kind": "canonical-occurrences", "items": items}))


def fake_analyzer(target, output, *args, **kwargs):
    text = (Path(target) / "site.yml").read_text()
    write_output(output, "BASE_MARKER" not in text)


def model_response(marker):
    response = {key: "fixture" for key in llm_explain.REQUIRED_KEYS}
    response["confidence"] = "high"
    response.update(assessment="supported", actionability="actionable", missing_evidence=[], evidence=[
        {"file": "site.yml", "line": 3}])
    return json.dumps(response)


@pytest.mark.parametrize("mode,parallel", [("head", False), ("head", True), ("staged", False)])
def test_prompt_uses_scanned_snapshot_and_cleanup_preserves_dirty_checkout(tmp_path, repository, monkeypatch, mode, parallel):
    repo = repository
    marker = "COMMITTED_MARKER" if mode == "head" else "STAGED_MARKER"
    if mode == "head":
        git(repo, "checkout", "-qb", "feature")
    (repo / "site.yml").write_text(source(marker))
    git(repo, "add", ".")
    if mode == "head":
        git(repo, "commit", "-qm", "Head")
    (repo / "site.yml").write_text(source("DIRTY_MARKER"))
    before = git(repo, "status", "--porcelain")
    index_before = git(repo, "write-tree")
    prompts, roots = [], []
    original = llm_explain._read_source_context

    def read(root, *args, **kwargs):
        roots.append(Path(root))
        assert Path(root).is_dir()
        return original(root, *args, **kwargs)

    def model(host, name, system, user, timeout):
        prompts.append(user)
        return model_response(marker), 0.1, None

    monkeypatch.setattr(cli, "analyze_path", fake_analyzer)
    monkeypatch.setattr(llm_explain, "_read_source_context", read)
    monkeypatch.setattr(llm_explain, "_call_ollama", model)
    output = tmp_path / "out"
    args = [str(repo), "--base", "main", "--policy", "observe", "--explain", "-o", str(output)]
    args += ["--head", "HEAD"] if mode == "head" else ["--staged"]
    if parallel:
        args.append("--parallel-base-head")
    cli._diff_main(args)
    assert len(prompts) == 1 and marker in prompts[0] and "DIRTY_MARKER" not in prompts[0]
    assert roots and all(not root.exists() for root in roots)
    assert git(repo, "status", "--porcelain") == before and git(repo, "write-tree") == index_before
    assert "DIRTY_MARKER" in (repo / "site.yml").read_text()
    assert git(repo, "worktree", "list", "--porcelain").count("worktree ") == 1
    payload = json.loads((output / "diff/comparison.json").read_text())
    assert payload["comparison"]["introduced"][0]["llm_status"] == "ok"
    assert payload["comparison"]["source_context"]["uses_separate_head_tree"]
    assert payload["playbooks"][0]["tasks_analyzed"] == 1


def test_precomputed_results_do_not_explain_using_current_checkout(tmp_path, repository, monkeypatch):
    repo = repository
    (repo / "site.yml").write_text(source("UNRELATED_CURRENT_MARKER"))
    base, head = tmp_path / "base", tmp_path / "head"
    write_output(base, False)
    write_output(head, True)
    monkeypatch.setattr(llm_explain, "_call_ollama", lambda *a, **k: pytest.fail("precomputed results read current source"))
    output = tmp_path / "out"
    cli._diff_main([str(repo), "--base", "HEAD", "--base-results", str(base), "--head-results", str(head),
                    "--policy", "observe", "--explain", "-o", str(output)])
    payload = json.loads((output / "diff/comparison.json").read_text())
    assert payload["comparison"]["introduced"][0]["llm_status"] == "insufficient-context"
    assert payload["comparison"]["source_context"]["status"] == "unavailable"
    assert payload["playbooks"] == [] and payload["comparison"]["variable_doc_gaps"] == []
    assert "Source for these saved results is unavailable" in (output / "diff/summary.md").read_text()


def test_snapshot_cleanup_also_runs_when_comparison_fails(tmp_path, repository, monkeypatch):
    repo = repository
    roots = []
    monkeypatch.setattr(cli, "analyze_path", fake_analyzer)

    def failed(*args, head_source_root, **kwargs):
        roots.append(Path(head_source_root))
        assert roots[-1].is_dir()
        raise diff_workflow.DiffWorkflowError("fixture reporting failure")

    monkeypatch.setattr(diff_workflow, "compare_outputs", failed)
    with pytest.raises(SystemExit) as result:
        cli._diff_main([str(repo), "--base", "main", "--head", "HEAD", "--policy", "observe", "-o", str(tmp_path / "out")])
    assert result.value.code == 2
    assert roots and not roots[0].exists()
    assert git(repo, "worktree", "list", "--porcelain").count("worktree ") == 1
