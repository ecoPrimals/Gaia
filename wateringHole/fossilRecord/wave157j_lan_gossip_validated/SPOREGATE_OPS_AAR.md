# AAR: sporeGate Ops — Peer Registry Cleanup + Depot Rebuild — Wave 157j

**Gate:** sporeGate (foreman)  
**Date:** 2026-08-11  
**From:** overwatch (eastGate)  
**Classification:** OPERATIONAL — cascade, registry fix, depot rebuild, eastGate triage

---

## Executive Summary

Cascaded from Forgejo (git.primals.eco), fixed the root cause of stale peer
registry addresses in both cellMembrane cytoplasm and wateringHole topology,
rebuilt the depot (13/13 current), and triaged eastGate NUCLEUS state. The
LAN IP gap identified by southGate's validation (SOUTHGATE_LAN_GOSSIP_AAR.md)
is now closed in code and topology files.

---

## Actions Taken

### 1. Cascade from Forgejo

```
membrane temporal.cascade --source temporal
  synced=15 failed=0 (2 SKIP: plasmidBin, projectNUCLEUS — not cloned on foreman)
  15/15 repos at parity with canonical Forgejo HEAD
```

barraCuda flagged as having source drift from depot — auto-harvest built it
but sandbox staging failed (see §3).

### 2. Peer Registry Cleanup — Root Cause Fix

**Problem:** songBird's LAN discovery fell back to WG-era addresses
(`192.168.1.x`, `10.0.0.x`) because the cytoplasm registry and topology
map had no `lan_ip` entries for house2 gates.

**Fix (cellMembrane `b84bed6`):** Added confirmed LAN IPs to `MESH_REGISTRY`:

| Gate | LAN IP | Verification |
|------|--------|-------------|
| sporeGate | 192.168.4.3 | `ip addr` |
| eastGate | 192.168.4.244 | `ip addr` (already present) |
| ironGate | 192.168.4.237 | ARP + ping + `ip addr` via SSH |
| southGate | 192.168.4.149 | southGate head file + ARP + ping |
| strandGate | 192.168.4.169 | ARP + ping + `ip addr` via SSH |
| blueGate | 192.168.4.210 | ARP table (already present) |

Tests: `cellmembrane-types` — 264 passed, including `lan_address_known_gates`,
`lan_addresses_in_subnet`, `lan_address_wan_gates_return_none`.

**Fix (wateringHole `42834e5e1`):** Added `lan_ip` fields to all 7 confirmed
LAN peers in `TOPOLOGY_MAP.toml` `[mesh.songbird_covalent]` table. Added
sporeGate as a peer entry (was missing). Updated southGate status to
`live_lan_validated`.

### 3. Sandbox Permission Fix

Cascade auto-harvest for barraCuda failed:
```
[sandbox] barracuda: ERROR — build: stage binary: Permission denied (os error 13)
```

Root cause: `/opt/membrane/sandbox` and `/run/membrane/sandbox` owned by
`root:root`, membrane runs as user `sporegate`.

Fix: `chown sporegate:sporegate` on both directories.

### 4. Depot Rebuild

biomeOS was 1/13 stale (commit drift: depot=`ce812818` src=`650ac475`).

```
plasmid.build: biomeos → 16979KB blake3=2b27b932e0fb98b8 commit=650ac475
               target=x86_64-unknown-linux-musl elf=VERIFIED
```

songBird depot binary confirmed to already contain MeshRelay (binary strings:
`mesh.rel`, `p.spread`, relay symbols present).

Depot push: **10 pushed, 47 current, 0 failed** (57 total, 4 architectures).

Final: **13/13 current, 0 stale.**

### 5. eastGate Triage (from overwatch)

| Check | Result |
|-------|--------|
| NUCLEUS services | 14/14 active (all running) |
| Sockets | 52+ in `/run/user/1000/biomeos/` |
| Depot primals | 20 binaries present |
| Stuck processes | **8 killed** — `dispatch::tests::dispatch_hits_each` at 99.9% CPU since Aug 10 (1,922 min CPU time) |
| songBird logs | `trust.evaluate_peer` rejections — bearDog missing method |
| Hostname | `pop-os` (node_id mismatch — should be `southGate` or `eastGate`) |
| swarmVine socket | Connection refused (service running but socket not accepting) |

---

## Commits Pushed

| Repo | Hash | Summary |
|------|------|---------|
| cellMembrane | `b84bed6` | peer registry: add LAN IPs for ironGate, southGate, strandGate |
| wateringHole | `42834e5e1` | topology: add LAN IPs to songbird_covalent mesh peers (Wave 157j) |

---

## Final State

| Metric | Value |
|--------|-------|
| Depot staleness | **13/13 current, 0 stale** |
| Depot integrity | 15 verified, 0 hash mismatch, 0 missing |
| Mesh reachability | 9 peers, 9 reachable |
| Sovereignty S1-S3 | All OPERATIONAL |
| Crash-loops | 0 (14 services scanned) |
| Gate status | DEGRADED (expected for foreman — only 1/13 primals run locally) |

---

## Remaining Items

| Item | Owner | Detail |
|------|-------|--------|
| blueGate depot pull | blueGate | Fresh depot available (MeshRelay songBird + G72) |
| biomeOS category shadow | biomeOS (eastGate) | TOML translation shadowing — code team |
| swarmVine Windows UDS/TCP | swarmVine | 5 call sites need TCP fallback |
| southGate node_id fix | southGate | Hostname `pop-os` → gate name |
| bearDog `trust.evaluate_peer` | songBird × bearDog | API surface gap — songBird calls method bearDog doesn't implement |
| eastGate hostname | eastGate | Also reports `pop-os` — should match gate identity |
| vcs.parity drift | sporeGate | 23 repos show drift — need audit of local-only vs upstream |
