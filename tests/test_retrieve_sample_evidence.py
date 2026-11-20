import json
import subprocess

import pytest

from scripts import retrieve_sample_evidence as retrieval
from scripts.sample_partitioned_occurrences import sha256, stable_digest, write_csv


def git(repository, *args):
    result = subprocess.run(
        ["git", "-C", str(repository), "-c", "user.name=Fixture", "-c", "user.email=fixture@example.com", *args],
        check=True, capture_output=True, env=retrieval.git_environment(),
    )
    return result.stdout.decode().strip()


@pytest.fixture
def frozen_repository(tmp_path):
    probe = subprocess.run(["git", "--no-lazy-fetch", "--no-replace-objects", "--version"], capture_output=True)
    if probe.returncode:
        pytest.skip("Git with explicit offline read flags is required")
    root = tmp_path / "repositories"
    repo = root / "o/repo"
    repo.mkdir(parents=True)
    git(repo, "init", "-q")
    (repo / "tasks.yml").write_text("- name: Frozen task\n  debug:\n    msg: old\n")
    git(repo, "add", "tasks.yml")
    git(repo, "commit", "-qm", "Frozen source")
    return root, repo, git(repo, "rev-parse", "HEAD")


def row(commit, *, line="1", path="tasks.yml", occurrence="occurrence"):
    result = {
        "run_id": "run", "repository": "o/repo", "commit_sha": commit, "occurrence_id": occurrence,
        "file": path, "line": line, "rule_id": "ansibleguard/example", "instrument": "required",
        "dataset_role": "calibration", "eligible_for_performance_scoring": "False",
        "retrieval_status": "pending", "label_status": "not-started", "sampling_weight": "17.5",
    }
    result["sample_id"] = "PROB-" + stable_digest("required", "run", "o/repo", commit, occurrence)
    return result


def test_read_uses_frozen_blob_despite_changed_head_worktree_and_replace_ref(frozen_repository):
    root, repo, frozen = frozen_repository
    original = (repo / "tasks.yml").read_bytes()
    (repo / "tasks.yml").write_text("- name: Replacement\n  debug: msg=new\n")
    git(repo, "commit", "-qam", "New head")
    replacement = git(repo, "rev-parse", "HEAD")
    git(repo, "replace", frozen, replacement)
    (repo / "tasks.yml").write_text("uncommitted working tree\n")
    before = git(repo, "status", "--porcelain")
    raw, oid = retrieval.FrozenGitReader(root).read("o/repo", frozen, "tasks.yml")
    assert raw == original and len(oid) in {40, 64}
    assert git(repo, "status", "--porcelain") == before
    assert git(repo, "rev-parse", "HEAD") == replacement
    assert (repo / "tasks.yml").read_text() == "uncommitted working tree\n"


def test_missing_commit_and_path_have_explicit_failures(frozen_repository):
    root, _, frozen = frozen_repository
    reader = retrieval.FrozenGitReader(root)
    with pytest.raises(retrieval.RetrievalFailure, match="commit-unavailable"):
        reader.read("o/repo", "0" * 40, "tasks.yml")
    with pytest.raises(retrieval.RetrievalFailure, match="path-unavailable"):
        reader.read("o/repo", frozen, "absent.yml")


def test_same_commit_is_recovered_from_explicit_cache_with_attempt_history(frozen_repository, tmp_path):
    root, _, frozen = frozen_repository
    primary = tmp_path / "primary"
    unrelated = primary / "o/repo"
    unrelated.mkdir(parents=True)
    git(unrelated, "init", "-q")
    (unrelated / "tasks.yml").write_text("name: unrelated source\n")
    git(unrelated, "add", "tasks.yml")
    git(unrelated, "commit", "-qm", "Unrelated snapshot")
    sources = retrieval.FrozenGitSources([primary, root])
    raw, _ = sources.read("o/repo", frozen, "tasks.yml")
    assert b"Frozen task" in raw and b"unrelated" not in raw
    assert sources.last_read["source_store_index"] == 1
    assert json.loads(sources.last_read["source_attempts"]) == [
        {"store_index": 0, "status": "commit-unavailable"}, {"store_index": 1, "status": "blob-read"}]


def test_cache_symlinks_require_explicitly_trusted_local_roots(frozen_repository, tmp_path):
    root, repo, frozen = frozen_repository
    cache = tmp_path / "cache"
    (cache / "o").mkdir(parents=True)
    (cache / "o/repo").symlink_to(repo, target_is_directory=True)
    with pytest.raises(retrieval.RetrievalFailure, match="repository-outside-root"):
        retrieval.FrozenGitReader(cache).read("o/repo", frozen, "tasks.yml")
    sources = retrieval.FrozenGitSources([cache, root])
    raw, _ = sources.read("o/repo", frozen, "tasks.yml")
    assert b"Frozen task" in raw
    assert sources.last_read["resolved_repository"] == str(repo.resolve())


