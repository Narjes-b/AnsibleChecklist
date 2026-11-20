from pathlib import Path
import subprocess
from types import SimpleNamespace
import pytest
from ansibleguard.cli import collect_yaml_files, _lint_location_path


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


def test_ansible_runtime_cache_excluded(tmp_path):
    (tmp_path / ".ansible" / "roles" / "cached").mkdir(parents=True)
    (tmp_path / ".ansible" / "roles" / "cached" / "main.yml").write_text("x: 1")
    (tmp_path / "site.yml").write_text("x: 1")
    assert collect_yaml_files(tmp_path) == [tmp_path / "site.yml"]


def test_nonexistent_lint_location_falls_back_to_repository_root(tmp_path):
    source = tmp_path / "roles" / "web" / "tasks" / "main.yml"
    source.parent.mkdir(parents=True)
    source.write_text("- include: missing.yml\n", encoding="utf-8")

    assert _lint_location_path("missing.yml", tmp_path) == tmp_path
    assert _lint_location_path(
        "roles/web/tasks/main.yml", tmp_path
    ) == source


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


def test_repository_local_symlink_does_not_duplicate_physical_yaml(tmp_path):
    target = tmp_path / "site.yml"
    target.write_text("- hosts: all\n", encoding="utf-8")
    alias = tmp_path / "test" / "integration" / "default.yml"
    alias.parent.mkdir(parents=True)
    alias.symlink_to(Path("../../site.yml"))

    assert collect_yaml_files(tmp_path) == [target]


def test_repository_external_yaml_symlink_is_not_followed(tmp_path):
    repository = tmp_path / "repo"
    repository.mkdir()
    outside = tmp_path / "outside.yml"
    outside.write_text("- hosts: all\n", encoding="utf-8")
    (repository / "external.yml").symlink_to(outside)

    assert collect_yaml_files(repository) == []


def test_broken_yaml_symlink_is_not_selected(tmp_path):
    (tmp_path / "broken.yml").symlink_to("missing.yml")

    assert collect_yaml_files(tmp_path) == []


def test_diff_incremental_plan_reports_deferred_semantic_rules(
    tmp_path, monkeypatch, capsys
):
    from ansibleguard import cli

    repository = tmp_path / "repository"
    repository.mkdir()

    def git_run(command, **_kwargs):
        if command[:3] == ["git", "rev-parse", "--show-toplevel"]:
            return SimpleNamespace(stdout=str(repository) + "\n")
        assert command[:2] == ["git", "diff"]
        return SimpleNamespace(
            stdout=(
                "diff --git a/roles/web/tasks/main.yml b/roles/web/tasks/main.yml\n"
                "+++ b/roles/web/tasks/main.yml\n"
                "@@ -1 +1 @@\n"
                "+- name: web\n"
            )
        )

    monkeypatch.setattr(subprocess, "run", git_run)

    assert cli.main(["diff", str(repository), "--incremental-plan"]) is None
    payload = __import__("json").loads(capsys.readouterr().out)
    assert payload["changed_files"] == ["roles/web/tasks/main.yml"]
    assert payload["mode"] == "safe-file-local-subset"
    assert "unguarded-variable" in payload["deferred_rules"]


def test_diff_runs_incremental_file_local_subset_as_explicit_partial_output(
    tmp_path, monkeypatch, capsys
):
    from ansibleguard import cli

    repository = tmp_path / "repository"
    task = repository / "roles" / "web" / "tasks" / "main.yml"
    task.parent.mkdir(parents=True)
    task.write_text("- debug: {msg: ok}\n", encoding="utf-8")
    calls = []

    def git_run(command, **_kwargs):
        if command[:3] == ["git", "rev-parse", "--show-toplevel"]:
            return SimpleNamespace(stdout=str(repository) + "\n")
        return SimpleNamespace(
            stdout=(
                "diff --git a/roles/web/tasks/main.yml b/roles/web/tasks/main.yml\n"
                "+++ b/roles/web/tasks/main.yml\n"
                "@@ -1 +1 @@\n"
                "+- debug: {msg: ok}\n"
            )
        )

    monkeypatch.setattr(subprocess, "run", git_run)
    monkeypatch.setattr(
        cli,
        "analyze_path",
        lambda target, output, _gitleaks, **kwargs: calls.append(
            (target, output, kwargs["profile"])
        ),
    )

    output = tmp_path / "output"
    assert cli.main([
        "diff", str(repository), "--run-incremental-file-local", "-o", str(output)
    ]) is None
    payload = __import__("json").loads(capsys.readouterr().out)
    assert payload["execution"] == "completed-partial-file-local"
    assert payload["analysis_health"]["complete"] is False
    assert payload["scanned_files"] == ["roles/web/tasks/main.yml"]
    assert calls[0][0] == task
    assert calls[0][2] == "incremental-file-local"
    assert (output / "incremental-file-local" / "incremental-plan.json").is_file()


