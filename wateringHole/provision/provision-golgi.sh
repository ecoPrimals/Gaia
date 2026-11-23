#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# provision-golgi.sh — Rebuild golgi VPS from a fresh Debian 12 droplet
#
# This script provisions the "thin edge" relay layer of the Sovereign Relay
# Architecture. golgi serves as the public ingress surface, running only:
#
#   - Forgejo    (sovereign git forge, SSH on :2222, HTTP on :3000)
#                Bare repos are SHALLOW (depth=1) — full history lives on
#                sporeGate at /opt/forgejo-mirror/. Pushes work normally;
#                periodic re-shallowing keeps disk thin.
#   - Caddy      (TLS on :443 for ALL domains — Host routing, ACME, HTTP/2)
#   - bearDog    (crypto identity + BTSP — ACME gateway standby on internal port)
#   - membrane   (temporal.cascade — Forgejo→sporeGate sync + freshness)
#   - songBird   (mesh federation hub + TURN relay)
#   - bearDog    (crypto identity + BTSP security provider)
#   - WireGuard  (backhaul tunnel to sporeGate LAN)
#   - fail2ban   (SSH brute-force protection)
#
# Prerequisites:
#   - Fresh Debian 12 (bookworm) VPS with ≥10GB disk, ≥2GB RAM
#   - sporeGate NUC online with full Forgejo mirror at /opt/forgejo-mirror/
#   - WireGuard keys generated for new droplet
#   - SSH access from sporeGate to new VPS
#
# Usage:
#   export GOLGI_IP=<new-vps-public-ip>
#   export SPOREGATE_WG_PUBKEY=<sporeGate-wg-pubkey>
#   export GOLGI_WG_PRIVKEY=<new-wg-private-key>
#   bash provision-golgi.sh
#
# Recovery from sporeGate:
#   1. Create new droplet
#   2. Set env vars above
#   3. Run this script via SSH
#   4. rsync SHALLOW Forgejo repos from sporeGate mirror:
#        bash provision-golgi-shallow-repos.sh   (or run inline — see bottom of file)
#      OR restore full history then shallow later:
#        rsync -avz /opt/forgejo-mirror/ root@$GOLGI_IP:/opt/forgejo/data/repositories/
#   5. rsync pepti depot:
#        rsync -avz /opt/ecoPrimals/depot/ root@$GOLGI_IP:/opt/ecoPrimals/depot/
#   6. Start services: systemctl start forgejo caddy-tls beardog-membrane beardog-sporeprint songbird-membrane songbird-relay cascade-sense.timer

set -euo pipefail

GOLGI_IP="${GOLGI_IP:?Set GOLGI_IP to the VPS public IP}"

echo "=== 1. SYSTEM BASE ==="
apt-get update && apt-get upgrade -y
apt-get install -y \
    wireguard \
    fail2ban \
    git \
    curl \
    rsync \
    jq \
    sqlite3 \
    socat \
    zola

grep -q 'DEPOT_TRUST_POLICY' /etc/environment 2>/dev/null || \
    echo 'DEPOT_TRUST_POLICY=require-signed' >> /etc/environment

echo "=== 2. CREATE USERS + DIRECTORIES ==="
adduser --system --shell /bin/bash --home /opt/forgejo --group git 2>/dev/null || true
mkdir -p /opt/forgejo/{custom/conf,data/repositories}
mkdir -p /opt/membrane
mkdir -p /opt/ecoPrimals/{depot/{x86_64-unknown-linux-musl,aarch64-unknown-linux-musl},infra/wateringHole/heads}
mkdir -p /etc/membrane
mkdir -p /run/membrane
mkdir -p /etc/songbird

echo "golgiBody" > /etc/membrane/gate-name

echo "=== 3. INSTALL FORGEJO ==="
FORGEJO_VERSION="10.0.1"
curl -sL "https://codeberg.org/forgejo/forgejo/releases/download/v${FORGEJO_VERSION}/forgejo-${FORGEJO_VERSION}-linux-amd64" \
    -o /usr/local/bin/forgejo
chmod +x /usr/local/bin/forgejo

cat > /opt/forgejo/custom/conf/app.ini << 'EOINI'
APP_NAME = ecoPrimals Forge
RUN_USER = git
RUN_MODE = prod
WORK_PATH = /opt/forgejo

[database]
DB_TYPE = sqlite3
PATH = /opt/forgejo/data/forgejo.db

