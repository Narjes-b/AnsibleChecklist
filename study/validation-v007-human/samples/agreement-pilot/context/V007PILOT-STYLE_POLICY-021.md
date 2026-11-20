# Frozen source context: V007PILOT-STYLE_POLICY-021

- Repository: `ansible/galaxy-operator`
- Commit: `a05c8663b7e5cf4c2350fb1faa074a378b86f0fc`
- Family: Style/policy
- Rule: `ansibleguard/unnamed-task`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `config/scorecard/patches/olm.config.yaml` (reported anchor line 41)
- Object: `source_location` `e6747493e413bec67c4cadc690b728f497609942240ac60bf2fecbbecc845a65`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–50 of 50:

```text
    1 | - op: add
    2 |   path: /stages/0/tests/-
    3 |   value:
    4 |     entrypoint:
    5 |     - scorecard-test
    6 |     - olm-bundle-validation
    7 |     image: quay.io/operator-framework/scorecard-test:v1.23.0
    8 |     labels:
    9 |       suite: olm
   10 |       test: olm-bundle-validation-test
   11 | - op: add
   12 |   path: /stages/0/tests/-
   13 |   value:
   14 |     entrypoint:
   15 |     - scorecard-test
   16 |     - olm-crds-have-validation
   17 |     image: quay.io/operator-framework/scorecard-test:v1.23.0
   18 |     labels:
   19 |       suite: olm
   20 |       test: olm-crds-have-validation-test
   21 | - op: add
   22 |   path: /stages/0/tests/-
   23 |   value:
   24 |     entrypoint:
   25 |     - scorecard-test
   26 |     - olm-crds-have-resources
   27 |     image: quay.io/operator-framework/scorecard-test:v1.23.0
   28 |     labels:
   29 |       suite: olm
   30 |       test: olm-crds-have-resources-test
   31 | - op: add
   32 |   path: /stages/0/tests/-
   33 |   value:
   34 |     entrypoint:
   35 |     - scorecard-test
   36 |     - olm-spec-descriptors
   37 |     image: quay.io/operator-framework/scorecard-test:v1.23.0
   38 |     labels:
   39 |       suite: olm
   40 |       test: olm-spec-descriptors-test
   41 | - op: add
   42 |   path: /stages/0/tests/-
   43 |   value:
   44 |     entrypoint:
   45 |     - scorecard-test
   46 |     - olm-status-descriptors
   47 |     image: quay.io/operator-framework/scorecard-test:v1.23.0
   48 |     labels:
   49 |       suite: olm
   50 |       test: olm-status-descriptors-test
```