def test_configuration_error_exits_with_usage_error(tmp_path, monkeypatch):
    from ansibleguard.cli import main
    from ansibleguard.detector_config import DetectorConfigError

    target = tmp_path / "site.yml"
    target.write_text("- debug: {msg: ok}\n", encoding="utf-8")
    monkeypatch.setattr(
        "ansibleguard.cli.analyze_path",
        lambda *a, **k: (_ for _ in ()).throw(DetectorConfigError("bad config")),
    )
    with pytest.raises(SystemExit) as exc:
        main([str(target), "--profile", "developer-fast"])
    assert exc.value.code == 2


def test_analysis_error_failure_policy(tmp_path, monkeypatch):
    from ansibleguard.cli import main

    target = tmp_path / "site.yml"
    target.write_text("- debug: {msg: ok}\n", encoding="utf-8")
    monkeypatch.setattr(
        "ansibleguard.cli.analyze_path",
        lambda *a, **k: {
            "findings": [],
            "tool_errors": 0,
            "parse_failures": 0,
            "analysis_failures": 1,
        },
    )
    with pytest.raises(SystemExit) as exc:
        main(
            [
                str(target),
                "--profile",
                "developer-fast",
                "--fail-on",
                "analysis-error",
            ]
        )
    assert exc.value.code == 1


def test_github_cli_materializes_source_then_uses_existing_analyzer(
    tmp_path, monkeypatch
):
    from ansibleguard.cli import main
    from ansibleguard.sources.snapshot import (
        MaterializedSource,
        SourceCapabilities,
        SourceSnapshot,
    )

    repository = tmp_path / "repository"
    repository.mkdir()
    (repository / "site.yml").write_text("- hosts: all\n", encoding="utf-8")
    constructed = {}
    analyzed = {}

    class Source:
        def __init__(self, target, **kwargs):
            constructed.update({"target": target, **kwargs})

        def materialize(self):
            return MaterializedSource(
                SourceSnapshot(
                    repository,
                    "github",
                    repository="owner/repo",
                    requested_ref="develop",
                    resolved_sha="a" * 40,
                    acquisition="git",
                    temporary=True,
                    capabilities=SourceCapabilities(
                        working_tree=True, git_history=True, diff=True
                    ),
                )
            )

    def analyze(target, output, *args, **kwargs):
        analyzed.update({"target": target, "output": output, **kwargs})
        return {
            "findings": [],
            "tool_errors": 0,
            "parse_failures": 0,
            "analysis_failures": 0,
        }

    monkeypatch.setattr("ansibleguard.sources.github.provider.GitHubSource", Source)
    monkeypatch.setattr("ansibleguard.cli.analyze_path", analyze)

    main(
        [
            "github",
            "owner/repo",
            "--ref",
            "develop",
            "--output",
            str(tmp_path / "output"),
            "--fail-on",
            "never",
            "--no-cache",
        ]
    )

    assert constructed["target"] == "owner/repo"
    assert constructed["ref"] == "develop"
    assert constructed["history_required"] is True
    assert analyzed["target"] == repository
    assert analyzed["source_snapshot"].resolved_sha == "a" * 40


def test_github_source_only_profile_does_not_require_git_history(
    tmp_path, monkeypatch
):
    from ansibleguard.cli import main
    from ansibleguard.sources.snapshot import MaterializedSource, SourceSnapshot

    repository = tmp_path / "repository"
    repository.mkdir()
    observed = {}

    class Source:
        def __init__(self, target, **kwargs):
            observed.update(kwargs)

        def materialize(self):
            return MaterializedSource(SourceSnapshot(repository, "github"))

    monkeypatch.setattr("ansibleguard.sources.github.provider.GitHubSource", Source)
    monkeypatch.setattr(
        "ansibleguard.cli.analyze_path",
        lambda *args, **kwargs: {
            "findings": [],
            "tool_errors": 0,
            "parse_failures": 0,
            "analysis_failures": 0,
        },
    )
    main(
        [
            "github",
            "owner/repo",
            "--profile",
            "quality",
            "--fail-on",
            "never",
            "--no-cache",
        ]
    )
    assert observed["history_required"] is False


