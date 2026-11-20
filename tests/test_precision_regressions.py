from packaging.version import Version

from ansibleguard.detectors.credentials_leaking_in_log import (
    detect_credentials_leaking_in_log,
)
from ansibleguard.detectors.deprecated_modules import detect_deprecated_modules
from ansibleguard.detectors.filters_for_comparison import check_missing_bool_filter
from ansibleguard.detectors.missing_tags import detect_missing_tags
from ansibleguard.detectors.files_extensions import check_missing_extension
from ansibleguard.detectors.handler_issues import detect_handler_issues
from ansibleguard.detectors.paper_candidates import detect_unguarded_variables
from ansibleguard.detectors.partial_checklist import (
    detect_invalid_task_attribute_types,
    detect_unscoped_shell_variables,
    detect_unused_registered_variables,
)
from ansibleguard.detectors.review_checklist import (
    detect_insecure_permissions,
    detect_non_idempotent_commands,
    detect_read_only_command_changes,
)
from ansibleguard.report.findings import RULE_CATALOG
from ansibleguard.symbol_index import build_repository_symbol_index


def _write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_jinja_none_is_a_literal_not_an_unguarded_variable(tmp_path):
    variables = _write(
        tmp_path / "group_vars" / "all" / "docker.yml",
        "docker_users: '{{ candidate | default(None) }}'\n",
    )

    count, details = detect_unguarded_variables(variables)

    assert count == 0
    assert details == []


def test_jinja_null_and_nested_default_text_are_not_variables(tmp_path):
    variables = _write(
        tmp_path / "defaults.yml",
        """optional_user: "{{ lookup('env', 'USER') | default(null) }}"
install_path: "{{ app_home | default('/opt/apache-app-{{ app_version }}') }}"
""",
    )

    count, details = detect_unguarded_variables(variables)

    assert count == 0
    assert details == []


def test_jinja_control_keywords_are_not_unguarded_variables(tmp_path):
    variables = _write(
        tmp_path / "group_vars" / "all" / "devices.yml",
        """device_guests: |-
  {% for guest in guests | default([]) %}
  - {{ guest.name }}
  {% endfor %}
""",
    )

    count, details = detect_unguarded_variables(variables)

    assert count == 0
    assert details == []


def test_jinja_tuple_loop_set_and_loop_object_are_local(tmp_path):
    variables = _write(
        tmp_path / "group_vars" / "all" / "mounts.yml",
        """mount_lines: |-
  {% set output = namespace(items=[]) %}
  {% for key, value in mounts | default({}) | dictsort %}
  {{ loop.index0 }}={{ key }}={{ value }}
  {% set output.items = output.items + [key] %}
  {% endfor %}
  {{ output.items | join(',') }}
""",
    )

    assert detect_unguarded_variables(variables) == (0, [])


def test_jinja_keyword_arguments_and_fqcn_tests_are_not_variables(tmp_path):
    playbook = _write(
        tmp_path / "expressions.yml",
        """- hosts: all
  vars:
    entries: []
    config: {}
    result: {}
  tasks:
    - debug:
        msg: "{{ entries | map(attribute='name') | list }}"
    - debug:
        msg: "{{ lookup('fileglob', '*.yml', wantlist=True) }}"
    - debug:
        msg: "{{ config | to_nice_yaml(indent=2) }}"
      when:
        - result is ansible.builtin.succeeded
        - result.enabled is truthy
""",
    )

    assert detect_unguarded_variables(playbook) == (0, [])


def test_loop_index_variable_is_visible_to_task_expressions(tmp_path):
    playbook = _write(
        tmp_path / "loop.yml",
        """- name: Display indexed item
  debug:
    msg: "{{ index }}={{ entry }}"
  loop: "{{ entries | default([]) }}"
  loop_control:
    loop_var: entry
    index_var: index
""",
    )

    assert detect_unguarded_variables(playbook) == (0, [])


