# AAR: Foreman Pipeline G69 Phase 3 + Gate Hygiene + Sub-Builder Dispatch

**Date**: Aug 13, 2026 | **Wave**: 157k | **Gate**: sporeGate (foreman)
**Commits**: `f6ea497` (sub-builder fan-out), `a38c70d` (G69 Phase 3 CAS), `703aed0` (gate.hygiene)

---

## Problem

golgiBody (10GB VPS) hit 100% disk — Forgejo couldn't accept pushes.

**Root cause (layered)**:
1. **Forgejo repo-archive cache**: 3.3GB of generated download tarballs, never cleaned
2. **No CAS archival on push**: old binaries overwritten on golgiBody with no copy anywhere
3. **aarch64 depot push**: 860MB of new binaries added without old ones being archived first
4. **Legacy `/opt/membrane/`**: 119MB of obsolete binaries (caddy, rustdesk, old primals)
5. **Hygiene via cron**: initial fix was a jelly string — external cron, not composition-native

## Resolution

### G69 Phase 3: CAS Archival Before Overwrite (`a38c70d`)

Modified `push_single_binary()` in `depot_sync.rs`:

```
new binary ready
  → SCP old binary FROM golgiBody → foreman CAS: $DEPOT/cas/{arch}/{blake3}
  → BLAKE3 verify on download (integrity)
  → Dedup check (skip if already archived)
  → Record lineage event (lineage.jsonl)
  → THEN overwrite on golgiBody
```

- Added `ssh::scp_from()` — inverse of `scp_to()` for pulling files from remote
- CAS uses BLAKE3 as filename — content-addressed, zero new infrastructure
- golgiBody never holds the only copy of an old generation again

### Gate Hygiene: Composition-Native Cleanup (`703aed0`)

Replaced external cron with `run_gate_hygiene()` in cascade `post_sync`:

- Runs as final phase of every cascade post-sync on every gate
- Forgejo `repo-archive`: purge files older than 24h
- Journal vacuum to 50MB
- Temp file cleanup
- Reports via cascade log: `[hygiene] forgejo-archive: freed`
- No cron, no external dependencies, topology-aware

### Cascade Sub-Builder Fan-Out (`f6ea497`)

Wired `dispatch_to_sub_builders()` into `post_sync_harvest.rs`:

- After local harvest, fans out to all manifest-registered sub-builders
- Transport: `TransportEndpoint::MeshRelay { peer_id, capability: "build" }`
- Zero SSH — pure Tower Atomic (songBird) mesh dispatch
- ironGate registered as `aarch64-unknown-linux-musl` sub-builder

### Immediate Cleanup

- Purged `/opt/forgejo/data/repo-archive/` (3.3GB)
- Cleaned `/opt/membrane/` legacy binaries (100MB)
- Apt cache + old logs cleaned
- Disk: 100% → 62% (3.6GB recovered)
- Forgejo restarted, accepting pushes

## Data Flow (Now)

```
cascade tick (15m)
  → sync repos from Forgejo
  → detect drift → harvest locally (x86_64-musl)
  → fan out to sub-builders via mesh (ironGate: aarch64-musl, etc.)
  → sandbox validate
  → CAS archive old binary from golgiBody → foreman $DEPOT/cas/{arch}/{blake3}
  → push new binary to golgiBody (SCP + atomic rename)
  → push metadata (provenance, BLAKE3SUMS)
  → gate.hygiene: auto-clean Forgejo cache, journal, tmp
  → gossip: depot.updated
```

## CAS Storage Targets (Next)

| Gate | Storage | Role | Status |
|------|---------|------|--------|
| sporeGate | Local CAS (`$DEPOT/cas/`) | Foreman staging | **LIVE** |
| ironGate | 14TB NFT braid | Binary CAS primary (hot) | NEXT |
| westGate | 50.7TB ZFS | Binary CAS secondary (cold) | NEXT |

Replication from foreman CAS to ironGate/westGate via mesh `content.put` is the next evolution step.

## Lessons

1. **VPS relay nodes must stay thin.** golgiBody is a HEAD pointer, not storage. The push pipeline must archive before overwrite.
2. **No jelly strings.** Crons, rsync scripts, manual SCP — all replaced by composition-native lifecycle phases. The gate cleans itself.
3. **Sub-builder dispatch via mesh is the topology.** SSH dispatch works but isn't the architecture. Tower Atomic mesh is.
4. **BLAKE3 is the universal key.** Same hash validates integrity, serves as CAS address, tracks lineage, and deduplicates. One hash, four purposes.