[repository]
ROOT = /opt/forgejo/data/repositories

[server]
DOMAIN = git.primals.eco
SSH_DOMAIN = git.primals.eco
HTTP_ADDR = 127.0.0.1
HTTP_PORT = 3000
ROOT_URL = https://git.primals.eco/
DISABLE_SSH = false
START_SSH_SERVER = true
SSH_PORT = 2222
SSH_LISTEN_HOST = 0.0.0.0
SSH_LISTEN_PORT = 2222
LFS_START_SERVER = true

[service]
DISABLE_REGISTRATION = true
REQUIRE_SIGNIN_VIEW = false
EOINI

chown -R git:git /opt/forgejo

echo "=== 4. INSTALL CADDY ==="
curl -sL "https://caddyserver.com/api/download?os=linux&arch=amd64" -o /opt/membrane/caddy
chmod +x /opt/membrane/caddy

cat > /etc/membrane/Caddyfile << 'EOCADDY'
# Membrane Channel 3 — Caddy TLS Surface (Hardened — Wave 136b)
#
# Caddy handles :443 for ALL domains (Host-based routing, HTTP/2, ACME).
# Security headers + CSP on all public-facing domains.
# Per-site JSON access logs feed skunkBat baseline.observe pipeline.
{
    email ops@primals.eco
    storage file_system /caddy
}

# Common security headers
(security_headers) {
    header {
        Strict-Transport-Security "max-age=63072000; includeSubDomains; preload"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "DENY"
        X-XSS-Protection "0"
        Referrer-Policy "strict-origin-when-cross-origin"
        Permissions-Policy "camera=(), microphone=(), geolocation=(), interest-cohort=()"
        -Server
    }
}

# Per-site structured access log (feeds skunkBat ingestion pipeline)
(access_log) {
    log {
        output file /var/log/caddy/access.log {
            roll_size 50MiB
            roll_keep 5
            roll_keep_for 720h
        }
        format json
    }
}

# CSP for static Zola site (self-hosted assets + inline search/nav JS)
(csp_static) {
    header Content-Security-Policy "default-src 'none'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; form-action 'none'; frame-ancestors 'none'; base-uri 'self'; manifest-src 'self'"
}

# CSP for reverse-proxied services (more permissive)
(csp_proxy) {
    header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self' wss:; frame-ancestors 'none'"
}

