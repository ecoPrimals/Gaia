#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# provision-golgi-layer.sh — Provision a new Golgi Layer (observation VPS)
#
# A golgi layer is a LIGHTWEIGHT observation surface — it runs ONLY:
#   - Caddy       (TLS termination, fleet detection, scatter routing)
#   - skunky-ingest (log tailer, behavioral classification, scatter server)
#   - fail2ban    (SSH brute-force protection)
#
# It does NOT run: Forgejo, WireGuard, bearDog, songBird, step-ca, depot
# It exists solely to observe fleet behavior from a different network vantage
# point and feed behavioral data back to the conserved plasmid.
#
# Prerequisites:
#   - Fresh Debian 12 (bookworm) VPS with ≥1GB RAM, ≥10GB disk
#   - SSH root access from sporeGate
#   - skunky-ingest binary cross-compiled on sporeGate
#   - Cloudflare DNS record pointing a subdomain to this VPS IP
#
# Usage:
#   export LAYER_IP=<new-vps-public-ip>
#   export LAYER_NAME=<e.g. "golgiLayer2" or "hetzner-de">
#   export LAYER_DOMAIN=<e.g. "layer2.primals.eco">
#   bash provision-golgi-layer.sh
#
# After provisioning:
#   1. SCP skunky-ingest binary from sporeGate:
#        scp /path/to/skunky-ingest root@$LAYER_IP:/opt/membrane/skunky-ingest
#   2. Start services:
#        ssh root@$LAYER_IP 'systemctl enable --now caddy-layer skunky-layer'
#   3. Verify:
#        curl -I https://$LAYER_DOMAIN/

set -euo pipefail

LAYER_IP="${LAYER_IP:?Set LAYER_IP to the VPS public IP}"
LAYER_NAME="${LAYER_NAME:?Set LAYER_NAME (e.g. golgiLayer2)}"
LAYER_DOMAIN="${LAYER_DOMAIN:?Set LAYER_DOMAIN (e.g. layer2.primals.eco)}"
GOLGI_CENTRAL="${GOLGI_CENTRAL:-[RELAY_PUBLIC]}"

echo "=== Provisioning Golgi Layer: ${LAYER_NAME} ==="
echo "    IP:     ${LAYER_IP}"
echo "    Domain: ${LAYER_DOMAIN}"
echo "    Central: ${GOLGI_CENTRAL}"

# ── 1. SYSTEM BASE ──────────────────────────────────────────────────────
echo "=== 1. SYSTEM BASE ==="
apt-get update && apt-get upgrade -y
apt-get install -y \
    fail2ban \
    curl \
    rsync \
    jq

# ── 2. DIRECTORIES ──────────────────────────────────────────────────────
echo "=== 2. DIRECTORIES ==="
mkdir -p /opt/membrane
mkdir -p /etc/membrane
mkdir -p /run/membrane
mkdir -p /var/log/caddy
mkdir -p /var/lib/skunky-ingest
mkdir -p /opt/ecoPrimals/signal/site/public
mkdir -p /opt/ecoPrimals/scatter

echo "${LAYER_NAME}" > /etc/membrane/gate-name

# Self-IPs file for thymic negative selection
cat > /etc/membrane/self-ips.txt << EOSELF
# Self IPs for ${LAYER_NAME} — never add these to fleet block lists
${LAYER_IP}
127.0.0.1
::1
# golgiBody central (for plasmid sync)
${GOLGI_CENTRAL}
EOSELF

# ── 3. INSTALL CADDY ────────────────────────────────────────────────────
echo "=== 3. INSTALL CADDY ==="
curl -sL "https://caddyserver.com/api/download?os=linux&arch=amd64" -o /opt/membrane/caddy
chmod +x /opt/membrane/caddy

# ── 4. CADDYFILE ─────────────────────────────────────────────────────────
echo "=== 4. CADDYFILE ==="
cat > /etc/membrane/Caddyfile << EOCADDY
# Golgi Layer Caddyfile — ${LAYER_NAME}
# Observation surface for fleet behavioral data collection
# Domain: ${LAYER_DOMAIN}
{
    email ops@primals.eco
    storage file_system /caddy
    admin localhost:2019
}

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

