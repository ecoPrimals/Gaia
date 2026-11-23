# strandGate — Science Pipeline Status

**Date**: Aug 17, 2026 | **Wave**: 157k | **From**: strandGate  
**To**: overwatch, sporePrint, upstream primals teams

---

## Current State

### Production Data: 45 configs BANKED

| Volume | β=5.90 | β=6.00 | β=6.20 | GPU |
|--------|--------|--------|--------|-----|
| 16⁴ | 5 seeds | 5 seeds | 5 seeds | AMD |
| 24⁴ | 5 seeds | 5 seeds | 5 seeds | AMD |
| 32⁴ | 5 seeds (AMD) | 5 seeds (NV) | 5 seeds (AMD+NV) | Mixed |

**Protocol**: Omelyan 2MN, hot start ε=3.0, 500 warmup, 200 production.  
**Cross-GPU**: AMD/NVIDIA agree within 0.19% at β=6.20 32⁴.

### Silicon Activation: 7/8 unit classes lit

Both GPUs active. Dark silicon explored: ROPs, RT cores, rasterizer, depth buffer, video encoder, mesh shaders.

### Known Issues

1. **Protocol mismatch**: 16⁴/24⁴ at dt=0.01 vs 32⁴ at dt=0.0025. Need unified protocol.
2. **Thermalization**: 32⁴ values systematically low (0.007 below literature). 500 warmup may be insufficient from hot start.
3. **One campaign still running**: NVIDIA β=5.90 32⁴ (ETA ~20h from launch).

---

## Upstream Needs

| # | Need | Owner | Priority |
|---|------|-------|----------|
| 1 | Configurable warmup count in GpuHmcConfig | barraCuda | P1 |
| 2 | Plaquette time-series export for autocorrelation analysis | barraCuda | P1 |
| 3 | Tensor Core PTX/SASS emission | coralReef (gen3) | P3 |
| 4 | pseudoSpore manifest for 32⁴ data | sporePrint pipeline | P2 |

---

## sporePrint Alignment

- [GPU Compute Live](https://sporeprint.primals.eco/lab/gpu-compute-live/) — shows SU(2) validation (Rung 1)
- [arXiv Draft](https://sporeprint.primals.eco/pseudospore/hotspring-qcd-sun-paper/) — paper status: 41/42 science-complete

Current production (SU(3) 32⁴, 45 configs) is **Rung 2** material — extends beyond what's published on sporePrint. sporePrint team is aligning site content.

---

## Next Actions (strandGate)

1. Unified protocol run: 16⁴/24⁴/32⁴ all at dt=0.0025, n_md=40, hot start ε=3.0, 2000 warmup
2. Autocorrelation analysis on existing data
3. Wire VideoArchiver into production campaigns
4. Push updated analysis to pseudoSpore pipeline when protocol is unified

---

## Commits Since Last Handoff (Aug 10)

```
d51adde data: arXiv analysis report — 45 configs, 9 grid points
efe7a9f docs: separate wired pipelines from demonstrated results
e31a512 feat: AMD full silicon activation — dark silicon exploration binaries
ddeab1b feat: validate_sovereign_compile Level 5 — coralReef SPIR-V emission tests
9feef8a feat: activate streaming encoder in NodeAtomicQcd (2.83x speedup)
42dd3a9 feat: NodeAtomicQcd probes FP64 throughput at init
ae464df feat: dual-GPU campaign — BARRACUDA_GPU_ADAPTER + CAMPAIGN_BETAS split
f1395a6 fix: 32⁴ campaign — Node-Atomic path replaces broken GPU PRNG pipeline
```

---

*strandGate science pipeline. 45 configs. Cross-GPU validated. Protocol correction needed for literature agreement. Silicon saturated. NVIDIA campaign finishing.*
