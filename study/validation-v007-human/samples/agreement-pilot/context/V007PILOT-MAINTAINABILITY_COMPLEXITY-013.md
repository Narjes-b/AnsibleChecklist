# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-013

- Repository: `dryvist/ansible-proxmox-apps`
- Commit: `b179574eb875a6b7be09df83d001f623a68a2681`
- Family: Maintainability/complexity
- Rule: `ansibleguard/complex-expression`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `roles/technitium_dns/tasks/main/validate_and_auth.yml` (reported anchor line 45)
- Object: `source_location` `43de6c6b68a9ff01d1bab1c2a65460907cca21d62fb614914aa753137b009a7a`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–95 of 95:

```text
    1 | ---
    2 | - name: Validate required variables
    3 |   ansible.builtin.assert:
    4 |     that:
    5 |       - technitium_dns_admin_password | length > 0
    6 |       - technitium_dns_zone | length > 0
    7 |       - technitium_dns_host is defined
    8 |     fail_msg: >-
    9 |       Required variables not set. Check: (1) TECHNITIUM_DNS_ADMIN_PASSWORD must be in Doppler
   10 |       (add via: doppler secrets set TECHNITIUM_DNS_ADMIN_PASSWORD=[REDACTED_LITERAL]
   11 |       (2) PROXMOX_SUBDOMAIN is available via Doppler; (3) technitium_dns_host must be set in
   12 |       the play vars.
   13 |     quiet: true
   14 | 
   15 | # A LOCAL heavy-tier serving host with no address would silently publish nothing:
   16 | # the A-record builder's truthy filter skips an empty ip, so the record the
   17 | # router chain resolves would just be absent from an otherwise green converge.
   18 | # That is the failure this repository is uniquely positioned to cause, because
   19 | # this is where the record is WRITTEN rather than merely read.
   20 | #
   21 | # Conditional, not absolute: an EXTERNAL runner host legitimately has no local
   22 | # address, and must not be pointed at one. The guard therefore fires only when a
   23 | # local host is named without an address to go with it.
   24 | - name: Assert a locally-named heavy-tier serving host has an address to publish
   25 |   ansible.builtin.assert:
   26 |     quiet: true
   27 |     that:
   28 |       - llm_large_serving_ip | default('') | trim | length > 0
   29 |     fail_msg: >-
   30 |       Heavy-tier serving host "{{ llm_large_serving_host }}" is named locally but
   31 |       has no address, so its A record would be silently SKIPPED by the truthy
   32 |       filter and this converge would report success while the name the router
   33 |       pool dials resolves to nothing.
   34 |       Supply the address from tofu-proxmox's constants.serving.ip (the
   35 |       destination state, published once an apply republishes the inventory
   36 |       artifact — tofu-proxmox#827) or from LLM_LARGE_RUNNER_IP.
   37 |       This deliberately does NOT fall back to a built-in address: a committed
   38 |       default is what this change removed, and here a wrong one would not fail
   39 |       locally — it would be published to the estate as authoritative DNS.
   40 |     success_msg: >-
   41 |       Heavy-tier serving host "{{ llm_large_serving_host }}" has an address to publish.
   42 |   when:
   43 |     - llm_large_serving_host | default('') | trim | length > 0
   44 |     # An external runner host is a full FQDN and owns its own DNS elsewhere.
   45 |     - not (lookup('env', 'LLM_LARGE_RUNNER_HOST') | trim | length > 0)
   46 | 
   47 | # Technitium API tokens are PER-INSTANCE — one shared token only authenticates the
   48 | # node that minted it, so the HA secondaries could not be configured. Log into THIS
   49 | # node's API with the shared admin password (technitium_install sets it identically
   50 | # on every member) to obtain this node's OWN session token, and use it for every
   51 | # API call below. Skipped under technitium_dns_apply=false (molecule/CI, no live API).
   52 | #
   53 | # WHY EVERY API TASK IN THIS ROLE IS DELEGATED TO THE CONTROLLER.
   54 | # technitium_dns_api_url is http://{{ technitium_dns_host }}:5380 — a NETWORK
   55 | # address. Running these tasks on the target meant entering the container over
   56 | # pct_remote only to turn around and open a network connection back to that same
   57 | # container's own IP. The container is not a privileged vantage point for its own
   58 | # API; it is just an extra hop, and it cost one SSH channel PER RECORD. The
   59 | # A-record loop alone is ~60 of them, and the paramiko-based pct_remote
   60 | # connection reset partway through every time, leaving the zone half-written and
   61 | # the run unreachable rather than failed.
   62 | #
   63 | # Delegating removes the hop entirely: same URL, same API, same credentials,
   64 | # one fewer failure mode. The task still evaluates the INVENTORY host's
   65 | # variables, so each member is configured through its own endpoint exactly as
   66 | # before — delegation changes where the HTTP call originates, not which host it
   67 | # is about.
   68 | #
   69 | # This is NOT the "delegate_to: localhost tests the controller, not the target"
   70 | # anti-pattern. That rule is about PROBES, where the point is to observe from the
   71 | # target's own position — and the two wait_for probes in ingress_and_apex.yml are
   72 | # deliberately left undelegated for exactly that reason. These are API writes
   73 | # whose subject IS the remote endpoint, so the controller is the correct origin.
   74 | - name: Authenticate to this node's Technitium API (per-host session token)
   75 |   delegate_to: localhost
   76 |   ansible.builtin.uri:
   77 |     url: "{{ technitium_dns_api_url }}/api/user/login"
   78 |     method: POST
   79 |     body_format: form-urlencoded
   80 |     body:
   81 |       user: "{{ technitium_dns_admin_user }}"
   82 |       pass: "{{ technitium_dns_admin_password }}"
   83 |     return_content: true
   84 |     timeout: "{{ technitium_dns_api_timeout }}"
   85 |   register: technitium_dns_login
   86 |   changed_when: false
   87 |   failed_when: technitium_dns_login.json.status | default('') != "ok"
   88 |   when: technitium_dns_apply | bool
   89 |   no_log: true
   90 | 
   91 | - name: Use this node's session token for subsequent API calls
   92 |   ansible.builtin.set_fact:
   93 |     technitium_dns_api_token: "{{ technitium_dns_login.json.token }}"
   94 |   when: technitium_dns_apply | bool
   95 |   no_log: true
```
