# Frozen source context: V007PILOT2-STRUCTURE_REUSE-014

- Repository: `dimagi/commcare-cloud`
- Commit: `f184ea5721b60efd0efce1cc96ce251bcf60df08`
- Family: structure_reuse
- Rule: `ansibleguard/unstructured-module`
- Codebook: `codebooks-v2/FAMILY_STRUCTURE_V2.md`
- Source: `src/commcare_cloud/ansible/roles/nginx/handlers/main.yml` (reported anchor line 1)
- Flagged construct: file-level finding about the whole file or role (`src/commcare_cloud/ansible/roles/nginx/handlers/main.yml`); it names no single task.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–7 of 7:

```text
    1 | ---
    2 | - name: reload nginx
    3 |   include_tasks: reload.yml
    4 | 
    5 | - name: quick start nginx
    6 |   become: yes
    7 |   service: name=nginx state=started enabled=yes
```

## Frozen tracked paths in the relevant role/scope

```text
Scope: `src/commcare_cloud/ansible/roles/nginx`; 21 tracked paths.
Presence checks (computed from the complete listing):
- tasks/main.yml or tasks/main.yaml: no
- README at the scope root: yes
- meta/main.yml or meta/main.yaml: no
- molecule/ directory: no

src/commcare_cloud/ansible/roles/nginx/README.md
src/commcare_cloud/ansible/roles/nginx/defaults/main.yml
src/commcare_cloud/ansible/roles/nginx/handlers/main.yml
src/commcare_cloud/ansible/roles/nginx/tasks/certs.yml
src/commcare_cloud/ansible/roles/nginx/tasks/dropsite.yml
src/commcare_cloud/ansible/roles/nginx/tasks/errorpages.yml
src/commcare_cloud/ansible/roles/nginx/tasks/install.yml
src/commcare_cloud/ansible/roles/nginx/tasks/reload.yml
src/commcare_cloud/ansible/roles/nginx/tasks/set_site_present.yml
src/commcare_cloud/ansible/roles/nginx/tasks/site.yml
src/commcare_cloud/ansible/roles/nginx/templates/default.conf.j2
src/commcare_cloud/ansible/roles/nginx/templates/default.j2
src/commcare_cloud/ansible/roles/nginx/templates/nginx.conf.j2
src/commcare_cloud/ansible/roles/nginx/templates/site.j2
src/commcare_cloud/ansible/roles/nginx/vars/cchq_http.yml
src/commcare_cloud/ansible/roles/nginx/vars/cchq_http_j2me.yml
src/commcare_cloud/ansible/roles/nginx/vars/cchq_ssl.yml
src/commcare_cloud/ansible/roles/nginx/vars/cchq_www_redirect_insecure.yml
src/commcare_cloud/ansible/roles/nginx/vars/cchq_www_redirect_secure.yml
src/commcare_cloud/ansible/roles/nginx/vars/couchdb2.yml
src/commcare_cloud/ansible/roles/nginx/vars/main.yml
```
