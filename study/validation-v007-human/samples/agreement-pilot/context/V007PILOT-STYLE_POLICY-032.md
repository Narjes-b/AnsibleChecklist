# Frozen source context: V007PILOT-STYLE_POLICY-032

- Repository: `mageops/ansible-infrastructure`
- Commit: `5c612ace8b03fdd369ce0dcdd5e74b638a35f6a8`
- Family: Style/policy
- Rule: `ansibleguard/variable-naming-convention`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `roles/cs.magento-shared-storage/defaults/main.yml` (reported anchor line 15)
- Object: `variable` `344fef6d27133247ddd4fbd100cd0c60334e09edb059be701f5d631a3a8e448b`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–57 of 57:

```text
    1 | # What to use for storing Magento media that must be shared across nodes
    2 | # Possible values:
    3 | #   - aws-s3 (default if `aws_use`) - store on AWS S3 media bucket and mount it via the selected S3 backend
    4 | #   - aws-efs - store on AWS EFS and mount it as NFS share on the node
    5 | #   - local-fs (default if not `aws_use`) - do nothing, just store the files on the local fs
    6 | # Note: If you set this to `aws-efs` then the media S3 bucket will not be created, but
    7 | # already existing buckets will not be removed.
    8 | # Someday: We may want to add plain NFS-based storage in the future to support non-AWS
    9 | # use cases or just allow using one of the persistent nodes for shared storage. As EFS is just
   10 | # plain NFS under the hood this should be relatively easy as most of the hard work is done.
   11 | magento_media_storage_strategy: local-fs
   12 | 
   13 | magento_s3_app_mounts_basic: []
   14 | 
   15 | magento_s3_app_mounts_media:
   16 |   - name: "Media"
   17 |     mountpoint: "{{ magento_media_dir }}"
   18 |     bucket: "{{ aws_s3_media_bucket }}"
   19 | 
   20 | magento_s3_app_mounts_extra: []
   21 | 
   22 | magento_efs_app_mounts_basic:
   23 |   - local_mountpoint: "{{ magento_efs_import_data_app_path }}"
   24 |     remote_path: "{{ magento_efs_import_data_remote_path }}"
   25 |     owner: "{{ magento_user }}"
   26 |     group: "{{ magento_group }}"
   27 |   - local_mountpoint: "{{ magento_efs_export_data_app_path }}"
   28 |     remote_path: "{{ magento_efs_export_data_remote_path }}"
   29 |     owner: "{{ magento_user }}"
   30 |     group: "{{ magento_group }}"
   31 |   - local_mountpoint: "{{ magento_efs_publicly_shared_app_path }}"
   32 |     remote_path: "{{ magento_efs_publicly_shared_remote_path }}"
   33 |     owner: "{{ magento_user }}"
   34 |     group: "{{ magento_group }}"
   35 |   - local_mountpoint: "{{ magento_static_cache_dir }}"
   36 |     remote_path: "{{ magento_efs_static_cache_release_remote_path }}"
   37 |     owner: "{{ magento_user }}"
   38 |     group: "{{ magento_group }}"
   39 |   - local_mountpoint: "{{ magento_efs_global_data_app_path }}"
   40 |     remote_path: "{{ magento_efs_global_data_remote_path }}"
   41 |     owner: "{{ magento_user }}"
   42 |     group: "{{ magento_group }}"
   43 | 
   44 | magento_efs_static_cache_release_remote_path: "{{ magento_efs_static_cache_releases_remote_path }}/{{ deploy_release_id }}"
   45 | 
   46 | magento_efs_app_mounts_media:
   47 |   - local_mountpoint: "{{ magento_media_dir }}"
   48 |     remote_path: "{{ magento_efs_media_remote_path }}"
   49 |     owner: "{{ magento_user }}"
   50 |     group: "{{ magento_group }}"
   51 | 
   52 | magento_efs_app_mounts_extra: []
   53 | 
   54 | # How many latest Magento static cache release dirs to keep (must be >=2)
   55 | # It weighs nothing so lets protect ourselves in case deploy starts failing
   56 | # or some strange stuff happens. Seven is the magic number ;)
   57 | magento_static_cache_releases_to_keep: 7
```
