# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-045

- Repository: `redhatci/ansible-collection-redhatci-ocp`
- Commit: `4b12e633ee5215ec02c302032fffb3d5f3e37425`
- Family: Objective correctness
- Rule: `ansibleguard/read-only-command-change`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `roles/mirror_ocp_release/tasks/facts.yml` (reported anchor line 15)
- Object: `source_location` `be33f6d57a7237d103d03aa3f63953331ad1eca074d53d176cee041ecfac10d4`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–131 of 131:

```text
    1 | ---
    2 | - name: "Get content of release.txt"
    3 |   ansible.builtin.slurp:
    4 |     src: "{{ mor_cache_dir }}/{{ mor_version }}/release.txt"
    5 |   register: _mor_release_content
    6 |   no_log: true
    7 |   retries: 6
    8 |   delay: 10
    9 |   until: _mor_release_content is not failed
   10 | 
   11 | - name: "Read release_image from release content"
   12 |   ansible.builtin.set_fact:
   13 |     mor_release_image: "{{ _mor_release_content.content | b64decode | regex_search('(?<=^Pull From: )(.*)$', multiline=true) }}"
   14 | 
   15 | - name: "Read the contents of rhcos.json"
   16 |   ansible.builtin.command: "cat {{ mor_cache_dir }}/{{ mor_version }}/rhcos.json"
   17 |   register: rhcos
   18 |   no_log: true
   19 |   retries: 6
   20 |   delay: 10
   21 |   until: rhcos is not failed
   22 | 
   23 | - name: "Set image facts"
   24 |   ansible.builtin.set_fact:
   25 |     ocp_release_data:
   26 |       container_image: "{{ mor_release_image }}"
   27 |       rhcos_version: "{{ rhcos.stdout | from_json | json_query('architectures.x86_64.artifacts.metal.release') }}"
   28 |       rhcos_images: >-
   29 |         {{ ocp_release_data['rhcos_images'] | default({})
   30 |         | combine({item.key: (rhcos.stdout | from_json
   31 |         | json_query('architectures.x86_64.artifacts.'
   32 |         + item.path))}) }}
   33 |   with_items:
   34 |     - {'key': 'aws_location', 'path': 'aws.formats."vmdk.gz".disk.location'}
   35 |     - {'key': 'aws_sha256', 'path': 'aws.formats."vmdk.gz".disk.sha256'}
   36 |     - {'key': 'azure_location', 'path': 'azure.formats."vhd.gz".disk.location'}
   37 |     - {'key': 'azure_sha256', 'path': 'azure.formats."vhd.gz".disk.sha256'}
   38 |     - {'key': 'azurestack_location', 'path': 'azurestack.formats."vhd.gz".disk.location'}
   39 |     - {'key': 'azurestack_sha256', 'path': 'azurestack.formats."vhd.gz".disk.sha256'}
   40 |     - {'key': 'gcp_location', 'path': 'gcp.formats."tar.gz".disk.location'}
   41 |     - {'key': 'gcp_sha256', 'path': 'gcp.formats."tar.gz".disk.sha256'}
   42 |     - {'key': 'ibmcloud_location', 'path': 'ibmcloud.formats."qcow2.gz".disk.location'}
   43 |     - {'key': 'ibmcloud_sha256', 'path': 'ibmcloud.formats."qcow2.gz".disk.sha256'}
   44 |     - {'key': 'metal_iso_location', 'path': 'metal.formats.iso.disk.location'}
   45 |     - {'key': 'metal_iso_sha256', 'path': 'metal.formats.iso.disk.sha256'}
   46 |     - {'key': 'metal_pxe_kernel_location', 'path': 'metal.formats.pxe.kernel.location'}
   47 |     - {'key': 'metal_pxe_kernel_sha256', 'path': 'metal.formats.pxe.kernel.sha256'}
   48 |     - {'key': 'metal_pxe_initramfs_location', 'path': 'metal.formats.pxe.initramfs.location'}
   49 |     - {'key': 'metal_pxe_initramfs_sha256', 'path': 'metal.formats.pxe.initramfs.sha256'}
   50 |     - {'key': 'metal_pxe_rootfs_location', 'path': 'metal.formats.pxe.rootfs.location'}
   51 |     - {'key': 'metal_pxe_rootfs_sha256', 'path': 'metal.formats.pxe.rootfs.sha256'}
   52 |     - {'key': 'metal_rawgz_location', 'path': 'metal.formats."raw.gz".disk.location'}
   53 |     - {'key': 'metal_rawgz_sha256', 'path': 'metal.formats."raw.gz".disk.sha256'}
   54 |     - {'key': 'openstack_location', 'path': 'openstack.formats."qcow2.gz".disk.location'}
   55 |     - {'key': 'openstack_sha256', 'path': 'openstack.formats."qcow2.gz".disk.sha256'}
   56 |     - {'key': 'qemu_location', 'path': 'qemu.formats."qcow2.gz".disk.location'}
   57 |     - {'key': 'qemu_sha256', 'path': 'qemu.formats."qcow2.gz".disk.sha256'}
   58 |     - {'key': 'qemu_uncompressed_sha256', 'path': 'qemu.formats."qcow2.gz".disk."uncompressed-sha256"'}  # only needed for bootstraposimage fact
   59 |     - {'key': 'vmware_location', 'path': 'vmware.formats.ova.disk.location'}
   60 |     - {'key': 'vmware_sha256', 'path': 'vmware.formats.ova.disk.sha256'}
   61 |   when:
   62 |     - mor_version is version("4.8", ">=")
   63 | 
   64 | # TODO: Remove this task when 4.7 is no longer supported
   65 | - name: "Set image facts (< 4.8)"
   66 |   vars:
   67 |     rhcos_ver: "{{ rhcos.stdout | from_json | json_query('buildid') }}"
   68 |     base_uri: "https://rhcos.mirror.openshift.com/art/storage/releases/rhcos-{{ mor_base_version }}/{{ rhcos_ver }}/x86_64/"
   69 |   ansible.builtin.set_fact:
   70 |     ocp_release_data:
   71 |       container_image: "{{ mor_release_image }}"
   72 |       rhcos_version: "{{ rhcos_ver }}"
   73 |       rhcos_images: >-
   74 |         {{ ocp_release_data['rhcos_images'] | default({})
   75 |         | combine({item.key: (item.baseURI | default(''))
   76 |         + (rhcos.stdout | from_json
   77 |         | json_query('images.' + item.path))}) }}
   78 |   with_items:
   79 |     - {'key': 'aws_location', 'baseURI': "{{ base_uri }}", 'path': 'aws.path'}
   80 |     - {'key': 'aws_sha256', 'path': 'aws.sha256'}
   81 |     - {'key': 'azure_location', 'baseURI': "{{ base_uri }}", 'path': 'azure.path'}
   82 |     - {'key': 'azure_sha256', 'path': 'azure.sha256'}
   83 |     - {'key': 'gcp_location', 'baseURI': "{{ base_uri }}", 'path': 'gcp.path'}
   84 |     - {'key': 'gcp_sha256', 'path': 'gcp.sha256'}
   85 |     - {'key': 'ibmcloud_location', 'baseURI': "{{ base_uri }}", 'path': 'ibmcloud.path'}
   86 |     - {'key': 'ibmcloud_sha256', 'path': 'ibmcloud.sha256'}
   87 |     - {'key': 'metal_iso_location', 'baseURI': "{{ base_uri }}", 'path': '"live-iso".path'}
   88 |     - {'key': 'metal_iso_sha256', 'path': '"live-iso".sha256'}
   89 |     - {'key': 'metal_pxe_kernel_location', 'baseURI': "{{ base_uri }}", 'path': '"live-kernel".path'}
   90 |     - {'key': 'metal_pxe_kernel_sha256', 'path': '"live-kernel".sha256'}
   91 |     - {'key': 'metal_pxe_initramfs_location', 'baseURI': "{{ base_uri }}", 'path': '"live-initramfs".path'}
   92 |     - {'key': 'metal_pxe_initramfs_sha256', 'path': '"live-initramfs".sha256'}
   93 |     - {'key': 'metal_pxe_rootfs_location', 'baseURI': "{{ base_uri }}", 'path': '"live-rootfs".path'}
   94 |     - {'key': 'metal_pxe_rootfs_sha256', 'path': '"live-rootfs".sha256'}
   95 |     - {'key': 'metal_rawgz_location', 'baseURI': "{{ base_uri }}", 'path': 'metal.path'}
   96 |     - {'key': 'metal_rawgz_sha256', 'path': 'metal.sha256'}
   97 |     - {'key': 'openstack_location', 'baseURI': "{{ base_uri }}", 'path': 'openstack.path'}
   98 |     - {'key': 'openstack_sha256', 'path': 'openstack.sha256'}
   99 |     - {'key': 'qemu_location', 'baseURI': "{{ base_uri }}", 'path': 'qemu.path'}
  100 |     - {'key': 'qemu_sha256', 'path': 'qemu.sha256'}
  101 |     - {'key': 'qemu_uncompressed_sha256', 'path': 'qemu."uncompressed-sha256"'}  # only needed for bootstraposimage fact
  102 |     - {'key': 'vmware_location', 'baseURI': "{{ base_uri }}", 'path': 'vmware.path'}
  103 |     - {'key': 'vmware_sha256', 'path': 'vmware.sha256'}
  104 |   when:
  105 |     - mor_version is version("4.8", "<")
  106 | 
  107 | # NOTE: using uncompressed-sha256 for the bootstraposimage is not a mistake,
  108 | # but needed on OCP versions prior to 4.8. The reason being, when the installer
  109 | # retrieves the image, it will first uncompress it, and then verify the SHA,
  110 | # and the SHA used for verification is the one in the URL.
  111 | # TODO: remove for releases >= 4.8
  112 | - name: "Set facts for *osimage URL overrides"
  113 |   ansible.builtin.set_fact:
  114 |     bootstraposimage: >-
  115 |       {{ mor_webserver_url }}/{{
  116 |       ocp_release_data['rhcos_images']['qemu_location']
  117 |       | basename }}?sha256={{
  118 |       ocp_release_data['rhcos_images']['qemu_uncompressed_sha256'] }}
  119 |     clusterosimage: >-
  120 |       {{ mor_webserver_url }}/{{
  121 |       ocp_release_data['rhcos_images']['openstack_location']
  122 |       | basename }}?sha256={{
  123 |       ocp_release_data['rhcos_images']['openstack_sha256'] }}
  124 |     metalosimage: >-
  125 |       {{ mor_webserver_url }}/{{
  126 |       ocp_release_data['rhcos_images']['metal_iso_location']
  127 |       | basename }}?sha256={{
  128 |       ocp_release_data['rhcos_images']['metal_iso_sha256'] }}
  129 |   when:
  130 |     - mor_write_custom_config | bool
  131 | ...
```
