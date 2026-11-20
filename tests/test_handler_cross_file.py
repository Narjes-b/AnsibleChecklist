"""Handler checks follow static handler imports, role handlers, and task includes."""

from ansibleguard.detectors.handler_issues import detect_handler_issues


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_handler_imported_into_play_is_not_missing(tmp_path):
    _write(tmp_path / "handlers/main.yml", "- name: Update initramfs\n  ansible.builtin.command: update-initramfs -u\n"
           "- name: Apply sysctl\n  ansible.builtin.command: sysctl --system\n  listen: hugepage sysctl\n")
    playbook = _write(tmp_path / "site.yml", """---
- hosts: all
  handlers:
    - name: Import handlers
      ansible.builtin.import_tasks: handlers/main.yml
  tasks:
    - name: Configure
      ansible.builtin.copy: {content: x, dest: /etc/x, mode: "0644"}
      notify: [Update initramfs, hugepage sysctl]
""")
    missing_count, _, _, _ = detect_handler_issues(playbook)
    assert missing_count == 0


def test_handler_notified_from_included_task_file_is_used(tmp_path):
    _write(tmp_path / "tasks/logrotate.yaml", "- name: Rotate\n  ansible.builtin.copy: {content: x, dest: /etc/x, mode: '0644'}\n  notify: Restart rsyslog\n")
    playbook = _write(tmp_path / "site.yml", """---
- hosts: all
  tasks:
    - ansible.builtin.include_tasks: tasks/logrotate.yaml
  handlers:
    - name: Restart rsyslog
      ansible.builtin.service: {name: rsyslog, state: restarted}
    - name: Never used
      ansible.builtin.service: {name: x, state: restarted}
""")
    _, _, unused_count, unused = detect_handler_issues(playbook)
    assert [item["handler_name"] for item in unused] == ["Never used"]
    assert unused_count == 1


def test_genuinely_missing_handler_is_still_reported(tmp_path):
    playbook = _write(tmp_path / "site.yml", """---
- hosts: all
  tasks:
    - name: Configure
      ansible.builtin.copy: {content: x, dest: /etc/x, mode: "0644"}
      notify: Update grub config
""")
    missing_count, missing, _, _ = detect_handler_issues(playbook)
    assert missing_count == 1 and missing[0]["handler_name"] == "Update grub config"


def test_unresolvable_handler_source_is_not_claimed_missing(tmp_path):
    playbook = _write(tmp_path / "site.yml", """---
- hosts: all
  handlers:
    - ansible.builtin.import_tasks: "{{ handler_file }}"
  tasks:
    - name: Configure
      ansible.builtin.copy: {content: x, dest: /etc/x, mode: "0644"}
      notify: Update grub config
""")
    missing_count, _, _, _ = detect_handler_issues(playbook)
    assert missing_count == 0
