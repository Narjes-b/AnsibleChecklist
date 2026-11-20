# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-029

- Repository: `theopenlab/openlab-zuul-jobs`
- Commit: `0d133dc0879296c0aacd0b70344515c94137a8ec`
- Family: Maintainability/complexity
- Rule: `ansibleguard/incomplete-task`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `playbooks/flink-end-to-end-test/e2e_cron_hadoop241_test.yaml` (reported anchor line 15)
- Object: `source_location` `df7fb12db889e67acae854d54d8ed31b4d3d1227df67d3f367194bd983caeb7d`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–38 of 38:

```text
    1 | - import_playbook: common.yaml
    2 | 
    3 | - hosts: all
    4 |   become: no
    5 |   tasks:
    6 |     - name: Build Flink
    7 |       shell:
    8 |         cmd: |
    9 |           mvn clean install -B -DskipTests -Dhadoop.version=2.8.3 -Dinclude_hadoop_aws -Dscala-2.11
   10 |       args:
   11 |         executable: /bin/bash
   12 |         chdir: '{{ zuul.project.src_dir }}'
   13 |       environment: '{{ global_env }}'
   14 | 
   15 |     - name: Hack - Use arm64 docker image
   16 |       shell:
   17 |          cmd: |
   18 |            # https://github.com/apache/flink-docker/pull/23
   19 |            sed -i 's/\/apache/\/wangxiyuan/' flink-end-to-end-tests/test-scripts/common_docker.sh
   20 |       args:
   21 |         executable: /bin/bash
   22 |         chdir: '{{ zuul.project.src_dir }}'
   23 |       environment: '{{ global_env }}'
   24 | 
   25 |     - name: Login SWR
   26 |       shell: docker login -u ap-southeast-3@{{ swr.ak }} -p {{ swr.sk }} swr.ap-southeast-3.myhuaweicloud.com
   27 |       no_log: yes
   28 | 
   29 |     - name: Run e2e test - openlab
   30 |       shell:
   31 |         cmd: |
   32 |           set -xo pipefail
   33 |           sudo iptables -P FORWARD ACCEPT
   34 |           PROFILE="-Dhadoop.version=2.8.3 -Dinclude_hadoop_aws -Dscala-2.11" FLINK_DIR=`pwd`/build-target ARTIFACTS_DIR=/home/zuul/ flink-end-to-end-tests/run-nightly-tests.sh
   35 |       args:
   36 |         executable: /bin/bash
   37 |         chdir: '{{ zuul.project.src_dir }}'
   38 |       environment: '{{ global_env }}'
```
