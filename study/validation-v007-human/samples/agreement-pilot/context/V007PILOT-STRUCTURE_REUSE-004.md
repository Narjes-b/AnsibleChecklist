# Frozen source context: V007PILOT-STRUCTURE_REUSE-004

- Repository: `usegalaxy-eu/infrastructure-playbook`
- Commit: `13681d4e758b42aeeb7e12aac62243e76a5c04fb`
- Family: Structure/reuse
- Rule: `ansibleguard/role-readme-absent`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `roles/hxr.sentry/tasks/main.yml` (reported anchor line 1)
- Object: `source_location` `8152daadfce91464710cc3355af1c32e2f7846d44ca09772cb722880a4903bed`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–123 of 123:

```text
    1 | ---
    2 | - name: Install useful tool
    3 |   package:
    4 |     name: "git"
    5 |     state: latest
    6 |     update_cache: yes
    7 | 
    8 | - name: "ensure sentry user part of docker group"
    9 |   user:
   10 |     name: "{{ hxr_sentry_user }}"
   11 |     groups: docker
   12 |     append: yes
   13 | 
   14 | - name: reset ssh connection to allow user changes to affect 'current login user'
   15 |   meta: reset_connection
   16 | 
   17 | - name: "Make data dir"
   18 |   file:
   19 |     dest: "{{ hxr_sentry_datadir }}"
   20 |     owner: "{{ hxr_sentry_user }}"
   21 |     group: "{{ hxr_sentry_group }}"
   22 |     mode: 0750
   23 |     state: directory
   24 | 
   25 | - name: "Make postgres data dir"
   26 |   file:
   27 |     dest: "{{ hxr_sentry_datadir }}/postgres"
   28 |     owner: "{{ hxr_sentry_user }}"
   29 |     group: "{{ hxr_sentry_group }}"
   30 |     mode: 0700
   31 |     state: directory
   32 | 
   33 | - name: "Make sentry data dir"
   34 |   file:
   35 |     dest: "{{ hxr_sentry_datadir }}/sentry"
   36 |     owner: "{{ hxr_sentry_user }}"
   37 |     group: "{{ hxr_sentry_group }}"
   38 |     mode: 0700
   39 |     state: directory
   40 | 
   41 | - name: "Make repo dir"
   42 |   file:
   43 |     dest: "{{ hxr_sentry_repodir }}"
   44 |     owner: "{{ hxr_sentry_user }}"
   45 |     group: "{{ hxr_sentry_group }}"
   46 |     mode: 0750
   47 |     state: directory
   48 | 
   49 | - name: "Clone repository"
   50 |   become: true
   51 |   become_user: "{{ hxr_sentry_user }}"
   52 |   git:
   53 |     repo: 'https://github.com/getsentry/onpremise'
   54 |     dest: "{{ hxr_sentry_repodir }}"
   55 |     version: "{{ hxr_sentry_version }}"
   56 |     force: true
   57 | 
   58 | - name: Template config files
   59 |   become: true
   60 |   become_user: "{{ hxr_sentry_user }}"
   61 |   template:
   62 |     src: "{{ item }}.j2"
   63 |     dest: "{{ hxr_sentry_repodir }}/{{ item }}"
   64 |     owner: "{{ hxr_sentry_user }}"
   65 |     group: "{{ hxr_sentry_group }}"
   66 |     mode: 0640
   67 |   with_items:
   68 |     - config.yaml
   69 |     - docker-compose.yml
   70 |     - Dockerfile
   71 |     - requirements.txt
   72 | 
   73 | - name: "Build sentry image"
   74 |   command: make
   75 |   become: true
   76 |   become_user: "{{ hxr_sentry_user }}"
   77 |   args:
   78 |     chdir: "{{ hxr_sentry_repodir }}"
   79 | 
   80 | - name: "Pull dependencies"
   81 |   command: docker-compose pull postgres redis smtp memcached
   82 |   become: true
   83 |   become_user: "{{ hxr_sentry_user }}"
   84 |   args:
   85 |     chdir: "{{ hxr_sentry_repodir }}"
   86 | 
   87 | - name: "Kill any existing containers"
   88 |   command: docker-compose kill
   89 |   become: true
   90 |   become_user: "{{ hxr_sentry_user }}"
   91 |   args:
   92 |     chdir: "{{ hxr_sentry_repodir }}"
   93 | 
   94 | - name: "Remove existing conatiners"
   95 |   command: docker-compose rm -f
   96 |   become: true
   97 |   become_user: "{{ hxr_sentry_user }}"
   98 |   args:
   99 |     chdir: "{{ hxr_sentry_repodir }}"
  100 | 
  101 | - name: "Bring up containers"
  102 |   command: docker-compose up -d
  103 |   become: true
  104 |   become_user: "{{ hxr_sentry_user }}"
  105 |   args:
  106 |     chdir: "{{ hxr_sentry_repodir }}"
  107 | 
  108 | - command: sleep 10
  109 | 
  110 | - name: "Migrate"
  111 |   command: docker-compose exec -T web sentry upgrade --noinput
  112 |   become: true
  113 |   become_user: "{{ hxr_sentry_user }}"
  114 |   args:
  115 |     chdir: "{{ hxr_sentry_repodir }}"
  116 | 
  117 | - name: "Create admin user"
  118 |   command: docker-compose exec -T web sentry createuser --email admin@local.host --password password --superuser
  119 |   become: true
  120 |   become_user: "{{ hxr_sentry_user }}"
  121 |   ignore_errors: yes
  122 |   args:
  123 |     chdir: "{{ hxr_sentry_repodir }}"
```

## Frozen tracked paths in the relevant role/scope

```text
roles/hxr.sentry/defaults/main.yml
roles/hxr.sentry/tasks/main.yml
roles/hxr.sentry/templates/Dockerfile.j2
roles/hxr.sentry/templates/config.yaml.j2
roles/hxr.sentry/templates/docker-compose.yml.j2
roles/hxr.sentry/templates/requirements.txt.j2
```
