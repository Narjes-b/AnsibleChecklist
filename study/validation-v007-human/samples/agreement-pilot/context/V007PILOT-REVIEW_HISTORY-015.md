# Frozen Git review context: V007PILOT-REVIEW_HISTORY-015

- Repository: `manala/ansible-roles`
- Target commit: `1ae6394d7b780665788234418ace2a060903f5f1`
- Actual first parent: `f2bc5c4c60665fdc1ccaf2d55da0cf3f440c5905`
- Evidence type: actual first-parent diff
- Family: Review/history
- Rule: `ansibleguard/missing-release-note`
- Codebook: `codebooks/FAMILY_REVIEW_HISTORY.md`
- Diff range: `f2bc5c4c60665fdc1ccaf2d55da0cf3f440c5905..1ae6394d7b780665788234418ace2a060903f5f1` (from frozen Git objects)
- No detector message or scan-time `base: null` fallback is used as review evidence.

## Exact target commit message

```text
Release
```

## Changed paths (2)

- `M` `CHANGELOG.md`
- `M` `galaxy.yml`

## Relevant first-parent diff

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
