# Evolution Pass 11 — Parallel Shadow Starts

**Date**: May 12, 2026
**From**: primalSpring coordination
**For**: All teams (copy-paste ready)
**Pass**: 11 of 14 toward interstadial exit
**Blocking**: Nothing — all upstream work is shipped. Start immediately.

---

## Context

Pillar 5 (river delta) is **MET**. All 8 springs are Tier 4 IPC-first.
All 13 primals at zero gate debt. Phase 32 atomic model is live
(Tower=3, Node=6, Nest=7, NUCLEUS=10+3=13).

The interstadial exit gate now depends on **shadow runs executing** —
sovereign infrastructure running alongside existing services, producing
comparison data that proves parity. Pass 11 starts the three shadow runs
that have zero blockers.

**Pull before starting**: `infra/wateringHole`, `primalSpring`, all `primals/` repos.

---

## Three Parallel Actions

### 1. BearDog TLS Shadow on :8443

**Owner**: projectNUCLEUS (L4 absorption)
**Upstream**: BearDog Wave 100 shipped TLS termination + rate limiting

**What to do**:
- Deploy BearDog TLS on `:8443` alongside the existing Cloudflare proxy
- Measure request latency, error rates, certificate renewal against
  Cloudflare baselines on the same traffic
- Document parity metrics in `projectNUCLEUS/shadow-runs/beardog-tls/`
- The shadow period runs until parity is proven; cutover is stadial work

**Success**: BearDog TLS serving real traffic on `:8443`, metrics
pipeline producing comparison data vs Cloudflare.

### 2. lithoSpore Tier 1 Integration

**Owner**: lithoSpore team (L4 integration)
**Upstream**: groundSpring B2+B1 reproductions COMPLETE (Python 9/9 + Rust 10/10)

**What to do**:
- Integrate groundSpring B2 (Wiser 2013 fitness) into `ltee-fitness` module
- Integrate groundSpring B1 (Barrick 2009 mutation) into `ltee-mutation` module
- Fetch real data from Dryad (Wiser 2013) and NCBI (Barrick 2009)
- BLAKE3-hash fetched data into NestGate content storage via `fetch_and_hash.sh`
- Run module validation: Python `expected_values.json` + Rust `validate_ltee_*` binary
- neuralSpring B1 Rust binary (`validate_ltee_b1_mutation_accumulation`, S201b)
  is also ready for ML surrogate modules when you get to it

**Success**: At least 2 lithoSpore modules producing PASS at Tier 1
with real hashed data. This satisfies Pillar 4 of the interstadial exit.

### 3. NestGate Content Pipeline

**Owner**: projectNUCLEUS (L4 absorption)
**Upstream**: NestGate Session 60 — `content.*` transport parity on all 4 surfaces

**What to do**:
- Wire `publish_sporeprint.sh` to push sporePrint artifacts to NestGate
  via `content.put` + `content.publish`
- Serve published content via NestGate extracellular (replaces GitHub Pages
  for `primals.eco` static content)
- Validate that `content.get` returns byte-identical content to what was put
- Document the publish pipeline in `projectNUCLEUS/shadow-runs/nestgate-content/`

**Success**: sporePrint artifacts served from NestGate, byte-parity
with existing GitHub Pages content.

---

## What's Next (Passes 12-14)

Pass 11 runs in parallel with no blockers. While shadow runs execute,
the ecosystem advances through:

- **Pass 12** (Upstream Sentinel): toadStool Phase C integration
  (batches 1-4 landed — remaining: VFIO channels, sovereign init, NvDevice,
  Phase D), Songbird VPS relay, coralReef stability — these are escalated
  because upstream issues cascade to all downstream.
- **Pass 13** (Gate Composition): BTSP dual-auth, ABG WCM through
  provenance trio, foundation thread seeding (3, 4, 8, 9, 10)
- **Pass 14** (Convergence): Tier 2 Science API (`toadstool.validate` —
  `list_workloads` already wired), ionic runtime, skunkBat E2E audit,
  CompositionContext L2 pass

