"""Discover candidate OpenStack repositories for the AnsibleGuard study.

OpenDev project-config is authoritative. GitHub URLs are emitted only as
convenient mirror metadata; GitHub pull requests are not study evidence.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path
import time

import requests
import yaml


PROJECTS_URL = (
    "https://opendev.org/openstack/project-config/"
    "raw/branch/master/gerrit/projects.yaml"
)
DEFAULT_CACHE = Path("study/cache/openstack-projects.yaml")
DEFAULT_OUTPUT = Path("study/manifests/candidates.csv")
SEED_PROJECTS = {
    "openstack/ansible-collection-kolla",
    "openstack/bifrost",
    "openstack/kayobe",
    "openstack/kayobe-config",
    "openstack/kayobe-config-dev",
    "openstack/kolla-ansible",
    "openstack/openstack-ansible",
}
KEYWORDS = ("ansible", "bifrost", "kayobe")
FIELDS = (
    "project",
    "description",
    "groups",
    "opendev_url",
    "github_url",
    "discovery_reason",
    "retired",
    "selected",
    "exclusion_reason",
    "registry_source",
    "registry_fetched_at_utc",
)


def _download(url, timeout=45, retries=5):
    delay = 2
    headers = {"User-Agent": "ansibleguard-openstack-study/1"}
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
        except requests.RequestException:
            if attempt == retries - 1:
                raise
            time.sleep(delay)
            delay = min(delay * 2, 30)
            continue
        if response.status_code in {429, 500, 502, 503, 504}:
            if attempt == retries - 1:
                response.raise_for_status()
            retry_after = response.headers.get("Retry-After")
            time.sleep(int(retry_after) if retry_after else delay)
            delay = min(delay * 2, 30)
            continue
        response.raise_for_status()
        return response.text
    raise RuntimeError(f"Could not download {url}")


def load_registry(cache_path=DEFAULT_CACHE, offline=False, source_url=PROJECTS_URL):
    cache_path = Path(cache_path)
    if offline:
        if not cache_path.is_file():
            raise FileNotFoundError(f"Offline cache does not exist: {cache_path}")
        text = cache_path.read_text(encoding="utf-8")
        fetched_at = datetime.fromtimestamp(
            cache_path.stat().st_mtime, timezone.utc
        ).isoformat()
    else:
        text = _download(source_url)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(text, encoding="utf-8")
        # Use the cache mtime as the persisted provenance timestamp so an
        # offline rerun produces byte-for-byte identical manifest rows.
        fetched_at = datetime.fromtimestamp(
            cache_path.stat().st_mtime, timezone.utc
        ).isoformat()
    entries = yaml.safe_load(text) or []
    if not isinstance(entries, list):
        raise ValueError("OpenDev project registry must contain a YAML list")
    return entries, fetched_at


def _as_groups(entry):
    groups = entry.get("groups") or []
    if isinstance(groups, str):
        groups = [groups]
    return sorted(str(group) for group in groups)


def _retired(entry):
    description = str(entry.get("description") or "")
    acl = str(entry.get("acl-config") or "")
    return description.lstrip().upper().startswith("RETIRED") or "retired" in acl.lower()


def candidate_rows(entries, fetched_at, source_url=PROJECTS_URL):
    rows = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        project = str(entry.get("project") or "")
        if not project.startswith("openstack/"):
            continue
        description = str(entry.get("description") or "")
        groups = _as_groups(entry)
        searchable = " ".join((project, description, *groups)).lower()
        reasons = []
        if project in SEED_PROJECTS:
            reasons.append("seed")
        if "ansible" in searchable:
            reasons.append("ansible-keyword")
        if any(keyword in searchable for keyword in ("bifrost", "kayobe")):
            reasons.append("ansible-project-family")
        if not reasons:
            continue
        retired = _retired(entry)
        rows.append(
            {
                "project": project,
                "description": description,
                "groups": ";".join(groups),
                "opendev_url": f"https://opendev.org/{project}.git",
                "github_url": f"https://github.com/{project}",
                "discovery_reason": ";".join(sorted(set(reasons))),
                "retired": str(retired).lower(),
                # Human review is mandatory. Discovery never auto-selects.
                "selected": "false",
                "exclusion_reason": "retired" if retired else "",
                "registry_source": source_url,
                "registry_fetched_at_utc": fetched_at,
            }
        )
    return sorted(rows, key=lambda row: row["project"])


def write_manifest(rows, output_path=DEFAULT_OUTPUT):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Discover OpenStack repositories likely to contain Ansible code."
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--cache", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--source-url", default=PROJECTS_URL)
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Read the cached registry without making a network request.",
    )
    args = parser.parse_args(argv)
    entries, fetched_at = load_registry(
        args.cache, offline=args.offline, source_url=args.source_url
    )
    rows = candidate_rows(entries, fetched_at, args.source_url)
    output = write_manifest(rows, args.output)
    active = sum(row["retired"] == "false" for row in rows)
    print(f"Wrote {len(rows)} candidates ({active} active) to {output}")
    print("Review the CSV and set selected=true only for repositories to collect.")


if __name__ == "__main__":
    main()