def test_include_vars_namespace_is_a_visible_definition(tmp_path):
    playbook = _write(
        tmp_path / "include.yml",
        """- name: Load status
  include_vars:
    file: /tmp/status.yml
    name: installed_components
- name: Inspect status
  debug:
    msg: "{{ installed_components.version }}"
""",
    )

    assert detect_unguarded_variables(playbook) == (0, [])
    index = build_repository_symbol_index(tmp_path)
    assert "installed_components" in index.names
    assert any(
        item.kind == "included-vars-namespace" for item in index.definitions
    )


def test_boolean_comparisons_and_tests_do_not_require_bool_filter():
    assert check_missing_bool_filter("distribution != 'Fedora'") == []
    assert check_missing_bool_filter("release is version(target, '>=')") == []
    assert check_missing_bool_filter("result is succeeded") == []
    assert check_missing_bool_filter("feature_enabled") == []
    assert check_missing_bool_filter("feature_enabled == 'true'")


def test_templated_attribute_types_use_visible_role_defaults(tmp_path):
    role = tmp_path / "roles" / "example"
    _write(
        role / "defaults" / "main.yml",
        "install_java: true\nretry_delay: 5\n",
    )
    tasks = _write(
        role / "tasks" / "main.yml",
        """- name: Valid dynamic values
  command: java -version
  ignore_errors: "{{ install_java }}"
  delay: "{{ retry_delay }}"
- name: Unknown dynamic value
  command: /bin/true
  retries: "{{ supplied_by_inventory }}"
""",
    )

    assert detect_invalid_task_attribute_types(tasks) == (0, [])


def test_templated_attribute_with_visible_wrong_type_is_reported(tmp_path):
    role = tmp_path / "roles" / "example"
    _write(role / "defaults" / "main.yml", "retry_delay: slow\n")
    tasks = _write(
        role / "tasks" / "main.yml",
        "- name: Invalid resolved value\n  command: /bin/true\n"
        "  delay: '{{ retry_delay }}'\n",
    )

    count, details = detect_invalid_task_attribute_types(tasks)

    assert count == 1
    assert details[0]["attribute"] == "delay"


def test_documentation_placeholder_is_not_a_credential_reference(tmp_path):
    playbook = _write(
        tmp_path / "credentials.yml",
        """- name: Explain required configuration
  fail:
    msg: "Set password=<jenkins_api_token> in the environment file"
- name: Actually display a credential
  debug:
    msg: "{{ jenkins_api_token }}"
""",
    )

    _, count, details = detect_credentials_leaking_in_log(playbook)

    assert count == 1
    assert details[0]["task_name"] == "Actually display a credential"


def test_read_only_query_is_not_classified_as_mutating(tmp_path):
    playbook = _write(
        tmp_path / "commands.yml",
        """- name: Query an API
  shell: curl -s https://example.invalid/api | grep result
- name: Install a package
  command: apt-get install nginx
- name: Download with curl
  command: curl -o /tmp/archive https://example.invalid/archive
- name: Download with wget
  command: wget https://example.invalid/other
""",
    )

    mutating_count, mutating = detect_non_idempotent_commands(playbook)
    query_count, queries = detect_read_only_command_changes(playbook)

    assert mutating_count == 3
    assert {item["task_name"] for item in mutating} == {
        "Install a package",
        "Download with curl",
        "Download with wget",
    }
    assert query_count == 1
    assert queries[0]["task_name"] == "Query an API"


def test_curl_with_remote_mutation_options_is_not_read_only(tmp_path):
    playbook = _write(
        tmp_path / "curl.yml",
        """- name: Trigger deployment
  shell: curl -X POST https://example.invalid/redeploy
- name: Upload feature state
  shell: curl --data '{\"enabled\":true}' https://example.invalid/feature
- name: Inspect feature state
  shell: curl -s https://example.invalid/feature
""",
    )

    count, details = detect_non_idempotent_commands(playbook)
    read_count, read_details = detect_read_only_command_changes(playbook)

    assert {item["task_name"] for item in details} == {
        "Trigger deployment", "Upload feature state"
    }
    assert count == 2
    assert read_count == 1
    assert read_details[0]["task_name"] == "Inspect feature state"


