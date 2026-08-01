from ansibleguard.detectors.review_checklist import (
    detect_default_credentials,
    detect_insecure_permissions,
    detect_non_idempotent_commands,
    detect_redundant_default_values,
    detect_shell_environment_exports,
    detect_silent_error_suppression,
    detect_undocumented_complex_tasks,
    detect_unsafe_file_writes,
)
from ansibleguard.parser import mainn
from ansibleguard.report.findings import build_findings_list


def _write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_security_reliability_and_environment_checks(tmp_path):
    playbook = _write(
        tmp_path / "review.yml",
        """- name: Review checklist
  hosts: all
  vars:
    admin_password: admin
  tasks:
    - name: Unsafe permissions
      copy:
        content: secret
        dest: /tmp/secret
        mode: "0777"
    - name: Mutating command
      command: apt-get install nginx
    - name: Guarded command
      command: touch /tmp/ready
      args:
        creates: /tmp/ready
    - name: Hidden failure
      command: /bin/false
      ignore_errors: true
    - name: Inspected failure
      command: /bin/false
      ignore_errors: true
      register: failed_command
    - name: Shell environment
      shell: export APP_MODE=production; ./deploy.sh
""",
    )

    assert detect_insecure_permissions(playbook)[0] == 1
    assert detect_default_credentials(playbook)[0] == 1
    assert detect_non_idempotent_commands(playbook)[0] == 1
    suppression_count, suppression_details = detect_silent_error_suppression(playbook)
    assert suppression_count == 2
    assert any("never inspected later" in item["issue"] for item in suppression_details)
    assert detect_shell_environment_exports(playbook)[0] == 1


def test_redundant_role_default_value(tmp_path):
    role = tmp_path / "roles" / "web"
    _write(role / "defaults" / "main.yml", "web_port: 8080\n")
    tasks = _write(
        role / "tasks" / "main.yml",
        """- name: Repeat the default
  set_fact:
    web_port: 8080
- name: Real override
  set_fact:
    web_port: 9090
""",
    )

    count, details = detect_redundant_default_values(tasks)
    assert count == 1
    assert details[0]["variable"] == "web_port"


def test_only_complex_tasks_without_comments_are_reported(tmp_path):
    playbook = _write(
        tmp_path / "comments.yml",
        """- name: Comments
  hosts: all
  tasks:
    - name: Undocumented wrapper
      block:
        - name: Child
          debug:
            msg: ok
    # Explains why recovery grouping is required.
    - name: Documented wrapper
      block:
        - name: Other child
          debug:
            msg: ok
""",
    )

    count, details = detect_undocumented_complex_tasks(playbook)
    assert count == 1
    assert details[0]["task_name"] == "Undocumented wrapper"


def test_review_checks_flow_to_findings(tmp_path):
    playbook = _write(
        tmp_path / "flow.yml",
        """- name: Flow
  hosts: all
  vars:
    password: changeme
  tasks:
    - name: Unsafe file
      file:
        path: /tmp/open
        state: touch
        mode: "0666"
""",
    )
    metrics = mainn(playbook)
    assert metrics["insecure_permissions"] == 1
    assert metrics["default_credentials"] == 1

    result = {
        "playbook": {
            "metrics": {"WarningUnusedIncludeVars": []},
            "plays": [],
        }
    }
    findings = build_findings_list(metrics, result, [], [], playbook)
    rule_ids = {finding["rule_id"] for finding in findings}
    assert "insecure-permissions" in rule_ids
    assert "default-credentials" in rule_ids


def test_private_key_group_read_and_unsafe_writes_are_reported(tmp_path):
    playbook = _write(
        tmp_path / "permissions.yml",
        """- name: Install private key
  copy:
    content: key
    dest: /root/.ssh/id_rsa
    mode: "0640"
    unsafe_writes: true
""",
    )
    assert detect_insecure_permissions(playbook)[0] == 1
    assert detect_unsafe_file_writes(playbook)[0] == 1
