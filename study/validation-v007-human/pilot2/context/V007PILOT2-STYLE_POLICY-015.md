# Frozen source context: V007PILOT2-STYLE_POLICY-015

- Repository: `spantaleev/matrix-docker-ansible-deploy`
- Commit: `8309e7932dd995f83fb022d646fe4b1c4f2a9d98`
- Family: style_policy
- Rule: `ansibleguard/long-statement`
- Codebook: `codebooks-v2/FAMILY_STYLE_POLICY_V2.md`
- Source: `roles/custom/matrix-bridge-steam/defaults/main.yml` (reported anchor line 177)
- Flagged construct: not named by the finding; the anchor line 177 lies in the top-level key `matrix_bridge_steam_database_connection_string` (line 177).
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–263 of 263:

```text
    1 | # SPDX-FileCopyrightText: 2025 Jason LaGuidice
    2 | #
    3 | # SPDX-License-Identifier: AGPL-3.0-or-later
    4 | 
    5 | ---
    6 | # matrix-steam-bridge is a Matrix <-> Steam bridge
    7 | # See: https://github.com/jasonlaguidice/matrix-steam-bridge
    8 | 
    9 | matrix_bridge_steam_enabled: true
   10 | 
   11 | matrix_bridge_steam_container_image_self_build: false
   12 | matrix_bridge_steam_container_image_self_build_repo: "https://github.com/jasonlaguidice/matrix-steam-bridge.git"
   13 | matrix_bridge_steam_container_image_self_build_repo_version: "{{ 'main' if matrix_bridge_steam_version == 'latest' else matrix_bridge_steam_version }}"
   14 | 
   15 | # renovate: datasource=docker depName=ghcr.io/jasonlaguidice/matrix-steam-bridge
   16 | matrix_bridge_steam_version: 1.3.1
   17 | matrix_bridge_steam_container_image: "{{ matrix_bridge_steam_container_image_registry_prefix }}jasonlaguidice/matrix-steam-bridge:{{ matrix_bridge_steam_version }}"
   18 | matrix_bridge_steam_container_image_registry_prefix: "{{ 'localhost/' if matrix_bridge_steam_container_image_self_build else matrix_bridge_steam_container_image_registry_prefix_upstream }}"
   19 | matrix_bridge_steam_container_image_registry_prefix_upstream: "{{ matrix_bridge_steam_container_image_registry_prefix_upstream_default }}"
   20 | matrix_bridge_steam_container_image_registry_prefix_upstream_default: "ghcr.io/"
   21 | matrix_bridge_steam_container_image_tag: "{{ matrix_bridge_steam_version }}"
   22 | 
   23 | matrix_bridge_steam_base_path: "{{ matrix_base_data_path }}/matrix-steam-bridge"
   24 | matrix_bridge_steam_config_path: "{{ matrix_bridge_steam_base_path }}/config"
   25 | matrix_bridge_steam_data_path: "{{ matrix_bridge_steam_base_path }}/data"
   26 | matrix_bridge_steam_container_src_files_path: "{{ matrix_bridge_steam_base_path }}/docker-src"
   27 | 
   28 | matrix_bridge_steam_homeserver_address: ""
   29 | matrix_bridge_steam_homeserver_domain: "{{ matrix_domain }}"
   30 | matrix_bridge_steam_appservice_address: "http://matrix-steam-bridge:{{ matrix_bridge_steam_appservice_port }}"
   31 | matrix_bridge_steam_appservice_port: "8080"
   32 | 
   33 | matrix_bridge_steam_msc4190_enabled: "{{ matrix_bridges_msc4190_enabled }}"
   34 | matrix_bridge_steam_self_sign_enabled: "{{ matrix_bridges_self_sign_enabled }}"
   35 | 
   36 | # matrix -> steam presence
   37 | matrix_bridge_steam_network_presence_enabled: true
   38 | # Default inactivity state
   39 | # This is what the bridge sets it's status to after some time of no user interaction
   40 | matrix_bridge_steam_network_presence_inactivity_status: 'invisible'
   41 | 
   42 | # steam -> matrix presence topic
   43 | # Master switch for setting a Steam friend's current game (+ rich presence flavor
   44 | # text) as the DM room's m.room.topic.
   45 | matrix_bridge_steam_network_presence_topic_enabled: false
   46 | # Append resolved rich presence flavor text to the topic (e.g. "Deadlock — Street Brawl: Paige (12 min)").
   47 | matrix_bridge_steam_network_presence_topic_rich_presence_enabled: false
   48 | # Fallback: show the raw unresolved rich presence token if resolution fails.
   49 | matrix_bridge_steam_network_presence_topic_show_raw_tokens: [REDACTED_LITERAL]
   50 | 
   51 | # A public address that external services can use to reach this appservice
   52 | matrix_bridge_steam_appservice_public_address: "https://{{ matrix_server_fqn_matrix }}"
   53 | 
   54 | # Public media configuration for external access to bridge media
   55 | matrix_bridge_steam_public_media_enabled: true
   56 | # A key for signing public media URLs. If set to "generate", a random key will be generated.
   57 | # This will be auto-generated deterministically if matrix_homeserver_generic_secret_key is set.
   58 | matrix_bridge_steam_public_media_signing_key: ''
   59 | # Number of seconds that public media URLs are valid for. If set to 0, URLs will never expire.
   60 | matrix_bridge_steam_public_media_expiry: 0
   61 | matrix_bridge_steam_public_media_hash_length: 32
   62 | 
   63 | # Display name template for Steam users.
   64 | # Available template variables:
   65 | # {{.PersonaName}} - The Steam display name/persona name (most commonly used)
   66 | # {{.AccountName}} - The Steam account/login name
   67 | # {{.SteamID}}     - The numeric Steam ID
   68 | # {{.ProfileURL}}  - The Steam profile URL
   69 | # You can use template functions like {{or}} to provide fallbacks.
   70 | matrix_bridge_steam_network_displayname_template: "{% raw %}{{ .PersonaName }} (Steam){% endraw %}"
   71 | 
   72 | matrix_bridge_steam_command_prefix: "!steam"
   73 | 
   74 | matrix_bridge_steam_bridge_permissions: |
   75 |   {{
   76 |     {matrix_bridge_steam_homeserver_domain: 'user'}
   77 |     | combine ({matrix_admin: 'admin'} if matrix_admin else {})
   78 |   }}
   79 | 
   80 | # TODO: May need to set network for public media?
   81 | matrix_bridge_steam_container_network: ""
   82 | 
   83 | matrix_bridge_steam_container_additional_networks: "{{ matrix_bridge_steam_container_additional_networks_auto + matrix_bridge_steam_container_additional_networks_custom }}"
   84 | matrix_bridge_steam_container_additional_networks_auto: []
   85 | matrix_bridge_steam_container_additional_networks_custom: []
   86 | 
   87 | # matrix_bridge_steam_container_labels_traefik_enabled controls whether labels to assist a Traefik reverse-proxy will be attached to the container.
   88 | # See `../templates/labels.j2` for details.
   89 | #
   90 | # To inject your own other container labels, see `matrix_bridge_steam_container_labels_additional_labels`.
   91 | matrix_bridge_steam_container_labels_traefik_enabled: true
   92 | matrix_bridge_steam_container_labels_traefik_docker_network: "{{ matrix_bridge_steam_container_network }}"
   93 | matrix_bridge_steam_container_labels_traefik_entrypoints: web-secure
   94 | matrix_bridge_steam_container_labels_traefik_tls: "{{ matrix_bridge_steam_container_labels_traefik_entrypoints != 'web' }}"
   95 | matrix_bridge_steam_container_labels_traefik_tls_certResolver: default  # noqa var-naming
   96 | 
   97 | # Whether this bridge's HTTP API (including the provisioning API) is exposed at a
   98 | # public path via Traefik. Disabled by default. When enabled, requests to
   99 | # https://<matrix_bridge_steam_exposure_hostname><matrix_bridge_steam_exposure_path_prefix>/...
  100 | # are forwarded to the bridge with that path prefix stripped.
  101 | matrix_bridge_steam_exposure_enabled: false
  102 | matrix_bridge_steam_exposure_hostname: ''
  103 | matrix_bridge_steam_exposure_path_prefix: ''
  104 | 
  105 | matrix_bridge_steam_container_labels_exposure_enabled: "{{ matrix_bridge_steam_exposure_enabled }}"
  106 | matrix_bridge_steam_container_labels_exposure_traefik_rule: "Host(`{{ matrix_bridge_steam_exposure_hostname }}`) && PathPrefix(`{{ matrix_bridge_steam_exposure_path_prefix }}`)"
  107 | matrix_bridge_steam_container_labels_exposure_traefik_priority: 0
  108 | matrix_bridge_steam_container_labels_exposure_traefik_entrypoints: "{{ matrix_bridge_steam_container_labels_traefik_entrypoints }}"
  109 | matrix_bridge_steam_container_labels_exposure_traefik_tls: "{{ matrix_bridge_steam_container_labels_exposure_traefik_entrypoints != 'web' }}"
  110 | matrix_bridge_steam_container_labels_exposure_traefik_tls_certResolver: "{{ matrix_bridge_steam_container_labels_traefik_tls_certResolver }}"  # noqa var-naming
  111 | 
  112 | # matrix_bridge_steam_container_labels_additional_labels contains a multiline string with additional labels to add to the container label file.
  113 | # See `../templates/labels.j2` for details.
  114 | #
  115 | # Example:
  116 | # matrix_bridge_steam_container_labels_additional_labels: |
  117 | #   my.label=1
  118 | #   another.label="here"
  119 | matrix_bridge_steam_container_labels_additional_labels: ''
  120 | 
  121 | # A list of extra arguments to pass to the container
  122 | matrix_bridge_steam_container_extra_arguments: []
  123 | 
  124 | # List of systemd services that matrix-steam-bridge.service depends on.
  125 | matrix_bridge_steam_systemd_required_services_list: "{{ matrix_bridge_steam_systemd_required_services_list_default + matrix_bridge_steam_systemd_required_services_list_auto + matrix_bridge_steam_systemd_required_services_list_custom }}"
  126 | matrix_bridge_steam_systemd_required_services_list_default: "{{ [devture_systemd_docker_base_docker_service_name] if devture_systemd_docker_base_docker_service_name else [] }}"
  127 | matrix_bridge_steam_systemd_required_services_list_auto: []
  128 | matrix_bridge_steam_systemd_required_services_list_custom: []
  129 | 
  130 | # List of systemd services that matrix-steam-bridge.service wants
  131 | matrix_bridge_steam_systemd_wanted_services_list: []
  132 | 
  133 | matrix_bridge_steam_appservice_token: [REDACTED VALUE BLOCK]
  134 | matrix_bridge_steam_homeserver_token: [REDACTED VALUE BLOCK]
  135 | 
  136 | # Whether or not created rooms should have federation enabled.
  137 | # If false, created portal rooms will never be federated.
  138 | matrix_bridge_steam_matrix_federate_rooms: false
  139 | 
  140 | # Bridge configuration options
  141 | # Should every user have their own portals rather than sharing them?
  142 | matrix_bridge_steam_bridge_split_portals: false
  143 | 
  144 | # Cleanup on logout configuration
  145 | matrix_bridge_steam_bridge_cleanup_on_logout_enabled: false
  146 | # Valid values for cleanup actions: nothing, kick, unbridge, delete
  147 | #   nothing - Do nothing, let the user stay in the portals
  148 | #   kick - Remove the user from the portal rooms, but don't delete them
  149 | #   unbridge - Remove all ghosts in the room and disassociate it from the remote chat
  150 | #   delete - Remove all ghosts and users from the room (i.e. delete it)
  151 | matrix_bridge_steam_bridge_cleanup_on_logout_manual_private: nothing
  152 | matrix_bridge_steam_bridge_cleanup_on_logout_manual_relayed: nothing
  153 | matrix_bridge_steam_bridge_cleanup_on_logout_manual_shared_no_users: nothing
  154 | matrix_bridge_steam_bridge_cleanup_on_logout_manual_shared_has_users: nothing
  155 | matrix_bridge_steam_bridge_cleanup_on_logout_bad_credentials_private: [REDACTED_LITERAL]
  156 | matrix_bridge_steam_bridge_cleanup_on_logout_bad_credentials_relayed: [REDACTED_LITERAL]
  157 | matrix_bridge_steam_bridge_cleanup_on_logout_bad_credentials_shared_no_users: [REDACTED_LITERAL]
  158 | matrix_bridge_steam_bridge_cleanup_on_logout_bad_credentials_shared_has_users: [REDACTED_LITERAL]
  159 | 
  160 | # Homeserver configuration options
  161 | # Does the homeserver support MSC2246 (async media uploads)?
  162 | matrix_bridge_steam_homeserver_async_media: false
  163 | 
  164 | # Database-related configuration fields.
  165 | #
  166 | # To use Postgres:
  167 | # - adjust your database credentials via the `matrix_bridge_steam_postgres_*` variables
  168 | matrix_bridge_steam_database_engine: 'postgres'
  169 | 
  170 | matrix_bridge_steam_database_username: 'matrix_steam_bridge'
  171 | matrix_bridge_steam_database_password: [REDACTED_LITERAL]
  172 | matrix_bridge_steam_database_hostname: ''
  173 | matrix_bridge_steam_database_port: 5432
  174 | matrix_bridge_steam_database_name: 'matrix_steam_bridge'
  175 | matrix_bridge_steam_database_sslmode: disable
  176 | 
  177 | matrix_bridge_steam_database_connection_string: 'postgres://{{ matrix_bridge_steam_database_username }}:{{ matrix_bridge_steam_database_password }}@{{ matrix_bridge_steam_database_hostname }}:{{ matrix_bridge_steam_database_port }}/{{ matrix_bridge_steam_database_name }}?sslmode={{ matrix_bridge_steam_database_sslmode }}'
  178 | 
  179 | matrix_bridge_steam_database_uri: "{{ {
  180 |     'postgres': matrix_bridge_steam_database_connection_string,
  181 | }[matrix_bridge_steam_database_engine] }}"
  182 | 
  183 | matrix_bridge_steam_double_puppet_secrets: "{{ matrix_bridge_steam_double_puppet_secrets_auto | combine(matrix_bridge_steam_double_puppet_secrets_custom) }}"
  184 | matrix_bridge_steam_double_puppet_secrets_auto: [REDACTED_LITERAL]
  185 | matrix_bridge_steam_double_puppet_secrets_custom: [REDACTED_LITERAL]
  186 | 
  187 | matrix_bridge_steam_appservice_bot_username: steambot
  188 | matrix_bridge_steam_appservice_bot_displayname: Steam bridge bot
  189 | matrix_bridge_steam_appservice_bot_avatar: mxc://shadowdrake.org/EeNKAcrmByNubPwoyceQsBaN
  190 | 
  191 | matrix_bridge_steam_backfill_enabled: true
  192 | # Maximum number of messages to backfill in empty rooms
  193 | matrix_bridge_steam_backfill_max_initial_messages: 50
  194 | 
  195 | # Maximum number of missed messages to backfill after bridge restarts
  196 | matrix_bridge_steam_backfill_max_catchup_messages: 500
  197 | 
  198 | # Shared secret for authentication of provisioning API requests.
  199 | # If set to "disable", the provisioning API will be disabled.
  200 | matrix_bridge_steam_provisioning_shared_secret: [REDACTED_LITERAL]
  201 | 
  202 | # Minimum severity of journal log messages.
  203 | # Valid values: fatal, error, warn, info, debug, trace
  204 | matrix_bridge_steam_logging_level: 'warn'
  205 | 
  206 | # Default configuration template which covers the generic use case.
  207 | # You can customize it by controlling the various variables inside it.
  208 | #
  209 | # For a more advanced customization, you can extend the default (see `matrix_bridge_steam_configuration_extension_yaml`)
  210 | # or completely replace this variable with your own template.
  211 | matrix_bridge_steam_configuration_yaml: "{{ lookup('template', 'templates/config.yaml.j2') }}"
  212 | 
  213 | matrix_bridge_steam_configuration_extension_yaml: |
  214 |   # Your custom YAML configuration goes here.
  215 |   # This configuration extends the default starting configuration (`matrix_bridge_steam_configuration_yaml`).
  216 |   #
  217 |   # You can override individual variables from the default configuration, or introduce new ones.
  218 |   #
  219 |   # If you need something more special, you can take full control by
  220 |   # completely redefining `matrix_bridge_steam_configuration_yaml`.
  221 | 
  222 | matrix_bridge_steam_configuration_extension: "{{ matrix_bridge_steam_configuration_extension_yaml | from_yaml if matrix_bridge_steam_configuration_extension_yaml | from_yaml is mapping else {} }}"
  223 | 
  224 | # Holds the final configuration (a combination of the default and its extension).
  225 | # You most likely don't need to touch this variable. Instead, see `matrix_bridge_steam_configuration_yaml`.
  226 | matrix_bridge_steam_configuration: "{{ matrix_bridge_steam_configuration_yaml | from_yaml | combine(matrix_bridge_steam_configuration_extension, recursive=True) }}"
  227 | 
  228 | matrix_bridge_steam_registration_yaml: |
  229 |   id: steam
  230 |   as_token: "{{ matrix_bridge_steam_appservice_token }}"
  231 |   hs_token: "{{ matrix_bridge_steam_homeserver_token }}"
  232 |   namespaces:
  233 |     users:
  234 |     - exclusive: true
  235 |       regex: '^@steam_.+:{{ matrix_bridge_steam_homeserver_domain | regex_escape }}$'
  236 |     - exclusive: true
  237 |       regex: '^@{{ matrix_bridge_steam_appservice_bot_username | regex_escape }}:{{ matrix_bridge_steam_homeserver_domain | regex_escape }}$'
  238 |   url: {{ matrix_bridge_steam_appservice_address }}
  239 |   sender_localpart: _bot_{{ matrix_bridge_steam_appservice_bot_username }}
  240 |   rate_limited: false
  241 |   de.sorunome.msc2409.push_ephemeral: true
  242 |   receive_ephemeral: true
  243 |   io.element.msc4190: {{ matrix_bridge_steam_msc4190_enabled | to_json }}
  244 | 
  245 | matrix_bridge_steam_registration: "{{ matrix_bridge_steam_registration_yaml | from_yaml }}"
  246 | 
  247 | # Enable End-to-bridge encryption
  248 | matrix_bridge_steam_bridge_encryption_allow: "{{ matrix_bridges_encryption_enabled }}"
  249 | matrix_bridge_steam_bridge_encryption_default: "{{ matrix_bridges_encryption_default }}"
  250 | matrix_bridge_steam_bridge_encryption_require: false
  251 | matrix_bridge_steam_bridge_encryption_appservice: false
  252 | matrix_bridge_steam_bridge_encryption_key_sharing_allow: "{{ matrix_bridge_steam_bridge_encryption_allow }}"
  253 | matrix_bridge_steam_bridge_encryption_pickle_key: mautrix.bridge.e2ee
  254 | 
  255 | # matrix_bridge_steam_restart_necessary controls whether the service
  256 | # will be restarted (when true) or merely started (when false) by the
  257 | # systemd service manager role (when conditional restart is enabled).
  258 | #
  259 | # This value is automatically computed during installation based on whether
  260 | # any configuration files, the systemd service file, or the container image changed.
  261 | # The default of `false` means "no restart needed" — appropriate when the role's
  262 | # installation tasks haven't run (e.g., due to --tags skipping them).
  263 | matrix_bridge_steam_restart_necessary: false
```
