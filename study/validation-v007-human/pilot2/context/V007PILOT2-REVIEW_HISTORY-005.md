# Frozen Git review context: V007PILOT2-REVIEW_HISTORY-005

- Repository: `manala/ansible-roles`
- Target commit: `1ae6394d7b780665788234418ace2a060903f5f1`
- Actual first parent: `f2bc5c4c60665fdc1ccaf2d55da0cf3f440c5905`
- Evidence type: actual first-parent diff, all changed paths
- Family: review_history
- Rule: `ansibleguard/missing-test-update`
- Codebook: `codebooks-v2/FAMILY_REVIEW_HISTORY_V2.md`
- Author and committer identities are not part of the evidence and are not included.

## Exact target commit message

```text
Release
```

## Changed paths (2)

- `M` `CHANGELOG.md`
- `M` `galaxy.yml`

## First-parent diff (every changed path)

### `CHANGELOG.md`
```diff
diff --git a/CHANGELOG.md b/CHANGELOG.md
index c3ff529a..ab9dd9cd 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -5,13 +5,18 @@ All notable changes to this project will be documented in this file.
 The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
 and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
 
 ## [Unreleased]
 
+## [5.5.2] - 2026-06-16
+
 ### Added
 - [Alloy] Add environment support (`manala_alloy_environment`) for managing `/etc/default/alloy` via lineinfile
 
+### Fixed
+- [Files] Forward recurse to file module for directory state
+
 ## [5.5.1] - 2026-05-22
 
 ### Fixed
 - [Files] Avoid `KeyError: 'diff'` in `files_attributes` action plugin when wrapped modules do not return a `diff` key (Ansible core 2.20+)
 
```

### `galaxy.yml`
```diff
diff --git a/galaxy.yml b/galaxy.yml
index 03bfd399..42448e52 100644
--- a/galaxy.yml
+++ b/galaxy.yml
@@ -6,11 +6,11 @@ namespace: manala
 
 # The name of the collection. Has the same character restrictions as 'namespace'
 name: roles
 
 # The version of the collection. Must be compatible with semantic versioning
-version: 5.5.1
+version: 5.5.2
 
 # The path to the Markdown (.md) readme file. This path is relative to the root of the collection
 readme: README.md
 
 # A list of the collection's content authors. Can be just the name or in the format 'Full Name <email> (url)
```

