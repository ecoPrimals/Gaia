<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->

# hotSpring — Comprehensive Primal Evolution + NUCLEUS Composition Handoff

**Date**: 2026-05-18
**From**: biomeGate (hotSpring hardware + physics team)
**For**: All primals teams, spring teams, primalPSing audit, biomeOS orchestration
**Hardware**: 2× Titan V (GV100) + RTX 5060 (Blackwell). K80 retired (Exp 199).
**Experiments**: 208 total (001-190 archived, 191-208 active)

---

## Executive Summary

hotSpring has evolved from a Python physics validation spring into a fully
sovereign hardware-to-science pipeline composed via NUCLEUS IPC. This handoff
captures everything upstream teams need: what primals we consume, what we
learned, what gaps remain, what NUCLEUS patterns work, and what deployment
patterns the ecosystem should absorb.

**Key numbers**: 208 experiments, 596/1,045 lib tests, 167 binaries, 128 WGSL
shaders, 7 deploy graphs, 15 JSON-RPC methods, 65 validation suites,
183ms warm GPU init, guideStone Level 6 CERTIFIED.

---

## 1. Three-Tier Validation Architecture

hotSpring's evolution traces the path from Python baselines to sovereign
primal composition. This is the pattern other springs should follow:

```
Tier 1: Python baseline     → Peer-reviewed science reproduced in Python
Tier 2: Rust validation     → Same science in pure Rust, checked against Python
Tier 3: NUCLEUS composition → Same science via IPC-composed primals, checked against Rust
```

The `hotspring_unibin serve` binary exposes 13 physics/compute methods as
JSON-RPC. `validate_nucleus_*` binaries (Tower/Node/Nest/FullNucleus) prove
atomic compositions. `validate_primal_proof.sh` runs bare + NUCLEUS modes.

**Pattern for adoption**: Each spring defines `LOCAL_CAPABILITIES` (what it
serves) and `ROUTED_CAPABILITIES` (what it proxies to other primals). The
`by_domain()` discovery replaces hardcoded primal names. `HOTSPRING_NO_NUCLEUS=1`
enables standalone mode where all IPC is skipped.

---

## 2. Primal Usage Map

### Cargo-Linked (compile-time)

| Primal | Crate | Feature Flag | Purpose |
|--------|-------|-------------|---------|
| primalSpring | `primalspring` | always | Composition API, guideStone, tolerances |
| barraCuda | `barracuda` | `barracuda-local` | GPU tensor ops, precision routing |
| toadStool | `akida-driver`, `akida-models` | `npu-hw` | Neuromorphic NPU (optional) |

### IPC-Composed (runtime via NUCLEUS)

| Primal | Domain | Methods Used | Notes |
|--------|--------|-------------|-------|
| **toadStool** | `compute`, `device`, `mmio`, `ember`, `sovereign` | `compute.dispatch.submit`, `sovereign.init`, `sovereign.profile`, `sovereign.warm_status`, `device.*`, `ember.firmware.*` | Primary compute dispatch + hardware lifecycle |
| **coralReef** | `shader` | `shader.compile.wgsl`, `shader.compile.spirv`, `shader.compile.multi`, `shader.compile.gemm` | Compile-then-dispatch pipeline |
| **barraCuda** | `precision` | `precision.route` | Precision tier advisory |
| **BearDog** | `crypto` | `crypto.sign_ed25519`, `crypto.verify_ed25519` | Optional provenance signing |
| **Songbird** | `discovery` | `discovery.find_primals`, `discovery.announce` | Primal discovery |
| **rhizoCrypt** | `dag` | `dag.session.create`, `dag.event.append`, `dag.merkle.root` | DAG provenance |
| **loamSpine** | `spine`, `entry` | `spine.entry.create`, `spine.entry.query` | Ledger entries |
| **sweetGrass** | `braid` | `braid.create`, `braid.seal` | Attribution braids |
| **NestGate** | `storage` | `storage.put`, `storage.get` | Artifact storage |
| **Squirrel** | `inference` | `inference.generate` | ML inference (optional) |
| **petalTongue** | `visualization` | `visualization.render` | Figure rendering (optional) |
| **SkunkBat** | `defense`, `security` | `defense.audit`, `security.scan` | Audit logging (optional) |
| **biomeOS** | `orchestration` | `primal.announce`, `primal.list`, `composition.status` | Registration + discovery |

