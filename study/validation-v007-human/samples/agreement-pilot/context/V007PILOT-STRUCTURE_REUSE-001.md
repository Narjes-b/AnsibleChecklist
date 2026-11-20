# Frozen source context: V007PILOT-STRUCTURE_REUSE-001

- Repository: `stackhpc/stackhpc-release-train`
- Commit: `3d2f5ac77d3aee42d3c2f206811a7eb8244c55f8`
- Family: Structure/reuse
- Rule: `ansibleguard/duplicated-code`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `ansible/test-pulp-repo-version-query.yml` (reported anchor line 1)
- Object: `source_location` `222827057033c7e8d5202b96ef0cac74f2e40da99aaddca703d6a8f79c268bbc`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–206 of 206:

```text
    1 | ---
    2 | # This playbook queries the dev Pulp server for the latest distribution of each
    3 | # repository. The version is extracted from the base_path, and used to set the
    4 | # 'test_pulp_repository_deb_repo_versions' and
    5 | # 'test_pulp_repository_rpm_repo_versions' facts which contain repository
    6 | # versions to sync to the test Pulp server.
    7 | 
    8 | - name: Update test repo versions
    9 |   hosts: localhost
   10 |   gather_facts: true
   11 |   vars:
   12 |     pulp_url: "{{ dev_pulp_url }}"
   13 |     pulp_username: "{{ dev_pulp_username }}"
   14 |     pulp_password: "{{ dev_pulp_password }}"
   15 |   tasks:
   16 |     - name: Query Deb repositories
   17 |       pulp.squeezer.deb_repository:
   18 |         pulp_url: "{{ pulp_url }}"
   19 |         username: "{{ pulp_username }}"
   20 |         password: "{{ pulp_password }}"
   21 |       register: pulp_deb_repos_list
   22 | 
   23 |     - name: Query Deb publications
   24 |       pulp.squeezer.deb_publication:
   25 |         pulp_url: "{{ pulp_url }}"
   26 |         username: "{{ pulp_username }}"
   27 |         password: "{{ pulp_password }}"
   28 |       register: pulp_deb_pubs_list
   29 | 
   30 |     - name: Query Deb verbatim publications
   31 |       pulp.squeezer.deb_publication:
   32 |         pulp_url: "{{ pulp_url }}"
   33 |         username: "{{ pulp_username }}"
   34 |         password: "{{ pulp_password }}"
   35 |         mode: verbatim
   36 |       register: pulp_deb_verbatim_pubs_list
   37 | 
   38 |     - name: Query Deb distributions
   39 |       pulp.squeezer.deb_distribution:
   40 |         pulp_url: "{{ pulp_url }}"
   41 |         username: "{{ pulp_username }}"
   42 |         password: "{{ pulp_password }}"
   43 |       register: pulp_deb_dists_list
   44 | 
   45 |     - name: Query RPM repositories
   46 |       pulp.squeezer.rpm_repository:
   47 |         pulp_url: "{{ pulp_url }}"
   48 |         username: "{{ pulp_username }}"
   49 |         password: "{{ pulp_password }}"
   50 |       register: pulp_rpm_repos_list
   51 | 
   52 |     - name: Query RPM publications
   53 |       pulp.squeezer.rpm_publication:
   54 |         pulp_url: "{{ pulp_url }}"
   55 |         username: "{{ pulp_username }}"
   56 |         password: "{{ pulp_password }}"
   57 |       register: pulp_rpm_pubs_list
   58 | 
   59 |     - name: Query RPM distributions
   60 |       pulp.squeezer.rpm_distribution:
   61 |         pulp_url: "{{ pulp_url }}"
   62 |         username: "{{ pulp_username }}"
   63 |         password: "{{ pulp_password }}"
   64 |       register: pulp_rpm_dists_list
   65 | 
   66 |     - vars:
   67 |         repo_list: >-
   68 |           {{ pulp_deb_repos_list.repositories
   69 |              | selectattr('name', 'equalto', item.repository)
   70 |              | list }}
   71 |         repo: "{{ repo_list[0] if (repo_list | length > 0) else {} }}"
   72 |         pubs: >-
   73 |           {{ (pulp_deb_pubs_list.publications + pulp_deb_verbatim_pubs_list.publications)
   74 |              | selectattr('repository', 'equalto', repo.get('pulp_href', ''))
   75 |              | stackhpc.pulp.sort_publications | list }}
   76 |         pub: "{{ pubs[0] if (pubs | length > 0) else {} }}"
   77 |         base_name: "{{ item.name | regex_replace('-[0-9]{8}T[0-9]{6}$', '') }}"
   78 |         safe_pattern: "^{{ base_name | regex_escape }}(-[0-9]{8}T[0-9]{6})?$"
   79 |         existing_dists: >-
   80 |           {{ pulp_deb_dists_list.distributions
   81 |              | selectattr('publication', 'equalto', pub.get('pulp_href', ''))
   82 |              | selectattr('name', 'match', safe_pattern)
   83 |              | list }}
   84 |         dist: "{{ existing_dists[0] if (existing_dists | length > 0) else {} }}"
   85 | 
   86 |       block:
   87 |         - name: Ensure Deb distributions exist for latest publication
   88 |           pulp.squeezer.deb_distribution:
   89 |             pulp_url: "{{ pulp_url }}"
   90 |             username: "{{ pulp_username }}"
   91 |             password: "{{ pulp_password }}"
   92 |             name: "{{ item.name }}"
   93 |             base_path: "{{ item.base_path }}"
   94 |             publication: "{{ pub.get('pulp_href') }}"
   95 |             content_guard: "{{ item.content_guard | default(omit) }}"
   96 |             state: present
   97 |           loop: "{{ dev_pulp_distribution_deb }}"
   98 |           loop_control:
   99 |             label: "{{ item.repository }}"
  100 |           when: (pub | length > 0) and (existing_dists | length == 0)
  101 | 
  102 |         - name: Re-query Deb distributions (to capture newly created ones)
  103 |           pulp.squeezer.deb_distribution:
  104 |             pulp_url: "{{ pulp_url }}"
  105 |             username: "{{ pulp_username }}"
  106 |             password: "{{ pulp_password }}"
  107 |           register: pulp_deb_dists_list
  108 | 
  109 |         - name: Display latest Deb distributions
  110 |           vars:
  111 |             info:
  112 |               repo: "{{ repo }}"
  113 |               pub: "{{ pub }}"
  114 |               dist: "{{ dist }}"
  115 |           ansible.builtin.debug:
  116 |             var: info
  117 |           loop: "{{ dev_pulp_distribution_deb }}"
  118 |           loop_control:
  119 |             label: "{{ item.repository }}"
  120 |           when: pub | length > 0
  121 | 
  122 |         - name: Set a fact about latest Deb versions
  123 |           ansible.builtin.set_fact:
  124 |             test_pulp_repository_deb_repo_versions: >-
  125 |               {{ test_pulp_repository_deb_repo_versions
  126 |                  | default({})
  127 |                  | combine({item.short_name: dist.base_path | basename}) }}
  128 |           loop: "{{ dev_pulp_distribution_deb }}"
  129 |           loop_control:
  130 |             label: "{{ item.repository }}"
  131 |           when: dist | length > 0
  132 | 
  133 |         - name: Display latest versions fact
  134 |           ansible.builtin.debug:
  135 |             var: test_pulp_repository_deb_repo_versions
  136 | 
  137 |     - vars:
  138 |         repo_list: >-
  139 |           {{ pulp_rpm_repos_list.repositories
  140 |              | selectattr('name', 'equalto', item.repository)
  141 |              | list }}
  142 |         repo: "{{ repo_list[0] if (repo_list | length > 0) else {} }}"
  143 |         pubs: >-
  144 |           {{ pulp_rpm_pubs_list.publications
  145 |              | selectattr('repository', 'equalto', repo.get('pulp_href', ''))
  146 |              | stackhpc.pulp.sort_publications | list }}
  147 |         pub: "{{ pubs[0] if (pubs | length > 0) else {} }}"
  148 |         base_name: "{{ item.name | regex_replace('-[0-9]{8}T[0-9]{6}$', '') }}"
  149 |         safe_pattern: "^{{ base_name | regex_escape }}(-[0-9]{8}T[0-9]{6})?$"
  150 |         existing_dists: >-
  151 |           {{ pulp_rpm_dists_list.distributions
  152 |              | selectattr('publication', 'equalto', pub.get('pulp_href', ''))
  153 |              | selectattr('name', 'match', safe_pattern)
  154 |              | list }}
  155 |         dist: "{{ existing_dists[0] if (existing_dists | length > 0) else {} }}"
  156 | 
  157 |       block:
  158 |         - name: Ensure RPM distributions exist for latest publication
  159 |           pulp.squeezer.rpm_distribution:
  160 |             pulp_url: "{{ pulp_url }}"
  161 |             username: "{{ pulp_username }}"
  162 |             password: "{{ pulp_password }}"
  163 |             name: "{{ item.name }}"
  164 |             base_path: "{{ item.base_path }}"
  165 |             publication: "{{ pub.get('pulp_href') }}"
  166 |             content_guard: "{{ item.content_guard | default(omit) }}"
  167 |             state: present
  168 |           loop: "{{ dev_pulp_distribution_rpm }}"
  169 |           loop_control:
  170 |             label: "{{ item.repository }}"
  171 |           when: (pub | length > 0) and (existing_dists | length == 0)
  172 | 
  173 |         - name: Re-query RPM distributions (to capture newly created ones)
  174 |           pulp.squeezer.rpm_distribution:
  175 |             pulp_url: "{{ pulp_url }}"
  176 |             username: "{{ pulp_username }}"
  177 |             password: "{{ pulp_password }}"
  178 |           register: pulp_rpm_dists_list
  179 | 
  180 |         - name: Display latest RPM distributions
  181 |           vars:
  182 |             info:
  183 |               repo: "{{ repo }}"
  184 |               pub: "{{ pub }}"
  185 |               dist: "{{ dist }}"
  186 |           ansible.builtin.debug:
  187 |             var: info
  188 |           loop: "{{ dev_pulp_distribution_rpm }}"
  189 |           loop_control:
  190 |             label: "{{ item.repository }}"
  191 |           when: pub | length > 0
  192 | 
  193 |         - name: Set a fact about latest RPM versions
  194 |           ansible.builtin.set_fact:
  195 |             test_pulp_repository_rpm_repo_versions: >-
  196 |               {{ test_pulp_repository_rpm_repo_versions
  197 |                  | default({})
  198 |                  | combine({item.short_name: dist.base_path | basename}) }}
  199 |           loop: "{{ dev_pulp_distribution_rpm }}"
  200 |           loop_control:
  201 |             label: "{{ item.repository }}"
  202 |           when: dist | length > 0
  203 | 
  204 |         - name: Display latest versions fact
  205 |           ansible.builtin.debug:
  206 |             var: test_pulp_repository_rpm_repo_versions
```

