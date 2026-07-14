"""
Detects shell/command usage where a dedicated Ansible module exists.

Using shell: or command: instead of a native Ansible module reduces
idempotency, loses built-in change detection, and makes playbooks
harder to maintain and harder to run in check mode.

Ansible best practice: always prefer a dedicated module over raw
shell/command when one exists.

Reference:
  - Ansible docs: "Always prefer modules over running raw commands"
    https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_intro.html
  - Ansible module index:
    https://docs.ansible.com/ansible/latest/collections/index_module.html

Detection strategy:
  Walk all leaf tasks using shell: or command:.
  Pattern-match the command string against known package manager,
  file manipulation, and service management patterns.
  Flag with the recommended replacement module.

  Conservative approach: only flag high-confidence patterns with
  unambiguous module equivalents. Avoid flagging complex pipelines,
  multi-command strings, or commands with pipes/redirects.

Complexity: O(n) where n = number of tasks.
False positives: commands with conditional logic, edge cases where
  a module exists but doesn't support the exact parameters needed.
Limitations: string-based pattern matching cannot understand shell
  semantics; some flagged commands may be intentional (e.g., one-off
  admin tasks that don't need idempotency).
"""

import re
from ansibleguard.detectors.source_lines import load_with_lines, source_line


# Pattern → (module, args description)
# Each pattern is matched against the shell/command string.
# Patterns are ordered from most specific to least specific.
_SHELL_PATTERNS = [
    # --- Package managers ---
    (r"\bapt(?:-get)?\s+(?:install|remove|purge|update|upgrade|autoremove)\b",
     "apt", "Use the 'apt' or 'package' module instead of apt-get/apt."),
    (r"\byum\s+(?:install|remove|update|upgrade)\b",
     "yum", "Use the 'yum' or 'package' module instead of yum."),
    (r"\bdnf\s+(?:install|remove|update|upgrade)\b",
     "dnf", "Use the 'dnf' or 'package' module instead of dnf."),
    (r"\bzypper\s+(?:install|remove|update|up)\b",
     "zypper", "Use the 'zypper' or 'package' module instead of zypper."),
    (r"\bpip(?:3)?\s+install\b",
     "pip", "Use the 'pip' module instead of 'pip install'."),
    (r"\bgem\s+install\b",
     "gem", "Use the 'gem' module instead of 'gem install'."),
    (r"\bnpm\s+(?:install|uninstall)\b",
     "npm", "Use the 'npm' module (community.general.npm) instead."),

    # --- Service management ---
    (r"\bsystemctl\s+(?:start|stop|restart|enable|disable|status)\b",
     "systemd", "Use the 'systemd' or 'service' module instead of systemctl."),
    (r"\bservice\s+\S+\s+(?:start|stop|restart|reload|status)\b",
     "service", "Use the 'service' module instead of the service command."),

    # --- File operations ---
    (r"\bmkdir\b",
     "file", "Use the 'file' module with state=directory instead of mkdir."),
    (r"\bchmod\b",
     "file", "Use the 'file' module with the mode parameter instead of chmod."),
    (r"\bchown\b",
     "file", "Use the 'file' module with owner/group instead of chown."),
    (r"\bcp\s+",
     "copy", "Use the 'copy' module instead of cp."),
    (r"\bmv\s+",
     "copy", "Use the 'copy' module with remote_src=true instead of mv."),
    (r"\brm\s+(?:-rf?\s+)?",
     "file", "Use the 'file' module with state=absent instead of rm."),
    (r"\bln\s+-s\b",
     "file", "Use the 'file' module with state=link instead of ln -s."),

    # --- Network / downloads ---
    (r"\bwget\b",
     "get_url", "Use the 'get_url' module instead of wget."),
    (r"\bcurl\b",
     "uri", "Use the 'uri' or 'get_url' module instead of curl."),

    # --- Version control ---
    (r"\bgit\s+clone\b",
     "git", "Use the 'git' module instead of 'git clone'."),
    (r"\bsvn\s+(?:co|checkout)\b",
     "subversion", "Use the 'subversion' module instead of svn checkout."),

    # --- Archives ---
    (r"\b(?:tar|unzip|gunzip)\s+(?:-.*)?x",
     "unarchive", "Use the 'unarchive' module instead of tar/unzip extraction."),

    # --- User management ---
    (r"\buseradd\b",
     "user", "Use the 'user' module instead of useradd."),
    (r"\bgroupadd\b",
     "group", "Use the 'group' module instead of groupadd."),
    (r"\busermod\b",
     "user", "Use the 'user' module instead of usermod."),

    # --- Cron ---
    (r"\bcrontab\b",
     "cron", "Use the 'cron' module instead of crontab."),
]


