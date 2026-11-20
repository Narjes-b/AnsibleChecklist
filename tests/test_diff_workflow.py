import json
import pytest

from ansibleguard.diff_workflow import (
    DiffWorkflowError,
    analyze_snapshot_jobs,
    compare_outputs,
    detect_variable_documentation_gaps,
    incremental_analysis_scope,
    mark_incremental_output_partial,
    parse_changed_lines,
    parse_renamed_files,
    snapshot_compatibility,
)
from ansibleguard.report.comparison import detect_breaking_changes_from_diff
from ansibleguard.report.playbook_summary import build_playbook_summary
from ansibleguard.report.output_contract import SCHEMA_VERSION


def occurrence(
    identity,
    file="site.yml",
    line=3,
    severity="warning",
    concept="missing-validate-certs",
):
    return {
        "occurrence_id": identity,
        "concept_id": concept,
        "file": file,
        "line": line,
        "scan_mode": "source",
        "severity": severity,
        "message": "Task needs review",
        "semantic_key": identity,
        "native_rules": [f"ansibleguard/{concept}"],
        "evidence_fingerprints": [],
        "detectors": [],
    }


def write_output(root, items):
    path = root / "canonical"
    path.mkdir(parents=True)
    (path / "occurrences.json").write_text(
        json.dumps({"kind": "canonical-occurrences", "items": items}),
        encoding="utf-8",
    )


def write_run_metadata(root, *, rules_sha="rules", tool_sha="tool"):
    payload = {
        "schema_version": SCHEMA_VERSION,
        "analysis_health": {"complete": True},
        "profile": {
            "name": "pr",
            "rules_sha256": rules_sha,
            "providers": ["ansibleguard", "ansible-lint", "gitleaks"],
            "ansible_lint_rules": [],
        },
        "reproducibility": {
            "ansibleguard_version": "0.0.5",
            "ansibleguard_git_sha": tool_sha,
            "rule_catalog_sha256": "catalog",
            "ansible_core_version": "2.20",
            "ansible_lint_version": "26.4",
            "gitleaks_version": "8.30",
            "config": {"sha256": "config"},
            "target_git_sha": "revision-may-differ",
        },
    }
    (root / "run_metadata.json").write_text(json.dumps(payload), encoding="utf-8")


def test_snapshot_compatibility_ignores_revision_but_rejects_semantic_change(tmp_path):
    base = tmp_path / "base"
    head = tmp_path / "head"
    base.mkdir()
    head.mkdir()
    write_run_metadata(base)
    write_run_metadata(head)
    assert snapshot_compatibility(base, head)["compatible"] is True

    write_run_metadata(head, rules_sha="different-rules")
    compatibility = snapshot_compatibility(base, head)
    assert compatibility["compatible"] is False
    assert compatibility["mismatches"][0]["field"] == "profile.rules_sha256"


@pytest.mark.parametrize("base_version", [None, "declared-leaf-tasks-v2"])
def test_snapshot_compatibility_rejects_changed_structural_metric_definition(tmp_path, base_version):
    base, head = tmp_path / "base", tmp_path / "head"
    base.mkdir()
    head.mkdir()
    write_run_metadata(base)
    write_run_metadata(head)
    if base_version is not None:
        path = base / "run_metadata.json"
        metadata = json.loads(path.read_text())
        metadata["reproducibility"]["structural_metrics_version"] = base_version
        path.write_text(json.dumps(metadata))
    path = head / "run_metadata.json"
    metadata = json.loads(path.read_text())
    metadata["reproducibility"]["structural_metrics_version"] = "declared-leaf-tasks-v3"
    path.write_text(json.dumps(metadata))
    compatibility = snapshot_compatibility(base, head)
    assert not compatibility["compatible"]
    assert any(m["field"] == "reproducibility.structural_metrics_version" for m in compatibility["mismatches"])


