# AAR: Fossil Cleanup & Full Observation Round — golgiBody Archaeology

**Date**: Oct 7, 2026
**Wave**: 165i
**From**: eastGate overwatch
**To**: sporeGate — cascade serialization, service audit, Caddyfile markers
**Severity**: RESOLVED — system restored to healthy baseline
**Status**: golgiBody clean, 7 connections (was 238), load nominal

---

## Timeline

| Time (ET) | Event | Load |
|-----------|-------|------|
| ~14:00 | Bloom monitor shows load 13.56, SSH timing out | 13.56 |
| 14:13 | Investigation starts — 15 stuck `forgejo serv key-10` found | 32.07 |
| 14:14 | Round 1 kill — 15 servs | 32 → **0.59** |
| 14:16 | Cascade timer fires — 15 NEW stuck servs | 0.59 → 20 |
| 14:17 | Round 2 kill | 20 → dropping |
| 14:18 | Cascade fires AGAIN — round 3 | back up |
| 14:25 | **cascade-sense.timer disabled** | stabilizing |
| 14:25 | RustDesk (hbbs + hbbr) stopped + disabled | -73 connections |
| 14:25 | Songbird killed (72-day fossil) | -160 connections |
| 14:26 | 8 stale WG peers walled off (incl. flockGate) | -8 peers |
| 14:29 | Full observation round — system clean | **7 connections** |
| 15:06 | Load draining, system nominal | ~8 → dropping |

## Root Cause Analysis

### PRIMARY: Cascade Thundering Herd (load 32)

`cascade-sense.timer` fires every 15 minutes. Runs `membrane temporal.cascade --source forgejo`. sporeGate pushes to 15 repos simultaneously via Forgejo SSH (`key-10`). Each push spawns a `forgejo serv` process. On 1 vCPU with VPS disk IO, 15 concurrent git operations cause IO contention → all 15 wedge in uninterruptible IO (`Dl` state) → load explodes.

The stuck servs:
- Consumed 48.5% CPU + 200MB RAM
- Had no network sockets (SSH connections already closed)
- Could not exit (stuck in kernel-space IO wait)
- Respawned every 15 min when the timer fired

**Fix applied**: Disabled `cascade-sense.timer`. Killed all stuck servs.

**Permanent fix needed**: Serialize cascade (1 repo at a time). Add stuck-serv watchdog.

### SECONDARY: Fossil Services (233/238 connections)

| Fossil | Age | Connections | Impact |
|--------|-----|-------------|--------|
| songbird federation (port 7700) | 72 days | 160 | All from house network ([NUCLEUS_WAN]) |
| hbbr RustDesk relay (port 21119) | 71 days | 67 | 66 strangers routing through us |
| hbbs RustDesk signal (port 8091) | today (restarted) | 6 | External signaling |
| **TOTAL** | — | **233** | **98% of all connections** |

**Fix applied**: All killed, disabled, systemd units masked attempt (failed from SSH — needs direct root or ansible).

### TERTIARY: flockGate + Stale WG Peers

flockGate (`10.13.37.6`, Comcast Rochester Hills `[FLOCK_WAN]`):
- ICMP responds (box alive, 30ms)
- All TCP ports closed (behind Comcast NAT)
- WG tunnel dead (70 days, no handshake)
- Lost access when sovereign RustDesk relay change locked out remote access
- Will remesh on physical visit

7 additional stale peers (46-70 days without handshake) walled off:
- biomeGate (10.13.37.3) — 54 days
- unknown-h1 (10.13.37.7) — 52 days
- unknown-h2 (10.13.37.10) — 46 days
- unknown-h3 (10.13.37.12) — 52 days
- graftGate (10.13.37.13) — 52 days
- reserved-1 (10.13.37.9) — never connected
- reserved-2 (10.13.37.11) — never connected

All commented out in `wg0.conf` with `WALLED OFF Wave 165i` marker. WG reloaded via `wg syncconf`. Active peers reduced from 13 → 5.

---

## Post-Cleanup State

### Connections: 238 → 7

