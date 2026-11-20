# Research brief for the v0.0.7 validation (deep version)

This brief replaces the earlier request "analyse the run and write a
validation plan". It asks for a defensible study, not a longer report.

## What a top professional would add

- Pre-register the analysis plan before touching heldout data, and simulate
  the design: plant a known precision per rule on the real population and
  check that the estimator recovers it with the claimed interval.
- Define "true positive" per rule against something checkable (for example
  ansible-core's own parser for type errors), not opinion.
- Measure whether findings matter: are flagged lines fixed in later commits?
- Measure rater reliability before and during the study, including repeat
  labelling by the same rater.
- Test recall on defects whose existence does not depend on this tool.

## Rawest material to start from

- Per-repository raw provider output and stderr logs in the run archive (not
  the aggregate tables and charts).
- The 207 frozen source trees with full git history, including commits after
  the freeze.
- The detector source for each rule (the exact condition being claimed).
- Ansible's own module specs (`ansible-doc -j`).
- The repository-selection ledger, to quantify selection bias.

## Methods and tools

- Sampling and estimation: Neyman allocation from pilot variances,
  Horvitz–Thompson estimators, cluster bootstrap with design effect and
  intra-cluster correlation, Wilson / Clopper–Pearson intervals.
- Reliability: Krippendorff's α, Cohen's κ, Gwet's AC1, Dawid–Skene rater
  model.
- Oracles: `ansible-playbook --syntax-check`, ansible-core argument specs,
  ansible-lint and yamllint as differential references, mutation injection
  for recall.
- Behavioural evidence: `git blame` / `git log -L` fix tracing, survival
  analysis.
- Engineering: numpy simulations in the repository, checksum manifests,
  labelling software that hides tool output from raters.

## What would show the result right, other than the authors

An independent oracle agreeing or disagreeing per rule; blind human raters
with measured agreement; a heldout set opened exactly once; a simulation
recovering a planted truth; maintainers' real later fixes; a third party
re-running from the archive and hashes with identical results; a supervisor's
sign-off of the pre-registration before data collection.

## The brief

> Treat the v0.0.7 study as a research project to be defended, not a report to
> be written.
>
> **Start from raw material:** the per-repository raw outputs and logs in the
> run archive, the frozen source trees and full git history, the detector
> source for each rule, and the repository-selection ledger. Use aggregate
> tables and charts only as claims to verify against those.
>
> **For each rule family:** state what counts as a true positive and name an
> independent, checkable oracle where one exists. Where none exists, say so
> and design the human protocol for that gap.
>
> **Design the validation before collecting anything:** write a pre-registered
> analysis plan; simulate the sampling and estimation on the real population
> with planted precisions to show the claimed intervals hold; use stratified
> allocation from pilot variances and cluster-aware intervals; report
> reliability with Krippendorff's α, κ and AC1 plus repeat-rater checks.
>
> **Add behavioural evidence:** trace whether flagged lines were fixed in later
> commits. **Add a recall test** on defects that do not depend on this tool.
>
> **Rules of evidence:** heldout repositories opened once; no AI labels
> counted as ground truth; every number tied to a frozen version and checksum.
>
> **Deliver:** the plan, the simulation code and its output, the generated
> sample files, and a one-page list of what an outside reviewer needs to
> reproduce each claim. For each conclusion, say what would show it wrong.

## Status

| Item | State |
|---|---|
| Sampling-design simulation | done: `scripts/v007_sampling_simulation.py`, results and findings in `study/validation-design-v007/` (weights are required; effective-n Wilson interval; overall interval needs calibration) |
| Oracle mapping per rule family | open |
| Fix-tracing (behavioural validity) | open |
| Pre-registered analysis plan | open; to be written from the simulation results |
| Generated sample files | open; blocked on a frozen `v0.0.7.1` run |
