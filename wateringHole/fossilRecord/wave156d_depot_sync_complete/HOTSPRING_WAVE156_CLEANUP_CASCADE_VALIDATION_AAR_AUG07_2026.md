# AAR: hotSpring Wave 156 — Cleanup, Cascade, Validation

**Date**: 2026-08-07  
**Gate**: strandGate  
**Wave**: 156 (post-cascade from golgiBody)  
**Scope**: Deprecation cleanup → Ecosystem cascade → QCD revalidation + profiling

---

## 1. Deprecation Cleanup

### Fully Fossilized (removed from build)

| Component | LOC | Destination |
|---|---|---|
| `low_level/` module (bar0.rs, falcon.rs, mod.rs) | 1,134 | `archive/_fossilized/low_level_legacy/` |
| 15 sovereign-boot experiments (exp070–exp234) | ~9,500 | `archive/_fossilized/` |
| 32 pre-existing fossilized binaries | ~14,609 | `archive/_fossilized/` |
| **Total removed from active build** | **~25,200** | |

### Marked Deprecated (retained for active consumers)

| Module | Consumers | Migration Target |
|---|---|---|
| `ember_types.rs` | `glowplug_client`, `s_cold_boot_sentinel` | Absorb into `glowplug_client/types.rs` |
| `fleet_client.rs` | `bin_helpers/sovereignty/connect.rs` | toadStool fleet RPCs |
| `fleet_ember.rs` | `ipc/mod.rs` re-exports | toadStool dispatch RPCs |

All three carry `#[deprecated(since = "0.6.32")]`.

### Cargo.toml

- `low-level` feature: commented out
- 15 `[[bin]]` entries: commented with `# FOSSILIZED (v0.6.32)` markers

---

## 2. Ecosystem Cascade

**Command**: `membrane temporal.cascade --from golgiBody`

| Result | Count |
|---|---|
| Synced (parity or pulled) | 23 |
| Failed (diverge) | 1 (`wateringHole` — local-ahead, expected) |
| Total repos | 24 |

**Repos with new upstream code**:
- toadStool (pulled)
- coralReef (pulled — build fails upstream, type inference in ecosystem/mod.rs)
- squirrel (pulled)
- petalTongue (pulled)
- skunkBat (pulled)

### Musl Rebuild + Deploy

| Primal | Status | Size |
|---|---|---|
| toadStool | ✅ built + deployed | 14.1 MB |
| squirrel | ✅ built + deployed | 11.5 MB |
| petalTongue | ✅ built + deployed | 41.7 MB |
| skunkBat | ✅ built + deployed | 3.5 MB |
| coralReef | ❌ upstream build failure | — |

**coralReef failure**: 11 type inference errors in `crates/coralreef-core/src/ecosystem/mod.rs` (async stream closures). Upstream fix needed — not caused by our changes.

---

## 3. QCD Revalidation

### Precision Tier Matrix — All PASS

Both GPUs (RTX 3090 + RX 6950 XT) pass all precision tiers:
- int2, int4, int8, u32, i32
- fp32 (FMA, π², Kahan sum, wg reduce)
- df64 (add, π², wg reduce)
- fp64 (π², Kahan sum, wg reduce)
- df128 (f64-pair add, π²)

Notable: AMD DF64 pi*pi achieves **3.6e-16 relative error** (near machine epsilon for pair arithmetic) — significantly better than NVIDIA's 1.15e-8. This confirms RDNA2's FMA path produces tighter DF64 than Ampere for transcendental accumulation.

### Production QCD Validation — 10/10 PASS

| Check | Result |
|---|---|
| 4^4 plaquette monotonic with β | ✓ |
| 4^4 HMC acceptance > 30% all β | ✓ |
| 4^4 plaq β=6.0 vs Bali (0.594) | ✓ (0.5969, 0.50% err) |
| 4^4 confined ⟨\|L\|⟩ (β≤5.0) < 0.4 | ✓ (0.275) |
| Polyakov transition (deconfined > confined) | ✓ |
| 8^4 vs 4^4 scaling at β=6.0 | ✓ |
| 8^4 HMC acceptance > 30% all β | ✓ |
| 8^4 plaquette monotonic with β | ✓ |
| Determinism (bitwise identical rerun) | ✓ (diff=0.0) |
| Susceptibility peak in transition region | ✓ (peak at β=5.80) |

### HMC GPU Scaling (RTX 3090, DF64, Omelyan)

