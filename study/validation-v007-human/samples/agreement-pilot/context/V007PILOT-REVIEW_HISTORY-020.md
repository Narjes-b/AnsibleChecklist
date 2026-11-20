# Frozen Git review context: V007PILOT-REVIEW_HISTORY-020

- Repository: `ethpandaops/ansible-collection-general`
- Target commit: `15a1f3490258357c4652b96b80f0a92636fa4135`
- Actual first parent: unavailable locally and not required for this message-only rule
- Evidence type: exact target commit message only
- Family: Review/history
- Rule: `ansibleguard/missing-bug-reference`
- Codebook: `codebooks/FAMILY_REVIEW_HISTORY.md`
- Diff range: not used for this message-only rule
- No detector message or scan-time `base: null` fallback is used as review evidence.

## Exact target commit message

```text
fix(powfaucet): move ENS/mainnet RPC default off rpc.flashbots.net (#583)

`rpc.flashbots.net` no longer whitelists `eth_call`:

```
$ curl -s https://rpc.flashbots.net/ -d '{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":"0x00000000000C2E074eC69A0dFb2997BA6C7d2e1e","data":"0x0178b8bf00..."},"latest"]}'
{"jsonrpc":"2.0","error":{"code":-32601,"message":"rpc method is not whitelisted"},"id":1}
```

so every ENS target on a faucet fails with `[INVALID_ENSNAME] Could not
resolve ENS Name 'x.eth': ... rpc method is not whitelisted` (seen on
glamsterdam-devnet-8).

- `powfaucet` role: default `powfaucet_ens_rpcurl` /
`powfaucet_mainnet_rpcurl` → `https://ethereum-rpc.publicnode.com`
(verified: `cast resolve-name bbusa.eth --rpc-url
https://ethereum-rpc.publicnode.com` works).
- `generate_kubernetes_config`: bump the `faucet` / `faucet-agents`
powfaucet chart dependency to 1.2.1, which carries the same default
(ethpandaops/ethereum-helm-charts#494) — no per-devnet value needed.

Depends on ethpandaops/ethereum-helm-charts#494 being released first.

https://claude.ai/code/session_01NxKD2ZoX34y1e5Sz56rGJJ
```

## Changed paths (not required for message-only evidence)

- [not used; this rule is evaluated on the exact target commit message]

The rule is evaluated only on the exact target commit message above. No parent/diff fallback or AI/detector label is used.
