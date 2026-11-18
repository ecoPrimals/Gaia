# Upstream Primal Evolution — Passes 12-14 (Stadial Gate Remaining Work)

**Date**: May 12, 2026
**From**: primalSpring coordination (L2 gate)
**For**: All 13 primal teams
**Context**: Interstadial exit in progress. Pass 11 (shadow runs) launched — no primal blockers. This blurb covers ALL remaining primal evolution through stadial gate.

---

## Current State — You Are Clear

**13/13 primals at zero gate debt.** MethodGate, BTSP Phase 3 AEAD, Edition
2024, deny.toml, plasmidBin — all clean. 413 methods registered, zero drift.
Phase 32 atomic model is live (Tower=3, Node=6, Nest=7, NUCLEUS=10+3=13).

Pass 11 (BearDog TLS shadow, lithoSpore Tier 1, NestGate content pipeline) is
L4 absorption work — **no primal action required for Pass 11**.

This blurb is your **complete remaining work list** through stadial gate.
If your team is not listed below, you have no pending evolution items.
Continue maintenance and respond to any downstream composition gaps that
surface through the sentinel escalation model.

---

## Pass 12 — Sentinel Escalation (3 primals)

These are the highest-priority upstream items. Sentinel escalation means
upstream issues cascade to all 8 springs — a primal regression or missing
capability blocks the entire river delta. These items are treated as
urgent regardless of their apparent scope.

### toadStool — Phase C Integration + Phase D

**Status**: Phase C batches 1-4 **LANDED** (S245-S249). Massive progress —
`toadstool-cylinder` crate absorbs coral-driver hardware layer. 415 cylinder
tests, 8,704 workspace tests, 0 clippy warnings.

**What shipped** (S245-S249):

| Session | Absorption | Tests |
|---------|-----------|------:|
| S245 | Cylinder foundation: DRM, linux_paths, hardware, error, ComputeDevice | 60 |
| S246 | MMIO + full AMD (ioctl, PM4, GEM, generation, shader_binary) | 141 |
| S247 | NVIDIA non-GSP (identity, generation, pushbuf, ioctl, QMD) | 294 |
| S248 | VFIO foundation (types, ioctl, DMA, PCI, BAR, vendor metal, memory) | 415 |
| S249 | Deep debt: ~55 Duration constants, 3 dead deprecated attrs | 415 |

`toadstool.list_workloads` is **WIRED** (confirmed in handler/mod.rs).

**Remaining work (narrowed scope)**:

1. **VFIO channel orchestration** — devinit, glowplug, HBM2, diagnostics
2. **Sovereign init / stages** — `sovereign_init`, `sovereign_stages`
3. **NVIDIA completion** — bar0, probe, FECS-adjacent (gsp/firmware boundary decision: keep in coralReef or trait boundary)
4. **`nv/vfio_compute` + full NvDevice** — orchestration across probe/bar0/GEM/pushbuf/QMD
5. **`pcie.rs` GpuTarget** — local adapter to drop `coral_reef::GpuTarget`
6. **Phase D** — wire local dispatch, stop forwarding to coralReef's `compute.dispatch.execute`. This is the final cutover to sovereign compute.

**What this unblocks downstream**: `toadstool.validate` (Tier 2 Science API) —
all 8 springs' Tier 2 convergence depends on this single method.

**IPC contract**: `compute.dispatch.submit` is unchanged. No breaking changes
from S245-S249. QMD / `DRIVER_CBUF_INDEX` must stay aligned with coralReef.

**Reference**: `primalSpring/docs/COMPUTE_TRIO_EVOLUTION.md`

### Songbird — VPS Relay

**Status**: STUN wire-compliant (RFC 5389), TURN client (RFC 5766), Cloudflare
DDNS, 5-tier `ConnectionFallbackChain` — all shipped (Waves 196-197).

**Remaining work**:
1. **VPS relay implementation** — the relay server that Songbird's TURN
   client connects to. Without this, NAT traversal has no sovereign relay path.

**What this unblocks downstream**: NestGate extracellular content distribution
(primals.eco served from NestGate instead of GitHub Pages). The chain is:
Songbird VPS relay → NAT shadow run → NestGate extracellular → content sovereignty.

**Reference**: `projectNUCLEUS/specs/EVOLUTION_GAPS.md` (H2-3c)