### Degradation Behavior

Every IPC call degrades gracefully. No primal absence panics the science.
Full table in `docs/DEGRADATION_BEHAVIOR.md`. Key pattern:

```rust
match nucleus.call_by_capability("shader", "shader.compile.wgsl", params).await {
    Ok(result) => use_compiled(result),
    Err(_) => fall_back_to_precompiled(),
}
```

Circuit breaker: 3 failures → dead, 30s cooldown, `call_tracked()` lifecycle.

---

## 3. What We Learned (for upstream teams)

### For toadStool

1. **Compile-then-dispatch is the correct pattern**: `compile_and_submit()`
   chains coralReef → toadStool atomically. Legacy `submit_workload()` with
   pre-compiled shaders is deprecated. The two RPCs should stay separate
   (coralReef compiles, toadStool dispatches) but the client should chain them.

2. **Sovereign init needs generous timeouts**: The VFIO pipeline can take
   14s on cold GPUs. IPC timeouts under 30s cause false failures. Recommend
   configurable per-method timeout on the client side.

3. **Falcon state is fragile**: pgraph_reset destroys FECS firmware.
   Pipeline ordering matters. Any future pipeline stage additions should
   document falcon-safety (does this stage survive with FECS running?).

4. **fd store is the keepalive primitive**: systemd FileDescriptorStore
   should be treated as mandatory for all VFIO-holding daemons. The
   `store_anchors()`/`retrieve_anchors()` pattern is proven.

5. **`sovereign.warm_status` is cheap**: O(1ms) via sysfs BAR0 mmap.
   Can be called speculatively for composition graph GPU readiness probes.

### For coralReef

1. **Barrier shaders need explicit membar**: 9 WGSL shaders use
   `workgroupBarrier()`. coralReef's `membar.{cta,gl}` emitter handles
   this, but the mapping isn't documented in the RPC surface. Consider
   returning barrier info in compile response metadata.

2. **SM120 compile + dispatch works**: RTX 5060 Blackwell validated
   (8/8 sovereign roundtrip). Architecture detection needed the
   `0x2900..=0x2FFF => "sm120"` range.

3. **f64 transcendental lowering (SM32+)** is critical for lattice QCD.
   Without it, double-precision physics silently produces garbage.

### For barraCuda

1. **`PrecisionTier` and `PhysicsDomain` should be canonical upstream**:
   hotSpring replaced its local 4-tier/12-variant enums with barraCuda's
   15-tier/15-variant versions. Other springs should do the same.

2. **TensorSession adoption is ready**: Sprint 66 shipped `sub`/`negate`,
   completing leapfrog momentum-update primitives. HMC trajectory is the
   natural first TensorSession consumer.

3. **BTSP encryption works**: Sprint 51-53 session crypto validated in
   hotSpring. No issues observed.

### For primalSpring

1. **`by_domain()` discovery is the correct default**: All named accessors
   deprecated. `niche::DEPENDENCIES` is single source of truth for primal
   requirements. `composition.rs` derives everything from that.

2. **Deploy graphs work at scale**: 7 deploy graphs covering QCD, MD,
   plasma, nuclear EOS, spectral, sovereign GPU. `biomeos deploy --graph`
   pattern is validated. proto_nucleate downstream manifest wiring proven.

3. **`CompositionContext` validation API is production-ready**: hotSpring
   uses `validate_parity()`, `validate_liveness()`, `from_live_discovery_with_fallback()`.
   Works cleanly.

4. **Wave 17 signals (`primal.announce`) are the registration path**:
   `lifecycle.register` + `capability.register` replaced by single
   `primal.announce`. Document this as the canonical pattern.

### For biomeOS / neuralAPI

1. **Atomic instantiation works**: Tower + Node + Nest composition validated
   via `validate_nucleus_*` binaries. Each atomic is independently health-
   checkable.

