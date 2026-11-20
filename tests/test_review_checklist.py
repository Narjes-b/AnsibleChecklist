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
from ansibleguard.symbol_index import build_repository_symbol_index


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
    assert detect_shell_environment_exports(playbook)[0] == 0


def test_default_credential_key_requires_a_real_sensitive_name(tmp_path):
    variables = _write(
        tmp_path / "vars.yml",
        "notokenusr: test\n"
        "api_db_userpass: changeme\n",
    )

    count, details = detect_default_credentials(variables)

    assert count == 1
    assert details[0]["credential_key"] == "api_db_userpass"


def test_default_credentials_ignore_explicit_example_trees(tmp_path):
    example = _write(
        tmp_path / "molecule" / "default" / "converge.yml",
        "admin_password: changeme\n",
    )
    production = _write(tmp_path / "vars" / "main.yml", "admin_password: changeme\n")

    assert detect_default_credentials(example) == (0, [])
    assert detect_default_credentials(production)[0] == 1


def test_export_only_shell_task_is_not_durable_configuration(tmp_path):
    playbook = _write(
        tmp_path / "exports.yml",
        "- name: Ineffective export\n"
        "  shell: export APP_MODE=production\n",
    )

    assert detect_shell_environment_exports(playbook)[0] == 1


def test_registered_state_check_does_not_automatically_guard_mutation(tmp_path):
    playbook = _write(
        tmp_path / "guarded.yml",
        "- name: Inspect module state\n"
        "  command: yum module list nodejs --disabled\n"
        "  changed_when: false\n"
        "  register: nodejs_disabled\n"
        "- name: Disable module only when needed\n"
        "  command: yum module disable -y nodejs\n"
        "  when: AppStream not in nodejs_disabled.stdout\n",
    )

    count, details = detect_non_idempotent_commands(playbook)

    assert count == 1
    assert details[0]["task_name"] == "Disable module only when needed"


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


def test_set_fact_cacheable_option_is_not_a_redundant_role_default(tmp_path):
    role = tmp_path / "roles" / "web"
    _write(role / "defaults" / "main.yml", "cacheable: true\n")
    tasks = _write(
        role / "tasks" / "main.yml",
        "- name: Cache actual fact\n"
        "  ansible.builtin.set_fact:\n"
        "    cacheable: true\n"
        "    web_port: 8080\n",
    )

    assert detect_redundant_default_values(tasks) == (0, [])


def test_runtime_reset_after_prior_assignment_is_not_redundant(tmp_path):
    role = tmp_path / "roles" / "web"
    _write(role / "defaults" / "main.yml", "web_port: 8080\n")
    tasks = _write(
        role / "tasks" / "main.yml",
        "- name: Initialize\n"
        "  set_fact:\n"
        "    web_port: 8080\n"
        "- name: Runtime transition\n"
        "  set_fact:\n"
        "    web_port: 9090\n"
        "- name: Restore configured state\n"
        "  set_fact:\n"
        "    web_port: 8080\n",
    )

    count, details = detect_redundant_default_values(tasks)

    assert count == 1
    assert details[0]["task_name"] == "Initialize"


def test_conditional_default_assignment_is_not_redundant(tmp_path):
    role = tmp_path / "roles" / "web"
    _write(role / "defaults" / "main.yml", "web_port: 8080\n")
    tasks = _write(
        role / "tasks" / "main.yml",
        "- name: Conditional assignment\n"
        "  set_fact:\n"
        "    web_port: 8080\n"
        "  when: restore_defaults | default(false)\n",
    )

    assert detect_redundant_default_values(tasks) == (0, [])


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

    # Structural wrappers alone are ordinary Ansible and are not complexity.
    count, details = detect_undocumented_complex_tasks(playbook)
    assert count == 0
    assert details == []


def test_only_objectively_complex_undocumented_conditions_are_reported(tmp_path):
    playbook = _write(
        tmp_path / "complex.yml",
        "- name: Ordinary condition\n"
        "  debug:\n    msg: ok\n"
        "  when: enabled and supported\n"
        "- name: Complex undocumented condition\n"
        "  debug:\n    msg: risky\n"
        "  when: a and b or c and d or e\n"
        "# Compatibility rationale for the exceptional branch.\n"
        "- name: Complex documented condition\n"
        "  debug:\n    msg: explained\n"
        "  when: a and b or c and d or e\n",
    )

    count, details = detect_undocumented_complex_tasks(playbook)

    assert count == 1
    assert details[0]["task_name"] == "Complex undocumented condition"
    assert "4 boolean operators" in details[0]["issue"]


def test_repeated_task_names_use_their_own_source_line_for_comments(tmp_path):
    playbook = _write(
        tmp_path / "repeated-names.yml",
        "# Rationale for only the first occurrence.\n"
        "- name: Repeated task\n"
        "  debug:\n    msg: first\n"
        "  when: a and b or c and d or e\n"
        "- name: Repeated task\n"
        "  debug:\n    msg: second\n"
        "  when: a and b or c and d or e\n",
    )

    count, details = detect_undocumented_complex_tasks(playbook)

    assert count == 1
    assert details[0]["line"] == 6


def test_registered_name_in_later_task_title_is_not_recovery(tmp_path):
    playbook = _write(
        tmp_path / "suppression.yml",
        "- name: Attempt operation\n"
        "  command: /bin/false\n"
        "  ignore_errors: true\n"
        "  register: failed_command\n"
        "- name: Document failed_command for humans\n"
        "  debug:\n    msg: no semantic reference\n",
    )

    assert detect_silent_error_suppression(playbook)[0] == 1


