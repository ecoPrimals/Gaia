# AAR: NPU Silicon Continuum — Preprint Integration & Upstream Handoff

**Date**: 2026-08-07  
**Gate**: strandGate  
**Wave**: 156 (post-NPU integration)  
**Scope**: Silicon substrate architecture → preprint expansion → upstream handoff for live system wiring

---

## 1. What Was Done

### Preprint Expansion (LATTICE_QCD_CONSUMER_GPU_ARXIV.md)

| Change | Section | Content |
|---|---|---|
| **Section 4.7 rewrite** | §4.7 Neuromorphic Co-Processing | Replaced 97%/4-feature/60-config with: 69 configs (SU(2)+SU(3)), 11-feature extraction (position + DFT momentum-space), 100% accuracy, MCC=1.000. ESN architecture + pipeline diagram. |
| **Section 2.9 added** | §2.9 Silicon Substrate Architecture | Three-substrate model (CPU/GPU/NPU) with precision/role/hardware table. Framing: hardware scheduling observation, not novel algorithm. |
| **Appendix A updated** | Hardware Profile | AKD1000 added (80 NPs, 10 MB SRAM, PCIe x4, <2W TDP) |
| **Section 7 expanded** | Conclusion | Silicon-agnostic scientific computing paragraph. Output independent of substrate — only cost differs. |
| **Section 7.1 expanded** | Precision Continuum | Precision-to-substrate mapping table (int4→NPU, DF64→GPU, f64→CPU, DF128→CPU emulated). 8-bit suffices for classification = natural resolution. |

### LaTeX Sync (lattice_qcd_consumer_gpu.tex)

| Change | Location |
|---|---|
| NPU in hardware table | `\section{Hardware Profile}` |
| Silicon substrate subsection | After `\subsection{Provenance}` |
| Heterogeneous compute paragraph | `\section{Conclusion}` |

### Murillo Claims Audit

Created `infra/whitePaper/attsi/non-anon/contact/murillo/CLAIMS_VS_REALITY_AUG07_2026.md`:
- Systematic comparison of prior email claims vs current evidence
- NPU: partially validated (simulator pipeline works, hardware path pending workspace dep)
- MILC interop: stronger than claimed (bidirectional validated)
- Sarkas reproduction: unverified (stretch goal)
- Modern pitch reframed around silicon continuum + precision routing

### NPU MetalForge Validation

Ran `sun_npu_metalforge` with `barracuda-local` feature:
- 69 configs classified (36 SU(2) + 33 SU(3))
- 11-feature extraction: plaquette, Polyakov (re/im/abs), W(1,1), W(2,1), χ(2,2), volume, DFT[0:3]
- ESN classifier: 100% accuracy, F1=1.000, MCC=1.000
- Baseline (3 features): 97.2% — demonstrates DFT modes as the discriminating signal

---

## 2. Current Rubric Status

| Category | Score |
|---|---|
| Bazavov (B1–B12) | 12/12 |
| Chuna (C1–C10) | 9/10 (C5 = upstream naga bug, nice-to-have) |
| Murillo (M1–M10) | 10/10 |
| Cross-Reviewer (X1–X10) | 10/10 |
| **Total** | **41/42 (98%)** |

---

## 3. Silicon Substrate Summary — For Upstream Teams

The preprint now frames the system as **silicon-agnostic scientific computing**. Each substrate handles what it does best:

```
┌─────────────────────────────────────────────────────────────┐
│                    BLAKE3 Content-Addressed Cache            │
│                    (shared provenance chain)                 │
├───────────────┬──────────────────┬──────────────────────────┤
│   CPU (f64)   │  GPU (DF64/FP32) │     NPU (int8)           │
│               │                  │                          │
│ Thermalize    │ Force compute    │ Phase classify           │
│ Accept/reject │ Plaquette        │ Anomaly detect           │
│ Validation    │ SpMV             │ Online monitoring        │
│               │                  │                          │
│ EPYC 7452     │ RTX 3090         │ AKD1000                  │
│ 128 threads   │ RX 6950 XT       │ 80 NPs, <2W             │
│ ~0.5 TF/s f64 │ ~140 GF DF64    │ ~500k inf/s             │
└───────────────┴──────────────────┴──────────────────────────┘
```

