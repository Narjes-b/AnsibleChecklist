# Frozen Git review context: V007PILOT-REVIEW_HISTORY-013

- Repository: `chrisshaiman/lamware`
- Target commit: `09f919635087b38354bce34c9bc48e7c6517b463`
- Actual first parent: unavailable locally and not required for this message-only rule
- Evidence type: exact target commit message only
- Family: Review/history
- Rule: `ansibleguard/commit-message-format`
- Codebook: `codebooks/FAMILY_REVIEW_HISTORY.md`
- Diff range: not used for this message-only rule
- No detector message or scan-time `base: null` fallback is used as review evidence.

## Exact target commit message

```text
chore(packer): pin the builder version, and make CI agree with it (#514-adjacent) (#520)

Every template said `required_version = ">= 1.10"`, so any Packer from 1.10
onward could build the guest images and no artifact recorded which one did. The
builder is an input to the image — a different Packer can produce a different
guest — and that is the same defect as the floating
`mcr.microsoft.com/dotnet/sdk:10.0` tag that left the dotnet-analysis image
unbuildable once the tag moved under a reusable cache (#514).

Pinned to `~> 1.16.0` in all six templates: patch releases inside 1.16.x stay
allowed so a security fix is not blocked, and a minor bump becomes a decision
rather than a surprise.

packer/README.md records the exact release, its sha256, and the verify-then-
install steps — a constraint says which versions are ALLOWED, but reproducing an
image needs the one that was USED. Installed as a pinned binary rather than from
HashiCorp's apt repo, which tracks latest and would reintroduce the same drift.

The version I first proposed (1.11.2) was stale; the release index says 1.16.0,
2026-07-24. Checked rather than asserted.

CI ALSO DECLARES A PACKER VERSION, and it said `~1.11`. Raising the templates
without moving CI would have made every `packer validate -syntax-only` fail —
a job that cannot pass is not a check. Two places declaring the same thing with
nothing making them agree is the drift this commit is about, so a test now
asserts the CI version and the template constraint share a series.

Still not pinned, and said so in the README rather than left implicit: `packer
init` fetches the qemu plugin (`~> 1.1`) from GitHub. The `.pkr.hcl.lock` file
it writes is the mechanism that fixes that, and should be committed after the
first init.

Mutations: one template drifting back to `>= 1.10` fails two tests; CI drifting
back to `~1.11` fails a third.


Claude-Session: https://claude.ai/code/session_015RjCB4eKYr9FGtuNmhKEUg

Co-authored-by: Claude Opus 5 (1M context) <noreply@anthropic.com>
```

## Changed paths (not required for message-only evidence)

- [not used; this rule is evaluated on the exact target commit message]

The rule is evaluated only on the exact target commit message above. No parent/diff fallback or AI/detector label is used.
