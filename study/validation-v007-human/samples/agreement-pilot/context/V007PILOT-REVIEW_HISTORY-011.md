# Frozen Git review context: V007PILOT-REVIEW_HISTORY-011

- Repository: `cfpb/aurora`
- Target commit: `03e01e4bd080040159dd089175179ef3c6baa3e3`
- Actual first parent: `b63d613368d8aa4c4715797a2b85f4dc27da51d2`
- Evidence type: actual first-parent diff
- Family: Review/history
- Rule: `ansibleguard/missing-release-note`
- Codebook: `codebooks/FAMILY_REVIEW_HISTORY.md`
- Diff range: `b63d613368d8aa4c4715797a2b85f4dc27da51d2..03e01e4bd080040159dd089175179ef3c6baa3e3` (from frozen Git objects)
- No detector message or scan-time `base: null` fallback is used as review evidence.

## Exact target commit message

```text
Temporary hotfix
```

## Changed paths (1)

- `M` `deploy/roles/logstash/tasks/main.yml`

## Relevant first-parent diff

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
