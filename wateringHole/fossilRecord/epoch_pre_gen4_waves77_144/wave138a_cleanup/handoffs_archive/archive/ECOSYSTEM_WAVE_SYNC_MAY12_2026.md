# Ecosystem Wave Sync — May 12, 2026

**Date**: May 12, 2026
**From**: primalSpring coordination (L2 gate)
**For**: All teams — primals, springs, products
**Signal**: Pass schedule acceleration. Multiple Pass 12/14 items resolved same-day.

---

## What Just Happened

The ecosystem shipped a coordinated wave today. Four primals and five springs
pushed evolution that collapsed the pass schedule forward significantly.

### Resolved Today

| Item | Pass | Who | What |
|------|:----:|-----|------|
| **toadStool Phase C** | 12 | toadStool | **COMPLETE** — S245-S250, 7 batches, +42K lines, `toadstool-cylinder` crate (520 tests, 8,809 workspace). DRM, AMD, NV, VFIO channel, devinit, glowplug, HBM2, sovereign init/stages — all absorbed. |
| **`toadstool.validate`** | 14 | toadStool | **IMPLEMENTED** (S250) — workload pre-flight: `valid`, `gpu_available`, `precision_tier`, `estimated_dispatch_time_ms`, `warnings`, `required_capabilities` |
| **`toadstool.list_workloads`** | 14 | toadStool | **WIRED** (S245+) |
| **Phase D plumbing** | 12 | toadStool | `LocalDeviceFactory`, `try_local_dispatch()`, server depends on cylinder. Default still forwards to coralReef — factory hook-up is stadial. |
| **`barracuda.precision.route`** | 14 | barraCuda | **IMPLEMENTED** — `precision.rs` + 242 unit tests + 407 trio E2E tests |
| **Songbird TURN server** | 12 | Songbird | 836-line TURN server shipped. MethodGate modularized (944L monolith → 5 focused files). 5 dead examples removed. |
| **coralReef FECS boot** | 12 | coralReef | **STABILITY PROOF SHIPPED** (Sprint 7) — `boot_gr_falcons_with_recovery()` (3× retry + PMC GR reset), structured `GrBootOutcome`, all boot/ACR/sovereign paths recovery-aware. Sprint 5-6: ISA latency tables, SPH header parsing, PTX SM120 subgroup scans, `naga::Module` direct ingest, error hardening. |

### Spring Evolution (same day)

| Spring | What Shipped |
|--------|-------------|
| **hotSpring** | 4 new validation scenarios (dielectric, gradient flow, screened Coulomb, transport), LTEE B2 `expected_values.json` + control README, `--format json` |
| **wetSpring** | LTEE B7 Rust validator (`validate_ltee_b7_v1.rs`, 219 lines), Tier 2 upstream handoff |
| **neuralSpring** | NestGate IPC module (218 lines — weight storage!), per-primal IPC modules (7 primals), LTEE mutation accumulation control README |
| **healthSpring** | Tower atomic IPC module (91 lines), validate improvements, `--format json` |
| **ludoSpring** | UniBin CLI expansion |
| **groundSpring** | V138 — B4 LTEE citrate (Blount 2008/2012), `--format json` on all 37 binaries (local) |
| **airSpring** | LTEE E3 Rust validator, `--format json`, AG-001 resolved, Thread 4 expression (local) |

---

## What This Means

### Tier 2 Is UNBLOCKED

`toadstool.validate` + `toadstool.list_workloads` are both live upstream.
`barracuda.precision.route` is implemented with full test coverage.

**All 8 springs can now wire Tier 2 convergence:**
1. Add `--format json` to validation binaries (hotSpring, healthSpring, groundSpring, airSpring already done)
2. Wire `toadstool.validate` for workload pre-flight
3. Wire `barracuda.precision.route` for precision advisory

### Pass Schedule — Updated

| Pass | Status | Remaining |
|------|--------|-----------|
| **11** | **ACTIVE** | Shadow runs (BearDog TLS, lithoSpore Tier 1, NestGate content) — no blockers, L4 work |
| **12** | **3/3 RESOLVED** | ~~toadStool Phase C~~ DONE. Songbird VPS relay progressing (TURN shipped). ~~coralReef FECS~~ **STABILITY PROOF SHIPPED** (Sprint 7). |
| **13** | Pending | BTSP dual-auth, ABG WCM, foundation threads — L3/L4 composition |
| **14** | **2/5 RESOLVED** | ~~`toadstool.validate`~~ DONE. ~~`barracuda.precision.route`~~ DONE. Remaining: ionic runtime, skunkBat E2E, Songbird `capability.resolve`. |

### Remaining Sentinel Blockers (2 items)

| Primal | What | Status |
|--------|------|--------|
| **Songbird** | VPS relay server | TURN foundation shipped — relay implementation in progress |
| **coralReef** | FECS/GPCCS cold silicon stability | **SHIPPED** — `boot_gr_falcons_with_recovery()` (3× retry + PMC GR reset), structured `GrBootOutcome`, all boot paths recovery-aware (Sprint 7) |

Everything else on the interstadial exit path is L3/L4 composition and
shadow run work — not sentinel blockers.

---

## For Each Audience

### Primals

The upstream primal evolution blurb (`UPSTREAM_PRIMAL_EVOLUTION_PASS_12_14_MAY12_2026.md`)
was issued earlier today. **toadStool and barraCuda have already resolved their
items from that blurb.** Songbird and coralReef: your Pass 12 work is progressing
well — keep pushing. All other primals: you remain clear.

### Springs

The river delta blurb (`RIVER_DELTA_EVOLUTION_MAY12_2026.md`) still applies.
**New development**: Tier 2 is now unblocked. If you already have `--format json`
(hotSpring, healthSpring, groundSpring, airSpring — you do), you can begin
Tier 2 wiring against `toadstool.validate` immediately.

Priority update for springs:
1. **Tier 2 wiring** — newly unblocked, start now
2. **LTEE handoffs** — lithoSpore team spinning up, have your artifacts ready
3. **Foundation thread expressions** — Threads 3, 4, 8, 9, 10 still need expressions
4. **Spring-specific gaps** — per your blurb

### projectNUCLEUS / lithoSpore / Foundation

Pass 11 shadow runs have no blockers. Start immediately:
- BearDog TLS on :8443
- lithoSpore Tier 1 (groundSpring B1-B3, hotSpring B2, neuralSpring B1 all ready)
- NestGate content pipeline (`publish_sporeprint.sh`)

The lithoSpore + foundation team inherits a strong position — 4 springs have
LTEE reproductions ready for module integration, 7/10 foundation threads are
seeded, and the Tier 2 API is now live.

---

## References

| Topic | Location |
|-------|----------|
| Upstream primal evolution (Passes 12-14) | `handoffs/UPSTREAM_PRIMAL_EVOLUTION_PASS_12_14_MAY12_2026.md` |
| River delta evolution (springs) | `handoffs/RIVER_DELTA_EVOLUTION_MAY12_2026.md` |
| Pass 11 shadow runs | `handoffs/EVOLUTION_PASS_11_SHADOW_STARTS_MAY12_2026.md` |
| Interstadial exit criteria (v1.4) | `INTERSTADIAL_EXIT_CRITERIA.md` |
| Compute trio evolution | `primalSpring/docs/COMPUTE_TRIO_EVOLUTION.md` |
| Live Science API (Tier 2) | `primalSpring/docs/LIVE_SCIENCE_API.md` |
| Ecosystem evolution cycle | `ECOSYSTEM_EVOLUTION_CYCLE.md` |