def test_boolean_key_presence_is_not_an_idempotency_guard(tmp_path):
    playbook = _write(
        tmp_path / "guards.yml",
        """- name: Always changed
  command: apt-get install foo
  changed_when: true
- name: Check mode disabled
  command: apt-get install bar
  check_mode: false
- name: Check mode enabled
  command: apt-get install baz
  check_mode: true
- name: Explicitly unchanged
  command: apt-get install qux
  changed_when: false
- name: Filesystem state check
  command: apt-get install quux
  args:
    creates: /opt/quux/ready
""",
    )

    count, details = detect_non_idempotent_commands(playbook)

    assert count == 4
    assert {item["task_name"] for item in details} == {
        "Always changed", "Check mode disabled", "Check mode enabled",
        "Explicitly unchanged",
    }


def test_unrelated_identifier_does_not_consume_registered_result(tmp_path):
    _write(tmp_path / ".git" / "HEAD", "ref: refs/heads/main\n")
    tasks = _write(
        tmp_path / "roles" / "producer" / "tasks" / "main.yml",
        "- command: /bin/true\n  register: result\n",
    )
    _write(
        tmp_path / "roles" / "consumer" / "vars" / "main.yml",
        "result: unrelated\n",
    )

    count, details = detect_unused_registered_variables(tasks)

    assert count == 1
    assert details[0]["variable"] == "result"


def test_deprecation_metadata_respects_older_project_pin(tmp_path, monkeypatch):
    repository = tmp_path / "repository"
    (repository / ".git").mkdir(parents=True)
    _write(repository / "Pipfile", 'ansible-core = "==2.16.19"\n')
    playbook = _write(
        repository / "roles" / "db" / "tasks" / "main.yml",
        "- name: Add key\n  ansible.builtin.apt_key:\n    url: https://example.invalid/key\n",
    )
    metadata = {
        "alternative": "ansible.builtin.deb822_repository",
        "removed_in": "2.25",
    }
    monkeypatch.setattr(
        "ansibleguard.detectors.deprecated_modules._installed_deprecation",
        lambda _module, _index=None: metadata,
    )
    monkeypatch.setattr(
        "ansibleguard.detectors.deprecated_modules._installed_ansible_version",
        lambda: Version("2.20"),
    )

    assert detect_deprecated_modules(playbook) == (0, [])


def test_missing_tags_is_explicitly_optional_style_policy(tmp_path):
    playbook = _write(
        tmp_path / "tags.yml",
        "- name: Untagged\n  debug:\n    msg: hello\n",
    )

    count, details = detect_missing_tags(playbook)

    assert count == 1
    assert details[0]["issue"].startswith("Optional style policy:")
    assert {
        key: RULE_CATALOG["missing-tags"][key]
        for key in ("level", "category", "policy", "description")
    } == {
        "level": "note",
        "category": "style",
        "policy": "optional",
        "description": "Optional style policy: a task has no explicit or inherited tags.",
    }
    assert RULE_CATALOG["missing-tags"]["confidence"] == "low"
    assert RULE_CATALOG["missing-tags"]["remediation"]


def test_play_level_tags_protect_all_nested_tasks(tmp_path):
    playbook = _write(
        tmp_path / "play-tags.yml",
        "- name: Tagged play\n"
        "  hosts: all\n"
        "  tags: [deployment]\n"
        "  tasks:\n"
        "    - name: Nested task\n"
        "      debug: {msg: ready}\n",
    )

    assert detect_missing_tags(playbook) == (0, [])


def test_extension_rule_only_checks_static_include_references():
    assert check_missing_extension({"command": {"cmd": "/usr/bin/java -version"}}) == 0
    assert check_missing_extension({"file": {"path": "/var/lib/service"}}) == 0
    assert check_missing_extension({"include_tasks": "install"}) == 1
    assert check_missing_extension({"ansible.builtin.include_tasks": "install.yml"}) == 0


