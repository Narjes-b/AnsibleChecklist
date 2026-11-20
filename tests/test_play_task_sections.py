from ansibleguard.detectors.credentials_leaking_in_log import (
    detect_credentials_leaking_in_log,
)
from ansibleguard.detectors.deprecated_modules import detect_deprecated_modules
from ansibleguard.detectors.filters_for_comparison import get_when_conditions
from ansibleguard.detectors.handler_issues import detect_handler_issues
from ansibleguard.detectors.missing_tags import detect_missing_tags
from ansibleguard.detectors.missing_validate_certs import (
    detect_missing_validate_certs,
)
from ansibleguard.detectors.shell_instead_of_module import (
    detect_shell_instead_of_module,
)


def test_pre_and_post_tasks_are_analyzed_like_normal_tasks(tmp_path):
    playbook = tmp_path / "playbook.yml"
    playbook.write_text(
        "---\n"
        "- name: Exercise every play task section\n"
        "  hosts: localhost\n"
        "  pre_tasks:\n"
        "    - name: Display token\n"
        "      debug:\n"
        "        var: api_token\n"
        "    - name: Restart service through shell\n"
        "      shell: service nginx restart\n"
        "    - name: Quoted condition\n"
        "      debug:\n"
        "        msg: test\n"
        "      when: enabled == 'true'\n"
        "  post_tasks:\n"
        "    - name: Disable TLS verification\n"
        "      get_url:\n"
        "        url: https://example.invalid/archive\n"
        "        dest: /tmp/archive\n"
        "        validate_certs: false\n"
        "    - name: Use legacy include\n"
        "      include: legacy.yml\n"
        "    - name: Notify missing handler\n"
        "      command: /bin/true\n"
        "      notify: definitely absent\n",
        encoding="utf-8",
    )

    assert detect_credentials_leaking_in_log(playbook)[1] == 1
    assert detect_shell_instead_of_module(playbook)[0] == 1
    assert get_when_conditions(playbook) == 1
    assert detect_missing_validate_certs(playbook)[0] == 1
    assert detect_deprecated_modules(playbook)[0] == 1
    assert detect_handler_issues(playbook)[0] == 1
    assert detect_missing_tags(playbook)[0] == 6
