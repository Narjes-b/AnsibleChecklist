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


def _installed_deprecation(module_name):
    from ansibleguard.detectors.missing_checklist import _module_document

    metadata = _module_document(module_name)
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
            if "tasks" in entry and isinstance(entry["tasks"], list):
                recurse(entry["tasks"])
            elif "block" in entry and isinstance(entry["block"], list):
                recurse(entry["block"])
            elif "hosts" not in entry:
                recurse([entry])
    return all_tasks


def detect_deprecated_modules(yaml_file_path):
    """
    Detect tasks using deprecated Ansible modules.

    Args:
        yaml_file_path: Path to an Ansible playbook YAML file.

    Returns:
        (count, details) where:
          count:   int — number of tasks using deprecated modules
          details: list[dict] — {"task_name", "module", "replacement", "issue"}
    """
    playbook = load_with_lines(yaml_file_path)
    if playbook is None:
        return 0, []

    all_tasks = _collect_all_tasks(playbook)
    details = []

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
            installed = _installed_deprecation(str(key))
            fallback = _DEPRECATED_MODULES.get(key)
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
                    "issue": f"Module '{key}' is deprecated.{replacement_text}",
                    "line": source_line(task, key),
                })
                break  # One module per task

    return len(details), details


def detect_redirected_modules(yaml_file_path):
    """Report legacy redirects/FQCN advice without calling them deprecated."""
    playbook = load_with_lines(yaml_file_path)
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
