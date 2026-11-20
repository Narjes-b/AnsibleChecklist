"""
Detects tasks using deprecated Ansible modules.

Ansible periodically deprecates modules in favor of newer, better
alternatives. Using deprecated modules means the playbook will break
in a future Ansible release. Each deprecated module is mapped to its
recommended replacement.

Reference:
  - Ansible porting guides:
    https://docs.ansible.com/ansible/latest/porting_guides/porting_guides.html
  - Ansible module index:
    https://docs.ansible.com/ansible/latest/collections/index_module.html

Detection strategy:
  Walk all leaf tasks (recurse into block/rescue/always).
  For each task, check whether the module key matches a known
  deprecated module. Flag with the recommended replacement.

Complexity: O(n) where n = number of tasks.
False positives: low — the mapping is based on documented deprecations.
Limitations: the deprecated module list is manually maintained and
  must be updated as new deprecations are announced.
"""

from pathlib import Path
import re
from functools import lru_cache

from packaging.version import InvalidVersion, Version

from ansibleguard.detectors.source_lines import load_with_lines, source_line

# Conservative fallback for real deprecations. Installed Ansible metadata is
# consulted first; moved/redirected names are deliberately kept separate.
_DEPRECATED_MODULES = {
    "docker": "community.docker.docker_container",
    "netscaler": "community.network.netscaler_*",
    "win_msi": "ansible.windows.win_package",
    "include": "include_tasks or import_tasks",
    "vsphere_guest": "community.vmware.vmware_guest",
}

_REDIRECTED_MODULES = {
    "docker_container": "community.docker.docker_container",
    "docker_image": "community.docker.docker_image",
    "docker_network": "community.docker.docker_network",
    "docker_volume": "community.docker.docker_volume",
    "docker_compose": "community.docker.docker_compose_v2",
    "ec2": "amazon.aws.ec2_instance",
    "ec2_ami": "amazon.aws.ec2_ami",
    "ec2_key": "amazon.aws.ec2_key",
    "ec2_vol": "amazon.aws.ec2_vol",
    "ec2_vpc_net": "amazon.aws.ec2_vpc_net",
    "ec2_vpc_subnet": "amazon.aws.ec2_vpc_subnet",
    "ec2_tag": "amazon.aws.ec2_tag",
    "ec2_snapshot": "amazon.aws.ec2_snapshot",
    "ec2_instance": "amazon.aws.ec2_instance",
    "s3": "amazon.aws.s3_object (for objects) or amazon.aws.s3_bucket (for buckets)",
    "s3_bucket": "amazon.aws.s3_bucket",
    "s3_lifecycle": "amazon.aws.s3_lifecycle",
    "iam": "amazon.aws.iam_role",
    "iam_policy": "amazon.aws.iam_policy",
    "route53": "amazon.aws.route53",
    "bigip": "community.network.bigip_*",
    "ios_command": "cisco.ios.ios_command",
    "ios_config": "cisco.ios.ios_config",
    "nxos_command": "cisco.nxos.nxos_command",
    "eos_command": "arista.eos.eos_command",
    "win_robocopy": "ansible.windows.win_robocopy",
    "win_chocolatey": "chocolatey.chocolatey.win_chocolatey",
    "vsphere_copy": "community.vmware.vmware_deployovf",
    "os_server": "openstack.cloud.server",
    "os_volume": "openstack.cloud.volume",
    "os_network": "openstack.cloud.network",
    "authorized_key": "ansible.posix.authorized_key",
    "firewalld": "ansible.posix.firewalld",
    "mount": "ansible.posix.mount",
    "selinux": "ansible.posix.selinux",
    "seboolean": "ansible.posix.seboolean",
    "sysctl": "ansible.posix.sysctl",
    "acl": "ansible.posix.acl",
    "ini_file": "community.general.ini_file",
    "jenkins_job": "community.general.jenkins_job",
    "datadog_monitor": "community.general.datadog_monitor",
    "git_config": "community.general.git_config",
    "npm": "community.general.npm",
}


def _installed_deprecation(module_name, module_metadata=None):
    metadata = (module_metadata or {}).get(module_name, {})
    doc = metadata.get("doc", {}) if isinstance(metadata, dict) else {}
    deprecated = (
        metadata.get("deprecated") if isinstance(metadata, dict) else None
    ) or (doc.get("deprecated") if isinstance(doc, dict) else None)
    return deprecated if isinstance(deprecated, dict) else {}


def _replacement(metadata):
    return (
        metadata.get("alternative")
        or metadata.get("replacement")
        or metadata.get("use_instead")
    )


ANSIBLE_VERSION_RE = re.compile(
    r"(?im)^\s*(?:ansible-core|ansible_core|ansible)\s*"
    r"(?:=|==|~=|>=|<=|>|<|:)\s*[\"']?(?:==|~=|>=|<=|>|<)?\s*"
    r"([0-9]+(?:\.[0-9]+){1,2})"
)


