# AAR: Inner Membrane Enrollment via Pure Primals Compositions — Wave 157k

**Gate:** sporeGate (foreman)
**Date:** 2026-08-12
**From:** sporeGate topology team
**Classification:** ARCHITECTURAL — inner membrane evolution, deployment pipeline, NanoWire retirement

---

## Executive Summary

Implemented the Inner Membrane Enrollment plan: evolved gate enrollment and
cascade to use pure primal compositions on the inner membrane (primal.eco) via
Tower Atomic mesh. Fixed live infrastructure (Caddy, dnsmasq, petalTongue
deployment), wired cascade.notify gossip types in swarmVine, brought
nestgate.io Phase 2 (depot + provenance) from code to production, and produced
a comprehensive NanoWire/SSH retirement checklist covering 18 files and 19
retirement items across 7 priority tiers.

---

## Architecture Delivered

```
primals.eco (outer membrane)     — public pull surface: Forgejo, depot, docs, TLS/Caddy
  └── Gates pull updates via HTTPS

primal.eco (inner membrane)      — sealed mesh: enrollment, cascade, config push
  └── songBird mesh dispatch via capability.call
  └── cascade.notify gossip → autonomous gate pulls
  └── No SSH, SCP, rsync, or NanoWire

nestgate.io (peptidoglycan)      — federated braid CAS between layers
  └── /depot/ — architecture browser with BLAKE3 provenance
  └── /provenance/ — hash-based binary lookup (prefix match)
  └── Phase 3: federated CAS via songBird content.locate
```

---

## Actions Taken

### 1. Fixed live.primals.eco 502

- **Root cause:** Caddyfile routed `live.primals.eco` to port `9900` but
  petalTongue binds `:8190` on sporeGate
- **Fix:** Changed port in `/etc/membrane/Caddyfile` on golgiBody, reloaded Caddy
- **Result:** `live.primals.eco` → HTTP 200
- **Spec updated:** `THREE_DOMAIN_TOPOLOGY_SPEC.md` port references corrected

### 2. SSH/NanoWire Retirement Audit

- Audited all 135 `.rs` files in membrane-shadow `src/`
- Found **18 files** with live SSH shell-out, **0 rsync**, **0 live NanoWire**
- Produced `NANOWIRE_RETIREMENT_CHECKLIST.md` with 7 priority tiers:
  - Tier 1: Already mesh-native (sub-builder dispatch, Forgejo API, Neural Bridge)
  - Tier 2: High-value retirements (gate.pull/check/info, service.*, plasmid.trigger)
  - Tier 3: Depot push (depot_sync, plasmid.refresh)
  - Tier 4: Caddy/TLS (gateway module migration)
  - Tier 5: Enrollment/provisioning (gate.enroll, gate.provision)
  - Tier 6: Relay/mirror (relay.ship)
  - Tier 7: Git transport (GIT_SSH_COMMAND → HTTPS)
- Central choke point: `ssh.rs` — all SSH/SCP flows through 9 functions here
- Shadow validation strategy documented (--mesh flag → compare → drop SSH)

### 3. dnsmasq LAN Entries for Inner Membrane

- Added LAN IPs (192.168.4.x/22) for 6 same-subnet gates:
  - sporeGate `192.168.4.3`, eastGate `192.168.4.244`, ironGate `192.168.4.237`
  - southGate `192.168.4.148`, strandGate `192.168.4.169`, blueGate `192.168.4.210`
- Added `wg.<gate>.primal.eco` aliases for explicit WireGuard routing
- WAN/VPS gates (flockGate, graftGate, grapheneGate) remain on WG overlay
- Bare `primal.eco` → `192.168.4.3` (sporeGate foreman, LAN)
- Verified all resolving via dnsmasq on localhost

### 4. cascade.notify Gossip Domain Types

- Added to swarmVine-core `domain_types.rs`:
  - `CascadeNotification` — foreman injects on Data topic after Forgejo push
  - `CascadeResult` — each gate reports cascade completion to mesh
  - `DepotFreshness` — gate advertises depot state after rebuild/sync
- Key convention: `cascade.notify:all` (fleet-wide), `cascade.result:{gate}`
- 4 new tests, all passing (141/141 total swarmVine tests)
- Pushed: `cb58d32` (swarmVine master)

