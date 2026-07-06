from pathlib import Path
from cli import collect_yaml_files


def test_single_file_target_returns_that_file(tmp_path):
    """Passing a single file (not a directory) should return exactly that
    file, not attempt directory traversal on it."""
    target = tmp_path / "playbook.yml"
    target.write_text("- name: play\n  hosts: all\n")
    result = collect_yaml_files(target)
    assert result == [target]


def test_finds_both_yml_and_yaml_extensions(tmp_path):
    (tmp_path / "a.yml").write_text("x: 1")
    (tmp_path / "b.yaml").write_text("x: 1")
    result = collect_yaml_files(tmp_path)
    names = {f.name for f in result}
    assert names == {"a.yml", "b.yaml"}


def test_recursive_discovery_finds_deeply_nested_files(tmp_path):
    """Regression test for the old glob('*.yml') behavior, which only
    ever found files in one flat folder — rglob() must find files no
    matter how deep the real project's role structure goes."""
    deep = tmp_path / "roles" / "tomcat" / "tasks"
    deep.mkdir(parents=True)
    (deep / "main.yml").write_text("x: 1")
    result = collect_yaml_files(tmp_path)
    assert result == [deep / "main.yml"]


def test_molecule_directory_excluded_at_any_depth(tmp_path):
    """Regression test confirming the real bug this exclusion list exists
    for: a role's molecule/ test scenarios contain real YAML but aren't
    production Ansible content, and 'molecule' can appear at any nesting
    depth (roles/tomcat/molecule/default/molecule.yml in a real project),
    not just as a top-level folder."""
    molecule_dir = tmp_path / "roles" / "tomcat" / "molecule" / "default"
    molecule_dir.mkdir(parents=True)
    (molecule_dir / "molecule.yml").write_text("x: 1")

    real_tasks = tmp_path / "roles" / "tomcat" / "tasks"
    real_tasks.mkdir(parents=True)
    (real_tasks / "main.yml").write_text("x: 1")

    result = collect_yaml_files(tmp_path)
    assert result == [real_tasks / "main.yml"]


def test_dotgit_and_dotgithub_excluded(tmp_path):
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config.yml").write_text("x: 1")
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / ".github" / "workflows" / "ci.yml").write_text("x: 1")
    (tmp_path / "site.yml").write_text("x: 1")

    result = collect_yaml_files(tmp_path)
    assert result == [tmp_path / "site.yml"]


def test_venv_directories_excluded(tmp_path):
    (tmp_path / ".venv" / "lib").mkdir(parents=True)
    (tmp_path / ".venv" / "lib" / "config.yml").write_text("x: 1")
    (tmp_path / "venv" / "lib").mkdir(parents=True)
    (tmp_path / "venv" / "lib" / "config.yml").write_text("x: 1")
    (tmp_path / "site.yml").write_text("x: 1")

    result = collect_yaml_files(tmp_path)
    assert result == [tmp_path / "site.yml"]


def test_empty_directory_returns_empty_list(tmp_path):
    assert collect_yaml_files(tmp_path) == []


def test_result_is_sorted(tmp_path):
    """collect_yaml_files() explicitly sorts its output — confirms that
    contract holds regardless of filesystem iteration order, which isn't
    guaranteed to be consistent across platforms."""
    (tmp_path / "zebra.yml").write_text("x: 1")
    (tmp_path / "alpha.yml").write_text("x: 1")
    (tmp_path / "middle.yml").write_text("x: 1")

    result = collect_yaml_files(tmp_path)
    assert result == sorted(result)
    assert [f.name for f in result] == ["alpha.yml", "middle.yml", "zebra.yml"]
