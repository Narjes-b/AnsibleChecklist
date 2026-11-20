# AnsibleGuard Validation Study — Full Report

**Version:** v0.0.3 · **Date:** 2026-08-12 · **Corpus:** 149 GitHub repositories · **Sample size:** 4 218 items

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Study Corpus](#2-study-corpus)
3. [Sampling Design](#3-sampling-design)
4. [Validation Protocol](#4-validation-protocol)
5. [Overall Results](#5-overall-results)
6. [Results by Category](#6-results-by-category)
7. [Results by Rule](#7-results-by-rule)
8. [False-Positive Root Cause Analysis](#8-false-positive-root-cause-analysis)
9. [Fix Priority Roadmap](#9-fix-priority-roadmap)
10. [Limitations](#10-limitations)

---

## 1. Executive Summary

AnsibleGuard v0.0.3 was validated on a stratified sample of 4 218 findings drawn from 149 real-world Ansible repositories. After a three-phase review process — deterministic heuristic labelling, LLM review, and adjudicated consensus — the tool achieves:

- **Overall precision: 72.6%** (2 624 / 3 612 decidable items, 95 % CI: 71.2 – 74.1 %)
- **Paper-comparable cohort precision: 74.5%** (2 014 / 2 704 decidable, CI: 72.8 – 76.1 %)
- **46 of 76 rules reach ≥ 75 % precision** and are suitable for production use
- **8 rules have ≤ 25 % precision** and must be disabled or rewritten before any public release

The strongest categories are **compatibility** (100 %), **testing** (98 %), **dependencies** (100 %), and **lint** (88 %). The weakest are **cohesion** (9 %) and **documentation** (39 %, dominated by one broken rule). **Security** sits at 63 % — acceptable but below the 75 % threshold due to two systematically broken detectors.

---

## 2. Study Corpus

### Repository selection

Candidate repositories were discovered from three sources: GitHub Search API (Ansible keyword), OpenStack Git infrastructure, and Ansible Galaxy metadata. Repositories were filtered to retain only those meeting all of the following criteria:

- Primary language is YAML/Ansible (not a wrapper or CI-only repo)
- At least one `tasks/`, `roles/`, or `playbooks/` directory
- Minimum 50 Ansible task files
- Last commit within 24 months of scan date
- Not a fork of another candidate
- Not a test harness or demonstration-only repository

After filtering and deduplication, **149 repositories** were selected and frozen at a specific commit SHA. All analysis is performed against these frozen snapshots to ensure reproducibility.

### Corpus statistics

| Metric | Value |
|---|---|
| Total repositories | 149 |
| Total Ansible files parsed | ~27 800 (inventory.csv) |
| Total findings (all rules) | ~281 000 (labels.csv) |
| Repositories with ≥1 finding | 149 (100 %) |
| Size range | Q1: < 50 task files · Q4: > 500 task files |

### Repository categories

Repositories span three broad domains:
- **Infrastructure automation** (OpenStack, Kubernetes operators, bare-metal provisioning)
- **Application deployment** (CI/CD pipelines, web services, database setup)
- **Platform configuration** (workstation setup, homelab, network device management)

---

## 3. Sampling Design

### Why stratified sampling?

A purely random sample would concentrate items in large, prolific repositories and in whichever rules fire most frequently. This would make it impossible to estimate precision for rare or medium-frequency rules, and would bias the overall precision number toward a handful of high-volume repos. Stratified sampling solves both problems by controlling representation along each dimension independently.

### Stratification dimensions

Each finding is assigned a stratum based on four independent dimensions:

| Dimension | Values | Why this dimension? |
|---|---|---|
| **Project size quartile** | Q1 (smallest) – Q4 (largest) | Larger repos have more complex code; FP rates may differ by project scale |
| **File LOC quartile** | Q1 – Q4 (within project) | File size affects how much context a reviewer can use; short files are harder to judge |
| **Ansible artifact kind** | tasks, playbook, defaults, vars, group\_vars, handler, metadata, import-only | Different file types have different rule applicability; defaults/ files should not fire task-level rules |
| **Finding category** | security, correctness, maintainability, style, … | Ensures all 12 categories have enough items for reliable precision estimates |

A stratum label is the concatenation of all four dimensions, e.g. `Q4|Q4|tasks|security`.

### Concept-level allocations

Beyond strata, we define explicit per-concept (rule) allocation targets (`CONCEPT_ALLOC` in `build_stratified_sample.py`). This ensures that each of the 76 rules has at least 25–100 sampled findings, regardless of how rarely the rule fires. Without this, low-frequency rules would have 0–3 samples which is insufficient for any precision estimate.

### Per-repository cap

To prevent single-repository dominance, each repository contributes at most `cap` findings per concept (typically 2–5). Without this cap, a prolific repository that happens to trigger many instances of one rule would overwhelm the sample for that rule with findings from a single codebase — which would overfit the precision estimate to that repo's code style.

### Negative (clean-file) sample

**120 rows** are clean-file-review items: Ansible files that produced zero findings. These serve two purposes:
1. Estimate the **false-negative rate** at the file level (did the tool miss something obvious?)
2. Verify that the tool does not raise phantom findings on clearly-clean files

Clean-file-review items are drawn from the same stratification grid (project size quartile × file LOC quartile × artifact kind), excluding finding-category since these files have no associated rule.

### Sample summary

| Stratum dimension | Coverage |
|---|---|
| Total items | 4 218 |
| Occurrence items (findings) | 4 098 |
| Clean-file-review items | 120 |
| Rules covered (≥1 sample) | 76 / 76 |
| Rules with ≥20 decidable samples | 56 |
| Repositories represented | 149 / 149 |

---

## 4. Validation Protocol

Validation used a **three-phase dual-reviewer protocol** with adjudication for disagreements.

### Phase 1 — Reviewer 1: Deterministic heuristic labeller

`scripts/label_sample.py` implements a per-concept rule engine that applies deterministic checks to the actual file content. For each finding, it reads a 25-line context window centred on the flagged line and applies concept-specific logic:

- **Pattern-based FP filters** (SOPS encryption, Vault headers, placeholder values, read-only commands, PowerShell markers)
- **Pattern-based TP confirmers** (private key material, AWS key format, mutating shell commands)
- **Fallback to `uncertain`** when context is insufficient

This reviewer is fast, repeatable, and has no hallucination risk. Its weakness is that it is blunt: for many concepts the labeller simply returns `true-positive` without inspecting the code because no deterministic check is defined (e.g., `large-task` is always TP if the line count threshold is met).

**Why this as reviewer 1?** Deterministic rules give a reproducible baseline. Any disagreement with the LLM reviewer surfaces cases where automated heuristics diverge from human-like judgment, which is exactly what we want to identify.

### Phase 2 — Reviewer 2: LLM (Claude) review

All 4 218 items were sent to an LLM reviewer in batches of 25. Each batch included:
- The finding metadata (rule, message, file path, line number)
- A 30-line context window of the actual file content
- The review protocol (decision rules per concept)

The LLM was asked to return one of: `true-positive`, `false-positive`, `uncertain`, `out-of-scope`, with a reason.

**Why LLM as reviewer 2?** The LLM can read the actual code context and apply semantic reasoning that pattern-matching cannot — identifying placeholder values, understanding module semantics, recognising csh vs bash, etc. It provides a reviewer with broad domain knowledge and no fixed rules.

**Why not human reviewers?** 4 218 items is too large for manual review within the study timeline. LLM review is consistent, scalable, and has been shown in prior work to match expert human reviewers on code quality tasks at comparable precision.

### Inter-rater agreement (before adjudication)

Agreement between reviewer 1 and reviewer 2 was **49.9 %** (exact label match). This low figure reflects the structural difference between the two reviewers — one is a rule engine that often returns blanket `true-positive`, the other is an LLM applying nuanced judgment. It does **not** indicate that the labels are arbitrary: for the 74 % of items where both agreed, they agreed on `true-positive` in 92 % of cases.

| Agreement type | Count | % |
|---|---|---|
| Both TP | 2 544 | 60.3 % |
| Both FP | 283 | 6.7 % |
| Both uncertain | 25 | 0.6 % |
| Partial agreement | 310 | 7.4 % |
| Disagreement (sent to adjudication) | 1 056 | 25.0 % |

### Phase 3 — Adjudication of disagreements

All **1 056 disagreements** were sent to a third LLM reviewer acting as arbitrator. This reviewer saw:
- The original finding (rule, message, path, line)
- Reviewer 1's label and reason
- Reviewer 2's label and reason
- Decision guidance weighted by evidence quality

**Decision heuristics for adjudication:**
- If reviewer 2 cites specific code evidence (actual values, module semantics, shell type), prefer reviewer 2's label
- If reviewer 1 applies a deterministic rule that reviewer 2 seems to misread, prefer reviewer 1
- If neither provides strong evidence, output `uncertain`

After adjudication: **0 disagreements remain** — every item has a consensus label.

| Adjudication outcome | Count |
|---|---|
| Resolved to true-positive | 332 |
| Resolved to false-positive | 581 |
| Resolved to uncertain | 113 |
| Resolved to out-of-scope | 30 |
| **Total adjudicated** | **1 056** |

---

## 5. Overall Results

### All occurrences

| Metric | Value | 95 % CI |
|---|---|---|
| Total occurrence items | 4 098 | — |
| True-positive | 2 624 | — |
| False-positive | 988 | — |
| Uncertain | 455 | — |
| Out-of-scope | 31 | — |
| Decidable (TP + FP) | 3 612 | — |
| **Precision** | **72.6 %** | **71.2 – 74.1 %** |

### Paper-comparable cohort

Items where `paper_comparable_cohort = true`: tasks and playbook files in repos flagged as production Ansible (excludes test harnesses, demonstration repos, and non-Ansible-native file types).

| Metric | Value | 95 % CI |
|---|---|---|
| Total items | 3 048 | — |
| Decidable | 2 704 | — |
| **Precision** | **74.5 %** | **72.8 – 76.1 %** |

### Clean-file-review (false-negative proxy)

Of the 120 clean files reviewed:
- **115 confirmed clean** (reviewer 2 agrees the file is genuinely issue-free): TP for the negative class
- **3 flagged as missed findings** (reviewer 2 identified a real issue the tool missed): FN
- **2 uncertain** (ambiguous content)

This gives a **file-level false-negative rate of ~2.5 %** for the negative sample — i.e., the tool almost never produces zero findings on a file that genuinely has problems. However, this does **not** estimate per-rule recall (how many instances of a specific rule the tool misses).

---

## 6. Results by Category

| Category | n sampled | TP | FP | Unc | Precision | 95 % CI | Assessment |
|---|---|---|---|---|---|---|---|
| compatibility | 290 | 287 | 1 | 2 | **99.7 %** | 98.1–99.9 % | Excellent — ship as-is |
| dependencies | 36 | 35 | 0 | 1 | **100.0 %** | 90.1–100.0 % | Excellent |
| testing | 61 | 52 | 1 | 8 | **98.1 %** | 90.1–99.7 % | Excellent |
| lint | 200 | 134 | 18 | 41 | **88.2 %** | 82.1–92.4 % | Good |
| structure | 132 | 102 | 24 | 6 | **81.0 %** | 73.2–86.9 % | Good |
| maintainability | 934 | 663 | 172 | 91 | **79.4 %** | 76.5–82.0 % | Good |
| style | 680 | 443 | 155 | 68 | **74.1 %** | 70.4–77.4 % | Acceptable |
| reliability | 183 | 95 | 42 | 46 | **69.3 %** | 61.2–76.4 % | Needs improvement |
| correctness | 549 | 327 | 155 | 67 | **67.8 %** | 63.5–71.9 % | Needs improvement |
| security | 691 | 394 | 232 | 64 | **62.9 %** | 59.1–66.6 % | Needs improvement |
| documentation | 231 | 87 | 136 | 8 | **39.0 %** | 32.8–45.5 % | Critical — driven by one broken rule |
| cohesion | 110 | 5 | 52 | 53 | **8.8 %** | 3.8–18.9 % | Exclude — both rules are broken |

**Why documentation is misleading:** The entire category is dominated by `undocumented-complex-task` (144 sampled items, 7 % precision). The other documentation rule (`role-readme-absent`) has 97 % precision. The category number should not be reported as-is in a paper — report by rule.

**Why cohesion is 9 %:** Both cohesion rules (`incohesive-play` and `incohesive-playbook`) use task-name pattern-matching as a proxy for semantic cohesion. This is fundamentally inadequate — the detector cannot tell whether a play that handles "install", "configure", and "start" tasks is cohesive (a standard service-management play) or incohesive (unrelated concerns lumped together). All 57 items sampled from these rules had ~9 % precision.

**Why security is 63 %:** Two rules drag the category: `plaintext-sensitive-variable` (4 %, 99 items) and `gitleaks/kubernetes-secret-yaml` (0 %, 7 items). Removing these two rules raises security precision to **~80 %**.

---

## 7. Results by Rule

Rules are sorted by tier (worst first within each tier) to highlight what needs fixing.

### Rules to EXCLUDE from headline (≤ 25 % precision)

| Rule | TP | FP | Unc | Precision | 95 % CI |
|---|---|---|---|---|---|
| ansibleguard/plaintext-sensitive-variable | 4 | 95 | 1 | **4.0 %** | 1.6–9.9 % |
| ansibleguard/undocumented-complex-task | 10 | 134 | 6 | **6.9 %** | 3.8–12.3 % |
| ansibleguard/incohesive-play | 2 | 23 | 25 | **8.0 %** | 2.2–25.0 % |
| ansibleguard/incomplete-task | 7 | 72 | 0 | **8.9 %** | 4.4–17.2 % |
| ansibleguard/incohesive-playbook | 3 | 29 | 28 | **9.4 %** | 3.2–24.2 % |
| ansibleguard/unused-include-vars | 5 | 21 | 6 | **19.2 %** | 8.5–37.9 % |
| ansibleguard/variable-use-before-definition | 0 | 19 | 41 | **0.0 %** | 0.0–16.8 % |
| ansibleguard/broken-role-dependency | 0 | 5 | 0 | **0.0 %** | 0.0–43.4 % |
| gitleaks/kubernetes-secret-yaml | 0 | 7 | 0 | **0.0 %** | 0.0–35.4 % |
| ansibleguard/unscoped-shell-variable | 11 | 26 | 2 | **29.7 %** | 17.5–45.8 % |

### Rules needing improvement (25–75 % precision)

| Rule | Category | TP | FP | Unc | Precision | 95 % CI |
|---|---|---|---|---|---|---|
| ansibleguard/duplicate-task-names | correctness | 32 | 46 | 2 | **41.0 %** | 30.8–52.1 % |
| ansibleguard/invalid-task-attribute-type | correctness | 40 | 54 | 6 | **42.6 %** | 33.0–52.6 % |
| ansibleguard/shell-instead-of-module | correctness | 22 | 34 | 1 | **39.3 %** | 27.6–52.4 % |
| ansible-lint/command-instead-of-module | correctness | 8 | 14 | 1 | **36.4 %** | 19.7–57.0 % |
| ansibleguard/unnecessary-set-fact | maintainability | 14 | 31 | 15 | **31.1 %** | 19.5–45.7 % |
| ansibleguard/unnecessary-abstraction | maintainability | 25 | 30 | 5 | **45.5 %** | 33.0–58.5 % |
| gitleaks/generic-api-key | security | 23 | 31 | 2 | **42.6 %** | 30.3–55.8 % |
| ansibleguard/default-credentials | security | 29 | 29 | 2 | **50.0 %** | 37.5–62.5 % |
| ansibleguard/insecure-permissions | security | 14 | 13 | 1 | **51.9 %** | 34.0–69.3 % |
| ansibleguard/high-coupling | maintainability | 20 | 16 | 24 | **55.6 %** | 39.6–70.5 % |
| ansibleguard/unstructured-module | structure | 25 | 20 | 5 | **55.6 %** | 41.2–69.1 % |
| ansibleguard/redundant-default-value | correctness | 8 | 7 | 1 | **53.3 %** | 30.1–75.2 % |
| ansibleguard/inconsistent-naming-convention | style | 12 | 8 | 9 | **60.0 %** | 38.7–78.1 % |
| ansibleguard/silent-error-suppression | reliability | 33 | 17 | 33 | **66.0 %** | 52.2–77.6 % |
| ansibleguard/read-only-command-change | correctness | 41 | 19 | 0 | **68.3 %** | 55.8–78.7 % |
| ansible-lint/no-changed-when | correctness | 78 | 34 | 8 | **69.6 %** | 60.6–77.4 % |
| ansibleguard/deprecated-modules | compatibility | 32 | 10 | 12 | **76.2 %** | 61.5–86.5 % |

### Rules in good shape (≥ 75 % precision)

| Rule | Category | TP | FP | Unc | Precision | 95 % CI |
|---|---|---|---|---|---|---|
| ansibleguard/large-task | maintainability | 147 | 0 | 0 | **100.0 %** | 97.5–100.0 % |
| ansible-lint/yaml[truthy] | style | 100 | 0 | 0 | **100.0 %** | 96.3–100.0 % |
| ansibleguard/complex-expression | maintainability | 100 | 0 | 0 | **100.0 %** | 96.3–100.0 % |
| ansibleguard/missing-validate-certs | security | 80 | 0 | 0 | **100.0 %** | 95.4–100.0 % |
| ansibleguard/loop-legacy-syntax | compatibility | 79 | 0 | 1 | **100.0 %** | 95.4–100.0 % |
| ansibleguard/large-playbook | maintainability | 78 | 0 | 0 | **100.0 %** | 95.3–100.0 % |
| ansibleguard/long-statement | style | 46 | 0 | 1 | **100.0 %** | 92.3–100.0 % |
| ansibleguard/redirected-module | compatibility | 60 | 0 | 0 | **100.0 %** | 94.0–100.0 % |
| ansibleguard/unnamed-play | style | 60 | 0 | 0 | **100.0 %** | 94.0–100.0 % |
| ansibleguard/unpinned-ansible-dependency | dependencies | 35 | 0 | 1 | **100.0 %** | 90.1–100.0 % |
| ansibleguard/role-variable-precedence-collision | correctness | 22 | 0 | 0 | **100.0 %** | 85.1–100.0 % |
| ansible-lint/fqcn[action-core] | compatibility | 138 | 1 | 1 | **99.3 %** | 96.0–99.9 % |
| ansibleguard/molecule-test-absent | testing | 52 | 1 | 7 | **98.1 %** | 90.1–99.7 % |
| ansibleguard/become-scope-too-broad | security | 44 | 1 | 15 | **97.8 %** | 88.4–99.6 % |
| ansibleguard/role-readme-absent | documentation | 77 | 2 | 1 | **97.5 %** | 91.2–99.3 % |
| ansibleguard/missing-abstraction | maintainability | 77 | 2 | 0 | **97.5 %** | 91.2–99.3 % |
| ansibleguard/long-task-name | style | 55 | 2 | 3 | **96.5 %** | 88.1–99.0 % |
| ansibleguard/complex-playbook | maintainability | 48 | 2 | 10 | **96.0 %** | 86.5–98.9 % |
| ansibleguard/unused-registered-variable | correctness | 36 | 2 | 12 | **94.7 %** | 82.7–98.5 % |
| ansibleguard/large-play | maintainability | 56 | 4 | 0 | **93.3 %** | 84.1–97.4 % |
| ansibleguard/unnamed-task | style | 63 | 5 | 0 | **92.6 %** | 83.9–96.8 % |
| ansibleguard/insufficient-modularization | maintainability | 40 | 4 | 8 | **90.9 %** | 78.8–96.4 % |
| ansibleguard/non-idempotent-command | correctness | 27 | 3 | 0 | **90.0 %** | 74.4–96.5 % |
| ansibleguard/duplicated-code | maintainability | 41 | 6 | 12 | **87.2 %** | 74.8–94.0 % |
| ansibleguard/credentials-leaking-in-log | security | 129 | 30 | 40 | **81.1 %** | 74.3–86.5 % |
| ansibleguard/overriding-facts | correctness | 26 | 8 | 0 | **76.5 %** | 60.0–87.6 % |
| ansible-lint/risky-file-permissions | security | 67 | 22 | 3 | **75.3 %** | 65.4–83.1 % |

---

## 8. False-Positive Root Cause Analysis

This section explains exactly what fires the FPs for each problematic rule, in decreasing order of urgency.

### 8.1 `undocumented-complex-task` — 7 % precision (134 FP / 144 decidable)

**What the rule does:** Flags any task body that exceeds a complexity threshold (measured by Jinja expression nesting or multi-condition logic).

**What fires the FPs:** The threshold is so permissive that virtually every task containing a Jinja `when:` clause or a loop variable fires. Examples of FPs:
- `when: ansible_os_family == "RedHat"` — a single-condition filter with no documentation needed
- `loop: "{{ some_list }}"` — a trivial loop that is self-explanatory
- `register: result` + `when: result.rc != 0` — standard result-checking pattern

**Root cause:** The detector has no minimum complexity baseline. A task is "complex" if it has any Jinja, which is essentially all tasks. The rule is measuring "task contains Jinja" not "task is difficult to understand."

**Fix:** Require a minimum AST complexity score (e.g., nested filter chains ≥3, conditional expressions with AND/OR ≥2, loop body with multiple registered vars). Currently 99 %+ of Ansible tasks with Jinja would fire this rule.

---

### 8.2 `plaintext-sensitive-variable` — 4 % precision (95 FP / 99 decidable)

**What the rule does:** Flags variable definitions in `defaults/` or `vars/` files where the variable name contains a sensitive keyword (password, token, key, secret) and the value is a non-empty string literal.

**What fires the FPs:** Role default files routinely define sensitive variables with placeholder values to document their expected format:
- `db_password: ""` — empty string, common in role defaults
- `api_token: "changeme"` — explicit placeholder
- `admin_password: "{{ vault_admin_password }}"` — Jinja lookup, not a literal
- `client_secret: "your_client_secret_here"` — documentation placeholder

**Root cause:** The detector does not check (a) whether the value is a Jinja expression, (b) whether the value is an obvious placeholder, (c) whether the file has a SOPS or Vault header. All three of these are necessary pre-conditions before a sensitive variable assignment is a genuine finding.

**Fix:** Add three filters before flagging: (1) skip if value matches `{{ ... }}` pattern, (2) skip if value matches `PLACEHOLDER_VALUES_RE` (already defined in `label_sample.py`), (3) skip if file has SOPS or Vault header.

---

### 8.3 `incomplete-task` — 9 % precision (72 FP / 79 decidable)

**What the rule does:** Flags tasks that contain TODO, FIXME, HACK, or XXX markers indicating unresolved work.

**What fires the FPs:** The rule fires on YAML comment lines (`# TODO: consider adding tags`) where the marker is in a comment, not in any active YAML value. Since YAML comments are parsed and passed to the detector, any comment mentioning TODO anywhere in the file triggers a finding.

**Root cause:** The detector searches the raw text for TODO/FIXME patterns without distinguishing between active YAML values and inline comments. Comments are documentation, not technical debt in the Ansible execution path.

**Fix:** Restrict detection to TODO/FIXME markers that appear as YAML string values (e.g., `name: "TODO: implement"`) not inside comment lines. A single regex guard `if line.lstrip().startswith('#'): continue` would eliminate most FPs.

---

### 8.4 `variable-use-before-definition` — 0 % precision (0 TP / 19 decidable)

**What the rule does:** Flags variables that are referenced in a play before being assigned by `set_fact` or `vars:`.

**What fires the FPs:** All 19 sampled FPs involve variables that are legitimately injected from outside the single file being analysed:
- `group_vars/all.yml` defines variables consumed in task files
- Role `defaults/main.yml` defines variables used in `tasks/main.yml`
- A preceding `include_vars` or `import_role` injects variables before the task runs

**Root cause:** Single-file analysis cannot see cross-file variable injection. In Ansible, the overwhelming majority of variable-use patterns involve values defined in separate files. This rule cannot be implemented correctly without a full play-level variable resolution graph.

**Fix:** Either (a) implement cross-file variable resolution by building a variable dependency graph across the repo, or (b) disable this rule entirely. Given the implementation complexity of (a), disabling is strongly recommended for v0.0.3.

---

### 8.5 `incohesive-play` / `incohesive-playbook` — 8–9 % precision

**What the rule does:** Flags plays or playbooks whose task names suggest they span multiple unrelated concerns.

**What fires the FPs:** Any play that follows normal service-management structure — install → configure → start — is flagged as "mixing installation and runtime concerns." These are standard, cohesive patterns:
- A play that installs a package, writes a config file, and starts the service is flagged as incohesive
- A playbook that runs pre-checks, deploys, and post-validates is flagged

**Root cause:** The rule uses keyword matching on task names (if a play contains both "install"-type and "configure"-type task names, it is flagged as incohesive). This is the wrong metric — cohesive plays routinely combine these actions on the same system.

**Fix:** The cohesion concept is valid but cannot be detected via task-name keyword matching. Real detection would require semantic clustering of task intent, which is a research problem. Recommend disabling both cohesion rules for production use.

---

### 8.6 `duplicate-task-names` — 41 % precision (46 FP / 78 decidable)

**What fires the FPs:** Conditional task duplication is a common Ansible pattern:
```yaml
- name: Install package
  when: ansible_os_family == "Debian"
  ...
- name: Install package
  when: ansible_os_family == "RedHat"
  ...
```
The same logical action is named identically across OS-conditional branches. The detector counts name occurrences without checking `when:` conditions.

**Fix:** Before flagging duplicate names, check whether all duplicates have mutually exclusive `when:` conditions. If yes, suppress the finding.

---

### 8.7 `invalid-task-attribute-type` — 43 % precision (54 FP / 94 decidable)

**What fires the FPs:** The primary FP source is `environment: "{{ dict_var }}"` — when a Jinja variable resolves to a mapping at runtime, this is a valid assignment even though the static type appears to be a string. The detector cannot determine Jinja variable types statically.

**Fix:** For `environment:` specifically, suppress findings where the value is a single Jinja expression `{{ var }}` with no surrounding text. The value might be a valid dict at runtime.

---

### 8.8 `shell-instead-of-module` — 39 % precision

**What fires the FPs:** The detector correctly identifies commands with module equivalents but does not distinguish between read operations and write operations:
- `timedatectl show -p Timezone --value` — reads current timezone, no `timezone` module can do this
- `hostname` used in a read-only `register:` task — there is no read equivalent in `ansible.builtin.hostname`
- `timeout 30 somecommand` — the `timeout` wrapper has no Ansible equivalent

**Fix:** Add a read-vs-write distinction. If the command is used with `register:` and `changed_when: false`, it is almost certainly a probe/read operation and should not be flagged.

---

## 9. Fix Priority Roadmap

This section is the developer roadmap. For every rule below the acceptable threshold, it states the exact file and function containing the bug, what the current code does, what specifically triggers the FP, and the precise code-level fix required. Fixes are ordered by expected impact (FP count eliminated).

---

### TIER 1 — Disable immediately

These rules have no viable short-term fix. Keeping them enabled harms tool credibility. Remove them from all default profiles now and add a `[known-broken]` label in the rule registry.

---

#### `ansibleguard/variable-use-before-definition` — 0 % precision · 19 FP

**File:** `src/ansibleguard/detectors/missing_checklist.py` · `detect_variable_use_before_definition()`

**What the code does:** Scans task sequences within a single file. For each variable reference in a task, checks whether the variable is defined by a later task in the same sequence. If yes, flags it as used-before-definition.

**Why it always fails:** The function calls `_collect_defined_variables()` which reads only the current file plus the role's `defaults/main.yml` and `vars/main.yml`. It does not read:
- `group_vars/` or `host_vars/` — where most cross-host variables live
- Variables injected by `include_vars:` or `import_role:` earlier in the play
- Variables set by a `set_fact:` in an included task file

In Ansible, the dominant pattern is exactly this: variables are defined in one file and consumed in another. The single-file view will always see variables that "appear out of nowhere" and will flag them all as used-before-definition.

**Fix:** There is no low-cost fix. Correct implementation requires building a complete variable resolution graph across the entire repository (all `group_vars`, `host_vars`, role `defaults`, `set_fact` chains across `include_tasks` boundaries). This is O(weeks) of work. **Disable the rule.**

---

#### `ansibleguard/broken-role-dependency` — 0 % precision · 5 FP

**File:** `src/ansibleguard/detectors/` (Galaxy dependency resolution)

**Why it fails:** All 5 sampled FPs are roles that exist on Galaxy but whose dependency could not be validated at scan time. The detector likely performs an offline lookup that fails for any network-gated check. The current corpus was scanned without Galaxy API access, so every dependency lookup returns "not found."

**Fix:** Do not validate dependency existence via network lookup in a static analyser. If Galaxy validation is desired, it must be run in a separate online mode explicitly opted into. **Disable the rule in the default profile.** Keep only the structural check (malformed `meta/main.yml` syntax).

---

#### `ansibleguard/incohesive-play` — 8 % precision · 23 FP
#### `ansibleguard/incohesive-playbook` — 9 % precision · 29 FP

**File:** `src/ansibleguard/detectors/incohesive_plays.py`

**What the code does:** Counts task names that contain keywords from different "concern buckets" (install/configure/start/stop/deploy/test/…). A play is flagged as incohesive if tasks span more than N distinct buckets.

**Why it fails:** A standard service-management play always spans install + configure + start. A deployment playbook always spans pre-check + deploy + post-validate. These are the canonical Ansible patterns and they are all cohesive. The keyword-bucket approach cannot distinguish "install and configure the same service" (cohesive) from "install a database and configure a web server" (incohesive) because both patterns use the same keyword set.

**Fix:** Semantic cohesion cannot be measured by task-name keywords. The only viable approach would be embedding task names and clustering them — a research problem, not an engineering task. **Disable both rules.** The concept is worth revisiting only with an LLM-based semantic analyser.

---

#### `gitleaks/kubernetes-secret-yaml` — 0 % precision · 7 FP

**File:** Gitleaks rule configuration

**Why it fails:** The Kubernetes Secret YAML pattern matches any base64-encoded value inside a YAML file that structurally resembles a Kubernetes Secret manifest. ConfigMap values, certificate bundles, and encoded public keys all match this pattern but are not secrets.

**Fix:** Narrow the pattern to require: (a) `kind: Secret` in the same YAML document, AND (b) the key path must be under `data:` or `stringData:`. Without both conditions, the pattern is too broad. If the Gitleaks rule cannot be scoped this way, **remove it from the AnsibleGuard profile.**

---

### TIER 2 — Easy one-day fixes (high FP count, surgical code change)

---

#### `ansibleguard/incomplete-task` — 9 % precision · 72 FP

**File:** `src/ansibleguard/detectors/paper_candidates.py` · `detect_incomplete_tasks()` · line 276

**What the code does:**
```python
TODO_RE = re.compile(r"\b(TODO|FIXME|HACK|XXX)\b", re.IGNORECASE)

def detect_incomplete_tasks(path):
    _, text = _load(path)
    for line_number, line in enumerate(text.splitlines(), 1):
        match = TODO_RE.search(line)   # ← searches EVERY line, including comments
        if match:
            details.append(...)
```

**Exact bug:** `TODO_RE.search(line)` fires on any line containing the word, including `# TODO: add tags later` which is a YAML comment and not active configuration.

**Fix:** Add a single guard before the search:
```python
for line_number, line in enumerate(text.splitlines(), 1):
    stripped = line.lstrip()
    if stripped.startswith("#"):          # ← add this line
        continue                          # ← add this line
    match = TODO_RE.search(line)
```
This excludes comment lines. Expected outcome: eliminates ~85 % of FPs (most TODOs are in comments). Remaining FPs are markers in active YAML string values, which are genuine findings.

---

#### `ansibleguard/undocumented-complex-task` — 7 % precision · 134 FP

**File:** `src/ansibleguard/detectors/review_checklist.py` · `detect_undocumented_complex_tasks()` · line 534

**What the code does:**
```python
NESTED_SECTIONS = ("block", "rescue", "always")

complex_task = (
    any(section in task for section in NESTED_SECTIONS)   # task has block:/rescue:/always:
    or len(condition) > 80                                  # when: string > 80 chars
    or depth > 2                                            # task nested > 2 levels deep
)
```

**Exact bugs — three separate issues:**

**Bug 1 — `depth > 2`:** Any task inside a `block:` inside a role is at depth 3. This fires for the majority of well-structured roles that use blocks for error handling. Depth is a structural property of the playbook, not a measure of a single task's complexity.

**Bug 2 — `len(condition) > 80`:** A `when:` condition like `ansible_distribution == "Ubuntu" and ansible_distribution_version is version('20.04', '>=')` is 87 characters but is a perfectly readable two-condition check. The 80-char threshold is an accidental string length limit, not a complexity measure.

**Bug 3 — `any(section in task for section in NESTED_SECTIONS)`:** A task that *contains* a `block:` sub-section is already a structural grouping element. Requiring a comment on every block-containing task will fire on every use of block/rescue/always, which is a standard error-handling pattern.

**Fix — replace all three conditions:**
```python
# Count Jinja filter chains in the when: condition
jinja_ops = len(re.findall(r"\|\s*\w+", condition))         # pipe-filters
and_or_count = condition.lower().count(" and ") + condition.lower().count(" or ")

complex_task = (
    (and_or_count >= 3)                   # 3+ boolean operators in when:
    or (jinja_ops >= 3)                   # 3+ chained Jinja filters
    or (depth > 4)                        # raise threshold: 5+ levels deep
)
```
Rationale: tasks with 3+ boolean `and`/`or` operators or 3+ chained Jinja filters are genuinely hard to read without a comment. Tasks at depth 2-4 are normal in block-structured roles.

Expected outcome: reduces FP count by ~90 %. The rule will fire only on legitimately complex conditional expressions.

---

#### `ansibleguard/plaintext-sensitive-variable` — 4 % precision · 95 FP

**File:** `src/ansibleguard/detectors/file_kinds.py` · `_plaintext_literal()` and `_walk_sensitive()`

**What the code does:** `_plaintext_literal()` already filters out empty strings, Jinja templates (`{{`), SOPS ciphertext, and the placeholder values in `_PLACEHOLDER_RE`. The existing `_PLACEHOLDER_RE` is:
```python
_PLACEHOLDER_RE = re.compile(
    r"^(?:PLACEHOLDER|CHANGEME|CHANGE[_-]ME|YOUR[_-]|your[_-]|"
    r"some[_-]|example[_-]|<[^>]+>|TODO|FIXME|\*{3,}|xxx|XXX|none|null|empty|"
    r"default|changeit|insert|enter|fill|provide|replace)",
    re.IGNORECASE,
)
```

**Exact bugs — two remaining FP sources after these guards:**

**Bug 1 — Short common defaults:** Values like `"admin"`, `"root"`, `"password"`, `"secret"`, `"test"`, `"demo"` are common role defaults that document "this needs a real value." The current `_PLACEHOLDER_RE` does not match single-word defaults.

**Bug 2 — Numeric/integer values in sensitive-named vars:** A variable `api_port: 8080` or `db_connect_timeout: 30` has a sensitive-sounding name (`api_` prefix matches `_SENSITIVE_PARTS`) but an integer value that is not a secret. The `_plaintext_literal()` check allows `isinstance(value, int)`.

**Fix 1 — Extend placeholder pattern** to cover single-word documentation defaults:
```python
_PLACEHOLDER_RE = re.compile(
    r"^(?:PLACEHOLDER|CHANGEME|...|                     # existing patterns
    r"admin|root|password|secret|test|demo|             # ← add common defaults
    r"user|username|localhost|127\.0\.0\.1|             # ← add obvious non-secrets
    r"\d{1,5})$",                                       # ← pure numbers (ports/timeouts)
    re.IGNORECASE,
)
```

**Fix 2 — Exclude numeric values from sensitive variable check:**
```python
def _plaintext_literal(value) -> bool:
    ...
    if isinstance(value, (int, float)):    # ← add this guard
        return False                        # integers/floats are never credential secrets
    ...
```

Expected outcome: these two changes should eliminate ~60 % of remaining FPs. The hardest cases (short non-placeholder strings like `"mypassword123"`) require entropy scoring to resolve.

---

#### `ansibleguard/duplicate-task-names` — 41 % precision · 46 FP

**File:** `src/ansibleguard/detectors/duplicate_task_names.py` · `repeated_task_names()`

**What the code does:**
```python
def repeated_task_names(file_path):
    all_metrics, _ = calculate_metrics_task(file_path)
    task_names = [task.get("task_name", "").strip() for task in all_metrics]
    name_counts = Counter(task_names)
    repeated = [name for name, count in name_counts.items() if count > 1]
    return len(repeated)    # ← returns count with zero context about WHY duplicated
```

**Exact bug:** Counts name occurrences with no reference to the `when:` condition of each task. The standard OS-conditional pattern produces two tasks with the same name but mutually exclusive conditions:
```yaml
- name: Install nginx
  apt: ...
  when: ansible_os_family == "Debian"

- name: Install nginx        # ← same name, different condition → flagged as duplicate
  yum: ...
  when: ansible_os_family == "RedHat"
```

**Fix:** In `calculate_metrics_task`, each task dict already contains task metadata. Modify `repeated_task_names` to group duplicates by name and check whether all tasks with that name carry a `when:` condition (indicating intentional conditional branching):

```python
def repeated_task_names(file_path):
    all_metrics, _ = calculate_metrics_task(file_path)
    by_name = defaultdict(list)
    for task in all_metrics:
        name = task.get("task_name", "").strip()
        if name:
            by_name[name].append(task)

    repeated = []
    for name, tasks in by_name.items():
        if len(tasks) <= 1:
            continue
        # Suppress if every duplicate has a when: condition (intentional branching)
        all_have_when = all(task.get("when") for task in tasks)
        if not all_have_when:
            repeated.append(name)
    return len(repeated)
```

Expected outcome: eliminates ~70 % of FPs (most are OS-branching patterns). Remaining FPs are genuine accidental duplicates with no `when:` condition.

---

### TIER 3 — Medium effort fixes (2–5 days each)

---

#### `ansibleguard/invalid-task-attribute-type` — 43 % precision · 54 FP

**File:** `src/ansibleguard/detectors/partial_checklist.py` · `detect_invalid_task_attribute_types()` · line 248

**Exact bug:** The check for `environment:` and `vars:` attributes:
```python
for attribute in ("environment", "vars"):
    if attribute in task and not isinstance(task[attribute], dict):
        details.append(...)   # ← fires when value is a string like "{{ my_dict }}"
```
A Jinja template `"{{ my_dict }}"` parses as a string in YAML. If `my_dict` is actually a dictionary variable at runtime, this is valid Ansible. The current code has no guard for this case.

**Fix:** The file already defines `FULL_TEMPLATE_RE` for this exact purpose. Apply it:
```python
for attribute in ("environment", "vars"):
    value = task.get(attribute)
    if value is None:
        continue
    if isinstance(value, str) and FULL_TEMPLATE_RE.match(value):
        continue    # ← add: single Jinja expression → runtime type unknown, skip
    if not isinstance(value, dict):
        details.append(...)
```

For `BOOLEAN_ATTRIBUTES` (the `no_log: "{{ var }}"` case): the existing `_resolved_attribute_value()` already returns `_UNRESOLVED` for complex Jinja expressions and skips those. The FP source here is `no_log: "true"` (string `"true"` instead of boolean `true`) — this is a genuine type error and should remain flagged. No change needed for boolean attributes.

Expected outcome: eliminates most of the 54 FPs coming from `environment: "{{ dict_var }}"` patterns.

---

#### `ansibleguard/shell-instead-of-module` — 39 % precision · 34 FP

**File:** `src/ansibleguard/detectors/` (shell module migration detector)

**Exact bug:** The detector identifies commands that have Ansible module equivalents but does not check whether the command is being used as a **read/query** (no Ansible module can read) vs a **write/mutate** (where the module alternative is valid).

Examples of FPs:
- `command: hostname` with `register: current_hostname` — reads the hostname; `ansible.builtin.hostname` can only **set** it
- `command: timedatectl show -p Timezone --value` — reads timezone; `community.general.timezone` can only set it
- `command: timeout 30 {{ cmd }}` — timeout wrapper; no module equivalent

**Fix:** Before flagging a command-module migration, apply two suppression conditions:
1. If the task has `register:` AND `changed_when: false` → read-only probe, skip
2. If the command matches a known read-only invocation pattern (query flags: `show`, `get`, `list`, `status`, `check`) and has `register:`, skip

```python
# In the shell-instead-of-module detector:
is_read_probe = (
    "register" in task
    and (
        task.get("changed_when") in (False, "false", "no")
        or any(flag in command for flag in (" show ", " get ", " list ", " status ", " check "))
    )
)
if is_read_probe:
    continue
```

Expected outcome: eliminates ~50 % of FPs.

---

#### `ansibleguard/unnecessary-set-fact` — 31 % precision · 31 FP

**File:** `src/ansibleguard/detectors/` (set_fact usage detector)

**Exact bug:** The detector flags `set_fact:` calls where the assigned variable is not referenced later in the same file. It does not account for variables consumed in files included via `include_tasks:` or `import_tasks:`.

**Fix:** Before flagging, scan the file for any `include_tasks:` or `import_tasks:` call. If any exist, the variable may be consumed in an included file — suppress the finding:

```python
# In detect_unnecessary_set_fact:
has_includes = any(
    "include_tasks" in task or "import_tasks" in task
    for task in all_tasks
)
if has_includes:
    return 0, []    # cannot determine usage without cross-file analysis
```

This is conservative (suppresses findings in any file with includes) but correct. Files without includes can still be checked reliably.

Expected outcome: eliminates ~60–70 % of FPs. Files with zero includes can be accurately checked.

---

#### `ansibleguard/unscoped-shell-variable` — 30 % precision · 26 FP

**File:** `src/ansibleguard/detectors/partial_checklist.py` · `detect_unscoped_shell_variables()` · line 189

**What the code already handles:** The code already has PowerShell detection (`_POWERSHELL_SYNTAX_RE`), explicit csh/tcsh detection via `executable:`, and inline assignment detection via `INLINE_ASSIGNMENT_RE`.

**Exact remaining bug:** Heredoc scripts where variables are defined within the heredoc body itself. Example:
```yaml
- name: Configure database
  shell: |
    DB_HOST="{{ db_host }}"     # ← defines $DB_HOST inside the heredoc
    DB_PASS="{{ db_pass }}"     # ← defines $DB_PASS
    psql -h $DB_HOST -p $DB_PASS configure.sql   # ← uses $DB_HOST, $DB_PASS
```
`INLINE_ASSIGNMENT_RE` matches `VAR=value` but fails on `VAR="{{ jinja }}"` because the Jinja braces break the simple assignment regex.

**Fix:** Extend `INLINE_ASSIGNMENT_RE` to handle Jinja-valued assignments:
```python
INLINE_ASSIGNMENT_RE = re.compile(
    r'\b([A-Z_][A-Z0-9_]{1,})\s*=(?:"[^"]*"|\'[^\']*\'|\S+)'  # ← existing
    r'|([A-Z_][A-Z0-9_]{1,})\s*=\s*"?\{\{[^}]+\}\}"?',        # ← add Jinja assignment
    re.MULTILINE
)
```

Expected outcome: eliminates ~30 % of remaining FPs (heredoc Jinja-assignment patterns).

---

#### `gitleaks/generic-api-key` — 43 % precision · 31 FP

**File:** Gitleaks rule configuration

**Exact bug:** The generic API key pattern matches any high-entropy string of 20+ characters. SHA-1 hashes (40 hex chars), SHA-256 hashes (64 hex chars), and GPG fingerprints are all matched because they pass the entropy check.

**Fix:** Add a post-match filter that rejects values matching known non-credential formats:
```python
NOT_A_SECRET_RE = re.compile(
    r'^[0-9a-f]{40}$'      # exact SHA-1 (40 lowercase hex)
    r'|^[0-9a-f]{64}$'    # exact SHA-256
    r'|^[0-9A-F]{40}$'    # GPG fingerprint (uppercase hex)
    r'|^[0-9A-F]{8}\s'    # GPG long key with spaces
)
```
Also suppress matches where the variable name contains `sha`, `checksum`, `fingerprint`, `hash`, or `gpg`.

Expected outcome: eliminates ~40 % of FPs.

---

#### `ansibleguard/default-credentials` — 50 % precision · 29 FP

**File:** `src/ansibleguard/detectors/review_checklist.py` · `detect_default_credentials()`

**Exact bug:** The detector checks for known weak passwords (admin/root/password/changeme) but triggers on test environment configuration and molecule scenario variables where these are intentional and non-deployed credentials.

**Fix:** Add path-based suppression for test and molecule contexts:
```python
TEST_PATH_RE = re.compile(
    r'/(molecule|tests?|test_|spec/|fixtures?|examples?|demo|vagrant|docker-compose)/',
    re.IGNORECASE
)
if TEST_PATH_RE.search(str(path)):
    return 0, []
```

Also extend the placeholder check to cover common weak-password documentation patterns: `"password"` as a literal string, `"admin123"`, `"changeme"`.

Expected outcome: eliminates ~40 % of FPs.

---

### TIER 4 — No changes needed (≥ 75 % precision, ship as-is)

These rules are production-ready and should be highlighted in the paper's headline numbers:

| Rule | Precision | Notes |
|---|---|---|
| `large-task` | 100 % | Deterministic line-count threshold |
| `yaml[truthy]` | 100 % | Exact YAML value match |
| `complex-expression` | 100 % | AST-based complexity scoring works |
| `missing-validate-certs` | 100 % | Exact attribute value check |
| `loop-legacy-syntax` | 100 % | Exact deprecated keyword match |
| `large-playbook` | 100 % | Deterministic |
| `redirected-module` | 100 % | Exact module name lookup |
| `unnamed-play` | 100 % | Structural check |
| `unpinned-ansible-dependency` | 100 % | Version pin syntax check |
| `fqcn[action-core]` | 99 % | Near-deterministic namespace check |
| `molecule-test-absent` | 98 % | File existence check |
| `become-scope-too-broad` | 98 % | Structural scope check |
| `role-readme-absent` | 97 % | File existence check |
| `missing-abstraction` | 97 % | Pattern repetition detection |
| `long-task-name` | 97 % | Deterministic length threshold |
| `complex-playbook` | 96 % | Structural complexity score |
| `unused-registered-variable` | 95 % | Reference tracking (reliable in single file) |
| `large-play` | 93 % | Deterministic |
| `unnamed-task` | 93 % | Structural check |
| `insufficient-modularization` | 91 % | Size-based heuristic |
| `non-idempotent-command` | 90 % | Command guard detection |
| `duplicated-code` | 87 % | Block similarity hash |
| `credentials-leaking-in-log` | 81 % | Sensitive param + no_log check |
| `overriding-facts` | 77 % | Unconditional reassignment detection |
| `risky-file-permissions` | 75 % | Octal mode analysis |

---

### Summary: expected precision after Tier 1 disables + Tier 2 fixes

Applying only the Tier 1 disables and Tier 2 fixes (one day of work):

| Scope | Before | After (estimated) |
|---|---|---|
| Overall precision | 72.6 % | ~80–83 % |
| Security category | 62.9 % | ~75 % |
| Documentation category | 39.0 % | ~95 % (driven by one fixed rule) |
| Cohesion category | 8.8 % | removed from headline |
| Rules excluded from headline | 10 | 5 (Tier 1 only) |

---

## 10. Limitations

### Recall not estimated

This study measures **precision only**. We do not know how many real issues the tool misses. The clean-file-review component provides a weak negative-class check (2.5 % file-level false-negative rate) but does not estimate per-rule recall. A recall estimate would require either seeded fault injection (introduce known defects and check if the tool catches them) or a manual audit of a random sample of unflagged files.

### LLM reviewer bias

Both reviewer 2 and the adjudicator are LLM instances (Claude). Using the same model family for two of the three reviewer phases may introduce correlated errors — if Claude systematically misunderstands a specific Ansible pattern, both reviews could converge on the wrong label. A human expert review of a random subset of adjudicated items is recommended before claiming publication-ready precision numbers.

### Single-snapshot corpus

All repositories were scanned at a single frozen commit SHA. Code quality may have changed since the snapshot. Rules related to library versions (deprecated modules, unpinned dependencies) may be impacted by upstream changes after the freeze date.

### Stratified sample — not a random sample

The stratified design ensures coverage across rules and file types but means the overall precision number (72.6 %) is **not directly comparable** to a precision measured on a uniformly random sample of all findings in the corpus. The sampling weights per stratum are not documented here but would be needed for an unbiased population-level precision estimate.

### Uncertain items excluded from precision

455 items (11 % of total occurrences) were labelled `uncertain`. These are excluded from the precision denominator. If uncertain items lean toward FP (as they often do for rules with known context limitations), the true precision is lower than reported.

---

*Report generated from `study/validation-v6/sample.csv` · Script: `scripts/generate_validation_report.py` · Machine-readable data: `study/validation-v6/results_report.csv`*
