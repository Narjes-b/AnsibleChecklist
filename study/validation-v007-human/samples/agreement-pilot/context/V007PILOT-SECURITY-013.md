# Frozen source context: V007PILOT-SECURITY-013

- Repository: `UtrechtUniversity/yoda`
- Commit: `a9175010319fee30fb056665e9821937f0ec07c5`
- Family: Security
- Rule: `ansibleguard/plaintext-sensitive-variable`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `environments/development/full/group_vars/full.yml` (reported anchor line 61)
- Object: `variable` `6ef71f0846fad416fef960832236b3fcbe0ae1d331f8db4d491fd31b3f0cee09`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–306 of 306:

```text
    1 | ---
    2 | # copyright Utrecht University
    3 | 
    4 | # Ansible configuration
    5 | ansible_user: vagrant                             # Administrative user on instance for Ansible
    6 | ansible_ssh_private_key_file: [REDACTED_LITERAL]
    7 | ansible_python_interpreter: /usr/bin/python3      # Path to Python interpreter on the target host
    8 | 
    9 | # This is a workaround for an issue with resource creation on EL 9 systems (see YDA-6324)
   10 | common_custom_dns_enable: true
   11 | 
   12 | # Yoda configuration
   13 | instance: full                                     # Name of Yoda instance, as defined in hosts file
   14 | yoda_version: development                          # Git branch, for example: development or release-1.5
   15 | yoda_environment: development                      # Yoda environment: development, testing, acceptance or production
   16 | yoda_portal_fqdn: portal.yoda.test                 # Yoda Portal fully qualified domain name (FQDN)
   17 | yoda_davrods_fqdn: data.yoda.test                  # Yoda Davrods WebDAV fully qualified domain name (FQDN)
   18 | yoda_davrods_anonymous_enabled: true
   19 | yoda_davrods_anonymous_fqdn: public.data.yoda.test # Yoda Davrods anonymous WebDAV fully qualified domain name (FQDN)
   20 | yoda_davrods_anonymous_host: combined.yoda.test    # Yoda Davrods anonymous WebDav host (for Anubis)
   21 | 
   22 | default_yoda_schema: default-3                     # Default Yoda metadata scheme: core-2 or default-3
   23 | yoda_prefix: UU01                                  # Prefix for internal portion of persistent identifier
   24 | update_schemas: 1                                  # Update already installed schemas, formelements and stylesheets: yes (1) or no (0)
   25 | credential_files: [REDACTED_LITERAL]
   26 | 
   27 | # Anubis configuration
   28 | enable_anubis: false                               # Enable Anubis
   29 | anubis_redis_password: [REDACTED_LITERAL]
   30 | # Hex-encoded ed25519 private key used to sign Anubis responses. Required to
   31 | # ensure challenges survive service restarts.
   32 | #
   33 | # This key is an "insecure" private key we offer for use in development instances.
   34 | # If you use this instance for anything other than development, you should create your own key.
   35 | # openssl rand -hex 32
   36 | anubis_ed25519_private_key: [REDACTED_LITERAL]
   37 | 
   38 | # Text file extensions configuration
   39 | text_file_extensions: ['bash', 'csv', 'c', 'cpp', 'csharp', 'css', 'diff', 'fortran', 'gams', 'gauss', 'go', 'graphql', 'ini', 'irpf90', 'java', 'js', 'json', 'julia', 'julia-repl', 'kotlin', 'less', 'lua', 'makefile', 'markdown', 'md', 'mathematica', 'matlab', 'maxima', 'mizar', 'objectivec', 'openscad', 'perl', 'php', 'php-template', 'plaintext', 'txt', 'python', 'py', 'python-repl', 'r', 'ruby', 'rust', 'sas', 'scilab', 'scss', 'shell', 'sh', 'sql', 'stan', 'stata', 'swift', 'typescript', 'ts', 'vbnet', 'wasm', 'xml', 'yaml', 'html']
   40 | 
   41 | # Research module configuration
   42 | enable_research: true                              # Enable research module
   43 | 
   44 | # OpenSearch module configuration
   45 | enable_open_search: true                           # Enable OpenSearch module
   46 | opensearch_server: portal.yoda.test
   47 | 
   48 | # Deposit module configuration
   49 | enable_deposit: true                               # Enable deposit module
   50 | 
   51 | # Datarequest module configuration
   52 | enable_datarequest: true                           # Enable datarequest module
   53 | datarequest_help_contact_name: PLACEHOLDER         # Help contact name
   54 | datarequest_help_contact_email: PLACEHOLDER        # Help contact email
   55 | 
   56 | # Data Package Reference
   57 | enable_data_package_reference: true                # Enable Data Package References for vault data packages
   58 | 
   59 | # Data Access Tokens
   60 | enable_tokens: [REDACTED_LITERAL]
   61 | token_database: [REDACTED_LITERAL]
   62 | token_database_password: [REDACTED_LITERAL]
   63 | token_length: [REDACTED_LITERAL]
   64 | token_lifetime: [REDACTED_LITERAL]
   65 | 
   66 | # Data Package Archive
   67 | enable_data_package_archive: false                     # Enable data package archive functionality
   68 | data_package_archive_fqdn: "{{ irods_resource_fqdn }}" # Fully qualified domain name (FQDN) of iRODS server connected to data archive
   69 | data_package_archive_minimum: 1024                     # Minimum data package archive size (1 KB), -1 for no limit
   70 | data_package_archive_maximum: -1                       # Maximum data package archive size (no limit), -1 for no limit
   71 | data_package_archive_resource: mockDataArchive         # Resource to use for data package archive functionality
   72 | 
   73 | # iRODS check tooling
   74 | enable_irods_consistency_check: true
   75 | enable_icat_database_checker: true
   76 | 
   77 | # Portal customization
   78 | yoda_theme_path: /var/www/yoda/themes              # Base path holding customised portal themes
   79 | yoda_theme: uu                                     # Yoda theme: uu or vu (default: uu)
   80 | portal_title_text: Yoda - Dev
   81 | yoda_portal_log_api_call_duration: true
   82 | 
   83 | # iRODS configuration
   84 | irods_password: [REDACTED_LITERAL]
   85 | irods_database_password: [REDACTED_LITERAL]
   86 | irods_zone: tempZone                       # The name of the iRODS Zone
   87 | irods_icat_fqdn: icat.yoda.test            # iRODS iCAT fully qualified domain name (FQDN)
   88 | irods_database_fqdn: database.yoda.test    # iRODS database fully qualified domain name (FQDN)
   89 | irods_resource_fqdn: resource.yoda.test    # iRODS resource fully qualified domain name (FQDN)
   90 | irods_ssl_verify_server: none              # Verify TLS certificate, use 'cert' for acceptance and production
   91 | irods_ca_certificate_file: "/etc/irods/{{ openssl_crt_signed_and_chain }}"
   92 | irods_enable_gocommands: false
   93 | irods_anonymous_account_permit_addresses: ['192.168.56.10']
   94 | irods_resources:
   95 |   - name: dev001_1
   96 |     host: "{{ irods_icat_fqdn }}"
   97 |     vault_path: /var/lib/irods/Vault1_1
   98 |     resource_type: unixfilesystem
   99 | 
  100 |   - name: dev001_2
  101 |     resource_type: unixfilesystem
  102 |     host: "{{ irods_icat_fqdn }}"
  103 |     vault_path: /var/lib/irods/Vault1_2
  104 | 
  105 |   - name: dev001_p1
  106 |     resource_type: passthru
  107 |     children:
  108 |       - dev001_1
  109 | 
  110 |   - name: dev001_p2
  111 |     resource_type: passthru
  112 |     children:
  113 |       - dev001_2
  114 | 
  115 |   - name: dev001
  116 |     resource_type: random
  117 |     children:
  118 |       - dev001_p1
  119 |       - dev001_p2
  120 | 
  121 |   - name: irodsResc
  122 |     resource_type: random
  123 |     children:
  124 |       - dev001
  125 | 
  126 |   - name: dev002_1
  127 |     resource_type: unixfilesystem
  128 |     host: "{{ irods_resource_fqdn }}"
  129 |     vault_path: /var/lib/irods/Vault2_1
  130 | 
  131 |   - name: dev002_p1
  132 |     resource_type: passthru
  133 |     children:
  134 |       - dev002_1
  135 | 
  136 |   - name: dev002
  137 |     resource_type: random
  138 |     children:
  139 |       - dev002_p1
  140 | 
  141 |   - name: irodsRescRepl
  142 |     resource_type: random
  143 |     children:
  144 |       - dev002
  145 | 
  146 |   - name: dev003_1
  147 |     resource_type: s3
  148 |     host: "{{ irods_icat_fqdn }}"
  149 |     vault_path: /yoda
  150 |     context: "S3_DEFAULT_HOSTNAME=localhost:9000;S3_AUTH_FILE=/var/lib/irods/.s3auth;S3_REGIONNAME=local-s3;S3_RETRY_COUNT=1;S3_WAIT_TIME_SECONDS=3;S3_PROTO=HTTP;ARCHIVE_NAMING_POLICY=decoupled;HOST_MODE=cacheless_attached"
  151 | 
  152 |   - name: dev003_p1
  153 |     resource_type: passthru
  154 |     children:
  155 |       - dev003_1
  156 | 
  157 |   - name: dev003
  158 |     resource_type: random
  159 |     children:
  160 |       - dev003_p1
  161 | 
  162 |   - name: irodsRescReplS3
  163 |     resource_type: random
  164 |     children:
  165 |       - dev003
  166 | 
  167 | # List of replication resources
  168 | irods_repl_resc:
  169 |   - irodsRescRepl
  170 |   - irodsRescReplS3
  171 | 
  172 | async_replication_delay_time: 3600     # Delay after last modification to data object before replication job can process it (sec)
  173 | vault_copy_backoff_time: 300           # How many seconds to wait before trying to copy a certain folder to vault again
  174 | 
  175 | # Automatic resource balancing configuration
  176 | irods_arb_enabled: true
  177 | irods_arb_exempt_resources: ""
  178 | irods_arb_min_gb_free: 0
  179 | irods_arb_min_percent_free: 5
  180 | 
  181 | # S3 configuration
  182 | enable_s3_resource: false
  183 | s3_access_key: [REDACTED_LITERAL]
  184 | s3_secret_key: [REDACTED_LITERAL]
  185 | s3_hostname: localhost:9000
  186 | 
  187 | # Mail notifications
  188 | send_notifications: 1                         # Enable notifications: yes (1) or no (0)
  189 | notifications_sender_email: noreply@yoda.test # Notifications sender email address
  190 | notifications_reply_to: noreply@yoda.test     # Notifications reply-To email address
  191 | smtp_server: smtp://localhost:25
  192 | smtp_auth: false
  193 | smtp_starttls: false
  194 | 
  195 | # DataCite Configuration
  196 | datacite_rest_api_url: datacite-mock.yoda.test # DataCite API server URL
  197 | datacite_username: PLACEHOLDER                 # DataCite username
  198 | datacite_password: [REDACTED_LITERAL]
  199 | datacite_prefix: 10.00012                      # DataCite DOI prefix
  200 | datacite_publisher: Yoda development team      # DataCite publisher: the name of the entity that publishes
  201 | datacite_tls_verify: 0                         # DataCite TLS verification / disabled on development environment
  202 |                                                # since the mock service uses self-signed certificates.
  203 | 
  204 | # EPIC PID Configuration
  205 | epic_url: PLACEHOLDER              # EPIC PID server URI (undefined disables EPIC PID)
  206 | epic_handle_prefix: PLACEHOLDER    # EPIC PID prefix
  207 | 
  208 | # Zabbix configuration
  209 | zabbix_server: PLACEHOLDER
  210 | 
  211 | # Public host configuration
  212 | yoda_public_host: public.yoda.test     # Yoda public host
  213 | yoda_public_fqdn: public.yoda.test     # Yoda public fully qualified domain name (FQDN)
  214 | 
  215 | # Yoda public upload private key (base64 encoded)
  216 | # These keys are the "insecure" public/private keypair we offer for use in development instances.
  217 | # If you use this instance for anything other than development, you should create your own keypair.
  218 | # ssh-keygen -t ed25519 -> base64
  219 | upload_priv_key: |
  220 |   LS0tLS1CRUdJTiBPUEVOU1NIIFBSSVZBVEUgS0VZLS0tLS0KYjNCbGJuTnphQzFyWlhrdGRqRUFB
  221 |   QUFBQkc1dmJtVUFBQUFFYm05dVpRQUFBQUFBQUFBQkFBQUFNd0FBQUF0emMyZ3RaVwpReU5UVXhP
  222 |   UUFBQUNDTGlhY01DT2xPZzNpSFg4VXdYOHpWUk11cFB2Y2NyTTdmQUNodU9WMi80UUFBQUpoQTVj
  223 |   YTlRT1hHCnZRQUFBQXR6YzJndFpXUXlOVFV4T1FBQUFDQ0xpYWNNQ09sT2czaUhYOFV3WDh6VlJN
  224 |   dXBQdmNjck03ZkFDaHVPVjIvNFEKQUFBRUFtRng0MmVDSDBYOHFHaXpmUmFpcFJWa3MzcVo1OWda
  225 |   SU92TUJkZy85SnhZdUpwd3dJNlU2RGVJZGZ4VEJmek5WRQp5NmsrOXh5c3p0OEFLRzQ1WGIvaEFB
  226 |   QUFEbWx5YjJSelFHTnZiV0pwYm1Wa0FRSURCQVVHQnc9PQotLS0tLUVORCBPUEVOU1NIIFBSSVZB
  227 |   VEUgS0VZLS0tLS0K
  228 | 
  229 | # Yoda public upload public key (base64 encoded)
  230 | upload_pub_key: |
  231 |   c3NoLWVkMjU1MTkgQUFBQUMzTnphQzFsWkRJMU5URTVBQUFBSUl1SnB3d0k2VTZEZUlkZnhUQmZ6
  232 |   TlZFeTZrKzl4eXN6dDhBS0c0NVhiL2ggaXJvZHNAY29tYmluZWQK
  233 | 
  234 | # External user service configuration
  235 | yoda_eus_fqdn: eus.yoda.test
  236 | eus_api_fqdn: api.eus.yoda.test
  237 | eus_api_secret: [REDACTED_LITERAL]
  238 | eus_api_tls_verify: false
  239 | eus_db_password: [REDACTED_LITERAL]
  240 | eus_smtp_from_address: yoda@yoda.test
  241 | eus_smtp_replyto_address: yoda@yoda.test
  242 | eus_mail_template: uu
  243 | external_users_domain_filter: '*.yoda.dev'                    # Domains to filter, separated by | and wildcard character *
  244 | 
  245 | portal_session_cookie_samesite: Lax                                  # 'Strict' (no OIDC, or OIDC IDP in same domain) or 'Lax'
  246 | 
  247 | # OpenID Connect configuration (This configuration is for TESTING purposes!)
  248 | oidc_active: true                                                    # Boolean indicating whether OpenId Connect is enabled
  249 | oidc_domains: ['*.yoda.dev']                                         # Domains that should use OIDC (list, wildcard character *)
  250 | oidc_always_redirect: false                                          # Ignore OIDC domains and redirect all domains
  251 | oidc_client_id: myClientId                                           # OIDC Client Id
  252 | oidc_client_secret: [REDACTED_LITERAL]
  253 | oidc_auth_base_uri: https://oauth.wiremockapi.cloud/oauth/authorize  # OIDC Authorization URI without parameters
  254 | oidc_token_uri: [REDACTED_LITERAL]
  255 | oidc_userinfo_uri: https://oauth.wiremockapi.cloud/userinfo          # OIDC Userinfo URI
  256 | oidc_scopes: openid                                                  # OIDC Scopes
  257 | oidc_acr_values: ""                                                  # OIDC Authentication Context Class Reference Values
  258 | oidc_email_field: email                                              # The identifier of the JSON field in the id_token containing the email address (default: email)
  259 | oidc_jwks_uri: https://oauth.wiremockapi.cloud/.well-known/jwks.json # The url where the JWKS can be found (Java web key sets)
  260 | oidc_jwt_issuer: https://oauth.wiremockapi.cloud                     # The issuer of the JWT tokens ('iss' value in JWT, for verification)
  261 | oidc_req_exp: true                                                   # Check that exp (expiration) claim is present
  262 | oidc_req_iat: false                                                  # Check that iat (issued at) claim is present
  263 | oidc_req_nbf: false                                                  # Check that nbf (not before) claim is present
  264 | oidc_verify_aud: true                                                # Check that aud (audience) claim matches audience
  265 | oidc_verify_iat: false                                               # Check that iat (issued at) claim value is an integer
  266 | oidc_verify_exp: true                                                # Check that exp (expiration) claim value is OK
  267 | oidc_verify_iss: true                                                # Check that iss (issue) claim is as expected
  268 | 
  269 | # SRAM configuration (This configuration is for TESTING purposes!)
  270 | enable_sram: true                                                    # Enable SRAM configuration
  271 | sram_rest_api_url: sram-mock.yoda.test                               # SRAM Rest API URL
  272 | sram_api_key: [REDACTED_LITERAL]
  273 | sram_service_entity_id: PLACEHOLDER                                  # SRAM Service Entity ID
  274 | sram_auto_external_users_co_sync: false                              # Automatic SRAM external users CO sync
  275 | sram_auto_group_sync: false                                          # Automatic SRAM group sync
  276 | sram_verbose_logging: true                                           # SRAM verbose logging
  277 | sram_tls_verify: false                                               # Enable TLS verification for SRAM API calls. Enabled by default.
  278 | sram_co_default_label: PLACEHOLDER                                   # Default SRAM label
  279 | sram_co_default_admins: ['sram-admin@yoda.test']                     # List of SRAM CO default administrators, used as fallback when CO is created by user without a valid email
  280 | sram_external_users_co: 76f1e2c9-a548-4019-a281-ece2da3fd642         # CO identifier of SRAM external users collaboration
  281 | 
  282 | sram_oidc_client_id: myClientId                                           # SRAM OIDC Client Id
  283 | sram_oidc_client_secret: [REDACTED_LITERAL]
  284 | sram_oidc_auth_base_uri: https://oauth.wiremockapi.cloud/oauth/authorize  # SRAM OIDC Authorization URI without parameters
  285 | sram_oidc_token_uri: [REDACTED_LITERAL]
  286 | sram_oidc_userinfo_uri: https://oauth.wiremockapi.cloud/userinfo          # SRAM OIDC Userinfo URI
  287 | sram_oidc_scopes: openid                                                  # SRAM OIDC Scopes
  288 | sram_oidc_acr_values: ""                                                  # SRAM OIDC Authentication Context Class Reference Values
  289 | sram_oidc_email_field: email                                              # The identifier of the JSON field in the id_token containing the email address (default: email)
  290 | sram_oidc_jwks_uri: https://oauth.wiremockapi.cloud/.well-known/jwks.json # The url where the JWKS can be found (Java web key sets)
  291 | sram_oidc_jwt_issuer: https://oauth.wiremockapi.cloud                     # The issuer of the JWT tokens ('iss' value in JWT, for verification)
  292 | sram_oidc_req_exp: true                                                   # Check that exp (expiration) claim is present
  293 | sram_oidc_req_iat: false                                                  # Check that iat (issued at) claim is present
  294 | sram_oidc_req_nbf: false                                                  # Check that nbf (not before) claim is present
  295 | sram_oidc_verify_aud: true                                                # Check that aud (audience) claim matches audience
  296 | sram_oidc_verify_iat: false                                               # Check that iat (issued at) claim value is an integer
  297 | sram_oidc_verify_exp: true                                                # Check that exp (expiration) claim value is OK
  298 | sram_oidc_verify_iss: true                                                # Check that iss (issue) claim is as expected
  299 | 
  300 | # Mail configuration
  301 | enable_mailpit: true
  302 | enable_postfix: false
  303 | enable_yoda_report: false
  304 | 
  305 | # yoda-clienttools
  306 | enable_yoda_clienttools: false
```