2. **Graph-collapsible signals**: `node.compute`, `tower.publish`,
   `nest.commit` are the Wave 17 neural API tier signals. hotSpring
   validates that these can be composed into deploy graph steps.

3. **`NEURAL_API_SOCKET` env var**: hotSpring resolves neural API socket
   via `resolve_neural_api_socket()` in `niche/mod.rs`. Standard env var
   for all springs to use.

### For BearDog / Songbird

1. **Ionic GPU lease blocked upstream** (GAP-HS-005): `crypto.sign_contract`
   and ionic propose/accept/seal not implemented. Blocks cross-family
   metallic fleet pooling. This is the main ecosystem-wide gap.

---

## 4. Sovereign Compute: What We Proved

### Timeline

| Date | Milestone | Exp |
|------|----------|-----|
| Mar 2026 | WGSL→SM70 SASS→DRM dispatch (5/5 E2E) | 164 |
| Apr 2026 | SovereignInit 8-stage pipeline replaces nouveau | 165 |
| May 14 | Dual Titan V installed (K80 slot) | 205 |
| May 17 | Falcon ACR DMA boot solved | 206 |
| May 17 | Boot state abstraction + twin-card profiling | 207 |
| May 18 | **183ms warm pipeline, falcon preservation, fd store** | 208 |

### Hardware Line (codified)

Cold boot = power-on reset = boot ROM trains HBM2. Software cannot train
HBM2 — only the boot ROM can. This is the same wall NVIDIA's proprietary
driver faces. Acceptable hardware constraint, not software limitation.

### Pipeline Architecture

```
identity_probe → pmc_enable → [pgraph_reset] → cg_sweep → pri_recovery
→ boot_state_probe → [memory_training] → [falcon_boot] → [gr_init] → verify
```

Bracketed stages are conditionally skipped:
- `pgraph_reset` skipped when falcon detected WarmRunning (PC >= 0x40)
- `memory_training` skipped when warm (PRAMIN sentinel alive)
- `falcon_boot` skipped when falcon already running
- `gr_init` skipped when PGRAPH already initialized

**Result**: 183ms warm, 200ms cold-early-exit, 3.9s warm-without-falcon-fix.

### Cross-Platform Testing Needed

| Architecture | Status | Testing Guide |
|-------------|--------|--------------|
| **Volta (GV100)** | ✅ Proven | Baseline — 183ms warm |
| **Blackwell (GB206)** | ✅ DRM | 8/8 roundtrip, needs VFIO validation |
| **Kepler (GK210)** | Historical | K80 retired; PIO boot (no HS security) |
| **Maxwell** | Untested | ACR boot expected similar to Volta |
| **Pascal** | Untested | ACR boot expected similar to Volta |
| **Turing** | Untested | GSP-RM transition; check if GSP replaces FECS |
| **Ampere+** | Untested | GSP-RM dominant; falcon warm detection may not apply |
| **AMD Vega/RDNA** | Stub | VegaInit, no falcon equivalent |

---

## 5. Deploy Graph + NUCLEUS Composition Patterns

### 7 Deploy Graphs

| Graph | Primals | Domain |
|-------|---------|--------|
| `hotspring_qcd_deploy` | 10 (full NUCLEUS + skunkBat) | Lattice QCD |
| `hotspring_md_deploy` | Tower + Node + barraCuda | Molecular dynamics |
| `hotspring_plasma_deploy` | Tower + Node + coralReef | Plasma physics |
| `hotspring_plasma_md_deploy` | Full Tower + barraCuda + coralReef | Plasma MD |
| `hotspring_nuclear_eos_deploy` | Tower + Node + Nest + skunkBat | Nuclear EOS |
| `hotspring_spectral_deploy` | Tower + barraCuda + skunkBat | Anderson/Hofstadter |
| `hotspring_sovereign_gpu_deploy` | Full NUCLEUS + skunkBat | Sovereign GPU |

### Deployment Pattern

```bash
biomeos deploy --graph graphs/hotspring_qcd_deploy.toml
```

Graphs reference `proto_nucleate` from primalSpring downstream manifest.
Wave ordering handled by topological sort. Binary spawning from plasmidBin.

### Atomic Instantiation Pattern

