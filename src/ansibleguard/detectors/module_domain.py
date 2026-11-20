"""Module-domain taxonomy and Shannon-entropy cohesion helpers.

Every task in a playbook has a module. We bucket modules into broad functional
domains (package, service, file, …) and measure how spread the tasks are across
those domains using normalised Shannon entropy.

    similarity = 1 - H / log2(N)

where H is the entropy over the domain distribution and N is the number of
distinct domains present.  similarity=1 means every task shares one domain
(fully cohesive); similarity=0 means tasks are spread perfectly uniformly
across all domains present (maximally diverse).
"""

import math
from collections import Counter

from ansibleguard.task_semantics import TASK_META_KEYS, task_action

_RESERVED_TASK_KEYS = TASK_META_KEYS

_DOMAIN_MAP = {
    # package management
    "apt": "package",
    "apt_key": "package",
    "apt_repository": "package",
    "yum": "package",
    "yum_repository": "package",
    "dnf": "package",
    "dnf5": "package",
    "pip": "package",
    "pip3": "package",
    "gem": "package",
    "package": "package",
    "apk": "package",
    "dpkg": "package",
    "rpm": "package",
    "rpm_key": "package",
    "zypper": "package",
    "zypper_repository": "package",
    "easy_install": "package",
    "homebrew": "package",
    "pacman": "package",
    "portage": "package",
    "pkg5": "package",
    "openbsd_pkg": "package",
    "snap": "package",
    "flatpak": "package",
    # service management
    "service": "service",
    "service_facts": "service",
    "systemd": "service",
    "systemd_service": "service",
    "supervisorctl": "service",
    "sysvinit": "service",
    "runit": "service",
    "openrc_service": "service",
    # file and content management
    "file": "file",
    "copy": "file",
    "template": "file",
    "fetch": "file",
    "stat": "file",
    "find": "file",
    "assemble": "file",
    "patch": "file",
    "replace": "file",
    "lineinfile": "file",
    "blockinfile": "file",
    "ini_file": "file",
    "xml": "file",
    "synchronize": "file",
    "unarchive": "file",
    "archive": "file",
    "get_url": "file",
    "slurp": "file",
    "tempfile": "file",
    "read_csv": "file",
    "acl": "file",
    "iso_extract": "file",
    # user and group management
    "user": "user",
    "group": "user",
    "authorized_key": "user",
    "openssh_keypair": "user",
    "known_hosts": "user",
    # command execution
    "command": "command",
    "shell": "command",
    "raw": "command",
    "script": "command",
    "expect": "command",
    # network
    "uri": "network",
    "firewalld": "network",
    "ufw": "network",
    "iptables": "network",
    "nmcli": "network",
    "interfaces_file": "network",
    "haproxy": "network",
    "wait_for": "network",
    "wait_for_connection": "network",
    "get_url": "network",
    "ping": "network",
    # source control
    "git": "source_control",
    "github_release": "source_control",
    "github_deploy_key": "source_control",
    "svn": "source_control",
    "subversion": "source_control",
    "hg": "source_control",
    # database
    "mysql_db": "database",
    "mysql_user": "database",
    "mysql_query": "database",
    "postgresql_db": "database",
    "postgresql_user": "database",
    "postgresql_query": "database",
    "mongodb_collection": "database",
    "mongodb_user": "database",
    "influxdb_database": "database",
    "redis": "database",
    "sqlite3": "database",
    # cloud / infrastructure
    "ec2": "cloud_infra",
    "ec2_instance": "cloud_infra",
    "ec2_group": "cloud_infra",
    "s3_bucket": "cloud_infra",
    "s3_object": "cloud_infra",
    "cloudformation": "cloud_infra",
    "gcp_compute_instance": "cloud_infra",
    "azure_rm_virtualmachine": "cloud_infra",
    "openstack_server": "cloud_infra",
    "os_server": "cloud_infra",
    "terraform": "cloud_infra",
    # container
    "docker_container": "container",
    "docker_image": "container",
    "docker_network": "container",
    "docker_volume": "container",
    "docker_compose": "container",
    "podman_container": "container",
    "podman_image": "container",
    "k8s": "container",
    "k8s_info": "container",
    "helm": "container",
    # notification / messaging
    "mail": "notification",
    "slack": "notification",
    "hipchat": "notification",
    "pagerduty": "notification",
    "telegram": "notification",
    "jabber": "notification",
    "pushover": "notification",
    "twilio": "notification",
    # system configuration
    "hostname": "system_config",
    "timezone": "system_config",
    "sysctl": "system_config",
    "cron": "system_config",
    "cron_var": "system_config",
    "at": "system_config",
    "mount": "system_config",
    "kernel_blacklist": "system_config",
    "alternatives": "system_config",
    "selinux": "system_config",
    "seport": "system_config",
    "ntp": "system_config",
    "ntp_peer": "system_config",
    "pamd": "system_config",
    "pam_limits": "system_config",
    "reboot": "system_config",
    "shutdown": "system_config",
    "locale_gen": "system_config",
    "ufw": "system_config",
    "logrotate": "system_config",
    "rsyslog": "system_config",
    # control flow / debug (not a functional module domain)
    "debug": "control",
    "assert": "control",
    "fail": "control",
    "pause": "control",
    "set_fact": "control",
    "set_stats": "control",
    "include_vars": "control",
    "include_tasks": "control",
    "import_tasks": "control",
    "include_role": "control",
    "import_role": "control",
    "include_playbook": "control",
    "import_playbook": "control",
    "meta": "control",
    "vars_prompt": "control",
    "add_host": "control",
    "group_by": "control",
    "gather_facts": "control",
    "setup": "control",
}


