# OpenStack Ansible study workspace

This directory separates versioned study definitions from local/generated
data.

## Versioned files

- `manifests/candidates.csv`: OpenDev discovery snapshot; every row starts with
  `selected=false` and requires human review.
- `manifests/pilot.csv`: the five-project technical pilot selection.
- `manifests/file-classification/*.csv`: portable row-level classifications
  keyed by project and frozen SHA; every YAML candidate records an inclusion
  decision and reason.
- future construct mappings, protocols, and labeling schemas.

## Local generated files

The following paths are ignored by Git:

- `cache/`: downloaded OpenDev registry data;
- `repositories/`: full Git clones;
- `snapshots/`: AnsibleGuard outputs pinned by project and SHA;
- `history/`: longitudinal mining data;
- `analysis/`: derived statistics;
- `logs/`: command logs;
- `manifests/*-frozen.csv`: machine-specific collection manifests containing
  absolute repository paths.

Do not manually edit generated findings. Regenerate them from the versioned
selection manifest, frozen commit SHAs, detector version, and configuration.

See [`../LOCAL_OPENSTACK_STUDY_WORKFLOW.md`](../LOCAL_OPENSTACK_STUDY_WORKFLOW.md)
for exact commands and
[`../CLASSIFIED_FILE_MANIFEST_IMPLEMENTATION.md`](../CLASSIFIED_FILE_MANIFEST_IMPLEMENTATION.md)
for the schema, safeguards, and Nova result.

For the meaning of a frozen snapshot and the rule-profile strata, read
[`../WHAT_IS_A_SNAPSHOT_STUDY.md`](../WHAT_IS_A_SNAPSHOT_STUDY.md) and
[`../RESEARCH_PROFILES_IMPLEMENTATION.md`](../RESEARCH_PROFILES_IMPLEMENTATION.md).
