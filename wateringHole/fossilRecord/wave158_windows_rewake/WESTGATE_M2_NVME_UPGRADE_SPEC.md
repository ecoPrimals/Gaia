# westGate M2_2 NVMe Upgrade — Dedicated CAS Hot Tier

**Status**: READY TO EXECUTE | **Wave**: 156d | **Date**: Aug 6, 2026
**Gate**: westGate | **Board**: MSI B550 TOMAHAWK MAX WIFI (MS-7C91)
**Team**: Hardware / Overwatch
**Cost**: $0 (Crucial T500 2TB on hand) | **Downtime**: ~15 min (physical install + mount)

---

## Problem

westGate's Samsung 970 EVO Plus 2TB serves triple duty:
1. OS root filesystem (`/`)
2. CAS hot tier (`/mnt/cas-hot`)
3. Bulk braider staging (`/mnt/cas-hot/_stage`)

This shared arrangement caused an ENOSPC event on Aug 5 when CAS writes
filled the OS drive to 100%. The multi-tier CAS deployment (cross-tier
dedup + 10 GB high-water mark) prevents a repeat, but the fundamental
issue remains: CAS and OS share a single failure domain.

**Current state** (Aug 6):

| Partition | Size | Used | Free | Use% |
|-----------|------|------|------|------|
| `/` (nvme0n1p3) | 1.8 TB | 958 GB | 774 GB | 56% |

Of the 958 GB used, ~177 GB is OS + packages + user data. The remaining
~780 GB is CAS objects from the convoy + staging residue. This will grow
as more datasets are braided.

---

## Solution: M2_2 Slot — Dedicated CAS NVMe

The MSI B550 TOMAHAWK has two M.2 slots:

| Slot | Interface | Current | PCIe Spec |
|------|-----------|---------|-----------|
| M2_1 | M-Key, CPU-direct | Samsung 970 EVO+ 2TB (OS) | PCIe 4.0 x4 (3.0 device) |
| M2_2 | M-Key, chipset | **EMPTY** | PCIe 3.0 x4 |

M2_2 is located below the CPU socket, between the PCIe x16 slots. It
shares bandwidth with the B550 chipset's PCIe 3.0 x4 uplink but has
dedicated lanes for M.2 traffic.

**PCIe 3.0 x4 theoretical**: ~3.5 GB/s read, ~3.3 GB/s write
**PCIe 3.0 x4 practical**: ~3.0 GB/s read, ~2.5 GB/s write (NVMe overhead)

This exceeds every downstream consumer:
- 10G NIC: 1.25 GB/s (NVMe is 2× faster)
- HDD sequential staging: 161 MB/s (NVMe is 15× faster)
- Convoy braiding: ~107 MB/s sustained write (NVMe has 23× headroom)

---

## Available Drive: Crucial T500 2TB

On hand from existing inventory — no purchase needed.

| Spec | Value |
|------|-------|
| Model | Crucial T500 2TB |
| Interface | PCIe 4.0 x4 NVMe (M.2 2280, M-Key) |
| Sequential read | 7,400 MB/s (PCIe 4.0) → **~3,500 MB/s in M2_2** (PCIe 3.0 x4 ceiling) |
| Sequential write | 7,000 MB/s (PCIe 4.0) → **~3,000 MB/s in M2_2** |
| TBW | 1,200 TBW |
| DRAM cache | Yes (Micron 232-layer NAND + DRAM) |
| Controller | Phison E26 |