def _is_shell_or_command(task):
    """Check if a task uses shell: or command: (including FQCN forms)."""
    shell_keys = {"shell", "command", "ansible.builtin.shell", "ansible.builtin.command"}
    return any(k in task for k in shell_keys)


def _get_command_string(task):
    """Extract the command string from a shell/command task."""
    for k in ("shell", "command", "ansible.builtin.shell", "ansible.builtin.command"):
        if k in task:
            val = task[k]
            if isinstance(val, str):
                return val
            if isinstance(val, dict) and "cmd" in val:
                return val["cmd"]
    return ""


def _collect_all_tasks(playbook):
    """Recursively collect all leaf tasks."""
    all_tasks = []

    def recurse(tasks):
        for task in tasks:
            if not isinstance(task, dict):
                continue
            has_nested = False
            for section in ("block", "rescue", "always"):
                if section in task and isinstance(task[section], list):
                    recurse(task[section])
                    has_nested = True
            if not has_nested:
                all_tasks.append(task)

    if isinstance(playbook, list):
        for entry in playbook:
            if not isinstance(entry, dict):
                continue
            if "tasks" in entry and isinstance(entry["tasks"], list):
                recurse(entry["tasks"])
            elif "block" in entry and isinstance(entry["block"], list):
                recurse(entry["block"])
            elif "hosts" not in entry:
                recurse([entry])
    return all_tasks


def detect_shell_instead_of_module(yaml_file_path):
    """
    Detect shell/command usage where a native Ansible module exists.

    Args:
        yaml_file_path: Path to an Ansible playbook YAML file.

    Returns:
        (count, details) where:
          count:   int — number of flagged shell/command tasks
          details: list[dict] — {"task_name", "command", "module", "issue"}
    """
    playbook = load_with_lines(yaml_file_path)
    if playbook is None:
        return 0, []

    all_tasks = _collect_all_tasks(playbook)
    details = []

    for task in all_tasks:
        task_name = task.get("name", "Unnamed task")

        if not _is_shell_or_command(task):
            continue

        cmd = _get_command_string(task)
        if not cmd:
            continue

        # Skip complex shell usage: pipes, redirects, loops, conditionals,
        # multi-line commands — these often require shell features that
        # modules can't replace.
        if any(c in cmd for c in ("|", ">", "<", ";", "&&", "||", "for ", "while ")):
            continue

        # Check each pattern
        for pattern, module_name, message in _SHELL_PATTERNS:
            if re.search(pattern, cmd, re.IGNORECASE):
                details.append({
                    "task_name": task_name,
                    "command": cmd[:80] + ("..." if len(cmd) > 80 else ""),
                    "module": module_name,
                    "issue": message,
                    "line": source_line(task),
                })
                break  # One match per task

    return len(details), details


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        count, details = detect_shell_instead_of_module(sys.argv[1])
        print(f"Found {count} shell/command task(s) with module alternatives:")
        for d in details:
            print(f"  - {d['task_name']}: {d['module']} — {d['issue']}")
    else:
        print("Usage: python shell_instead_of_module.py <playbook.yml>")
