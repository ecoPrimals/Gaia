# FRAGO: Gatehouse Cutover — Caddy Retirement

**Date**: Jul 5, 2026 09:42 EDT
**Wave**: 132g
**Gate**: sporeGate (cellMembrane team)
**From**: eastGate overwatch
**Priority**: P1 — enables full sovereign HTTP
**Type**: Deployment cutover — code already on Forgejo

---

## Situation

bearDog 16430d90c landed on Forgejo (Sovereign CI triggered). This commit adds:
- `BEARDOG_GATEHOUSE_MODE=true` — unified gatehouse activation
- HTTP→HTTPS 301 redirect on :80 for non-ACME traffic
- Dual-purpose :80 handler (ACME challenges when needed, redirect always)

Combined with the existing :443 TLS gateway (`serve_https_gateway`) and songBird's `http.proxy` routing, **Caddy is now fully replaceable**.

---

## Cutover Procedure

### Pre-checks

```bash
# Verify new bearDog built by Sovereign CI
ls -la /opt/ecoPrimals/depot/beardog-*  # or wherever CI puts artifacts
# Verify songBird http.proxy is LIVE
curl -s --unix-socket /run/membrane/songbird.sock \
  -d '{"jsonrpc":"2.0","id":1,"method":"http.proxy","params":{"capability":"jupyter"}}' \
  http://localhost/ | jq .
```

### Step 1: Deploy new bearDog binary

```bash
sudo systemctl stop beardog 2>/dev/null || true
sudo cp /opt/ecoPrimals/depot/beardog /usr/local/bin/beardog
sudo chmod +x /usr/local/bin/beardog
```

### Step 2: Configure gatehouse environment

Create/update `/etc/beardog/gatehouse.env`:

```bash
BEARDOG_GATEHOUSE_MODE=true
BEARDOG_ACME_DOMAINS=lab.primals.eco
BEARDOG_ACME_EMAIL=admin@primals.eco
BEARDOG_ACME_DIRECTORY=https://acme-v2.api.letsencrypt.org/directory
BEARDOG_GATEWAY_UPSTREAM=127.0.0.1:7700
BEARDOG_HTTPS_PORT=443
BEARDOG_ACME_CHALLENGE_PORT=80
```

### Step 3: Stop Caddy

```bash
sudo systemctl stop caddy
sudo systemctl disable caddy
```

### Step 4: Start bearDog in gatehouse mode

```bash
# Option A: systemd unit
sudo systemctl start beardog

# Option B: direct (for testing)
sudo BEARDOG_GATEHOUSE_MODE=true \
     BEARDOG_ACME_DOMAINS=lab.primals.eco \
     BEARDOG_ACME_EMAIL=admin@primals.eco \
     BEARDOG_GATEWAY_UPSTREAM=127.0.0.1:7700 \
     /usr/local/bin/beardog server
```

### Step 5: Validate

```bash
# ACME cert issuance (check logs)
journalctl -u beardog --since "1 min ago" | grep -i "certificate\|ACME\|gatehouse"

# HTTP→HTTPS redirect
curl -I http://lab.primals.eco
# Expected: HTTP/1.1 301 Moved Permanently
#           Location: https://lab.primals.eco/

# HTTPS works
curl -I https://lab.primals.eco
# Expected: HTTP/1.1 200 OK (from songBird → backend)

# E2E through darkforest
curl https://lab.primals.eco/hub/api
# Expected: JupyterHub API response (once ironGate deploys)
```

### Rollback (if needed)

```bash
sudo systemctl stop beardog
sudo systemctl start caddy
sudo systemctl enable caddy
```

---

## Architecture After Cutover

```
Internet → Cloudflare → Flint H1 (DNAT :80/:443)
    → bearDog :443 (TLS termination, ACME certs)     ← GATEHOUSE
    → bearDog :80 (ACME challenges + HTTP→HTTPS)     ← GATEHOUSE
        ↓ cleartext HTTP
    → songBird :7700 (http.proxy routing)            ← DRAWBRIDGE
        ↓ capability.call
    → mesh (UDS, abstract, LAN direct-connect)       ← DARKFOREST
        → ironGate JupyterHub
        → strandGate compute
        → (any capability provider)
```

Caddy is permanently retired. bearDog IS the castle wall.

---

## Acceptance

1. `curl -I http://lab.primals.eco` → 301 redirect to HTTPS
2. `curl -I https://lab.primals.eco` → 200 OK (via songBird)
3. Caddy is stopped and disabled
4. ACME cert valid for `lab.primals.eco`
5. No port 80 conflict (bearDog owns both ports exclusively)

---

*Tower atomic is the gatehouse. The darkforest is invisible.*