The T500 is a top-tier PCIe 4.0 drive. In the M2_2 slot (PCIe 3.0 x4),
it'll be capped at ~3.5 GB/s read / ~3.0 GB/s write — still 2x faster
than the current 970 EVO+ measured speeds (2.5/1.5 GB/s). The DRAM cache
and high write endurance (1,200 TBW) make it ideal for sustained CAS
convoy writes. 2 TB provides headroom for staging + CAS hot tier
simultaneously (AlphaFold staging at 122 GB won't trigger backpressure).

---

## Installation Steps

### Physical

1. Power down westGate
2. Remove GPU (RTX 3070) to access M2_2 slot underneath
3. Remove M2_2 heatsink (B550 TOMAHAWK includes one)
4. Insert NVMe into M2_2 at 30° angle, press flat, secure with standoff screw
5. Replace heatsink and GPU
6. Power on — BIOS should detect new NVMe automatically

### Software

```bash
# 1. Verify detection
lsblk | grep nvme
# Expected: nvme0n1 (existing OS) + nvme1n1 (new CAS)

# 2. Create GPT partition table + single partition
sudo parted /dev/nvme1n1 mklabel gpt
sudo parted /dev/nvme1n1 mkpart cas-hot ext4 0% 100%

# 3. Format as ext4 (not ZFS — CAS hot tier is ephemeral, no need for COW)
sudo mkfs.ext4 -L cas-hot /dev/nvme1n1p1

# 4. Create mount point
sudo mkdir -p /mnt/cas-hot-new

# 5. Add to fstab
echo 'LABEL=cas-hot /mnt/cas-hot-new ext4 defaults,noatime,discard 0 2' | sudo tee -a /etc/fstab

# 6. Mount
sudo mount /mnt/cas-hot-new

# 7. Migrate existing CAS objects from OS drive
# (only if objects remain on /mnt/cas-hot from OS partition)
sudo rsync -a --remove-source-files /mnt/cas-hot/ /mnt/cas-hot-new/
sudo rmdir /mnt/cas-hot
sudo ln -s /mnt/cas-hot-new /mnt/cas-hot
# OR: update NESTGATE_WARM_PATHS directly

# 8. Update nestGate env
# In ~/.config/systemd/user/nestgate.env:
#   NESTGATE_WARM_PATHS=/mnt/cas-hot-new
#   (or /mnt/cas-hot if symlinked)

# 9. Restart nestGate
systemctl --user restart nestgate-tower.service

# 10. Verify
df -h /mnt/cas-hot-new
# Should show ~1.8 TB (2 TB drive) with near-zero usage
```

### Why ext4, Not ZFS

The CAS hot tier is ephemeral — objects drain to ZFS cold on
`spine.commit`. Using ZFS on the hot tier adds COW write amplification
(the exact problem that motivated the NVMe hot tier). ext4 with
`noatime,discard` gives raw NVMe write speed for CAS objects.

ZFS ARC/L2ARC caching is irrelevant here — the hot tier is write-heavy,
and reads come from the cold ZFS pool (which has ARC + L2ARC).

---

## Post-Install Configuration

### nestGate env (`~/.config/systemd/user/nestgate.env`)

```
NESTGATE_WARM_PATHS=/mnt/cas-hot-new
NESTGATE_COLD_PATHS=/mnt/nestgate/cold/zfs/cas
NESTGATE_WARM_MIN_FREE_BYTES=10737418240
```

### XDG symlink (if still using symlink routing)

```bash
# Point to new drive instead of cold or old CAS-hot
ln -sf /mnt/cas-hot-new ~/.local/share/nestgate/storage
```

### Bulk braider staging

Update `STAGE_ROOT` in `bulk_braid.py`:
```python
STAGE_ROOT = Path("/mnt/cas-hot-new/_stage")
```

Or keep using `/mnt/cas-hot/_stage` if symlinked.

---

## Impact Assessment

| Metric | Before (shared NVMe) | After (dedicated NVMe) |
|--------|---------------------|----------------------|
| OS ENOSPC risk | Mitigated by backpressure, not eliminated | **Eliminated** — separate filesystem |
| CAS write speed | 1.5 GB/s (shared with OS I/O) | ~2.5 GB/s (dedicated, no contention) |
| Staging capacity | ~774 GB free (shared) | ~1.8 TB free (dedicated) |
| ARC impact | None | -64 MB (HMB for SN770 mapping tables) |
| Convoy throughput | 313/s (already NVMe-limited by hashing) | 313+/s (no OS contention) |
| Hot tier drain | rsync from OS partition | rsync from dedicated partition |
| OS I/O latency | Occasional stalls during CAS bursts | **No CAS contention** |

### What This Doesn't Fix

- ARC is still at 8.7/62 GB (RAM upgrade needed separately)
- HDD cold reads are still 28 MB/s random (unchanged)
- No automatic drain on `spine.commit` (Rust primal work)
- sweetGrass convergence backpressure still polling-based

---

## Validation Checklist

After installation:

- [ ] `lsblk` shows two NVMe devices
- [ ] `df -h /mnt/cas-hot-new` shows ~1.8 TB free
- [ ] `dd if=/dev/zero of=/mnt/cas-hot-new/test bs=1M count=1024 oflag=direct` reports >1 GB/s
- [ ] nestGate `content.put` writes to new drive (check with `ls /mnt/cas-hot-new/`)
- [ ] Cross-tier dedup works (re-CAS a known file, verify `deduplicated: true`)
- [ ] Bulk braider staging works (`python3 bulk_braid.py --only kegg --dry-run`)
- [ ] OS drive not filling during braiding (`df -h /` stays stable)

---

*M2_2 NVMe spec complete. Crucial T500 2TB on hand — $0, DRAM-cached,
1200 TBW endurance. 15-minute install, zero-downtime migration with rsync.
Eliminates the OS/CAS shared failure domain permanently.*
