import json
from pathlib import Path
import subprocess
import sys

import pytest

pytest.importorskip("resource")

from scripts import profile_frozen_context as probe
from scripts.retrieve_sample_evidence import FrozenGitSources
from tests.test_retrieve_sample_evidence import frozen_repository, git


def test_mirror_reads_exact_git_bytes_skips_symlinks_and_never_executes_scripts(frozen_repository, tmp_path):
    root, repository, _ = frozen_repository
    marker = tmp_path / "must-not-exist"
    script = repository / "untrusted.sh"
    script.write_text(f"#!/bin/sh\ntouch '{marker}'\n")
    script.chmod(0o755)
    (repository / "outside-link").symlink_to(marker)
    git(repository, "add", ".")
    git(repository, "commit", "-qm", "Add executable and link fixtures")
    frozen = git(repository, "rev-parse", "HEAD")
    old = (repository / "tasks.yml").read_bytes()
    (repository / "tasks.yml").write_text("changed working tree\n")
    records = probe.materialize(FrozenGitSources([root]), "o/repo", frozen, tmp_path / "mirror/source")
    assert (tmp_path / "mirror/source/tasks.yml").read_bytes() == old
    assert (tmp_path / "mirror/source/.git").is_dir()
    assert not (tmp_path / "mirror/source/outside-link").exists()
    assert not ((tmp_path / "mirror/source/untrusted.sh").stat().st_mode & 0o111)
    assert not marker.exists()
    assert next(r for r in records if r["path"] == "outside-link")["status"] == "skipped-nonregular"


@pytest.mark.parametrize("file_detectors", [False, True])
def test_worker_records_completed_context_and_symbol_stages_in_separate_process(tmp_path, file_detectors):
    source = tmp_path / "source"
    source.mkdir()
    (source / "tasks.yml").write_text("- name: Small task\n  debug: {msg: '{{ local_value }}'}\n  vars: {local_value: hello}\n")
    command = [sys.executable, str(Path(probe.__file__).resolve()),
                             "--worker-root", str(source), "--worker-dir", str(tmp_path / "work"),
                             "--stack-seconds", "5", "--memory-mib", "2048"]
    if file_detectors:
        command.append("--include-file-detectors")
    result = subprocess.run(command,
                            capture_output=True, timeout=20, cwd=Path(__file__).resolve().parents[1])
    assert result.returncode == 0, result.stderr.decode(errors="replace")
    report = json.loads((tmp_path / "work/worker-result.json").read_text())
    assert report["status"] == "completed" and report["selected_files"] == 1
    events = [json.loads(line) for line in (tmp_path / "work/events.jsonl").read_text().splitlines()]
    assert [(e["stage"], e["state"]) for e in events if e["stage"] in {"repository-context", "symbol-index"}] == [
        ("repository-context", "start"), ("repository-context", "end"), ("symbol-index", "start"), ("symbol-index", "end")]
    assert (tmp_path / "work/profile.pstats").stat().st_size > 0
    assert report["eligible_for_performance_scoring"] is False
    completed = [event for event in events if event["stage"].startswith("file-detectors:") and event["state"] == "end"]
    assert len(completed) == int(file_detectors)
    if file_detectors:
        assert completed[0]["structurally_analyzed"] is True
        assert completed[0]["detector_timings"] and completed[0]["detector_errors"] == 0


@pytest.mark.parametrize("project,commit", [("../escape", "a" * 40), ("owner/repo", "HEAD")])
def test_invalid_snapshot_identity_produces_no_outputs(tmp_path, project, commit):
    with pytest.raises(SystemExit) as exc:
        probe.main(["--project", project, "--commit", commit, "--repositories-root", str(tmp_path),
                    "--local-dir", str(tmp_path / "local"), "--report-dir", str(tmp_path / "report")])
    assert exc.value.code == 2 and not (tmp_path / "local").exists()
