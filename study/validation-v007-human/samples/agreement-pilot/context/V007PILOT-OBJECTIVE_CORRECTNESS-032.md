# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-032

- Repository: `theopenlab/openlab-zuul-jobs`
- Commit: `0d133dc0879296c0aacd0b70344515c94137a8ec`
- Family: Objective correctness
- Rule: `ansibleguard/non-idempotent-command`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `roles/upload-testgrid/tasks/main.yml` (reported anchor line 1)
- Object: `source_location` `659e4c60e44d29b434dc44b401dab25823e27ebd1a6d3768351e976059f20e9e`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–31 of 31:

```text
    1 | - name: Upload E2E test result to kubernetes testgrid
    2 |   environment: '{{ global_env }}'
    3 |   ignore_errors: yes  # the test run should not fail when upload doesnt work
    4 |   shell:
    5 |     executable: /bin/bash
    6 |     cmd: |
    7 |       set -ex
    8 | 
    9 |       # install gsutil, upload_e2e.py depends on it
   10 |       export CLOUD_SDK_REPO="cloud-sdk-$(lsb_release -c -s)"
   11 |       echo "deb http://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
   12 |       curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add
   13 |       apt-get update && sudo apt-get install google-cloud-sdk --yes
   14 |       apt-get install google-cloud-sdk-app-engine-java --yes
   15 | 
   16 |       # get upload_e2e.py
   17 |       wget https://raw.githubusercontent.com/kubernetes/test-infra/master/testgrid/conformance/upload_e2e.py
   18 | 
   19 |       # TODO(RuiChen): Add timestamp for e2e.log in order to workaround upload_e2e.py bug
   20 |       export LOG_DIR="{{ k8s_log_dir }}"
   21 |       date  +"%b %e %H:%M:%S.999: DONE" >> $LOG_DIR/e2e.log
   22 | 
   23 |       PIPELINE_LOGS_DIR='pr-logs'
   24 |       if [[ '{{ zuul.pipeline }}' =~ ^periodic ]]; then
   25 |           PIPELINE_LOGS_DIR='periodic-logs'
   26 |       fi
   27 | 
   28 |       # upload e2e log to new google storage bucket.
   29 |       python3.7 upload_e2e.py --junit=$LOG_DIR/junit*.xml --log=$LOG_DIR/e2e.log \
   30 |           --bucket=gs://{{ upload_testgrid_bucket_name }}/$PIPELINE_LOGS_DIR/ci-'{{ zuul.job }}' \
   31 |           --key-file='{{ upload_testgrid_key_file }}'
```
