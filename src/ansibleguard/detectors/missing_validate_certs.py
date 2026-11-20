"""
Detects tasks that explicitly disable SSL/TLS certificate validation in an
Ansible module call.

Setting `validate_certs: false` disables certificate verification,
making the connection vulnerable to man-in-the-middle (MITM) attacks.
While there are legitimate cases (internal services with self-signed
certificates), the practice should be explicitly reviewed.

Reference:
  - Ansible uri module docs:
    https://docs.ansible.com/ansible/latest/collections/ansible/builtin/uri_module.html
  - Ansible get_url module docs:
    https://docs.ansible.com/ansible/latest/collections/ansible/builtin/get_url_module.html
  - CIS security best practices: always validate TLS certificates
    in production environments.

Detection strategy:
  Walk all leaf tasks (recurse into block/rescue/always).
  For any module invocation, check if validate_certs is explicitly set to
  false/no. This covers uri/get_url as well as modules such as unarchive and
  Slack integrations that expose the same security control.

Complexity: O(n) where n = number of tasks.
False positives: internal self-signed certs, dev environments.
Limitations: does not detect validate_certs set via variable
  (e.g., validate_certs: "{{ verify_ssl }}").
"""

from ansibleguard.detectors.source_lines import load_with_lines, source_line


# Modules that support HTTPS connections and accept validate_certs
_HTTPS_MODULES = {
    # ansible.builtin HTTPS modules
    "uri", "ansible.builtin.uri",
    "get_url", "ansible.builtin.get_url",
    # community.general network/API modules
    "slack", "community.general.slack",
    "hipchat", "community.general.hipchat",
    "telegram", "community.general.telegram",
    "rocketchat", "community.general.rocketchat",
    "mattermost", "community.general.mattermost",
    "campfire",
    "mail", "community.general.mail",
    # Cloud provider modules (commonly use HTTPS APIs)
    "aws_s3", "amazon.aws.s3_object",
    "ec2", "amazon.aws.ec2_instance",
    "s3_bucket", "amazon.aws.s3_bucket",
    "azure_rm_storageblob", "azure.azcollection.azure_rm_storageblob",
    "gcp_storage_bucket", "google.cloud.gcp_storage_bucket",
    # HTTP fetch / download modules
    "maven_artifact", "community.general.maven_artifact",
    "pip", "ansible.builtin.pip",
    # Infrastructure / API modules
    "github_release", "community.general.github_release",
    "gitlab_project", "community.general.gitlab_project",
    "jira", "community.general.jira",
    "jenkins_job", "community.general.jenkins_job",
    "nexus", "community.general.nexus",
    "influxdb_database", "community.general.influxdb_database",
}

# Values that explicitly disable certificate validation
_DISABLED_VALUES = {False, "false", "no", "False", "No", "NO"}

_TASK_META_KEYS = {
    "name", "when", "tags", "block", "rescue", "always", "register",
    "ignore_errors", "no_log", "become", "delegate_to", "run_once", "vars",
    "environment", "notify", "changed_when", "failed_when", "loop",
    "loop_control", "with_items",
}


def _collect_all_tasks(playbook):
    """Recursively collect all leaf tasks (not block/rescue/always wrappers).
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


def detect_missing_validate_certs(yaml_file_path, parsed_document=None):
    """
    Detect tasks that disable TLS certificate validation.

    Args:
        yaml_file_path: Path to an Ansible playbook YAML file.

    Returns:
        (count, details) where:
          count:   int — number of tasks with validate_certs disabled
          details: list[dict] — {"task_name", "module", "issue"} per flagged task
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

        for key, module_params in task.items():
            module_name = str(key)
            if module_name in _TASK_META_KEYS:
                continue
            if module_name in {"action", "local_action"} and isinstance(
                module_params, dict
            ):
                action_params = dict(module_params)
                action_module = str(action_params.pop("module", module_name))
                _check_params(
                    task_name,
                    action_module,
                    action_params,
                    details,
                    source_line(task, key),
                )
                continue
            _check_params(
                task_name,
                module_name,
                module_params,
                details,
                source_line(task, key),
            )

    return len(details), details


def _check_params(task_name, module_name, module_params, details, line=1):
    """Check if validate_certs is explicitly disabled in module parameters."""
    params = module_params if isinstance(module_params, dict) else {}
    val = params.get("validate_certs")
    if val is not None and val in _DISABLED_VALUES:
        details.append({
            "task_name": task_name,
            "module": module_name,
            "issue": (
                f"validate_certs is set to {val!r} in {module_name} — "
                "TLS certificate validation is disabled, making the "
                "connection vulnerable to MITM attacks."
            ),
            "line": line,
        })


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        count, details = detect_missing_validate_certs(sys.argv[1])
        print(f"Found {count} task(s) with validate_certs disabled:")
        for d in details:
            print(f"  - {d['task_name']}: {d['issue']}")
    else:
        print("Usage: python missing_validate_certs.py <playbook.yml>")