def test_missing_from_all_local_stores_keeps_all_attempts(frozen_repository, tmp_path):
    root, _, _ = frozen_repository
    sources = retrieval.FrozenGitSources([root, tmp_path / "absent"])
    with pytest.raises(retrieval.RetrievalFailure, match="source-not-in-configured-stores"):
        sources.read("o/repo", "0" * 40, "tasks.yml")
    assert [entry["status"] for entry in json.loads(sources.last_read["source_attempts"])] == [
        "commit-unavailable", "repository-unavailable"]


def test_nonavailability_limits_do_not_trigger_fallback(frozen_repository, tmp_path):
    root, _, frozen = frozen_repository
    sources = retrieval.FrozenGitSources([root, tmp_path / "absent"], max_bytes=1)
    with pytest.raises(retrieval.RetrievalFailure, match="source-too-large"):
        sources.read("o/repo", frozen, "tasks.yml")
    assert json.loads(sources.last_read["source_attempts"]) == [{"store_index": 0, "status": "source-too-large"}]


def test_symlink_is_not_followed(frozen_repository, tmp_path):
    root, repo, _ = frozen_repository
    outside = tmp_path / "outside.yml"
    outside.write_text("secret material outside repository\n")
    (repo / "link.yml").symlink_to(outside)
    git(repo, "add", "link.yml")
    git(repo, "commit", "-qm", "Symlink")
    with pytest.raises(retrieval.RetrievalFailure, match="not-a-regular-blob"):
        retrieval.FrozenGitReader(root).read("o/repo", git(repo, "rev-parse", "HEAD"), "link.yml")


def test_source_limit_blocks_large_blob_before_display(frozen_repository):
    root, _, frozen = frozen_repository
    with pytest.raises(retrieval.RetrievalFailure, match="source-too-large"):
        retrieval.FrozenGitReader(root, max_bytes=1).read("o/repo", frozen, "tasks.yml")


def test_git_pathspec_characters_are_literal(frozen_repository):
    root, repo, _ = frozen_repository
    name = ":(glob)task[one].yml"
    (repo / name).write_text("name: literal filename\n")
    git(repo, "--literal-pathspecs", "add", "--", name)
    git(repo, "commit", "-qm", "Literal pathspec characters")
    raw, _ = retrieval.FrozenGitReader(root).read("o/repo", git(repo, "rev-parse", "HEAD"), name)
    assert raw == b"name: literal filename\n"


@pytest.mark.parametrize("path", [".", "../outside.yml", "/absolute.yml", "a/../tasks.yml", "a//tasks.yml", "a\\tasks.yml", "a\n.yml"])
def test_unsafe_paths_are_rejected(path):
    with pytest.raises(retrieval.RetrievalFailure, match="unsafe-path"):
        retrieval.safe_relative(path)


@pytest.mark.parametrize("raw,anchor,reason", [(b"", "1", "empty-source"), (b"x\n", "99", "anchor-out-of-range"),
                                              (b"x\n", "0", "invalid-anchor"), (b"\xff", "1", "source-not-utf8"),
                                              (b"x\0y", "1", "binary-source")])
def test_invalid_source_or_anchor_never_clamps(raw, anchor, reason):
    packet, info, failure = retrieval.base_packet(row("a" * 40, line=anchor), raw, "blob")
    assert packet is None and failure == reason
    assert info["evidence_complete"] is False


def test_full_file_redaction_precedes_window_and_preserves_anchor_numbers():
    text = "password: |\n  secret value\n  continuation\nname: safe\n"
    packet, info, failure = retrieval.base_packet(row("a" * 40, line="3"), text.encode(), "blob", max_lines=2, window=0)
    assert not failure
    assert info["truncated"] is True and info["redaction_affects_anchor"] is True
    assert packet["display_line_start"] == packet["display_line_end"] == 3
    assert "continuation" not in packet["numbered_source"]
    assert packet["numbered_source"].startswith("    3 | ")
    assert packet["subject_verified"] is False


def test_redaction_failure_is_retained_as_unavailable(monkeypatch):
    def broken(_):
        raise RuntimeError("sensitive exception detail")
    monkeypatch.setattr(retrieval, "redact_sensitive_text_v2", broken)
    packet, _, failure = retrieval.base_packet(row("a" * 40), b"name: x\n", "blob")
    assert packet is None and failure == "redaction-failed"


def test_residual_secret_scan_blocks_packet(monkeypatch):
    monkeypatch.setattr(retrieval, "scan_text", lambda _: [(1, "token-prefix", 30)])
    packet, _, failure = retrieval.base_packet(row("a" * 40), b"name: x\n", "blob")
    assert packet is None and failure == "residual-secret-scan-blocked"


def test_every_selected_id_and_weight_survives_retrieval(frozen_repository, tmp_path):
    root, _, frozen = frozen_repository
    rows = [row(frozen), row(frozen, path="missing.yml", occurrence="missing"),
            row(frozen, line="99", occurrence="bad-line")]
    results = retrieval.retrieve_rows(rows, retrieval.FrozenGitReader(root), tmp_path / "packets")
    assert len(results) == 3
    assert [result["sample_id"] for result in results] == [item["sample_id"] for item in rows]
    assert all(result["sampling_weight"] == "17.5" for result in results)
    assert [result["retrieval_status"] for result in results] == ["source-retrieved", "unavailable", "unavailable"]
    assert results[1]["failure_reason"] == "path-unavailable"
    assert results[2]["failure_reason"] == "anchor-out-of-range"
    assert len(list((tmp_path / "packets").glob("*.json"))) == 1
    assert all(result["label_status"] == "not-started" for result in results)