@lru_cache(maxsize=4096)
def _project_version_from_directory(directory):
    directory = Path(directory)
    candidates = [directory / "Pipfile", directory / "pyproject.toml"]
    candidates.extend(directory.glob("requirements*.txt"))
    for candidate in candidates:
        try:
            match = ANSIBLE_VERSION_RE.search(
                candidate.read_text(encoding="utf-8")
            )
        except (OSError, UnicodeError):
            continue
        if match:
            try:
                return Version(match.group(1))
            except InvalidVersion:
                pass
    if (directory / ".git").exists() or directory.parent == directory:
        return None
    return _project_version_from_directory(directory.parent)


def _project_ansible_version(path):
    """Find the nearest explicit Ansible pin/constraint in project files."""
    return _project_version_from_directory(Path(path).resolve().parent)


@lru_cache(maxsize=1)
def _installed_ansible_version():
    try:
        from ansible.release import __version__

        return Version(__version__)
    except (ImportError, InvalidVersion):
        return None


def _metadata_version(metadata, *keys):
    for key in keys:
        value = metadata.get(key)
        if not value:
            continue
        try:
            return Version(str(value))
        except InvalidVersion:
            continue
    return None


def _deprecation_applies(metadata, target_version, analyzer_version):
    """Avoid projecting newer analyzer metadata onto older pinned projects."""
    if target_version is None:
        return True
    removed_in = _metadata_version(metadata, "removed_in", "removal_version")
    if removed_in is not None and target_version >= removed_in:
        return True
    deprecated_since = _metadata_version(
        metadata, "deprecated_since", "deprecated_in", "version"
    )
    if deprecated_since is not None:
        return target_version >= deprecated_since
    if analyzer_version is None:
        return False
    return target_version >= analyzer_version


def _collect_all_tasks(playbook):
    """Recursively collect all leaf tasks.
    Processes ALL nested sections (block, rescue, always), not just the first."""
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


def detect_deprecated_modules(
    yaml_file_path, parsed_document=None, repository_context=None,
    module_metadata=None,
):
    """
    Detect tasks using deprecated Ansible modules.

    Args:
        yaml_file_path: Path to an Ansible playbook YAML file.

    Returns:
        (count, details) where:
          count:   int — number of tasks using deprecated modules
          details: list[dict] — {"task_name", "module", "replacement", "issue"}
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
    target_version = _project_ansible_version(yaml_file_path)
    analyzer_version = _installed_ansible_version()

    for task in all_tasks:
        task_name = task.get("name", "Unnamed task")

        # A task dict has keys like name:, module_name:, when:, etc.
        # Module keys are the ones not in the known meta-key set.
        meta_keys = {
            "name", "when", "tags", "block", "rescue", "always",
            "register", "ignore_errors", "no_log", "become",
            "delegate_to", "run_once", "any_errors_fatal",
            "vars", "environment", "notify", "changed_when",
            "failed_when", "with_items", "loop", "until", "retries",
            "delay", "async", "poll", "connection", "check_mode",
            "diff", "throttle", "serial", "remote_user",
            "gather_facts", "strategy", "collections",
            "max_fail_percentage", "order",
        }
        for key in task:
            if key in meta_keys:
                continue
            installed = _installed_deprecation(
                str(key),
                repository_context.module_metadata
                if repository_context is not None else module_metadata,
            )
            fallback = _DEPRECATED_MODULES.get(key)
            if installed and not _deprecation_applies(
                installed, target_version, analyzer_version
            ):
                installed = {}
            if installed or fallback:
                replacement = _replacement(installed) or fallback
                replacement_text = (
                    f" Use '{replacement}' instead." if replacement else ""
                )
                details.append({
                    "task_name": task_name,
                    "module": key,
                    "replacement": replacement,
                    "metadata_source": (
                        "installed-ansible-doc" if installed else "curated-fallback"
                    ),
                    "target_ansible_version": (
                        str(target_version) if target_version else None
                    ),
                    "issue": f"Module '{key}' is deprecated.{replacement_text}",
                    "line": source_line(task, key),
                })
                break  # One module per task

    return len(details), details


def detect_redirected_modules(yaml_file_path, parsed_document=None):
    """Report legacy redirects/FQCN advice without calling them deprecated."""
    playbook = (
        parsed_document.document
        if parsed_document is not None
        else load_with_lines(yaml_file_path)
    )
    if playbook is None:
        return 0, []
    details = []
    for task in _collect_all_tasks(playbook):
        task_name = task.get("name", "Unnamed task")
        for key in task:
            if key in _REDIRECTED_MODULES:
                details.append({
                    "task_name": task_name,
                    "module": key,
                    "replacement": _REDIRECTED_MODULES[key],
                    "issue": (
                        f"Module name '{key}' is a legacy redirect or short "
                        f"name. Prefer '{_REDIRECTED_MODULES[key]}'."
                    ),
                    "line": source_line(task, key),
                })
                break
    return len(details), details


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        count, details = detect_deprecated_modules(sys.argv[1])
        print(f"Found {count} task(s) using deprecated modules:")
        for d in details:
            print(f"  - {d['task_name']}: {d['module']} → {d['replacement']}")
    else:
        print("Usage: python deprecated_modules.py <playbook.yml>")