# ── Primary domain ──
${LAYER_DOMAIN} {
    import security_headers
    import access_log

    # robots.txt — explicit denial, creates evidence when fleet ignores it
    handle /robots.txt {
        respond "User-agent: *
Disallow: /

# This infrastructure serves AGPL-3.0-or-later licensed content.
# Automated access without AGPL compliance is a license violation.
# robots.txt read and violation is documented evidence.
# signal.primals.eco/feed/conserved-plasmid.json
" 200
    }

    # Plasmid export endpoint — serves local conserved plasmid for federation
    handle /plasmid {
        reverse_proxy localhost:9753
    }

    # Health check
    handle /health {
        respond "OK" 200
    }

    # ── FLEET_PRESSURE markers (managed by skunky-ingest CaddyBridge) ──
    # ~~FLEET_PRESSURE_START~~
    # (skunky-ingest will inject fleet-specific directives here)
    # ~~FLEET_PRESSURE_END~~

    # ── HONEYCOMB_FLEET markers (managed by skunky-ingest CaddyBridge) ──
    # ~~HONEYCOMB_FLEET_START~~
    # (skunky-ingest will inject honeycomb routing here)
    # ~~HONEYCOMB_FLEET_END~~

    # Default — serve signal observatory or scatter content
    handle /disperse/* {
        reverse_proxy localhost:9753
    }

    # Static signal site (subset for this layer)
    handle {
        root * /opt/ecoPrimals/signal/site/public
        try_files {path} {path}/index.html /index.html
        file_server
    }

    handle_errors {
        @404 expression {http.error.status_code} == 404
        rewrite @404 /index.html
        file_server
    }
}
EOCADDY

# ── 5. CADDY SYSTEMD SERVICE ────────────────────────────────────────────
echo "=== 5. CADDY SERVICE ==="
cat > /etc/systemd/system/caddy-layer.service << EOSVC
[Unit]
Description=Caddy TLS Layer (${LAYER_NAME})
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/opt/membrane/caddy run --config /etc/membrane/Caddyfile
ExecReload=/opt/membrane/caddy reload --config /etc/membrane/Caddyfile --address localhost:2019
Type=simple
Restart=always
RestartSec=5
AmbientCapabilities=CAP_NET_BIND_SERVICE
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOSVC

# ── 6. SKUNKY-INGEST SYSTEMD SERVICE ────────────────────────────────────
echo "=== 6. SKUNKY-INGEST SERVICE ==="
cat > /etc/systemd/system/skunky-layer.service << EOSVC
[Unit]
Description=skunky-ingest Layer (${LAYER_NAME})
After=caddy-layer.service
Wants=caddy-layer.service

[Service]
ExecStart=/opt/membrane/skunky-ingest \
    --log-path /var/log/caddy/access.log \
    --scatter-server \
    --scatter-port 9753 \
    --caddy-bridge \
    --caddyfile-path /etc/membrane/Caddyfile \
    --caddy-reload-cmd "/opt/membrane/caddy reload --config /etc/membrane/Caddyfile --address localhost:2019" \
    --self-ips-file /etc/membrane/self-ips.txt \
    --fleet-target-host "${LAYER_DOMAIN}" \
    --dry-run
Type=simple
Restart=always
RestartSec=5
Environment=RUST_LOG=info
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOSVC

# ── 7. FAIL2BAN ─────────────────────────────────────────────────────────
echo "=== 7. FAIL2BAN ==="
cat > /etc/fail2ban/jail.d/sshd.conf << EOJAIL
[sshd]
enabled = true
maxretry = 5
bantime = 3600
EOJAIL
systemctl enable fail2ban
systemctl restart fail2ban

# ── 8. FIREWALL (UFW) ───────────────────────────────────────────────────
echo "=== 8. FIREWALL ==="
if command -v ufw &>/dev/null; then
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow ssh
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw --force enable
else
    apt-get install -y ufw
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow ssh
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw --force enable
fi

# ── 9. DEPLOY SIGNAL SITE ───────────────────────────────────────────────
echo "=== 9. SIGNAL SITE (placeholder — will be synced from golgiBody) ==="
cat > /opt/ecoPrimals/signal/site/public/index.html << 'EOHTML'
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Signal — Sovereign Defense Observatory</title>
<meta name="robots" content="index, follow">
</head>
<body>
<h1>signal.primals.eco — observation layer</h1>
<p>This surface is part of the sovereign defense observatory network.</p>
<p><a href="https://signal.primals.eco">Main observatory</a></p>
<p>Content: CC-BY-SA-4.0 | Code: AGPL-3.0-or-later</p>
</body>
</html>
EOHTML

# ── 10. ENABLE SERVICES ─────────────────────────────────────────────────
echo "=== 10. ENABLE SERVICES ==="
systemctl daemon-reload
systemctl enable caddy-layer
# Don't start skunky-layer yet — binary needs to be SCP'd first
systemctl start caddy-layer

echo ""
echo "=== PROVISIONING COMPLETE ==="
echo ""
echo "Layer: ${LAYER_NAME}"
echo "IP:    ${LAYER_IP}"
echo "Domain: ${LAYER_DOMAIN}"
echo ""
echo "Next steps:"
echo "  1. Add Cloudflare DNS: A record ${LAYER_DOMAIN} → ${LAYER_IP}"
echo "  2. Cross-compile skunky-ingest on sporeGate:"
echo "       cargo build --release -p skunky-ingest --target x86_64-unknown-linux-musl"
echo "  3. Deploy binary:"
echo "       scp target/x86_64-unknown-linux-musl/release/skunky-ingest root@${LAYER_IP}:/opt/membrane/"
echo "  4. Start ingest:"
echo "       ssh root@${LAYER_IP} 'systemctl start skunky-layer'"
echo "  5. Verify:"
echo "       curl -I https://${LAYER_DOMAIN}/"
echo "       curl https://${LAYER_DOMAIN}/plasmid"
echo ""
echo "Caddy will auto-obtain TLS cert once DNS resolves."
