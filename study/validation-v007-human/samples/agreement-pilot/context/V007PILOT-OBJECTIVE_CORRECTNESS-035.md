# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-035

- Repository: `ConnectBox/connectbox-pi`
- Commit: `e69eabdecfa2e39b2751acdb928bfafb2f8f28f6`
- Family: Objective correctness
- Rule: `ansibleguard/silent-error-suppression`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `ansible/roles/hat-service/tasks/main.yml` (reported anchor line 29)
- Object: `source_location` `b6d9241a95a5f27444945fad702958db5dd358858217c9a32412bf27d0ab89b3`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–439 of 439:

```text
    1 | --- 
    2 | - name: Find the /tmp  system paramaters
    3 |   shell: df -h /tmp
    4 |   register: tempoutput
    5 |   ignore_errors: yes
    6 | 
    7 | - name: Set a default fact for Swap_Val
    8 |   set_fact:
    9 |      Swap_Val:  ""
   10 |      Temp_Val:  ""
   11 | 
   12 | - name: Find the /swap system paramaters
   13 |   shell: df -h /swap
   14 |   register: swapoutput
   15 |   ignore_errors: yes
   16 | 
   17 | - debug:
   18 |     msg: "Swap system output: {{swapoutput.stdout}}"
   19 | 
   20 | - name: Set /TMP size value into variable
   21 |   vars:
   22 |      tmpvl: "{{ tempoutput.stdout | regex_search('tmpfs\\s*([0-9]*[KMG])', '\\1') }}" 
   23 |   set_fact:
   24 |      Temp_Val: "{{ tmpvl[0] }}"
   25 |      cacheable: yes
   26 |   when: tempoutput != ""   
   27 |   ignore_errors: yes
   28 | 
   29 | - name: Set /Swap size value into variable
   30 |   vars:
   31 |      swpvl:  "{{ swapoutput.stdout | regex_search('\\s*([0-9]*[KMG])', '\\1') }}" 
   32 |   set_fact:
   33 |      Swap_Val: "{{ swpvl[0] }}"
   34 |      cacheable: yes
   35 |   when: swapoutput != ""   
   36 |   ignore_errors: yes
   37 |  
   38 | - name: Print the temp variables we have found on file size
   39 |   debug:
   40 |     msg: "temp file size is {{ Temp_Val }}"
   41 |   ignore_errors: yes
   42 | 
   43 | - name: print the swap variables we have found on file size
   44 |   debug:
   45 |     msg: "swap file size is {{ Swap_Val }}"
   46 |   ignore_errors: yes
   47 | 
   48 | - name: Expand Temp directory otherwise we will run out of space
   49 |   command: umount /tmp
   50 |   ignore_errors: yes
   51 |   when: connectbox_os != "raspbian" and Temp_Val != "" and Temp_Val < '400M'
   52 | 
   53 | - name: recreate the Temp directory
   54 |   command: mount -t tmpfs -o size=400M tmpfs /tmp
   55 |   ignore_errors: yes
   56 |   when: connectbox_os != "raspbian" and Temp_Val != "" and Temp_Val < '400M'
   57 | 
   58 | #original swapfile on NEO is /dev/zram0 if size 121968 and priority 5 but not for Buster
   59 | 
   60 | - name: create swapfile if it dosn't exist
   61 |   file:
   62 |     path: "/swapfile"
   63 |     mode: 0600
   64 |     owner: "root"
   65 |     group: "root"
   66 |     state: touch
   67 |   register: swapcreate
   68 |   when: connectbox_os != 'raspbian' 
   69 | 
   70 | - name: fix variables if we created the swapfile
   71 |   set_fact:
   72 |     Swap_Val: 0M
   73 |     cacheable: yes
   74 |   ignore_errors: yes
   75 |   when: swapcreate != ""
   76 | 
   77 | - name: Turn off swap
   78 |   command: swapoff -a
   79 |   when: swapcreate != ""
   80 |   ignore_errors: yes
   81 | 
   82 | - name: Expand swapfile
   83 |   command: fallocate -l 400M /swapfile
   84 |   register: swap_result
   85 |   ignore_errors: yes
   86 |   when: connectbox_os != "raspbian" Swap_Val < '400M'
   87 | 
   88 | - name: show swap_result
   89 |   debug:
   90 |    msg: "output of expand swapfile is {{ swap_result }}"
   91 | 
   92 | - name: fill swapfile
   93 |   command: dd if=/dev/zero of=/swapfile bs=1024 count=409600
   94 |   register: command_result
   95 |   ignore_errors: yes
   96 |   when: connectbox_os != "raspbian" and Swap_Val != ""
   97 | 
   98 | 
   99 | - name: change swap mode
  100 |   file:
  101 |     path: /swapfile
  102 |     mode: 0600
  103 |   when: connectbox_os != "raspbian"
  104 | 
  105 | - name: make it a swapfile
  106 |   command: mkswap /swapfile
  107 |   register: command_result
  108 |   ignore_errors: yes
  109 |   when: connectbox_os != "raspbian"
  110 | 
  111 | - name: turn swapfile on
  112 |   command: swapon /swapfile
  113 |   register: command_result
  114 |   ignore_errors: yes 
  115 |   when: connectbox_os != "raspbian"
  116 | 
  117 | - name: Enable fstab change
  118 |   lineinfile:
  119 |     path: /etc/fstab
  120 |     line: '/swapfile none swap sw,rw,auto,nodev,nosuid,size=400M,rw,sync 0 0'
  121 |     state: present
  122 |     create: yes
  123 |   when: connectbox_os != "raspbian"
  124 | 
  125 | - name: install aptitude
  126 |   apt:
  127 |     name: aptitude
  128 |     state: latest
  129 | 
  130 | # Following sections install needed packages for the display, depending on configuration
  131 | 
  132 | - name: Install packages to run OLED (!raspbian, !bullseye, !buster)
  133 |   command: aptitude -y install "{{ item }}"
  134 |   loop:
  135 |     - 'libjpeg-turbo8'
  136 |     - 'python3-dev'
  137 |     - 'libfreetype6'
  138 |     - 'libfreetype6-dev'
  139 |     - 'zlib1g-dev'
  140 |     - 'libpng-dev'
  141 |     - 'lshw'
  142 |     - 'libjpeg-dev'
  143 |     - 'python3-setuptools'
  144 |     - 'libtiff5-dev'
  145 |     - 'libjpeg8-dev'
  146 |     - 'libopenjp2-7-dev'
  147 |     - 'liblcms2-dev'
  148 |     - 'libwebp-dev'
  149 |     - 'tcl8.6-dev'
  150 |     - 'tk8.6-dev'
  151 |     - 'python3-tk'
  152 |     - 'libharfbuzz-dev'
  153 |     - 'libfribidi-dev'
  154 |     - 'libxcb1-dev'
  155 |     - 'libtiff5' 
  156 |   when: connectbox_os != "raspbian" and OS_Version != "bullseye" and OS_Version != 'buster'
  157 | 
  158 | - name: Install prerequesitst for Pillow build (!raspbian & (bullseye or buster))
  159 |   apt:
  160 |     name: ['python3-dev', 'python3-setuptools', 'libtiff5-dev', 'libjpeg62-turbo-dev', 'libjpeg62-turbo', 'libopenjp2-7-dev', 'libopenjp2-7', 'zlib1g-dev', 'zlib1g', 'libfreetype6-dev', 'libfreetype6', 'liblcms2-dev', 'libwebp-dev', 'tcl8.6-dev', 'tk8.6-dev', 'python3-tk', 'libharfbuzz-dev', 'libfribidi-dev', 'libxcb1-dev', 'libtiff5']
  161 |     state: present
  162 |   when: connectbox_os != 'raspbian' and (OS_Version == 'bullseye' or OS_Version == "buster")
  163 | 
  164 | - name: Install packages to run OLED (raspbian, !bullseye, !buster)
  165 |   apt:
  166 |     name: [ 'libjpeg9-dev', 'python3-dev', 'libjpeg9', 'libfreetype6', 'libfreetype6-dev', 'zlib1g', 'zlib1g-dev', 'libopenjp2-7', 'libtiff5', 'lshw', 'libjpeg-dev']
  167 |     state: present
  168 |   when: connectbox_os == 'raspbian' and (OS_Version != 'bullseye' and OS_Version != 'buster')
  169 | 
  170 | - name: install packages to run OLED (raspbian & (bullseye or buster))
  171 |   apt:
  172 |     name: [ 'libjpeg62-turbo', 'python3-dev', 'libjpeg62-turbo-dev', 'libfreetype6', 'libfreetype6-dev', 'zlib1g', 'zlib1g-dev', 'libopenjp2-7', 'libtiff5', 'lshw']
  173 |     state: present
  174 |   when: connectbox_os == 'raspbian' and (OS_Version == 'bullseye' or OS_Version == 'buster')
  175 | 
  176 | 
  177 | # Create hat-service venv... the python3-venv method is used because without it we 
  178 | #  get build errors relating to missing Python.h when installing NEO_BatteryLevelShutdown.git
  179 | 
  180 | - name: Make neo battery shutdown virtualenv directory
  181 |   file:
  182 |     path: "{{ hat_service_virtualenv_dir }}"
  183 |     state: directory  
  184 | 
  185 | - name: Install virtual environment tool
  186 |   apt:
  187 |     name: python3-venv
  188 | 
  189 | - name: Create virtual environment
  190 |   command: python3 -m venv {{ hat_service_virtualenv_dir }}
  191 | 
  192 | - name: Setup neo battery shutdown virtualenv (python3)
  193 |   pip:
  194 |     name: git+https://github.com/ConnectBox/NEO_BatteryLevelShutdown.git
  195 |     virtualenv: "{{ hat_service_virtualenv_dir }}"
  196 |   ignore_errors: yes                                              #If already installed don't fail on the failed git.
  197 | 
  198 | - name: Install Pillow and psutil in virtual environment
  199 |   pip:
  200 |     name: ['Pillow==6.2.1', 'psutil']
  201 |     state: present
  202 |     virtualenv: "{{ hat_service_virtualenv_dir }}"
  203 | 
  204 | 
  205 | - name: determine python version
  206 |   shell: python --version
  207 |   register: python_version_raw
  208 | 
  209 | - debug:
  210 |     msg: "{{ python_version_raw.stdout }}"
  211 | 
  212 | - name: parse the python version
  213 |   vars:
  214 |      pythonversion: "{{ python_version_raw.stdout | regex_replace('P[a-z]*\\s(\\d\\.\\d).*', 'python\\1') }}"
  215 |   set_fact:
  216 |      python_ver: "{{ pythonversion }}"
  217 |      cacheable: yes
  218 | 
  219 | - name: python version is now 
  220 |   debug:
  221 |     msg: "python version is now: {{ python_ver }}" 
  222 | 
  223 | - name: Install devmem2 in NEO
  224 |   apt:
  225 |     name: devmem2
  226 |     state: present
  227 |   ignore_errors: yes
  228 |   when: connectbox_os != "raspbian" and OS_Version != 'bullseye' and OS_Version != 'buster'
  229 | 
  230 | - name: check for devmem2 install
  231 |   shell: 'find / -name devmem2'
  232 |   register: devmem_check
  233 |   ignore_errors: yes
  234 | 
  235 | - name: Showing if devmem2 is valid or if we need to compiler
  236 |   debug:
  237 |     msg: "Were loading to compile devmem2 as its absent" 
  238 |   when: (connectbox_os != "raspbian") and (devmem_check.stdout.find("devmem2") <= 0)
  239 | 
  240 | - name: If were bullseye/buster on NEO or OZ2 then we need to compile devmem2
  241 |   command: wget https://bootlin.com/pub/mirror/devmem2.c
  242 |   args:
  243 |     chdir: /home
  244 |   when: (devmem_check.stdout.find("devmem2") <= 0) and (connectbox_os != 'raspbian')
  245 | 
  246 | - name: get the compiler we need
  247 |   apt:
  248 |     name: gcc
  249 |     state: present
  250 |   when: (devmem_check.stdout.find("devmem2") <= 0) and (connectbox_os != 'raspbian')
  251 | 
  252 | - name: compile the devmem2 utility placing the output into /usr/bin
  253 |   command: gcc -o /usr/bin/devmem2 /home/devmem2.c
  254 |   register: command_result
  255 |   when: (devmem_check.stdout.find("devmem2") <= 0) and connectbox_os != 'raspbian'
  256 | 
  257 | 
  258 | - name: Install lower level of docutils == 0.16 for now
  259 |   pip:
  260 |     name: docutils==0.16
  261 |     virtualenv: "{{ hat_service_virtualenv_dir }}"
  262 | 
  263 | - name: Install smbus2 in raspbian
  264 |   pip:
  265 |     name: smbus2
  266 |     virtualenv: "{{ hat_service_virtualenv_dir }}"
  267 |   when: connectbox_os == "raspbian" 
  268 | 
  269 | - name: Install OPi.GPIO for RM3
  270 |   pip:
  271 |     name: OPi.GPIO
  272 |     virtualenv: "{{ hat_service_virtualenv_dir }}"
  273 |   when: connectbox_os == "debian" 
  274 | 
  275 | - name: Make radxa directory
  276 |   file:
  277 |     path: "{{ hat_service_virtualenv_dir }}/lib/{{ python_ver }}/site-packages/radxa"
  278 |     state: directory  
  279 | 
  280 | - name: copy CM3.py
  281 |   copy:
  282 |    src: radxa_CM3.py
  283 |    dest: "{{ hat_service_virtualenv_dir }}/lib/{{ python_ver }}/site-packages/radxa/CM3.py"
  284 |   when: connectbox_os == "debian"
  285 | 
  286 | - name: copy __init__.py to radxa
  287 |   copy:
  288 |    src: radxa___init__.py
  289 |    dest: "{{ hat_service_virtualenv_dir }}/lib/{{ python_ver }}/site-packages/radxa/__init__.py"
  290 |   when: connectbox_os == "debian"
  291 | 
  292 | 
  293 | 
  294 | 
  295 | # GPIO Version selection begins here....
  296 | - name: set fact for RPi_GPIO_path
  297 |   set_fact:
  298 |     RPi_GPIO_path: "{{ hat_service_virtualenv_dir }}/lib/{{ python_ver }}/site-packages/RPi.GPIO"
  299 |  
  300 | # Install RPi.GPIO_NP_CB as RPi.GPIO for NEO compiling of RPi.GPIO
  301 | # note that this was done in the ansible/group_var/all file
  302 | 
  303 | - name: get the status of OZ2_present 
  304 |   set_fact:
  305 |     OZ2_present: "{{ hostvars[inventory_hostname]['OZ2_present'] }}"
  306 | 
  307 | - name: output the OZ2 variable
  308 |   debug:
  309 |     msg: "The OZ2_present status is {{ OZ2_present }}"
  310 | 
  311 | - name: set path to Opi.GPIO (Orange Pi Zero2) for compiling RPi.GPIO
  312 |   set_fact:
  313 |     hat_services_repo: '{{ oz2_services_repo }}'
  314 |   when: connectbox_os != 'raspbian' and OZ2_present
  315 | 
  316 | # Hat Services Repo for NEO is set in ansible/group_vars/all by default
  317 | 
  318 | - name: Clone the RPi.GPIO_NP_CB or OrangePi.GPIO repo or RPI.GPIO to battery venv (NEO)
  319 |   debug:
  320 |     msg: "the cloned directory is: {{ hat_services_repo }} to: {{ RPi_GPIO_path }}"
  321 | 
  322 | - name: Output the path for RPI_GPIO
  323 |   debug:
  324 |     msg: "The path for RPi_GPIO is: {{ RPi_GPIO_path }}"
  325 | 
  326 | 
  327 | ## For NEO or OPi we must download the source and manually compile here
  328 | - name: clone the repo for compile
  329 |   git: 
  330 |     repo: "{{ hat_services_repo }}"
  331 |     dest: "{{ RPi_GPIO_path }}"
  332 |     clone: yes
  333 |     update: yes
  334 |     force: yes
  335 |   ignore_errors: yes
  336 |   when: (connectbox_os != "raspbian") and (connectbox_os != "debian")
  337 | 
  338 | - name: check for setup.python
  339 |   stat:
  340 |     path: "{{ RPi_GPIO_path }}/setup.py"
  341 |   register: setup_file_exists
  342 |   
  343 | # new RPi_GPIO handles the pull down service for these pins where it did not in focal
  344 | # The command must include the path to the virtual environment version of python3 or the resulting
  345 | #  library will be installed in usr/local/lib/python3.8/dist-packages rather than the desired
  346 | #  location of /usr/local/connectbox/battery_tool_venv/lib/python3.8/site-packages 
  347 | - name: Run setup.py to build RPi.GPIO (NEO) or (OZ2)
  348 |   command: "{{ hat_service_virtualenv_dir }}/bin/python3 setup.py install"
  349 |   args:
  350 |     chdir: "{{ RPi_GPIO_path }}"
  351 |   register: compile_out
  352 |   when: (connectbox_os != "raspbian") and (connectbox_os != "debian") and (setup_file_exists.stat.exists)   # it will not exist if we have come through here already
  353 | 
  354 | - name: show results of compile if it failed 
  355 |   debug:
  356 |     msg: compile_out.stdout
  357 |   when: (connectbox_os != "raspbian") and (connectbox_os != "debian") and (setup_file_exists.stat.exists) and compile_out.rc
  358 | 
  359 | 
  360 | # if we are ARE raspian OR debian, we will just install the correct RPi.GPIO
  361 | - name: Install RPi.GPIO for Buster buildcd 
  362 |   command: "{{ hat_service_virtualenv_dir }}/bin/pip3 install RPi.GPIO==0.7.0"
  363 |   when: OS_Version  == 'buster' and (connectbox_os == 'raspbian' or connectbox_os == 'debian')
  364 | 
  365 | - name: Install RPi.GPIO for Bullseye build
  366 |   command: "{{ hat_service_virtualenv_dir }}/bin/pip3 install RPi.GPIO==0.7.1"
  367 |   when: OS_Version == 'bullseye' and (connectbox_os == 'raspbian' or connectbox_os == 'debian')
  368 | 
  369 | 
  370 | 
  371 | # With RPi.GPIO installed, we can now install the luma.core and luma.oled modules
  372 | #  which will use the installed RPi.GPIO 
  373 | - name: Install luma.oled in hat service virtualenv
  374 |   command: "{{ hat_service_virtualenv_dir }}/bin/pip3 install luma.oled==2.4.1"
  375 | 
  376 | - name: Copy neo battery shutdown systemd service definition
  377 |   template:
  378 |     src: "{{ hat_service_name }}.j2"
  379 |     dest: "/etc/systemd/system/{{ hat_service_name }}"
  380 |     mode: 0644
  381 |     owner: root
  382 |     group: root
  383 |     
  384 | - name: Load final elements libjpeg-dev
  385 |   apt:
  386 |     name: "libjpeg-dev"
  387 |     state: present
  388 |   notify:
  389 |      - "restart neo battery shutdown service"
  390 |   when: OS_Version  != 'bullseye'
  391 | 
  392 | - name: Load final elements libjpeg62-turbo-dev
  393 |   apt:
  394 |     name: "libjpeg62-turbo-dev"
  395 |     state: present
  396 |   notify:
  397 |      - "restart neo battery shutdown service"
  398 |   when: OS_Version == 'bullseye'
  399 | 
  400 | - name: Remove Extra files
  401 |   debug: 
  402 |     msg: "remove build and files and get rigd of gcc"
  403 | 
  404 | - name: Copy displays.py with animated wait page support
  405 |   copy:
  406 |     src: neo-batterylevelshutdown/displays.py
  407 |     dest: "{{ hat_service_virtualenv_dir }}/lib/{{ python_ver }}/site-packages/neo_batterylevelshutdown/displays.py"
  408 |     mode: 0644
  409 | 
  410 | - name: Copy page_display_image.py with left-aligned text for wait frames
  411 |   copy:
  412 |     src: neo-batterylevelshutdown/page_display_image.py
  413 |     dest: "{{ hat_service_virtualenv_dir }}/lib/{{ python_ver }}/site-packages/neo_batterylevelshutdown/page_display_image.py"
  414 |     mode: 0644
  415 | 
  416 | - name: Copy wait frame images for OLED animation
  417 |   copy:
  418 |     src: "assets/{{ item }}"
  419 |     dest: "{{ hat_service_virtualenv_dir }}/lib/{{ python_ver }}/site-packages/neo_batterylevelshutdown/assets/{{ item }}"
  420 |     mode: 0644
  421 |   loop:
  422 |     - wait.png
  423 |     - wait0.png
  424 |     - wait1.png
  425 |     - wait2.png
  426 |     - wait3.png
  427 |     - wait4.png
  428 |     - wait5.png
  429 |     - wait6.png
  430 |     - wait7.png
  431 | 
  432 | - name: Enable and restart NEO_BatteryLevelShutdown
  433 |   systemd:
  434 |     name: "{{ item }}"
  435 |     daemon_reload: yes
  436 |     enabled: yes
  437 |   with_items:
  438 |   - "{{ hat_service_name }}"
  439 | 
```
