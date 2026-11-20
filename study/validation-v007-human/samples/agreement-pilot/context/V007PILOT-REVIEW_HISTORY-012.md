# Frozen Git review context: V007PILOT-REVIEW_HISTORY-012

- Repository: `IDR/deployment`
- Target commit: `77f7a7e438a41ca775e85b629c0f84cc636ffad7`
- Actual first parent: `f7e2258900faa2d643e5e3749c1140c9e96c7ba6`
- Evidence type: actual first-parent diff
- Family: Review/history
- Rule: `ansibleguard/missing-test-update`
- Codebook: `codebooks/FAMILY_REVIEW_HISTORY.md`
- Diff range: `f7e2258900faa2d643e5e3749c1140c9e96c7ba6..77f7a7e438a41ca775e85b629c0f84cc636ffad7` (from frozen Git objects)
- No detector message or scan-time `base: null` fallback is used as review evidence.

## Exact target commit message

```text
Merge pull request #462 from dominikl/revert_ms

revert back to 2024.08.13 version
```

## Changed paths (1)

- `M` `ansible/idr-omero-readonly.yml`

## Relevant first-parent diff

```diff
diff --git a/ansible/idr-omero-readonly.yml b/ansible/idr-omero-readonly.yml
index 9bfc993..6c52d2b 100644
--- a/ansible/idr-omero-readonly.yml
+++ b/ansible/idr-omero-readonly.yml
@@ -254,9 +254,9 @@
 - hosts: "{{ idr_environment | default('idr') }}-omeroreadonly-hosts"
   become: true
 
   roles:
   - role: ome.omero_ms_image_region
-    omero_ms_image_region_download_URL: 'https://github.com/ome/omero-ms-image-region/releases/download/v2025.11.05/omero-ms-image-region-0.10.0_21.zip'
-    omero_ms_image_region_package_sha256: 128c1d27059c748a828908d60619814ace65376bc3040b5d8146154579a13003
+    omero_ms_image_region_download_URL: 'https://github.com/ome/omero-ms-image-region/releases/download/2024.08.13/omero-ms-image-region-0.10.0_11.zip'
+    omero_ms_image_region_package_sha256: f45fb83cf55b4c87bb15b58a5c314ebd355d59cab9225d1bb598130d32fb86d9
 
   environment: "{{ idr_ANSIBLE_ENVIRONMENT_VARIABLES | default({}) }}"

```
