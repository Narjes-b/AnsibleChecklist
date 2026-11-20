# Frozen source context: V007PILOT2-MAINTAINABILITY_COMPLEXITY-022

- Repository: `ConnectBox/connectbox-pi`
- Commit: `e69eabdecfa2e39b2751acdb928bfafb2f8f28f6`
- Family: maintainability_complexity
- Rule: `ansibleguard/shell-instead-of-module`
- Codebook: `codebooks-v2/FAMILY_MAINTAINABILITY_V2.md`
- Source: `ansible/roles/bootstrap/tasks/main.yml` (reported anchor line 436)
- Flagged construct: task `restart dns services if were on ubuntu debian focal`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 336–536 of 1115:

```text
  336 |      state: directory
  337 |      mode: '0755'
  338 |   ignore_errors: yes
  339 |   when: connectbox_os == 'armbian' and (OS_Version == 'xenial' or OS_Version == 'focal') and not OZ2_present
  340 | 
  341 | - name: copy service file over
  342 |   template:
  343 |      src: 10-switch-role.conf.j2
  344 |      dest: /etc/systemd/system/[REDACTED_EMAIL]/10-switch-role.conf
  345 |      mode: '0666'
  346 |   when: connectbox_os == 'armbian' and (OS_Version == 'xenial' or OS_Version == 'focal') and not OZ2_present
  347 | 
  348 | - name: setup link for ttyGS0 service
  349 |   file:
  350 |      src: /lib/systemd/system/serial-getty@.service
  351 |      dest: /etc/systemd/system/getty.target.wants/[REDACTED_EMAIL]
  352 |      state: link
  353 |   when: (connectbox_os == 'armbian' and (OS_Version == 'xenial' or OS_Version == 'focal') and not OZ2_present)
  354 |      
  355 | - name: add it to default load of modules
  356 |   command: echo 'g_serial' >> /etc/modules
  357 |   when: connectbox_os == 'armbian' and (OS_Version == 'xenial' or OS_Version == 'focal') and not OZ2_present
  358 | 
  359 | - name: make sure we  delete the g_mass_storage.conf if it exsists
  360 |   file:
  361 |     path: /etc/modules-load.d/g_mass_storage.conf
  362 |     state: absent
  363 | 
  364 | - name: Enable 10/100baseT on CM4
  365 |   copy:
  366 |     src: ethtool
  367 |     dest: /etc/network/if-pre-up.d/ethtool
  368 |   when: CM4_present
  369 | 
  370 | - name: print out reboot status
  371 |   debug:
  372 |     msg: "Reboot status is: {{ reboot_required }} "
  373 | 
  374 | - name: confirm reboot_required
  375 |   pause:
  376 |     prompt: "Are you sure you want to reboot (yes/no)? Note you need to reboot at least one time going through this loop: "
  377 |   register: confirm_reboot
  378 |    
  379 | # The system takes 5-10 seconds to disappear from the network
  380 | #  so let's wait 15 seconds before doing our first check
  381 | #  Use newer ansible 2.7 function reboot
  382 | 
  383 | - name: Reboot device for changes to take effect
  384 |   reboot:
  385 |     post_reboot_delay: 35
  386 |     connect_timeout: 90
  387 |     reboot_timeout: 120
  388 |   when: (reboot_required and (confirm_reboot.user_input | bool)) or (confirm_reboot.user_input | bool)
  389 |   tags: reboot1
  390 | 
  391 | - name: Install PHP if this is an OrangePi Zero2 
  392 |   apt:
  393 |     name: php
  394 |     state: present 
  395 |   when: OZ2_present
  396 | 
  397 | - name: Copy over a new dnsmasq file if were on ubuntu debian focal
  398 |   copy: 
  399 |     src: dnsmasq.conf
  400 |     dest: /etc/dnsmasq.conf
  401 |   when: (OS_Version == 'focal') and  ( ansible_os_family|lower == 'debian') and (connectbox_os == 'ubuntu') and not OZ2_present
  402 | 
  403 | 
  404 | - name: Install fdisk 
  405 |   apt:
  406 |     name: fdisk
  407 |     state: present
  408 | 
  409 | - name: Install crda 
  410 |   apt:
  411 |     name: crda    
  412 |     state: present
  413 | 
  414 | - name: Copy over the ATTiny.bat file
  415 |   copy:
  416 |     src: ATTiny.bat
  417 |     dest: /usr/bin/ATTiny.bat 
  418 |   when: CM4_present
  419 | 
  420 | - name: make ATTiny.bat executable
  421 |   command: chmod +x /usr/bin/ATTiny.bat 
  422 |   when: CM4_present
  423 | 
  424 | - name: copy over a new avahi-daemon.conf
  425 |   copy:
  426 |    src: etc_avahi_avahi-daemon.conf
  427 |    dest: /etc/avahi/avahi-daemon.conf
  428 |   when: OZ2_present and OS_Version == "focal"
  429 | 
  430 | - name: Copy over the default hostapd if were on ubuntu Debian
  431 |   copy:
  432 |     src: etc_default_hostapd
  433 |     dest: /etc/default/hostapd
  434 |   when: (ansible_os_family|lower == 'debian') and (connectbox_os == "ubuntu")
  435 | 
  436 | - name: Restart dns services if were on Ubuntu Debian focal
  437 |   command: systemctl restart dnsmasq
  438 |   when: (OS_Version == 'focal') and  (ansible_os_family|lower == 'debian') and (connectbox_os == 'ubuntu') 
  439 | 
  440 | - name : Increase size of /tmp to handle upcoming installs
  441 |   command: mount -o remount,size=400M /tmp/
  442 |   when: (ansible_os_family  == 'Ubuntu' or connectbox_os == 'armbian') and not aws_instance
  443 | 
  444 | - name: Get current rfkill state for interface 0 (wireless LAN) on Raspbian
  445 |   command: cat /sys/class/rfkill/rfkill0/soft
  446 |   register: rfkill0_state
  447 |   ignore_errors: yes
  448 |   changed_when: False
  449 |   when: ansible_os_family == 'Ubuntu' and not aws_instance
  450 | 
  451 | # Raspbian-lite buster and onwards rfkill wlan0 by default, which causes
  452 | #  problems when we try to start wlan0 (at hostapd reload)
  453 | # This change persists across reboots, so it's safe to do here.
  454 | - name: Unblock rfkill'ed interface 0 (wireless LAN) on Raspbian
  455 |   command: /usr/sbin/rfkill unblock 0
  456 |   ignore_errors: yes
  457 |   when:  ansible_os_family  == 'Debian'
  458 | 
  459 | - name: Get current rfkill state for interface 1 (wireless LAN) on Raspbian
  460 |   command: cat /sys/class/rfkill/rfkill1/soft
  461 |   register: rfkill1_state
  462 |   ignore_errors: yes
  463 |   changed_when: False
  464 |   when: connectbox_os == 'Debian'
  465 | 
  466 | - name: load lshw if not installed
  467 |   apt:
  468 |     name: lshw
  469 |     state: present
  470 |   
  471 | - name: load usbutils if not installed
  472 |   apt:
  473 |     name: usbutils
  474 |     state: present
  475 | 
  476 | - name: load NTFS file system
  477 |   apt:
  478 |     name: ntfs-3g
  479 |     state: present 
  480 | 
  481 | # Raspbian-lite buster and onwards rfkill wlan1 by default, which causes
  482 | #  problems when we try to start wlan1 (at hostapd reload)
  483 | # This change persists across reboots, so it's safe to do here.
  484 | - name: Unblock rfkill'ed interface 1 (wireless LAN) on Raspbian
  485 |   command: /usr/sbin/rfkill unblock 1
  486 |   ignore_errors: yes
  487 |   when: connectbox_os == 'Debian'
  488 | 
  489 | - name: Set default locale
  490 |   lineinfile:
  491 |     path: /etc/default/locale
  492 |     line: LC_ALL=en_US.UTF-8
  493 |     state: present
  494 |   when: connectbox_os == 'armbian'
  495 | 
  496 | # Remove some systrem services for NEO
  497 | - name: Remove armbian-filesystem-resize since we do it in PxUSBm.py 
  498 |   shell: systemctl disable armbian-filesystem-resize
  499 |   ignore_errors: yes
  500 |   when: NEO_present
  501 | 
  502 | - name: Remove orangepi-resize-filesystem since we do it in PxUSBm.py
  503 |   shell: systemctl disable armbian-resize-filesystem.service
  504 |   ignore_errors: yes
  505 |   when: OZ2_present
  506 | 
  507 | # Remove the smart.service for NEO
  508 | - name: Remove smart.service for NEO 
  509 |   shell: systemctl disable smartd.service
  510 |   ignore_errors: yes
  511 |   when: connectbox_os != 'raspbian'
  512 | 
  513 | # Remove the smartmontools.service
  514 | - name: remove the smartmontools.service 
  515 |   shell: systemctl disable smartmontools.service 
  516 |   ignore_errors: yes
  517 |   when: connectbox_os != 'raspbian' or OZ2_present
  518 | 
  519 | #  Needed for package upgrades via ansible (aptitude safe-upgrade)
  520 | - name: Install apt
  521 |   apt:
  522 |     name: apt
  523 |     state: present
  524 | 
  525 | - name: Install jq so that ConnectBoxManage.sh can edit brand.txt easily
  526 |   apt:
  527 |     name: ['jq']
  528 |     state: present
  529 | 
  530 | # mikegleasonjr.firewall assumes iptables but Armbian doesn't ship with it
  531 | - name: Install iptables
  532 |   apt:
  533 |     name: iptables
  534 |     state: present
  535 |   when: connectbox_os == 'armbian'
  536 | 
```

The file is larger than the inline limit; only a window of ±100 lines around the anchor is included. If that prevents a defensible decision, label the item unreviewable (bundle-defect).
