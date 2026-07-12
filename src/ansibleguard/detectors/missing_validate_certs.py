"""
Detects tasks that disable SSL/TLS certificate validation when using
HTTPS-based Ansible modules (uri, get_url).

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
  For any task using uri: or get_url:, check if validate_certs
  is explicitly set to false/no. Flag as a warning.

Complexity: O(n) where n = number of tasks.
False positives: internal self-signed certs, dev environments.
Limitations: does not detect validate_certs set via variable
  (e.g., validate_certs: "{{ verify_ssl }}").
"""

import yaml


# Modules that support HTTPS connections and accept validate_certs
_HTTPS_MODULES = {
    "uri",
    "get_url",
    "ansible.builtin.uri",
    "ansible.builtin.get_url",
}

# Values that explicitly disable certificate validation
_DISABLED_VALUES = {False, "false", "no", "False", "No", "NO"}


def _collect_all_tasks(playbook):
    """Recursively collect all leaf tasks (not block/rescue/always wrappers)."""
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


def detect_missing_validate_certs(yaml_file_path):
    """
    Detect tasks that disable TLS certificate validation.

    Args:
        yaml_file_path: Path to an Ansible playbook YAML file.

    Returns:
        (count, details) where:
          count:   int — number of tasks with validate_certs disabled
          details: list[dict] — {"task_name", "module", "issue"} per flagged task
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

        # Check direct module keys (uri:, get_url:)
        for module_name in _HTTPS_MODULES:
            if module_name in task:
                module_params = task[module_name]
                _check_params(task_name, module_name, module_params, details)
                break  # A task has only one module

    return len(details), details


def _check_params(task_name, module_name, module_params, details):
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
            "line": None,
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