def test_role_parameters_are_repository_symbols(tmp_path):
    playbook = _write(
        tmp_path / "site.yml",
        "- hosts: all\n  roles:\n    - role: devkit\n      devkit_version: v1\n",
    )
    index = build_repository_symbol_index(tmp_path)
    assert "devkit_version" in index.names
    assert any(item.kind == "role-parameter" for item in index.definitions)


def test_registered_result_used_by_handler_is_not_unused(tmp_path):
    _write(tmp_path / ".git" / "HEAD", "ref: refs/heads/main\n")
    tasks = _write(
        tmp_path / "roles" / "web" / "tasks" / "main.yml",
        "- name: Start service\n  systemd:\n    name: web\n"
        "  register: web_started\n",
    )
    _write(
        tmp_path / "roles" / "web" / "handlers" / "main.yml",
        "- name: Restart web\n  when: web_started is changed\n"
        "  debug:\n    msg: changed\n",
    )
    graph = build_repository_symbol_index(tmp_path)
    assert detect_unused_registered_variables(tasks, symbol_index=graph) == (0, [])


def test_standalone_role_handler_uses_register(tmp_path):
    tasks = _write(
        tmp_path / "tasks" / "main.yml",
        "- command: /bin/true\n  register: standalone_result\n",
    )
    _write(
        tmp_path / "handlers" / "main.yml",
        "- debug: {msg: '{{ standalone_result.stdout }}'}\n",
    )

    graph = build_repository_symbol_index(tmp_path)

    assert detect_unused_registered_variables(tasks, symbol_index=graph) == (0, [])


def test_unrelated_registered_when_does_not_guard_idempotency(tmp_path):
    playbook = _write(
        tmp_path / "commands.yml",
        "- command: health-check\n  register: health\n"
        "- command: apt-get install nginx\n  when: health.rc == 0\n",
    )

    count, details = detect_non_idempotent_commands(playbook)

    assert count == 1
    assert details[0]["command"] == "apt-get install nginx"


def test_command_instead_of_module_noqa_does_not_hide_idempotency(tmp_path):
    playbook = _write(
        tmp_path / "commands.yml",
        "- name: Install\n"
        "  command: apt-get install nginx  # noqa command-instead-of-module\n",
    )

    assert detect_non_idempotent_commands(playbook)[0] == 1


def test_changed_when_false_does_not_prove_execution_idempotency(tmp_path):
    playbook = _write(
        tmp_path / "commands.yml",
        "- command: apt-get install nginx\n  changed_when: false\n",
    )

    assert detect_non_idempotent_commands(playbook)[0] == 1


def test_undefined_guard_does_not_make_reference_safe(tmp_path):
    playbook = _write(
        tmp_path / "variables.yml",
        "- debug:\n    msg: '{{ foo is undefined }} {{ foo }}'\n",
    )

    count, details = detect_unguarded_variables(playbook)

    assert count == 1
    assert details[0]["variable"] == "foo"


def test_shell_local_assignments_and_awk_builtins_are_scoped(tmp_path):
    playbook = _write(
        tmp_path / "shell.yml",
        """- name: Local variables
  shell: |
    current_ps=$(command)
    echo "$current_ps"
    awk '{print $NF}' input
""",
    )
    assert detect_unscoped_shell_variables(playbook) == (0, [])


def test_authentication_arguments_do_not_make_downloaded_artifact_sensitive(tmp_path):
    playbook = _write(
        tmp_path / "download.yml",
        """- name: Download artifact
  get_url:
    url: https://example.invalid/archive.zip
    url_password: "{{ repository_password }}"
    dest: /tmp/archive.zip
    mode: "0644"
""",
    )
    assert detect_insecure_permissions(playbook) == (0, [])


def test_static_handler_import_wrapper_is_not_unused(tmp_path):
    playbook = _write(
        tmp_path / "handlers.yml",
        """- hosts: all
  handlers:
    - name: Load handlers
      import_tasks: handlers/main.yml
  tasks: []
""",
    )
    assert detect_handler_issues(playbook)[2:] == (0, [])
