# lithoSpore + Foundation: Deep Debt Resolution & Evolution — May 12, 2026

**From**: lithoSpore/Foundation team
**For**: primalSpring audit (upstream primals teams)
**Date**: 2026-05-12 20:24 EDT

---

## Summary

Comprehensive deep-debt sweep across lithoSpore and Foundation. Resolved all
code quality issues, evolved to modern idiomatic Rust, eliminated unsafe patterns,
created missing Python baselines, and aligned all documentation with current state.

---

## lithoSpore Evolution

### Modules Wired (new this session)

| Module | Spring | Checks | Status |
|--------|--------|--------|--------|
| 6 (breseq) | wetSpring B7 Tenaillon 2016 | 8/8 | **PASS** Tier 2 |
| 7 (anderson) | hotSpring B2 Anderson disorder | 5/5 | **PASS** Tier 2 |

Total: **4/7 modules PASS, 28/28 checks, 3 scaffold SKIP** (awaiting neuralSpring B3/B4/B6).

### Code Quality Debt Resolved

| Issue | Resolution |
|-------|-----------|
| `partial_cmp().unwrap()` panic risk | Evolved to `f64::total_cmp()` — NaN-safe |
| `/etc/hostname` hardcoded | Capability-based discovery: env → file → command |
| `#[allow(clippy::cast_possible_truncation)]` | Proper `u32::try_from()` with bounded fallback |
| Dead CLI parameters (`data_dir`) | Wired to validate data presence |
| `cmd_status` only counted modules 1+2 | Now discovers all 4 live modules dynamically |
| Placeholder DOIs (`XXXXX`) | Cleared to empty with explicit TBD notes |

### Final Quality Metrics

- **Zero** clippy warnings
- **Zero** `unsafe` code
- **Zero** `#[allow]` in production
- **Zero** `TODO`/`FIXME` in Rust (only in scaffold Python awaiting upstream)
- **27+** unit tests
- **CI** wired (clippy, test, integration)

---

## Foundation Evolution

### Provenance Trio Compliance

All **20/20** workload TOMLs now declare `[provenance]` block with
`chain = "rhizoCrypt"`, `attestation = "sweetGrass"`, `spine = "loamSpine"`,
`requires_trio = true`. DATA_INTEGRITY_CONTRACT compliant.

### Capability-Based Discovery (was hardcoded)

| Was | Now |
|-----|-----|
| Hardcoded ports (9100, 9200, etc.) | `discover_port()`: env → XDG socket `capability.resolve` → default |
| `127.0.0.1` literals | `$PRIMAL_HOST` env var (runtime configurable) |
| `/usr/bin/bash` | `/usr/bin/env bash` |
| `$HOME/Development/ecoPrimals/springs` | `$ECOPRIMALS_ROOT` relative discovery |

### barraCuda CPU Parity Baselines (NEW)

Created `benchmarks/barracuda_cpu_parity/` with scipy/numpy reference implementations:

| Baseline | Validates | Result |
|----------|-----------|--------|
| `stats_variance.py` | Welford/two-pass vs numpy VarianceF64 | 6/6 PASS |
| `md_velocity_verlet.py` | Sarkas/LAMMPS OCP Yukawa integration | 3/3 PASS |
| `spectral_eigenvalues.py` | Anderson tridiagonal eigensolver + Lyapunov | 5/5 PASS |

These are the **first Python CPU baselines** for validating barraCuda Rust numerical parity.
The Kokkos/LAMMPS parity gap remains documented-intent (no automated cross-execution).

### Thread 4 + 7 Workloads

- **Thread 4 (enviro)**: QS validation (7 targets) + lithoSpore Module 6 integration
- **Thread 7 (anderson)**: 22-target math validation + lithoSpore Module 7 integration

### Documentation Cleanup

- `workloads/README.md`: Updated structure, added threads 4/7, corrected dispatch
- `specs/EVOLUTION_GAPS.md`: Fixed 4 dead links (pointed to projectNUCLEUS files)
- Dead `$HOME/Development` paths removed from 3 workload TOMLs

---

## Gaps for Upstream Primal Teams

### barraCuda

- **MathOp::Max/Min** still uses CPU fallback (pending GPU kernel)
- **NN surface** partially implemented
- **No automated Kokkos/LAMMPS cross-execution** — parity is Rust-internal + documented
- Python baselines now exist in Foundation for parity assertion

### plasmidBin

- **songbird** and **coralreef** release assets not published yet (checksums.toml updated)
- Automation pipeline hardened (fail-closed on partial harvest)

### Paper Queue (neuralSpring critical path for lithoSpore)

| Paper | Needed for | Status |
|-------|-----------|--------|
| neuralSpring B3 | Module 3 (alleles) | QUEUED |
| neuralSpring B4 | Module 4 (citrate) | QUEUED |
| neuralSpring B6 | Module 5 (biobricks) | QUEUED |
| hotSpring B9 | Module 7 DFE extension | QUEUED |
| healthSpring E2/E4 | Future modules | QUEUED |

### Foundation Data Sources

- **165 dataset manifests** in `data/sources/*.toml` have `blake3 = ""` (intent recorded, data not fetched)
- Sovereign fetch pipeline exists (`fetch_sources.sh`) but most threads lack NCBI accession pinning
- **~30 validation targets** remain `validated = false` (awaiting spring-side data)

---

## Archival Note

All stale docs updated in-place (fossil record preserved via git history).
No files deleted — ecosystem policy is to evolve, not remove. Dead links
converted to plain-text references with repo location noted.
