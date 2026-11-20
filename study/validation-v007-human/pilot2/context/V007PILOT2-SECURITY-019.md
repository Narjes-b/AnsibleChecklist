# Frozen source context: V007PILOT2-SECURITY-019

- Repository: `gdcc/dataverse-ansible`
- Commit: `ae29ce65dd4cddd5187c2bc00aefd319b6bb4484`
- Family: security
- Rule: `ansibleguard/plaintext-sensitive-variable`
- Codebook: `codebooks-v2/FAMILY_SECURITY_V2.md`
- Source: `defaults/main.yml` (reported anchor line 375)
- Flagged construct: variable `minio.docker.secret_key`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–492 of 492:

```text
    1 | ---
    2 | # dataverse/defaults/main.yml
    3 | 
    4 | # un-nested so we can pass them at the CLI
    5 | dataverse_branch: release
    6 | dataverse_repo: https://github.com/IQSS/dataverse.git
    7 | # To use a dvinstall.zip from a different location than IQSS:
    8 | # dataverse_installer_url: https://example.com/path/to/dvinstall.zip
    9 | 
   10 | # set this to true for troubleshooting
   11 | any_errors_fatal: false
   12 | 
   13 | apache:
   14 |   enabled: true
   15 |   public_fqdn: 
   16 |   ssl:
   17 |     enabled: false
   18 |     remote_cert: false
   19 |     port: 443
   20 |     cert: 
   21 |     interm: 
   22 |     key: 
   23 |     pem:
   24 |       cert: 
   25 |       key: 
   26 |       interm: 
   27 |   port: 80
   28 |   use_ajp: true
   29 |   behind_reverse_proxy: false
   30 |   behind_ssl_reverse_proxy: false
   31 |   block:
   32 |     admin: true
   33 |     builtin_users: true
   34 |     destroy: true
   35 |     sword: false
   36 | 
   37 | letsencrypt:
   38 |   enabled: false
   39 |   certbot:
   40 |     autorenew: true
   41 |     email:
   42 |     user: certbot
   43 |     # Use the letsencrypt staging server for deployment tests
   44 |     # to avoid rate limiting:
   45 |     # https://letsencrypt.org/docs/duplicate-certificate-limit/
   46 |     test_cert: false
   47 | 
   48 | dataverse_misc_files_dir: '/opt/dv'
   49 | 
   50 | dataverse:
   51 |   adminpass: [REDACTED_LITERAL]
   52 |   allow_signups: true
   53 |   api:
   54 |     allow_lookup: false
   55 |     blocked_endpoints: "admin,builtin-users,test"
   56 |     blocked_policy: "localhost-only"
   57 |     location: "http://localhost:8080/api"
   58 |     test_suite: false
   59 |     # possible test values from https://github.com/IQSS/dataverse/blob/develop/conf/docker-aio/run-test-suite.sh#L11
   60 |     # beware DataversesIT and DatasetsIT at minimum must be run for any other tests to succeed. have fun.
   61 |     #tests: "DataversesIT,DatasetsIT,AdminIT"
   62 |     tests: default
   63 |   branding:
   64 |     enabled: false
   65 |     directory: "{{ playbook_dir }}/files/branding"
   66 |     favicons_directory: "{{ playbook_dir }}/files/favicons"
   67 |     fileSettings:
   68 |      - setting: HeaderCustomizationFile
   69 |        file: custom-header.html
   70 |      - setting: StyleCustomizationFile
   71 |        file: custom-stylesheet.css
   72 |      - setting: LogoCustomizationFile
   73 |        file: topbanner001w425_darkbg.png'
   74 |     otherSettings:
   75 |      - setting: FooterCopyright
   76 |        value: Your institute name here
   77 |   language:
   78 |     enabled: false # setting this to true allows the language task to run
   79 |     languages:
   80 |      - locale: en_US
   81 |        title: English
   82 |      - locale: de_DE
   83 |        title: Deutsch
   84 |     language_packs:
   85 |       source: https://github.com/GlobalDataverseCommunityConsortium/dataverse-language-packs.git
   86 |       version: develop
   87 |     lang_directory: "{{ dataverse_misc_files_dir }}/lang"
   88 |   licenses:
   89 |     enabled: false
   90 |     user: dataverseAdmin
   91 |     licenses:
   92 |      - name: CC0 1.0
   93 |        uri: http://creativecommons.org/publicdomain/zero/1.0
   94 |        shortDescription: Creative Commons CC0 1.0 Universal Public Domain Dedication.
   95 |        iconUrl: https://licensebuttons.net/p/zero/1.0/88x31.png
   96 |        active: true
   97 |        sortOrder: 1
   98 |      - name: CC BY 4.0
   99 |        uri: http://creativecommons.org/licenses/by/4.0
  100 |        shortDescription: Creative Commons Attribution 4.0 International License.
  101 |        iconUrl: https://licensebuttons.net/l/by/4.0/88x31.png
  102 |        active: true
  103 |        sortOrder: 2
  104 |      - name: CC BY-NC 4.0
  105 |        uri: http://creativecommons.org/licenses/by-nc/4.0
  106 |        shortDescription: Creative Commons Attribution-NonCommercial 4.0 International License.
  107 |        iconUrl: https://licensebuttons.net/l/by-nc/4.0/88x31.png
  108 |        active: true
  109 |        sortOrder: 3
  110 |      - name: CC BY-NC-ND 4.0
  111 |        uri: http://creativecommons.org/licenses/by-nc-nd/4.0
  112 |        shortDescription: Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License.
  113 |        iconUrl: https://licensebuttons.net/l/by-nc-nd/4.0/88x31.png
  114 |        active: true
  115 |        sortOrder: 4
  116 |      - name: CC BY-NC-SA 4.0
  117 |        uri: http://creativecommons.org/licenses/by-nc-sa/4.0
  118 |        shortDescription: Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
  119 |        iconUrl: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
  120 |        active: true
  121 |        sortOrder: 5
  122 |      - name: CC BY-ND 4.0
  123 |        uri: http://creativecommons.org/licenses/by-nd/4.0
  124 |        shortDescription: Creative Commons Attribution-NoDerivatives 4.0 International License.
  125 |        iconUrl: https://licensebuttons.net/l/by-nd/4.0/88x31.png
  126 |        active: true
  127 |        sortOrder: 6
  128 |      - name: CC BY-SA 4.0
  129 |        uri: http://creativecommons.org/licenses/by-sa/4.0
  130 |        shortDescription: Creative Commons Attribution-ShareAlike 4.0 International License.
  131 |        iconUrl: https://licensebuttons.net/l/by-sa/4.0/88x31.png
  132 |        active: true
  133 |        sortOrder: 7
  134 |   copyright: "Your Institution"
  135 |   counter:
  136 |     enabled: false
  137 |     #geoipdir: maxmind_geoip
  138 |     #geoipfile: GeoLite2-Country.mmdb
  139 |     hub_api_token: [REDACTED_LITERAL]
  140 |     hub_base_url: "https://api.datacite.org"
  141 |     machines_url: "https://raw.githubusercontent.com/CDLUC3/Make-Data-Count/master/user-agents/lists/machine.txt"
  142 |     maxmind_geoip_country_path: "maxmind_geoip/GeoLite2-Country.mmdb"
  143 |     output_file: "/dataverse/sushi_sample_logs"
  144 |     output_format: json
  145 |     platform: dash
  146 |     robots_url: "https://raw.githubusercontent.com/CDLUC3/Make-Data-Count/master/user-agents/lists/robot.txt"
  147 |     version: "0.1.04"
  148 |     upload_to_hub: False
  149 |     user: counter
  150 |     year_month: "2018-05"
  151 |   custom_metadata_blocks:
  152 |     enabled: false
  153 |     urls:
  154 |       - https://github.com/IQSS/dataverse/files/3744336/codemeta.tsv.txt
  155 |   default:
  156 |     config:
  157 |     storage_id: file
  158 |   demo: false
  159 |   pid:
  160 |     authority: "10.5072"
  161 |     protocol: doi
  162 |     shoulder: "FK2/"
  163 |   doi:
  164 |     baseurl: "https://mds.test.datacite.org/"
  165 |     dataciterestapiurl: "https://api.test.datacite.org"
  166 |     mdcbaseurl: "https://api.test.datacite.org/"
  167 |     provider: FAKE
  168 |     username: "testaccount"
  169 |     password: [REDACTED_LITERAL]
  170 |   ## Handlenet variables are only used if dataverse.pid.protocol is set to 'hdl'
  171 |   handlenet:
  172 |     independenthandleservice: 'false'
  173 | #   handleauthhandle: YOUR:HANDLE/USERNAME
  174 |     admcredfile: "{{ dataverse_misc_files_dir }}/admpriv.bin"
  175 |     admcredfile_source: files/handlenet/admcredfile
  176 | #   admprivphrase:
  177 | #   index: 300
  178 |   externaltools:
  179 |     datacurationtool:
  180 |       enabled: false
  181 |       method: demo
  182 |     dataexplorer:
  183 |       enabled: true
  184 |     wholetale:
  185 |       enabled: false
  186 |   ## The first item of 'filesdirs' is the default filestore
  187 |   ## If you change the label, be prepared to change the SQL database if there are already files here
  188 |   ## It is better practice to add a new data store and then migrate to it later
  189 |   ## Also, changing the default storage takes effect immediately for temp files, but
  190 |   ## only after restart for publishing (i.e. without restart the temp files will be moved to the old default data store at publish time).
  191 |   filesdirs:
  192 |     - label: file
  193 |       path: /usr/local/dvn/data
  194 | #   - label: label
  195 | #     path: /path/to/filestore   ## this is a sample entry for further file stores
  196 |   frontend:
  197 |     branch: develop
  198 |     enabled: false
  199 |     docroot:
  200 |       base: /var/www/html
  201 |       dir: spa
  202 |     nodejs:
  203 |       version: 18
  204 |     repo: "http://github.com/IQSS/dataverse-frontend"
  205 |     srcdir: /tmp/dataverse-frontend
  206 |   payara:
  207 |     user: dataverse
  208 |     group: dataverse
  209 |     domain: domain1
  210 |     logformat: ulf
  211 |     adminuser: admin
  212 |     adminpass: [REDACTED_LITERAL]
  213 |     siteurl:
  214 |     listen_address: 127.0.0.1
  215 |     launch_timeout: 180
  216 |     request_timeout: 1800
  217 |     root: /usr/local
  218 |     dir: payara7
  219 |     zipurl: https://nexus.payara.fish/repository/payara-community/fish/payara/distributions/payara/7.2026.2/payara-7.2026.2.zip
  220 |     zipchecksum: sha256:3495d025450f2b4263f7fc91014bea89db9de907ad516b675d4f47b00e1ad4de
  221 |   google_analytics_key:
  222 |   jacoco:
  223 |     enabled: false
  224 |     home: /tmp/jacoco
  225 |     version: 0.8.12
  226 |   file_fixity_checksum_algorithm: "MD5"
  227 |   memheap: 4096
  228 |   options:
  229 |     filepids: 
  230 |     maxfileuploadsizeinbytes:
  231 |     provcollectionenabled:
  232 |     tabularingestsizelimit: 
  233 |   previewers:
  234 |     enabled: true
  235 |     on_same_server: true
  236 |     zip_url: https://github.com/gdcc/dataverse-previewers/releases/download/1.2/dataverse-previewers-1.2.zip
  237 |     dir: /var/www/html
  238 |   sampledata:
  239 |     enabled: false
  240 |     dir: /tmp/sampledata
  241 |     repo: https://github.com/IQSS/dataverse-sample-data.git
  242 |     branch: master
  243 |     venv: /tmp/sampledata/venv
  244 |   custom_sampledata:
  245 |     enabled: false
  246 |     custom_sampledir: "{{ playbook_dir }}/custom_sampledata"
  247 |     custom_sampledatasets: "{{ playbook_dir }}/custom_sampledata/datasets"
  248 |     custom_sampledataverses: "{{ playbook_dir }}/custom_sampledata/dataverses"
  249 |     custom_sampleusers: "{{ playbook_dir }}/custom_sampledata/users"
  250 |     custom_samplefiles: "{{ playbook_dir }}/custom_sampledata/files"
  251 |   service_email: [REDACTED_EMAIL]
  252 |   smtp: localhost # or the FQDN of your organization's SMTP relay
  253 |   solr:
  254 |     download_url: https://archive.apache.org/dist/solr/solr/9.8.0/solr-9.8.0.tgz
  255 |     group: solr
  256 |     root: /usr/local/solr
  257 |     user: solr
  258 |     version: 9.8.0
  259 |     listen: 127.0.0.1
  260 |     checksum: sha256:9948dcf798c196b834c4cbb420d1ea5995479431669d266c33d46548b67e69e1
  261 |   srcdir: /opt/dataverse/dataverse
  262 |   thumbnails: false
  263 |   unittests:
  264 |     enabled: false
  265 |     argument: '-DcompilerArgument=-Xlint:unchecked test -P all-unit-tests'
  266 |   uploads_dir: /tmp
  267 |   usermgmtkey: burrito
  268 |   deployment:
  269 |     upgrade_only: false
  270 |   version: '6.11'
  271 | #  robots_txt_url: https://guides.dataverse.org/en/latest/_downloads/3a5cd7a283eecd5e93289e30af713554/robots.txt
  272 | 
  273 | build_guides: false
  274 | 
  275 | db:
  276 |   postgres:
  277 |     enabled: true
  278 |     adminpass: [REDACTED_LITERAL]
  279 |     name: dvndb
  280 |     host: localhost
  281 |     user: dvnuser
  282 |     pass: [REDACTED_LITERAL]
  283 |     jdbcurl: 
  284 |     log_lock_waits: true
  285 |     log_statements: none
  286 |     version: 16
  287 |     port: 5432
  288 |     query_counts: false
  289 |     replication:
  290 |       enabled: false
  291 |       # all servers must be defined so firewalls may be opened accordingly
  292 |       servers: 
  293 |         - 192.168.0.1
  294 |         - 192.168.0.2
  295 |       user: rep
  296 | #      pass: [REDACTED_LITERAL]
  297 |   backups:
  298 |     enabled: false
  299 |     rootdir: /opt/pg_backups
  300 |     backupdir: backups
  301 |     host: localhost
  302 |     user: postgres
  303 |     custom: 'yes'
  304 |     globals: 'no'
  305 |     plain: 'no'
  306 |   use_rds: false
  307 | 
  308 | docker:
  309 |   cidr: 10.0.0.99/24
  310 |   repo: https://download.docker.com/linux/centos/docker-ce.repo
  311 | 
  312 | grafana:
  313 |   grafana_user: 'admin'
  314 |   grafana_password: [REDACTED_LITERAL]
  315 | 
  316 | java:
  317 |   version: 21
  318 | java_home: /usr/lib/jvm/java-{{ java.version }}
  319 | 
  320 | localstack:
  321 |   enabled: false
  322 |   container_name: dev_localstack
  323 |   # set to /tmp/localstack/data to enable persistence
  324 |   data_dir: /tmp/localstack/data
  325 |   debug: true
  326 |   hostname_external: localstack
  327 |   port: 4566
  328 |   web_ui: 8888
  329 |   buckets:
  330 |     - label: LocalStack
  331 |       id: localstack1
  332 |       bucket_name: mybucket
  333 |       enabled: false
  334 |       access_key: [REDACTED_LITERAL]
  335 |       secret_access_key: [REDACTED_LITERAL]
  336 |       # for non-amazon services.
  337 |       custom_endpoint_url: "http://localhost:4566"
  338 |       # note: direct upload and download require CORS on the bucket
  339 |       download_redirect: true
  340 |       upload_redirect: true
  341 |       files_type: s3
  342 |       ingestsizelimit: 2000000000
  343 |       # for localstack this must be true
  344 |       path_style_access: true
  345 |       region: us-east-2
  346 |       url_expiration_minutes: 60
  347 |       payload_signing: false
  348 |       chunked_encoding: true
  349 | 
  350 | maven:
  351 |   version: 3.9.15
  352 | 
  353 | minio:
  354 |   enabled: false
  355 |   docker:
  356 |     version: "latest"
  357 |     service_name: "minio"
  358 |     network:
  359 |       name: "minio"
  360 |       external: false
  361 |     project_location: "/home/dataverse/minio"
  362 |     timezone: "America/New_York"
  363 |     user: dataverse
  364 |     group: dataverse
  365 |     server_port: 9000
  366 |     console_port: 9001
  367 |     root_user: "4cc355_k3y"
  368 |     root_password: [REDACTED_LITERAL]
  369 |     default_bucket: "mybucket"
  370 |     label: MinIO
  371 |     custom_endpoint_url: "http://localhost:9000"
  372 |     custom_endpoint_region: us-east-1
  373 |     path-style-access: true
  374 |     access_key: [REDACTED_LITERAL]
  375 |     secret_key: [REDACTED_LITERAL]
  376 | 
  377 | munin:
  378 |   install: false
  379 |   admin:
  380 |     user: admin
  381 |     passwd: [REDACTED_LITERAL]
  382 | 
  383 | postfix:
  384 |   enabled: true
  385 | 
  386 | prometheus:
  387 |   install: false
  388 |   node_exporter: https://github.com/prometheus/node_exporter/releases/download/v1.0.1/node_exporter-1.0.1.linux-amd64.tar.gz
  389 |   root: /usr/local/prometheus
  390 |   url: https://github.com/prometheus/prometheus/releases/download/v2.19.1/prometheus-2.19.1.linux-amd64.tar.gz
  391 |   user: prometheus
  392 | 
  393 | rserve:
  394 |   install: false
  395 |   host: localhost
  396 |   user: rserve
  397 |   group: rserve
  398 |   pass: [REDACTED_LITERAL]
  399 |   port: 6311
  400 |   workdir: /tmp/Rserv
  401 | 
  402 | s3:
  403 |   enabled: false
  404 |   access_key: [REDACTED_LITERAL]
  405 |   secret_access_key: [REDACTED_LITERAL]
  406 |   bucket_name: s3-test
  407 |   cors_already_set: false
  408 |   create_bucket: true
  409 |   # for non-amazon services. for localstack, you might set
  410 |   #custom_endpoint_url: "http://localhost:4572"
  411 |   custom_endpoint_url:
  412 |   # note: direct upload and download require CORS on the bucket
  413 |   download_redirect: true
  414 |   upload_redirect: true
  415 |   files_type: s3
  416 |   ingestsizelimit:
  417 |   label: s3-test
  418 |   # for localstack this must be true
  419 |   path_style_access: true
  420 |   region: us-east-1
  421 |   storage_driver_id: s3
  422 |   url_expiration_minutes: 60
  423 |   payload_signing: false
  424 |   chunked_encoding: true
  425 | 
  426 | schemaspy:
  427 |   enabled: false
  428 |   jarurl: https://github.com/schemaspy/schemaspy/releases/download/v6.1.0/schemaspy-6.1.0.jar
  429 | 
  430 | shibboleth:
  431 |   enabled: false
  432 |   email: TODO
  433 |   organizationName: TODO
  434 |   organizationalUnitName: TODO
  435 |   requestedAttributes:
  436 | # the ones marked Required seem to be really required by dataverse
  437 |    - '<md:RequestedAttribute FriendlyName="eduPersonPrincipalName" Name="urn:oid:1.3.6.1.4.1.5923.1.1.1.6" isRequired="true"/>'
  438 |    - '<md:RequestedAttribute FriendlyName="email" Name="urn:oid:0.9.2342.19200300.100.1.3" isRequired="true"/>'
  439 |    - '<md:RequestedAttribute FriendlyName="givenName" Name="urn:oid:2.5.4.42" isRequired="true"/>'
  440 |    - '<md:RequestedAttribute FriendlyName="sn" Name="urn:oid:2.5.4.4" isRequired="true"/>'
  441 |    - '<md:RequestedAttribute FriendlyName="eduPersonScopedAffiliation" Name="urn:oid:1.3.6.1.4.1.5923.1.1.1.9" />'
  442 | #   - '<md:RequestedAttribute FriendlyName="affiliation" Name="urn:oid:1.3.6.1.4.1.5923.1.1.1.9" />'
  443 |   organizationDisplayName: TODO
  444 |   organizationURL: TODO
  445 |   UIInfo: []
  446 | ## this is an example below
  447 | #    - lang: en
  448 | #      DisplayName: TODO
  449 | #      Description: TODO
  450 | #      InformationURL: TODO
  451 | #      PrivacyStatementURL: TODO
  452 | #      Logo:
  453 | #        url: TODO
  454 | #        height: TODO
  455 | #        width: TODO
  456 |   contactPerson: []
  457 | ## this is an example below
  458 | #    - type: technical
  459 | #      givenName: TODO
  460 | #      surName: TODO
  461 | #      emailAddress: TODO
  462 | #    - type: support
  463 | #      givenName: TODO
  464 | #      surName: TODO
  465 | #      emailAddress: TODO
  466 | #    - type: administrative
  467 | #      givenName: TODO
  468 | #      surName: TODO
  469 | #      emailAddress: TODO
  470 |   SSO: "<SSO>SAML2 SAML1</SSO>"
  471 |   MetadataProvider: '<MetadataProvider type="XML" file="dataverse-idp-metadata.xml" backingFilePath="local-idp-metadata.xml" legacyOrgNames="true" reloadInterval="7200"/>'
  472 |   showListFirst: 'true'
  473 | 
  474 | orcid:
  475 |   enabled: false
  476 |   clientId: SETME
  477 |   clientSecret: [REDACTED_LITERAL]
  478 | 
  479 | sshkeys:
  480 |   enabled: false
  481 |   files:
  482 |   urls:
  483 |   user:
  484 | 
  485 | extra_certificates:
  486 |   # this should be a list of certificate files in x509 format put in your files/ ansible directory
  487 |   files: []
  488 |   java_keystores:
  489 |     - path: '{{ payara_dir }}/glassfish/domains/{{ dataverse.payara.domain }}/config/cacerts.jks'
  490 |       pass: [REDACTED_LITERAL]
  491 |     - path: '{{ java.home }}/lib/security/cacerts'
  492 |       pass: [REDACTED_LITERAL]
```