# footPrint GIS External Proxy — 10 upstream services via /footprint/ext/{service}/
(footprint_gis_proxy) {
    handle_path /footprint/ext/overpass/* {
        reverse_proxy https://overpass-api.de {
            header_up Host overpass-api.de
            transport http {
                tls
            }
        }
    }
    handle_path /footprint/ext/fema/* {
        reverse_proxy https://hazards.fema.gov {
            header_up Host hazards.fema.gov
            transport http {
                tls
            }
        }
    }
    handle_path /footprint/ext/arcgis1/* {
        reverse_proxy https://services1.arcgis.com {
            header_up Host services1.arcgis.com
            transport http {
                tls
            }
        }
    }
    handle_path /footprint/ext/arcgis2/* {
        reverse_proxy https://services2.arcgis.com {
            header_up Host services2.arcgis.com
            transport http {
                tls
            }
        }
    }
    handle_path /footprint/ext/nominatim/* {
        reverse_proxy https://nominatim.openstreetmap.org {
            header_up Host nominatim.openstreetmap.org
            transport http {
                tls
            }
        }
    }
    handle_path /footprint/ext/usgs/* {
        reverse_proxy https://epqs.nationalmap.gov {
            header_up Host epqs.nationalmap.gov
            transport http {
                tls
            }
        }
    }
    handle_path /footprint/ext/nrcs/* {
        reverse_proxy https://sdmdataaccess.sc.egov.usda.gov {
            header_up Host sdmdataaccess.sc.egov.usda.gov
            transport http {
                tls
            }
        }
    }
    handle_path /footprint/ext/michigan/* {
        reverse_proxy https://gisagocss.state.mi.us {
            header_up Host gisagocss.state.mi.us
            transport http {
                tls
            }
        }
    }
    handle_path /footprint/ext/mcgi/* {
        reverse_proxy https://gisp.mcgi.state.mi.us {
            header_up Host gisp.mcgi.state.mi.us
            transport http {
                tls
            }
        }
    }
    handle_path /footprint/ext/eastlansing/* {
        reverse_proxy https://gis2.cityofeastlansing.com {
            header_up Host gis2.cityofeastlansing.com
            transport http {
                tls
            }
        }
    }
}

# Sovereign public surface — primals.eco (sporePrint Zola site)
primals.eco {
    import security_headers
    import csp_static
    import access_log
    encode gzip

    handle /lab/spores/* {
        root * /opt/ecoPrimals/sporePrint/spores
        file_server browse
    }
    import footprint_gis_proxy
    handle_path /footprint/* {
        root * /opt/ecoPrimals/compositions/footprint/dist/client
        header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https://*.tile.openstreetmap.org https://*.arcgis.com; font-src 'self'; connect-src 'self'; frame-ancestors 'none'"
        encode gzip
        try_files {path} /index.html
        file_server
    }
    handle {
        root * /opt/ecoPrimals/sporePrint/public
        file_server
    }

    handle_errors {
        rewrite * /404.html
        root * /opt/ecoPrimals/sporePrint/public
        file_server
    }
}

www.primals.eco {
    redir https://primals.eco{uri} permanent
}

# Primary sovereign surface — membrane
membrane.primals.eco {
    import security_headers
    import csp_static
    import access_log
    encode gzip

    handle /depot/* {
        uri strip_prefix /depot
        root * /opt/ecoPrimals/depot
        file_server browse
    }
    handle /health {
        respond "membrane-relay TLS active" 200
    }
    handle /status {
        respond "Channel 3 — sovereign TLS operational" 200
    }
    handle /hooks/* {
        reverse_proxy unix//run/membrane/nestgate.sock
    }
    handle {
        root * /var/cache/membrane/nestgate
        file_server
    }
}

# Lab — songBird drawbridge to sporeGate (EXP-06 auth-gated)
lab.primals.eco {
    import security_headers
    import csp_proxy
    import access_log

    basicauth {
        sporegate {CADDY_LAB_BCRYPT_HASH}
    }

    reverse_proxy 10.13.37.2:7780 {
        header_up Host {host}
        header_up X-Real-IP {remote_host}
        header_up X-Forwarded-For {remote_host}
        header_up X-Forwarded-Proto {scheme}
        header_down -Content-Security-Policy
    }
}

# Forgejo — sovereign git forge
git.primals.eco {
    import security_headers
    import csp_proxy
    import access_log

    reverse_proxy localhost:3000
}

# live.primals.eco — petalTongue NUCLEUS on sporeGate (TOPO-VIS live topology)
live.primals.eco {
    import security_headers
    import csp_proxy
    import access_log

    reverse_proxy 10.13.37.2:9900 {
        header_up Host {host}
        header_up X-Real-IP {remote_host}
        header_up X-Forwarded-For {remote_host}
        header_up X-Forwarded-Proto {scheme}
    }
}

# ── Subdomain composition aliases ──
# Each subdomain serves the same Zola public/ directory but rewrites
# the root to a specific section. Single build, single source of truth.
# DNS: *.primals.eco wildcard A record — no Cloudflare changes needed.

docs.primals.eco {
    import security_headers
    import csp_static
    import access_log
    encode gzip

    handle / {
        redir https://primals.eco/architecture/ permanent
    }
    handle /llms.txt {
        root * /opt/ecoPrimals/sporePrint/public
        rewrite * /llms-docs.txt
        file_server
    }
    handle {
        root * /opt/ecoPrimals/sporePrint/public
        file_server
    }
    handle_errors {
        rewrite * /404.html
        root * /opt/ecoPrimals/sporePrint/public
        file_server
    }
}

science.primals.eco {
    import security_headers
    import csp_static
    import access_log
    encode gzip

    handle / {
        redir https://primals.eco/science/ permanent
    }
    handle /llms.txt {
        root * /opt/ecoPrimals/sporePrint/public
        rewrite * /llms-science.txt
        file_server
    }
    handle {
        root * /opt/ecoPrimals/sporePrint/public
        file_server
    }
    handle_errors {
        rewrite * /404.html
        root * /opt/ecoPrimals/sporePrint/public
        file_server
    }
}

atlas.primals.eco {
    import security_headers
    import csp_static
    import access_log
    encode gzip

    handle / {
        redir https://primals.eco/architecture/atlas-memory-palace/ permanent
    }
    handle /llms.txt {
        root * /opt/ecoPrimals/sporePrint/public
        rewrite * /llms-atlas.txt
        file_server
    }
    handle {
        root * /opt/ecoPrimals/sporePrint/public
        file_server
    }
    handle_errors {
        rewrite * /404.html
        root * /opt/ecoPrimals/sporePrint/public
        file_server
    }
}

products.primals.eco {
    import security_headers
    import csp_static
    import access_log
    encode gzip

    handle / {
        redir https://primals.eco/products/ permanent
    }
    handle /llms.txt {
        root * /opt/ecoPrimals/sporePrint/public
        rewrite * /llms-products.txt
        file_server
    }
    handle {
        root * /opt/ecoPrimals/sporePrint/public
        file_server
    }
    handle_errors {
        rewrite * /404.html
        root * /opt/ecoPrimals/sporePrint/public
        file_server
    }
}

# Wildcard catch-all — sovereign routing authority.
# Caddy handles all *.primals.eco routing via explicit blocks above.
# DNS: single *.primals.eco wildcard A record in Cloudflare (DNS only).
# New subdomains only need a Caddy block here — no Cloudflare changes.
*.primals.eco {
    tls {
        on_demand
    }
    import security_headers
    respond "Not found" 404
}
EOCADDY

echo "=== 5. INSTALL RUSTDESK SERVER ==="
RUSTDESK_VERSION="1.1.15"
curl -sL "https://github.com/rustdesk/rustdesk-server/releases/download/${RUSTDESK_VERSION}/rustdesk-server-linux-amd64.zip" \
    -o /tmp/rustdesk-server.zip
unzip -o /tmp/rustdesk-server.zip -d /tmp/rustdesk-extract
cp /tmp/rustdesk-extract/amd64/hbbs /opt/membrane/hbbs
cp /tmp/rustdesk-extract/amd64/hbbr /opt/membrane/hbbr
chmod +x /opt/membrane/hbbs /opt/membrane/hbbr
rm -rf /tmp/rustdesk-server.zip /tmp/rustdesk-extract

mkdir -p /opt/membrane/rustdesk
chmod 600 /opt/membrane/rustdesk/id_ed25519 2>/dev/null || true
echo "RustDesk identity will be restored from pepti depot (see NEXT STEPS)"

echo "=== 6. PULL BINARIES FROM SPOREGATE DEPOT ==="
echo "Binaries are deployed from pepti depot on sporeGate."
echo "After WireGuard is up, run:"
echo "  rsync -avz sporegate:/opt/ecoPrimals/depot/primals/x86_64-unknown-linux-musl/{membrane,songbird,beardog} /opt/membrane/"
echo "  rsync -avz sporegate:/opt/ecoPrimals/depot/ /opt/ecoPrimals/depot/"
echo "  cp /opt/membrane/membrane /usr/local/bin/membrane"

echo "=== 7. WIREGUARD ==="
cat > /etc/wireguard/wg0.conf << EOWG
[Interface]
Address = 10.13.37.1/24
ListenPort = 51820
PrivateKey = ${GOLGI_WG_PRIVKEY:-REPLACE_ME}

[Peer]
# sporeGate
PublicKey = ${SPOREGATE_WG_PUBKEY:-REPLACE_ME}
AllowedIPs = 10.13.37.2/32, 192.168.4.0/22
Endpoint = REPLACE_WITH_SPOREGATE_ENDPOINT
PersistentKeepalive = 25
EOWG

systemctl enable wg-quick@wg0

echo "=== 8. SYSTEMD SERVICES ==="

cat > /etc/systemd/system/forgejo.service << 'EOSVC'
[Unit]
Description=Forgejo — Sovereign Git Forge (golgiBody periplasmic surface)
After=network.target

[Service]
User=git
Group=git
Type=simple
WorkingDirectory=/opt/forgejo
ExecStart=/usr/local/bin/forgejo web --config /opt/forgejo/custom/conf/app.ini
Restart=always
RestartSec=5
Environment=USER=git HOME=/opt/forgejo FORGEJO_WORK_DIR=/opt/forgejo

[Install]
WantedBy=multi-user.target
EOSVC

cat > /etc/systemd/system/caddy-tls.service << 'EOSVC'
[Unit]
Description=Channel 3 TLS Surface (Caddy — all domains on :443, HTTP/2)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/opt/membrane/caddy run --config /etc/membrane/Caddyfile
Environment=HOME=/root
Restart=always
RestartSec=5
NoNewPrivileges=true
PrivateTmp=true
MemoryMax=128M
CPUQuota=25%

[Install]
WantedBy=multi-user.target
EOSVC

cat > /etc/systemd/system/beardog-membrane.service << 'EOSVC'
[Unit]
Description=BearDog Crypto (Membrane Tower — BTSP + Secrets)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/opt/membrane/beardog server --socket /run/membrane/beardog.sock
Environment=BEARDOG_SOCKET_MODE=0660
Environment=BEARDOG_LOG_LEVEL=info
Environment=BEARDOG_ROLE=membrane
Restart=always
RestartSec=5
NoNewPrivileges=true
PrivateTmp=true
MemoryMax=64M
CPUQuota=25%

[Install]
WantedBy=multi-user.target
EOSVC

# bearDog ACME gateway — standby, NOT enabled by default.
# Caddy handles TLS on :443. bearDog ACME is ready when bearDog gains
# Host-header routing (SNI dispatch), then it can replace Caddy for primals.eco.
cat > /etc/systemd/system/beardog-sporeprint.service << 'EOSVC'
[Unit]
Description=bearDog ACME gateway — standby (primals.eco sovereign TLS)
After=network-online.target

[Service]
Type=simple
ExecStart=/opt/membrane/beardog server --bind-mode tcp --port 9999 --socket /run/membrane/beardog-gw.sock
Environment=BEARDOG_GATEHOUSE_MODE=true
Environment=BEARDOG_ACME_DOMAINS=primals.eco,www.primals.eco
Environment=BEARDOG_ACME_EMAIL=ops@primals.eco
Environment=BEARDOG_GATEWAY_UPSTREAM=127.0.0.1:8091
Environment=BEARDOG_DATA_DIR=/var/lib/beardog
Environment=GATE_NAME=golgiBody
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOSVC

cat > /etc/systemd/system/songbird-membrane.service << 'EOSVC'
[Unit]
Description=Songbird Discovery + Federation (Membrane Tower — Mesh Hub)
After=network-online.target beardog-membrane.service
Wants=network-online.target
Requires=beardog-membrane.service

[Service]
Type=simple
ExecStartPre=-/bin/rm -f /run/membrane/songbird.sock
ExecStart=/opt/membrane/songbird server \
    --socket /run/membrane/songbird.sock \
    --security-socket /run/membrane/beardog.sock \
    --federation-port 7700 \
    --bind 0.0.0.0 \
    --dark-forest \
    --pid-dir /run/membrane
Environment=SONGBIRD_NODE_ID=golgiBody
Environment=SONGBIRD_DARK_FOREST=true
Environment=SONGBIRD_SECURITY_PROVIDER=beardog
Environment=BEARDOG_SOCKET=/run/membrane/beardog.sock
Environment=SONGBIRD_FEDERATION_PORT=7700
Environment=SONGBIRD_FEDERATION_ENABLED=true
Restart=always
RestartSec=5
MemoryMax=128M
CPUQuota=50%

[Install]
WantedBy=multi-user.target
EOSVC

cat > /etc/systemd/system/songbird-relay.service << 'EOSVC'
[Unit]
Description=Songbird TURN Relay (Membrane Channel 2)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStart=/opt/membrane/songbird relay --bind 0.0.0.0 --port 3478
Restart=always
RestartSec=5
AmbientCapabilities=CAP_NET_BIND_SERVICE
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
NoNewPrivileges=true
PrivateTmp=true
MemoryMax=128M
CPUQuota=50%

[Install]
WantedBy=multi-user.target
EOSVC

cat > /etc/systemd/system/cascade-sense.service << 'EOSVC'
[Unit]
Description=Quorum Phase 1 — Cascade Sense (temporal.cascade with freshness)
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/membrane temporal.cascade --source forgejo
ExecStartPost=/bin/chown -R git:git /opt/forgejo/data/repositories
Environment=GATE_NAME=golgiBody
Environment=FORGEJO_REPO_ROOT=/opt/forgejo/data/repositories
User=root
WorkingDirectory=/opt/ecoPrimals
TimeoutStartSec=300
StandardOutput=journal
StandardError=journal
EOSVC

# sporePrint auto-rebuild: after cascade pulls, rebuild Zola site
mkdir -p /etc/systemd/system/cascade-sense.service.d
cat > /etc/systemd/system/cascade-sense.service.d/zola-rebuild.conf << 'EODROP'
[Service]
ExecStartPost=/bin/sh -c "cd /opt/ecoPrimals/sporePrint && git fetch origin && git reset --hard origin/main && zola build --output-dir public --force >/dev/null 2>&1 || true"
EODROP

cat > /etc/systemd/system/cascade-sense.timer << 'EOSVC'
[Unit]
Description=Quorum Phase 1 — Cascade Sense Timer

[Timer]
OnBootSec=2min
OnUnitActiveSec=15min
RandomizedDelaySec=60

[Install]
WantedBy=timers.target
EOSVC

cat > /etc/systemd/system/skunky-ingest.service << 'EOSVC'
[Unit]
Description=skunky-ingest — Caddy JSON log tailer → skunkBat baseline.observe
After=caddy-tls.service
Wants=caddy-tls.service

[Service]
Type=simple
ExecStart=/opt/membrane/skunky-ingest --dry-run
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOSVC
mkdir -p /var/lib/skunky-ingest

cat > /etc/systemd/system/hbbs-membrane.service << 'EOSVC'
[Unit]
Description=RustDesk Rendezvous Server (cellMembrane — remote.primals.eco)
After=network-online.target
Wants=network-online.target
StartLimitIntervalSec=60
StartLimitBurst=5

[Service]
Type=simple
ExecStart=/bin/sh -c '/opt/membrane/hbbs -k _ -r $(hostname -I | awk "{print \\$1}")'
WorkingDirectory=/opt/membrane/rustdesk
Restart=always
RestartSec=5
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/membrane/rustdesk
MemoryMax=64M
CPUQuota=25%

[Install]
WantedBy=multi-user.target
EOSVC

cat > /etc/systemd/system/hbbr-membrane.service << 'EOSVC'
[Unit]
Description=RustDesk Relay Server (cellMembrane — remote.primals.eco)
After=network-online.target hbbs-membrane.service
Wants=network-online.target
StartLimitIntervalSec=60
StartLimitBurst=5

[Service]
Type=simple
ExecStart=/opt/membrane/hbbr
WorkingDirectory=/opt/membrane/rustdesk
Restart=always
RestartSec=5
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/membrane/rustdesk
MemoryMax=64M
CPUQuota=25%

[Install]
WantedBy=multi-user.target
EOSVC

systemctl daemon-reload

echo "=== 9. FIREWALL ==="
# UFW or iptables — allow essential ports only
if command -v ufw &>/dev/null; then
    ufw allow 22/tcp     # SSH
    ufw allow 2222/tcp   # Forgejo SSH
    ufw allow 80/tcp     # HTTP (Caddy ACME + HTTPS redirect)
    ufw allow 443/tcp    # HTTPS (Caddy — all domains, Host routing)
    ufw allow 51820/udp  # WireGuard
    ufw allow 7700/tcp   # SongBird federation
    ufw allow 3478/udp   # TURN relay
    ufw allow 21115/tcp  # RustDesk NAT test
    ufw allow 21116/tcp  # RustDesk ID registration
    ufw allow 21116/udp  # RustDesk NAT probe
    ufw allow 21117/tcp  # RustDesk relay
    ufw --force enable
fi

echo "=== 9b. FAIL2BAN — FORGEJO SSH HARDENING ==="

cat > /etc/fail2ban/jail.d/forgejo-ssh.conf << 'EOFAIL'
[forgejo-ssh]
enabled = true
port = 2222
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
findtime = 600
backend = systemd
EOFAIL

systemctl restart fail2ban

echo "=== 9c. HTTPS RATE LIMITING ==="

# Limit new HTTPS connections per IP (50 per 10 seconds)
iptables -I INPUT 1 -p tcp --dport 443 -m conntrack --ctstate NEW -m recent --name https_flood --set
iptables -I INPUT 2 -p tcp --dport 443 -m conntrack --ctstate NEW -m recent --name https_flood --update --seconds 10 --hitcount 50 -j DROP

echo "=== 9c2. RUSTDESK RATE LIMITING ==="

# Limit new RustDesk TCP connections per IP (20 per 10 seconds)
iptables -I INPUT 1 -p tcp -m multiport --dports 21115,21116,21117,21118,21119 -m conntrack --ctstate NEW -m recent --name rustdesk_flood --set
iptables -I INPUT 2 -p tcp -m multiport --dports 21115,21116,21117,21118,21119 -m conntrack --ctstate NEW -m recent --name rustdesk_flood --update --seconds 10 --hitcount 20 -j DROP
# Limit RustDesk UDP NAT probe (30 packets per 10 seconds per IP)
iptables -I INPUT 3 -p udp --dport 21116 -m recent --name rustdesk_udp --set
iptables -I INPUT 4 -p udp --dport 21116 -m recent --name rustdesk_udp --update --seconds 10 --hitcount 30 -j DROP

iptables-save > /etc/iptables.rules 2>/dev/null || true

echo "=== 9d. CADDY ACCESS LOGS ==="

mkdir -p /var/log/caddy

echo "=== 9e. WIREGUARD KEY AUDIT TOOL ==="

cat > /usr/local/bin/wg-key-audit << 'EOWGAUDIT'
#!/usr/bin/env bash
set -euo pipefail
WG_CONF="/etc/wireguard/wg0.conf"
ROTATION_DAYS=${1:-90}
NOW=$(date +%s)

echo "=== WireGuard Key Audit (rotation policy: ${ROTATION_DAYS}d) ==="
echo
conf_age=$(( (NOW - $(stat -c %Y "$WG_CONF")) / 86400 ))
echo "Config last modified: ${conf_age}d ago"
if [ "$conf_age" -gt "$ROTATION_DAYS" ]; then
    echo "WARNING: Config older than ${ROTATION_DAYS}d — key rotation recommended"
else
    echo "OK: Within rotation window"
fi
echo
echo "=== Active Peers ==="
wg show wg0 dump | tail -n +2 | while IFS=$'\t' read -r pubkey psk endpoint aips handshake rx tx keepalive; do
    hs_ago="never"
    if [ "$handshake" != "0" ]; then
        hs_ago="$(( (NOW - handshake) / 60 ))m ago"
    fi
    echo "  ${pubkey:0:20}...  endpoint=${endpoint}  handshake=${hs_ago}"
done
echo
echo "=== Rotation Protocol ==="
echo "1. Generate new keypair on EACH gate"
echo "2. Exchange public keys via secure channel (SSH/WireGuard)"
echo "3. Update configs on all peers simultaneously"
echo "4. Reload: wg syncconf wg0 <(wg-quick strip wg0)"
echo "5. Verify all handshakes within 2 minutes"
EOWGAUDIT
chmod +x /usr/local/bin/wg-key-audit

echo "=== 10. FORGEJO RE-SHALLOW MAINTENANCE ==="

cat > /usr/local/bin/forgejo-reshallow << 'EOSHALLOW'
#!/usr/bin/env bash
set -euo pipefail
REPO_BASE="/opt/forgejo/data/repositories"

# Repos that must keep full history (used as fetch origins by working copies)
SKIP_REPOS="sporeprint"

systemctl stop forgejo.service
SAVED=0
for repo_path in $(find "$REPO_BASE" -maxdepth 2 -name "*.git" -type d | sort); do
  repo_name=$(basename "$repo_path" .git)
  if echo "$SKIP_REPOS" | grep -qw "$repo_name"; then
    echo "  SKIP (full): $repo_path"
    continue
  fi
  before=$(du -sm "$repo_path" | awk '{print $1}')
  tmpdir=$(mktemp -d)
  if git clone --bare --depth=1 "file://${repo_path}" "${tmpdir}/shallow.git" 2>/dev/null; then
    [ -d "${repo_path}/hooks" ] && cp -a "${repo_path}/hooks" "${tmpdir}/shallow.git/hooks"
    rm -rf "$repo_path"
    mv "${tmpdir}/shallow.git" "$repo_path"
    chown -R git:git "$repo_path"
    after=$(du -sm "$repo_path" | awk '{print $1}')
    delta=$((before - after))
    SAVED=$((SAVED + delta))
  fi
  rm -rf "$tmpdir"
done
systemctl start forgejo.service
echo "forgejo-reshallow: saved ~${SAVED}M (skipped: $SKIP_REPOS)"
EOSHALLOW
chmod +x /usr/local/bin/forgejo-reshallow

cat > /etc/systemd/system/forgejo-reshallow.service << 'EOSVC'
[Unit]
Description=Re-shallow Forgejo bare repos (Thin Relay maintenance)
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/forgejo-reshallow
TimeoutStartSec=600
StandardOutput=journal
StandardError=journal
EOSVC

cat > /etc/systemd/system/forgejo-reshallow.timer << 'EOSVC'
[Unit]
Description=Monthly re-shallow of Forgejo bare repos

[Timer]
OnCalendar=monthly
RandomizedDelaySec=3600

[Install]
WantedBy=timers.target
EOSVC

echo "=== 10b. FORGEJO PERMISSION ENFORCEMENT (FORGEJO-PERMS-RECUR fix) ==="

# tmpfiles.d ensures ownership is correct on every boot.
cat > /etc/tmpfiles.d/forgejo-perms.conf << 'EOTMP'
# Enforce git:git ownership on Forgejo repository directories.
# Prevents permission drift from cascade-sense, reshallow, or any
# root-owned operation touching /opt/forgejo/data/repositories/.
Z /opt/forgejo/data/repositories - git git - -
EOTMP

# Apply immediately (don't wait for reboot)
systemd-tmpfiles --create /etc/tmpfiles.d/forgejo-perms.conf

# Periodic enforcement timer — runs every 6 hours as a safety net
cat > /etc/systemd/system/forgejo-perms.service << 'EOSVC'
[Unit]
Description=Enforce git:git ownership on Forgejo repositories

[Service]
Type=oneshot
ExecStart=/bin/chown -R git:git /opt/forgejo/data/repositories
EOSVC

cat > /etc/systemd/system/forgejo-perms.timer << 'EOSVC'
[Unit]
Description=Periodic Forgejo ownership enforcement (every 6h)

[Timer]
OnBootSec=5min
OnUnitActiveSec=6h

[Install]
WantedBy=timers.target
EOSVC

echo "=== 11. ENABLE SERVICES ==="
systemctl enable forgejo caddy-tls beardog-membrane songbird-membrane songbird-relay cascade-sense.timer hbbs-membrane hbbr-membrane fail2ban forgejo-reshallow.timer forgejo-perms.timer skunky-ingest
# beardog-sporeprint is NOT enabled — standby until bearDog gains Host routing

echo ""
echo "========================================="
echo " golgi VPS provisioned (Sovereign Relay)"
echo "========================================="
echo ""
echo "NEXT STEPS:"
echo "  1. Configure WireGuard keys in /etc/wireguard/wg0.conf"
echo "  2. Start WireGuard: systemctl start wg-quick@wg0"
echo "  3. rsync Forgejo repos from sporeGate mirror:"
echo "       rsync -avz sporegate:/opt/forgejo-mirror/ /opt/forgejo/data/repositories/"
echo "       chown -R git:git /opt/forgejo/data/repositories/"
echo "  4. rsync pepti depot from sporeGate:"
echo "       rsync -avz sporegate:/opt/ecoPrimals/depot/ /opt/ecoPrimals/depot/"
echo "  5. Copy relay binaries:"
echo "       rsync sporegate:/opt/ecoPrimals/depot/primals/x86_64-unknown-linux-musl/{membrane,songbird,beardog} /opt/membrane/"
echo "       cp /opt/membrane/membrane /usr/local/bin/membrane"
echo "  6. Restore RustDesk identity from depot:"
echo "       cp /opt/ecoPrimals/depot/rustdesk/id_ed25519* /opt/membrane/rustdesk/"
echo "  7. Add remote.primals.eco DNS record:"
echo "       knotc zone-begin primals.eco"
echo "       knotc zone-set primals.eco remote.primals.eco. 300 A <NEW_VPS_IP>"
echo "       knotc zone-commit primals.eco"
echo "  8. Start services: systemctl start forgejo caddy-tls beardog-membrane beardog-sporeprint songbird-membrane songbird-relay cascade-sense.timer hbbs-membrane hbbr-membrane"
echo "  9. Verify: curl https://primals.eco && curl https://membrane.primals.eco:8443/health"
echo ""
echo "Estimated disk usage after restore: ~3.5GB of 10GB (35%)"
echo "If golgi dies, re-run this script + rsync from sporeGate."
echo ""
echo "MAINTENANCE:"
echo "  - forgejo-reshallow.timer runs monthly to keep repos at depth=1 (except sporePrint)"
echo "  - Full history lives on sporeGate at /opt/forgejo-mirror/"
echo "  - sporePrint kept as full repo (docs, low churn, cascade fetch needs it)"
echo "  - Manual re-shallow: forgejo-reshallow"
