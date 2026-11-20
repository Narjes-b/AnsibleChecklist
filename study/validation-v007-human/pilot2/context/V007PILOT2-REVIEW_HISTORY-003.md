# Frozen Git review context: V007PILOT2-REVIEW_HISTORY-003

- Repository: `cfpb/aurora`
- Target commit: `03e01e4bd080040159dd089175179ef3c6baa3e3`
- Actual first parent: `b63d613368d8aa4c4715797a2b85f4dc27da51d2`
- Evidence type: actual first-parent diff, all changed paths
- Family: review_history
- Rule: `ansibleguard/missing-test-update`
- Codebook: `codebooks-v2/FAMILY_REVIEW_HISTORY_V2.md`
- Author and committer identities are not part of the evidence and are not included.

## Exact target commit message

```text
Temporary hotfix
```

## Changed paths (1)

- `M` `deploy/roles/logstash/tasks/main.yml`

## First-parent diff (every changed path)

### `deploy/roles/logstash/tasks/main.yml`
```diff
diff --git a/deploy/roles/logstash/tasks/main.yml b/deploy/roles/logstash/tasks/main.yml
index 2c7e83e..7142f7b 100644
--- a/deploy/roles/logstash/tasks/main.yml
+++ b/deploy/roles/logstash/tasks/main.yml
@@ -32,10 +32,11 @@
 
 - name: Install logstash-output-elasticsearch plugin
   shell: 'su logstash -c "/opt/logstash/bin/logstash-plugin install logstash-output-elasticsearch"'
   notify:
     - restart logstash
+  ignore_errors: yes
 
 - name: Remove sgroups because it doesn't work with Active Directory
   lineinfile:
     dest: /etc/init.d/logstash
     line: >
```