---

## toadStool Update (amended — S245-S249 landed)

toadStool just shipped Phase C batches 1-4 (S245-S249, +20,090 lines).
The new `toadstool-cylinder` crate absorbs the coral-driver hardware layer:

| Session | What Landed | Tests |
|---------|-------------|------:|
| S245 | Cylinder foundation: DRM, linux_paths, hardware, error, ComputeDevice | 60 |
| S246 | MMIO + full AMD path (ioctl, PM4, GEM, generation, shader_binary) | 141 |
| S247 | NVIDIA non-GSP (identity, generation, pushbuf, ioctl, QMD) | 294 |
| S248 | VFIO foundation (types, ioctl, DMA, PCI discovery, BAR cartography, vendor metal) | 415 |
| S249 | Deep debt: ~55 Duration constants, 3 dead deprecated attrs, audit clean | 415 |

**Key facts**:
- `toadstool.list_workloads` is **WIRED** — already implemented upstream
- `toadstool.validate` is still **NOT IMPLEMENTED** — remains the Tier 2 blocker
- `CORALREEF_*` env vars migrated to `TOADSTOOL_*` (legacy fallback retained)
- No IPC contract changes — `compute.dispatch.submit` unchanged
- Workspace: 8,704 lib tests, 0 clippy warnings

**Remaining Phase C** (narrowed scope):
- VFIO channel orchestration (devinit, glowplug, HBM2, diagnostics)
- Sovereign init / stages
- NVIDIA: bar0, probe, FECS-adjacent (gsp/firmware boundary)
- `nv/vfio_compute` + full NvDevice orchestration
- `pcie.rs` GpuTarget adapter

**Phase D** (post-C): wire local dispatch — stop forwarding to coralReef's
`compute.dispatch.execute`. This is the final cutover to sovereign compute.

**For toadStool team**: Phase C batches 1-4 are a major milestone.
Remaining integration (VFIO channels, NvDevice) and Phase D are the final
items before `toadstool.validate` can be wired. Pass 12 scope is narrower
than before your push.

**For everyone else**: toadStool Phase C does NOT block Pass 11. Start
your shadow runs now. The remaining toadStool work blocks Pass 14
(`toadstool.validate` only — `list_workloads` is already live).

---

## Sentinel Escalation Model

This pass follows the ecosystem's sentinel model:

- **Downstream surfaces the gap** — springs discover composition failures
- **Upstream owns the fix** — primal teams resolve at the source
- **primalSpring validates closure** — gate tests confirm correct composition
- **Escalation rule**: upstream issues are always higher priority than
  downstream. A primal regression cascades to all 8 springs; a spring
  gap affects only that spring. Primals are sentinels — most exposed to
  the glacial shift, least composed, first to feel schema pressure.

Pass 11 is L4 absorption work (no upstream issues). Pass 12 escalates
the three sentinel items that block downstream chains.

---

## References

| Topic | Location |
|-------|----------|
| Interstadial exit criteria + pass schedule | `infra/wateringHole/INTERSTADIAL_EXIT_CRITERIA.md` |
| Phase 32 atomic model handoff | `infra/wateringHole/handoffs/PRIMALSPRING_PHASE32_ATOMIC_EVOLUTION_MAY12_2026.md` |
| Compute trio evolution (toadStool contracts) | `primalSpring/docs/COMPUTE_TRIO_EVOLUTION.md` |
| Downstream pattern guide | `primalSpring/docs/DOWNSTREAM_PATTERN_GUIDE.md` |
| Live Science API (Tier 2 contract) | `primalSpring/docs/LIVE_SCIENCE_API.md` |
| Temporal ecosystem review | `primalSpring/docs/TEMPORAL_ECOSYSTEM_REVIEW_MAY12_2026.md` |
| Ecosystem evolution cycle | `infra/wateringHole/ECOSYSTEM_EVOLUTION_CYCLE.md` |
| Cross-spring parity scorecard | `primalSpring/docs/CROSS_SPRING_PARITY_SCORECARD.md` |
