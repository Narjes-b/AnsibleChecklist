# Frozen source context: V007PILOT2-OBJECTIVE_CORRECTNESS-012

- Repository: `anthonymolinari/ansible-gitops`
- Commit: `61aa79a0c1f6641317187d3a7afec6b6c4d54a5f`
- Family: objective_correctness
- Rule: `ansibleguard/redirected-module`
- Codebook: `codebooks-v2/FAMILY_OBJECTIVE_CORRECTNESS_V2.md`
- Source: `tasks/main/containers.yml` (reported anchor line 265)
- Flagged construct: task `deploy shelfmark`
- Evidence source: Git blob at the frozen commit; no current worktree content was used.
- Redaction: v1 sensitive-key redaction plus second-pass redaction of emails, tokens and base64 blocks.

## Source excerpt

Lines 1–313 of 313:

```text
    1 | ---
    2 | 
    3 | # node exporter
    4 | - name: node-exporter
    5 |   docker_container:
    6 |     name: node-exporter
    7 |     image: prom/node-exporter:v1.12.1
    8 |     command: ["--path.rootfs=/host"]
    9 |     ports:
   10 |       - "9100:9100"
   11 |     volumes:
   12 |       - "/:/host:ro,rslave"
   13 |     restart_policy: unless-stopped
   14 | 
   15 | # uptime kuma
   16 | - name: uptime kuma
   17 |   docker_container:
   18 |     name: uptime-kuma
   19 |     image: louislam/uptime-kuma:2
   20 |     ports:
   21 |       - "3001:3001"
   22 |     volumes:
   23 |       - "{{ docker_path }}/uptime-kuma/data:/app/data"
   24 |       - "/var/run/docker.sock:/var/run/docker.sock"
   25 |     env:
   26 |       TZ: "{{ timezone }}"
   27 |     restart_policy: unless-stopped
   28 | 
   29 | # nvidia exporter
   30 | - name: gpu-exporter
   31 |   docker_container:
   32 |     name: nvidia-smi-exporter
   33 |     image: nvcr.io/nvidia/k8s/dcgm-exporter:3.3.5-3.4.0-ubuntu22.04
   34 |     ports:
   35 |       - "9400:9400"
   36 |     networks:
   37 |       - name: "metrics"
   38 |       - name: "traefik"
   39 |     device_requests:
   40 |       - device_ids: 0
   41 |         driver: nvidia
   42 |         capabilities:
   43 |           - gpu
   44 |           - compute
   45 |           - utility
   46 |     restart_policy: unless-stopped
   47 | 
   48 | # plex
   49 | - name: plex
   50 |   community.docker.docker_container:
   51 |     name: plex
   52 |     image: linuxserver/plex:1.43.3
   53 |     volumes:
   54 |       - "{{ media_dir }}:/Media"
   55 |       - "{{ docker_path }}/plex/config:/config"
   56 |     ports:
   57 |       - "32400:32400"
   58 |       - "5353:5353/udp"
   59 |       - "8324:8324/tcp"
   60 |       - "32410:32410/udp"
   61 |       - "32412:32412/udp"
   62 |       - "32413:32413/udp"
   63 |       - "32469:32469/tcp"
   64 |     device_requests:
   65 |       - device_ids: 0
   66 |         driver: nvidia
   67 |         capabilities:
   68 |           - gpu
   69 |           - compute
   70 |           - utility
   71 |     env:
   72 |       PUID: "1000"
   73 |       PGID: "1000"
   74 |       VERSION: "docker"
   75 |     restart_policy: unless-stopped
   76 | 
   77 | # tdarr 
   78 | - name: tdarr
   79 |   community.docker.docker_container:
   80 |     name: tdarr
   81 |     image: haveagitgat/tdarr:2.86.01 
   82 |     ports:
   83 |       - "8265:8265"
   84 |       - "8266:8266"
   85 |     volumes:
   86 |       - "{{ docker_path }}/tdarr/server:/app/server"
   87 |       - "{{ docker_path }}/tdarr/configs:/app/config"
   88 |       - "{{ docker_path }}/tdarr/logs:/app/logs"
   89 |       - "{{ media_dir }}:/media"
   90 |       - "/transcode_cache:/temp"
   91 |     device_requests:
   92 |       - device_ids: 0
   93 |         driver: nvidia
   94 |         capabilities:
   95 |           - gpu
   96 |           - compute
   97 |           - utility
   98 |     env:
   99 |       serverIP: "0.0.0.0"
  100 |       serverPort: "8266"
  101 |       webUIPort: "8265"
  102 |       internalNode: "true"
  103 |       inContainer: "true"
  104 |       ffmpegVersion: "6"
  105 |       nodeName: "MyInternalNode"
  106 |       TZ: "{{ timezone }}"
  107 |       PUID: "1000"
  108 |       PGID: "1000"
  109 |       NVIDIA_DRIVER_CAPABILITIES: "all"
  110 |       NVIDIA_VISIBLE_DEVICES: "all"
  111 |     restart_policy: unless-stopped
  112 | 
  113 | # sonarr
  114 | - name: sonarr
  115 |   docker_container:
  116 |     name: sonarr
  117 |     image: linuxserver/sonarr:4.0.19-develop   
  118 |     ports:
  119 |       - "8989:8989"
  120 |     volumes:
  121 |       - "{{ docker_path }}/sonarr/config:/config"
  122 |       - "{{ media_dir }}:/tv"
  123 |       - "{{ downloads_dir }}/torrents:/downloads"
  124 |     env:
  125 |       PGID: "1000"
  126 |       PUID: "1000"
  127 |       TZ: "{{ timezone }}"
  128 |     restart_policy: unless-stopped
  129 | 
  130 | # radarr
  131 | - name: radarr
  132 |   docker_container:
  133 |     name: radarr
  134 |     image: linuxserver/radarr@sha256:119aaa4a4f7349bcd2a136c5373a0d7925b5479915c7dfe0c0ad352db2a6d438    
  135 |     ports:
  136 |       - "7878:7878"
  137 |     volumes:
  138 |       - "{{ docker_path }}/radarr/config:/config"
  139 |       - "{{ media_dir }}:/movies"
  140 |       - "{{ downloads_dir }}/torrents:/downloads"
  141 |     env:
  142 |       PGID: "1000"
  143 |       PUID: "1000"
  144 |       TZ: "{{ timezone }}"
  145 |     restart_policy: unless-stopped
  146 | 
  147 | # bazarr
  148 | - name: deploy bazarr
  149 |   docker_container:
  150 |     name: bazarr
  151 |     image: lscr.io/linuxserver/bazarr:latest
  152 |     ports:
  153 |       - "6767:6767"
  154 |     volumes:
  155 |       - "{{ docker_path }}/bazarr/config:/config"
  156 |       - "{{ media_dir }}:/media"
  157 |     env:
  158 |       PUID: "1000"
  159 |       PGID: "1000"
  160 |       TZ: "{{ timezone }}"
  161 |     restart_policy: unless-stopped
  162 | 
  163 | # overseerr
  164 | - name: deploy overseerr
  165 |   docker_container:
  166 |     name: overseerr
  167 |     image: sctx/overseerr:1.35.0
  168 |     ports:
  169 |       - "5055:5055"
  170 |     volumes:
  171 |       - "{{ docker_path }}/overseerr/config:/app/config"
  172 |     env:
  173 |       LOG_LEVEL: "debug"
  174 |       TZ: "{{ timezone }}"
  175 |     restart_policy: unless-stopped
  176 | 
  177 | # pia-vpn-container
  178 | - name: deploy vpn-client container
  179 |   docker_container:
  180 |     name: vpn
  181 |     image: dperson/openvpn-client@sha256:d174047b57d51734143325ad7395210643025e6516ba60a937e9319dbb462293
  182 |     volumes:
  183 |       - "{{ docker_path }}/vpn-client:/vpn"
  184 |     ports:
  185 |       - "9696:9696" # prowlarr webui
  186 |       - "9091:9091" # transmission webui
  187 |     restart_policy: unless-stopped
  188 |     capabilities:
  189 |       - "NET_ADMIN"
  190 |     devices:
  191 |       - "/dev/net/tun"
  192 |     env:
  193 |       VPN: "{{ vpn_arg }}"
  194 |       ROUTE: 172.24.10.0/24
  195 | 
  196 | # prowlarr
  197 | - name: deploy prowlarr behind vpn
  198 |   docker_container:
  199 |     name: prowlarr
  200 |     image: linuxserver/prowlarr@sha256:ab91301778251f82a31bbfc87f0497376d59e84439d9a1ceff6a61d594d1e3d7
  201 |     volumes:
  202 |       - "{{ docker_path }}/prowlarr/config:/config"
  203 |     env:
  204 |       PUID: "1000"
  205 |       PGID: "1000"
  206 |     network_mode: container:vpn
  207 |     restart_policy: unless-stopped
  208 | 
  209 | # transmission
  210 | - name: deploy transmission behind vpn
  211 |   docker_container:
  212 |     name: transmission
  213 |     image: linuxserver/transmission:4.1.3
  214 |     volumes:
  215 |       - "{{ docker_path }}/transmission/config:/config"
  216 |       - "{{ downloads_dir }}/torrents:/downloads"
  217 |     env:
  218 |       PUID: "1000"
  219 |       PGID: "1000"
  220 |       TZ: "{{ timezone }}"
  221 |     network_mode: container:vpn
  222 |     restart_policy: unless-stopped
  223 | 
  224 | # scrutiny disk metrics
  225 | - name: deploy scrutiny disk metrics
  226 |   docker_container:
  227 |     name: scrutiny
  228 |     image: ghcr.io/analogj/scrutiny:master-omnibus
  229 |     ports:
  230 |       - "8181:8080" # webapp
  231 |       - "8086:8086" # influxdb admin
  232 |     volumes:
  233 |       - "{{ docker_path }}/scrutiny/config:/opt/scrutiny/config"
  234 |       - "{{ docker_path }}/scrutiny/influxdb:/opt/scrutiny/influxdb"
  235 |       - "/run/udev:/run/udev:ro"
  236 |     capabilities:
  237 |       - "SYS_RAWIO"
  238 |     devices:
  239 |       - "/dev/sda"
  240 |       - "/dev/sdb"
  241 |       - "/dev/sdc"
  242 |       - "/dev/sdd"
  243 |       - "/dev/sde"
  244 |     restart_policy: unless-stopped
  245 | 
  246 | - name: deploy calibre web automated
  247 |   docker_container:
  248 |     name: calibre-web-automated
  249 |     image: crocodilestick/calibre-web-automated:latest
  250 |     ports:
  251 |       - "8083:8083"
  252 |     volumes:
  253 |       - "{{ docker_path }}/calibre-automated/config:/config"
  254 |       - "{{ media_dir }}/Books/ingest:/cwa-book-ingest"
  255 |       - "{{ docker_path }}/calibre/config/Calibre Library:/calibre-library"
  256 |     env:
  257 |       PUID: "1000"
  258 |       PGID: "1000"
  259 |       TZ: "{{ timezone }}"
  260 |       HARDCOVER_TOKEN: "{{ hardcover_token }}"
  261 |     restart_policy: unless-stopped
  262 | 
  263 | # shelfmark
  264 | - name: deploy shelfmark
  265 |   docker_container:
  266 |     name: shelfmark
  267 |     image: ghcr.io/calibrain/shelfmark:latest
  268 |     ports:
  269 |       - "8084:8084"
  270 |     volumes:
  271 |       - "{{ docker_path }}/shelfmark/config:/config"
  272 |       - "{{ media_dir }}/Books/ingest:/books" # ingest for cwa
  273 |       - "{{ docker_path }}/calibre/config:/calibre"
  274 |       - "{{ downloads_dir }}/torrents:/downloads"
  275 |     env:
  276 |       PUID: "1000"
  277 |       PGID: "1000"
  278 |     restart_policy: unless-stopped
  279 | 
  280 | # immich 
  281 | #- name: immich - deploy redis 
  282 | # docker_container:
  283 | #   name: immich_redis
  284 | #   image: 
  285 | #   ports:
  286 | #   volumes:
  287 | #   env:
  288 | #   restart_policy: unless-stopped
  289 | 
  290 | #- name: immich - deploy postgres 
  291 | # docker_container:
  292 | #   name: immich_database
  293 | #   image: ghcr.io/immich-app/postgres:14-vectorchord0.4.3-pgvectors0.2.0@sha256:bcf63357191b76a916ae5eb93464d65c07511da41e3bf7a8416db519b40b1c23
  294 | #   ports: 
  295 | #   volumes:
  296 | #     - "{{ docker_path }}"
  297 | #   env:
  298 | #     POSTGRES_PASSWORD: "{{ DB_PASSWORD }}"
  299 | #     POSTGRES_USER: "{{ DB_USERNAME }}"
  300 | #     POSTGRES_DB: "{{ DB_DATABASE_NAME }}"
  301 | #     POSTGRES_INITDB_ARGS: "'--data-checksums'"
  302 | #   restart_policy: unless-stopped
  303 | 
  304 | #- name: immich - deploy server
  305 | # docker_container:
  306 | #   name: immich_server
  307 | #   image:
  308 | #   ports:
  309 | #   volumes:
  310 | #   env:
  311 | #   restart_policy: unless-stopped
  312 | 
  313 | 
```
