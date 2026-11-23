# AAR: westGate ZFS Pool Creation — Wave 155i

**Date**: Jul 29, 2026 08:13 EDT | **Wave**: 155i | **Gate**: westGate
**From**: westGate hardware/overwatch team
**Type**: After-Action Report — P1 #5 resolved: ZFS pool online

---

## Summary

westGate `nestgate` ZFS pool is **ONLINE** — 25.4TB usable across 2 mirrored
vdevs + 1 hot spare. Existing pool from prior dev/test sessions imported
(essentially empty), expanded with remaining drives. CAS dataset layout created
for Nest Atomic tiered storage. TIER 4 (HDD/cold/bulk) is operational.

**P1 #5 (westGate ZFS pool creation) is RESOLVED.**

---

## Pool Topology

```
nestgate (ONLINE, 25.4TB)
├── mirror-0 (sdd + sdb)            ← 12.7TB, from prior pool
│   ├── ata-OOS14000G_0006DCVL      sdd
│   └── ata-OOS14000G_0007JBSV      sdb
├── mirror-1 (sda + sdc)            ← 12.7TB, added this session
│   ├── ata-OOS14000G_00017N66      sda (was hot spare, promoted)
│   └── ata-OOS14000G_0007QG7Q      sdc (wiped, added)
└── spare
    └── ata-OOS14000G_0007LBE0      sde (wiped, designated spare)
```

**Topology rationale**: Mirror vdevs give the best read IOPS (important for CAS
random reads), tolerate 1 failure per vdev, and the hot spare covers a second
failure. This matches Nest Atomic's needs — CAS workloads are read-heavy with
large sequential writes during ingestion.

| Metric | Value |
|--------|-------|
| Raw capacity | 5 × 12.7TB = 63.5TB |
| Usable capacity | **25.4TB** (2 mirror vdevs) |
| Hot spare | 1 × 12.7TB (sde) |
| Redundancy | 1 disk failure per vdev |
| Compression | lz4 (all datasets) |
| atime | off |

---

## Dataset Layout (CAS-Oriented)

| Dataset | Mountpoint | RecordSize | Quota | Purpose |
|---------|------------|------------|-------|---------|
| `nestgate` | `/mnt/nestgate/cold/zfs` | 128K | — | Pool root |
| `nestgate/cas` | `.../cas` | 1M | — | CAS root |
| `nestgate/cas/objects` | `.../cas/objects` | 128K | — | Content-addressed objects |
| `nestgate/cas/metadata` | `.../cas/metadata` | 128K | — | Object metadata / indices |
| `nestgate/cas/bulk` | `.../cas/bulk` | 1M | — | Large blob storage (AlphaFold PDBs) |
| `nestgate/data` | `.../data` | 1M | 20T | General data |
| `nestgate/cache` | `.../cache` | 128K | — | Hot cache tier on HDD |
| `nestgate/snapshots` | `.../snapshots` | 128K | — | ZFS snapshots |
| `nestgate/testing` | `.../testing` | 128K | — | Test datasets |

**RecordSize rationale**:
- 128K for metadata/objects: matches typical CAS hash-addressed blocks
- 1M for bulk/data: large sequential writes (PDB files, dataset ingestion)

All datasets have `compression=lz4` (fast, low CPU). Protein structures
(PDB/mmCIF) compress well — expect 2-3x ratio on AlphaFold data.

---

## Actions Taken

| Step | Detail |
|------|--------|
| Import existing pool | `nestgate` mirror (sdd+sdb) imported, ~1MB used |
| Wipe sdc | `wipefs -a /dev/sdc` — old GPT partition table |
| Wipe sde | `wipefs -a /dev/sde` — old btrfs filesystem |
| Promote sda | Removed from spare role |
| Add mirror-1 | sda + sdc as second mirror vdev |
| Add spare | sde as hot spare |
| Configure pool | `compression=lz4`, `atime=off`, `xattr=sa` |
| Create CAS datasets | `cas`, `cas/objects`, `cas/metadata`, `cas/bulk` |
| Set permissions | `chown westgate:westgate` on CAS tree |
| Verify Tower | All 3 primals healthy after disk operations |

---

