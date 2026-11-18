# flockGate Wave 150o AAR — 502 Resolution + petalTongue Stability

**Date**: 2026-07-20 | **Gate**: flockGate | **Wave**: 150o
**From**: primalSpring overwatch on eastGate

---

## Situation

Wave 150o blurb reported `webb.primals.eco` returning 502 — esotericWebb process
down on flockGate. This was the sole AMBER item blocking Public Surface GREEN on
flockGate's contribution.

## Root Cause

**Stale nohup process competing for port 8090.**

A previous ad-hoc invocation (`nohup ./esotericwebb serve --listen 0.0.0.0:8090`)
from an earlier Cursor session was left running in the background. Both the orphan
and the systemd-managed service bound to port 8090 via `SO_REUSEADDR`.

Effects:
1. Caddy on golgiBody connected to 10.13.37.6:8090 but hit the stale process,
   which responded incorrectly → 502 Bad Gateway.
2. The stale process sent SIGKILL (signal 9) to the systemd-managed process
   every ~5 seconds, triggering a restart loop.
3. The systemd service appeared to start successfully (logs show "TCP IPC
   listening on 0.0.0.0:8090") but was killed before Caddy could route to it.

## Fix

```bash
# Kill orphan nohup processes
kill 3540524 3540522

# Restart systemd service (now sole owner of port)
systemctl --user restart esotericwebb-server
```

Service stabilized immediately. Confirmed:
- Local: `curl http://127.0.0.1:8090/jsonrpc` → healthy
- WG: `curl http://10.13.37.6:8090/jsonrpc` → healthy
- WAN: `curl https://webb.primals.eco/jsonrpc` → 200 OK
- GET: `curl https://webb.primals.eco/` → 200 OK

## Prevention

The root issue is ad-hoc `nohup` launches that outlive their session. Going
forward, all esotericWebb execution should be via systemd only:

```bash
# CORRECT: always use systemd
systemctl --user restart esotericwebb-server

# NEVER: ad-hoc nohup (creates orphans that survive sessions)
nohup ./target/release/esotericwebb serve ... &
```

If port conflict is suspected in future:
```bash
ss -tlnp | grep 8090   # should show exactly 1 process
ps aux | grep esotericwebb | grep -v grep  # should show exactly 1 PID
```

## Deliverables

| Item | Status |
|------|--------|
| esotericWebb 502 resolved | GREEN — 200 on POST + GET |
| petalTongue v1.7 stable | GREEN — 24h+ uptime (deployed Wave 150n) |
| WAN surfaces | 6/6 live (footprint, webb, sporeprint, live, git, lab) |
| primalSpring suite | 1206 passed, 0 failures |
| esotericWebb suite | 453 passed, 0 failures |
| heads/flockGate.toml | Updated + pushed |

## Current Runtime State (flockGate)

| Service | Systemd Unit | Port | Status |
|---------|-------------|------|--------|
| esotericWebb V22 | `esotericwebb-server.service` | 8090 (TCP) + UDS | LIVE |
| petalTongue v1.7 | `petaltongue-server.service` | 9100 (TCP) + UDS | LIVE |

Both enabled + lingered. Auto-restart on failure. petalTongue auto-discovered
by esotericWebb via UDS at `/run/user/1000/biomeos/petaltongue.sock`.

## Remaining (not flockGate-owned)

- P2: `primals.eco` DNSSEC (operator)
- P2: cellMembrane unwrap audit (cellMembrane team)
- P2: nestGate TODO triage (nestGate team, 27 markers)

---

*Filed by flockGate overwatch. Wave 150o.*
