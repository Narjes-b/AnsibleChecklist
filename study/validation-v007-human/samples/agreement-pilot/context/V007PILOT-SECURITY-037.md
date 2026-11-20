# Frozen source context: V007PILOT-SECURITY-037

- Repository: `compscidr/iac`
- Commit: `350e7b8162778ad7beab8e2da8be53ea24a1127a`
- Family: Security
- Rule: `ansibleguard/insecure-permissions`
- Codebook: `codebooks/FAMILY_SECURITY.md`
- Source: `ansible/roles/media_server/tasks/main.yml` (reported anchor line 142)
- Object: `source_location` `14f167725e9caed59a0baa6879ecb2016bbb18fbf675f2d69e9c7910c2fd13ba`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: non-default literals associated with sensitive keys and recognizable provider tokens are redacted; listed public defaults may remain visible for rule assessment.

## Source excerpt

Lines 1–297 of 297:

```text
    1 | ---
    2 | # Ensure variables are set before including roles
    3 | # (Role defaults don't pass through to included collection roles)
    4 | # media_user_user/media_user_group/media_storage_base_path/
    5 | # media_storage_network_enabled/media_storage_network_name are the
    6 | # documented interface vars of the external compscidr.media_server
    7 | # collection's media_user/media_storage roles (included below), so they
    8 | # intentionally do not carry a media_server_ prefix.
    9 | - name: Set media defaults # noqa: var-naming[no-role-prefix]
   10 |   tags: always
   11 |   ansible.builtin.set_fact:
   12 |     media_user_user: jason
   13 |     media_user_group: admin
   14 |     media_storage_base_path: /volume1/storage
   15 |     media_storage_network_enabled: true
   16 |     media_storage_network_name: "media"
   17 |     media_server_media_letsencrypt_email: "ernstjason1@gmail.com"
   18 | 
   19 | # Initialize media_user facts (UID/GID detection) before other tasks
   20 | # This runs media_storage which depends on media_user
   21 | - name: Initialize media storage and user facts
   22 |   tags: always
   23 |   ansible.builtin.include_role:
   24 |     name: compscidr.media_server.media_storage
   25 |     apply:
   26 |       become: true
   27 | 
   28 | # Nginx reverse proxy + LetsEncrypt for SSL certs
   29 | - name: Create nginx config directory
   30 |   tags: nginx
   31 |   become: true
   32 |   ansible.builtin.file:
   33 |     path: /etc/nginx-proxy/conf.d
   34 |     state: directory
   35 |     mode: "755"
   36 |     owner: root
   37 |     group: root
   38 | 
   39 | - name: Copy nginx config
   40 |   tags: nginx
   41 |   become: true
   42 |   ansible.builtin.copy:
   43 |     content: "client_max_body_size 100m;"
   44 |     dest: /etc/nginx-proxy/conf.d/client_max_body_size.conf
   45 |     mode: "644"
   46 |     owner: root
   47 |     group: root
   48 | 
   49 | - name: Deploy Nginx Reverse Proxy
   50 |   tags: nginx
   51 |   become: true
   52 |   community.docker.docker_container:
   53 |     name: nginx-proxy
   54 |     image: jwilder/nginx-proxy
   55 |     published_ports:
   56 |       - "80:80"
   57 |       - "443:443"
   58 |     volumes:
   59 |       - /etc/nginx-proxy/conf.d:/etc/nginx/conf.d
   60 |       - nginx-vhost:/etc/nginx/vhost.d
   61 |       - nginx-html:/usr/share/nginx/html
   62 |       - nginx-dhparam:/etc/nginx/dhparam
   63 |       - nginx-certs:/etc/nginx/certs:ro
   64 |       - /var/run/docker.sock:/tmp/docker.sock:ro
   65 |     networks:
   66 |       - name: media
   67 |     restart_policy: unless-stopped
   68 | 
   69 | - name: Deploy LetsEncrypt companion
   70 |   tags: letsencrypt
   71 |   become: true
   72 |   community.docker.docker_container:
   73 |     name: letsencrypt
   74 |     image: jrcs/letsencrypt-nginx-proxy-companion
   75 |     volumes:
   76 |       - nginx-certs:/etc/nginx/certs:rw
   77 |       - nginx-vhost:/etc/nginx/vhost.d
   78 |       - nginx-html:/usr/share/nginx/html
   79 |       - /var/run/docker.sock:/var/run/docker.sock:ro
   80 |     env:
   81 |       NGINX_PROXY_CONTAINER: "nginx-proxy"
   82 |     networks:
   83 |       - name: media
   84 |     restart_policy: unless-stopped
   85 | 
   86 | # NAS web UI reverse proxy (proxies nas.jasonernst.com -> host port 9999)
   87 | - name: Create NAS proxy config directory
   88 |   tags: nas-proxy
   89 |   become: true
   90 |   ansible.builtin.file:
   91 |     path: /etc/nas-proxy
   92 |     state: directory
   93 |     mode: "755"
   94 |     owner: root
   95 |     group: root
   96 | 
   97 | - name: Copy NAS proxy nginx config
   98 |   tags: nas-proxy
   99 |   become: true
  100 |   ansible.builtin.copy:
  101 |     src: nas-proxy.conf
  102 |     dest: /etc/nas-proxy/default.conf
  103 |     mode: "644"
  104 |     owner: root
  105 |     group: root
  106 |   notify: Restart nas-proxy container
  107 | 
  108 | - name: Deploy NAS web proxy
  109 |   tags: nas-proxy
  110 |   become: true
  111 |   community.docker.docker_container:
  112 |     name: nas-proxy
  113 |     image: nginx:alpine
  114 |     pull: true
  115 |     volumes:
  116 |       - /etc/nas-proxy/default.conf:/etc/nginx/conf.d/default.conf:ro
  117 |     env:
  118 |       VIRTUAL_HOST: "nas.jasonernst.com"
  119 |       VIRTUAL_PORT: "80"
  120 |       LETSENCRYPT_HOST: "nas.jasonernst.com"
  121 |       LETSENCRYPT_EMAIL: "{{ media_server_media_letsencrypt_email | default('ernstjason1@gmail.com') }}"
  122 |     etc_hosts:
  123 |       host.docker.internal: host-gateway
  124 |     networks:
  125 |       - name: media
  126 |     restart_policy: unless-stopped
  127 |     memory: "256m"
  128 | 
  129 | # Media storage folders are now created automatically by the media_storage role
  130 | # which is a dependency of the media roles below
  131 | 
  132 | - name: Create Transmission Directories
  133 |   tags: transmission
  134 |   become: true
  135 |   ansible.builtin.file:
  136 |     path: "/etc/transmission/"
  137 |     state: directory
  138 |     mode: "755"
  139 |     owner: "{{ media_user_user }}"
  140 |     group: "{{ media_user_group }}"
  141 | 
  142 | - name: Set transmission nordvpn credentials
  143 |   tags: transmission
  144 |   become: true
  145 |   ansible.builtin.copy:
  146 |     mode: "755"
  147 |     owner: "{{ media_user_user }}"
  148 |     group: "{{ media_user_group }}"
  149 |     dest: "/etc/transmission/.env"
  150 |     content: |
  151 |       TRANSMISSION_WEB_UI=transmission-web-control
  152 |       OPENVPN_PROVIDER=NORDVPN
  153 |       NORDVPN_PROTOCOL=udp
  154 |       OPENVPN_USERNAME={{ lookup('community.general.onepassword', 'NordVPN Manual', field='username', vault=onepassword_vault,
  155 |         account_id=onepassword_account_id) }}
  156 |       OPENVPN_PASSWORD={{ lookup('community.general.onepassword', 'NordVPN Manual', field='credential', vault=onepassword_vault,
  157 |         account_id=onepassword_account_id) }}
  158 |       NORDVPN_COUNTRY=US
  159 |       NORDVPN_CATEGORY=P2P
  160 |       LOCAL_NETWORK=192.168.0.0/24
  161 |       HEALTH_CHECK_HOST=8.8.8.8
  162 | 
  163 | - name: Install transmission
  164 |   tags: transmission
  165 |   ansible.builtin.include_role:
  166 |     name: compscidr.media_server.transmission
  167 |     apply:
  168 |       become: true
  169 |       tags: transmission
  170 |   vars:
  171 |     transmission_folder: /etc/transmission
  172 |     transmission_memory: "5g"
  173 |     transmission_memory_swap: "5g"
  174 | 
  175 | - name: Install plex
  176 |   tags: plex
  177 |   ansible.builtin.include_role:
  178 |     name: compscidr.media_server.plex
  179 |     apply:
  180 |       become: true
  181 |       tags: plex
  182 |   vars:
  183 |     plex_folder: "{{ media_storage_base_path }}/plex"
  184 |     plex_dri_devices: true
  185 |     plex_bonjour_port: 5354
  186 |     plex_claim: claim-haziyvUxG2Fb4uj5-tF1
  187 |     plex_memory: "24g"
  188 |     plex_memory_swap: "24g"
  189 |     plex_shm_size: "8g"
  190 |     plex_virtual_host: "plex.jasonernst.com"
  191 |     plex_letsencrypt_email: "{{ media_server_media_letsencrypt_email }}"
  192 |     plex_network_mode: "bridge"
  193 |     plex_dlna_port: 1901
  194 | 
  195 | - name: Install sabnzbd
  196 |   tags: sabnzbd
  197 |   ansible.builtin.include_role:
  198 |     name: compscidr.media_server.sabnzbd
  199 |     apply:
  200 |       become: true
  201 |       tags: sabnzbd
  202 |   vars:
  203 |     sabnzbd_memory: "5g"
  204 |     sabnzbd_memory_swap: "5g"
  205 | 
  206 | - name: Install sonarr
  207 |   tags: sonarr
  208 |   ansible.builtin.include_role:
  209 |     name: compscidr.media_server.sonarr
  210 |     apply:
  211 |       become: true
  212 |       tags: sonarr
  213 |   vars:
  214 |     sonarr_folder: /etc/sonarr
  215 |     sonarr_memory: "1g"
  216 |     sonarr_memory_swap: "1g"
  217 |     sonarr_virtual_host: "sonarr.jasonernst.com"
  218 |     sonarr_letsencrypt_email: "{{ media_server_media_letsencrypt_email }}"
  219 | 
  220 | - name: Install radarr
  221 |   tags: radarr
  222 |   ansible.builtin.include_role:
  223 |     name: compscidr.media_server.radarr
  224 |     apply:
  225 |       become: true
  226 |       tags: radarr
  227 |   vars:
  228 |     radarr_memory: "1g"
  229 |     radarr_memory_swap: "1g"
  230 |     radarr_virtual_host: "radarr.jasonernst.com"
  231 |     radarr_letsencrypt_email: "{{ media_server_media_letsencrypt_email }}"
  232 | 
  233 | - name: Install prowlarr
  234 |   tags: prowlarr
  235 |   ansible.builtin.include_role:
  236 |     name: compscidr.media_server.prowlarr
  237 |     apply:
  238 |       become: true
  239 |       tags: prowlarr
  240 |   vars:
  241 |     prowlarr_memory: "1g"
  242 |     prowlarr_memory_swap: "1g"
  243 | 
  244 | - name: Install flaresolverr
  245 |   tags: flaresolverr
  246 |   ansible.builtin.include_role:
  247 |     name: compscidr.media_server.flaresolverr
  248 |     apply:
  249 |       become: true
  250 |       tags: flaresolverr
  251 |   vars:
  252 |     flare_port: 8191
  253 | 
  254 | - name: Install ombi
  255 |   tags: ombi
  256 |   ansible.builtin.include_role:
  257 |     name: compscidr.media_server.ombi
  258 |     apply:
  259 |       become: true
  260 |       tags: ombi
  261 |   vars:
  262 |     ombi_virtual_host: "ombi.jasonernst.com"
  263 |     ombi_letsencrypt_email: "{{ media_server_media_letsencrypt_email }}"
  264 | 
  265 | - name: Install slskd
  266 |   tags: slskd
  267 |   ansible.builtin.include_role:
  268 |     name: compscidr.media_server.slskd
  269 |     apply:
  270 |       become: true
  271 |       tags: slskd
  272 |   vars:
  273 |     slskd_memory: "1g"
  274 |     slskd_memory_swap: "1g"
  275 | 
  276 | - name: Install soularr
  277 |   tags: soularr
  278 |   ansible.builtin.include_role:
  279 |     name: compscidr.media_server.soularr
  280 |     apply:
  281 |       become: true
  282 |       tags: soularr
  283 |   vars:
  284 |     soularr_memory: "1g"
  285 |     soularr_memory_swap: "1g"
  286 | 
  287 | - name: Install lidarr
  288 |   tags: lidarr
  289 |   ansible.builtin.include_role:
  290 |     name: compscidr.media_server.lidarr
  291 |     apply:
  292 |       become: true
  293 |       tags: lidarr
  294 |   vars:
  295 |     lidarr_plugins: true
  296 |     lidarr_memory: "1g"
  297 |     lidarr_memory_swap: "1g"
```