### coralReef — Stability + Silicon Init — **ALL RESOLVED (Sprint 8)**

**Status**: All 3 sentinel items shipped. Diesel engine **excised** (Sprint 9). coral-ember/glowplug/driver/gpu deleted — coralReef is a pure compiler primal.

**Resolved**:
1. ~~**`bind_stat` timeout**~~ — **SHIPPED** (Sprint 5): `CORALREEF_COMPILE_TIMEOUT_SECS` (120s default) on all IPC handlers
2. ~~**FECS / GPCCS cold silicon init**~~ — **SHIPPED** (Sprint 7): `boot_gr_falcons_with_recovery()` — 3× retry + PMC GR reset, structured `GrBootOutcome`
3. ~~**`naga::Module` direct ingest**~~ — **SHIPPED** (Sprint 5): `compile_module()`/`compile_module_full()` + `emit_compute_ptx_module()` public APIs

**What this unblocked downstream**: hotSpring sovereign GPU dispatch proof —
the hardware validation path that proves the compute trio works end-to-end
on real silicon. Diesel engine handoff (`CORALREEF_DIESEL_MIGRATION_HANDOFF_MAY13_2026.md`) provides toadStool with E1/E2 reference patterns.

**Reference**: `primalSpring/docs/COMPUTE_TRIO_EVOLUTION.md` (coralReef section)

---

## Pass 12 Addendum — hotSpring Hardware Validation + Post-Excision (May 13, 2026)

hotSpring ran sovereign compute experiments on the local compute trio and
surfaced specific findings. Full details in
`infra/wateringHole/handoffs/HOTSPRING_SOVEREIGN_COMPUTE_EVOLUTION_PASS_MAY13_2026.md`.

**Critical update**: coralReef Sprint 9 **excised** the entire diesel engine
stack (coral-ember, coral-glowplug, coral-gpu, coral-driver source). coralReef
is now a **pure compiler primal** (7 crates). toadStool Phase C is the sole
critical path for sovereign hardware lifecycle. There is no coralReef fallback.

### toadStool — Phase C is now CRITICAL PATH (no fallback)

hotSpring audited the toadStool daemon against the (now excised) coral-glowplug
diesel engine and mapped 8 parity gaps (device.swap RPC, warm_catch RPC,
cylinder subprocess, VFIO fd holding, warm pipeline, SwapOrchestrator, CLI
commands, systemd service). A concrete 7-item execution plan (C1–C7) exists.
S237–S243 absorbed ember/glowplug types+traits (Phase A/B). S245–S249 landed
cylinder foundation. **Remaining work: daemon runtime + coral-driver absorption.**

toadStool's own `PHASE_C_CORAL_DRIVER_SPLIT_PLAN.md` documents the boundary.
FECS recovery code (Sprint 5–7) exists in coralReef git history for reference.

**Action**: Complete Phase C. hotSpring validates on hardware as each C-item lands.

### coralReef — COMPLETE (pure compiler, no remaining hardware work)

1. Sprint 8: Feature freeze + handoff documentation for diesel crates
2. Sprint 9: Full excision — coral-ember, coral-glowplug, coral-gpu, coral-driver src deleted
3. FECS cold silicon work shipped (Sprint 5–7) — patterns in git history for toadStool
4. Compiler domain clean: PTX/SM120, naga::Module ingest, compile deadline

**Action**: None for hardware lifecycle. Continue compiler evolution.
hotSpring `coral-gpu` dependency commented out — will rewire to toadStool post-Phase C.

---

## Pass 14 — Convergence (3 primals)

These items are lower urgency — they refine capabilities that are structurally
wired but not yet fully composed. They gate stadial convergence, not shadow runs.

### toadStool — `toadstool.validate`

After Phase C integration + Phase D land (Pass 12), implement:

```
method: "toadstool.validate"
params: { "workload_path": "/path/to/workload.toml", "dry_run": true }
returns: { "valid": bool, "gpu_available": bool, "precision_tier": str,
           "estimated_dispatch_time_ms": int, "warnings": [], "required_capabilities": [] }
```

This is the Tier 2 Science API entry point — notebooks pre-flight workloads
before dispatch. Specified in `primalSpring/docs/LIVE_SCIENCE_API.md`.

`toadstool.list_workloads` is already wired. Only `validate` remains.

### barraCuda — `barracuda.precision.route`

