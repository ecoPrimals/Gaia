# westGate 4-Tier Storage Architecture

**Date**: Aug 5, 2026 | **Gate**: westGate (Data NAS)
**Context**: Convoy provenance I/O analysis revealed write contention on
spinning raidz1. NVMe hot tier eliminated the bottleneck (2.7x improvement).
This generalizes into a 4-tier storage architecture for data ingest,
braiding, and federation serving.

---

## Hardware Tiers

| Tier | Device | Capacity | Speed | Role |
|------|--------|----------|-------|------|
| **T0: RAM** | DDR4 (ZFS ARC) | 39.5 GB (auto) | ~100 GB/s | Hottest reads. ZFS auto-manages. 98% hit rate. |
| **T1: NVMe** | Samsung 970 EVO Plus 2TB | 1.6 TB free | 1.7 GB/s write, 3.5 GB/s read | **Hot ingest + braiding.** CAS writes land here. |
| **T2: SSD** | Crucial BX500 2TB | 1.8 TB (L2ARC) | ~500 MB/s | **Warm read cache.** ZFS L2ARC. 65.9% hit rate. |
| **T3: HDD** | 5× 14TB OOS14000G (raidz1) | 58.5 TB free | 28 MB/s write, 9 MB/s read | **Cold archive.** Bulk storage. Sequential access. |

## Data Flow: Ingest → Braid → Archive → Serve

```
DOWNLOAD          BRAID (hot)        ARCHIVE (cold)      SERVE (federation)
  │                  │                    │                    │
  ▼                  ▼                    ▼                    ▼
Internet ──1G──► NVMe CAS ──batch──► ZFS raidz1 ◄──read──── songBird
  │           (1.7 GB/s write)    (sequential rsync)     │
  │           BLAKE3 + put         zero contention        ▼
  │           DAG + spine                              ironGate
  │                                                   (federation pull)
  │
  └──► ARC (RAM) ◄──automatic──► L2ARC (SSD)
       98% hits                  65.9% hits
       (hottest objects)         (warm read cache)
```

### Phase 1: Hot Ingest (NVMe)

New data enters through NVMe. Download scripts and convoy workers write
CAS objects to `/mnt/cas-hot` (ext4 on NVMe). The 500K random-write IOPS
of NVMe means CAS puts are effectively free — the bottleneck becomes
source file reads from spinning disks (which now have zero write contention).

**Convoy improvement**: 80/s → 217/s combined (2.7×) by eliminating
spinner read/write contention.

### Phase 2: Warm Cache (SSD L2ARC)

ZFS automatically promotes frequently-read cold data to L2ARC (SSD).
This is transparent — no manual management. The BX500 2TB serves as a
read cache with 65.9% hit rate. Objects accessed multiple times (e.g.,
tideGlass science queries) get promoted automatically.

### Phase 3: Cold Archive (HDD raidz1)

After hot ingest completes, data is migrated from NVMe to ZFS raidz1
via sequential rsync or `zfs send`. Sequential writes are 5-10x more
efficient than random writes on spinning disks. The migration can run
during off-peak hours.

### Phase 4: Federation Serving

When ironGate requests `content.replicate.pull`:
- Objects in ARC (RAM): served at memory speed (~100 GB/s)
- Objects in L2ARC (SSD): served at SSD speed (~500 MB/s)
- Objects on NVMe hot tier: served at NVMe speed (~3.5 GB/s)
- Objects on HDD cold: served at spinner speed (~100 MB/s seq, 9 MB/s random)

The tiering is transparent to the federation consumer. ZFS automatically
manages T0 (ARC) and T2 (L2ARC) promotion. Only T1 (NVMe hot) and T3
(HDD cold) require manual or scripted migration.

---

## Measured Results

| Metric | Before (all-spinner) | After (NVMe hot) |
|--------|---------------------|-------------------|
| CAS write latency | ~4ms (spinner random) | ~0.02ms (NVMe) |
| Convoy combined rate | 80/s | 217/s |
| Spinner iowait | 29% | ~15% (reads only) |
| Write bandwidth | 28.7 MB/s on spinners | 1.7 GB/s on NVMe |
| ETA (11M files) | ~26h | ~14h |

## Configuration

### Active (during convoy)

```
NESTGATE_STORAGE_PATH=/mnt/cas-hot          # NVMe hot tier
```

### Post-convoy (archive mode)

```bash
# Migrate hot → cold
rsync -av --progress /mnt/cas-hot/ /mnt/nestgate/cold/zfs/cas/

# Restore cold path
NESTGATE_STORAGE_PATH=/mnt/nestgate/cold/zfs/cas
```

### Future: Permanent 2-tier nestGate

nestGate could natively support multi-path storage:
- `NESTGATE_HOT_PATH=/mnt/cas-hot` (NVMe, new writes)
- `NESTGATE_COLD_PATH=/mnt/nestgate/cold/zfs/cas` (HDD, archived)
- Read: check hot first, fall back to cold
- Background migrator: hot → cold after N hours or when hot tier > threshold

This is a primal capability gap worth upstreaming.

---

*The principle: write fast (NVMe), read smart (ARC → L2ARC → NVMe → HDD),
serve from the fastest available tier. The tiering is partially automatic
(ZFS ARC/L2ARC) and partially managed (hot NVMe ↔ cold HDD migration).*
