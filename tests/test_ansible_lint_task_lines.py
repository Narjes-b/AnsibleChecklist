"""ansible-lint task findings must point at the task they describe."""

import pytest
from importlib.metadata import version

from ansibleguard.external.ansible_lint import (
    lint_issue_line,
    scan_with_ansible_lint,
)

TASKS = """---
- name: Restart a
  ansible.builtin.shell: systemctl restart a

- name: Inner
  block:
    - name: Restart b
      ansible.builtin.shell: systemctl restart b
- name: Long value
  ansible.builtin.debug:
    msg: yes
"""


@pytest.mark.slow
def test_task_level_lint_lines_are_aligned_to_task_start(tmp_path):
    assert version("ansible-lint") == "26.4.0"
    (tmp_path / "tasks").mkdir()
    (tmp_path / "tasks" / "main.yml").write_text(TASKS, encoding="utf-8")

    result = scan_with_ansible_lint(tmp_path)

    by_rule = {}
    for issue in result.findings:
        by_rule.setdefault(issue["check_name"], set()).add(lint_issue_line(issue))
    assert by_rule["no-changed-when"] == {2, 7}
    assert by_rule["command-instead-of-shell"] == {2, 7}
    # yaml[...] problems are reported at their exact line and are not moved.
    assert by_rule["yaml[truthy]"] == {11}
    assert result.metadata["task_line_alignment"]["aligned_findings"] >= 4


def test_nested_task_alignment_does_not_depend_on_provider_rule_emission(tmp_path):
    from ansibleguard.external.ansible_lint import _align_task_lines

    (tmp_path / "tasks").mkdir()
    (tmp_path / "tasks" / "main.yml").write_text(TASKS, encoding="utf-8")
    issues = [{"check_name": "no-changed-when", "location": {
        "path": "tasks/main.yml", "lines": {"begin": 9}}}]
    assert _align_task_lines(issues, tmp_path) == 1
    assert lint_issue_line(issues[0]) == 7
    assert issues[0]["provider_reported_line"] == 9


def test_set_literals_in_lint_messages_have_a_stable_order():
    from ansibleguard.external.ansible_lint import _normalize_lint_issues

    def issue(message):
        return {"check_name": "redhat-ci[no-role-prefix]", "location": {"path": "tasks/main.yml", "lines": {"begin": 3}},
                "message": message}

    first, second = _normalize_lint_issues(
        [issue("prefix ({'global', 'ccp', 'create'} are possible)"),
         issue("prefix ({'create', 'global', 'ccp'} are possible)")],
        ".",
    )
    assert first["message"] == second["message"]
    assert first["fingerprint"] == second["fingerprint"]
