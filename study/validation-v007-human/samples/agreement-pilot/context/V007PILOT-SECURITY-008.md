# Frozen source context: V007PILOT-SECURITY-008

- Repository: `RedHatGov/redhatgov.workshops`
- Commit: `c946ce095cafcf55bb14a465932410419dac34f2`
- Family: Security
- Rule: `ansibleguard/become-scope-too-broad`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `rhel_edge_aws/3_load.yml` (reported anchor line 51)
- Object: `source_location` `903a0eed884c535e54aed7bf5d047cc1811604e79b56ca595338596a7efb6490`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–423 of 423:

```text
    1 | # file: 2_load.yml
    2 | ---
    3 | 
    4 | - name: Wait for AWS AMIs to become initialized
    5 |   hosts: localhost
    6 |   gather_facts: no
    7 |   tasks:
    8 |     - wait_for:
    9 |         host: "{{ item }}"
   10 |         port: 22
   11 |         state: started
   12 |         timeout: 300
   13 |       with_items:
   14 |         - "{{ groups.rhel_nodes }}"
   15 |         - "{{ groups.tower_rhel_nodes }}"
   16 | 
   17 | - name: Configure repositories on all RHEL nodes
   18 |   become: yes
   19 |   remote_user: ec2-user
   20 |   hosts:
   21 |     - rhel_nodes
   22 |   gather_facts: yes
   23 |   roles:
   24 |     - role: subscription_manager 
   25 |     - role: firewalld
   26 |     - role: epel
   27 |   tasks:
   28 |     - name: add codeready-builder repo
   29 |       community.general.rhsm_repository:
   30 |         name: "{{ item }}"
   31 |       loop:
   32 |         - codeready-builder-for-rhel-8-x86_64-rpms
   33 |         - rhel-8-for-x86_64-appstream-rpms
   34 |       when: not cloud_access and ansible_distribution == 'RedHat' and ansible_distribution_major_version == '8'
   35 | 
   36 |     - name: add codeready-builder rhui repo
   37 |       command: "dnf config-manager --set-enabled {{ item }}"
   38 |       loop:
   39 |         - codeready-builder-for-rhel-8-rhui-rpms
   40 |         - rhel-8-appstream-rhui-rpms
   41 |       when: cloud_access and ansible_distribution == 'RedHat' and ansible_distribution_major_version == '8'
   42 | 
   43 | - name: Configure repositories on nodes
   44 |   become: yes
   45 |   remote_user: ec2-user
   46 |   hosts: le_node
   47 |   gather_facts: no
   48 |   roles:
   49 |     - role: LetsEncrypt
   50 | 
   51 | - name: Configure nodes for workshop
   52 |   become: yes
   53 |   remote_user: ec2-user
   54 |   hosts: rhel_nodes
   55 |   gather_facts: no
   56 |   tasks:
   57 |     - name: check to see if there is a 'System eth0' connection
   58 |       command: "nmcli con show 'System eth0'"
   59 |       register: eth0_result
   60 |       ignore_errors: yes
   61 | 
   62 |     - name: rename system eth0 interface
   63 |       command: "nmcli con mod 'System eth0' connection.id eth0"
   64 |       when: eth0_result.rc == 1
   65 | 
   66 |     - name: install required packages
   67 |       package:
   68 |         name: "{{ item }}"
   69 |         state: latest
   70 |       loop:
   71 |         - bash-completion
   72 |         - composer-cli
   73 |         - cowsay
   74 |         - figlet
   75 |         - golang
   76 |         - lorax-composer
   77 | 
   78 |     - name: install containers-tools
   79 |       command: "dnf -y module install container-tools"
   80 | 
   81 |     - name: add system user to weldr group
   82 |       user:
   83 |         name: ec2-user
   84 |         groups:
   85 |           - "weldr"
   86 |  
   87 | - name: Ensure python3-pip installed for powerline (RHEL 8)
   88 |   become: yes
   89 |   remote_user: ec2-user
   90 |   hosts: rhel_nodes
   91 |   gather_facts: no
   92 |   tasks:
   93 |     - package:
   94 |         name: python3-pip
   95 |         state: latest
   96 |       when: rhel_ver == 'rhel8'    
   97 | 
   98 | - name: Configure software on nodes
   99 |   become: yes
  100 |   remote_user: ec2-user
  101 |   hosts: rhel_nodes
  102 |   gather_facts: no
  103 |   tasks:
  104 |     - name: install git
  105 |       package:
  106 |         name: git
  107 |         state: latest
  108 |   roles:
  109 |     - role: system-user
  110 |     - role: powerline
  111 | 
  112 | - name: Configure web console (RHEL 7)
  113 |   become: yes
  114 |   remote_user: ec2-user
  115 |   hosts: rhel_nodes
  116 |   gather_facts: no
  117 |   roles:
  118 |     - role: wetty
  119 |       when: rhel_ver == 'rhel7'
  120 | 
  121 | - name: Configure web console (RHEL 8)
  122 |   become: yes
  123 |   remote_user: ec2-user
  124 |   hosts: rhel_nodes
  125 |   gather_facts: no
  126 |   roles:
  127 |     - role: cockpit
  128 |       when: rhel_ver == 'rhel8'
  129 | 
  130 | - name: Upgrade packages
  131 |   become: yes
  132 |   remote_user: ec2-user
  133 |   hosts:
  134 |     - rhel_nodes
  135 |   roles:
  136 |     - role: upgrade
  137 | 
  138 | - name: Re-enable SCL repo when upgrade disables it
  139 |   become: yes
  140 |   remote_user: ec2-user
  141 |   hosts:
  142 |     - rhel_nodes
  143 |   gather_facts: yes
  144 |   roles:
  145 |     - role: subscription_manager 
  146 | 
  147 | - name: Open firewalld ports on nodes
  148 |   become: yes
  149 |   remote_user: ec2-user
  150 |   hosts:
  151 |     - rhel_nodes
  152 |   gather_facts: yes
  153 |   tasks:
  154 | #    - name: open firewalld ports
  155 | #      ansible.posix.firewalld:
  156 | #        port: "{{ item }}"
  157 | #        permanent: yes
  158 | #        state: enabled
  159 | #      with_items:
  160 | #      - '8000/tcp'
  161 | 
  162 |     - name: open firewalld services
  163 |       ansible.posix.firewalld:
  164 |         service: "{{ item }}"
  165 |         permanent: yes
  166 |         state: enabled
  167 |       with_items:
  168 |       - 'http'
  169 |       - 'https'
  170 | 
  171 |     - name: restart firewalld service
  172 |       service:
  173 |         name: firewalld
  174 |         state: reloaded
  175 | 
  176 | - name: copy and install qemu
  177 |   become: yes
  178 |   remote_user: ec2-user
  179 |   hosts:
  180 |     - rhel_nodes
  181 |   gather_facts: yes
  182 |   tasks:
  183 |     - name: add codeready-builder repo
  184 |       community.general.rhsm_repository:
  185 |         name: codeready-builder-for-rhel-8-x86_64-rpms
  186 |       when: not cloud_access and ansible_distribution == 'RedHat' and ansible_distribution_major_version == '8'
  187 | 
  188 |     - name: add codeready-builder rhui repo
  189 |       command: dnf config-manager --set-enabled codeready-builder-for-rhel-8-rhui-rpms
  190 |       when: cloud_access and ansible_distribution == 'RedHat' and ansible_distribution_major_version == '8'
  191 | 
  192 |     - name: checkout code
  193 |       git:
  194 |         repo: https://github.com/ajacocks/qemu.git
  195 |         dest: ~ec2-user/edge-workshop
  196 | 
  197 |     - name: copy package
  198 |       copy:
  199 |         src: "{{ item }}"
  200 |         dest: "/work/"
  201 |       with_fileglob:
  202 |         - "/build/rpmbuild/RPMS/x86_64/qemu-full*rpm"
  203 | 
  204 |     - name: find package
  205 |       find:
  206 |         paths: "/work"
  207 |         file_type: file
  208 |         patterns: "*.rpm"
  209 |       register: packages
  210 | 
  211 |     - name: install package
  212 |       dnf:
  213 |         name: "{{ item.path }}"
  214 |         disable_gpg_check: yes
  215 |         state: present
  216 |       loop: "{{ packages.files }}"
  217 | 
  218 |     - name: look up bin directory
  219 |       shell: rpm -ql qemu-full | grep bin | head -1 | sed 's]/bin.*]]'
  220 |       register: path
  221 | 
  222 |     - name: update bashrc with path
  223 |       lineinfile:
  224 |         path: "~ec2-user/.bashrc"
  225 |         regex: "^export PATH=.*"
  226 |         insertafter: EOF
  227 |         line: "export PATH={{ path.stdout }}/bin:~{{ system_user }}/.local/bin:$PATH"
  228 | 
  229 |     - name: update bashrc with manpath
  230 |       lineinfile:
  231 |         path: "~ec2-user/.bashrc"
  232 |         regex: "^export MANPATH=.*"
  233 |         insertafter: EOF
  234 |         line: "export MANPATH={{ path.stdout }}/share/man:$MANPATH"
  235 | 
  236 | - name: clone workshop repo
  237 |   become: yes
  238 |   remote_user: ec2-user
  239 |   hosts:
  240 |     - rhel_nodes
  241 |   gather_facts: yes
  242 |   tasks:
  243 | 
  244 |     - name: create build partition
  245 |       community.general.parted:
  246 |         device: /dev/nvme1n1
  247 |         number: 1
  248 |         fs_type: ext4
  249 |         state: present
  250 | 
  251 |     - name: create build filesystem
  252 |       community.general.filesystem:
  253 |         dev: /dev/nvme1n1p1
  254 |         fstype: ext4
  255 | 
  256 |     - name: create mountpoint
  257 |       file:
  258 |         path: "/work"
  259 |         state: directory
  260 |         mode: '0755'
  261 | 
  262 |     - name: mount build filesystem
  263 |       ansible.posix.mount:
  264 |         path: "/work"
  265 |         src: "/dev/nvme1n1p1"
  266 |         state: mounted
  267 |         fstype: ext4
  268 | 
  269 |     - name: create workshop directory
  270 |       file:
  271 |         path: "/work/workshop"
  272 |         state: directory
  273 |         owner: ec2-user
  274 |         group: ec2-user
  275 | 
  276 |     - name: checkout code
  277 |       git:
  278 |         repo: https://github.com/rlucente-se-jboss/demo-rfe.git
  279 |         dest: "/work/workshop/src/edge-workshop"
  280 |       become: no
  281 | 
  282 |     - name: link workshop dir to home directory
  283 |       file:
  284 |         src: "/work/workshop/src/edge-workshop"
  285 |         dest: "~ec2-user/workshop"
  286 |         state: link
  287 |       become: no
  288 | 
  289 |     - name: regenerate edge.ks
  290 |       shell:
  291 |         cmd: ". ./demo.conf && envsubst < edge.ks.orig > edge.ks"
  292 |         chdir: "~ec2-user/workshop"
  293 |       become: no
  294 | 
  295 |     - name: get VM_NET
  296 |       command: egrep ^VM_NET ~ec2-user/workshop/demo.conf
  297 |       register: vmnet
  298 | 
  299 |     - set_fact:
  300 |         hostip: "{{ vmnet.stdout | regex_replace('.*=','') | regex_replace('\\.[0-9]{1,3}/[0-9]{1,2}$','.2') }}"
  301 | 
  302 |     - name: add ip address to eth0
  303 |       command: "sudo nmcli con mod 'System eth0' +ipv4.addresses {{ hostip }}/24"
  304 | 
  305 |     - name: apply changed ip
  306 |       command: "sudo nmcli con up 'System eth0'"
  307 | 
  308 |     - name: create container registry
  309 |       file:
  310 |         path: "/var/lib/registry"
  311 |         state: directory
  312 | 
  313 |     - name: update registries.conf with dummy entry
  314 |       command: sed -i.bak '/\[registries.insecure\]/!b;n;cdummy'  /etc/containers/registries.conf
  315 | 
  316 |     - name: update dummy entry with hostip
  317 |       command: sed -i "s/dummy/registries = ['{{ hostip }}:5000']/g" /etc/containers/registries.conf
  318 | 
  319 |     - name: Populate service facts
  320 |       ansible.builtin.service_facts:
  321 | 
  322 |     - debug:
  323 |         var: ansible_facts.services
  324 | 
  325 |     - name: create and start registry service
  326 |       block:
  327 | 
  328 |       - name: get registry name for podman service
  329 |         command: >
  330 |           podman run --privileged -d --name registry \
  331 |           -p 5000:5000  -v /var/lib/registry:/var/lib/registry:Z \
  332 |           --restart=always docker.io/library/registry:2
  333 |         register: ctrid
  334 | 
  335 |       - name: generate systemd unit file for podman
  336 |         command: "podman generate systemd --new --files --name {{ ctrid.stdout }}"
  337 |         args:
  338 |           creates: container-registry.service
  339 | 
  340 |       - name: stop podman
  341 |         command: podman stop --all
  342 | 
  343 |       - name: remove all podman content
  344 |         command: podman rm -f --all
  345 | 
  346 |       - name: install container registry service
  347 |         copy:
  348 |           src: container-registry.service
  349 |           dest: /etc/systemd/system/
  350 |           remote_src: yes
  351 | 
  352 |       - name: apply systemd info
  353 |         command: restorecon -vFr /etc/systemd/system
  354 | 
  355 |       - name: start and enable container registry service
  356 |         systemd:
  357 |           name: container-registry.service
  358 |           enabled: yes
  359 |           state: started
  360 |           daemon_reload: yes
  361 |       when: ansible_facts.services['container-registry.service'] is not defined
  362 | 
  363 |     - name: stage rhel 8.3 boot ISO
  364 |       copy:
  365 |         src: "/build/rhel-8.3-x86_64-boot.iso"
  366 |         dest: "~ec2-user/workshop/"
  367 |       become: no
  368 |    
  369 |     - name: create osbuild work directories
  370 |       file:
  371 |         state: directory
  372 |         path: "{{ item }}"
  373 |         owner: _osbuild-composer
  374 |         group: _osbuild-composer
  375 |       loop:
  376 |         - "/work/workshop/cache/osbuild-composer"
  377 |         - "/work/workshop/cache/osbuild-worker"
  378 |         - "/work/workshop/lib/osbuild-composer"
  379 | 
  380 |     - name: apply proper context to directory
  381 |       community.general.sefcontext:
  382 |         target: "{{ item }}(/.*)?"
  383 |         setype: var_lib_t
  384 |         state: present
  385 |       loop:
  386 |         - "/work/workshop/cache/osbuild-composer"
  387 |         - "/work/workshop/cache/osbuild-worker"
  388 |         - "/work/workshop/lib/osbuild-composer"
  389 | 
  390 |     - name: Apply new SELinux file context to filesystem
  391 |       ansible.builtin.command: restorecon -irv /work/workshop
  392 |    
  393 |     - name: create osbuild-composer work directories
  394 |       file:
  395 |         state: directory
  396 |         path: "{{ item }}"
  397 |       loop:
  398 |         - "/etc/systemd/system/osbuild-composer.service.d"
  399 |         - "/etc/systemd/system/osbuild-worker@.service.d"
  400 | 
  401 |     - name: change osbuild composer cache and state directories
  402 |       copy:
  403 |         src: "osbuild-override.conf"
  404 |         dest: "/etc/systemd/system/osbuild-composer.service.d/override.conf"
  405 |         owner: root
  406 |         group: root
  407 |         mode: "0644"
  408 | 
  409 |     - name: change osbuild composer cache and state directories
  410 |       copy:
  411 |         src: "osbuild-worker-override.conf"
  412 |         dest: "/etc/systemd/system/osbuild-worker@.service.d/override.conf"
  413 |         owner: root
  414 |         group: root
  415 |         mode: "0644"
  416 | 
  417 |     - name: Restart service
  418 |       ansible.builtin.systemd:
  419 |         state: restarted
  420 |         daemon_reload: yes
  421 |         name: osbuild-composer.socket
  422 | 
  423 | ...
```
