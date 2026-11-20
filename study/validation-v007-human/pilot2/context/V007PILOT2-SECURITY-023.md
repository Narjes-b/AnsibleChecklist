# Frozen source context: V007PILOT2-SECURITY-023

- Repository: `ConnectBox/connectbox-pi`
- Commit: `e69eabdecfa2e39b2751acdb928bfafb2f8f28f6`
- Family: security
- Rule: `ansibleguard/insecure-permissions`
- Codebook: `codebooks-v2/FAMILY_SECURITY_V2.md`
- Source: `ansible/roles/bootstrap/tasks/main.yml` (reported anchor line 760)
- Flagged construct: not named by the finding; the anchor line 760 lies in the task at line 760, name `Install systemd for PxUSBm`.
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 660–860 of 1115:

```text
  660 | - name: Create the /usr/local/connectbox/bin directory
  661 |   file:
  662 |     path: /usr/local/connectbox/bin
  663 |     state: directory
  664 | 
  665 | - name: Install CreateLogFiles.sh  
  666 |   copy: 
  667 |     src: usr_local_connectbox_bin_CreateLogFiles.sh
  668 |     dest: /usr/local/connectbox/bin/CreateLogFiles.sh
  669 | 
  670 | - name: Create connectbox group
  671 |   group:
  672 |     name: _connectbox
  673 |     system: yes
  674 | 
  675 | # Not strictly necessary but can be used for testing
  676 | - name: Create _connectbox user and to _connectbox group
  677 |   user:
  678 |     name: _connectbox
  679 |     group: _connectbox
  680 |     system: yes
  681 |     createhome: no
  682 | 
  683 | - name: Install PxUSBm.py 
  684 |   copy:
  685 |     src: usr_local_connectbox_bin_PxUSBm.py 
  686 |     dest: /usr/local/connectbox/bin/PxUSBm.py
  687 |     owner: _connectbox
  688 |     group: _connectbox
  689 |     mode: 0555
  690 | 
  691 | - name: Install indexer.py
  692 |   copy:
  693 |     src: usr_local_connectbox_bin_indexer.py
  694 |     dest: /usr/local/connectbox/bin/indexer.py
  695 |     owner: _connectbox
  696 |     group: _connectbox
  697 |     mode: 0555
  698 | 
  699 | - name: Install mmiLoader.py
  700 |   copy:
  701 |     src: usr_local_connectbox_bin_mmiLoader.py
  702 |     dest: /usr/local/connectbox/bin/mmiLoader.py
  703 |     owner: _connectbox
  704 |     group: _connectbox
  705 |     mode: 0555
  706 | 
  707 | - name: Install usb_mounter.py
  708 |   copy:
  709 |     src: usr_local_connectbox_bin_usb_mounter.py
  710 |     dest: /usr/local/connectbox/bin/usb_mounter.py
  711 |     owner: _connectbox
  712 |     group: _connectbox
  713 |     mode: 0555
  714 | 
  715 | - name: Change the permissions of PxUSBm.py 
  716 |   command: chmod 644 /usr/local/connectbox/bin/PxUSBm.py 
  717 | 
  718 | - name: Install Macchanger
  719 |   apt:
  720 |     name: macchanger
  721 |     state: present 
  722 | 
  723 | - name: copy over configuration files 
  724 |   copy:
  725 |     src: etc_macchanger_ifupdown.sh
  726 |     dest: /etc/macchange/
  727 |     owner: root 
  728 |     group: root 
  729 |     mode: 0644  
  730 | 
  731 | - name: copy over the default interfaces macchanger affects
  732 |   copy:
  733 |     src: etc_default_macchanger
  734 |     dest: /etc/default/macchanger
  735 |     owner: root 
  736 |     group: root 
  737 |     mode: 0644
  738 | 
  739 | - name: remove the if-pre-up.d/macchanger file
  740 |   file:
  741 |     path: /etc/network/if-pre-up.d/macchanger
  742 |     state: absent    
  743 |     
  744 | - name: Install shutdown.sh 
  745 |   copy:
  746 |     src: usr_local_connectbox_bin_shutdown.sh 
  747 |     dest: /usr/local/connectbox/bin/shutdown.sh
  748 |     owner: _connectbox
  749 |     group: _connectbox
  750 |     mode: 0755
  751 | 
  752 | - name: Install shutdownShell.sh 
  753 |   copy:
  754 |     src: usr_local_connectbox_bin_shutdownShell.sh 
  755 |     dest: /usr/local/connectbox/bin/shutdownShell.sh
  756 |     owner: _connectbox
  757 |     group: _connectbox
  758 |     mode: 0655
  759 | 
  760 | - name: Install systemd for PxUSBm 
  761 |   copy:
  762 |     src: etc_systemd_system_PxUSBm.service
  763 |     dest: /etc/systemd/system/PxUSBm.service
  764 |     owner: root 
  765 |     group: root 
  766 |     mode: 0622
  767 | 
  768 | - name: make poweroff directory
  769 |   file:
  770 |     state: directory
  771 |     path: /usr/local/bin/poweroff
  772 |     mode: 0655
  773 | 
  774 | - name: copy content to poweroff
  775 |   copy:
  776 |     src: usr_local_bin_poweroff_poweroff
  777 |     dest: /usr/local/bin/poweroff/poweroff
  778 |     mode: 0755
  779 | 
  780 | - name: copy extra poweroff filesystem
  781 |   copy:
  782 |     src: usr_local_poweroff_internal
  783 |     dest: /usr/local/bin/poweroff/_internal 
  784 |     mode: 0655
  785 | 
  786 | - name: enable the PxUSBm service 
  787 |   command: systemctl enable PxUSBm.service 
  788 | 
  789 | - name: Make connectbox directory
  790 |   file:
  791 |     state: directory
  792 |     path: /usr/local/connectbox
  793 |     mode: 0655
  794 | 
  795 | - name: Install PIP
  796 |   apt:
  797 |     name: python-pip
  798 |     state: present
  799 |   ignore_errors: yes
  800 | 
  801 | - name: Install PIP3
  802 |   apt:
  803 |     name: python3-pip
  804 |     state: present
  805 |   ignore_errors: yes
  806 | 
  807 | - name: set up resize of filesystem
  808 |   debug:
  809 |     msg: Setting up resize of filesystem
  810 |   notify:
  811 |     - Install PxUSBm.py
  812 |   changed_when: True
  813 | 
  814 | - name: install pexpect (needed for PxUSBm.py script)
  815 |   pip:
  816 |     name: pexpect
  817 | 
  818 | - name: Add items to rc.local
  819 |   blockinfile:
  820 |     path: /etc/rc.local
  821 |     insertafter: "# By default this script does nothing."
  822 |     block: |
  823 |       # Create missing log files and restart nginx service
  824 |       #  we need this or nginx won't run
  825 |         sh /usr/local/connectbox/bin/CreateLogFiles.sh
  826 |   when: not aws_instance and not OZ2_present
  827 | 
  828 | 
  829 | - name: Add items to rc.local
  830 |   blockinfile:
  831 |     path: /etc/rc.local
  832 |     insertafter: "# By default this script does nothing."
  833 |     block: |
  834 |       # Create missing log files and restart nginx service
  835 |       #  we need this or nginx won't run
  836 |         sh /usr/local/connectbox/bin/CreateLogFiles.sh 
  837 |       # Change the way the LED's work on the OrangePi Zero2
  838 |         echo 'mmc0' > /sys/class/leds/red\:power/trigger
  839 |         echo 'activity' > /sys/class/leds/green\:status/trigger
  840 |   when: not aws_instance and OZ2_present
  841 | 
  842 | # Moved over from connectbox/tasks/main.yml by Derek Maxson 20220129
  843 | #   So that we have access to the scripts during startup
  844 | #
  845 | 
  846 | - name: Configure hostname
  847 |   copy:
  848 |     content: "{{ connectbox_default_hostname }}\n"
  849 |     dest: /etc/hostname
  850 | 
  851 | - name: Add hosts entry
  852 |   blockinfile:
  853 |     dest: /etc/hosts
  854 |     block: |
  855 |       127.0.0.1  {{ connectbox_default_hostname }}
  856 |       127.0.0.1  learn.{{ connectbox_default_hostname }}
  857 | 
  858 | - name: Create connectbox version file
  859 |   copy:
  860 |     content: "{{ connectbox_version }}\n"
```

The file is larger than the inline limit; only a window of ±100 lines around the anchor is included. If that prevents a defensible decision, label the item unreviewable (bundle-defect).
