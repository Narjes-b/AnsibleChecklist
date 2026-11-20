# Frozen source context: V007PILOT-STRUCTURE_REUSE-013

- Repository: `yunionio/ocboot`
- Commit: `b781237b81676ff5718525da798292e207124e01`
- Family: Structure/reuse
- Rule: `ansibleguard/duplicated-code`
- Codebook: `codebooks/FAMILY_STRUCTURE.md`
- Source: `onecloud/roles/utils/misc-check/tasks/main.yml` (reported anchor line 1)
- Object: `source_location` `1968dc0b0695583c137acc09ebc1ac9c27f3fb77f71d5435609b01322bea8323`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–70 of 70:

```text
    1 | ---
    2 | - name: check user privilege
    3 |   include_role:
    4 |     name: utils/check-sudoer-privilege
    5 | 
    6 | - name: ansible version
    7 |   set_fact:
    8 |     supported_ansible_version: "2.11.12"
    9 |     minimal_mem: "{{ 1 if lookup('env','IGNORE_ALL_CHECKS') == 'true' or enable_lbagent else 6 }}"
   10 |     minimal_cpu: "{{ 1 if lookup('env','IGNORE_ALL_CHECKS') == 'true' or enable_lbagent else 4 }}"
   11 | 
   12 | - name: debug
   13 |   debug:
   14 |     msg: "minimal_mem: {{minimal_mem}} minimal_cpu: {{minimal_cpu}}"
   15 | 
   16 | - block:
   17 | 
   18 |   - name: test ansible version expecting {{ supported_ansible_version }}, got {{ ansible_version.full }}
   19 |     fail:
   20 |       msg: "Expected ansible version: {{supported_ansible_version}}. Current ansible version is {{ ansible_version.full }}. Please uninstall the old ansible `yum remove -y ansible` or `pip uninstall ansible`, and install the latest ansible as root: `yum install -y python3-pip; python3 -m pip install --upgrade pip setuptools wheel; python3 -m pip install --upgrade ansible`"
   21 | 
   22 |   - meta: end_play
   23 | 
   24 |   when: ansible_version.full is version(supported_ansible_version, '<')
   25 | 
   26 | - block:
   27 | 
   28 |   - name: print hostname msg
   29 |     fail:
   30 |       msg: "Host name can not contain 'localhost'!"
   31 | 
   32 |   - meta: end_play
   33 |   when: ansible_hostname | regex_search('^localhost', ignorecase=True)
   34 | 
   35 | - block:
   36 |   - name: set fact if ignore resource check
   37 |     set_fact:
   38 |       ignore_check: "{{ lookup('env', 'IGNORE_ALL_CHECKS') | default('false') | lower}}"
   39 | 
   40 |   - name: Check Minimum Hardware Requirements
   41 |     assert:
   42 |       that:
   43 |         - ansible_processor_vcpus >= minimal_cpu | int
   44 |         - (ansible_memtotal_mb / 1024 +0.5) | round(1) | int >= minimal_mem | int
   45 |       msg: |
   46 |         cpu: got {{ ansible_processor_vcpus }} (req: {{minimal_cpu}} cores)
   47 |         mem: got {{(ansible_memtotal_mb / 1024 +0.5) | round(1) | int}}GB (req: {{minimal_mem}}GB)
   48 |         you may export IGNORE_ALL_CHECKS=true in test environment to ignore resource check.
   49 |     when:
   50 |     - ignore_check != True
   51 | 
   52 | - name: check if os/ver is supported
   53 |   include_tasks: os.yml
   54 | 
   55 | - name: Get SELinux status
   56 |   shell: |
   57 |     setenforce 0
   58 |     getenforce
   59 |   become: yes
   60 |   register: selinux_status
   61 |   failed_when: false
   62 |   args:
   63 |     executable: /bin/bash
   64 | 
   65 | - name: Warning for SELinux
   66 |   fail:
   67 |     msg: "Please disable selinux and reboot the OS before deploying centos. "
   68 |   when:
   69 |   - selinux_status.stdout == 'Enforcing'
   70 | 
```

## Frozen tracked paths in the relevant role/scope

