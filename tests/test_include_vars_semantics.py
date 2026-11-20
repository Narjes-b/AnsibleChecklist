from pathlib import Path

import pytest

from ansibleguard.include_vars_semantics import expand_include_vars_target


def test_expand_include_vars_target_on_regular_file(tmp_path):
    target = tmp_path / "vars.yml"
    target.write_text("a: 1\n", encoding="utf-8")
    assert expand_include_vars_target(target) == (target.resolve(),)


def test_expand_include_vars_target_expands_directory(tmp_path):
    (tmp_path / "a.yml").write_text("a: 1\n", encoding="utf-8")
    (tmp_path / "b.yaml").write_text("b: 2\n", encoding="utf-8")
    (tmp_path / "ignored.txt").write_text("not yaml\n", encoding="utf-8")
    result = expand_include_vars_target(tmp_path)
    assert result == tuple(sorted([(tmp_path / "a.yml").resolve(), (tmp_path / "b.yaml").resolve()]))


def test_permission_denied_on_is_dir_is_not_fatal(monkeypatch):
    """Regression test: a literal include_vars target can be an absolute
    path meaningful only on the target inventory host at playbook-run time
    (e.g. "/root/pull_variables.yml"), not on the machine doing this static
    analysis. Path.is_dir() can raise PermissionError for such a path, which
    previously propagated uncaught and crashed the whole repository's scan
    (observed on fgci-org/fgci-ansible during the v0.0.7.1 full-corpus run).
    It must be treated the same as "not a directory" instead."""

    def _raise_permission_error(self):
        raise PermissionError(13, "Permission denied")

    monkeypatch.setattr(Path, "is_dir", _raise_permission_error)
    result = expand_include_vars_target("/root/pull_variables.yml")
    assert result == (Path("/root/pull_variables.yml").resolve(),)


def test_other_os_error_on_is_dir_is_also_not_fatal(monkeypatch):
    def _raise_os_error(self):
        raise OSError("some other filesystem error")

    monkeypatch.setattr(Path, "is_dir", _raise_os_error)
    result = expand_include_vars_target("/some/unreadable/path")
    assert result == (Path("/some/unreadable/path").resolve(),)
