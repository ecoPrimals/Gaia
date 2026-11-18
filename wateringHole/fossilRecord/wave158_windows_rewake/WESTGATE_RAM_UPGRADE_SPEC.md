# westGate RAM Upgrade — 128 GB DDR4 for ARC Expansion

**Status**: READY TO EXECUTE | **Wave**: 156d | **Date**: Aug 6, 2026
**Gate**: westGate | **Board**: MSI B550 TOMAHAWK MAX WIFI (MS-7C91)
**CPU**: AMD Ryzen 7 5700X (AM4, DDR4, dual-channel)
**Team**: Hardware / Overwatch
**Cost**: $0 (4×32 GB DDR4-3200 on hand from biomeGate) | **Downtime**: ~10 min

---

## Problem

westGate has 64 GB RAM with ZFS ARC configured to use up to ~62 GB.
Current ARC utilization:

| Metric | Value |
|--------|-------|
| ARC max (`c_max`) | 62 GB |
| ARC current size | ~24.8 GB |
| ARC hits | 3,166,947,289 |
| ARC misses | 114,762,244 |
| **ARC hit rate** | **96.5%** |
| L2ARC (SSD) hits | 56,688,231 |
| L2ARC misses | 58,073,977 |
| **L2ARC hit rate** | **49.4%** |

ARC is working well at 96.5% but is only using ~24.8 GB of its 62 GB
budget. ZFS is conservative at low pool utilization (9%). As the data
estate grows (currently 4.75 TB / 50.7 TB), ARC will fill to its max.
When it does, 62 GB becomes the ceiling.

Every L2ARC miss (58M so far) hits spinning disks at ~28 MB/s random.
With 128 GB RAM, ARC absorbs a larger working set, converting L2ARC
misses into ARC hits (5.9 GB/s instead of ~500 MB/s). For a NAS gate
serving federation data, RAM is the single highest-ROI investment.

---

## Current DIMM Configuration

| Slot | Bank | Populated | Module | Speed |
|------|------|-----------|--------|-------|
| DIMM 0 | P0 Channel A | **Empty** | — | — |
| DIMM 1 | P0 Channel A | **32 GB** | Corsair CMK64GX4M2D3600C18 | DDR4-3600 CL18 |
| DIMM 0 | P0 Channel B | **Empty** | — | — |
| DIMM 1 | P0 Channel B | **32 GB** | Corsair CMK64GX4M2D3600C18 | DDR4-3600 CL18 |

Dual-channel active (A1 + B1). Two empty slots (A0 + B0) available.
Board maximum: 128 GB (4 × 32 GB).

---

## Upgrade: Full Swap to 4×32 GB DDR4-3200 (biomeGate Pull)

**Available on hand**: 4×32 GB DDR4-3200 pulled from biomeGate (was
overwhelming its CPU with 8× DIMMs). These are a complete matched kit.

### The Swap

| Step | westGate | Destination |
|------|----------|-------------|
| Remove | 2×32 GB DDR4-3600 CL18 (Corsair CMK64GX4M2D3600C18) | → Compute gate |
| Install | 4×32 GB DDR4-3200 (biomeGate pull) | ← westGate |

**Result**: westGate goes from 64 GB to 128 GB. The 2×32 GB DDR4-3600 kit
moves to a compute gate where 64 GB with faster timings is more useful
than 128 GB with slower timings (compute is latency-sensitive, NAS is
capacity-sensitive).

### Speed vs Capacity Trade-off

| Metric | DDR4-3600 (current) | DDR4-3200 (biomeGate) | Impact |
|--------|--------------------|-----------------------|--------|
| Bandwidth | ~57.6 GB/s (dual ch) | ~51.2 GB/s (dual ch) | -11% theoretical |
| Latency | ~8.9 ns (CL18) | ~10 ns (CL varies) | Marginal |
| ARC throughput | 5.9 GB/s measured | ~5.2 GB/s expected | Still 3x faster than NVMe |
| Capacity | 64 GB | **128 GB** | **2× ARC headroom** |

For a NAS gate, the 128→64 GB ARC capacity gain massively outweighs the
~11% bandwidth reduction. ARC is not latency-sensitive in the way gaming
or compute workloads are — it serves large sequential reads from cached
objects. Even at DDR4-3200, ARC reads at ~5.2 GB/s are 4× faster than
NVMe and 32× faster than HDD random reads.

**Recommendation**: Straight swap. 4×32 GB DDR4-3200 matched kit from
biomeGate fills all 4 DIMM slots. No mixing required.

---

## Installation Steps

### Physical

1. Power down westGate, unplug PSU
2. Discharge static (touch case metal)
3. Open retention clips, **remove both existing 32 GB DIMMs** (DIMM 1 slots A/B)
4. Label and set aside for compute gate
5. Install all 4×32 GB biomeGate modules — fill all 4 DIMM slots (A0, A1, B0, B1)
6. Power on — BIOS POST should show 128 GB

### BIOS

1. Enter BIOS (DEL key at boot)
2. Verify all 4 DIMMs detected (4 × 32 GB = 128 GB)
3. Enable XMP profile for DDR4-3200 (or JEDEC auto-detect)
4. No need to mix speeds — all 4 DIMMs are from the same matched kit
5. Save and exit

