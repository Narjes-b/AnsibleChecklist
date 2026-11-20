#!/usr/bin/env python3
"""Reproduce the committed v0.0.5 15-repository diagnostic cohort."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


DIAGNOSTIC_PROJECTS = (
    "roots/trellis",
    "ManageIQ/manageiq",
    "ansible/workshops",
    "dbrennand/home-ops",
    "fgci-org/fgci-ansible",
    "dell/omnia",
    "openstack-k8s-operators/ci-framework",
    "redhat-openstack/infrared",
    "ansible-lockdown/RHEL7-STIG",
    "CentOS-PaaS-SIG/linchpin",
    "confluentinc/cp-ansible",
    "spantaleev/matrix-docker-ansible-deploy",
    "AtlasOfLivingAustralia/ala-install",
    "ministryofjustice/modernisation-platform-configuration-management",
    "ceph/ceph-ansible",
)


def build_cohort(source: Path, destination: Path) -> int:
    with Path(source).open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
        fields = list(rows[0]) if rows else []
    if not fields or "project" not in fields:
        raise ValueError(f"source manifest has no project column: {source}")
    by_project = {row["project"]: row for row in rows}
    missing = [name for name in DIAGNOSTIC_PROJECTS if name not in by_project]
    if missing:
        raise ValueError(
            "source manifest is missing diagnostic projects: "
            + ", ".join(missing)
        )
    selected = [by_project[name] for name in DIAGNOSTIC_PROJECTS]
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as stream:
        # Match the original research-manifest writer byte-for-byte.
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(selected)
    return len(selected)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "source", type=Path,
        help="Frozen 149-repository manifest",
    )
    parser.add_argument(
        "--output", type=Path,
        default=Path("study/manifests/v005-diagnostic-15.csv"),
    )
    args = parser.parse_args(argv)
    count = build_cohort(args.source, args.output)
    print(f"wrote {count} diagnostic repositories to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
