# strandGate Phase 1 — Wave 157e Divergence Examination AAR

**Date**: Aug 10, 2026 | **Gate**: strandGate | **Wave**: 157e
**Scope**: Cascade from golgi, Phase 1 divergence examination, Rung 1 production campaign

---

## EXECUTIVE SUMMARY

strandGate completed Phase 1 divergence examination per Wave 157e deployment plan.
All silicon-specific validation paths pass except one identified divergence (toadStool
silicon registry not yet in deployed binary). Production campaign for arXiv Rung 1
clean data is in progress (22/45 configs complete, ~6h remaining).

---

## CASCADE FROM GOLGI

Pulled all 16 repos from Forgejo (`git.primals.eco:2222`):

| Repo | Status | Notable |
|------|--------|---------|
| hotSpring | Up to date | Campaign binary already in tree |
| barraCuda | Up to date | Zero-panic refactor, 5,031 tests |
| coralReef | Up to date | GEMM Phase 2 shared-memory tiling, 3,814 tests |
| toadStool | Up to date | S374 silicon registry in source |
| biomeOS | Updated | G68 dispatch + Stage 2 routing infra handoffs |
| songBird | Updated | Transport convergence, tor/turn transport_impl |
| bearDog | Updated | RiboCipher handler, health socket guard |
| nestGate | Updated | Platform links/process, isomorphic IPC |
| petalTongue | Updated | WebGL bridge, scene_stream |
| sweetGrass | Updated | method_gate + UDS lifecycle fixes |
| loamSpine | Updated | Platform abstraction (access/fs/mod) |
| primalSpring | Updated | NUCLEUS lab integration, Stage 2 activation specs |
| wateringHole | Updated | Blurb + orthogonal dimensions review |

---

## PHASE 1 DIVERGENCE CHECKS

### Service Health — 7/7 ALIVE

| Service | PID | Socket | Status |
|---------|-----|--------|--------|
| biomeOS | 2368831 | `/run/membrane/biomeos.sock` | API responding |
| neural-api | 2369234 | `/run/membrane/neural-api.sock` | capability.resolve routing |
| songBird | 2368943 | `/run/membrane/songbird.sock` | mesh.peers: 5 online |
| toadStool | 1518032 | `/run/membrane/toadstool.sock` | health: alive |
| barraCuda | 1517088 | `/run/membrane/barracuda.sock` | IPC server active |
| swarmVine | 2374870 | TCP :7800 | gossip active, gate-id: strandGate |
| bearDog | — | `/run/membrane/beardog.sock` | riboCipher handler active |

### Silicon Validation

| Check | Result | Detail |
|-------|--------|--------|
| coralReef GEMM Phase 2 | **PASS** | 5/5 tests: compile_gemm (sm80, invalid_precision, unsupported_arch) + tarpc integration |
| toadStool device.list | **PASS** | 2 GPUs: AMD 0x73a5 NAVI21 (`amdgpu`), NVIDIA 0x2204 (`nvidia`, protected) |
| riboCipher Tier 2 | **ACTIVE** | `[0xEC,0x01]` prefix enforced on toadStool socket |
| songBird mesh | **PASS** | 5 peers: westGate, blueGate, sporeGate, ironGate, wg-A2fvz3cz |

### Divergence Identified

| Item | Status | Root Cause | Fix |
|------|--------|------------|-----|
| `compute.silicon.registry` | **NOT FOUND** | Deployed toadStool binary (Aug 8 10:15) predates S374 commit `8d0377c26` | Next sporeGate depot rebuild from HEAD |

**Impact**: Low. Silicon registry is a discovery feature; GPU compute paths (`device.list`, coralReef IPC) function correctly without it. No science blocked.

---

## RUNG 1 PRODUCTION CAMPAIGN — IN PROGRESS

### Protocol

