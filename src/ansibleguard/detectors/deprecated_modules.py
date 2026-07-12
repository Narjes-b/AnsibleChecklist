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

import yaml

# Map of deprecated module names → recommended replacement.
# Sourced from Ansible porting guides and module documentation.
# Last updated: Ansible 9.x / core 2.16 deprecations.
_DEPRECATED_MODULES = {
    # --- Docker (moved to community.docker collection) ---
    "docker": "community.docker.docker_container",
    "docker_container": "community.docker.docker_container",
    "docker_image": "community.docker.docker_image",
    "docker_network": "community.docker.docker_network",
    "docker_volume": "community.docker.docker_volume",
    "docker_compose": "community.docker.docker_compose_v2",
    "docker_swarm": "community.docker.docker_swarm",
    "docker_secret": "community.docker.docker_secret",
    "docker_config": "community.docker.docker_config",
    "docker_stack": "community.docker.docker_stack",
    # --- AWS (moved to amazon.aws / community.aws collections) ---
    "ec2": "amazon.aws.ec2_instance",
    "ec2_ami": "amazon.aws.ec2_ami",
    "ec2_key": "amazon.aws.ec2_key",
    "ec2_vol": "amazon.aws.ec2_vol",
    "ec2_vpc_net": "amazon.aws.ec2_vpc_net",
    "ec2_vpc_subnet": "amazon.aws.ec2_vpc_subnet",
    "ec2_tag": "amazon.aws.ec2_tag",
    "ec2_snapshot": "amazon.aws.ec2_snapshot",
    "ec2_instance": "amazon.aws.ec2_instance",
    "s3": "amazon.aws.s3_object",
    "s3_bucket": "amazon.aws.s3_bucket",
    "s3_lifecycle": "amazon.aws.s3_lifecycle",
    "iam": "amazon.aws.iam_role",
    "iam_policy": "amazon.aws.iam_policy",
    "route53": "amazon.aws.route53",
    # --- Networking ---
    "netscaler": "community.network.netscaler_*",
    "bigip": "community.network.bigip_*",
    "ios_command": "cisco.ios.ios_command",
    "ios_config": "cisco.ios.ios_config",
    "nxos_command": "cisco.nxos.nxos_command",
    "eos_command": "arista.eos.eos_command",
    # --- Windows ---
    "win_msi": "ansible.windows.win_package",
    "win_robocopy": "ansible.windows.win_robocopy",
    "win_chocolatey": "chocolatey.chocolatey.win_chocolatey",
    # --- Core deprecations ---
    "include": "include_tasks or import_tasks (use include_tasks for dynamic, import_tasks for static)",
    "action": "use dedicated module instead of low-level action plugin",
    # --- VMware ---
    "vsphere_guest": "community.vmware.vmware_guest",
    "vsphere_copy": "community.vmware.vmware_deployovf",
    # --- OpenStack ---
    "os_server": "openstack.cloud.server",
    "os_volume": "openstack.cloud.volume",
    "os_network": "openstack.cloud.network",
}

# Modules that are aliases (old names still work but warn)
_ALIASED_MODULES = {
    "authorized_key": "ansible.posix.authorized_key",
    "firewalld": "ansible.posix.firewalld",
    "mount": "ansible.posix.mount",
    "selinux": "ansible.posix.selinux",
    "seboolean": "ansible.posix.seboolean",
    "sysctl": "ansible.posix.sysctl",
    "acl": "ansible.posix.acl",
    "at": "ansible.posix.at",
    "ini_file": "community.general.ini_file",
    "jenkins_job": "community.general.jenkins_job",
    "datadog_monitor": "community.general.datadog_monitor",
    "git_config": "community.general.git_config",
    "npm": "community.general.npm",
    "pip": "ansible.builtin.pip",  # still in core but noted
}


def _collect_all_tasks(playbook):
    """Recursively collect all leaf tasks."""
    all_tasks = []

    def recurse(tasks):
        for task in tasks:
            if not isinstance(task, dict):
                continue
            for section in ("block", "rescue", "always"):
                if section in task and isinstance(task[section], list):
                    recurse(task[section])
                    break
            else:
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
    try:
        with open(yaml_file_path, "r", encoding="utf-8") as f:
            playbook = yaml.safe_load(f)
    except (yaml.YAMLError, FileNotFoundError) as e:
        print(f"Could not parse {yaml_file_path}: {e}")
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
            # Check deprecated modules
            if key in _DEPRECATED_MODULES:
                details.append({
                    "task_name": task_name,
                    "module": key,
                    "replacement": _DEPRECATED_MODULES[key],
                    "issue": (
                        f"Module '{key}' is deprecated. "
                        f"Use '{_DEPRECATED_MODULES[key]}' instead."
                    ),
                    "line": None,
                })
                break  # One module per task
            # Check aliased modules (old names)
            elif key in _ALIASED_MODULES:
                details.append({
                    "task_name": task_name,
                    "module": key,
                    "replacement": _ALIASED_MODULES[key],
                    "issue": (
                        f"Module '{key}' is aliased. "
                        f"Use FQCN '{_ALIASED_MODULES[key]}' instead."
                    ),
                    "line": None,
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
