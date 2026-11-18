# hotSpring — Deep Debt Sprint + Documentation Evolution (May 16, 2026)

**Spring:** hotSpring v0.6.32
**Date:** May 16, 2026
**Sprint:** Deep Debt Resolution + Doc Evolution (post-Wave 20)
**Tests:** 596 (default) / 1,045 (barracuda-local) — all pass, zero clippy

---

## What Changed

### 1. glowplug_client.rs Refactored (938L → 647 + 221)

The last library file >800L has been split into a directory module:
- `glowplug_client/mod.rs` (647L) — GlowplugClient impl, free functions, tests
- `glowplug_client/types.rs` (221L) — protocol types (GlowplugDispatchOptions,
  GlowplugDeviceSummary, GlowplugDeviceDetail, GlowplugError, CaptureTrainingResult,
  WarmCatchResult, SovereignBootResult, BootStepResult)

**Zero library files >800L remain.** Highest: `gpu_rhmc.rs` (796L).

### 2. Idiomatic Rust Upgrade

- `#[allow(deprecated)]` upgraded to `#[expect(deprecated, reason = "...")]` in
  `compute_dispatch/mod.rs` for Rust 1.81+ lint expectations.

### 3. Full Deep Debt Audit Re-confirmed

| Dimension | Status |
|-----------|--------|
| TODO/FIXME/HACK | Zero in all library code |
| `unsafe` | 9 blocks in `bar0.rs` (MMIO) + 1 CUDA binary — necessary, well-audited |
| Library files >800L | **Zero** |
| External deps | All pure Rust (default). `cudarc` (CUDA FFI) + `wgpu` (Vulkan) feature-gated |
| Hardcoded paths | `/run/toadstool` has env-var fallbacks (`BIOMEOS_SOCKET_DIR`, `XDG_RUNTIME_DIR`) |
| Mock leakage | `NpuSimulator` is intentional cross-substrate math, not test leak |
| `.unwrap()` in lib | `#![deny(clippy::unwrap_used)]` — zero |
| `Box<dyn>` hot paths | Zero |

### 4. Documentation Normalized

- All docs updated to 596/1,045 test counts
- Experiment count normalized to 198 across all surfaces
- Directory tree in README updated for module refactors (niche/, compute_dispatch/, glowplug_client/)
- `hotspring_primal` → `_fossilized/` path corrected in tree
- Notebook upgraded to Level 6 CERTIFIED
- May 13–14 handoffs archived (5 files → `handoffs/archive/`)

### 5. Wave 20 Absorption (prior commit, same day)

- `capabilities_list_response()` canonical builder
- `primal.list` registered (452-method registry sync)
- `nest.commit` signal dispatch adopted
- `s_schema_standard` validation scenario

---

## Signal Adoption Status

| Signal | Status | What it collapses |
|--------|--------|-------------------|
| `primal.announce` | **Adopted** (Wave 17) | `lifecycle.register` + `capability.register` + `method.register` |
| `node.compute` | **Adopted** (Wave 17) | `toadStool.dispatch` + `coralReef.compile` + `barracuda.execute` |
| `tower.publish` | **Adopted** (Wave 17) | `bearDog.sign` → `songBird.announce` → `skunkBat.audit` |
| `nest.commit` | **Adopted** (Wave 20) | `event.append` → `crypto.sign` → `content.put` → `session.commit` → `braid.create` |
| `nest.store` | **Candidate** | DAG dehydration persistence |

---

## Benchmark Status

- **Python CPU parity:** 10 papers wired (6, 8–13, 43–45), `run_all_parity.py` green
- **Kokkos GPU parity:** `bench_md_parity`, `bench_kokkos_complexity` — gap 27× → 3.7×
- **OpenMM/GROMACS/Galaxy:** Not applicable per physics scope

## Paper Queue (~25 remaining)

- Paper 23 (Sulfolobus): queued — wetSpring domain
- Track 5 [25–31]: Folding@home, SETI@home, BOINC scheduling
- Tier 4 [32–42]: WDM/NIF roadmap
- LTEE B9: DFE evolution — queued
- LTEE B1–B7: **COMPLETE** (per `LTEE_PAPER_QUEUE_TRACKER.md`)

## Dataset Examination Queue

| Dataset | Status | Next Step |
|---------|--------|-----------|
| Militzer FPEOS | Partial (binaries exist) | Expand table/case coverage |
| atoMEC | 7/9 checks | Complete remaining 2 checks |
| Dense Plasma Properties DB | Off-repo | Download + wire into `compare_susceptibility_vs_md.py` |
| Zenodo surrogate archive | Optional 6GB | Ingest if fresh-machine reproduction needed |
| Sulfolobus genomes | wetSpring queued | Blocked on Paper 23 + wetSpring pipeline |

---

## What Springs Should Know

1. **Zero >800L library files** across hotSpring — refactoring pattern (extract types to
   separate submodule, keep impl + tests in `mod.rs`) works well for RPC client modules.
2. **`#[expect]` over `#[allow]`** — Rust 1.81+ `#[expect(lint, reason = "...")]` is strictly
   better: the compiler warns if the suppressed lint disappears, catching dead suppressions.
3. **Module refactoring pattern** used consistently:
   - `niche.rs` → `niche/{mod.rs, tables.rs}` (runtime vs static data)
   - `compute_dispatch.rs` → `compute_dispatch/{mod.rs, fused.rs}` (core vs FusedPipeline)
   - `glowplug_client.rs` → `glowplug_client/{mod.rs, types.rs}` (client vs protocol types)
4. **LTEE B2 Anderson reproduction** is COMPLETE in hotSpring (`lithoSpore` module 7).
   groundSpring owns the main B1–B4 reproductions.

---

## Files Changed

- `barracuda/src/glowplug_client.rs` → `barracuda/src/glowplug_client/{mod.rs, types.rs}`
- `barracuda/src/compute_dispatch/mod.rs` (`#[expect]` upgrade)
- `docs/PRIMAL_GAPS.md` (GAP-HS-105)
- `CHANGELOG.md`
- `README.md`, `EXPERIMENT_INDEX.md`, `whitePaper/README.md`, `whitePaper/baseCamp/README.md`
- `experiments/README.md`, `notebooks/01-composition-validation.ipynb`
- `wateringHole/README.md` + 5 handoffs → `archive/`