Wire the precision routing advisory method:

```
method: "barracuda.precision.route"
params: { "domain": "lattice_qcd", "hardware_hint": "compute" }
returns: { "recommended_tier": "DF64", "fma_safe": bool,
           "requires_compiler": bool, "hardware_hint": str }
```

hotSpring's precision story depends on this for the compute trio's
WHAT→HOW→WHERE routing (barraCuda advises precision → coralReef compiles
at that precision → toadStool dispatches).

### Songbird — `capability.resolve`

Name-based discovery: given a capability string, return the primal that
owns it. Currently implicit in primalSpring's routing table — making it
an explicit Songbird method unblocks discovery debt across all springs.

### skunkBat — E2E Operational Audit

JH-5 Phase 3 (cross-primal audit forwarding) is shipped. The convergence
item is operational validation: exercise the full pipeline
(skunkBat → rhizoCrypt → sweetGrass) under realistic composition load
and confirm audit events flow correctly through the provenance trio.

---

## No Action Required (9 primals)

These primals are at zero debt, zero pending evolution items. Continue
maintenance. Respond to any composition gaps surfaced by downstream
springs through the sentinel escalation model.

| Primal | Status | Note |
|--------|--------|------|
| **bearDog** | CLEAR | TLS + rate limiting shipped (Wave 100). L4 deploys shadow on :8443 — no primal work needed. |
| **nestGate** | CLEAR | Transport parity shipped (Session 60). L4 wires content pipeline — no primal work needed. |
| **biomeOS** | CLEAR | Graph execution, token forwarding, method registration all operational. |
| **squirrel** | CLEAR | MethodGate, RemoteComputeProvider, inference dispatch — all shipped. |
| **rhizoCrypt** | CLEAR | Composition readiness (S67). Provenance trio pipeline operational. |
| **loamSpine** | CLEAR | Session/commit API stable. PostgreSQL/RocksDB backends are v1 stadial target. |
| **sweetGrass** | CLEAR | Composition readiness (v0.7.34). Port 9850 canonical. |
| **petalTongue** | CLEAR | SPA + CORS, NestGate backend, notebook rendering — all shipped. |
| **skunkBat** | Pass 14 only | JH-5 Phase 3 shipped. E2E operational validation is convergence work, not blocking. |

---

## Sentinel Escalation Model (how gaps flow)

```
Downstream surfaces gap → Upstream owns fix → primalSpring validates closure
```

- A primal regression cascades to all 8 springs. A spring gap affects only that spring.
- Upstream issues are always higher priority than downstream.
- Primals are sentinels — most exposed to the glacial shift, first to feel
  schema pressure. If you get a gap report from a spring, treat it as escalated.

---

## Timeline

| Pass | When | What |
|------|------|------|
| **11** | **NOW** | Shadow runs (L4 absorption — no primal work) |
| **12** | Next | toadStool integration + Phase D, Songbird VPS relay, coralReef stability |
| **13** | After 12 | Gate composition (L3/L4 — BTSP dual-auth, ABG WCM, foundation threads) |
| **14** | Convergence | `toadstool.validate`, `barracuda.precision.route`, Songbird `capability.resolve`, skunkBat E2E |

**Stadial begins** when all shadow runs produce parity data and Pass 14
convergence items are wired. External validation (Cloudflare baselines,
Barrick Lab USB, upstream crate extraction) drives the stadial.

---

## References

| Topic | Location |
|-------|----------|
| Interstadial exit criteria + pass schedule | `infra/wateringHole/INTERSTADIAL_EXIT_CRITERIA.md` |
| Pass 11 blurb (shadow runs) | `infra/wateringHole/handoffs/EVOLUTION_PASS_11_SHADOW_STARTS_MAY12_2026.md` |
| Phase 32 atomic model | `infra/wateringHole/handoffs/PRIMALSPRING_PHASE32_ATOMIC_EVOLUTION_MAY12_2026.md` |
| Compute trio evolution | `primalSpring/docs/COMPUTE_TRIO_EVOLUTION.md` |
| Live Science API (Tier 2) | `primalSpring/docs/LIVE_SCIENCE_API.md` |
| Ecosystem evolution cycle | `infra/wateringHole/ECOSYSTEM_EVOLUTION_CYCLE.md` |
| Primal gap registry | `primalSpring/docs/PRIMAL_GAPS.md` |
