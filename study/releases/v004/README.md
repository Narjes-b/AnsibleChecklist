# AnsibleGuard v0.0.4 compact evidence package

This directory is the versioned, checksum-addressed home for compact evidence.
Rebuild it with:

```bash
.venv/bin/python scripts/build_v004_release_package.py
cd study/releases/v004
sha256sum --check checksums.sha256
cd ../../..
```

The historical 149-repository labels are calibration/tuning evidence. They are
not an independent held-out precision estimate. The PR package is controlled
anti-pattern injection evidence, and the recall package measures synthetic
injection detection rate. Neither is labeled as natural PR precision or
natural recall.

`provenance.json` deliberately records the three missing publication gates:
independent human labels, a source-first natural recall reference set, and
natural pull-request validation. Those fields must not be changed to completed
until the corresponding immutable files are added and independently reviewed.

Large raw scan trees remain outside Git and should be published to Zenodo/OSF
or a release artifact. Fill in the DOI and archive SHA-256 in provenance only
after upload; never point a paper at an unversioned local directory.

The integrated semantic freeze is commit
`645b6c5521f992c6d40e7c9159812468908373e6`. Its retained research image is
`ansibleguard-research:v004-integrated-freeze` with image ID
`sha256:429955276b3d9564772a2a3d8d66af2ed940a6b93a4f4483c50475e089a2ca1d`.
The image embeds the same commit SHA and passed the full suite plus the pinned
public local/Git/archive equivalence gate and the 8-case calibration gate with
no errors. The future 149-repository study still uses frozen local checkouts
and manifests through `LocalSource`.
