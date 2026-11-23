# sporeGate Stability & Systemd Registry Convergence AAR

**Date**: Aug 14, 2026 07:33 EDT | **Wave**: 157k | **Gate**: sporeGate (foreman)
**Trigger**: High fan / elevated CPU load observed overnight. Process audit revealed systemic orphan process accumulation.

---

## Root Cause

**Systemd unit name registry mismatch** — the compile-time service registry in `cellmembrane-types/src/service/registry.rs` mapped every primal to the wrong systemd unit name:

| Primal | Registry Said | Actual Unit |
|--------|---------------|-------------|
| beardog | `beardog-membrane.service` | `membrane-beardog.service` |
| songbird | `songbird-relay.service` | `songbird-gateway.service` |
| skunkbat | `skunkbat-membrane.service` | `membrane-skunkbat.service` |
| petaltongue | `petaltongue-membrane.service` | `membrane-petaltongue.service` |
| ... (all 13) | `{primal}-membrane.service` | `membrane-{primal}.service` |

When the cascade's `nucleus_restart` phase attempted to restart services after binary updates, `systemctl restart {wrong-name}` failed silently and fell back to `restart_bare_process()` — spawning raw orphan processes that accumulated across every 15-minute cascade cycle.

### Secondary: Dual songbird services

Two competing systemd units managed songbird:
- `songbird-gateway.service` — rich config (drawbridge, proxy, mesh-init, `Restart=always`)
- `membrane-songbird.service` — newer naming convention

Both launched the same binary on the same socket. The gateway's `Restart=always` kept respawning after conflicts.

---

## Fixes Applied

### 1. Registry Convergence (`cellmembrane-types`)

Updated all 13 `systemd_unit` entries in `registry.rs` to match deployed unit names:

```
SONGBIRD:     "songbird-relay.service"     → "songbird-gateway.service"
BEARDOG:      "beardog-membrane.service"   → "membrane-beardog.service"
PETALTONGUE:  "petaltongue-membrane.service" → "membrane-petaltongue.service"
... (10 more: {primal}-membrane → membrane-{primal})
```

Binary rebuilt and deployed. `cargo test -p cellmembrane-types` passes.

### 2. Songbird Service Consolidation

- Disabled `membrane-songbird.service` (newer but less configured)
- Kept `songbird-gateway.service` as authoritative (drawbridge, proxy routes, mesh-init)
- Added `membrane-compat.conf` drop-in with `FAMILY_ID`, `FAMILY_SEED`, `ECOPRIMALS_ROOT`

### 3. Process Cleanup

- Killed accumulated orphan processes from previous cascade cycles
- Restarted all 15 primal systemd services to clean state
- Removed stale sockets (`/run/membrane/ai.sock`, `neural-api-default.sock`)
- Confirmed `pop-upgrade.service` remains masked (prior session fix)

### 4. CAS Replication Wiring (depot_sync.rs)

Added `replicate_to_cas_nodes()` function — after archiving a binary to local CAS, replicates to configured storage nodes (currently ironGate at `/mnt/nestgate/cas`). Dedup-aware: checks remote existence before transfer.

---

## Verification

- Cascade fired at 07:30 EDT — **zero orphan processes spawned**
- Process count stable at 15 (14 primals + biomeos dual-mode)
- Biomeos children: 0 (no accumulation)
- Load: 1.62 (down from 5+ during build spike)
- CPU temp: 42°C
- All 15 systemd services ACTIVE
- All depot binaries MATCH between depot and `/usr/local/bin`

---

## Impact

This was a slow-leak stability issue. Every 15-minute cascade cycle that encountered a binary update would spawn 1+ orphan processes. Over hours/days, this accumulated dozens of duplicate processes consuming memory and CPU. The registry fix ensures `nucleus_restart` uses the correct systemd unit names, eliminating orphan spawning entirely.

---

## Files Changed

| File | Change |
|------|--------|
| `cellmembrane-types/src/service/registry.rs` | 13 systemd_unit entries corrected |
| `cellmembrane-types/src/service/mod.rs` | Doc comment updated |
| `membrane-shadow/src/plasmid/depot_sync.rs` | CAS replication to ironGate |
| `/etc/systemd/system/songbird-gateway.service.d/membrane-compat.conf` | New drop-in |
| `membrane-songbird.service` | Disabled |
