# barraCuda: Sprint 72+73 — Cross-Spring Shader & Math Absorption

**Date:** May 20, 2026
**From:** barraCuda team
**To:** primalSpring (coordination), all springs
**Priority:** INFORMATIONAL — upstream evolution
**Context:** Universal shader/math absorption from ludoSpring, airSpring, healthSpring, groundSpring

---

## Summary

Cross-spring audit of all 8 springs identified shader/math patterns that barraCuda
could absorb and universalize. Two sprints executed back-to-back:

**Sprint 72**: 4 spatial compute WGSL shaders absorbed from ludoSpring + 3 ecology
IPC methods wired from existing library.

**Sprint 73**: 9 IPC methods absorbed from airSpring (regression, gamma/SPI),
healthSpring (signal processing), and groundSpring (rarefaction).

**Net result**: 75 → 87 IPC methods. New `signal.*` namespace. New `spatial/` shader
category. ludoSpring registered in provenance.

---

## Sprint 72 — Spatial Compute + Diversity IPC

### New WGSL shaders (`shaders/spatial/`)

| Shader | Origin | Universal pattern |
|--------|--------|-------------------|
| `bfs_wavefront_2d.wgsl` | ludoSpring V74 | GPU BFS expansion — pathfinding, flood-fill, influence maps |
| `dda_raycast_2d.wgsl` | ludoSpring V74 | Batch DDA raycasting — visibility, LiDAR sim |
| `fog_of_war_2d.wgsl` | ludoSpring V74 | Progressive tile visibility revelation |
| `tile_lighting_2d.wgsl` | ludoSpring V74 | Multi-source inverse-square lighting |

### New IPC methods

| Method | Library existed | Wire gap resolved |
|--------|----------------|-------------------|
| `stats.simpson` | `barracuda::stats::simpson` | ✅ |
| `stats.bray_curtis` | `barracuda::stats::bray_curtis` | ✅ |
| `stats.hill` | `barracuda::stats::hill` | ✅ |

### Provenance

- `SpringDomain::LUDO_SPRING` added to types
- `ShaderCategory::SpatialCompute` added
- 4 registry entries + evolution timeline event

---

## Sprint 73 — Regression + Signal + Ecology + Gamma

### From airSpring (sensor correction + drought indices)

| Method | Pattern | Notes |
|--------|---------|-------|
| `stats.fit_quadratic` | 3×3 normal equations (Cramer) | Extends `stats.fit_linear` |
| `stats.fit_exponential` | Log-linearized LS | For calibration curves |
| `stats.fit_logarithmic` | Linearized LS | For sensor drift |
| `stats.gamma_fit` | Thom (1958) MLE | Building block for SPI drought index |
| `stats.gamma_cdf` | Regularized incomplete gamma | Maps to `special::regularized_gamma_p` |

### From healthSpring (Pan-Tompkins ECG pipeline)

| Method | Pattern | Notes |
|--------|---------|-------|
| `signal.detect_peaks` | Local maxima + distance/height/prominence | Uses `ops::peak_detect_f64` |
| `signal.bandpass` | FFT zeroing outside [low, high] Hz | CPU frequency-domain filter |
| `signal.derivative` | 5-point Pan-Tompkins FIR | `(-x[i-2] - 2x[i-1] + 2x[i+1] + x[i+2]) / 8` |

### From groundSpring (ecology)

| Method | Pattern | Notes |
|--------|---------|-------|
| `stats.rarefaction_curve` | Hypergeometric expected richness | Uses `barracuda::stats::rarefaction_curve` |

---

## Testing

- **36 new tests** (Sprint 72: 13, Sprint 73: 23)
- **143 IPC method tests total** (all passing)
- Clippy clean, zero warnings
- SIGSEGV in GPU-init tests is pre-existing (no GPU on CI)

---

## Doc Hygiene (same commit)

Updated method count to 87 in: `STATUS.md`, `README.md`, `CONTEXT.md`,
`SOVEREIGN_PIPELINE_TRACKER.md`, `PURE_RUST_EVOLUTION.md`, `sporeprint/validation-summary.md`,
`ipc/mod.rs` module docs. Fixed stale `ecoPrimals/` discovery path in showcase scripts
(→ `biomeos/`). Fixed broken Tier 3 nextest filter in `test-tiered.sh`.

---

## For primalSpring audit

- **Zero debt** — all prior audit items remain resolved
- **New namespaces** for stability tier annotation: `signal.*` → `evolving`
- **sporePrint updated** — 87 methods, 22 namespaces
- **ludoSpring provenance** registered — first non-science spring in shader registry
- Upstream teams: `coralReef` and `toadStool` may want to register these spatial shaders
  in their compile/dispatch manifests if springs request GPU dispatch for grid compute

---

## Commits

| SHA | Message |
|-----|---------|
| `67cd0c8e` | Sprint 72: absorb ludoSpring spatial shaders + wire stats IPC gaps |
| `d48ed6a2` | Sprint 73: absorb multi-model regression, signal processing, ecology from springs |
| (pending) | docs: sync method count to 87, fix stale paths and scripts |