def test_compare_rejects_incompatible_snapshot_semantics(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    base = tmp_path / "base"
    head = tmp_path / "head"
    write_output(base, [])
    write_output(head, [])
    write_run_metadata(base, tool_sha="base-tool")
    write_run_metadata(head, tool_sha="head-tool")

    with pytest.raises(DiffWorkflowError, match="incompatible analysis semantics"):
        compare_outputs(base, head, tmp_path / "result", repo)


def test_contract_readers_reject_unknown_v005_envelopes(tmp_path):
    root = tmp_path / "output"
    (root / "canonical").mkdir(parents=True)
    (root / "canonical" / "occurrences.json").write_text(
        json.dumps({
            "schema_version": 999,
            "contract": "ansibleguard://schemas/output-v999.json",
            "kind": "canonical-occurrences",
            "items": [],
        }),
        encoding="utf-8",
    )

    with pytest.raises(DiffWorkflowError, match="invalid occurrence contract"):
        from ansibleguard.diff_workflow import load_occurrences
        load_occurrences(root)


def test_compare_rejects_equally_partial_snapshots(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    base = tmp_path / "base"
    head = tmp_path / "head"
    write_output(base, [])
    write_output(head, [])
    write_run_metadata(base)
    write_run_metadata(head)
    for root in (base, head):
        metadata = json.loads((root / "run_metadata.json").read_text())
        metadata["analysis_health"]["complete"] = False
        (root / "run_metadata.json").write_text(json.dumps(metadata))

    with pytest.raises(DiffWorkflowError, match="analysis_health"):
        compare_outputs(base, head, tmp_path / "result", repo)


def test_incompatible_snapshot_override_is_recorded(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    base = tmp_path / "base"
    head = tmp_path / "head"
    write_output(base, [])
    write_output(head, [])
    write_run_metadata(base, rules_sha="base-rules")
    write_run_metadata(head, rules_sha="head-rules")

    payload = compare_outputs(
        base,
        head,
        tmp_path / "result",
        repo,
        allow_incompatible_snapshots=True,
    )
    compatibility = payload["comparison"]["snapshot_compatibility"]
    assert compatibility["compatible"] is False
    assert compatibility["override_applied"] is True


def test_parse_changed_lines_handles_additions_deletions_and_files():
    changed = parse_changed_lines(
        """diff --git a/site.yml b/site.yml
--- a/site.yml
+++ b/site.yml
@@ -2,0 +3,2 @@
+one
+two
diff --git a/old.yml b/old.yml
--- a/old.yml
+++ b/old.yml
@@ -8 +7,0 @@
-gone
"""
    )
    assert changed == {"site.yml": {3, 4}, "old.yml": set()}


def test_parse_renamed_files_uses_explicit_git_metadata():
    diff = (
        "diff --git a/roles/apache/tasks/main.yml b/roles/httpd/tasks/main.yml\n"
        "similarity index 91%\n"
        "rename from roles/apache/tasks/main.yml\n"
        "rename to roles/httpd/tasks/main.yml\n"
    )
    assert parse_renamed_files(diff) == {
        "roles/apache/tasks/main.yml": "roles/httpd/tasks/main.yml"
    }


def test_compare_outputs_writes_diff_bundle_and_introduced_sarif(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "site.yml").write_text(
        "- name: Deploy\n  hosts: all\n  tasks:\n    - debug: {msg: ok}\n",
        encoding="utf-8",
    )
    base = tmp_path / "base"
    head = tmp_path / "head"
    write_output(base, [])
    write_output(head, [occurrence("new")])
    (head / "summary.csv").write_text(
        "file,new_pr_findings,pr_comparison_status\nsite.yml,,not-compared\n",
        encoding="utf-8",
    )
    (head / "summary").mkdir()
    (head / "summary" / "report.json").write_text(
        json.dumps({"artifacts": {}, "pr_comparison": {"status": "not-compared"}}),
        encoding="utf-8",
    )
    output = tmp_path / "result"

    payload = compare_outputs(
        base, head, output, repo,
        changed_lines={"site.yml": {3}}, policy_mode="observe",
    )

    assert payload["comparison"]["introduced"][0]["on_changed_line"] is True
    for name in (
        "comparison.json",
        "introduced.json",
        "introduced-actionable.json",
        "fixed.json",
        "playbooks.json",
        "introduced.sarif",
        "introduced-actionable.sarif",
        "summary.md",
    ):
        assert (output / "diff" / name).is_file()
    summary = (output / "diff" / "summary.md").read_text(encoding="utf-8")
    assert "site.yml" in summary
    assert "Introduced findings by category" in summary
    assert "Actionable introduced findings" in summary
    sarif = json.loads((output / "diff" / "introduced.sarif").read_text())
    assert sarif["runs"][0]["results"][0]["partialFingerprints"]
    assert "site.yml,1,compared" in (head / "summary.csv").read_text()
    head_report = json.loads((head / "summary" / "report.json").read_text())
    assert head_report["pr_comparison"]["introduced"] == 1
    assert head_report["pr_comparison"]["actionable"] == 1
    assert head_report["pr_comparison"]["optional"] == 0


def test_optional_findings_remain_in_evidence_but_not_actionable_sarif(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "site.yml").write_text("- hosts: all\n", encoding="utf-8")
    base = tmp_path / "base"
    head = tmp_path / "head"
    write_output(base, [])
    write_output(head, [occurrence("optional", line=1, concept="missing-tags")])

    compare_outputs(
        base,
        head,
        tmp_path / "result",
        repo,
        changed_lines={"site.yml": {1}},
        policy_mode="observe",
    )

    diff = tmp_path / "result" / "diff"
    assert len(json.loads((diff / "introduced.json").read_text())["items"]) == 1
    assert json.loads((diff / "introduced-actionable.json").read_text())["items"] == []
    assert len(json.loads((diff / "introduced.sarif").read_text())["runs"][0]["results"]) == 1
    assert json.loads((diff / "introduced-actionable.sarif").read_text())["runs"][0]["results"] == []
    summary = (diff / "summary.md").read_text(encoding="utf-8")
    assert "<summary>Optional policy findings (1)</summary>" in summary


def test_playbook_summary_marks_shared_role_without_double_counting(tmp_path):
    roles = tmp_path / "roles" / "common" / "tasks"
    roles.mkdir(parents=True)
    (roles / "main.yml").write_text("- debug: {msg: ok}\n", encoding="utf-8")
    for name in ("one.yml", "two.yml"):
        (tmp_path / name).write_text(
            "- hosts: all\n  roles:\n    - common\n", encoding="utf-8"
        )
    item = occurrence("shared", "roles/common/tasks/main.yml", 1)
    summary = build_playbook_summary(
        tmp_path,
        {"introduced": [item], "fixed": [], "unchanged": []},
        changed_files={"roles/common/tasks/main.yml"},
    )
    assert len(summary) == 2
    assert all(entry["findings"]["introduced"] == 1 for entry in summary)
    assert all(entry["shared_introduced_occurrence_ids"] == ["shared"] for entry in summary)


def test_playbook_summary_resolves_roles_relative_to_nested_playbook(tmp_path):
    tasks = tmp_path / "provisioning" / "roles" / "create_user" / "tasks"
    tasks.mkdir(parents=True)
    (tasks / "main.yml").write_text("- debug: {msg: ok}\n", encoding="utf-8")
    (tmp_path / "provisioning" / "playbook.yml").write_text(
        "- hosts: all\n  roles:\n    - create_user\n", encoding="utf-8"
    )
    item = occurrence(
        "nested-role", "provisioning/roles/create_user/tasks/main.yml", 1
    )

    summary = build_playbook_summary(
        tmp_path,
        {"introduced": [item], "fixed": [], "unchanged": []},
        changed_files={item["file"]},
    )

    assert len(summary) == 1
    assert summary[0]["affected"] is True
    assert summary[0]["findings"]["introduced"] == 1


def test_detect_breaking_changes_flags_task_rename():
    diff = (
        "diff --git a/tasks/main.yml b/tasks/main.yml\n"
        "--- a/tasks/main.yml\n"
        "+++ b/tasks/main.yml\n"
        "@@ -3 +3 @@\n"
        "-      name: Install nginx package\n"
        "+      name: Install the nginx web server\n"
    )
    results = detect_breaking_changes_from_diff(diff)
    assert len(results) == 1
    assert results[0]["type"] == "task-renamed"
    assert "nginx package" in results[0]["message"]
    assert "nginx web server" in results[0]["message"]


def test_incremental_scope_only_selects_explicitly_file_local_rules():
    scope = incremental_analysis_scope(
        {"roles/web/tasks/main.yml"},
        {"missing-tags", "unguarded-variable", "plaintext-sensitive-variable"},
    )

    assert scope["mode"] == "safe-file-local-subset"
    assert scope["file_local_rules"] == ["plaintext-sensitive-variable"]
    assert scope["deferred_rules"] == ["missing-tags", "unguarded-variable"]
    assert scope["requires_full_repository_analysis"] is True


def test_snapshot_jobs_have_stable_result_order_in_parallel_mode():
    calls = []

    def analyzer(label):
        calls.append(label)
        return f"done:{label}"

    results = analyze_snapshot_jobs(
        {"head": ("head",), "base": ("base",)}, analyzer, parallel=True
    )

    assert list(results) == ["base", "head"]
    assert results == {"base": "done:base", "head": "done:head"}
    assert sorted(calls) == ["base", "head"]


def test_incremental_output_marker_makes_run_metadata_ineligible_for_comparison(tmp_path):
    root = tmp_path / "incremental"
    (root / "metadata").mkdir(parents=True)
    (root / "summary").mkdir()
    payload = {"analysis_health": {"complete": True, "status": "completed"}}
    for relative in ("run_metadata.json", "metadata/run.json", "summary/report.json"):
        (root / relative).write_text(json.dumps(payload), encoding="utf-8")
    (root / "summary/run-summary.md").write_text(
        "# Trust summary\n\n- Run status: **completed**\n", encoding="utf-8"
    )

    mark_incremental_output_partial(root, changed_file="roles/web/tasks/main.yml")

    metadata = json.loads((root / "metadata/run.json").read_text())
    report = json.loads((root / "summary/report.json").read_text())
    assert metadata["analysis_health"]["complete"] is False
    assert metadata["incremental_analysis"]["comparison_eligible"] is False
    assert report["analysis_health"]["status"] == "partial"
    assert report["status"] == "partial"
    summary = (root / "summary/run-summary.md").read_text()
    assert "Run status: **partial**" in summary
    assert "not eligible for repository comparison" in summary


def test_detect_breaking_changes_flags_defaults_removal():
    diff = (
        "diff --git a/defaults/main.yml b/defaults/main.yml\n"
        "--- a/defaults/main.yml\n"
        "+++ b/defaults/main.yml\n"
        "@@ -2 +1,0 @@\n"
        "-myapp_port: 8080\n"
    )
    results = detect_breaking_changes_from_diff(diff)
    assert len(results) == 1
    assert results[0]["type"] == "defaults-variable-removed"
    assert "myapp_port" in results[0]["message"]


def test_detect_breaking_changes_no_false_positive_on_same_name():
    diff = (
        "diff --git a/tasks/main.yml b/tasks/main.yml\n"
        "--- a/tasks/main.yml\n"
        "+++ b/tasks/main.yml\n"
        "@@ -3 +3 @@\n"
        "-      name: Install nginx\n"
        "+      name: Install nginx\n"
    )
    results = detect_breaking_changes_from_diff(diff)
    assert results == []


def test_detect_breaking_changes_empty_diff_returns_empty():
    assert detect_breaking_changes_from_diff("") == []
    assert detect_breaking_changes_from_diff(None) == []


def test_breaking_change_parser_handles_real_task_yaml_and_context_lines():
    diff = """diff --git a/roles/web/tasks/main.yml b/roles/web/tasks/main.yml
--- a/roles/web/tasks/main.yml
+++ b/roles/web/tasks/main.yml
@@ -10,5 +10,5 @@
 - debug:
     msg: context
-- name: Install nginx
+- name: Install web server
   command: apt-get install nginx
"""

    results = detect_breaking_changes_from_diff(diff)

    assert len(results) == 1
    assert results[0]["type"] == "task-renamed"
    assert results[0]["line"] == 12


def test_compare_outputs_includes_breaking_changes_key(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "site.yml").write_text("- hosts: all\n", encoding="utf-8")
    base = tmp_path / "base"
    head = tmp_path / "head"
    write_output(base, [])
    write_output(head, [])
    output = tmp_path / "result"
    payload = compare_outputs(
        base, head, output, repo,
        policy_mode="observe",
        diff_text="",
    )
    assert "breaking_changes" in payload["comparison"]
    assert payload["comparison"]["breaking_changes"] == []


def test_detect_breaking_changes_flags_idempotency_guard_removal():
    diff = (
        "diff --git a/tasks/main.yml b/tasks/main.yml\n"
        "--- a/tasks/main.yml\n"
        "+++ b/tasks/main.yml\n"
        "@@ -5 +4,0 @@\n"
        "-        changed_when: false\n"
    )
    results = detect_breaking_changes_from_diff(diff)
    assert len(results) == 1
    assert results[0]["type"] == "idempotency-guard-removed"


def test_detect_breaking_changes_flags_ignore_errors_added():
    diff = (
        "diff --git a/tasks/main.yml b/tasks/main.yml\n"
        "--- a/tasks/main.yml\n"
        "+++ b/tasks/main.yml\n"
        "@@ -3 +3 @@\n"
        "+        ignore_errors: true\n"
    )
    results = detect_breaking_changes_from_diff(diff)
    assert len(results) == 1
    assert results[0]["type"] == "error-suppression-added"


def test_detect_variable_documentation_gaps_flags_undocumented_var(tmp_path):
    role = tmp_path / "roles" / "myrole"
    (role / "defaults").mkdir(parents=True)
    (role / "README.md").write_text("# myrole\nSome docs.\n", encoding="utf-8")
    diff = (
        "diff --git a/roles/myrole/defaults/main.yml b/roles/myrole/defaults/main.yml\n"
        "--- a/roles/myrole/defaults/main.yml\n"
        "+++ b/roles/myrole/defaults/main.yml\n"
        "@@ -1,0 +2 @@\n"
        "+myapp_port: 8080\n"
    )
    gaps = detect_variable_documentation_gaps(diff, tmp_path)
    assert len(gaps) == 1
    assert gaps[0]["type"] == "variable-undocumented"
    assert "myapp_port" in gaps[0]["message"]


def test_detect_variable_documentation_gaps_no_gap_when_readme_mentions_var(tmp_path):
    role = tmp_path / "roles" / "myrole"
    (role / "defaults").mkdir(parents=True)
    (role / "README.md").write_text("## Variables\n`myapp_port`: port number\n", encoding="utf-8")
    diff = (
        "diff --git a/roles/myrole/defaults/main.yml b/roles/myrole/defaults/main.yml\n"
        "--- a/roles/myrole/defaults/main.yml\n"
        "+++ b/roles/myrole/defaults/main.yml\n"
        "@@ -1,0 +2 @@\n"
        "+myapp_port: 8080\n"
    )
    gaps = detect_variable_documentation_gaps(diff, tmp_path)
    assert gaps == []


def test_detect_variable_documentation_gaps_empty_diff_returns_empty(tmp_path):
    assert detect_variable_documentation_gaps("", tmp_path) == []
    assert detect_variable_documentation_gaps(None, tmp_path) == []


def test_compare_outputs_includes_variable_doc_gaps_key(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "site.yml").write_text("- hosts: all\n", encoding="utf-8")
    base = tmp_path / "base"
    head = tmp_path / "head"
    write_output(base, [])
    write_output(head, [])
    payload = compare_outputs(
        base, head, tmp_path / "result", repo,
        policy_mode="observe",
        diff_text="",
    )
    assert "variable_doc_gaps" in payload["comparison"]
    assert payload["comparison"]["variable_doc_gaps"] == []


def _mark_provider_partial(root, *, internal="completed", category="PROVIDER_ERROR"):
    metadata = json.loads((root / "run_metadata.json").read_text())
    metadata["analysis_health"] = {
        "complete": False,
        "internal_status": internal,
        "providers": {"ansible_lint": "partial", "gitleaks": "completed"},
        "faults_by_category": {category: 1},
    }
    (root / "run_metadata.json").write_text(json.dumps(metadata))


def test_partial_external_provider_is_excluded_from_both_sides(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    base, head = tmp_path / "base", tmp_path / "head"
    lint_only_in_base = {**occurrence("lint-base"), "canonical_provider": "ansible-lint"}
    write_output(base, [occurrence("kept"), lint_only_in_base])
    write_output(head, [occurrence("kept"), occurrence("new", line=9, severity="error")])
    write_run_metadata(base)
    write_run_metadata(head)
    _mark_provider_partial(base)
    _mark_provider_partial(head)

    payload = compare_outputs(base, head, tmp_path / "result", repo)

    compatibility = payload["comparison"]["snapshot_compatibility"]
    assert compatibility["status"] == "partial"
    assert compatibility["excluded_providers"] == ["ansible-lint"]
    # The missing lint evidence is not reported as "fixed".
    assert [item["occurrence_id"] for item in payload["comparison"]["fixed"]] == []
    assert [item["occurrence_id"] for item in payload["comparison"]["introduced"]] == ["new"]
    summary = (tmp_path / "result" / "diff" / "summary.md").read_text()
    assert "Partial comparison" in summary and "`ansible-lint`" in summary


@pytest.mark.parametrize(
    "internal, category",
    [("partial", "PROVIDER_ERROR"), ("completed", "INTERNAL_DETECTOR_EXCEPTION")],
)
def test_incomplete_internal_analysis_still_refuses_comparison(tmp_path, internal, category):
    repo = tmp_path / "repo"
    repo.mkdir()
    base, head = tmp_path / "base", tmp_path / "head"
    write_output(base, [])
    write_output(head, [])
    write_run_metadata(base)
    write_run_metadata(head)
    _mark_provider_partial(head, internal=internal, category=category)

    with pytest.raises(DiffWorkflowError, match="analysis_health"):
        compare_outputs(base, head, tmp_path / "result", repo)


def _mark_parse_failure(root, path):
    metadata = json.loads((root / "run_metadata.json").read_text())
    metadata["analysis_health"] = {
        "complete": False, "internal_status": "completed",
        "providers": {"ansible_lint": "completed", "gitleaks": "completed"},
        "faults_by_category": {"PARSER_ERROR": 1},
    }
    (root / "run_metadata.json").write_text(json.dumps(metadata))
    (root / "diagnostics.json").write_text(json.dumps({"items": [
        {"file": path, "stage": "yaml-parse", "status": "invalid", "category": "PARSER_ERROR"}
    ]}))


def test_unparseable_file_is_excluded_instead_of_aborting(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    base, head = tmp_path / "base", tmp_path / "head"
    write_output(base, [occurrence("kept"), occurrence("docs", file="mkdocs.yml")])
    write_output(head, [occurrence("kept"), occurrence("new", line=9, severity="error")])
    write_run_metadata(base)
    write_run_metadata(head)
    _mark_parse_failure(base, "mkdocs.yml")
    _mark_parse_failure(head, "mkdocs.yml")

    payload = compare_outputs(base, head, tmp_path / "result", repo)

    assert payload["comparison"]["snapshot_compatibility"]["excluded_files"] == ["mkdocs.yml"]
    assert payload["comparison"]["fixed"] == []
    assert payload["policy"]["introduced_parse_failures"] == []
    assert "Not compared" in (tmp_path / "result" / "diff" / "summary.md").read_text()


def test_change_that_breaks_parsing_fails_the_policy(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    base, head = tmp_path / "base", tmp_path / "head"
    write_output(base, [])
    write_output(head, [])
    write_run_metadata(base)
    write_run_metadata(head)
    _mark_parse_failure(head, "site.yml")

    payload = compare_outputs(base, head, tmp_path / "result", repo, policy_mode="observe",
                              changed_lines={"site.yml": {3}})

    assert payload["policy"]["introduced_parse_failures"] == ["site.yml"]
    assert payload["policy"]["conclusion"] == "failure"


def test_identical_findings_shifted_by_an_insertion_are_moved_not_churned():
    from ansibleguard.report.comparison import compare_occurrences
    from ansibleguard.diff_workflow import parse_line_maps

    def truthy(identity, line):
        item = occurrence(identity, file="tasks.yml", line=line, concept="yaml-truthy")
        item["semantic_key"] = "same-key"  # identical findings share semantics
        return item

    base = [truthy("b10", 10), truthy("b20", 20), truthy("b30", 30)]
    # Two lines inserted after line 5; the finding at base line 20 was edited away.
    diff = "+++ b/tasks.yml\n@@ -5,0 +6,2 @@\n@@ -20 +22 @@\n"
    head = [truthy("h12", 12), truthy("h32", 32), truthy("h40", 40)]

    result = compare_occurrences(base, head, line_maps=parse_line_maps(diff))

    pairs = {(m["base"]["line"], m["head"]["line"]): m["match"] for m in result["moved"]}
    # Ambiguous identical findings are paired exactly where the diff moved them.
    assert pairs[(10, 12)].endswith("line-mapped")
    assert pairs[(30, 32)].endswith("line-mapped")
    # The single remaining identical pair is a unique semantic move (unchanged rule).
    assert pairs[(20, 40)] == "semantic"
    assert result["fixed"] == [] and result["introduced"] == []


def test_optional_policy_error_does_not_block_but_secret_does():
    from ansibleguard.report.comparison import evaluate_policy

    optional_error = {**occurrence("opt", severity="error", concept="missing-tags"),
                      "native_rules": ["ansibleguard/missing-tags"]}
    required_error = occurrence("req", severity="error", concept="insecure-permissions")
    required_error["native_rules"] = ["ansibleguard/insecure-permissions"]
    secret = {**occurrence("sec", severity="warning", concept="hardcoded-secret"),
              "native_rules": ["gitleaks/generic-api-key"]}

    assert evaluate_policy({"introduced": [optional_error]}, "ratchet")["conclusion"] == "success"
    assert evaluate_policy({"introduced": [required_error]}, "ratchet")["conclusion"] == "failure"
    assert evaluate_policy({"introduced": [secret]}, "observe")["conclusion"] == "failure"


def test_line_coincidence_does_not_pair_different_tasks():
    from ansibleguard.report.comparison import compare_occurrences
    from ansibleguard.diff_workflow import parse_line_maps

    def fqcn(line):
        item = occurrence(f"fqcn-{line}", file="tasks.yml", line=line, concept="fqcn")
        item["occurrence_id"] = f"fqcn|tasks.yml|{line}"  # identity includes the line
        item["semantic_key"] = "fqcn-set-fact"
        return item

    # Two identical set_fact tasks at 135/139 move to 139/143 (4 lines inserted above).
    base, head = [fqcn(135), fqcn(139)], [fqcn(139), fqcn(143)]
    result = compare_occurrences(base, head, line_maps=parse_line_maps("+++ b/tasks.yml\n@@ -12,0 +13,4 @@\n"))

    assert result["unchanged"] == []
    assert sorted((m["base"]["line"], m["head"]["line"]) for m in result["moved"]) == [(135, 139), (139, 143)]
    assert result["fixed"] == [] and result["introduced"] == []


def test_location_fingerprint_coincidence_is_not_a_move():
    from ansibleguard.report.comparison import compare_occurrences
    from ansibleguard.diff_workflow import parse_line_maps

    def lint(identity, line):
        item = occurrence(identity, file="tasks.yml", line=line, concept="fqcn")
        item["semantic_key"] = "fqcn-set-fact"
        item["evidence_fingerprints"] = [f"fqcn|tasks.yml|{line}"]  # provider fingerprint embeds the line
        return item

    base = [lint("b135", 135), lint("b139", 139)]
    head = [lint("h139", 139), lint("h143", 143)]
    result = compare_occurrences(base, head, line_maps=parse_line_maps("+++ b/tasks.yml\n@@ -12,0 +13,4 @@\n"))

    assert sorted((m["base"]["line"], m["head"]["line"]) for m in result["moved"]) == [(135, 139), (139, 143)]
    assert result["fixed"] == [] and result["introduced"] == []
