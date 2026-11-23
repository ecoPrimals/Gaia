# AAR: Fossil Layer Load Crisis — golgiBody Load 32 → 0.59

**Date**: Oct 7, 2026
**Wave**: 165i
**From**: eastGate overwatch
**To**: sporeGate — cascade serialization, fossil cleanup
**Severity**: RESOLVED — load 32 → 0.59
**Root cause**: 15 stuck Forgejo servs from parallel cascade + 233 fossil connections

---

## Incident

golgiBody load average spiked to **32.07** on 1 vCPU. SSH connections timing out (30s+ for banner exchange). HTTPS handshakes stalling. Initial hypothesis: fleet DDoS.

## Actual Cause

**Not fleet.** Three self-inflicted sources:

### 1. Stuck Forgejo SSH Workers (PRIMARY — caused load 32)

15 `forgejo serv key-10` processes spawned simultaneously at 18:15:42 UTC:
- All authenticated via `key-10` = `sporegate-gate-v1`
- All children of Forgejo web process (PID 2947882)
- 9 in `Dl` (uninterruptible IO), 6 in `Sl` (sleeping)
- No network sockets — SSH connections already closed
- Total CPU: 48.5%, Total RAM: 200MB
- Running 10+ minutes with no progress

**Cause**: temporal cascade pushed 15 repos simultaneously via SSH. IO contention on 1 vCPU caused all 15 to wedge in kernel-space IO wait.

**Fix**: `kill` on all 15 PIDs → load dropped 32 → 0.59 in 30 seconds.

### 2. Fossil Connections (233/238 = 98% of all TCP)

| Port | Service | Connections | Age | Source |
|------|---------|------------|-----|--------|
| 7700 | songbird federation | 160 | 72 days | [NUCLEUS_WAN] (house) |
| 21119 | hbbr RustDesk relay | 67 | 71 days | 66 random external IPs |
| 8091 | hbbs RustDesk signal | 6 | today (restarted) | external |

These services have been running since the cellMembrane era (late July). The RustDesk relay is an open relay with 66 strangers routing traffic through golgiBody.

### 3. Orphaned Investigation Process

PID 2950797 — our own bash session from earlier API queries, still running after SSH timeout. Killed during cleanup.

## Fleet Contribution

**2 out of 238 connections.** ClaudeBot at 600 req/min and Meta fleet at 150 req/min use short-lived HTTP connections. Their load is CPU-per-request, not connection count. They were the loudest signal but the smallest load source.

## Stratigraphy Discovered

Complete process archaeology from boot to present:

```
Layer 0  May 15  145d  systemd (Genesis)
Layer 1  May 31  129d  knotd (DNS sovereignty)
Layer 2  Jun 17  112d  WireGuard mesh
Layer 3  Jul  8   91d  nestgate (gateway)
Layer 4  Jul 11   88d  fail2ban (first immune)
Layer 5  Jul 27   72d  songbird federation  <<< FOSSIL
Layer 6  Jul 28   71d  hbbr RustDesk relay  <<< FOSSIL
Layer 7  Jul 29   70d  step-ca (internal PKI)
Layer 8  Oct  7    0d  caddy + skunky-ingest + bloom (current)
```

## Action Items for sporeGate

### CRITICAL
- [ ] **Serialize temporal cascade** — one git push at a time on single-vCPU. No more 15-at-once thundering herd.
- [ ] **Add cascade watchdog** — detect stuck `forgejo serv` processes (>5 min, no sockets) and kill them.

### EVALUATE
- [ ] **songbird federation** — 160 persistent connections from house network. Still needed? If not, stop the service and reclaim the connection slots.
- [ ] **RustDesk relay** — 66 strangers using golgiBody as a free relay. Intentional? If not, stop `hbbr` and `hbbs`.
- [ ] **ssh-hygiene.sh** — expand to detect orphaned Forgejo serv workers, not just stale SSH connections.

### CLEANUP
- [ ] Audit all services against current mission requirements
- [ ] Consider process budget: on 1 vCPU, every persistent connection and background service costs

---

*We got so good at finding fleet that we found our own fossils. Load 32 → 0.59 by killing 15 of our own orphaned processes. The organism is learning to diagnose itself.*

*eastGate overwatch — Wave 165i, Oct 7, 2026*
