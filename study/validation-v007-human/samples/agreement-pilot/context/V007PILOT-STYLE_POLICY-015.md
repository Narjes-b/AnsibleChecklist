# Frozen source context: V007PILOT-STYLE_POLICY-015

- Repository: `spantaleev/matrix-docker-ansible-deploy`
- Commit: `8309e7932dd995f83fb022d646fe4b1c4f2a9d98`
- Family: Style/policy
- Rule: `ansibleguard/long-statement`
- Codebook: `codebooks/FAMILY_STYLE_POLICY.md`
- Source: `roles/custom/matrix-client-fluffychat/defaults/main.yml` (reported anchor line 32)
- Object: `source_location` `8e17dace111d0806e123c6d9017ec46cd73c884640fbcc95e19a8399b700f745`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–163 of 163:

```text
    1 | # SPDX-FileCopyrightText: 2025 Nikita Chernyi
    2 | # SPDX-FileCopyrightText: 2025 Slavi Pantaleev
    3 | #
    4 | # SPDX-License-Identifier: AGPL-3.0-or-later
    5 | 
    6 | ---
    7 | # Project source code URL: https://github.com/krille-chan/fluffychat
    8 | 
    9 | matrix_client_fluffychat_enabled: true
   10 | 
   11 | matrix_client_fluffychat_container_image_self_build: false
   12 | matrix_client_fluffychat_container_image_self_build_repo: "https://github.com/etkecc/fluffychat-web.git"
   13 | matrix_client_fluffychat_container_image_self_build_version: "{{ 'main' if matrix_client_fluffychat_version == 'latest' else matrix_client_fluffychat_version }}"
   14 | 
   15 | # renovate: datasource=docker depName=ghcr.io/etkecc/fluffychat-web
   16 | matrix_client_fluffychat_version: v2.9.1
   17 | matrix_client_fluffychat_container_image: "{{ matrix_client_fluffychat_container_image_registry_prefix }}etkecc/fluffychat-web:{{ matrix_client_fluffychat_version }}"
   18 | matrix_client_fluffychat_container_image_registry_prefix: "{{ 'localhost/' if matrix_client_fluffychat_container_image_self_build else matrix_client_fluffychat_container_image_registry_prefix_upstream }}"
   19 | matrix_client_fluffychat_container_image_registry_prefix_upstream: "{{ matrix_client_fluffychat_container_image_registry_prefix_upstream_default }}"
   20 | matrix_client_fluffychat_container_image_registry_prefix_upstream_default: ghcr.io/
   21 | 
   22 | matrix_client_fluffychat_base_path: "{{ matrix_base_data_path }}/client-fluffychat"
   23 | matrix_client_fluffychat_config_path: "{{ matrix_client_fluffychat_base_path }}/config"
   24 | matrix_client_fluffychat_container_src_files_path: "{{ matrix_client_fluffychat_base_path }}/docker-src"
   25 | 
   26 | # The base container network
   27 | matrix_client_fluffychat_container_network: ''
   28 | 
   29 | # A list of additional container networks that the container would be connected to.
   30 | # The role does not create these networks, so make sure they already exist.
   31 | # Use this to expose this container to a reverse proxy, which runs in a different container network.
   32 | matrix_client_fluffychat_container_additional_networks: "{{ matrix_client_fluffychat_container_additional_networks_auto + matrix_client_fluffychat_container_additional_networks_custom }}"
   33 | matrix_client_fluffychat_container_additional_networks_auto: []
   34 | matrix_client_fluffychat_container_additional_networks_custom: []
   35 | 
   36 | # Configures the port number used inside the container image.
   37 | matrix_client_fluffychat_container_http_port: 8080
   38 | 
   39 | # Controls whether the matrix-client-fluffychat container exposes its configured HTTP port (tcp/8080 by default).
   40 | #
   41 | # Takes an "<ip>:<port>" or "<port>" value (e.g. "127.0.0.1:8080"), or empty string to not expose.
   42 | #
   43 | # Also see: `matrix_client_fluffychat_container_http_port`
   44 | matrix_client_fluffychat_container_http_host_bind_port: ''
   45 | 
   46 | # matrix_client_fluffychat_container_labels_traefik_enabled controls whether labels to assist a Traefik reverse-proxy will be attached to the container.
   47 | # See `../templates/labels.j2` for details.
   48 | #
   49 | # To inject your own other container labels, see `matrix_client_fluffychat_container_labels_additional_labels`.
   50 | matrix_client_fluffychat_container_labels_traefik_enabled: true
   51 | matrix_client_fluffychat_container_labels_traefik_docker_network: "{{ matrix_client_fluffychat_container_network }}"
   52 | matrix_client_fluffychat_container_labels_traefik_http_service_load_balancer_port: "{{ matrix_client_fluffychat_container_http_port }}"
   53 | matrix_client_fluffychat_container_labels_traefik_hostname: "{{ matrix_client_fluffychat_hostname }}"
   54 | # The path prefix must either be `/` or not end with a slash (e.g. `/fluffychat`).
   55 | matrix_client_fluffychat_container_labels_traefik_path_prefix: "{{ matrix_client_fluffychat_path_prefix }}"
   56 | matrix_client_fluffychat_container_labels_traefik_rule: "Host(`{{ matrix_client_fluffychat_container_labels_traefik_hostname }}`){% if matrix_client_fluffychat_container_labels_traefik_path_prefix != '/' %} && PathPrefix(`{{ matrix_client_fluffychat_container_labels_traefik_path_prefix }}`){% endif %}"
   57 | matrix_client_fluffychat_container_labels_traefik_priority: 0
   58 | matrix_client_fluffychat_container_labels_traefik_entrypoints: web-secure
   59 | matrix_client_fluffychat_container_labels_traefik_tls: "{{ matrix_client_fluffychat_container_labels_traefik_entrypoints != 'web' }}"
   60 | matrix_client_fluffychat_container_labels_traefik_tls_certResolver: default  # noqa var-naming
   61 | 
   62 | # Controls which additional headers to attach to all HTTP responses.
   63 | # To add your own headers, use `matrix_client_fluffychat_container_labels_traefik_additional_response_headers_custom`
   64 | matrix_client_fluffychat_container_labels_traefik_additional_response_headers: "{{ matrix_client_fluffychat_container_labels_traefik_additional_response_headers_auto | combine(matrix_client_fluffychat_container_labels_traefik_additional_response_headers_custom) }}"
   65 | matrix_client_fluffychat_container_labels_traefik_additional_response_headers_auto: |
   66 |   {{
   67 |     {}
   68 |     | combine ({'X-XSS-Protection': matrix_client_fluffychat_http_header_xss_protection} if matrix_client_fluffychat_http_header_xss_protection else {})
   69 |     | combine ({'X-Content-Type-Options': matrix_client_fluffychat_http_header_content_type_options} if matrix_client_fluffychat_http_header_content_type_options else {})
   70 |     | combine ({'Content-Security-Policy': matrix_client_fluffychat_http_header_content_security_policy} if matrix_client_fluffychat_http_header_content_security_policy else {})
   71 |     | combine ({'Permission-Policy': matrix_client_fluffychat_http_header_content_permission_policy} if matrix_client_fluffychat_http_header_content_permission_policy else {})
   72 |     | combine ({'Strict-Transport-Security': matrix_client_fluffychat_http_header_strict_transport_security} if matrix_client_fluffychat_http_header_strict_transport_security and matrix_client_fluffychat_container_labels_traefik_tls else {})
   73 |   }}
   74 | matrix_client_fluffychat_container_labels_traefik_additional_response_headers_custom: {}
   75 | 
   76 | # matrix_client_fluffychat_container_labels_additional_labels contains a multiline string with additional labels to add to the container label file.
   77 | # See `../templates/labels.j2` for details.
   78 | #
   79 | # Example:
   80 | # matrix_client_fluffychat_container_labels_additional_labels: |
   81 | #   my.label=1
   82 | #   another.label="here"
   83 | matrix_client_fluffychat_container_labels_additional_labels: ''
   84 | 
   85 | # A list of extra arguments to pass to the container
   86 | matrix_client_fluffychat_container_extra_arguments: []
   87 | 
   88 | # List of systemd services that matrix-client-fluffychat.service depends on
   89 | matrix_client_fluffychat_systemd_required_services_list: "{{ matrix_client_fluffychat_systemd_required_services_list_default + matrix_client_fluffychat_systemd_required_services_list_auto + matrix_client_fluffychat_systemd_required_services_list_custom }}"
   90 | matrix_client_fluffychat_systemd_required_services_list_default: "{{ [devture_systemd_docker_base_docker_service_name] if devture_systemd_docker_base_docker_service_name else [] }}"
   91 | matrix_client_fluffychat_systemd_required_services_list_auto: []
   92 | matrix_client_fluffychat_systemd_required_services_list_custom: []
   93 | 
   94 | # Specifies the value of the `X-XSS-Protection` header
   95 | # Stops pages from loading when they detect reflected cross-site scripting (XSS) attacks.
   96 | #
   97 | # Learn more about it is here:
   98 | # - https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-XSS-Protection
   99 | # - https://portswigger.net/web-security/cross-site-scripting/reflected
  100 | matrix_client_fluffychat_http_header_xss_protection: "1; mode=block"
  101 | 
  102 | # Specifies the value of the `X-Content-Type-Options` header.
  103 | # See: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Content-Type-Options
  104 | matrix_client_fluffychat_http_header_content_type_options: nosniff
  105 | 
  106 | # Specifies the value of the `Content-Security-Policy` header.
  107 | # See: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy
  108 | matrix_client_fluffychat_http_header_content_security_policy: frame-ancestors 'self'
  109 | 
  110 | # Specifies the value of the `Permission-Policy` header.
  111 | # See: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Permission-Policy
  112 | matrix_client_fluffychat_http_header_content_permission_policy: "{{ 'interest-cohort=()' if matrix_client_fluffychat_floc_optout_enabled else '' }}"
  113 | 
  114 | # Specifies the value of the `Strict-Transport-Security` header.
  115 | # See: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security
  116 | matrix_client_fluffychat_http_header_strict_transport_security: "max-age=31536000; includeSubDomains{{ '; preload' if matrix_client_fluffychat_hsts_preload_enabled else '' }}"
  117 | 
  118 | # Controls whether to send a "Permissions-Policy interest-cohort=();" header along with all responses
  119 | #
  120 | # Learn more about what it is here:
  121 | # - https://www.eff.org/deeplinks/2021/03/googles-floc-terrible-idea
  122 | # - https://paramdeo.com/blog/opting-your-website-out-of-googles-floc-network
  123 | # - https://amifloced.org/
  124 | #
  125 | # Of course, a better solution is to just stop using browsers (like Chrome), which participate in such tracking practices.
  126 | # See: `matrix_client_fluffychat_content_permission_policy`
  127 | matrix_client_fluffychat_floc_optout_enabled: true
  128 | 
  129 | # Controls if HSTS preloading is enabled
  130 | #
  131 | # In its strongest and recommended form, the [HSTS policy](https://www.chromium.org/hsts) includes all subdomains, and
  132 | # indicates a willingness to be "preloaded" into browsers:
  133 | # `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`
  134 | # For more information visit:
  135 | # - https://en.wikipedia.org/wiki/HTTP_Strict_Transport_Security
  136 | # - https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security
  137 | # - https://hstspreload.org/#opt-in
  138 | # See: `matrix_client_fluffychat_http_header_strict_transport_security`
  139 | matrix_client_fluffychat_hsts_preload_enabled: false
  140 | 
  141 | matrix_client_fluffychat_scheme: https
  142 | # The hostname at which FluffyChat Web is served.
  143 | matrix_client_fluffychat_hostname: "{{ matrix_server_fqn_fluffychat }}"
  144 | 
  145 | # The path at which FluffyChat Web is exposed.
  146 | # This value must either be `/` or not end with a slash (e.g. `/fluffychat`).
  147 | matrix_client_fluffychat_path_prefix: /
  148 | 
  149 | # Controls whether the self-check feature should validate SSL certificates.
  150 | matrix_client_fluffychat_self_check_validate_certificates: true
  151 | 
  152 | # Controls the default homeserver domain (not URL) used in the FluffyChat Web configuration.
  153 | matrix_client_fluffychat_config_defaultHomeserver: ~  # noqa var-naming
  154 | 
  155 | # matrix_client_fluffychat_restart_necessary controls whether the service
  156 | # will be restarted (when true) or merely started (when false) by the
  157 | # systemd service manager role (when conditional restart is enabled).
  158 | #
  159 | # This value is automatically computed during installation based on whether
  160 | # any configuration files, the systemd service file, or the container image changed.
  161 | # The default of `false` means "no restart needed" — appropriate when the role's
  162 | # installation tasks haven't run (e.g., due to --tags skipping them).
  163 | matrix_client_fluffychat_restart_necessary: false
```
