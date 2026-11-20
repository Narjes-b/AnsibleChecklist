"""Tests for the 7 new detectors added in the v2 improvements round (C1-C6, H4)."""

from pathlib import Path

import pytest

from ansibleguard.detectors.become_scope import detect_become_scope_too_broad
from ansibleguard.detectors.galaxy_meta import detect_galaxy_meta_incomplete
from ansibleguard.detectors.loop_legacy_syntax import detect_loop_legacy_syntax
from ansibleguard.detectors.molecule_test import detect_molecule_test_absent
from ansibleguard.detectors.role_documentation import detect_role_readme_absent
from ansibleguard.detectors.variable_naming import detect_variable_naming_convention
from ansibleguard.detectors.vault_structure import detect_vault_inline_overload


def _write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# C1 — role-readme-absent
# ---------------------------------------------------------------------------

def test_role_readme_absent_fires_when_no_readme(tmp_path):
    role = tmp_path / "roles" / "myrole"
    tasks_main = _write(role / "tasks" / "main.yml", "- debug:\n    msg: ok\n")
    count, details = detect_role_readme_absent(tasks_main)
    assert count == 1
    assert "myrole" in details[0]["message"]


def test_role_readme_absent_no_fire_when_readme_exists(tmp_path):
    role = tmp_path / "roles" / "myrole"
    tasks_main = _write(role / "tasks" / "main.yml", "- debug:\n    msg: ok\n")
    _write(role / "README.md", "# myrole\n")
    assert detect_role_readme_absent(tasks_main) == (0, [])


def test_role_readme_absent_only_fires_for_tasks_main(tmp_path):
    role = tmp_path / "roles" / "myrole"
    other = _write(role / "tasks" / "other.yml", "- debug:\n    msg: ok\n")
    assert detect_role_readme_absent(other) == (0, [])


# ---------------------------------------------------------------------------
# C2 — galaxy-meta-incomplete
# ---------------------------------------------------------------------------

def test_galaxy_meta_incomplete_fires_for_missing_fields(tmp_path):
    meta = _write(
        tmp_path / "meta" / "main.yml",
        "galaxy_info:\n  author: alice\n",
    )
    count, details = detect_galaxy_meta_incomplete(meta)
    assert count == 1
    assert "description" in details[0]["message"]
    assert "min_ansible_version" in details[0]["message"]


def test_galaxy_meta_complete_no_fire(tmp_path):
    meta = _write(
        tmp_path / "meta" / "main.yml",
        "galaxy_info:\n  author: alice\n  description: My role\n  min_ansible_version: '2.9'\n",
    )
    assert detect_galaxy_meta_incomplete(meta) == (0, [])


def test_galaxy_meta_missing_galaxy_info_fires(tmp_path):
    meta = _write(tmp_path / "meta" / "main.yml", "dependencies: []\n")
    count, details = detect_galaxy_meta_incomplete(meta)
    assert count == 1
    assert "no galaxy_info" in details[0]["message"]


def test_galaxy_meta_only_fires_for_meta_main(tmp_path):
    other = _write(tmp_path / "tasks" / "main.yml", "- debug:\n    msg: ok\n")
    assert detect_galaxy_meta_incomplete(other) == (0, [])


# ---------------------------------------------------------------------------
# C5 — variable-naming-convention
# ---------------------------------------------------------------------------

def test_variable_naming_convention_flags_unprefixed_var(tmp_path):
    role = tmp_path / "roles" / "myrole"
    defaults = _write(
        role / "defaults" / "main.yml",
        "port: 8080\nmyrole_name: myapp\n",
    )
    count, details = detect_variable_naming_convention(defaults)
    assert count == 1
    assert any("port" in d["message"] for d in details)
    assert all("myrole_name" not in d["message"] for d in details)


def test_variable_naming_convention_no_fire_when_all_prefixed(tmp_path):
    role = tmp_path / "roles" / "myrole"
    defaults = _write(
        role / "defaults" / "main.yml",
        "myrole_port: 8080\nmyrole_name: myapp\n",
    )
    assert detect_variable_naming_convention(defaults)[0] == 0


def test_variable_naming_convention_normalizes_hyphenated_role_name(tmp_path):
    role = tmp_path / "roles" / "my-role"
    defaults = _write(
        role / "defaults" / "main.yml",
        "my_role_port: 8080\nmyrole_name: app\n",
    )

    assert detect_variable_naming_convention(defaults) == (0, [])


def test_variable_naming_convention_skips_non_defaults_file(tmp_path):
    tasks = _write(tmp_path / "roles" / "myrole" / "tasks" / "main.yml", "- debug:\n    msg: ok\n")
    assert detect_variable_naming_convention(tasks) == (0, [])


# ---------------------------------------------------------------------------
# H4 — vault-inline-overload
# ---------------------------------------------------------------------------