def test_registered_result_used_in_later_condition_is_recovery(tmp_path):
    playbook = _write(
        tmp_path / "suppression.yml",
        "- name: Attempt operation\n"
        "  command: /bin/false\n"
        "  ignore_errors: true\n"
        "  register: failed_command\n"
        "- name: Recover explicitly\n"
        "  debug:\n    msg: recovered\n"
        "  when: failed_command.rc != 0\n",
    )

    assert detect_silent_error_suppression(playbook) == (0, [])


def test_registered_result_used_by_later_assert_is_recovery(tmp_path):
    playbook = _write(
        tmp_path / "suppression.yml",
        "- name: Probe\n  command: /bin/false\n"
        "  ignore_errors: true\n  register: probe_result\n"
        "- name: Validate probe\n  assert:\n"
        "    that: probe_result.rc in [0, 1]\n",
    )

    assert detect_silent_error_suppression(playbook) == (0, [])


def test_registered_result_inspected_in_another_task_file_is_recovery(tmp_path):
    producer = _write(
        tmp_path / "roles" / "web" / "tasks" / "prepare.yml",
        "- name: Attempt operation\n  command: /bin/false\n"
        "  ignore_errors: true\n  register: failed_command\n",
    )
    _write(
        tmp_path / "roles" / "web" / "tasks" / "recover.yml",
        "- name: Recover\n  debug: {msg: recovered}\n"
        "  when: failed_command.rc != 0\n",
    )
    _write(
        tmp_path / "roles" / "web" / "tasks" / "main.yml",
        "- import_tasks: prepare.yml\n- import_tasks: recover.yml\n",
    )
    index = build_repository_symbol_index(tmp_path)

    assert detect_silent_error_suppression(producer, symbol_index=index) == (0, [])


def test_unrelated_role_reference_does_not_hide_silent_suppression(tmp_path):
    producer = _write(
        tmp_path / "roles" / "web" / "tasks" / "prepare.yml",
        "- name: Attempt operation\n  command: /bin/false\n"
        "  ignore_errors: true\n  register: failed_command\n",
    )
    _write(
        tmp_path / "roles" / "db" / "tasks" / "main.yml",
        "- name: Inspect unrelated result\n  debug: {msg: ok}\n"
        "  when: failed_command.rc != 0\n",
    )
    index = build_repository_symbol_index(tmp_path)

    assert detect_silent_error_suppression(producer, symbol_index=index)[0] == 1


def test_ignore_errors_does_not_treat_unreachable_rescue_as_recovery(tmp_path):
    playbook = _write(
        tmp_path / "rescue.yml",
        "- name: Recovery wrapper\n"
        "  block:\n"
        "    - name: Suppressed failure\n"
        "      command: /bin/false\n"
        "      ignore_errors: true\n"
        "      register: failed_command\n"
        "  rescue:\n"
        "    - name: This rescue is bypassed by ignore_errors\n"
        "      debug: {msg: '{{ failed_command.rc }}'}\n",
    )

    assert detect_silent_error_suppression(playbook)[0] == 1


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


def test_setgid_shared_directory_with_group_is_intentional(tmp_path):
    playbook = _write(
        tmp_path / "shared.yml",
        "- name: Shared group directory\n"
        "  file:\n"
        "    path: /srv/shared\n"
        "    state: directory\n"
        "    group: developers\n"
        "    mode: '2775'\n",
    )

    assert detect_insecure_permissions(playbook) == (0, [])


def test_world_writable_setgid_directory_is_still_insecure(tmp_path):
    playbook = _write(
        tmp_path / "shared.yml",
        "- name: Unsafe shared directory\n"
        "  file:\n"
        "    path: /srv/shared\n"
        "    state: directory\n"
        "    group: developers\n"
        "    mode: '2777'\n",
    )

    assert detect_insecure_permissions(playbook)[0] == 1


def test_h5_sensitive_file_without_explicit_mode_fires(tmp_path):
    playbook = _write(
        tmp_path / "deploy.yml",
        """- name: Deploy
  hosts: all
  tasks:
    - name: Write credentials config
      template:
        src: db_password.j2
        dest: /etc/app/db_password.conf
""",
    )
    count, details = detect_insecure_permissions(playbook)
    assert count == 1
    assert details[0]["mode"] == "(unset)"
    assert "umask" in details[0]["issue"]


def test_h5_no_false_positive_when_mode_is_set(tmp_path):
    playbook = _write(
        tmp_path / "deploy.yml",
        """- name: Deploy
  hosts: all
  tasks:
    - name: Write credentials config with restricted mode
      template:
        src: db_password.j2
        dest: /etc/app/db_password.conf
        mode: "0600"
""",
    )
    count, _ = detect_insecure_permissions(playbook)
    assert count == 0


def test_h5_no_false_positive_for_nonsensitive_file(tmp_path):
    playbook = _write(
        tmp_path / "deploy.yml",
        """- name: Deploy
  hosts: all
  tasks:
    - name: Write nginx config
      template:
        src: nginx.conf.j2
        dest: /etc/nginx/nginx.conf
""",
    )
    count, _ = detect_insecure_permissions(playbook)
    assert count == 0


def test_pipeline_ending_in_umount_is_not_read_only():
    from ansibleguard.detectors.review_checklist import _is_read_only_command
    assert _is_read_only_command("cat /proc/mounts")
    assert not _is_read_only_command("grep /mnt /proc/mounts | awk '{print $2}' | xargs umount")
    assert not _is_read_only_command("find /tmp -name x; rm -rf /tmp/x")
