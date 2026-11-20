import json
import sys

import pytest

from scripts import profile_frozen_gitleaks as probe


def fake_provider(tmp_path, body):
    executable = tmp_path / "fake-gitleaks"
    executable.write_text("#!" + sys.executable + "\n" + body)
    executable.chmod(0o755)
    return executable


def test_worker_separates_native_and_postprocessing_checkpoints(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "tasks.yml").write_text("- debug: {msg: hello}\n")
    executable = fake_provider(tmp_path, """import sys,json
from pathlib import Path
report=Path(sys.argv[sys.argv.index('--report-path')+1])
report.write_text(json.dumps([{'File':'tasks.yml','StartLine':1,'RuleID':'test-rule','Secret':'REDACTED'}]))
sys.exit(1)
""")
    work = tmp_path / "work"
    assert probe.worker(source, work, executable, 5) == 0
    result = json.loads((work / "result.json").read_text())
    assert result["status"] == "completed" and result["findings"] == 1 and result["suppressed"] == 0
    events = [json.loads(line) for line in (work / "events.jsonl").read_text().splitlines()]
    assert [(e["stage"], e["state"]) for e in events] == [
        ("adapter", "start"), ("native-provider", "start"), ("native-provider", "end"),
        ("noise-postprocessing", "start"), ("noise-postprocessing", "end"), ("adapter", "end")]
    assert events[3]["distinct_files"] == 1 and events[3]["findings"] == 1
    assert result["eligible_for_performance_scoring"] is False
    assert (work / "profile.pstats").exists()


def test_native_timeout_is_retained_as_provider_timeout(tmp_path):
    executable = fake_provider(tmp_path, "import time\ntime.sleep(2)\n")
    assert probe.worker(tmp_path, tmp_path / "work", executable, .05) == 1
    result = json.loads((tmp_path / "work/result.json").read_text())
    assert result["status"] == "timeout" and result["metadata"]["failure_category"] == "TIMEOUT"


@pytest.mark.parametrize("native,worker", [(0, 2), (2, 1), (1, 1)])
def test_invalid_deadlines_rejected_before_output(tmp_path, native, worker):
    with pytest.raises(SystemExit):
        probe.main(["--gitleaks", str(tmp_path / "missing"), "--native-timeout", str(native), "--timeout", str(worker)])
    assert not (tmp_path / "work").exists()