def test_git_environment_cannot_redirect_the_source(monkeypatch):
    monkeypatch.setenv("GIT_DIR", "/wrong/repository")
    monkeypatch.setenv("GIT_OBJECT_DIRECTORY", "/wrong/objects")
    env = retrieval.git_environment()
    assert "GIT_DIR" not in env and "GIT_OBJECT_DIRECTORY" not in env
    assert env["GIT_NO_LAZY_FETCH"] == env["GIT_NO_REPLACE_OBJECTS"] == "1"


def make_draw(path, selected):
    path.mkdir()
    write_csv(path / "selection-ledger.csv", selected)
    (path / "sampling-plan.csv").write_text("metadata\n")
    manifest = {"schema_version": 1, "run_id": "run", "instrument": "required",
                "selected_occurrences": len(selected), "eligible_for_performance_scoring": False,
                "output_sha256": {name: sha256(path / name) for name in ("selection-ledger.csv", "sampling-plan.csv")}}
    (path / "selection-manifest.json").write_text(json.dumps(manifest))


def test_cli_keeps_packets_separate_and_refuses_overwrite(frozen_repository, tmp_path):
    root, _, frozen = frozen_repository
    draw, packets, report = tmp_path / "draw", tmp_path / "packets", tmp_path / "report"
    make_draw(draw, [row(frozen)])
    args = ["--draw-dir", str(draw), "--repositories-root", str(root), "--packet-dir", str(packets),
            "--report-dir", str(report)]
    assert retrieval.main(args) == 0
    manifest = json.loads((report / "retrieval-manifest.json").read_text())
    assert manifest["selected_rows"] == manifest["recorded_rows"] == 1
    assert manifest["complete_rule_evidence"] == manifest["labels_generated"] == manifest["model_calls"] == 0
    assert not list(report.glob("PROB-*.json"))
    with pytest.raises(SystemExit):
        retrieval.main(args)


def test_recovery_report_keeps_previous_failure_for_the_same_id(frozen_repository, tmp_path):
    root, _, frozen = frozen_repository
    draw = tmp_path / "draw"
    make_draw(draw, [row(frozen)])
    missing, old_report, new_report = tmp_path / "missing", tmp_path / "old-report", tmp_path / "new-report"
    retrieval.main(["--draw-dir", str(draw), "--repositories-root", str(missing),
                    "--packet-dir", str(tmp_path / "old-packets"), "--report-dir", str(old_report)])
    retrieval.main(["--draw-dir", str(draw), "--repositories-root", str(missing), "--repositories-root", str(root),
                    "--previous-report", str(old_report), "--packet-dir", str(tmp_path / "new-packets"),
                    "--report-dir", str(new_report)])
    result = list(retrieval.read_csv(new_report / "retrieval-ledger.csv"))[0]
    manifest = json.loads((new_report / "retrieval-manifest.json").read_text())
    assert result["sample_id"] == row(frozen)["sample_id"]
    assert result["sampling_weight"] == "17.5"
    assert result["previous_retrieval_status"] == "unavailable" and result["recovered_from_previous"] == "True"
    assert manifest["recovered_from_previous"] == 1
    assert manifest["previous_report_manifest_sha256"] == sha256(old_report / "retrieval-manifest.json")


def test_previous_report_with_changed_draw_identity_is_rejected(frozen_repository, tmp_path):
    root, _, frozen = frozen_repository
    draw, report = tmp_path / "draw", tmp_path / "report"
    make_draw(draw, [row(frozen)])
    retrieval.main(["--draw-dir", str(draw), "--repositories-root", str(root),
                    "--packet-dir", str(tmp_path / "packets"), "--report-dir", str(report)])
    with pytest.raises(ValueError, match="another selection draw"):
        retrieval.previous_report(report, "not-the-draw-hash", [row(frozen)])


def test_changed_selection_ledger_is_rejected_before_retrieval(tmp_path):
    draw = tmp_path / "draw"
    make_draw(draw, [row("a" * 40)])
    with (draw / "selection-ledger.csv").open("a") as target:
        target.write("\n")
    with pytest.raises(ValueError, match="hash mismatch"):
        retrieval.load_draw(draw)


@pytest.mark.parametrize("location", ["nested", "source-tree"])
def test_cli_rejects_overlapping_or_source_tree_outputs(frozen_repository, tmp_path, location):
    root, _, frozen = frozen_repository
    draw = tmp_path / "draw"
    make_draw(draw, [row(frozen)])
    report = tmp_path / "report"
    packets = report / "packets" if location == "nested" else root / "generated-packets"
    with pytest.raises(SystemExit):
        retrieval.main(["--draw-dir", str(draw), "--repositories-root", str(root),
                        "--packet-dir", str(packets), "--report-dir", str(report)])
    assert not report.exists() and not packets.exists()
