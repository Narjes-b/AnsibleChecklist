"""False-positive classes found in the 2026-10-15 calibration sample (AI precheck)."""

from ansibleguard.detectors.paper_candidates import (
    detect_broken_role_dependencies,
    detect_incomplete_tasks,
)
from ansibleguard.detectors.review_checklist import (
    detect_non_idempotent_commands,
    detect_read_only_command_changes,
)


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_kubectl_output_format_is_not_a_file_write(tmp_path):
    # FP-055: kubectl --output jsonpath / -o json selects a format.
    tasks = _write(tmp_path / "tasks.yml", """---
- name: Generate kubeconfig for cluster
  ansible.builtin.command: >-
    kubectl get secret demo-kubeconfig --namespace demo --output jsonpath='{.data.value}'
  changed_when: false
- name: Read clusters
  ansible.builtin.command: kubectl get clusters -n demo -o json
  changed_when: false
- name: Download a file
  ansible.builtin.command: curl -fsSL -o /tmp/app.tgz https://example.invalid/app.tgz
""")
    count, details = detect_non_idempotent_commands(tasks)
    assert [item["task_name"] for item in details] == ["Download a file"]


def test_read_only_command_message_does_not_claim_curl(tmp_path):
    tasks = _write(tmp_path / "tasks.yml", "- name: Read routes\n  ansible.builtin.shell: ip -6 route list | grep default\n")
    _, details = detect_read_only_command_changes(tasks)
    assert details and "curl" not in details[0]["issue"]


def test_hack_inside_an_identifier_is_not_a_marker(tmp_path):
    # FP-023: "containerd-hack" is a service name.
    tasks = _write(tmp_path / "tasks.yml", """---
- name: Enable containerd-hack service
  ansible.builtin.systemd: {name: containerd-hack, enabled: true}
- name: Create conf dir [Hack - remove once using gssproxy]
  ansible.builtin.file: {path: /etc/httpd/conf, state: directory}
""")
    count, details = detect_incomplete_tasks(tasks)
    assert count == 1
    assert details[0]["line"] == 4


def test_namespaced_galaxy_dependency_is_not_a_self_dependency(tmp_path):
    # FP-003: role "redis" depending on "DavidWittman.redis".
    anchor = _write(tmp_path / "roles/redis/tasks/main.yml", "- name: Noop\n  ansible.builtin.debug: {msg: ok}\n")
    _write(tmp_path / "roles/redis/meta/main.yml", "dependencies:\n  - role: monit\n  - role: DavidWittman.redis\n")
    _write(tmp_path / "roles/monit/tasks/main.yml", "- name: Noop\n  ansible.builtin.debug: {msg: ok}\n")
    assert detect_broken_role_dependencies(anchor) == (0, [])


def test_exact_self_dependency_is_still_reported(tmp_path):
    anchor = _write(tmp_path / "roles/web/tasks/main.yml", "- name: Noop\n  ansible.builtin.debug: {msg: ok}\n")
    _write(tmp_path / "roles/web/meta/main.yml", "dependencies:\n  - role: web\n")
    count, details = detect_broken_role_dependencies(anchor)
    assert count == 1 and "depends on itself" in details[0]["issue"]


def test_environment_list_of_mappings_is_valid_but_vars_list_is_not(tmp_path):
    # cfpb/aurora PR: environment given as a list of mappings is valid Ansible.
    from ansibleguard.detectors.partial_checklist import detect_invalid_task_attribute_types

    tasks = _write(tmp_path / "tasks.yml", """---
- name: Build
  ansible.builtin.shell: make
  environment:
    - PKG_CONFIG_PATH: /usr/local/lib/pkgconfig
- name: Include role with list vars
  ansible.builtin.import_role:
    name: web
  vars:
    - remove: true
""")
    count, details = detect_invalid_task_attribute_types(tasks)
    assert [item["attribute"] for item in details] == ["vars"]


def test_marker_inside_a_path_is_not_a_marker(tmp_path):
    # `hack/` is a directory name, not an unresolved-work marker.
    tasks = _write(tmp_path / "tasks.yml", """---
- name: Run script from hack/ directory
  ansible.builtin.command: ./hack/verify.sh
- name: Fix later [HACK - remove once fixed]
  ansible.builtin.debug: {msg: ok}
""")
    count, details = detect_incomplete_tasks(tasks)
    assert count == 1
    assert details[0]["line"] == 4
