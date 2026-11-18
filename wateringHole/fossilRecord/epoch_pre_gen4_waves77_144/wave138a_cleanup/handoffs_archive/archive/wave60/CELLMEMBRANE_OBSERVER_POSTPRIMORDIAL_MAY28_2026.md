# cellMembrane Handoff — Observer Surface Down + postPrimordial Evolution

**Date:** 2026-05-28
**From:** projectNUCLEUS (irongate)
**To:** cellMembrane via primalSpring
**Priority:** P0 (lab.primals.eco down)

---

## Immediate Issue: lab.primals.eco Unreachable

After irongate reboot, `lab.primals.eco` returns 502 for all non-hub paths.

### Root Cause

Two systemd service units reference a stale repo path. The repo was relocated
from `ecoPrimals/sporeGarden/projectNUCLEUS` to `ecoPrimals/gardens/projectNUCLEUS`
but the units were never updated.

| Service | Unit File | Status | Restart Count |
|---------|-----------|--------|---------------|
| `observer-static.service` | `/etc/systemd/system/observer-static.service` | crash-loop (exit 2) | 2,194+ |
| `pappusCast.service` | `/etc/systemd/system/pappusCast.service` | crash-loop (CHDIR fail) | continuous |

### Broken Path

```
ExecStart=…/ecoPrimals/sporeGarden/projectNUCLEUS/deploy/observer_server.py  # WRONG
WorkingDirectory=…/ecoPrimals/sporeGarden/projectNUCLEUS/deploy              # WRONG
```

### Correct Path

```
/home/irongate/Development/ecoPrimals/gardens/projectNUCLEUS/deploy/observer_server.py
/home/irongate/Development/ecoPrimals/gardens/projectNUCLEUS/deploy/
```

### Impact

- `lab.primals.eco/` (root, static observer) → 502
- `lab.primals.eco/hub/*`, `/user/*`, `/api/*` → JupyterHub works fine (port 8000 is up)
- `git.primals.eco` → unaffected (Forgejo on port 3000 is up)
- cloudflared tunnel itself survived reboot — both user unit and system replica are running

### Immediate Fix (cellMembrane operational action)

```bash
# 1. Update observer-static.service
sudo sed -i 's|sporeGarden|gardens|g' /etc/systemd/system/observer-static.service

# 2. Update pappusCast.service
sudo sed -i 's|sporeGarden|gardens|g' /etc/systemd/system/pappusCast.service

# 3. Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart observer-static.service
sudo systemctl restart pappusCast.service

# 4. Verify
curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8866/
```

---

## postPrimordial Evolution: VPS-Hosted Static Observer

### Current Architecture (primordial)

```
visitor → Cloudflare CDN → cloudflared tunnel → irongate:8866 (observer-static)
```

The static observer surface is pre-rendered HTML served from irongate's LAN via
a Cloudflare tunnel. This creates a single-point-of-failure: if irongate reboots
or the observer process crashes, the public-facing page goes down.

### Proposed Architecture (postPrimordial)

```
visitor → Cloudflare CDN → VPS:443 (nginx/caddy static) → pre-rendered HTML
```

Move the static observer HTML to the VPS where cellMembrane already runs. Benefits:

| Aspect | Primordial (now) | postPrimordial (proposed) |
|--------|-----------------|--------------------------|
| Availability | Depends on irongate uptime + tunnel | VPS 99.9% SLA |
| Latency | CDN → tunnel → LAN → python HTTP | CDN → VPS nginx (direct) |
| Complexity | tunnel + python server + systemd | static files + web server |
| Sovereignty | Traffic traverses Cloudflare tunnel | Traffic to sovereign VPS |
| Reboot survival | Fragile (this incident) | Stateless static files |

### Implementation Path

1. **pappusCast evolution**: Instead of propagating HTML to local irongate, push
   pre-rendered notebooks to VPS via rsync/scp (already has SSH access)
2. **VPS web server**: cellMembrane's deploy already has nginx or caddy capability —
   add a static site block for the observer HTML
3. **DNS/tunnel update**: Point `lab.primals.eco` catch-all to VPS static rather than
   irongate:8866. Hub/user/api paths remain tunneled to irongate JupyterHub
4. **Retire observer-static.service**: Once VPS serves static content, this irongate
   service is no longer needed

### Aligns With

- **S2 DNS sovereignty** — reduces tunnel dependency
- **NC-1 CODE COMPLETE** → operational deploy path
- **biomeOS v3.84 VPS deploy** — same operational window
- **cellMembrane composition evolution** — NUCLEUS tier already typed

---

## For primalSpring

- Route this handoff to cellMembrane for immediate fix + postPrimordial planning
- The immediate fix is a 4-command operational action (path update)
- The postPrimordial evolution aligns with the P0 VPS deploy window
- projectNUCLEUS code is unaffected — this is infrastructure/operational scope

---

*Wave 59b. Observer down. Path stale. Evolution: VPS-hosted static. Sovereignty gains.*
