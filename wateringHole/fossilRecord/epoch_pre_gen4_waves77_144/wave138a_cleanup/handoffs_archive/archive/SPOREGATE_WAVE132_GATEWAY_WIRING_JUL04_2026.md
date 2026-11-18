# sporeGate Handoff — Wave 132: Gateway Wiring + Caddy Retirement

**Date**: Jul 4, 2026  
**Gate**: sporeGate  
**Team**: cellMembrane code team  
**From**: eastGate overwatch  
**Type**: Integration + deployment — Tower atomic gateway replaces Caddy

---

## Objective

Once flockGate delivers evolved songBird (with `http.gateway`) and bearDog (with ACME front), deploy them on sporeGate to replace the current Caddy reverse proxy for `lab.primals.eco`. This handoff covers deployment, systemd integration, shadow validation, and eventual Caddy removal.

---

## Prerequisites (from flockGate)

Before starting this work, confirm these binaries are available in the plasmidBin depot:

| Binary | Minimum Feature | Source |
|--------|-----------------|--------|
| `songbird` | `http.proxy` JSON-RPC method + `ReverseProxyConfig` route matching | flockGate WAVE132 build |
| `beardog` | ACME gateway listener on :443, `HotReloadAcceptor`, HTTP-01 solver | flockGate WAVE132 build |

Check depot: `ls /opt/plasmidBin/depot/songbird-*` and `ls /opt/plasmidBin/depot/beardog-*`

---

## Current State on sporeGate

| Component | State |
|-----------|-------|
| Caddy | Active, handles `lab.primals.eco` → reverse_proxy to ironGate:8000 |
| songBird | Running v0.2.1, mesh hub, 3-gate peered |
| bearDog | Not running (no TLS role yet) |
| Systemd | `membrane-nucleus@songbird.service` exists |

Current Caddyfile routes for `lab.primals.eco`:
```
lab.primals.eco {
    /hub/*  → reverse_proxy 192.168.4.237:8000
    /user/* → reverse_proxy 192.168.4.237:8000
    /api/*  → reverse_proxy 192.168.4.237:8000
    /services/* → reverse_proxy 192.168.4.237:8000
}
```

---

## Deployment Steps

### Step 1: Deploy new songBird with `http.gateway`

```bash
# Pull from depot
sudo cp /opt/plasmidBin/depot/songbird-latest /usr/local/bin/songbird
sudo chmod +x /usr/local/bin/songbird

# Add gateway config
cat >> /etc/songbird/songbird.toml << 'EOF'
[network.reverse_proxy]
enabled = true
upstream_timeout_secs = 30
max_upstream_connections = 100

[[network.reverse_proxy.routes]]
host = "lab.primals.eco"
path_prefix = "/hub"
capability = "jupyter"

[[network.reverse_proxy.routes]]
host = "lab.primals.eco"
path_prefix = "/user"
capability = "jupyter"

[[network.reverse_proxy.routes]]
host = "lab.primals.eco"
path_prefix = "/api"
capability = "jupyter"

[[network.reverse_proxy.routes]]
host = "lab.primals.eco"
path_prefix = "/services"
capability = "jupyter"
EOF

# Restart songBird
sudo systemctl restart membrane-nucleus@songbird
```

### Step 2: Deploy bearDog with ACME gateway

```bash
# Pull from depot
sudo cp /opt/plasmidBin/depot/beardog-latest /usr/local/bin/beardog
sudo chmod +x /usr/local/bin/beardog

# Configure ACME gateway
cat > /etc/beardog/gateway.env << 'EOF'
BEARDOG_TLS_MODE=acme
BEARDOG_GATEWAY_BIND=0.0.0.0:443
BEARDOG_GATEWAY_DOMAINS=lab.primals.eco
BEARDOG_ACME_DIRECTORY=https://acme-v02.api.letsencrypt.org/directory
BEARDOG_ACME_CONTACTS=mailto:ops@primals.eco
BEARDOG_ACME_CHALLENGE_PORT=80
BEARDOG_SONGBIRD_SOCKET=/run/songbird/songbird.sock
BEARDOG_DATA_DIR=/var/lib/beardog
EOF
```

### Step 3: Systemd integration

Create `/etc/systemd/system/membrane-nucleus@beardog-tls.service`:

```ini
[Unit]
Description=bearDog TLS Gateway (Tower atomic)
After=network-online.target membrane-nucleus@songbird.service
Requires=membrane-nucleus@songbird.service
Wants=network-online.target

[Service]
Type=simple
EnvironmentFile=/etc/beardog/gateway.env
ExecStart=/usr/local/bin/beardog gateway
Restart=always
RestartSec=5
AmbientCapabilities=CAP_NET_BIND_SERVICE
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable membrane-nucleus@beardog-tls
sudo systemctl start membrane-nucleus@beardog-tls
```

### Step 4: Shadow period (Caddy + Tower in parallel)

During shadow validation (7 days minimum):

1. bearDog binds :8443 (not :443) — Caddy keeps :443
2. Port-forward :8443 from Flint for test access
3. Validate: `curl -k https://sporegate.primals.local:8443/hub/login` returns JupyterHub page
4. Compare latency and error rates between Caddy path and Tower path
5. Monitor `/var/log/beardog/gateway.log` and songBird telemetry

### Step 5: Caddy retirement (after shadow validates)

```bash
# Switch bearDog to :443
sudo sed -i 's/BEARDOG_GATEWAY_BIND=0.0.0.0:8443/BEARDOG_GATEWAY_BIND=0.0.0.0:443/' /etc/beardog/gateway.env
sudo systemctl stop caddy
sudo systemctl restart membrane-nucleus@beardog-tls

# Validate
curl https://lab.primals.eco/hub/login  # should work

# Disable Caddy
sudo systemctl disable caddy
```

---

## Firewall Updates

bearDog needs port 80 for ACME HTTP-01 challenges:

```bash
sudo ufw allow 80/tcp comment "ACME HTTP-01 challenges"
```

Port 443 is already open (Caddy uses it today).

---

## DNS (no changes needed)

`lab.primals.eco` already points to sporeGate via Cloudflare → Flint DNAT → sporeGate:443. No DNS changes required.

---

## Rollback Plan

If Tower gateway fails during shadow or after cutover:

```bash
sudo systemctl stop membrane-nucleus@beardog-tls
sudo systemctl start caddy
```

Caddy config remains intact throughout.

---

## Monitoring

| Check | Method |
|-------|--------|
| bearDog TLS health | `curl -k https://localhost:443/health` (if wired) or port probe |
| songBird gateway metrics | `echo '{"method":"http.gateway.stats","params":{},"id":1}' | socat - UNIX:/run/songbird/songbird.sock` |
| ACME cert expiry | `openssl s_client -connect localhost:443 | openssl x509 -enddate` |
| E2E validation | `curl https://lab.primals.eco/hub/login` from external host |

---

## Acceptance Criteria

1. bearDog terminates TLS for `lab.primals.eco` with valid ACME cert
2. Requests flow: bearDog :443 → songBird `http.proxy` → mesh → ironGate → JupyterHub
3. Shadow period shows zero regressions vs Caddy path
4. Caddy disabled, Tower atomic owns :443 exclusively
5. Systemd units restart automatically on failure

---

## Dependency Chain

```
flockGate delivers binaries
    → sporeGate deploys (this handoff)
        → ironGate registers jupyter capability (see IRONGATE handoff)
            → E2E validated
```

---

*The membrane becomes sovereign. No external dependencies for HTTP routing.*