---

## 4. What Upstream Needs to Wire

### For Live Site (sporePrint / lithoSpore / golgi)

| Item | Owner | Status | Action |
|---|---|---|---|
| `primals.eco/pseudospore/hotspring-qcd-sun/` artifact hosting | lithoSpore | URL resolves (HTTP 200) | Populate with: configs, measurements, shaders, provenance |
| `validate.sh` script | hotSpring → sporePrint | Not yet written | Implement BLAKE3 verify + DAG check + Ed25519 signature verify |
| pseudoSpore v1.0.0 freeze + sign | Node Atomic | Pending | Tag, hash, sign with Ed25519 key |
| GitHub mirror (`github.com/ecoPrimals/hotspring`) | golgi → GitHub | Remote configured | Push public subset |
| sporePrint preprint surface (LaTeX → web) | sporePrint | In progress | Wire `lattice_qcd_consumer_gpu.tex` → rendered preprint page |

### For Overwatch Audit

| Item | Description |
|---|---|
| Preprint §4.7 updated | NPU now 100% accuracy, 11 features, honest framing (ESN simulator, not raw hardware) |
| Silicon continuum thesis | "All compute is math on silicon" — architectural insight, not claim of novelty |
| Precision-to-substrate mapping | Formal table connecting bits → hardware → operation type |
| Murillo pitch modernized | Audit doc ready for review before re-engagement |
| MILC validated | Bidirectional roundtrip Δ⟨P⟩ = 3×10⁻⁹ |

### For NUCLEUS / petalTongue Local Execution

| Capability | How to Use Locally |
|---|---|
| Thermalization campaigns | `cargo run --release --features barracuda-local --bin arxiv_thermalize_sun` |
| Observable measurement | `cargo run --release --features barracuda-local --bin arxiv_measure_battery` |
| NPU phase classification | `cargo run --release --features barracuda-local --bin sun_npu_metalforge` |
| MILC import/export | `cargo run --release --features barracuda-local --bin milc_validation_loop` |
| GPU Lanczos benchmark | `cargo run --release --features barracuda-local --bin bench_lanczos_scaling` |
| petalTongue visualization | Grammar-of-Graphics pipeline for observable time series |

---

## 5. Open Experimental Tracks (local execution continues)

| Track | Status | Next Step |
|---|---|---|
| SU(4) 32⁴ thermalization | Running (CPU-bound, days remaining) | Monitor via process check |
| SU(3) 32⁴ thermalization | Running | Let complete, then measure |
| NPU hardware timing | Blocked on `akida-chip` workspace dep in `toadStool` | Resolve workspace member, then VFIO → real latency |
| DF64 folding experiments | Design complete | DF32 (f16-pair) MD integrator prototype |
| Two-particle Anderson (Kachkovskiy) | Stretch | L=100 GPU Lanczos after spectral review package sent |
| Compensated summation | Shader written (`df64_compensated_sum.wgsl`) | Wire into force/plaquette hot loops |

---

## 6. Handoff Summary

**To upstream (golgi → overwatch → sporePrint → lithoSpore):**
- Preprint markdown + LaTeX updated with silicon continuum framing
- Murillo claims audit ready for review
- NPU validation data (100% accuracy, honest scope)
- MILC interop validated and documented
- All binaries production-ready with `barracuda-local` feature flag

**Upstream absorbs:**
- Wire live site artifact hosting
- Implement `validate.sh` reproducibility script
- Push GitHub mirror for public access
- sporePrint renders preprint from LaTeX source
- Overwatch audits gaps, flags anything for upstream primals teams

**Local continues (NUCLEUS + petalTongue):**
- Long-running thermalizations
- NPU hardware path (once workspace dep resolved)
- Precision folding experiments
- Kachkovskiy spectral package preparation

---

*strandGate AAR — NPU silicon continuum integration complete. Preprint at 41/42. System science-complete for Rung 1. Upstream: wire live site + audit. Local: continue production campaigns + NPU hardware path. Push via cascade for overwatch absorption.*
