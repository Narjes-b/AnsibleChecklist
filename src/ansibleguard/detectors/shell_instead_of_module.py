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

_WINDOWS_GUARD_RE = re.compile(
    r"""ansible_system\s*==\s*['"]Windows['"]"""
    r"""|ansible_os_family\s*==\s*['"]Windows['"]"""
    r"""|ansible_connection\s*(?:==\s*['"](?:winrm|psrp)['"]|\bin\b[^]]*(?:winrm|psrp))""",
    re.IGNORECASE,
)

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
    # v0.0.4: anchor these to the start of the command string to avoid matching
    # command names or arguments that contain these words (e.g. paths with "cp",
    # variable names with "mv", "rm" inside option strings).
    (r"^(?:sudo\s+)?mkdir\b",
     "file", "Use the 'file' module with state=directory instead of mkdir."),
    (r"^(?:sudo\s+)?chmod\b",
     "file", "Use the 'file' module with the mode parameter instead of chmod."),
    (r"^(?:sudo\s+)?chown\b",
     "file", "Use the 'file' module with owner/group instead of chown."),
    (r"^(?:sudo\s+)?cp\s+",
     "copy", "Use the 'copy' module instead of cp."),
    (r"^(?:sudo\s+)?mv\s+",
     "copy", "Use the 'copy' module with remote_src=true instead of mv."),
    (r"^(?:sudo\s+)?rm\s+",
     "file", "Use the 'file' module with state=absent instead of rm."),
    (r"^(?:sudo\s+)?ln\s+-s\b",
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

    # --- Sync / transfer ---
    (r"\brsync\b",
     "ansible.posix.synchronize",
     "Use the 'synchronize' module (ansible.posix.synchronize) instead of rsync."),
    (r"\bscp\s+",
     "copy",
     "Use the 'copy' module with remote_src=true instead of scp."),

    # --- Search ---
    (r"^(?:sudo\s+)?find\s+\S+\s+-name\b",
     "find",
     "Use the 'find' module (ansible.builtin.find) instead of the find command."),

    # --- System configuration ---
    (r"\bhostname\b",
     "hostname",
     "Use the 'hostname' module (ansible.builtin.hostname) instead of the hostname command."),
    (r"\btimedatectl\b",
     "community.general.timezone",
     "Use the 'timezone' module (community.general.timezone) instead of timedatectl."),
    (r"\bupdate-alternatives\b",
     "community.general.alternatives",
     "Use the 'alternatives' module (community.general.alternatives) instead of update-alternatives."),

    # --- User and group management ---
    (r"\badduser\b",
     "user",
     "Use the 'user' module instead of adduser."),
    (r"\bdeluser\b",
     "user",
     "Use the 'user' module instead of deluser."),
    (r"\buserdel\b",
     "user",
     "Use the 'user' module instead of userdel."),
    (r"\bgroupdel\b",
     "group",
     "Use the 'group' module instead of groupdel."),

    # --- File creation ---
    (r"^(?:sudo\s+)?touch\b",
     "file",
     "Use the 'file' module with state=touch instead of touch."),
]


def _is_shell_or_command(task):
    """Check if a task uses shell:, command:, or raw: (including FQCN forms)."""
    shell_keys = {
        "shell", "command", "raw",
        "ansible.builtin.shell", "ansible.builtin.command", "ansible.builtin.raw",
    }
    return any(k in task for k in shell_keys)


def _get_command_string(task):
    """Extract the command string from a shell/command/raw task."""
    for k in (
        "shell", "command", "raw",
        "ansible.builtin.shell", "ansible.builtin.command", "ansible.builtin.raw",
    ):
        if k in task:
            val = task[k]
            if isinstance(val, str):
                return val
            if isinstance(val, dict) and "cmd" in val:
                return val["cmd"]
    return ""


_LEADING_ASSIGNMENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=\S+\s+")
_ABSOLUTE_EXECUTABLE_RE = re.compile(r"^/(?:usr/)?(?:s?bin)/")