### 5. nestgate.io Phase 2 — Depot + Provenance Routes

- Added 5 routes to petalTongue `peptidoglycan.rs`:
  - `GET /depot/` — architecture overview (4 archs, 54 binaries, 594MB)
  - `GET /depot/{arch}` — per-binary listing with BLAKE3 checksums
  - `GET /depot/{arch}/{name}` — single binary provenance details
  - `GET /provenance/` — provenance chain overview
  - `GET /provenance/{hash}` — BLAKE3 prefix-match lookup across all archs
- Reads per-architecture `BLAKE3SUMS` files (b3sum standard format)
- Pushed: `947183a7` (Phase 2 routes), `7ffb7a21` (BLAKE3SUMS format fix)

### 6. Deployment Pipeline End-to-End

- **Service unit drift fixed:** systemd unit said `--port 9900` but process
  ran with `--bind 10.13.37.2:8190`. Fixed unit to match reality.
- **Stale binary resolved:** running binary was `(deleted)` inode — three
  different hashes across three locations. Built fresh, deployed atomically.
- **Added `ECOP_DEPOT_PATH` env** to service unit so `/depot/` routes find
  the local binary tree at runtime.
- **Added `nestgate.io` to CORS** allowed origins.
- **Regenerated BLAKE3SUMS** for x86_64-unknown-linux-musl depot.
- **Pushed to golgiBody WAN depot** — binary `c68f735a...` with matching
  BLAKE3SUMS file.

---

## Commits

| Repo | Hash | Description |
|------|------|-------------|
| swarmVine | `cb58d32` | cascade domain types: CascadeNotification, CascadeResult, DepotFreshness |
| petalTongue | `947183a7` | nestgate.io Phase 2: /depot/ and /provenance/ peptidoglycan routes |
| petalTongue | `7ffb7a21` | peptidoglycan: read per-arch BLAKE3SUMS files instead of checksums.toml |
| wateringHole | `6a6f98e0d` | inner membrane: NanoWire retirement checklist + Phase 2 spec update |

---

## Verification

| Surface | Route | Status |
|---------|-------|--------|
| `live.primals.eco` | `/` | HTTP 200 |
| `nestgate.io` | `/depot/` | 4 architectures, checksums=true |
| `nestgate.io` | `/depot/x86_64-unknown-linux-musl` | 16 binaries, 15 with BLAKE3 |
| `nestgate.io` | `/depot/x86_64-unknown-linux-musl/songbird` | Full provenance JSON |
| `nestgate.io` | `/provenance/` | 4 architectures tracked |
| `nestgate.io` | `/provenance/0ae06747` | Prefix match → songbird binary |

---

## Artifacts Created

- `infra/wateringHole/specs/NANOWIRE_RETIREMENT_CHECKLIST.md` — 19 retirement items, 7 tiers
- `infra/wateringHole/specs/THREE_DOMAIN_TOPOLOGY_SPEC.md` — Phase 2 marked ACTIVE
- `/etc/dnsmasq.d/primal-eco.conf` — LAN + WG dual resolution
- `/etc/systemd/system/membrane-petaltongue.service` — corrected bind/args/env

---

## Next Steps

- Wire `cascade.notify` into membrane dispatch (Tier 2 retirement items R-01, R-02)
- Add `--mesh` shadow flag to `gate.pull` / `gate.check` for SSH→mesh comparison
- nestgate.io Phase 3: federated CAS via songBird `content.locate` mesh queries
- Evolve `/provenance/` with build commit, source repo, and DAG provenance chains

---

## Lessons Learned

1. **Service unit drift is real.** Someone restarted petalTongue with different
   args months ago and the unit file was never updated. The running process used
   a deleted binary on a different port than the unit specified. Infrastructure
   as code means the unit file must be the source of truth.

2. **Checksum format matters.** Assumed TOML checksums based on Phase 1 design,
   but the depot pipeline actually produces standard `b3sum` output files. Ship
   code that reads what's actually on disk, not what the spec imagined.

3. **The NanoWire retirement is mostly about depot push.** Sub-builder dispatch
   is already mesh-native. The biggest SSH debt is in `plasmid.refresh` and
   `depot_sync --push` (SCP binaries + remote systemctl). Once mesh file relay
   or HTTPS depot push exists, half the SSH call sites become dead code.
