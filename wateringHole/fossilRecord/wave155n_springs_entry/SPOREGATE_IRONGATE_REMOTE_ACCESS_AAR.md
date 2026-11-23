# sporeGate AAR — ironGate Remote Access + golgi Auto-Publish Fix

**Date**: 2026-08-01
**Gate**: sporeGate (build authority)
**Scope**: ironGate remote access (RustDesk), golgi/golgi-ext DNS mismatch, tower atomic mesh validation
**Status**: RESOLVED (operational), DIVERGENCE DOCUMENTED (architectural)

---

## Summary

Two issues resolved in a single ops session:

1. **golgi/golgi-ext auto-publish mismatch** — sporePrint deploying to inner membrane only
2. **ironGate RustDesk inaccessible** — relay auth failures + service instability

Both trace to the same architectural gap: the outer membrane layer lacks a coherent remote access pattern. Current remote access is ad-hoc (per-gate RustDesk configs, manual firewall rules, relay key management). The inner membrane (WireGuard mesh + SSH) proved to be the reliable fallback — the tower atomic mesh was the path that ultimately resolved ironGate access.

---

## Issue 1: golgi/golgi-ext Auto-Publish Mismatch

### Architecture

| Server | IP | Role | sporePrint Source |
|--------|-----|------|-------------------|
| golgiBody | [RELAY_PUBLIC] | Inner membrane — Forgejo, depot, WG hub | Post-receive hook (instant) |
| golgiBody-ext | 137.184.197.151 | Outer membrane — public Caddy, Cloudflare | 15-min timer pull from Forgejo |

- `sporeprint.primals.eco` → golgiBody (direct HTTPS)
- `primals.eco` → golgiBody-ext (via Cloudflare HTTP)

### Root Cause — THREE compounding bugs

1. **Worktree ownership mismatch**: Post-receive hook runs as `git:git` (Forgejo user), but `/opt/ecoPrimals/sporePrint/` was owned by `root:root`. `git reset --hard` and `zola build` failed silently — `2>&1` swallowed permission errors, page count reported stale files as "success."

2. **Missing `--force` flag**: `zola build --output-dir public` refuses to overwrite existing `public/` without `--force`. Even with correct ownership, build still fails.

3. **SSH config mismatch**: `Host golgi-ext` in `~/.ssh/config` pointed to `[RELAY_PUBLIC]` (golgiBody) instead of `137.184.197.151` (golgiBody-ext).

### Fixes Applied

- `chown -R git:git /opt/ecoPrimals/sporePrint/` on golgiBody
- Updated `50-zola-publish` hook: added `--force`, added explicit error logging with `continue` on failure, added commit hash to success log
- Fixed `~/.ssh/config`: `Host golgi-ext` → HostName `137.184.197.151`
- Verified: both servers at `b8a4965`, HTTP 200, 379 pages served

### Remaining Arch Note

golgi-ext timer pulls every 15 minutes — natural delay vs golgi's instant hook. For zero-lag, the hook could rsync `public/` to golgi-ext, but 15-min timer is acceptable for now.

---

## Issue 2: ironGate RustDesk Inaccessible

### Topology Context

- ironGate: `192.168.4.237` (LAN), `10.13.37.7` (WG mesh), House 2
- sporeGate: `192.168.4.3` (LAN), `10.13.37.2` (WG mesh), House 1
- Both houses share external IP `[NUCLEUS_WAN]` (same ISP)
- RustDesk relay: golgiBody `[RELAY_PUBLIC]` (hbbs 1.1.16 + hbbr 1.1.16)
- RustDesk client: ironGate v1.4.6

### Diagnostic Path

1. **LAN ping**: OK (0.2ms, ARP + DHCP lease active)
2. **SSH port 22**: OPEN but key not enrolled — `Permission denied (publickey)`
3. **RustDesk ports 21115-21119**: FILTERED by UFW (policy DROP, no RustDesk rules)
4. **Tower atomic mesh**: `ssh irongate@10.13.37.7` — **SUCCESS** (WG mesh, key accepted)
5. **From inside ironGate via WG SSH**:
   - RustDesk service running, `DISPLAY=:0` set, GNOME session active
   - TCP connections to golgi:21116 immediately closing (TIME-WAIT)
   - golgi hbbr logs: `Relay authentication failed - invalid key` from `[NUCLEUS_WAN]`
   - golgi hbbs: no registration from ironGate
6. **Root cause identified**: UFW had no RustDesk LAN/WG rules; relay key format had extra TOML quotes; service needed clean restart after boot

### Fixes Applied

