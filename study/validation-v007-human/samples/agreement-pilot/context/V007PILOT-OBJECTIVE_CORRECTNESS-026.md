# Frozen source context: V007PILOT-OBJECTIVE_CORRECTNESS-026

- Repository: `adoptium/infrastructure`
- Commit: `d31f47293b3a0166a4f9d7b8c51475d548999408`
- Family: Objective correctness
- Rule: `ansibleguard/non-idempotent-command`
- Codebook: `codebooks/FAMILY_OBJECTIVE_CORRECTNESS.md`
- Source: `ansible/playbooks/AdoptOpenJDK_Unix_Playbook/roles/CentOS6-Cent7SSL/tasks/main.yml` (reported anchor line 28)
- Object: `source_location` `f260be141238b27032b11bfa8561dcfa4d7e5b6028159f32c46bb182e40ef7a1`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–149 of 149:

```text
    1 | ---
    2 | ##################################################################
    3 | # Install OpenSSL 1.0.2 and certificates bundle from CentOS7     #
    4 | # Need for CentOS6 to accept LetsEncrypt certs via Python/wget   #
    5 | # Based on https://forums.centos.org/viewtopic.php?f=13&p=328731 #
    6 | # Ref: https://github.com/adoptium/infrastructure/issues/2342    #
    7 | ##################################################################
    8 | 
    9 | - name: Check version of ca-certificates package on the system ...
   10 |   shell: rpm -q ca-certificates | grep -E 'ca-certificates.2020|ca-certificates.201' warn=no
   11 |   register: cacertsold
   12 |   changed_when: false
   13 |   failed_when: false
   14 | 
   15 | - name: Install prereqs for building openssl
   16 |   yum:
   17 |     name:
   18 |       - krb5-devel
   19 |       - zlib-devel
   20 |       - lksctp-tools-devel
   21 |       - util-linux # Only for /usr/bin/rename
   22 |       - make
   23 |       - gcc
   24 |       - rpm-build
   25 |     state: present
   26 |   when: cacertsold.rc == 0
   27 | 
   28 | - name: Download CentOS7 OpenSSL 1.0.2k SRPM ...
   29 |   shell: curl -O https://vault.centos.org/7.9.2009/updates/Source/SPackages/openssl-1.0.2k-21.el7_9.src.rpm warn=False
   30 | 
   31 | - name: Verify checksum for CentOS7 OpenSSL 1.0.2k SRPM
   32 |   shell: sha256sum  openssl-1.0.2k-21.el7_9.src.rpm | grep ^6dd850b2be01ff85c500428461019566984d91d7ad8d0002885d33ea37546da4
   33 |   when: cacertsold.rc == 0
   34 |   changed_when: false
   35 | 
   36 | # Invoking rpm as ansible yum module skips due to non-source RPM presence
   37 | - name: Install CentOS7 OpenSSL 1.0.2k SRPM ...
   38 |   shell: rpm -ivh openssl-1.0.2k-21.el7_9.src.rpm
   39 |   when: cacertsold.rc == 0
   40 | 
   41 | # Not using ansible operations as the don't take wildcards hence warn=False
   42 | # Could explicitly list the ones I know match it I guess
   43 | - name: Apply CentOS patches to OpenSSL Source (Part 1) ...
   44 |   shell: sed -i 's/secure_getenv(/getenv(/g' /root/rpmbuild/SOURCES/*patch warn=False
   45 |   when: cacertsold.rc == 0
   46 | 
   47 | - name: Apply CentOS patches to OpenSSL Source (Part 2) ...
   48 |   lineinfile:
   49 |     path: /root/rpmbuild/SPECS/openssl.spec
   50 |     regexp: '%patch68 -p1 -b .secure-getenv'
   51 |     line: '#%patch68 -p1 -b .secure-getenv'
   52 |   when: cacertsold.rc == 0
   53 | 
   54 | # Need To Regenerate The SMIME Test certificates
   55 | # Due To Coding In The Generator Script, Need To Include The CHDIRS :(
   56 | # Also Need To Seperate The Compile From The Testing
   57 | 
   58 | - name: Update Spec File To Seperate App Build Target From Test Targets ...
   59 |   lineinfile:
   60 |     path: /root/rpmbuild/SPECS/openssl.spec
   61 |     regexp: 'make -C test apps tests'
   62 |     line: 'make -C apps'
   63 |   when: cacertsold.rc == 0
   64 | 
   65 | - name: Update Spec File To Regenerate SMIME Test Certificates And Run Tests ...
   66 |   lineinfile:
   67 |     path: /root/rpmbuild/SPECS/openssl.spec
   68 |     regexp: './openssl-thread-test --threads %{thread_test_threads}'
   69 |     backrefs: yes
   70 |     state: present
   71 |     line: |
   72 |       ./openssl-thread-test --threads %{thread_test_threads}
   73 |       cd test/smime-certs/
   74 |       chmod 755 ./mksmime-certs.sh
   75 |       ./mksmime-certs.sh
   76 |       cd ../..
   77 |       make -C test tests
   78 |         %{__cc} -o openssl-thread-test \
   79 |         `krb5-config --cflags` \
   80 |         -I./include \
   81 |         $RPM_OPT_FLAGS \
   82 |         %{SOURCE8} \
   83 |         -L. \
   84 |         -lssl -lcrypto \
   85 |         `krb5-config --libs` \
   86 |         -lpthread -lz -ldl
   87 |       ./openssl-thread-test --threads %{thread_test_threads}
   88 |   when: cacertsold.rc == 0
   89 | 
   90 | - name: Build OpenSSL 1.0.2k with rpmbuild ...
   91 |   shell: cd /root/rpmbuild/SPECS && rpmbuild -bb openssl.spec
   92 |   when: cacertsold.rc == 0
   93 | 
   94 | - name: Install new OpenSSL 1.0.2k, libs and development package ...
   95 |   shell: "rpm -U openssl-1.0.2k-21.el6.x86_64.rpm openssl-libs-1.0.2k-21.el6.x86_64.rpm openssl-devel-1.0.2k-21.el6.x86_64.rpm"
   96 |   args:
   97 |     chdir: /root/rpmbuild/RPMS/x86_64/
   98 |   when: cacertsold.rc == 0
   99 | 
  100 | - name: Install prereqs for building ca-certificate bundle ...
  101 |   yum:
  102 |     name:
  103 |       - asciidoc
  104 |       - java-1.6.0-openjdk      # Explicit build dep of ca-certificates SRPM
  105 |     state: present
  106 |   when: cacertsold.rc == 0
  107 | 
  108 | - name: Download CentOS6 ca-certificates SRPM ...
  109 |   shell: curl -O https://vault.centos.org/6.10/updates/Source/SPackages/ca-certificates-2020.2.41-65.1.el6_10.src.rpm
  110 | 
  111 | - name: Verify checksum for CentOS6 ca-certificates download ...
  112 |   shell: sha256sum ca-certificates-2020.2.41-65.1.el6_10.src.rpm | grep ^85326e70da937c09d342612190d23d3501a2a46954d2e197f9d343bf060ca000
  113 |   when: cacertsold.rc == 0
  114 |   changed_when: false
  115 | 
  116 | # Invoking rpm as ansible yum module skips due to non-source RPM presence
  117 | - name: Install CentOS6 ca-certificates SRPM ...
  118 |   shell: rpm -ivh ca-certificates-2020.2.41-65.1.el6_10.src.rpm warn=False
  119 |   when: cacertsold.rc == 0
  120 | 
  121 | - name: Download new CentOS7 ca-certificates SRPM ...
  122 |   shell: curl -o ca-certificates-2021.2.50-72.el7_9.src.rpm https://vault.centos.org/7.9.2009/updates/Source/SPackages/ca-certificates-2021.2.50-72.el7_9.src.rpm
  123 |   when: cacertsold.rc == 0
  124 | 
  125 | - name: Verify checksum for CentOS7 ca-certificates  download ...
  126 |   shell: sha256sum  ca-certificates-2021.2.50-72.el7_9.src.rpm | grep ^86fe6df26e7612e63a70e435786f2eb6587cb00e6f9927aea113797afacebb57
  127 |   when: cacertsold.rc == 0
  128 |   changed_when: false
  129 | 
  130 | - name: Extract certdata.txt from CentOS7 ca-certificates SRPM ...
  131 |   shell: rpm2cpio ca-certificates-2021.2.50-72.el7_9.src.rpm | (cd /root/rpmbuild/SOURCES && cpio -idmv certdata.txt)
  132 |   when: cacertsold.rc == 0
  133 | 
  134 | - name: Edit version number in the ca-certificates spec ...
  135 |   lineinfile:
  136 |     path: /root/rpmbuild/SPECS/ca-certificates.spec
  137 |     regexp: 'Version: 2020.2.41'
  138 |     line: 'Version: 2021.2.50'
  139 |   when: cacertsold.rc == 0
  140 | 
  141 | - name: Rebuild later ca-certificates (2021.2.50-72.el7_9) with rpmbuild ...
  142 |   shell: cd /root/rpmbuild/SPECS && rpmbuild -bb ca-certificates.spec
  143 |   when: cacertsold.rc == 0
  144 | 
  145 | - name: Install CentOS6 ca-certificates SRPM ...
  146 |   yum:
  147 |     name: /root/rpmbuild/RPMS/noarch/ca-certificates-2021.2.50-65.1.el6.noarch.rpm
  148 |     state: present
  149 |   when: cacertsold.rc == 0
```