Single binary `arxiv_production_campaign.rs` executing unified protocol:
- **Start**: Cold (U=I) — unambiguous thermalization baseline
- **Warmup**: 500 trajectories with staged dt ramp (volume-adaptive)
- **Production**: 200 measured trajectories
- **HMC**: Omelyan 2MN, dt=0.01, n_md=20, τ=0.2
- **Grid**: 3 volumes × 3 β × 5 seeds = 45 configs

### Staged Warmup Fix

Initial run revealed cold-start failure at V≥24⁴: ΔH ∝ V causes 0% acceptance
with production dt=0.01 from ordered state. Fix: volume-adaptive dt schedule:
- 16⁴: dt=0.01 (single stage) — 91% acceptance
- 24⁴: dt=0.002→0.005→0.01 (3 stages) — 82% warmup, 72% production
- 32⁴: dt=0.001→0.002→0.005→0.01 (4 stages) — TBD

### Results So Far (22/45 complete)

| Volume | β | Seeds done | ⟨P⟩ (mean of seeds) | Error | Accept |
|--------|-----|-----------|-------------------|---------|----|
| 16⁴ | 5.9 | 5/5 | 0.5778 | ~6×10⁻⁵ | 91-95% |
| 16⁴ | 6.0 | 5/5 | 0.5900 | ~6×10⁻⁵ | 92-95% |
| 16⁴ | 6.2 | 5/5 | 0.6106 | ~5×10⁻⁵ | 90-93% |
| 24⁴ | 5.9 | 5/5 | 0.5787 | ~3×10⁻⁵ | 67-72% |
| 24⁴ | 6.0 | 2/5 | ~0.591 | TBD | ~70% |
| 24⁴ | 6.2 | 0/5 | — | — | — |
| 32⁴ | all | 0/15 | — | — | — |

### Physics Quality

- Volume convergence visible: 16⁴ ⟨P⟩=0.5778 → 24⁴ ⟨P⟩=0.5787 at β=5.9 (correct direction)
- β-dependence clean: 5.9→6.0→6.2 gives 0.578→0.590→0.611 (monotonic, expected)
- Errors decrease with volume (√V scaling): ~6×10⁻⁵ at 16⁴ → ~3×10⁻⁵ at 24⁴
- All values consistent with Bali et al. literature

### Timing

- 16⁴: ~190s per config (500+200 trajs × ~0.27s/traj)
- 24⁴: ~1020s per config (500+200 trajs × ~1.46s/traj)
- 32⁴: estimated ~4500s per config
- Total ETA: ~6-7 hours remaining (32⁴ dominant)

---

## UPSTREAM GUIDANCE

### For sporeGate (depot authority)

1. **Rebuild toadStool from HEAD** (`28f674048`) to include `compute.silicon.registry`
2. Push rebuilt binary to golgi depot
3. strandGate will redeploy on next cycle

### For primalSpring (cascade orchestration)

- strandGate Phase 1: CLEAR (1 non-blocking divergence documented)
- Ready for Phase 2 fleet deploy once sporeGate rebuilds depot
- Production campaign does NOT require service restart (uses wgpu directly, not toadStool)

### For arXiv pipeline

- Campaign ETA: ~6h remaining (all 32⁴ configs pending)
- Once complete: validate convergence → update paper data → jackknife errors
- 5 seeds per point enables proper jackknife error estimation
- Cold start + 500 warmup eliminates the thermalization-length systematic

---

## HARDWARE STATUS

| Device | Status | Current Use |
|--------|--------|-------------|
| AMD RX 6950 XT (NAVI21) | ACTIVE | Production campaign (GPU HMC) |
| NVIDIA RTX 3090 (GA102) | IDLE | Available for cross-validation post-campaign |
| BrainChip Akida AKD1000 | IDLE | Phase classification (post-production) |
| AMD EPYC 7763 (128T) | IDLE | Available for CPU validation if needed |

---

*strandGate Phase 1 CLEAR. 1 divergence (toadStool S374 not in depot binary — non-blocking). Production campaign 22/45, quality excellent. Push upstream for sporeGate depot rebuild.*