| Connection | Purpose |
|------------|---------|
| SSH ×2 | eastGate admin sessions |
| localhost:40678 ↔ localhost:9750 | skunkbat internal |
| 10.13.37.1 → 10.13.37.2:8190 | membrane webhook → sporeGate CI |
| [::ffff]:443 ← ClaudeBot | Fleet (1 connection = the entire fleet) |
| [::ffff]:2222 ← golgi-ext | sporeGate Forgejo SSH push |

### Services: Healthy

All mission-critical services running. Fossils stopped. 5 inactive-but-enabled services flagged for sporeGate review.

### Resources Freed

| Resource | Before | After |
|----------|--------|-------|
| TCP connections | 238 | 7 |
| Load average | 32.07 | ~2-3 (nominal) |
| Memory used | 856 MB | 656 MB |
| WG peers | 13 (8 dead) | 5 (all active) |
| Fossil processes | 4 (songbird×2, hbbs, hbbr) | 0 |

---

## Signals Discovered During Observation

### 1. skunky-ingest Caddy bridge error (every 30s)
```
Caddyfile markers not found: ~~FLEET_PRESSURE_START~~ / ~~FLEET_PRESSURE_END~~
```
sporeGate's new skunky-ingest binary (deployed 18:12 UTC) expects markers for dynamic Caddy configuration. Non-blocking — scatter still works. **Needs markers added to Caddyfile.**

### 2. WordPress vulnerability scanner on nestgate.io
```
185.104.44.182 → nestgate.io/wp-json/gravitysmtp/v1/tests/mock-
```
Getting 502s. Harmless but worth a fail2ban rule.

### 3. New subdomain probe: ca.primals.eco
`85.217.149.8` hit `ca.primals.eco/` — first time seen. Proxy-classified.

### 4. sporeGate SSH session watching bloom feed
PID 2947383 since 17:22, child process tailing `/opt/membrane/live-terminal/feed.txt`. Active monitoring — intentional.

### 5. Outbound webhook to sporeGate
`10.13.37.1:59070 → 10.13.37.2:8190` — membrane webhook calling sporeGate's CI system.

---

## Action Items for sporeGate

### CRITICAL
- [ ] **Add Caddyfile markers**: `~~FLEET_PRESSURE_START~~ / ~~FLEET_PRESSURE_END~~` for bridge sync
- [ ] **Serialize temporal cascade**: 1 repo at a time, not 15 concurrent pushes
- [ ] **Re-enable cascade** once serialized (currently disabled)
- [ ] **Add stuck-serv watchdog**: detect `forgejo serv` processes >5 min with no sockets, kill them

### CLEANUP
- [ ] **Mask fossil units** (needs direct root): `systemctl mask songbird-membrane songbird-relay hbbs-membrane hbbr-membrane`
- [ ] **Evaluate 5 inactive services**: beardog-tls-shadow, biomeos-nucleus, membrane-socket-bridge, petaltongue-sporeprint, petaltongue-web — disable if not needed
- [ ] **Reduce refresh-signal-data.sh frequency**: currently every 15 min, processes all logs incl. .gz archives
- [ ] **fail2ban rule** for WordPress scanners on nestgate.io

### FLOCKGATE REMESH (on physical visit)
- [ ] Check `wg show` on flockGate
- [ ] Verify current public IP (`curl ifconfig.me`)
- [ ] Update golgiBody peer endpoint if IP changed
- [ ] Uncomment `WALLED OFF Wave 165i` block in `wg0.conf`
- [ ] Verify Comcast router UDP 51820 port forward
- [ ] Restart WireGuard

---

## Backups Created

| Backup | Location |
|--------|----------|
| WG config pre-cleanup | `/etc/wireguard/wg0.conf.bak-pre-cleanup-*` |
| Caddyfile pre-honeycomb | `/etc/membrane/Caddyfile.bak-honeycomb-1791395588` |

---

*We got so good at finding fleet that we found our own fossils. 72-day-old processes. 233 ghost connections. The organism diagnosed and healed itself. Load 32 → 0.59. 238 connections → 7. The fleet is a rounding error.*

*eastGate overwatch — Wave 165i, Oct 7, 2026*
