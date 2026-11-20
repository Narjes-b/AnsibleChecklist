from ansibleguard.detectors.deprecated_modules import (
    detect_deprecated_modules,
    detect_redirected_modules,
)
from ansibleguard.detectors.handler_issues import detect_handler_issues
from ansibleguard.detectors.missing_tags import detect_missing_tags
from ansibleguard.detectors.missing_validate_certs import detect_missing_validate_certs
from ansibleguard.detectors.shell_instead_of_module import detect_shell_instead_of_module


def test_legacy_detectors_report_source_lines(tmp_path):
    playbook = tmp_path / "lines.yml"
    playbook.write_text(
        """---
- hosts: all
  tasks:
    - name: Untagged
      debug:
        msg: hello
    - name: Deprecated
      docker:
        name: demo
      tags: docker
    - name: Unsafe TLS
      uri:
        url: https://example.invalid
        validate_certs: false
      tags: tls
    - name: Native module exists
      shell: mkdir /tmp/demo
      tags: shell
    - name: Missing notification
      debug:
        msg: change
      notify: Custom missing handler
      tags: notify
  handlers:
    - name: Never notified
      debug:
        msg: unused
""",
        encoding="utf-8",
    )

    assert detect_missing_tags(playbook)[1][0]["line"] == 4
    assert detect_deprecated_modules(playbook)[1][0]["line"] == 8
    assert detect_missing_validate_certs(playbook)[1][0]["line"] == 12
    assert detect_shell_instead_of_module(playbook)[1][0]["line"] == 16
    missing = detect_handler_issues(playbook)[1]
    unused = detect_handler_issues(playbook)[3]
    assert missing[0]["line"] == 22
    assert unused[0]["line"] == 25


def test_redirected_modules_flags_legacy_short_name(tmp_path):
    playbook = tmp_path / "redirect.yml"
    playbook.write_text(
        "- name: Manage container\n"
        "  docker_container:\n"
        "    name: app\n"
        "    image: nginx\n",
        encoding="utf-8",
    )
    count, details = detect_redirected_modules(playbook)
    assert count == 1
    assert details[0]["module"] == "docker_container"
    assert "community.docker.docker_container" in details[0]["replacement"]


def test_redirected_modules_flags_aws_ec2(tmp_path):
    playbook = tmp_path / "aws.yml"
    playbook.write_text(
        "- name: Launch instance\n"
        "  ec2:\n"
        "    instance_type: t2.micro\n",
        encoding="utf-8",
    )
    count, details = detect_redirected_modules(playbook)
    assert count == 1
    assert details[0]["module"] == "ec2"
    assert "amazon.aws" in details[0]["replacement"]


def test_redirected_modules_no_fire_for_fqcn(tmp_path):
    playbook = tmp_path / "fqcn.yml"
    playbook.write_text(
        "- name: Manage container\n"
        "  community.docker.docker_container:\n"
        "    name: app\n"
        "    image: nginx\n",
        encoding="utf-8",
    )
    assert detect_redirected_modules(playbook) == (0, [])


def test_redirected_modules_no_fire_for_unrelated_module(tmp_path):
    playbook = tmp_path / "plain.yml"
    playbook.write_text(
        "- name: Install nginx\n"
        "  apt:\n"
        "    name: nginx\n"
        "    state: present\n",
        encoding="utf-8",
    )
    assert detect_redirected_modules(playbook) == (0, [])


def test_complex_install_script_and_docker_cp_have_no_direct_module_replacement(
    tmp_path,
):
    tasks = tmp_path / "tasks.yml"
    tasks.write_text(
        "- name: Install Homebrew\n"
        "  shell: |\n"
        "    export NONINTERACTIVE=1\n"
        "    /bin/bash -c \"$(curl -fsSL https://example.invalid/install.sh)\"\n"
        "- name: Copy into a container\n"
        "  command: docker cp /tmp/data app:/var/lib/data\n",
        encoding="utf-8",
    )

    assert detect_shell_instead_of_module(tasks) == (0, [])