## Updated Tiering Profile (westGate)

```
TIER 0 — AMD Ryzen 7 5700X L3 (32MB)     ← AVAILABLE
TIER 1 — 64GB DDR4 RAM (tmpfs/ramdisk)    ← AVAILABLE
TIER 2 — Samsung 970 EVO Plus 2TB NVMe    ← AVAILABLE (1.1TB free, root FS)
TIER 3 — (absent — no SATA SSD)           ← NOT AVAILABLE
TIER 4 — ZFS mirror pool, 25.4TB usable   ← ONLINE (this AAR)
         5×14TB HDD, 2 mirror vdevs + spare
         Mountpoint: /mnt/nestgate/cold/zfs
```

All Nest Atomic storage tiers except TIER 3 (SSD) are now operational.
nestGate CAS can profile read/write latencies across TIERs 0, 1, 2, and 4.

---

## Divergence: Existing Pool Topology

The prior pool used a 2-disk mirror with a hot spare (conservative for
dev/test). We expanded to 2 mirror vdevs rather than converting to raidz.
This demonstrates that ecoPrimals deployment can adapt to existing storage
topology — import what exists, expand incrementally. This is the pattern for
standing up Nest Atomic on gates with existing infrastructure.

---

## Update: Reboot + SSD Added (Jul 29 08:25 EDT)

Gate rebooted. Tower Atomic survived reboot — all 3 systemd user units came
back active (linger working as intended). ZFS pool required re-import.

### ZFS Auto-Import Enabled

Enabled `zfs-import-cache`, `zfs-mount`, and `zfs.target` systemd services.
Pool will auto-import on future reboots.

### SSD Added — TIER 3 Operational (Crucial BX500 2TB SATA)

A **Crucial BX500 2TB SATA SSD** was plugged in (`/dev/sdf`). Old OS partitions
wiped. Added to the `nestgate` pool as **L2ARC read cache** — ZFS will
automatically cache hot CAS reads on the SSD, accelerating repeat access to
frequently-queried objects without any application changes.

```
nestgate (ONLINE, 25.4TB + 1.82TB L2ARC)
├── mirror-0 (sdd + sdb)            ← 12.7TB data
├── mirror-1 (sda + sdc)            ← 12.7TB data
├── cache
│   └── ata-CT2000BX500SSD1_2452E99C5541  ← 1.82TB L2ARC read cache (TIER 3)
└── spare
    └── ata-OOS14000G_0007LBE0      ← hot spare
```

| Device | Model | Serial | Size | Role |
|--------|-------|--------|------|------|
| sdf | Crucial BX500 SSD | 2452E99C5541 | 2TB | L2ARC read cache |

### Updated Tiering Profile (all tiers operational)

```
TIER 0 — AMD Ryzen 7 5700X L3 (32MB)     ← AVAILABLE
TIER 1 — 64GB DDR4 RAM (ARC)              ← AVAILABLE (ZFS ARC uses RAM automatically)
TIER 2 — Samsung 970 EVO Plus 2TB NVMe    ← AVAILABLE (root FS, 1.1TB free)
TIER 3 — Crucial BX500 2TB SATA SSD       ← ONLINE (L2ARC read cache)
TIER 4 — ZFS mirror pool, 25.4TB usable   ← ONLINE (2 mirror vdevs + spare)
```

**All 5 tiers are now operational.** The ZFS ARC (RAM) + L2ARC (SSD) + mirror
vdevs (HDD) form a complete caching hierarchy that maps directly to Nest
Atomic's storage tiering model.

---

## Next Steps

1. **Configure nestGate primal** to use `/mnt/nestgate/cold/zfs/cas/` as CAS root
2. **E2E Nest Atomic validation** — small PDB ingestion test through the pipeline
3. **AlphaFold bulk ingestion** (~1TB) from northGate through full pipeline

---

*westGate Wave 155i: ZFS pool ONLINE. 25.4TB usable + 2TB SSD L2ARC cache.
All 5 storage tiers operational (cache→RAM→NVMe→SSD→HDD). ZFS auto-import
enabled. Tower survived reboot. P1 #5 resolved. Ready for nestGate CAS
configuration and E2E Nest Atomic validation.*