- **UFW rules added on ironGate**:
  - `allow from 192.168.4.0/22 to any port 21115:21119 proto tcp` (RustDesk LAN)
  - `allow from 192.168.4.0/22 to any port 21116 proto udp` (RustDesk LAN UDP)
  - `allow from 10.13.37.0/24 to any port 21115:21119 proto tcp` (RustDesk WG mesh)
  - `allow from 10.13.37.0/24 to any port 21116 proto udp` (RustDesk WG mesh UDP)
- **RustDesk config cleaned**: Rewrote `RustDesk2.toml` (both user + root) with correct key format
- **Service restart**: Full kill + restart after boot stabilized the connection
- **SSH config**: Added `Host strandgate` → `192.168.4.169` (was missing)

### Key Discovery: Tower Atomic as Inner Membrane Fallback

The WireGuard mesh (`10.13.37.x`) provided the reliable path when all outer membrane access (RustDesk, direct SSH on LAN IP) failed. The tower atomic proved its value as the trust backbone:

```
sporeGate → wg0 → golgi hub ([RELAY_PUBLIC]) → wg0 → ironGate
   10.13.37.2                10.13.37.1              10.13.37.7
```

This path works regardless of LAN firewall state, RustDesk health, or SSH key enrollment on the LAN interface.

---

## Architectural Divergence: Outer Membrane Remote Access

### Current State (Ad-hoc)

Each gate manages its own remote access independently:
- RustDesk: per-gate install, per-gate relay key, per-gate firewall rules
- SSH: per-gate key enrollment, per-gate user/config
- No unified enrollment, no fleet-wide health check, no automatic recovery

### Proposed Evolution: Isomorphic Deployment Pattern

Remote access should follow the same inner/outer membrane separation as the rest of the architecture:

**Outer Membrane (User-Facing)**:
- RustDesk (or equivalent) for graphical remote access
- Unified relay configuration distributed from golgiBody
- Auto-enrollment via tower atomic trust chain
- Health watchdog: if outer membrane access fails, alert via inner membrane

**Inner Membrane (Primals/Ops)**:
- WireGuard mesh SSH (already working — tower atomic)
- `membrane` CLI for fleet operations
- Sovereign CI dispatch (already working — J12 pattern)

**Convergence Path**:
1. **G30**: Codify RustDesk relay config in `ecosystem_manifest.toml` (relay server, key, version)
2. **G31**: `membrane remote.enroll` — auto-configure RustDesk + UFW on any gate via WG SSH
3. **G32**: `membrane remote.health` — fleet-wide RustDesk connectivity probe
4. **G33**: Outer membrane watchdog — if RustDesk drops, auto-restart + alert via inner membrane channel

This is an isomorphic deployment divergence: the pattern that works (tower atomic mesh) should bootstrap and monitor the pattern that users interact with (RustDesk/outer membrane). The inner membrane manages the outer membrane, not the other way around.

---

## Fleet Topology Snapshot

| Gate | LAN IP | WG IP | Zone | SSH from sporeGate | RustDesk |
|------|--------|-------|------|-------------------|----------|
| sporeGate | 192.168.4.3 | 10.13.37.2 | House 1 | localhost | N/A |
| eastGate | 192.168.4.244 | — | House 1 | — | — |
| ironGate | 192.168.4.237 | 10.13.37.7 | House 2 | `irongate@10.13.37.7` ✓ | ✓ (fixed) |
| strandGate | 192.168.4.169 | — | House 2 | pending key enrollment | — |
| blueGate | 192.168.4.210 | — | House 2 | `user@blueGate` ✓ | — |
| northGate | 192.168.4.147 | — | House 2 | — | — |
| golgiBody | [RELAY_PUBLIC] | 10.13.37.1 | VPS | `root@golgi` ✓ | relay host |
| golgiBody-ext | 137.184.197.151 | — | VPS | needs key enrollment | — |

---

## Remaining Threads

| ID | Item | Owner | Status |
|----|------|-------|--------|
| G30 | Codify RustDesk relay in manifest | sporeGate | PROPOSED |
| G31 | `membrane remote.enroll` | sporeGate | PROPOSED |
| SSH-strand | Enroll SSH key on strandGate | sporeGate | PENDING (needs user) |
| SSH-golgi-ext | Enroll SSH key on golgiBody-ext | eastGate ops | PENDING |
| WG-ironGate-direct | ironGate WG peer direct (bypass golgi hop) | sporeGate | OPTIONAL |

---

*Filed from sporeGate overwatch. Tower atomic mesh validated as inner membrane trust backbone. Outer membrane remote access pattern identified as architectural divergence for isomorphic evolution.*
