# AAR: westGate Enrollment — Wave 155f

**Date**: Jul 28, 2026 13:00 EDT | **Wave**: 155f | **Gate**: westGate
**From**: westGate hardware/overwatch team
**Type**: After-Action Report — gate enrollment and sync

---

## Summary

westGate is synced and operating as a dev node. 41 repos pulled to Wave 155f
current via HTTPS public clone/pull. SSH push verified (handoff committed and
pushed to Forgejo). Gate is ready for Phase 3 code team spin-up.

**Next step**: Deploy Tower Atomic binaries from golgiBody depot.

---

## Divergences From Blurb

### D1: CPU — AMD Ryzen 7, not Intel i7 (SIGNIFICANT)

| Blurb Says | Actual |
|------------|--------|
| Intel i7-4771 (Haswell, 2013) | **AMD Ryzen 7 5700X** (Zen 3, 2022) |
| 4 cores / 8 threads | **8 cores / 16 threads** |
| No AMD cache hierarchy | **32MB L3 cache** (Zen 3 unified) |

**Impact**: This is better hardware than documented. The storage tiering
model's TIER 0 (AMD L3/L1 cache) **IS applicable** on this gate — the blurb
hedged with "if AMD CPU" and this gate qualifies. The Ryzen 7 5700X also
has significantly better single-thread and multi-thread performance than the
i7-4771, which matters for Rust compilation and CAS operations.

### D2: RAM — 64GB (not documented in blurb)

| Blurb Says | Actual |
|------------|--------|
| Not specified | **64GB DDR4** |
| — | 16GB zram compressed swap |

**Impact**: 64GB is substantial for TIER 1 (RAM/tmpfs/ramdisk). CAS can
use a large RAM cache tier before touching persistent storage.

### D3: NVMe Present — TIER 2 Confirmed

| Blurb Says | Actual |
|------------|--------|
| "NVMe if present" (uncertain) | **Samsung 970 EVO Plus 2TB NVMe** |
| — | Mounted as root `/`, 1.1TB free |

**Impact**: TIER 2 (fast persistent, sub-millisecond) is available. The
system runs entirely off this NVMe. This is the current working storage
for all repos, builds, and OS.

### D4: HDD Array — Raw, NOT in ZFS Pool

| Blurb Says | Actual |
|------------|--------|
| "76TB ZFS" / "5x14TB HDD" | 5× OOS14000G (12.7TB usable each) — **raw/unmounted** |
| ZFS pool active | **No ZFS pools** (`zpool list` → "no pools available") |

**Impact**: The HDDs exist but are not yet pooled or mounted. TIER 4 (cold/bulk
CAS) requires ZFS pool creation before nestGate can use it. This is a human
action item — pool creation requires decisions on:
- Topology: raidz1 (1 parity, ~50.8TB usable) vs raidz2 (2 parity, ~38.1TB) vs mirror+stripe
- Dataset layout for CAS tiers
- Whether to reserve a drive as hot spare

### D5: No SSD (TIER 3 absent)

| Blurb Says | Actual |
|------------|--------|
| "2.5" SSD available" | **No SATA SSD detected** |

**Impact**: TIER 3 is absent. The tiering model jumps from NVMe (TIER 2) to
HDD (TIER 4) once the pool is created. A 2.5" SSD can be added later to fill
the gap, but the three-tier profile (NVMe→RAM→HDD) is sufficient for initial
Nest Atomic validation.

### D6: Hostname

| Blurb Says | Actual |
|------------|--------|
| westGate | **pop-os** |

**Impact**: Cosmetic. Should be set to `westgate` via `sudo hostnamectl set-hostname westgate`
during Phase 2 enrollment.

---

## Actual Storage Tiering Profile (westGate)

```
TIER 0 — AMD Ryzen 7 5700X L3 (32MB)     ← AVAILABLE (Zen 3 unified cache)
TIER 1 — 64GB DDR4 RAM (tmpfs/ramdisk)    ← AVAILABLE
TIER 2 — Samsung 970 EVO Plus 2TB NVMe    ← AVAILABLE (1.1TB free, root FS)
TIER 3 — (absent — no SATA SSD)           ← NOT AVAILABLE
TIER 4 — 5×14TB HDD (OOS14000G)           ← RAW/UNMOUNTED (needs ZFS pool)
```

For nestGate CAS profiling, TIERs 0–2 are ready now. TIER 4 requires human
intervention to create the ZFS pool.

---

## Sync Execution Log

| Step | Result |
|------|--------|
| Phase 0: SSH host key scan | DONE |
| Phase 0: SSH config added | DONE (`forgejo` + `git.primals.eco`) |
| Phase 0: SSH auth verified | DONE (`golgiAdmin` / `westGate-wave155f` key) |
| Phase 1a: Naming fixes | 3 renames (`beardog`/`nestgate`/`songbird`), 2 dupes removed, 1 branch `master→main` |
| Phase 1a: toadStool | Was symlink → toadstool. Both removed, cloned fresh |
| Phase 1b: Remote repoint | 27 repos GitHub → Forgejo HTTPS (pull) + SSH (push for wateringHole) |
| Phase 1c: Clone missing | 13 repos cloned (toadStool, cellMembrane, lithoSpore, projectFOUNDATION, projectNUCLEUS, helixVision, initioChem, metalForge, coralForge, rustChip, fossilRecord, agentReagents, benchScale) |
| Phase 1d: Pull all | 41/41 repos at Wave 155f HEAD |
| Phase 1e: State files | wave.toml, ECOSYSTEM_BLURB.md, ORTHOGONAL_DIMENSIONS_REVIEW.md — all present and current |
| Phase 1f: Push test | Sync report committed and pushed to Forgejo — VERIFIED |

### Minor Notes

- `springs/coralForge`: empty repo (no commits). Either new or name mismatch on Forgejo.
- `primals/nestGate`: has `vendor/` directory (untracked, likely generated).
- Remotes: HTTPS for fetch, SSH for push (wateringHole only per convergence rule).

---

## Depot Accessibility

| Check | Result |
|-------|--------|
| `https://depot.primals.eco/` | **HTTP 200** — depot index accessible |
| `https://depot.primals.eco/primals/` | **HTTP 200** — primal listing accessible |
| beardog binary (`x86_64-unknown-linux-musl`) | **HTTP 200** — 11.5MB |
| Architecture | `x86_64` — matches depot target |

Tower Atomic genomeBins are fetchable. Ready for Phase 2 binary deployment.

---

## Recommendations

1. **Register westGate hardware accurately** in blurb/gate profiles:
   AMD Ryzen 7 5700X, 64GB RAM, 2TB NVMe, 5×14TB HDD (raw)
2. **ZFS pool creation** (human action) before Nest Atomic TIER 4 work
3. **Hostname set** to `westgate` during Phase 2
4. **Proceed with Tower Atomic deployment** — depot is reachable, binaries serve,
   architecture matches

---

*westGate Wave 155f: Dev node ONLINE. 41 repos synced. SSH push verified.
Hardware divergences documented (AMD Ryzen 7 5700X, not i7-4771; 64GB RAM;
2TB NVMe present; HDDs raw/no ZFS pool). Depot accessible. Ready for Tower
Atomic binary deployment.*