## Frozen tracked paths in the relevant role/scope

```text
.ansible-lint
.coderabbit.yaml
.github/CODEOWNERS
.github/actions/setup/action.yml
.github/actions/slack-alert/action.yml
.github/workflows/ansible-lint.yml
.github/workflows/ansible-validations.yml
.github/workflows/container-promote-old.yml
.github/workflows/container-promote.yml
.github/workflows/container-publish.yml
.github/workflows/container-sync.yml
.github/workflows/docs-build.yml
.github/workflows/docs-publish.yml
.github/workflows/package-promote.yml
.github/workflows/package-sync-nightly.yml
.github/workflows/package-sync-version-test-pulp.yml
.github/workflows/package-sync.yml
.github/workflows/package-update-kayobe.yml
.github/workflows/source-repo-sync.yml
.github/workflows/terraform-github-import.yml
.github/workflows/terraform-github.yml
.github/workflows/validate-source-repos.yml
.gitignore
LICENSE
README.md
ansible.cfg
ansible/dev-pulp-container-promote-old.yml
ansible/dev-pulp-container-promote.yml
ansible/dev-pulp-container-publish.yml
ansible/dev-pulp-container-tag-query-kayobe.yml
ansible/dev-pulp-content-guards.yml
ansible/dev-pulp-distribution-list.yml
ansible/dev-pulp-repo-promote.yml
ansible/dev-pulp-repo-publication-cleanup.yml
ansible/dev-pulp-repo-publish.yml
ansible/dev-pulp-repo-sync.yml
ansible/dev-pulp-repo-version-query-kayobe.yml
ansible/filter_plugins/filters.py
ansible/inventory/group_vars/all/deb-package-repos
ansible/inventory/group_vars/all/dev-pulp
ansible/inventory/group_vars/all/dev-pulp-containers
ansible/inventory/group_vars/all/dev-pulp-repos
ansible/inventory/group_vars/all/kolla
ansible/inventory/group_vars/all/package-repos
ansible/inventory/group_vars/all/package-repos-deprecated
ansible/inventory/group_vars/all/rpm-package-repos
ansible/inventory/group_vars/all/source-repositories
ansible/inventory/group_vars/all/test-pulp
ansible/inventory/group_vars/all/test-pulp-containers
ansible/inventory/group_vars/all/test-pulp-repos
ansible/inventory/hosts
ansible/kayobe-container-tag-query.yml
ansible/kayobe-repo-version-query.yml
ansible/roles/pulp-rpm-publication-cleanup/defaults/main.yml
ansible/roles/pulp-rpm-publication-cleanup/tasks/destroy-pubs.yml
ansible/roles/pulp-rpm-publication-cleanup/tasks/main.yml
ansible/roles/source-repo-sync/defaults/main.yml
ansible/roles/source-repo-sync/tasks/add_community_files.yml
ansible/roles/source-repo-sync/tasks/add_label.yml
ansible/roles/source-repo-sync/tasks/add_workflows.yml
ansible/roles/source-repo-sync/tasks/configure_repository.yml
ansible/roles/source-repo-sync/tasks/main.yml
ansible/roles/source-repo-sync/templates/lint-collection.jinja
ansible/roles/source-repo-sync/templates/publish-collection.jinja
ansible/roles/source-repo-sync/templates/publish-role.jinja
ansible/roles/source-repo-sync/templates/tag-and-release.jinja
ansible/roles/source-repo-sync/templates/tox.jinja
ansible/roles/source-repo-sync/templates/upstream-sync.jinja
ansible/source-repo-sync.yml
ansible/test-kayobe-repo-version-generate.yml
ansible/test-pulp-container-publish.yml
ansible/test-pulp-container-sync.yml
ansible/test-pulp-distribution-list.yml
ansible/test-pulp-repo-publication-cleanup.yml
ansible/test-pulp-repo-publish.yml
ansible/test-pulp-repo-specific-version-query.yml
ansible/test-pulp-repo-sync.yml
ansible/test-pulp-repo-version-query.yml
ansible/test-repo-test.yml
ansible/validate-deb-repos.yml
ansible/validate-kolla-container-images.yml
ansible/validate-rpm-repos.yml
docs-requirements.txt
docs/architecture/index.md
docs/contributing.md
docs/img/components.png
docs/index.md
docs/operations/ark.md
docs/operations/github.md
docs/operations/test-pulp.md
docs/usage/access.md
docs/usage/content-howto.md
docs/usage/content-workflows.md
docs/usage/github-organisation-management.md
docs/usage/notifications.md
docs/usage/secrets.md
docs/usage/source-code-ci.md
mkdocs.yml
requirements.txt
requirements.yml
scripts/validate-source-repos.py
terraform/github-runners/.terraform.lock.hcl
terraform/github-runners/ansible.cfg
terraform/github-runners/ansible/group_vars/all
terraform/github-runners/ansible/inventory.yml
terraform/github-runners/ansible/requirements.txt
terraform/github-runners/ansible/requirements.yml
terraform/github-runners/ansible/site.yml
terraform/github-runners/outputs.tf
terraform/github-runners/provider.tf
terraform/github-runners/templates/userdata.cfg.tpl
terraform/github-runners/terraform.tfvars
terraform/github-runners/vm.tf
terraform/github/.terraform.lock.hcl
terraform/github/branches.tf
terraform/github/import_resources.py
terraform/github/provider.tf
terraform/github/repositories.tf
terraform/github/teams.tf
terraform/github/terraform.tfvars.json
[listing truncated after 120 paths]
```
