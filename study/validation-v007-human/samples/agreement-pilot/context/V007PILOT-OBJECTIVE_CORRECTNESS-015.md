# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-015

- Repository: `theforeman/forklift`
- Commit: `ee24dec347fc0a785d22989fd1a183393fa4e054`
- Family: Objective correctness
- Rule: `ansibleguard/silent-error-suppression`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `roles/katello_client/tasks/cleanup.yml` (reported anchor line 12)
- Object: `source_location` `fcaba99b590188cea7383e635ccd03997f585d1041d1b4dd02951a0f28eff45d`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–24 of 24:

```text
    1 | ---
    2 | - name: 'Remove possibly faulty RHSM facts'
    3 |   file:
    4 |     name: /etc/rhsm/facts/katello.facts
    5 |     state: absent
    6 | 
    7 | - name: 'Install subscription-manager'
    8 |   yum:
    9 |     name: "subscription-manager"
   10 |     state: "present"
   11 | 
   12 | - name: 'Try to unregister from any old upstream'
   13 |   redhat_subscription:
   14 |     state: "absent"
   15 |   ignore_errors: True
   16 | 
   17 | - name: 'Clean old registrations'
   18 |   command: subscription-manager clean
   19 | 
   20 | - name: 'Remove old katello-ca-consumer RPM'
   21 |   yum:
   22 |     name: katello-ca-consumer-*
   23 |     state: absent
   24 |   ignore_errors: True
```
