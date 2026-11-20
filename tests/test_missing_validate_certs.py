from ansibleguard.detectors.missing_validate_certs import (
    detect_missing_validate_certs,
)


def test_disabled_validation_in_unarchive_is_detected(tmp_path):
    playbook = tmp_path / "tasks.yml"
    playbook.write_text(
        "- name: Download archive\n"
        "  unarchive:\n"
        "    src: https://example.invalid/archive.tar.gz\n"
        "    remote_src: true\n"
        "    validate_certs: false\n",
        encoding="utf-8",
    )

    count, details = detect_missing_validate_certs(playbook)

    assert count == 1
    assert details[0]["module"] == "unarchive"


def test_disabled_validation_in_action_module_is_detected(tmp_path):
    playbook = tmp_path / "tasks.yml"
    playbook.write_text(
        "- name: Notify team\n"
        "  action:\n"
        "    module: slack\n"
        "    token: '{{ slack_token }}'\n"
        "    validate_certs: no\n",
        encoding="utf-8",
    )

    count, details = detect_missing_validate_certs(playbook)

    assert count == 1
    assert details[0]["module"] == "slack"


def test_task_variable_named_validate_certs_is_not_a_module_setting(tmp_path):
    playbook = tmp_path / "tasks.yml"
    playbook.write_text(
        "- name: Keep project variable\n"
        "  debug:\n"
        "    msg: hello\n"
        "  vars:\n"
        "    validate_certs: false\n",
        encoding="utf-8",
    )

    assert detect_missing_validate_certs(playbook)[0] == 0