| Volume | CPU (ms/traj) | GPU (ms/traj) | Speedup |
|---|---|---|---|
| 4^4 (256) | 92.3 | 9.4 | 9.9× |
| 8^4 (4,096) | 1,514 | 28.4 | 53.3× |
| 8³×4 (2,048) | 771 | 14.3 | 53.8× |
| 16³×4 (16,384) | 6,182 | 153 | 40.4× |
| 16³×8 (32,768) | 12,365 | 313 | 39.5× |
| 16^4 (65,536) | 24,726 | 617 | 40.1× |

**Peak GPU throughput**: 53× at 8^4 (saturated ALU utilization). Large volumes plateau at ~40× — memory bandwidth limited at 16^4+.

---

## 4. Profiling — Optimization Opportunities

### Kernel-Level Analysis (bench_qcd_silicon)

**RTX 3090 peak throughput at 8^4** (sweet spot for GPU occupancy):

| Kernel | Sites/s | GFLOP/s | Bottleneck |
|---|---|---|---|
| gauge force | 130M | 112 | ALU-bound (staple matmuls) |
| plaquette | 95M | 123 | ALU-bound (6 plane matmuls) |
| SU3 matmul | 181M | 39 | **Tensor core candidate** |
| link update (Cayley) | 127M | 51 | ALU + transcendental |
| mom update | 183M | 13 | Memory-bound |
| Dirac stencil | 126M | 36 | Balanced (stencil + matvec) |
| pf force | 133M | 133 | ALU-bound (expensive) |
| PRNG heat bath | 149M | 54 | **TMU LUT candidate** |
| DF64 force | 113M | 389 | DF64 ALU — excellent |
| DF64 plaquette | 142M | 735 | DF64 ALU — peak utilization |

### Identified Optimization Paths

1. **SU3 matmul → Tensor Core (MMA-shaped)**: At 181M sites/s but only 39 GFLOP/s — massive headroom via WMMA/cooperative matrix operations on 3×3 complex. This is the single highest-impact optimization target.

2. **PRNG heat bath → TMU LUT**: Transcendental-heavy kernel (Box-Muller log/cos) — could leverage texture memory unit lookup tables for faster throughput. 149M sites/s at 54 GFLOP/s suggests ALU bottleneck on transcendentals.

3. **Memory-bound kernels (mom update)**: At 183M sites/s but only 13 GFLOP/s / 39 GB/s — well below theoretical bandwidth. Coalescing optimization or shared-memory staging could help.

4. **AMD DF64 advantage**: AMD achieves 1:16 DF64-to-FP32 throughput ratio (vs NVIDIA ~1:32). For precision-sensitive reductions, preferring AMD for DF64 paths is a scheduling opportunity.

5. **Volume scaling plateau at 40×**: The drop from 53× (8^4) to 40× (16^4) indicates either L2 cache pressure or workgroup scheduling inefficiency at large volumes. Investigate tiled dispatch patterns.

---

## 5. Gaps for Upstream Primal Teams

### barraCuda (GPU compute substrate)

- [ ] Absorb `PrecisionEval` empirical GPU probing
- [ ] Absorb `HardwareCalibration` clock/thermal measurement
- [ ] Upstream `df64_compensated_sum.wgsl` into `shaders/math/`
- [ ] Investigate cooperative matrix (tensor core) path for SU3 matmul
- [ ] TMU LUT path for Box-Muller transcendentals

### toadStool (device fleet management)

- [ ] Provide `fleet.discover` RPC equivalent for bin_helpers/sovereignty migration
- [ ] Fix coralReef ecosystem/mod.rs type inference (upstream build failure)

### coralReef (mesh orchestration)

- [ ] Fix 11 type inference errors in `crates/coralreef-core/src/ecosystem/mod.rs`
- [ ] Requires explicit type annotations on async stream closures

---

## 6. Status

| Item | Status |
|---|---|
| Deprecated code fossilized | ✅ |
| Ecosystem cascade (23/24) | ✅ |
| Musl builds redeployed (4/5) | ✅ |
| Precision matrix validation | ✅ ALL PASS |
| Production QCD validation | ✅ 10/10 PASS |
| HMC GPU scaling benchmark | ✅ 40–53× GPU speedup |
| Kernel-level profiling | ✅ Optimization targets identified |
| coralReef upstream build | ❌ Needs upstream fix |

**Next**: Clean hotSpring docs, debris audit, push via cascade for overwatch review.
