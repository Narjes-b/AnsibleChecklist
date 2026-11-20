import json
from pathlib import Path
from types import SimpleNamespace

from ansibleguard.module_metadata import build_module_metadata_index


def test_module_metadata_is_batched_instead_of_one_process_per_module(monkeypatch):
    calls = []

    def fake_run(command, **kwargs):
        calls.append(command)
        payload = {
            name: {"doc": {"module": name}}
            for name in command[2:]
        }
        return SimpleNamespace(
            returncode=0, stdout=json.dumps(payload), stderr=""
        )

    monkeypatch.setattr(
        "ansibleguard.module_metadata.ansible_doc_executable",
        lambda: "/bin/ansible-doc",
    )
    monkeypatch.setattr("ansibleguard.module_metadata.subprocess.run", fake_run)

    metadata, telemetry = build_module_metadata_index(
        ["copy", "debug", "ansible.builtin.user"], chunk_size=128
    )

    assert len(calls) == 1
    assert telemetry["subprocesses"] == 1
    assert "copy" in metadata
    assert "ansible.builtin.user" in metadata


def test_module_metadata_uses_private_ephemeral_ansible_temp(tmp_path, monkeypatch):
    observed = []

    def fake_run(command, **kwargs):
        observed.append(kwargs["env"]["ANSIBLE_LOCAL_TEMP"])
        return SimpleNamespace(returncode=0, stdout="{}", stderr="")

    monkeypatch.setenv("ANSIBLE_LOCAL_TEMP", str(tmp_path / "shared"))
    monkeypatch.setattr(
        "ansibleguard.module_metadata.ansible_doc_executable",
        lambda: "/bin/ansible-doc",
    )
    monkeypatch.setattr("ansibleguard.module_metadata.subprocess.run", fake_run)

    build_module_metadata_index(["copy"])
    build_module_metadata_index(["debug"])

    assert len(set(observed)) == 2
    assert all(path != str(tmp_path / "shared") for path in observed)
    assert all(not Path(path).exists() for path in observed)
