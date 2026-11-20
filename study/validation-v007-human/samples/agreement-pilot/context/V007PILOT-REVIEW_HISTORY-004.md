# Frozen Git review context: V007PILOT-REVIEW_HISTORY-004

- Repository: `ome/prod-playbooks`
- Target commit: `1e935ebbd3344066db3a175fbe4e89c55ffc930b`
- Actual first parent: `f431e8e5998c8b38084de3c1f7fcb551e1b2e39d`
- Evidence type: actual first-parent diff
- Family: Review/history
- Rule: `ansibleguard/missing-test-update`
- Codebook: `codebooks/FAMILY_REVIEW_HISTORY.md`
- Diff range: `f431e8e5998c8b38084de3c1f7fcb551e1b2e39d..1e935ebbd3344066db3a175fbe4e89c55ffc930b` (from frozen Git objects)
- No detector message or scan-time `base: null` fallback is used as review evidence.

## Exact target commit message

```text
Merge pull request #391 from pwalczysko/post-deploy-fix

Adjust django-redis version
```

## Changed paths (1)

- `M` `playbooks/ome-demoserver.yml`

## Relevant first-parent diff

```diff
diff --git a/playbooks/ome-demoserver.yml b/playbooks/ome-demoserver.yml
index 4ff358e..05e4871 100644
--- a/playbooks/ome-demoserver.yml
+++ b/playbooks/ome-demoserver.yml
@@ -65,11 +65,11 @@
         - "omero-signup=={{ omero_signup_release }}"
         - "omero-py>={{ omero_py_release }}"
         # This is to force minimal Django version - optional
         - "Django>=5.2.10"
         # necessary as omero.web.caches configured with redis
-        - "django-redis==5.3.0"
+        - "django-redis>=6"
 
     - role: ome.omero_user
       no_log: true
       omero_user_system: omero-server
       omero_user_admin_user: root

```
