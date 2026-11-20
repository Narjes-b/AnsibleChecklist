# Missing-abstraction labeling codebook

## Review question

Does this Ansible file contain too many leaf tasks without adequate decomposition into roles, task includes, or another meaningful abstraction?

Judge the design condition, not whether the current threshold fired.

## Labels

- `positive`: the file combines separable responsibilities or has a long sequence that should be divided into meaningful roles/task includes.
- `negative`: the file is cohesive, appropriately scoped, and splitting it would create artificial indirection without improving maintainability.
- `uncertain`: repository structure or omitted source context is necessary to decide.

## Decision rules

1. Consider the entire file and its responsibility, not only the number of tasks.
2. Repeated tasks for one cohesive operation are not automatically a defect.
3. A file can still need further abstraction even if it contains one include or role reference.
4. Small files should normally be negative unless they clearly mix unrelated responsibilities.
5. Large generated files, compliance checklists, and ordered migrations require special care: size alone does not prove that decomposition is appropriate.
6. Record concrete evidence, such as distinct responsibilities that should be separated or a reason the current grouping is cohesive.

Two humans must label independently. The target agreement is Cohen's kappa ≥ 0.80 on a pilot before the primary labels are frozen.
