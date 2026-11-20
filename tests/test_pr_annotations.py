import io
import json

from ansibleguard.report.pr_annotations import (
    annotation_command,
    main,
    publish,
    render_markdown,
)


def occurrence(
    occurrence_id="new",
    *,
    severity="warning",
    file="tasks/main.yml",
    line=7,
    concept="shell-instead-of-module",
    message="Prefer a purpose-built module",
):
    return {
        "occurrence_id": occurrence_id,
        "severity": severity,
        "file": file,
        "line": line,
        "concept_id": concept,
        "message": message,
    }


def decision(introduced):
    return {
        "kind": "pr-comparison",
        "comparison": {
            "introduced": introduced,
            "unchanged": [occurrence("old")],
            "fixed": [occurrence("fixed")],
        },
    }


def test_annotation_preserves_severity_and_location():
    assert annotation_command(occurrence(severity="error")) == (
        "::error file=tasks/main.yml,line=7,"
        "title=AnsibleGuard [maintainability]%3A shell-instead-of-module::"
        "Prefer a purpose-built module"
    )
    assert annotation_command(occurrence(severity="note")).startswith("::notice ")


def test_annotation_escapes_workflow_command_data_and_properties():
    command = annotation_command(
        occurrence(
            file="tasks/a,b.yml",
            concept="rule:variant",
            message="first%\n::error::injected",
        )
    )
    assert "file=tasks/a%2Cb.yml" in command
    assert "title=AnsibleGuard [uncategorized]%3A rule%3Avariant" in command
    assert command.endswith("first%25%0A::error::injected")


def test_publish_emits_only_introduced_occurrences_and_truncates():
    stream = io.StringIO()
    emitted = publish(decision([occurrence("one"), occurrence("two")]), limit=1, stream=stream)
    output = stream.getvalue()
    assert emitted == 1
    assert output.count("file=tasks/main.yml") == 1
    assert "Showing 1 of 2 actionable introduced occurrences" in output
    assert "old" not in output


def test_markdown_summary_is_readable_and_escaped():
    text = render_markdown(
        [occurrence(message="Use shell | command\ncarefully")], total=2
    )
    assert "**2** introduced canonical occurrence(s)" in text
    assert "`tasks/main.yml:7`" in text
    assert "Use shell \\| command carefully" in text
    assert "Showing the first 1 of 2" in text


def test_optional_findings_are_collapsed_by_default_but_remain_in_summary():
    optional = occurrence("optional", concept="missing-tags")
    stream = io.StringIO()
    summary = io.StringIO()

    assert publish(decision([optional]), stream=stream, summary=summary) == 0
    assert "file=tasks/main.yml" not in stream.getvalue()
    assert "Collapsed 1 optional finding(s)" in stream.getvalue()
    assert "<summary>Optional policy findings (1)</summary>" in summary.getvalue()
    assert "missing-tags" in summary.getvalue()


def test_optional_findings_can_be_explicitly_annotated():
    optional = occurrence("optional", concept="missing-tags")
    stream = io.StringIO()

    assert publish(
        decision([optional]), stream=stream, include_optional=True
    ) == 1
    assert "title=AnsibleGuard [style]%3A missing-tags" in stream.getvalue()


def test_annotation_limit_prioritizes_risk_categories():
    maintainability = occurrence("maintainability")
    security = occurrence("security", concept="hardcoded-secret", severity="error")
    stream = io.StringIO()

    publish(decision([maintainability, security]), limit=1, stream=stream)

    assert "hardcoded-secret" in stream.getvalue()
    assert "shell-instead-of-module" not in stream.getvalue()


def test_cli_reads_decision_and_appends_summary(tmp_path, capsys):
    input_path = tmp_path / "decision.json"
    summary_path = tmp_path / "summary.md"
    input_path.write_text(json.dumps(decision([occurrence()])), encoding="utf-8")

    assert main([str(input_path), "--summary", str(summary_path)]) == 0
    assert "::warning file=tasks/main.yml,line=7" in capsys.readouterr().out
    assert "Introduced findings" in summary_path.read_text(encoding="utf-8")


def test_cli_rejects_non_comparison_document(tmp_path, capsys):
    input_path = tmp_path / "decision.json"
    input_path.write_text('{"kind": "run-report"}', encoding="utf-8")

    assert main([str(input_path)]) == 2
    assert "not an AnsibleGuard pr-comparison" in capsys.readouterr().err


def test_controlled_pr_acceptance_view_separates_actionable_optional_and_baseline():
    actionable = occurrence("introduced-error", severity="error")
    actionable["confidence"] = "high"
    actionable["remediation"] = "Use ansible.builtin.package."
    optional = occurrence("introduced-optional", concept="missing-tags")
    payload = decision([actionable, optional])
    stream = io.StringIO()
    summary = io.StringIO()

    emitted = publish(payload, stream=stream, summary=summary)

    assert emitted == 1
    assert "Suggested fix: Use ansible.builtin.package." in stream.getvalue()
    assert "introduced-optional" not in stream.getvalue()
    rendered = summary.getvalue()
    assert "**1 actionable** and **1 optional policy**" in rendered
    assert "Use ansible.builtin.package." in rendered
    assert "old" not in rendered
    assert "fixed" not in rendered


def test_annotation_rejects_paths_outside_repository():
    for file in ("/etc/passwd", "../outside.yml"):
        try:
            annotation_command(occurrence(file=file))
        except ValueError as exc:
            assert "repository-relative" in str(exc)
        else:
            raise AssertionError(f"unsafe path was accepted: {file}")
