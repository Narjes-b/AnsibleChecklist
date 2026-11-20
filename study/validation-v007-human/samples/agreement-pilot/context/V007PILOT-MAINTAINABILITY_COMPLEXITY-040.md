# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-040

- Repository: `jr0dd/home-ops`
- Commit: `0e76c37818159bea648890d4ee132616f6ed6499`
- Family: Maintainability/complexity
- Rule: `ansibleguard/incomplete-task`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `infrastructure/ansible/playbooks/k3s/install.yml` (reported anchor line 16)
- Object: `source_location` `d917fd6892a49d150a3a519204395ca6af50c3347c1f6dd9f2d9e6942e8abd21`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–27 of 27:

```text
    1 | ---
    2 | - hosts:
    3 |     - master-nodes
    4 |     - worker-nodes
    5 |     - storage-nodes
    6 |   become: true
    7 |   gather_facts: true
    8 |   any_errors_fatal: true
    9 |   pre_tasks:
   10 |     - name: Pausing for 5 seconds...
   11 |       ansible.builtin.pause:
   12 |         seconds: 5
   13 |   roles:
   14 |     - k3s
   15 |   tasks:
   16 |     - name: k3s | install extra binaries
   17 |       ansible.builtin.shell: |
   18 |         # cilium
   19 |         curl -L --remote-name-all https://github.com/cilium/cilium-cli/releases/latest/download/cilium-linux-amd64.tar.gz{,.sha256sum}
   20 |         sha256sum --check cilium-linux-amd64.tar.gz.sha256sum
   21 |         tar xzvfC cilium-linux-amd64.tar.gz /usr/local/bin
   22 |         rm cilium-linux-amd64.tar.gz{,.sha256sum}
   23 |         # flux
   24 |         curl -s "https://fluxcd.io/install.sh" | bash
   25 |         # kustomize
   26 |         curl -s "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh"  | bash
   27 |         install -o root -g root -m 0755 kustomize /usr/local/bin/kustomize
```