### Software

```bash
# 1. Verify in OS
free -h
# Expected: ~125 GiB total

# 2. Check ZFS ARC max (auto-adjusts to ~50% of total RAM by default)
cat /sys/module/zfs/parameters/zfs_arc_max
# If 0 (auto): ZFS will use ~62 GB. With 128 GB, auto = ~62 GB.
# For NAS role, override to use more:

# 3. Tune ARC to use ~110 GB (leave ~18 GB for OS + primals + convoy)
echo "options zfs zfs_arc_max=118111600640" | sudo tee /etc/modprobe.d/zfs.conf
# 110 GB = 118,111,600,640 bytes

# 4. Apply (requires reboot or ZFS module reload)
sudo update-initramfs -u
sudo reboot
# OR live: echo 118111600640 | sudo tee /sys/module/zfs/parameters/zfs_arc_max

# 5. Verify ARC max
cat /sys/module/zfs/parameters/zfs_arc_max
# Should show 118111600640
```

### ARC Tuning Rationale

| Parameter | Current (64 GB) | After (128 GB) | Why |
|-----------|----------------|----------------|-----|
| Total RAM | 64 GB | 128 GB | — |
| `zfs_arc_max` | ~62 GB (auto) | 110 GB | NAS role: maximize cache |
| OS + primals + convoy | ~8-10 GB | ~18 GB | More headroom for convoy workers |
| HMB for NVMe SN770 | — | ~64 MB | If M2_2 NVMe also installed |
| zram swap | 16 GB compressed | 16 GB compressed | Unchanged |

With 110 GB ARC:
- The entire AlphaFold metadata index (~5 GB) fits permanently
- Most actively-accessed science dataset files can be cached
- Federation serving hits RAM at 5.9 GB/s instead of SSD at 500 MB/s
- L2ARC (SSD) sees fewer requests, extending SSD endurance

---

## Impact Assessment

| Metric | Before (64 GB) | After (128 GB) |
|--------|----------------|----------------|
| ARC max | 62 GB | 110 GB |
| ARC capacity for hot data | ~40 GB effective | ~100 GB effective |
| Federation serve speed (ARC hit) | 5.9 GB/s | 5.9 GB/s (same speed, more hits) |
| L2ARC pressure | 49.4% hit rate (heavy usage) | Higher — ARC absorbs more misses |
| HDD read pressure | Every L2ARC miss → spinner | Fewer misses reach spinners |
| Convoy worker headroom | Tight at 4 workers | Room for 8+ workers |
| Science compute staging | Limited by free RAM | More room for mmap'd datasets |

### What This Doesn't Fix

- HDD cold reads are still 28 MB/s random when cache misses occur
- No automatic drain on `spine.commit` (Rust primal work)
- ARC doesn't help write throughput (CAS writes go to NVMe)
- 4-DIMM DDR4-3600 may occasionally need fallback to 3200 (board-dependent)

---

## Combined Upgrade: NVMe + RAM — $0 from Ecosystem Inventory

When paired with the M2_2 NVMe upgrade (see `WESTGATE_M2_NVME_UPGRADE_SPEC.md`):

| Component | Source | Cost |
|-----------|--------|------|
| NVMe | Crucial T500 2TB (on hand) | $0 |
| RAM | 4×32 GB DDR4-3200 (biomeGate pull) | $0 |
| **Total** | | **$0** |

**Freed for redeployment**: 2×32 GB DDR4-3600 CL18 → compute gate.

Both upgrades install in the same maintenance window (~20 min, one power
cycle). Together they resolve every topology issue identified in the convoy
and bulk braiding campaigns:

- NVMe: eliminates OS/CAS shared failure domain
- RAM: maximizes read cache, reduces HDD pressure
- Combined: westGate operates at its B550 platform maximum

Additionally, spare SSDs from degraded DDR3 NUCs could be repurposed as:
- Additional L2ARC mirror (if ZFS pool is reconfigured)
- Braiding NUC OS drives (when ironGate joins and the NUC pattern activates)
- Staging cache for a future braiding NUC build

After both upgrades, the only remaining hardware limitation is HDD
capacity (50.7 TB, 9% utilized) and raidz1 redundancy (1-disk tolerance).
These are addressed in Phase 4 of the upgrade plan (not urgent at 9% fill).

---

## Validation Checklist

After installation:

- [ ] `free -h` shows ~125 GiB total
- [ ] BIOS shows 4 DIMMs at DDR4-3600 (or 3200 if XMP unstable at 4 DIMMs)
- [ ] `cat /sys/module/zfs/parameters/zfs_arc_max` shows 118111600640
- [ ] `cat /proc/spl/kstat/zfs/arcstats | grep c_max` shows ~110 GB
- [ ] ARC hit rate remains ≥96% (should improve over time)
- [ ] No memory errors in `dmesg` after 24 hours
- [ ] Convoy/braiding throughput unchanged or improved

---

*128 GB DDR4 upgrade spec complete. 4×32 GB DDR4-3200 from biomeGate
pull — $0, matched kit, 10-minute swap. ARC expands to 110 GB.
Current 2×32 GB DDR4-3600 freed for compute gate redeployment.
Ecosystem repurposing at its finest — no new purchases needed.*