```text
onecloud/roles/utils/ai-env/README.md
onecloud/roles/utils/ai-env/files/nvidia-container-toolkit.repo
onecloud/roles/utils/ai-env/tasks/check-gpu-and-driver.yml
onecloud/roles/utils/ai-env/tasks/check-local-files.yml
onecloud/roles/utils/ai-env/tasks/configure-containerd.yml
onecloud/roles/utils/ai-env/tasks/configure-grub-Debian.yml
onecloud/roles/utils/ai-env/tasks/configure-grub-RedHat.yml
onecloud/roles/utils/ai-env/tasks/configure-grub.yml
onecloud/roles/utils/ai-env/tasks/configure-host.yml
onecloud/roles/utils/ai-env/tasks/install-container-toolkit-Debian.yml
onecloud/roles/utils/ai-env/tasks/install-container-toolkit-RedHat.yml
onecloud/roles/utils/ai-env/tasks/install-container-toolkit.yml
onecloud/roles/utils/ai-env/tasks/install-cuda.yml
onecloud/roles/utils/ai-env/tasks/install-nvidia-driver-Debian.yml
onecloud/roles/utils/ai-env/tasks/install-nvidia-driver-RedHat.yml
onecloud/roles/utils/ai-env/tasks/install-nvidia-driver.yml
onecloud/roles/utils/ai-env/tasks/main.yml
onecloud/roles/utils/ai-env/tasks/post-tasks.yml
onecloud/roles/utils/ai-env/tasks/pre-tasks.yml
onecloud/roles/utils/ai-env/templates/containerd_config.toml.j2
onecloud/roles/utils/ai-env/templates/host_container_device.yml.j2
onecloud/roles/utils/ai-env/vars/Debian.yml
onecloud/roles/utils/ai-env/vars/OpenCloudOS.yml
onecloud/roles/utils/ai-env/vars/RedHat.yml
onecloud/roles/utils/ai-env/vars/main.yml
onecloud/roles/utils/auto-backup-services/files/db_backup.sh
onecloud/roles/utils/auto-backup-services/tasks/main.yml
onecloud/roles/utils/bin-version-check/tasks/main.yml
onecloud/roles/utils/bin-version-check/vars/default.yml
onecloud/roles/utils/build-iptables-legacy/tasks/main.yml
onecloud/roles/utils/build-iptables-legacy/vars/main.yml
onecloud/roles/utils/ce-services/tasks/main.yml
onecloud/roles/utils/check-sudoer-privilege/tasks/main.yml
onecloud/roles/utils/config-network-manager/tasks/main.yml
onecloud/roles/utils/containerd/handlers/main.yml
onecloud/roles/utils/containerd/tasks/config-host.yml
onecloud/roles/utils/containerd/tasks/ensure-services.yml
onecloud/roles/utils/containerd/tasks/install-lxcfs.yml
onecloud/roles/utils/containerd/tasks/main.yml
onecloud/roles/utils/controlplane/tasks/main.yml
onecloud/roles/utils/cronjobs/tasks/k3s_image_prune.yml
onecloud/roles/utils/cronjobs/tasks/k8s_image_prune.yml
onecloud/roles/utils/cronjobs/tasks/main.yml
onecloud/roles/utils/detect-os/tasks/main.yml
onecloud/roles/utils/detect-os/vars/almalinux-10.aarch64.yml
onecloud/roles/utils/detect-os/vars/almalinux-10.x86_64.yml
onecloud/roles/utils/detect-os/vars/almalinux-8.aarch64.yml
onecloud/roles/utils/detect-os/vars/almalinux-8.x86_64.yml
onecloud/roles/utils/detect-os/vars/almalinux-9.aarch64.yml
onecloud/roles/utils/detect-os/vars/almalinux-9.x86_64.yml
onecloud/roles/utils/detect-os/vars/anolis_os-8.aarch64.yml
onecloud/roles/utils/detect-os/vars/anolis_os-8.x86_64.yml
onecloud/roles/utils/detect-os/vars/archlinux-rolling.aarch64.yml
onecloud/roles/utils/detect-os/vars/archlinux-rolling.x86_64.yml
onecloud/roles/utils/detect-os/vars/centos-10.aarch64.yml
onecloud/roles/utils/detect-os/vars/centos-10.x86_64.yml
onecloud/roles/utils/detect-os/vars/centos-7.aarch64.yml
onecloud/roles/utils/detect-os/vars/centos-7.x86_64.yml
onecloud/roles/utils/detect-os/vars/centos-8.aarch64.yml
onecloud/roles/utils/detect-os/vars/centos-8.x86_64.yml
onecloud/roles/utils/detect-os/vars/centos-9.aarch64.yml
onecloud/roles/utils/detect-os/vars/centos-9.x86_64.yml
onecloud/roles/utils/detect-os/vars/containerd_packages.yml
onecloud/roles/utils/detect-os/vars/ctyunos.yml
onecloud/roles/utils/detect-os/vars/debian-11.aarch64.yml
onecloud/roles/utils/detect-os/vars/debian-11.x86_64.yml
onecloud/roles/utils/detect-os/vars/debian-12.aarch64.yml
onecloud/roles/utils/detect-os/vars/debian-12.x86_64.yml
onecloud/roles/utils/detect-os/vars/debian-13.aarch64.yml
onecloud/roles/utils/detect-os/vars/debian-13.x86_64.yml
onecloud/roles/utils/detect-os/vars/kylin_linux_advanced_server-v10.aarch64.yml
onecloud/roles/utils/detect-os/vars/kylin_linux_advanced_server-v10.x86_64.yml
onecloud/roles/utils/detect-os/vars/kylin_linux_advanced_server-v11.aarch64.yml
onecloud/roles/utils/detect-os/vars/kylin_linux_advanced_server-v11.x86_64.yml
onecloud/roles/utils/detect-os/vars/latest_packages.yml
onecloud/roles/utils/detect-os/vars/opencloudos-8.aarch64.yml
onecloud/roles/utils/detect-os/vars/opencloudos-8.x86_64.yml
onecloud/roles/utils/detect-os/vars/opencloudos-9.aarch64.yml
onecloud/roles/utils/detect-os/vars/opencloudos-9.x86_64.yml
onecloud/roles/utils/detect-os/vars/openeuler-aarch64.yml
onecloud/roles/utils/detect-os/vars/openeuler-x86_64.yml
onecloud/roles/utils/detect-os/vars/qemu_10_packages.yml
onecloud/roles/utils/detect-os/vars/rocky-10.aarch64.yml
onecloud/roles/utils/detect-os/vars/rocky-10.x86_64.yml
onecloud/roles/utils/detect-os/vars/rocky-8.aarch64.yml
onecloud/roles/utils/detect-os/vars/rocky-8.x86_64.yml
onecloud/roles/utils/detect-os/vars/rocky-9.aarch64.yml
onecloud/roles/utils/detect-os/vars/rocky-9.x86_64.yml
onecloud/roles/utils/detect-os/vars/ubuntu-20.aarch64.yml
onecloud/roles/utils/detect-os/vars/ubuntu-20.x86_64.yml
onecloud/roles/utils/detect-os/vars/ubuntu-22.aarch64.yml
onecloud/roles/utils/detect-os/vars/ubuntu-22.x86_64.yml
onecloud/roles/utils/detect-os/vars/ubuntu-24.aarch64.yml
onecloud/roles/utils/detect-os/vars/ubuntu-24.x86_64.yml
onecloud/roles/utils/detect-os/vars/ubuntu-25.aarch64.yml
onecloud/roles/utils/detect-os/vars/ubuntu-25.x86_64.yml
onecloud/roles/utils/detect-os/vars/uniontech-kongzi.yml
onecloud/roles/utils/detect-os/vars/uniontech_os_server_20-fou.yml
onecloud/roles/utils/detect-os/vars/uniontech_os_server_20_enterprise-20.aarch64.yml
onecloud/roles/utils/detect-os/vars/uniontech_os_server_20_enterprise-20.x86_64.yml
onecloud/roles/utils/detect-os/vars/uos-aarch64.yml
onecloud/roles/utils/detect-os/vars/win11_packages.yml
onecloud/roles/utils/disable-telegraf-service/tasks/main.yml
onecloud/roles/utils/ee-services/tasks/main.yml
onecloud/roles/utils/eip-ha/files/get_oc_vars.sh
onecloud/roles/utils/eip-ha/files/keepalived-eipgw-notify.sh
onecloud/roles/utils/eip-ha/handlers/main.yml
onecloud/roles/utils/eip-ha/tasks/main.yml
onecloud/roles/utils/eip-ha/templates/keepalived-eipgw.conf.j2
onecloud/roles/utils/eip-ha/templates/sdnagent.conf.j2
onecloud/roles/utils/enable-eip/tasks/main.yml
onecloud/roles/utils/enable-pod-feature/tasks/main.yml
onecloud/roles/utils/fabric-setup/tasks/main.yml
onecloud/roles/utils/fabric-setup/templates/25-vxlan.netdev.j2
onecloud/roles/utils/fabric-setup/templates/25-vxlan.network.j2
onecloud/roles/utils/fetch-node-interface/tasks/main.yml
onecloud/roles/utils/gpu-init/files/functions
onecloud/roles/utils/gpu-init/files/gpu_setup.sh
onecloud/roles/utils/gpu-init/files/pci.ids
onecloud/roles/utils/gpu-init/tasks/main.yml
[listing truncated after 120 paths]
```
