# strandGate — Post-Threshold Node Atomic AAR

**Date**: 2026-08-01
**Wave**: post-155n (Post-Threshold)
**Gate**: strandGate
**Operator**: strandGate/overwatch
**biomeOS**: v4.56.0 (G22 COMPLETE)

---

## Summary

Post-threshold cascade, fresh NUCLEUS restart, and deep exercise of strandGate's Node Atomic workhorse role. GPU HMC benchmark produced first RTX 3090 lattice QCD scaling data. Shader compilation pipeline (coralReef) proven for custom WGSL→PTX kernels including DF64 precision. NUCLEUS IPC matmul scaling profiled. hotSpring composition wiring validated.

---

## Cascade Review

| Source | Deltas |
|--------|--------|
| wateringHole | southGate 22/22 validation AAR, Peptidoglycan DNS fix AAR, westGate real data ingestion (33.79 GB), blueGate Wave 155 close |
| whitePaper | `subGen/WINDOWS_CROSSING.md` — Silicon Deism Tier 1 proven on blueGate |
| biomeOS | G22 complete handoff (already deployed) |
| hotSpring | Up to date |
| All primals | Up to date |

**Fleet status (post-threshold)**:
- 5 NUCLEUS gates operational
- 33.79 GB real science data at 100% provenance (westGate)
- Portability proven without WireGuard (southGate 22/22)
- DNS architecture fixed (G29 Phase 1)
- Sub-builder E2E (J12: sporeGate → blueGate → verified)

---

## GPU HMC Benchmark: RTX 3090 Lattice QCD

First production run of `bench_gpu_hmc` on strandGate. Pure SU(2) gauge theory, Omelyan integrator, β=6.0, n_md=10, dt=0.05. DF64 (double-float on FP32 cores) for physics precision.

| Lattice | Volume | CPU ms/traj | GPU ms/traj | Speedup | Accept |
|---------|--------|-------------|-------------|---------|--------|
| 4⁴ | 256 | 93.1 | 9.4 | **9.9×** | 19-20/20 |
| 8⁴ | 4,096 | 1,490.7 | 25.8 | **57.8×** | 20/20 |
| 8³×4 | 2,048 | 750.4 | 14.8 | **50.8×** | 20/20 |
| 16³×4 | 16,384 | 5,978.4 | 150.4 | **39.8×** | 5/5 |
| 16³×8 | 32,768 | 11,969.1 | 316.4 | **37.8×** | 5/5 |
| **16⁴** | **65,536** | **24,007.7** | **625.9** | **38.4×** | 5/5 |
| 32³×4 | 131,072 | 48,292.0 | (dispatch-bound) | — | — |

### Key Findings

1. **Sweet spot: 8⁴ to 16⁴** — GPU achieves 38-58× speedup with sub-second trajectory times
2. **DF64 precision**: Concurrent strategy (DF64 on FP32 cores) — physics validated by plaquette convergence
3. **16⁴ production rate**: 1.6 trajectories/sec (GPU) vs 1 trajectory/24s (CPU)
4. **32³×4 dispatch bottleneck**: CPU-side DF64 shader coordination dominates at V>65K — metalForge optimization target
5. **Acceptance rate**: 100% at all sizes ≥8⁴ (proper thermalization)

### Production Capacity (16⁴ regime)

At 626ms/traj on 16⁴:
- **~5,500 trajectories/hour** (GPU)
- **~138,000 trajectories/day** sustained
- Thermalization (1000 traj) in ~10 minutes
- 10,000-traj production run in ~1.7 hours

---

## coralReef Shader Compilation

| Kernel | Instructions | GPRs | Compile Time | Target | Size |
|--------|-------------|------|--------------|--------|------|
| Gauge update (f32) | 35 | 22 | 148ms | sm_70 PTX | 560 B |
| DF64 leapfrog | 72 | 22 | 290ms | sm_70 PTX | 1,152 B |
| Scale (sm_86) | 23 | — | 135ms | sm_86 PTX | — |