def _strip_fqcn(module_name):
    """Strip namespace.collection. prefix from a fully-qualified collection name."""
    parts = module_name.split(".")
    if len(parts) >= 3:
        return ".".join(parts[2:])
    return module_name


def _module_domain(module_name):
    return _DOMAIN_MAP.get(_strip_fqcn(module_name), "other")


def _task_module(task):
    """Return the module name from a task dict, or None for block/control tasks."""
    return task_action(task)


def _collect_modules_from_tasks(tasks):
    """Recursively collect module names from a task list (including blocks)."""
    modules = []
    for task in tasks:
        if not isinstance(task, dict):
            continue
        module = _task_module(task)
        if module:
            modules.append(module)
        for section in ("block", "rescue", "always"):
            if section in task and isinstance(task[section], list):
                modules.extend(_collect_modules_from_tasks(task[section]))
    return modules


# Control-flow tasks (debug, set_fact, include_tasks, …) are structural
# scaffolding that appears in almost every playbook regardless of its purpose.
# Including them in the entropy distribution would dilute every score and make
# "install nginx + restart nginx + 3 set_facts" look less cohesive than it
# actually is.  We keep them in _DOMAIN_MAP for labelling but exclude them
# from the entropy calculation.
_ENTROPY_EXCLUDED_DOMAINS = frozenset({"control"})

# Module diversity alone is not evidence of poor cohesion.  In particular,
# package -> file/template -> service is the normal lifecycle of an Ansible
# role.  Cohesion findings therefore use a deliberately conservative gate on
# top of the entropy score.  The detector only reports a candidate when a
# reasonably large play spans several *specialised* responsibility domains,
# no domain dominates, and the result cannot be explained by the common
# service-deployment lifecycle.
_LIFECYCLE_DOMAINS = frozenset({
    "package",
    "file",
    "service",
    "user",
    "network",
    "system_config",
    "source_control",
    "command",
})
_SPECIALISED_DOMAINS = frozenset({
    "cloud_infra",
    "container",
    "database",
    "notification",
})

MIN_COHESION_TASKS = 8
MIN_COHESION_DOMAINS = 4
MIN_SPECIALISED_DOMAINS = 3
MAX_DOMINANT_DOMAIN_SHARE = 0.50


def domain_entropy(modules):
    """Return (similarity, domain_counts) for a list of module names.

    Control-flow modules (debug, set_fact, include_tasks, …) are excluded
    from the distribution before entropy is computed — they are structural
    scaffolding, not functional work.

    similarity = 1 - normalised_H, where normalised_H = H / log2(N_domains).
    Returns similarity=1.0 when fewer than 2 functional domains are present.
    domain_counts reflects only the functional domains used in the calculation.
    """
    if not modules:
        return 1.0, {}

    domains = [
        d for d in (_module_domain(m) for m in modules)
        if d not in _ENTROPY_EXCLUDED_DOMAINS
    ]

    if not domains:
        return 1.0, {}

    counts = Counter(domains)
    n_domains = len(counts)

    if n_domains <= 1:
        return 1.0, dict(counts)

    total = len(domains)
    entropy = 0.0
    for count in counts.values():
        p = count / total
        entropy -= p * math.log2(p)

    max_entropy = math.log2(n_domains)
    similarity = 1.0 - entropy / max_entropy
    return similarity, dict(counts)


def cohesion_evidence(modules):
    """Return conservative evidence for a multi-responsibility play.

    The returned mapping is intentionally richer than a bare threshold so a
    future corpus run can audit *why* a play fired.  ``is_incohesive`` means
    "strong static candidate for manual review", not semantic proof.
    Unknown modules are excluded because mapping them all to ``other`` would
    manufacture a misleading common domain.
    """
    known_modules = [
        module for module in modules if _module_domain(module) != "other"
    ]
    similarity, counts = domain_entropy(known_modules)
    functional_tasks = sum(counts.values())
    domains = frozenset(counts)
    specialised = domains & _SPECIALISED_DOMAINS
    dominant_share = (
        max(counts.values()) / functional_tasks if functional_tasks else 1.0
    )
    lifecycle_only = bool(domains) and domains <= _LIFECYCLE_DOMAINS

    is_incohesive = (
        functional_tasks >= MIN_COHESION_TASKS
        and len(domains) >= MIN_COHESION_DOMAINS
        and len(specialised) >= MIN_SPECIALISED_DOMAINS
        and dominant_share <= MAX_DOMINANT_DOMAIN_SHARE
        and not lifecycle_only
    )
    return {
        "is_incohesive": is_incohesive,
        "similarity": similarity,
        "functional_tasks": functional_tasks,
        "domain_counts": counts,
        "specialised_domains": sorted(specialised),
        "dominant_share": dominant_share,
        "lifecycle_only": lifecycle_only,
    }