def _normalise_command_prefix(command):
    """Expose the real executable without searching arbitrary arguments.

    This retains common wrappers (environment assignments, ``env`` and
    ``sudo``) and absolute executable paths while allowing every detector
    pattern to be matched at position zero.  It prevents false positives such
    as ``echo 'run rm later'`` without losing ``/usr/bin/rm``.
    """
    rendered = command.strip()
    if rendered.startswith("env "):
        rendered = rendered[4:].lstrip()
    while _LEADING_ASSIGNMENT_RE.match(rendered):
        rendered = _LEADING_ASSIGNMENT_RE.sub("", rendered, count=1)
    if rendered.startswith("sudo "):
        rendered = rendered[5:].lstrip()
        # Support common flag-only sudo prefixes.  Options that consume a
        # value are intentionally left unresolved and therefore not flagged.
        while re.match(r"^-[A-Za-z]+\s+", rendered):
            rendered = re.sub(r"^-[A-Za-z]+\s+", "", rendered, count=1)
    return _ABSOLUTE_EXECUTABLE_RE.sub("", rendered, count=1)


def _is_read_only_query(command):
    """Commands whose matched executable is used only to inspect state."""
    rendered = _normalise_command_prefix(command)
    return bool(
        re.match(r"^hostname\s*$", rendered, re.IGNORECASE)
        or re.match(
            r"^systemctl\s+(?:status|is-active|is-enabled|show)\b",
            rendered,
            re.IGNORECASE,
        )
        or re.match(r"^service\s+\S+\s+status\b", rendered, re.IGNORECASE)
        or (
            re.match(r"^timedatectl\b", rendered, re.IGNORECASE)
            and not re.search(r"\bset-", rendered, re.IGNORECASE)
        )
    )


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
            found_play_section = False
            for section in ("pre_tasks", "tasks", "post_tasks", "handlers"):
                if isinstance(entry.get(section), list):
                    recurse(entry[section])
                    found_play_section = True
            if "block" in entry and isinstance(entry["block"], list):
                recurse(entry["block"])
            elif not found_play_section and "hosts" not in entry:
                recurse([entry])
    return all_tasks


def detect_shell_instead_of_module(yaml_file_path, parsed_document=None):
    """
    Detect shell/command usage where a native Ansible module exists.

    Args:
        yaml_file_path: Path to an Ansible playbook YAML file.

    Returns:
        (count, details) where:
          count:   int — number of flagged shell/command tasks
          details: list[dict] — {"task_name", "command", "module", "issue"}
    """
    playbook = (
        parsed_document.document
        if parsed_document is not None
        else load_with_lines(yaml_file_path)
    )
    if playbook is None:
        return 0, []

    all_tasks = _collect_all_tasks(playbook)
    details = []

    for task in all_tasks:
        task_name = task.get("name", "Unnamed task")

        if not _is_shell_or_command(task):
            continue

        # B7: Skip tasks guarded by Windows-only conditions
        when_val = task.get("when")
        when_str = (
            when_val if isinstance(when_val, str)
            else " ".join(str(w) for w in when_val) if isinstance(when_val, list)
            else ""
        )
        if when_str and _WINDOWS_GUARD_RE.search(when_str):
            continue

        cmd = _get_command_string(task)
        if not cmd:
            continue

        # Skip complex shell usage: pipes, redirects, loops, conditionals,
        # multi-line commands — these often require shell features that
        # modules can't replace.
        if any(c in cmd for c in ("\n", "|", ">", "<", ";", "&&", "||", "for ", "while ")):
            continue
        if re.search(r"(?:^|\s)docker\s+cp\b", cmd, re.IGNORECASE):
            continue

        match_command = _normalise_command_prefix(cmd)
        if _is_read_only_query(cmd):
            continue
        # Check each pattern
        for pattern, module_name, message in _SHELL_PATTERNS:
            if re.match(pattern, match_command, re.IGNORECASE):
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