def test_github_diff_resolves_two_refs_through_shared_comparison(
    tmp_path, monkeypatch
):
    from ansibleguard.cli import main

    created = []

    class Client:
        def __init__(self, host):
            self.host = host

    class Source:
        def __init__(self, target, **kwargs):
            created.append((target, kwargs))

    def compare(**kwargs):
        (kwargs["output"] / "diff").mkdir(parents=True)
        (kwargs["output"] / "diff" / "summary.md").write_text("summary")
        return {"policy": {"conclusion": "success"}}

    monkeypatch.setattr("ansibleguard.sources.github.client.GitHubClient", Client)
    monkeypatch.setattr("ansibleguard.sources.github.provider.GitHubSource", Source)
    monkeypatch.setattr("ansibleguard.cli._compare_github_snapshots", compare)

    main(
        [
            "github-diff",
            "owner/repo",
            "--base",
            "main",
            "--head",
            "feature/security",
            "--output",
            str(tmp_path / "output"),
            "--no-cache",
        ]
    )
    assert created[0][1]["ref"] == "main"
    assert created[1][1]["ref"] == "feature/security"
    assert created[0][1]["client"] is created[1][1]["client"]


def test_github_pr_uses_fork_head_repository_and_optional_comment(
    tmp_path, monkeypatch
):
    from ansibleguard.cli import main
    from ansibleguard.sources.github.pr import GitHubPullRequest

    created = []
    comments = []

    class Client:
        def __init__(self, host):
            self.host = host

    class Source:
        def __init__(self, target, **kwargs):
            created.append((target, kwargs))

    class Publisher:
        def __init__(self, client, repository):
            self.repository = repository

        def publish(self, number, summary):
            comments.append((self.repository, number, summary))

    def compare(**kwargs):
        (kwargs["output"] / "diff").mkdir(parents=True)
        (kwargs["output"] / "diff" / "summary.md").write_text("PR summary")
        return {"policy": {"conclusion": "success"}}

    monkeypatch.setattr("ansibleguard.sources.github.client.GitHubClient", Client)
    monkeypatch.setattr("ansibleguard.sources.github.provider.GitHubSource", Source)
    monkeypatch.setattr(
        "ansibleguard.sources.github.pr.resolve_pull_request",
        lambda *args: GitHubPullRequest(
            42, "company/base", "a" * 40, "person/fork", "b" * 40
        ),
    )
    monkeypatch.setattr(
        "ansibleguard.sources.github.comments.GitHubCommentPublisher", Publisher
    )
    monkeypatch.setattr("ansibleguard.cli._compare_github_snapshots", compare)

    main(
        [
            "github-pr",
            "company/base",
            "42",
            "--comment",
            "--output",
            str(tmp_path / "output"),
            "--no-cache",
        ]
    )

    assert created[0][0] == "company/base"
    assert created[0][1]["commit"] == "a" * 40
    assert created[1][0] == "person/fork"
    assert created[1][1]["commit"] == "b" * 40
    assert comments == [("company/base", 42, "PR summary")]


def test_gitlab_cli_uses_common_snapshot_analyzer(tmp_path, monkeypatch):
    from ansibleguard.cli import main
    from ansibleguard.sources.snapshot import (
        MaterializedSource,
        SourceCapabilities,
        SourceSnapshot,
    )

    repository = tmp_path / "repository"
    repository.mkdir()
    observed = {}

    class Source:
        def __init__(self, target, **kwargs):
            observed.update({"target": target, **kwargs})

        def materialize(self):
            return MaterializedSource(
                SourceSnapshot(
                    repository,
                    "gitlab",
                    repository="group/project",
                    resolved_sha="c" * 40,
                    capabilities=SourceCapabilities(
                        working_tree=True, git_history=True, diff=True
                    ),
                )
            )

    monkeypatch.setattr("ansibleguard.sources.gitlab.provider.GitLabSource", Source)
    monkeypatch.setattr(
        "ansibleguard.cli.analyze_path",
        lambda *args, **kwargs: {
            "findings": [],
            "tool_errors": 0,
            "parse_failures": 0,
            "analysis_failures": 0,
        },
    )
    main(
        [
            "gitlab",
            "group/project",
            "--ref",
            "develop",
            "--no-cache",
            "--fail-on",
            "never",
        ]
    )
    assert observed["target"] == "group/project"
    assert observed["ref"] == "develop"
    assert observed["history_required"] is True


def test_cache_info_and_clean_commands(tmp_path, capsys):
    from ansibleguard.cli import main

    cache = tmp_path / "cache"
    main(["cache", "info", "--cache-dir", str(cache)])
    info = capsys.readouterr().out
    assert '"backend": "filesystem"' in info
    main(["cache", "clean", "--cache-dir", str(cache)])
    cleaned = capsys.readouterr().out
    assert '"removed": 0' in cleaned
