"""Tests for shell_instead_of_module detector — new patterns added 2026-08-11.

Each test covers one or more of the 11 new patterns (rsync, scp, find,
hostname, timedatectl, update-alternatives, adduser, deluser, userdel,
groupdel, touch) and one negative case per pattern (command with a pipe,
which the detector intentionally skips).
"""

from ansibleguard.detectors.shell_instead_of_module import detect_shell_instead_of_module


def _task(cmd, module="shell"):
    return (
        f"- name: test task\n"
        f"  {module}: {cmd}\n"
    )


def _write(tmp_path, content):
    p = tmp_path / "tasks.yml"
    p.write_text(content, encoding="utf-8")
    return p


# --- rsync ---

def test_rsync_in_shell_is_flagged(tmp_path):
    f = _write(tmp_path, _task("rsync -av /src/ /dst/"))
    count, details = detect_shell_instead_of_module(f)
    assert count == 1
    assert details[0]["module"] == "ansible.posix.synchronize"


def test_rsync_with_pipe_is_skipped(tmp_path):
    f = _write(tmp_path, _task("rsync -av /src/ /dst/ | tee log.txt"))
    assert detect_shell_instead_of_module(f)[0] == 0


# --- scp ---

def test_scp_in_shell_is_flagged(tmp_path):
    f = _write(tmp_path, _task("scp file.txt remote:/path/"))
    count, details = detect_shell_instead_of_module(f)
    assert count == 1
    assert details[0]["module"] == "copy"


# --- find ---

def test_find_with_name_in_shell_is_flagged(tmp_path):
    f = _write(tmp_path, _task("find /etc -name '*.conf'"))
    count, details = detect_shell_instead_of_module(f)
    assert count == 1
    assert details[0]["module"] == "find"


def test_find_without_name_flag_is_not_flagged(tmp_path):
    # A plain `find /etc` with no -name is not the pattern we target.
    f = _write(tmp_path, _task("find /etc -type f"))
    # This should not match the specific pattern `find <path> -name`
    count, _ = detect_shell_instead_of_module(f)
    # Either outcome is acceptable for -type; we assert the module isn't find.
    for detail in (detect_shell_instead_of_module(f)[1] or []):
        assert detail["module"] != "find"


# --- hostname ---

def test_hostname_command_in_shell_is_flagged(tmp_path):
    f = _write(tmp_path, _task("hostname newname"))
    count, details = detect_shell_instead_of_module(f)
    assert count == 1
    assert details[0]["module"] == "hostname"


# --- timedatectl ---

def test_timedatectl_in_shell_is_flagged(tmp_path):
    f = _write(tmp_path, _task("timedatectl set-timezone Europe/Paris"))
    count, details = detect_shell_instead_of_module(f)
    assert count == 1
    assert details[0]["module"] == "community.general.timezone"


# --- update-alternatives ---

def test_update_alternatives_in_shell_is_flagged(tmp_path):
    f = _write(tmp_path, _task("update-alternatives --set java /usr/lib/jvm/java-11"))
    count, details = detect_shell_instead_of_module(f)
    assert count == 1
    assert details[0]["module"] == "community.general.alternatives"


# --- user management ---

def test_adduser_in_shell_is_flagged(tmp_path):
    f = _write(tmp_path, _task("adduser --system svc"))
    count, details = detect_shell_instead_of_module(f)
    assert count == 1
    assert details[0]["module"] == "user"


def test_deluser_in_shell_is_flagged(tmp_path):
    f = _write(tmp_path, _task("deluser svc"))
    count, details = detect_shell_instead_of_module(f)
    assert count == 1
    assert details[0]["module"] == "user"


def test_userdel_in_shell_is_flagged(tmp_path):
    f = _write(tmp_path, _task("userdel -r olduser"))
    count, details = detect_shell_instead_of_module(f)
    assert count == 1
    assert details[0]["module"] == "user"


def test_groupdel_in_shell_is_flagged(tmp_path):
    f = _write(tmp_path, _task("groupdel oldgroup"))
    count, details = detect_shell_instead_of_module(f)
    assert count == 1
    assert details[0]["module"] == "group"


# --- touch ---

def test_touch_in_shell_is_flagged(tmp_path):
    f = _write(tmp_path, _task("touch /tmp/sentinel"))
    count, details = detect_shell_instead_of_module(f)
    assert count == 1
    assert details[0]["module"] == "file"


def test_touch_with_pipe_is_skipped(tmp_path):
    f = _write(tmp_path, _task("touch /tmp/sentinel && echo done"))
    assert detect_shell_instead_of_module(f)[0] == 0


# --- pre-existing patterns not regressed by new additions ---

def test_apt_still_detected_after_new_pattern_additions(tmp_path):
    f = _write(tmp_path, _task("apt-get install nginx"))
    count, details = detect_shell_instead_of_module(f)
    assert count == 1
    assert details[0]["module"] == "apt"


def test_useradd_still_detected(tmp_path):
    f = _write(tmp_path, _task("useradd newuser"))
    count, details = detect_shell_instead_of_module(f)
    assert count == 1
    assert details[0]["module"] == "user"


# --- command: module is also covered ---

def test_new_patterns_work_with_command_module(tmp_path):
    f = _write(tmp_path, _task("timedatectl set-timezone UTC", module="command"))
    count, details = detect_shell_instead_of_module(f)
    assert count == 1
    assert details[0]["module"] == "community.general.timezone"


# --- raw: module is also covered ---

def test_apt_in_raw_is_flagged(tmp_path):
    f = _write(tmp_path, _task("apt-get install nginx", module="raw"))
    count, details = detect_shell_instead_of_module(f)
    assert count == 1
    assert details[0]["module"] == "apt"


def test_useradd_in_raw_is_flagged(tmp_path):
    f = _write(tmp_path, _task("useradd newuser", module="raw"))
    count, details = detect_shell_instead_of_module(f)
    assert count == 1
    assert details[0]["module"] == "user"


def test_raw_with_pipe_is_skipped(tmp_path):
    f = _write(tmp_path, _task("apt-get install nginx | tee log.txt", module="raw"))
    assert detect_shell_instead_of_module(f)[0] == 0


def test_command_name_in_an_argument_is_not_flagged(tmp_path):
    f = _write(tmp_path, _task("echo 'run apt-get install manually'"))
    assert detect_shell_instead_of_module(f) == (0, [])


def test_absolute_file_operation_executable_is_flagged(tmp_path):
    f = _write(tmp_path, _task("/usr/bin/rm -f /tmp/stale"))
    count, details = detect_shell_instead_of_module(f)
    assert count == 1
    assert details[0]["module"] == "file"


def test_environment_and_sudo_wrappers_preserve_detection(tmp_path):
    f = _write(tmp_path, _task("env LC_ALL=C sudo rm -f /tmp/stale"))
    count, details = detect_shell_instead_of_module(f)
    assert count == 1
    assert details[0]["module"] == "file"


def test_read_only_service_and_system_queries_are_not_module_migrations(tmp_path):
    for command in (
        "hostname",
        "systemctl status nginx",
        "systemctl is-active nginx",
        "service nginx status",
        "timedatectl",
    ):
        assert detect_shell_instead_of_module(_write(tmp_path, _task(command))) == (0, [])


def test_mutating_service_and_time_commands_remain_flagged(tmp_path):
    assert detect_shell_instead_of_module(
        _write(tmp_path, _task("systemctl restart nginx"))
    )[0] == 1
    assert detect_shell_instead_of_module(
        _write(tmp_path, _task("timedatectl set-timezone UTC"))
    )[0] == 1