### coralReef Capabilities

- **Targets**: sm_35, sm_70, sm_75, sm_80, sm_86, sm_89, sm_120, gcn5, rdna2, rdna3, rdna4
- **f64 transcendentals**: sin, cos, exp, exp2, log, log2, sqrt, rcp (via composite lowering)
- **Subgroup ops**: supported
- **Atomics**: supported
- **Math ops**: 34 supported

### D8 Issue: GEMM SM Target

coralReef's `shader.compile.gemm` endpoint hardcodes SM70 check and ignores target parameter. RTX 3090 (SM86) supports tf32 tensor core GEMM but can't access it through this endpoint. WGSL compilation with explicit `target: "sm_86"` works correctly.

---

## NUCLEUS IPC Matmul Scaling

10× burst throughput at each matrix size:

| Size | Time (10 matmul) | Rate |
|------|-----------------|------|
| 64×64 | 59ms | 169/sec |
| 128×128 | 61ms | 164/sec |
| 256×256 | 55ms | 182/sec |
| 512×512 | 57ms | 175/sec |
| 1024×1024 | 55ms | 182/sec |
| 2048×2048 | 66ms | 152/sec |
| 4096×4096 | 104ms | 96/sec |

**Observation**: Constant-time (IPC-dominated) up to 2048² at ~170 ops/sec. GPU computation only becomes visible at 4096². The IPC overhead (~5ms per call) is the floor — well below any lattice computation time.

---

## NUCLEUS Stability

| Metric | Before workload | After 40min QCD + compilation |
|--------|----------------|-------------------------------|
| Processes | 13 (1:1) | 13 (1:1) |
| coralReef/skunkBat accumulation | — | **NONE** during this session |
| GPU temp | 65°C | 68°C |
| GPU VRAM | 1.3 GB | 2.1 GB |
| Total RSS | 408 MB | 408 MB |

The P3 coralReef/skunkBat accumulation from earlier today did NOT recur during this clean restart session (45 min uptime). This suggests the accumulation trigger may be related to startup timing or initial health check race conditions rather than a steady-state issue.

---

## Divergences (updated)

| ID | Issue | Severity | Status |
|----|-------|----------|--------|
| D2 | Socket path: `membrane/` vs `biomeos/` | P3 | Symlink workaround. Composition lib needs update |
| D8 | coralReef GEMM endpoint ignores target param | P3 | WGSL compile works. GEMM endpoint hardcoded SM70 |
| D8b | Capability registration WARNs (songBird) | P4 | Cosmetic — biomeOS routes via virtual sockets |
| P3 | coralReef/skunkBat process accumulation | P3 | Intermittent — did not reproduce this session |

---

## hotSpring QCD Readiness: PROVEN

| Component | Status | Evidence |
|-----------|--------|----------|
| GPU HMC (native) | ✓ | 38-58× speedup, production rates validated |
| coralReef shader compilation | ✓ | Custom WGSL→PTX, DF64 kernels, SM86 target |
| barraCuda tensor IPC | ✓ | 96-182 ops/sec, constant up to 2048² |
| Cross-primal provenance | ✓ | DAG session + spine + seal (proven earlier today) |
| hotSpring composition | ✓ | 7/7 caps discovered, event loop operational |
| NUCLEUS stability under load | ✓ | 13 processes maintained through 40min GPU workload |

**strandGate is the Node Atomic workhorse. QCD dynamical programming is operational.**

---

## Next Steps

1. **hotSpring QCD background runs**: Start production 16⁴ sweeps (β scan) using composition script's DAG memoization
2. **metalForge dispatch optimization**: Profile and optimize 32³×4+ GPU dispatch (reduce CPU coordinator overhead)
3. **coralReef GEMM D8**: Fix target param propagation to unlock tensor core GEMM on SM86
4. **G19**: petalTongue live QCD visualization rendering

---

*Post-threshold. Real lattice QCD on sovereign GPU. The hardware speaks physics.*
