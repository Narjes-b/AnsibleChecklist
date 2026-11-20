# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-016

- Repository: `theopenlab/openlab-zuul-jobs`
- Commit: `0d133dc0879296c0aacd0b70344515c94137a8ec`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/unscoped-shell-variable`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `playbooks/flink-end-to-end-test/build_and_test_scheduler_ng_core_and_ng_tests.yaml` (reported anchor line 49)
- Object: `source_location` `6628fc25a805bef9c6b939bce4cdb9e5c00291409f0b37189c133b0655601a60`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–61 of 61:

```text
    1 | - import_playbook: common.yaml
    2 | 
    3 | # NOTE: Some tests should not be ran under root.
    4 | - hosts: all
    5 |   become: no
    6 |   tasks:
    7 |     - name: Build Flink scheduler_ng_core
    8 |       shell:
    9 |         cmd: |
   10 |           set -xe
   11 | 
   12 |           export PROFILE="-Dflink.forkCount=2 -Dflink.forkCountTestPackage=2 -Dfast -Pskip-webui-build -DskipTests -Dhadoop.version=2.8.3 -Dinclude_hadoop_aws -Dscala-2.11"
   13 |           source tools/ci/stage.sh
   14 | 
   15 |           mvn clean install -nsu -B -am $PROFILE -pl $MODULES_CORE
   16 |       args:
   17 |         executable: /bin/bash
   18 |         chdir: '{{ zuul.project.src_dir }}'
   19 |       environment: '{{ global_env }}'
   20 | 
   21 |     - name: Test Flink scheduler_ng_core
   22 |       shell:
   23 |         cmd: |
   24 |           set -xe
   25 | 
   26 |           export PROFILE="-Dflink.forkCount=2 -Dflink.forkCountTestPackage=2 -Dfast -Pskip-webui-build -Dflink.tests.with-openssl -Dhadoop.version=2.8.3 -Dinclude_hadoop_aws -Dscala-2.11 -Dlegacy-scheduler"
   27 |           source tools/ci/stage.sh
   28 | 
   29 |           mvn verify -nsu -B -fn $PROFILE -pl $MODULES_CORE
   30 |       args:
   31 |         executable: /bin/bash
   32 |         chdir: '{{ zuul.project.src_dir }}'
   33 |       environment: '{{ global_env }}'
   34 | 
   35 |     - name: Build Flink scheduler_ng_tests
   36 |       shell:
   37 |         cmd: |
   38 |           set -xe
   39 | 
   40 |           export PROFILE="-Dflink.forkCount=2 -Dflink.forkCountTestPackage=2 -Dfast -Pskip-webui-build -DskipTests -Dhadoop.version=2.8.3 -Dinclude_hadoop_aws -Dscala-2.11"
   41 |           source tools/ci/stage.sh
   42 | 
   43 |           mvn clean install -nsu -B -am $PROFILE -pl $MODULES_TESTS
   44 |       args:
   45 |         executable: /bin/bash
   46 |         chdir: '{{ zuul.project.src_dir }}'
   47 |       environment: '{{ global_env }}'
   48 | 
   49 |     - name: Test Flink scheduler_ng_tests
   50 |       shell:
   51 |         cmd: |
   52 |           set -xe
   53 | 
   54 |           export PROFILE="-Dflink.forkCount=2 -Dflink.forkCountTestPackage=2 -Dfast -Pskip-webui-build -Dflink.tests.with-openssl -Dhadoop.version=2.8.3 -Dinclude_hadoop_aws -Dscala-2.11 -Dlegacy-scheduler"
   55 |           source tools/ci/stage.sh
   56 | 
   57 |           mvn verify -nsu -B -fn $PROFILE -pl $MODULES_TESTS
   58 |       args:
   59 |         executable: /bin/bash
   60 |         chdir: '{{ zuul.project.src_dir }}'
   61 |       environment: '{{ global_env }}'
```
