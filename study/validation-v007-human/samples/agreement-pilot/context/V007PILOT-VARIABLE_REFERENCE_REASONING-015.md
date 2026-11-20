# Frozen source context: V007PILOT-VARIABLE_REFERENCE_REASONING-015

- Repository: `redhatci/ansible-collection-redhatci-ocp`
- Commit: `4b12e633ee5215ec02c302032fffb3d5f3e37425`
- Family: Variable/reference reasoning
- Rule: `ansibleguard/unnecessary-set-fact`
- Codebook: `codebooks/FAMILY_VARIABLES.md`
- Source: `roles/upi_installer/tasks/23_rhcos_image_paths.yml` (reported anchor line 136)
- Object: `variable` `aa4057704e9e007ff7322f1608710c5a252d35cf81cfcd514251eb6a551c39fd`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–140 of 140:

```text
    1 | ---
    2 | - name: "Check if rhcos.json exists"
    3 |   ansible.builtin.stat:
    4 |     path: "{{ cache_dir }}/{{ version }}/rhcos.json"
    5 |     get_checksum: false
    6 |   register: rhcos_json
    7 |   delegate_to: "{{ cache_server }}" # This fact was defined in 10_get_oc.yml
    8 |   tags: rhcospath
    9 | 
   10 | - name: "Fetch rhcos.json File"
   11 |   ansible.builtin.shell: >
   12 |     set -o pipefail &&
   13 |     {{ cache_dir }}/{{ version }}/openshift-install coreos print-stream-json |
   14 |     tee {{ cache_dir }}/{{ version }}/rhcos.json
   15 |   register: rhcos_json_file
   16 |   retries: 3
   17 |   delay: 10
   18 |   until: rhcos_json_file is not failed
   19 |   changed_when: false
   20 |   no_log: true
   21 |   delegate_to: "{{ cache_server }}" # This fact was defined in 10_get_oc.yml
   22 |   when:
   23 |     - not rhcos_json.stat.exists or force_mirroring
   24 |   tags: rhcospath
   25 | 
   26 | - name: "Get the rhcos.json from cache server into temp file on control machine"
   27 |   ansible.builtin.fetch:
   28 |     dest: /tmp/
   29 |     flat: true
   30 |     src: "{{ cache_dir }}/{{ version }}/rhcos.json"
   31 |   delegate_to: "{{ cache_server }}"
   32 | 
   33 | - name: "Load variables from rhcos.json"
   34 |   ansible.builtin.include_vars:
   35 |     file: "/tmp/rhcos.json"
   36 |     name: rhcos_json_vars
   37 |   tags: rhcospath
   38 | 
   39 | - name: "Remove the temporary copy of rhcos.json on control machine"
   40 |   ansible.builtin.file:
   41 |     path: "/tmp/rhcos.json"
   42 |     state: absent
   43 |   delegate_to: localhost
   44 | 
   45 | - name: "Set Facts for RHCOS PXE"  # noqa: jinja[invalid]
   46 |   ansible.builtin.set_fact:
   47 |     rhcos_pxe_kernel_path: "{{ rhcos_json_vars | json_query(kernel_location) }}"
   48 |     rhcos_pxe_kernel_sha256: "{{ rhcos_json_vars | json_query(kernel_sha) }}"
   49 |     rhcos_pxe_initramfs_path: "{{ rhcos_json_vars | json_query(initramfs_location) }}"
   50 |     rhcos_pxe_initramfs_sha256: "{{ rhcos_json_vars | json_query(initramfs_sha) }}"
   51 |     rhcos_pxe_rootfs_path: "{{ rhcos_json_vars | json_query(rootfs_location) }}"
   52 |     rhcos_pxe_rootfs_sha256: "{{ rhcos_json_vars | json_query(rootfs_sha) }}"
   53 |     rhcos_live_iso_path: "{{ rhcos_json_vars | json_query(live_iso_location) }}"
   54 |     rhcos_live_iso_sha256: "{{ rhcos_json_vars | json_query(live_iso_sha) }}"
   55 |     rhcos_vmware_ova_path: "{{ rhcos_json_vars | json_query(vmware_ova_location) }}"
   56 |     rhcos_vmware_ova_sha256: "{{ rhcos_json_vars | json_query(vmware_ova_sha) }}"
   57 |     rhcos_openstack_qcow2_path: "{{ rhcos_json_vars | json_query(openstack_qcow2_location) }}"
   58 |     rhcos_openstack_qcow2_sha256: "{{ rhcos_json_vars | json_query(openstack_qcow2_sha) }}"
   59 |   vars:
   60 |     kernel_location: 'architectures.x86_64.artifacts.metal.formats.pxe.kernel.location'
   61 |     kernel_sha: 'architectures.x86_64.artifacts.metal.formats.pxe.kernel.sha256'
   62 |     initramfs_location: 'architectures.x86_64.artifacts.metal.formats.pxe.initramfs.location'
   63 |     initramfs_sha: 'architectures.x86_64.artifacts.metal.formats.pxe.initramfs.sha256'
   64 |     rootfs_location: 'architectures.x86_64.artifacts.metal.formats.pxe.rootfs.location'
   65 |     rootfs_sha: 'architectures.x86_64.artifacts.metal.formats.pxe.rootfs.sha256'
   66 |     live_iso_location: 'architectures.x86_64.artifacts.metal.formats.iso.disk.location'
   67 |     live_iso_sha: 'architectures.x86_64.artifacts.metal.formats.iso.disk.sha256'
   68 |     vmware_ova_location: 'architectures.x86_64.artifacts.vmware.formats.ova.disk.location'
   69 |     vmware_ova_sha: 'architectures.x86_64.artifacts.vmware.formats.ova.disk.sha256'
   70 |     openstack_qcow2_location: 'architectures.x86_64.artifacts.openstack.formats."qcow2.gz".disk.location'
   71 |     openstack_qcow2_sha: 'architectures.x86_64.artifacts.openstack.formats."qcow2.gz".disk.sha256'
   72 |   tags: rhcospath
   73 | 
   74 | - name: "Set Facts for RHCOS basenames"
   75 |   ansible.builtin.set_fact:
   76 |     rhcos_pxe_kernel_name: "{{ rhcos_pxe_kernel_path | basename }}"
   77 |     rhcos_pxe_initramfs_name: "{{ rhcos_pxe_initramfs_path | basename }}"
   78 |     rhcos_pxe_rootfs_name: "{{ rhcos_pxe_rootfs_path | basename }}"
   79 |     rhcos_live_iso_name: "{{ rhcos_live_iso_path | basename }}"
   80 |     rhcos_vmware_ova_name: "{{ rhcos_vmware_ova_path | basename }}"
   81 |     rhcos_openstack_qcow2_name: "{{ rhcos_openstack_qcow2_path | basename }}"
   82 | 
   83 | - name: "Download file for cache"
   84 |   ansible.builtin.get_url:
   85 |     url: "{{ item[0] }}"
   86 |     dest: "{{ provision_cache_store }}/{{ item[1] }}"
   87 |     mode: '0644'
   88 |     setype: httpd_sys_content_t
   89 |     checksum: "sha256:{{ item[2] }}"
   90 |     timeout: 600
   91 |   register: rootfs_img_file
   92 |   retries: 3
   93 |   delay: 10
   94 |   until: rootfs_img_file is not failed
   95 |   become: true
   96 |   loop: "{{ data[0] | zip(*data[1:]) | list }}"
   97 |   vars:
   98 |     data:
   99 |       - [
  100 |         "{{ rhcos_pxe_kernel_path }}",
  101 |         "{{ rhcos_pxe_initramfs_path }}",
  102 |         "{{ rhcos_pxe_rootfs_path }}",
  103 |         "{{ rhcos_live_iso_path }}",
  104 |         "{{ rhcos_vmware_ova_path }}",
  105 |         "{{ rhcos_openstack_qcow2_path }}"
  106 |       ]
  107 |       - [
  108 |         "{{ rhcos_pxe_kernel_name }}",
  109 |         "{{ rhcos_pxe_initramfs_name }}",
  110 |         "{{ rhcos_pxe_rootfs_name }}",
  111 |         "{{ rhcos_live_iso_name }}",
  112 |         "{{ rhcos_vmware_ova_name }}",
  113 |         "{{ rhcos_openstack_qcow2_name }}"
  114 |       ]
  115 |       - [
  116 |         "{{ rhcos_pxe_kernel_sha256 }}",
  117 |         "{{ rhcos_pxe_initramfs_sha256 }}",
  118 |         "{{ rhcos_pxe_rootfs_sha256 }}",
  119 |         "{{ rhcos_live_iso_sha256 }}",
  120 |         "{{ rhcos_vmware_ova_sha256 }}",
  121 |         "{{ rhcos_openstack_qcow2_sha256 }}"
  122 |       ]
  123 |   tags:
  124 |     - cache
  125 |     - rhcospxe
  126 |   when:
  127 |     - webserver_url | length
  128 |   delegate_to: "{{ cache_server }}" # This fact was defined in 10_get_oc.yml
  129 | 
  130 | - name: "Set Facts for RHCOS cache"
  131 |   ansible.builtin.set_fact:
  132 |     rhcos_pxe_kernel_path: "{{ webserver_url }}/{{ rhcos_pxe_kernel_name }}"
  133 |     rhcos_pxe_initramfs_path: "{{ webserver_url }}/{{ rhcos_pxe_initramfs_name }}"
  134 |     rhcos_pxe_rootfs_path: "{{ webserver_url }}/{{ rhcos_pxe_rootfs_name }}"
  135 |     rhcos_live_iso_path: "{{ webserver_url }}/{{ rhcos_live_iso_name }}"
  136 |     rhcos_vmware_ova_path: "{{ webserver_url }}/{{ rhcos_vmware_ova_name }}"
  137 |     rhcos_openstack_qcow2_path: "{{ webserver_url }}/{{ rhcos_openstack_qcow2_name }}"
  138 |   when:
  139 |     - webserver_url | length
  140 | ...
```

## Visible variable references

```text
4b12e633ee5215ec02c302032fffb3d5f3e37425:roles/upi_installer/tasks/23_rhcos_image_paths.yml:55:    rhcos_vmware_ova_path: "{{ rhcos_json_vars | json_query(vmware_ova_location) }}"
4b12e633ee5215ec02c302032fffb3d5f3e37425:roles/upi_installer/tasks/23_rhcos_image_paths.yml:80:    rhcos_vmware_ova_name: "{{ rhcos_vmware_ova_path | basename }}"
4b12e633ee5215ec02c302032fffb3d5f3e37425:roles/upi_installer/tasks/23_rhcos_image_paths.yml:104:        "{{ rhcos_vmware_ova_path }}",
4b12e633ee5215ec02c302032fffb3d5f3e37425:roles/upi_installer/tasks/23_rhcos_image_paths.yml:136:    rhcos_vmware_ova_path: "{{ webserver_url }}/{{ rhcos_vmware_ova_name }}"
```
