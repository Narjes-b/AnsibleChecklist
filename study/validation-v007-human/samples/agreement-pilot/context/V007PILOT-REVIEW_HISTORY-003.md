# Frozen Git review context: V007PILOT-REVIEW_HISTORY-003

- Repository: `usegalaxy-eu/vgcn`
- Target commit: `c65e4ea9febe2bf5eeca04715c93a441d82f7875`
- Actual first parent: `9cf0572aeae5ce57b1771eb35b2bac46c792bf27`
- Evidence type: actual first-parent diff
- Family: Review/history
- Rule: `ansibleguard/missing-release-note`
- Codebook: `codebooks/FAMILY_REVIEW_HISTORY.md`
- Diff range: `9cf0572aeae5ce57b1771eb35b2bac46c792bf27..c65e4ea9febe2bf5eeca04715c93a441d82f7875` (from frozen Git objects)
- No detector message or scan-time `base: null` fallback is used as review evidence.

## Exact target commit message

```text
Merge pull request #120 from usegalaxy-eu/rocky_security_repository

Enable Rocky Linux security repository
```

## Changed paths (2)

- `M` `ansible/generic.yml`
- `M` `requirements.yml`

## Relevant first-parent diff

```diff
diff --git a/ansible/generic.yml b/ansible/generic.yml
index f89b6e3..d84980b 100644
--- a/ansible/generic.yml
+++ b/ansible/generic.yml
@@ -1,7 +1,44 @@
 ---
+- name: Manage kernel
+  hosts: generic
+  tasks:
+    - name: Retrieve kernel version
+      ansible.builtin.shell:
+        cmd: uname -r
+      register: kernel
+      changed_when: false
+
+    - name: Print kernel version
+      ansible.builtin.debug:
+        msg: "{{ kernel }}"
+
+    - name: Ensure kernel-modules-extra is installed (provides xt_addrtype etc. needed by Docker's iptables rules)
+      ansible.builtin.dnf:
+        name: kernel-modules-extra
+        state: present
+
+- name: Manage package repositories and system updates
+  hosts: generic
+  roles:
+    - role: usegalaxy_eu.rocky_security_repository
+      vars:
+        rocky_security_repository_repo_definitions_upgrade: true
+      become: true
+    - geerlingguy.repo-epel # Install EPEL
+    - usegalaxy-eu.autoupdates # keep all of our packages up to date REMOVED until latest kernel is supported in dnbd3
+  tasks:
+    - name: system update (without kernel update)
+      ansible.builtin.dnf:
+        name: "*"
+        exclude:
+          - kernel*
+          - kmod-kvdo
+        state: latest
+
 - hosts: generic
+  name: Create users and install packages 
   vars:
     software_groups_to_install:
       - admin
       - editors
       - terminals
@@ -15,29 +52,10 @@
     - name: Add the user Galxy
       ansible.builtin.user:
         name: galaxy
         uid: 999
         group: galaxy
-    - name: Debug Kernel version
-      ansible.builtin.shell:
-        cmd: uname -r
-      register: kernel
-    - name: Print kernel version
-      ansible.builtin.debug:
-        msg: "{{ kernel }}"
-    - name: system update (without kernel update)
-      ansible.builtin.dnf:
-        name: "*"
-        exclude:
-          - kernel*
-          - kmod-kvdo
-        state: latest
-    # Bug Fix Test: https://build.galaxyproject.eu/job/usegalaxy-eu/job/VGCN-Image-Build/367/console
-    - name: Ensure kernel-modules-extra is installed (provides xt_addrtype etc. needed by Docker's iptables rules)
-      ansible.builtin.dnf:
-        name: kernel-modules-extra
-        state: present
     - name: Put SELinux in permissive mode, logging actions that would be blocked.
       ansible.posix.selinux:
         policy: targeted
         state: permissive
     - name: Enable firewalld service
@@ -59,10 +77,9 @@
         enable_powertools: true
         enable_install_software: true
         enable_grub: true
         enable_kernel_5: "{{ true if (ansible_facts['distribution_major_version'] < '9') else false }}"
 
-    - geerlingguy.repo-epel # Install EPEL
     - usegalaxy-eu.ffmpeg
     - usegalaxy-eu.dynmotd
     - influxdata.chrony
     - usegalaxy-eu.telegraf
diff --git a/requirements.yml b/requirements.yml
index 68b86c3..120004b 100644
--- a/requirements.yml
+++ b/requirements.yml
@@ -11,10 +11,12 @@ collections:
     type: galaxy
   - name: devsec.hardening
     version: 10.5.2
     source: https://galaxy.ansible.com
     type: galaxy
+  - name: community.general
+    version: 8.2.0
 roles:
   - name: usegalaxy_eu.cuda
     version: 2.0.0
     src: https://github.com/usegalaxy-eu/ansible-cuda
   - name: usegalaxy_eu.nvidia_container
@@ -52,5 +54,8 @@ roles:
   - name: openslx-ng.dracut
     src: https://github.com/usegalaxy-eu/ansible-dracut
     version: 0.1.1
   - name: usegalaxy_eu.ssh_manager
     version: 0.0.2
+  - name: usegalaxy_eu.rocky_security_repository
+    version: v0.1.0
+    src: https://github.com/usegalaxy-eu/ansible-rocky-security-repository

```
