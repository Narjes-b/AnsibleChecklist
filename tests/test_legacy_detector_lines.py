from ansibleguard.detectors.deprecated_modules import detect_deprecated_modules
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