def test_vault_inline_overload_fires_when_over_threshold(tmp_path):
    role = tmp_path / "roles" / "myrole"
    vault_content = "\n".join(
        f"var{i}: !vault |\n  $ANSIBLE_VAULT;1.1;AES256\n  abc{i}"
        for i in range(4)
    )
    _write(role / "defaults" / "main.yml", vault_content)
    tasks_main = _write(role / "tasks" / "main.yml", "- debug:\n    msg: ok\n")
    count, details = detect_vault_inline_overload(tasks_main)
    assert count == 1
    assert "4" in details[0]["message"]


def test_vault_inline_overload_no_fire_under_threshold(tmp_path):
    role = tmp_path / "roles" / "myrole"
    _write(role / "defaults" / "main.yml", "var1: !vault |\n  $ANSIBLE_VAULT;1.1;AES256\n  abc\n")
    tasks_main = _write(role / "tasks" / "main.yml", "- debug:\n    msg: ok\n")
    assert detect_vault_inline_overload(tasks_main) == (0, [])


def test_vault_inline_overload_only_fires_for_tasks_main(tmp_path):
    role = tmp_path / "roles" / "myrole"
    other = _write(role / "tasks" / "other.yml", "- debug:\n    msg: ok\n")
    assert detect_vault_inline_overload(other) == (0, [])


# ---------------------------------------------------------------------------
# C3 — become-scope-too-broad
# ---------------------------------------------------------------------------

def test_become_scope_too_broad_fires_for_large_play(tmp_path):
    tasks = "\n".join(
        f"    - name: Task {i}\n      debug:\n        msg: ok"
        for i in range(6)
    )
    playbook = _write(
        tmp_path / "site.yml",
        f"- name: Deploy\n  hosts: all\n  become: true\n  tasks:\n{tasks}\n",
    )
    count, details = detect_become_scope_too_broad(playbook)
    assert count == 1
    assert "Deploy" in details[0]["issue"]


def test_become_scope_too_broad_no_fire_for_small_play(tmp_path):
    playbook = _write(
        tmp_path / "site.yml",
        "- name: Deploy\n  hosts: all\n  become: true\n  tasks:\n    - name: T1\n      debug:\n        msg: ok\n",
    )
    assert detect_become_scope_too_broad(playbook) == (0, [])


def test_become_scope_too_broad_no_fire_without_become(tmp_path):
    tasks = "\n".join(
        f"    - name: Task {i}\n      debug:\n        msg: ok"
        for i in range(6)
    )
    playbook = _write(
        tmp_path / "site.yml",
        f"- name: Deploy\n  hosts: all\n  tasks:\n{tasks}\n",
    )
    assert detect_become_scope_too_broad(playbook) == (0, [])


# ---------------------------------------------------------------------------
# C4 — loop-legacy-syntax
# ---------------------------------------------------------------------------

def test_loop_legacy_syntax_fires_for_with_items(tmp_path):
    playbook = _write(
        tmp_path / "tasks.yml",
        "- name: Install pkgs\n  apt:\n    name: '{{ item }}'\n  with_items:\n    - nginx\n    - curl\n",
    )
    count, details = detect_loop_legacy_syntax(playbook)
    assert count == 1
    assert "with_items" in details[0]["issue"]


def test_loop_legacy_syntax_fires_for_with_dict(tmp_path):
    playbook = _write(
        tmp_path / "tasks.yml",
        "- name: Create users\n  user:\n    name: '{{ item.key }}'\n  with_dict:\n    alice: admin\n",
    )
    count, _ = detect_loop_legacy_syntax(playbook)
    assert count == 1


def test_loop_legacy_syntax_no_fire_for_loop(tmp_path):
    playbook = _write(
        tmp_path / "tasks.yml",
        "- name: Install pkgs\n  apt:\n    name: '{{ item }}'\n  loop:\n    - nginx\n    - curl\n",
    )
    assert detect_loop_legacy_syntax(playbook) == (0, [])


# ---------------------------------------------------------------------------
# C6 — molecule-test-absent
# ---------------------------------------------------------------------------

def test_molecule_test_absent_fires_when_no_molecule_dir(tmp_path):
    role = tmp_path / "roles" / "myrole"
    meta = _write(role / "meta" / "main.yml", "galaxy_info:\n  author: alice\n")
    tasks_main = _write(role / "tasks" / "main.yml", "- debug:\n    msg: ok\n")
    count, details = detect_molecule_test_absent(tasks_main)
    assert count == 1
    assert "myrole" in details[0]["issue"]


def test_molecule_test_absent_no_fire_when_molecule_exists(tmp_path):
    role = tmp_path / "roles" / "myrole"
    _write(role / "meta" / "main.yml", "galaxy_info:\n  author: alice\n")
    tasks_main = _write(role / "tasks" / "main.yml", "- debug:\n    msg: ok\n")
    (role / "molecule" / "default").mkdir(parents=True)
    assert detect_molecule_test_absent(tasks_main) == (0, [])


def test_molecule_test_absent_only_fires_for_role_anchor(tmp_path):
    role = tmp_path / "roles" / "myrole"
    _write(role / "meta" / "main.yml", "galaxy_info:\n  author: alice\n")
    other = _write(role / "tasks" / "other.yml", "- debug:\n    msg: ok\n")
    assert detect_molecule_test_absent(other) == (0, [])
