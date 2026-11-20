# Frozen source context: V007PILOT-MAINTAINABILITY_COMPLEXITY-025

- Repository: `kubernetes-sigs/kubespray`
- Commit: `9ee6f9b27981b251d77302fd6cf631f330e0ec39`
- Family: Maintainability/complexity
- Rule: `ansibleguard/complex-expression`
- Codebook: `codebooks/FAMILY_MAINTAINABILITY.md`
- Source: `roles/container-engine/docker/tasks/set_facts_dns.yml` (reported anchor line 45)
- Object: `source_location` `b32d0046e7ba16eecff2bbed10a23cedd9d52c41bb7f9d7c5633bc8c620a7d75`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–66 of 66:

```text
    1 | ---
    2 | 
    3 | - name: Set dns server for docker
    4 |   set_fact:
    5 |     docker_dns_servers: "{{ dns_servers }}"
    6 | 
    7 | - name: Show docker_dns_servers
    8 |   debug:
    9 |     msg: "{{ docker_dns_servers }}"
   10 | 
   11 | - name: Add upstream dns servers
   12 |   set_fact:
   13 |     docker_dns_servers: "{{ docker_dns_servers + upstream_dns_servers }}"
   14 |   when: dns_mode in ['coredns', 'coredns_dual']
   15 | 
   16 | - name: Add global searchdomains
   17 |   set_fact:
   18 |     docker_dns_search_domains: "{{ docker_dns_search_domains + searchdomains }}"
   19 | 
   20 | - name: Check system nameservers
   21 |   shell: set -o pipefail && grep "^nameserver" /etc/resolv.conf | sed -r 's/^nameserver\s*([^#\s]+)\s*(#.*)?/\1/'
   22 |   args:
   23 |     executable: /bin/bash
   24 |   changed_when: false
   25 |   register: system_nameservers
   26 |   check_mode: false
   27 | 
   28 | - name: Check system search domains
   29 |   # noqa risky-shell-pipe - if resolf.conf has no search domain, grep will exit 1 which would force us to add failed_when: false
   30 |   # Therefore -o pipefail is not applicable in this specific instance
   31 |   shell: grep "^search" /etc/resolv.conf | sed -r 's/^search\s*([^#]+)\s*(#.*)?/\1/'
   32 |   args:
   33 |     executable: /bin/bash
   34 |   changed_when: false
   35 |   register: system_search_domains
   36 |   check_mode: false
   37 | 
   38 | - name: Add system nameservers to docker options
   39 |   set_fact:
   40 |     docker_dns_servers: "{{ docker_dns_servers | union(system_nameservers.stdout_lines) | unique }}"
   41 |   when: system_nameservers.stdout
   42 | 
   43 | - name: Add system search domains to docker options
   44 |   set_fact:
   45 |     docker_dns_search_domains: "{{ docker_dns_search_domains | union(system_search_domains.stdout.split() | default([])) | unique }}"
   46 |   when: system_search_domains.stdout
   47 | 
   48 | - name: Check number of nameservers
   49 |   fail:
   50 |     msg: "Too many nameservers. You can relax this check by set docker_dns_servers_strict=false in docker.yml and we will only use the first 3."
   51 |   when: docker_dns_servers | length > 3 and docker_dns_servers_strict | bool
   52 | 
   53 | - name: Rtrim number of nameservers to 3
   54 |   set_fact:
   55 |     docker_dns_servers: "{{ docker_dns_servers[0:3] }}"
   56 |   when: docker_dns_servers | length > 3 and not docker_dns_servers_strict | bool
   57 | 
   58 | - name: Check number of search domains
   59 |   fail:
   60 |     msg: "Too many search domains"
   61 |   when: docker_dns_search_domains | length > 6
   62 | 
   63 | - name: Check length of search domains
   64 |   fail:
   65 |     msg: "Search domains exceeded limit of 256 characters"
   66 |   when: docker_dns_search_domains | join(' ') | length > 256
```