```
Tower = toadStool + coralReef + barraCuda       (compute trio)
Node  = rhizoCrypt + loamSpine + sweetGrass     (provenance trio)
Nest  = NestGate + BearDog + Songbird           (storage + security + discovery)
```

Each atomic is independently health-checkable. Composition validators
exercise Tower → Node → Nest → FullNucleus in sequence, with skip-aware
exit codes (0 = pass, 1 = fail, 2 = all skipped).

---

## 6. Active Gaps for Upstream

| ID | Description | Owner | Priority |
|----|-------------|-------|----------|
| GAP-HS-001 | Squirrel E2E (wait for neuralSpring WGSL ML) | Squirrel | Low |
| GAP-HS-005 | Ionic GPU lease (BearDog/Songbird) | BearDog | Medium |
| GAP-HS-027 | TensorSession adoption (barraCuda Sprint 66 ready) | hotSpring | Low |
| — | Cross-generation falcon validation (Maxwell/Pascal/Turing) | toadStool + hotSpring | High |
| — | AMD Vega/RDNA warm detection equivalent | toadStool | Medium |
| — | GSP-RM interaction on Turing+ | toadStool | Medium |
| — | Long-running warm endurance test (48h+) | hotSpring | Next |
| — | pmc_enable optimization (73ms, 40% of warm pipeline) | hotSpring | Next |

---

## 7. For Spring Teams

### Adopting the hotSpring Pattern

1. Define `LOCAL_CAPABILITIES` + `ROUTED_CAPABILITIES` in a `niche` module
2. Create `capability_registry.toml` with bidirectional sync test
3. Implement `by_domain()` discovery (not hardcoded primal names)
4. Add `HOTSPRING_NO_NUCLEUS=1` standalone mode
5. Write `validate_nucleus_*` composition validators
6. Create deploy graphs in `graphs/`
7. Document degradation behavior per capability

### Three-Tier Validation

Each spring should be able to prove:
- **Tier 1**: Science is correct (vs published papers)
- **Tier 2**: Rust implementation matches Python baselines
- **Tier 3**: IPC-composed NUCLEUS matches direct Rust

guideStone certification validates all three tiers. Level 6 requires
passing all three with documented tolerances.

---

## 8. Artifacts

| Artifact | Location |
|----------|----------|
| Root docs | `hotSpring/README.md`, `CHANGELOG.md`, `EXPERIMENT_INDEX.md` |
| Primal gaps | `hotSpring/docs/PRIMAL_GAPS.md` |
| Degradation | `hotSpring/docs/DEGRADATION_BEHAVIOR.md` |
| IPC mapping | `hotSpring/docs/PRIMAL_PROOF_IPC_MAPPING.md` |
| Cross-tier parity | `hotSpring/docs/CROSS_TIER_PARITY.md` |
| Deploy graphs | `hotSpring/graphs/*.toml` |
| Capability registry | `hotSpring/barracuda/config/capability_registry.toml` |
| Warm keepalive whitepaper | `infra/whitePaper/gen4/architecture/SOVEREIGN_WARM_KEEPALIVE.md` |
| baseCamp paper 14 | `infra/whitePaper/gen3/baseCamp/14_sovereign_compute_hardware.md` |
| Exp 208 write-up | `hotSpring/experiments/208_REBOOT_EFFICIENT_SOVEREIGN_EVOLUTION.md` |

---

## 9. Debris / Archive Notes

- **K80 hardware retired** (Exp 199 fire). K80 experiment journals preserved
  as fossil record. `scripts/boot/k80-wake-and-run.sh` is historical.
- **`scripts/archive/`** contains superseded shell/Python workflows. All
  replaced by `toadstool device` CLI. Kept as fossil record per policy.
- **Zero TODO/FIXME/HACK** in production code. Zero `.bak/.old/.tmp` files.
- **`docs/PRIMAL_GAPS.md` header date** (April 10) is behind content
  (May 17 resolutions). Header updated to May 18.

---

*208 experiments. Python → Rust → NUCLEUS. Consumer GPUs reproduce HPC
physics at paper parity. 183ms sovereign GPU init. The primals disappear
into the product.*
