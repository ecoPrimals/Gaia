# AAR: westGate Persistence Hardening

**Date**: Aug 1, 2026 16:35 EDT
**Gate**: westGate
**Wave**: 155n post-threshold
**Author**: westGate overwatch (agent-assisted)
**biomeOS**: v4.56.0 (13/13 active post-reboot)

---

## TL;DR

After a reboot revealed that ZFS pool didn't auto-import and 5 NUCLEUS units were disabled,
hardened all persistence layers: ZFS auto-import via cachefile, all 13 NUCLEUS units enabled
with proper boot ordering, daily ZFS snapshots (keep 14), monthly scrubs, CAS roundtrip
verified, PDB rsync redirected to ZFS-direct, boot check script shipped. 9/9 PASS on boot
verification. westGate now survives reboot with zero manual intervention.

---

## What Was Broken

| Issue | Impact | Root Cause |
|-------|--------|-----------|
| ZFS pool not auto-imported | CAS offline after reboot, 41 GB inaccessible | `cachefile` not set at pool creation |
| 5 NUCLEUS units disabled | toadstool, barracuda, coralreef, petaltongue, squirrel wouldn't start on boot | Never enabled during initial deployment |
| No boot dependency ordering | nestGate could start before ZFS mounted → empty CAS | No `After=` on ZFS readiness |
| PDB rsync to /tmp | 2.4 GB lost on reboot | Volatile staging directory |
| No ZFS scrub/snapshot schedule | Silent data corruption risk | Not configured |

## What Was Fixed

### ZFS Persistence

| Fix | What | How |
|-----|------|-----|
| Auto-import | Pool imports on boot | `zpool set cachefile=/etc/zfs/zpool.cache nestgate` |
| Monthly scrub | Detect silent corruption | systemd timer: `zfs-scrub-nestgate.timer` (monthly) |
| Daily snapshots | Point-in-time recovery | systemd timer: `zfs-snapshot-nestgate.timer` (daily, keep 14) |
| Properties | Reduce writes, improve integrity | `atime=off`, `compression=lz4`, `checksum=on` |

### NUCLEUS Persistence

| Fix | What | How |
|-----|------|-----|
| Enable all units | 13/13 start on boot | `systemctl --user enable` for toadstool, barracuda, coralreef, petaltongue, squirrel |
| ZFS readiness gate | NUCLEUS waits for ZFS | `zfs-nestgate-ready.service` — polls for `/mnt/nestgate/cold/zfs/cas` up to 60s |
| Boot ordering | nestGate starts after ZFS | `After=zfs-nestgate-ready.service` in nestgate-tower unit |
| beardog ordering | All primals start after crypto | `After=beardog-tower.service` in all GPU/rendering units |
| NUCLEUS target | One-command start/stop | `nucleus.target` — `Wants=` all 13 services + neural-api |

### Boot Dependency Chain

```
system boot
  → ZFS import (zfs-import-cache.service)
  → ZFS mount (zfs-mount.service)
  → user session (lingering enabled)
    → zfs-nestgate-ready.service (polls for mount, max 60s)
    → beardog-tower.service (first — crypto foundation)
      → nestgate-tower.service (CAS — needs ZFS + beardog)
        → rhizocrypt-tower.service (DAG — needs nestgate)
        → loamspine-tower.service (ledger — needs nestgate)
          → sweetgrass-tower.service (attribution — needs all provenance)
      → songbird-tower.service (network — needs beardog)
      → skunkbat-tower.service (BTSP — needs beardog)
      → {barracuda, coralreef, petaltongue, squirrel, toadstool} (GPU/render)
      → neural-api-tower.service (biomeOS coordinator)
```

### Data Pipeline Persistence

| Fix | What | How |
|-----|------|-----|
| PDB rsync to ZFS | Data survives reboot | Redirected from `/tmp` to `/mnt/nestgate/cold/zfs/data/pdb_mmcif/` |
| pdb-rsync.service | On-demand rsync unit | `systemctl --user start pdb-rsync.service` (not auto-enabled) |
| Boot check script | Post-reboot verification | `scripts/westgate_boot_check.sh` — 9-point check |

---

## Boot Check Results (current)

```
--- ZFS ---
  PASS  ZFS pool imported
  PASS  ZFS mounted
  PASS  ZFS zero errors
  PASS  Data directories (11)
  PASS  CAS objects (4758)

--- NUCLEUS ---
  PASS  Services active (13/13)
  PASS  Sockets (17)
  PASS  biomeOS health (v4.56.0 Coordinated 487caps)

--- Provenance Pipeline ---
  PASS  CAS put roundtrip

Results: 9 PASS  0 WARN  0 FAIL
```

---

## Observations

1. **Reboot exposed all the gaps.** The original deployment was done as a single session —
   start services, create pool, ingest data. None of that was persisted. A reboot should be
   a non-event for a data federation root. Now it is.

2. **ZFS snapshots are free insurance.** At lz4 compression with mostly-static science data,
   daily snapshots cost almost nothing. 14-day rolling window means we can recover from
   accidental deletion or corruption within two weeks.

3. **The dependency chain matters.** nestGate starting before ZFS mounts means an empty CAS.
   The `zfs-nestgate-ready.service` gate ensures the mount exists before any primal that needs
   it starts. This is the same pattern as southGate's validation (user-space paths, no root
   required) — just applied to ZFS mounts.

4. **PDB rsync to ZFS is the right pattern.** Long-running downloads should target persistent
   storage directly, not volatile staging. rsync's idempotency means we can restart any time
   without re-downloading. The `pdb-rsync.service` unit makes this a one-command operation.

---

*westGate persistence hardened. 9/9 boot check PASS. ZFS auto-imports, NUCLEUS auto-starts
with proper ordering, CAS survives reboot, daily snapshots, monthly scrubs. PDB rsync
targets ZFS directly. The data federation root survives power cycles.*
