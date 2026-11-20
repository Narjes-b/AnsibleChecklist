# Frozen Git review context: V007PILOT-REVIEW_HISTORY-043

- Repository: `trailofbits/algo`
- Target commit: `20e22a8715c198b38c01c1ca62d0953b93587a74`
- Actual first parent: unavailable locally and not required for this message-only rule
- Evidence type: exact target commit message only
- Family: Review/history
- Rule: `ansibleguard/commit-message-format`
- Codebook: `codebooks/FAMILY_REVIEW_HISTORY.md`
- Diff range: not used for this message-only rule
- No detector message or scan-time `base: null` fallback is used as review evidence.

## Exact target commit message

```text
chore(deps): bump the github-actions group across 1 directory with 6 updates (#15030)

Bumps the github-actions group with 6 updates in the / directory:

| Package | From | To |
| --- | --- | --- |
| [actions/checkout](https://github.com/actions/checkout) | `7.0.0` | `7.0.1` |
| [docker/setup-buildx-action](https://github.com/docker/setup-buildx-action) | `4.1.0` | `4.2.0` |
| [docker/login-action](https://github.com/docker/login-action) | `4.2.0` | `4.4.0` |
| [docker/metadata-action](https://github.com/docker/metadata-action) | `6.1.0` | `6.2.0` |
| [actions/setup-python](https://github.com/actions/setup-python) | `6.3.0` | `7.0.0` |
| [dorny/paths-filter](https://github.com/dorny/paths-filter) | `4.0.1` | `4.0.2` |



Updates `actions/checkout` from 7.0.0 to 7.0.1
- [Release notes](https://github.com/actions/checkout/releases)
- [Changelog](https://github.com/actions/checkout/blob/main/CHANGELOG.md)
- [Commits](https://github.com/actions/checkout/compare/9c091bb21b7c1c1d1991bb908d89e4e9dddfe3e0...3d3c42e5aac5ba805825da76410c181273ba90b1)

Updates `docker/setup-buildx-action` from 4.1.0 to 4.2.0
- [Release notes](https://github.com/docker/setup-buildx-action/releases)
- [Commits](https://github.com/docker/setup-buildx-action/compare/d7f5e7f509e45cec5c76c4d5afdd7de93d0b3df5...bb05f3f5519dd87d3ba754cc423b652a5edd6d2c)

Updates `docker/login-action` from 4.2.0 to 4.4.0
- [Release notes](https://github.com/docker/login-action/releases)
- [Commits](https://github.com/docker/login-action/compare/650006c6eb7dba73a995cc03b0b2d7f5ca915bee...af1e73f918a031802d376d3c8bbc3fe56130a9b0)

Updates `docker/metadata-action` from 6.1.0 to 6.2.0
- [Release notes](https://github.com/docker/metadata-action/releases)
- [Commits](https://github.com/docker/metadata-action/compare/80c7e94dd9b9319bd5eb7a0e0fe9291e23a2a2e9...dc802804100637a589fabce1cb79ff13a1411302)

Updates `actions/setup-python` from 6.3.0 to 7.0.0
- [Release notes](https://github.com/actions/setup-python/releases)
- [Commits](https://github.com/actions/setup-python/compare/ece7cb06caefa5fff74198d8649806c4678c61a1...5fda3b95a4ea91299a34e894583c3862153e4b97)

Updates `dorny/paths-filter` from 4.0.1 to 4.0.2
- [Release notes](https://github.com/dorny/paths-filter/releases)
- [Changelog](https://github.com/dorny/paths-filter/blob/master/CHANGELOG.md)
- [Commits](https://github.com/dorny/paths-filter/compare/fbd0ab8f3e69293af611ebaee6363fc25e6d187d...7b450fff21473bca461d4b92ce414b9d0420d706)

---
updated-dependencies:
- dependency-name: actions/checkout
  dependency-version: 7.0.1
  dependency-type: direct:production
  update-type: version-update:semver-patch
  dependency-group: github-actions
- dependency-name: docker/setup-buildx-action
  dependency-version: 4.2.0
  dependency-type: direct:production
  update-type: version-update:semver-minor
  dependency-group: github-actions
- dependency-name: docker/login-action
  dependency-version: 4.4.0
  dependency-type: direct:production
  update-type: version-update:semver-minor
  dependency-group: github-actions
- dependency-name: docker/metadata-action
  dependency-version: 6.2.0
  dependency-type: direct:production
  update-type: version-update:semver-minor
  dependency-group: github-actions
- dependency-name: actions/setup-python
  dependency-version: 7.0.0
  dependency-type: direct:production
  update-type: version-update:semver-major
  dependency-group: github-actions
- dependency-name: dorny/paths-filter
  dependency-version: 4.0.2
  dependency-type: direct:production
  update-type: version-update:semver-patch
  dependency-group: github-actions
...

Signed-off-by: dependabot[bot] <support@github.com>
Co-authored-by: dependabot[bot] <49699333+dependabot[bot]@users.noreply.github.com>
```

## Changed paths (not required for message-only evidence)

- [not used; this rule is evaluated on the exact target commit message]

The rule is evaluated only on the exact target commit message above. No parent/diff fallback or AI/detector label is used.
