# biomeGate Overwatch Sync — Wave 155n

**Date**: Aug 2, 2026
**Gate**: biomeGate (hostname: `biomeGate`)
**Team**: hotSpring (Compute Trio focus)
**WireGuard IP**: 10.13.37.3
**Wave at sync**: 155n

---

## Hardware Profile

| Component | Actual | Blurb (strandGate) |
|-----------|--------|--------------------|
| CPU | AMD Ryzen Threadripper 3970X (32c/64t) | Dual EPYC 7452 (64c) |
| RAM | 128 GB | — |
| GPU (host) | **RTX 5060** (8 GB, SM100, Ada/Blackwell) | RTX 3090 (24 GB) |
| GPU (VFIO) | **Titan V** (12 GB HBM2, SM70, FP64 1:2) | — |
| GPU (VFIO) | **K80 die 0** (12 GB GDDR5, SM37, FP64 1:3) | — |
| GPU (VFIO) | **K80 die 1** (12 GB GDDR5, SM37, FP64 1:3) | — |

**NOTE**: This gate is NOT strandGate. biomeGate is a distinct machine with
different hardware. It appears to be unlisted in wave.toml gate roster.
The blurb's strandGate entry (Dual EPYC + RTX 3090) does not match.

biomeGate has HPC-class FP64 silicon (Titan V 1:2, K80 1:3) — unique in the
fleet for native f64 validation without DF64 emulation.

---

## Phase 0: Connectivity

| Check | Result |
|-------|--------|
| SSH to Forgejo | PASS — authenticated as `biomegate` (key: `biomegate-gate-v1`) |
| HTTPS to Forgejo | PASS — API responds |
| SSH config | Present, correct (port 2222, `id_ed25519_ecoPrimal`) |
| WireGuard | LIVE — 10.13.37.3, golgiBody reachable (41.6 ms) |

---

## Phase 1: Sync

### 1a: Naming Divergences — NONE
No symlinks, no lowercase directories, no `springs/barraCuda` duplicate.

### 1b: Remotes — ALL ON FORGEJO
All 40 repos point at `git.primals.eco` with correct org mapping.
Two repos use SSH (hotSpring, wateringHole — push access). Rest use HTTPS.
No GitHub remotes to repoint.

### 1c: Missing Repos — 1
| Repo | Status |
|------|--------|
| `infra/sporePrint` | Cloned via SSH (HTTPS failed — private?) |

### 1d: Pull — 40/40 OK
All repos fetched and rebased successfully. Zero failures.

### 1e: State
- **Wave**: 155n (blurb template says 155i — outdated)
- **Dirty repos**: ZERO (all 40 clean)
- **biomeOS**: strandGate shows v4.51 in ECOSYSTEM_BLURB. biomeGate version TBD.

### 1f: hotSpring Code Health

| Metric | Value |
|--------|-------|
| Version | 0.6.32 |
| Rust | 1.97.1 |
| `cargo test --lib` | **627 pass, 0 fail** |
| `cargo clippy --lib` | **1 warning** (`manual_noop_waker` in `block_on.rs`) |
| `cargo fmt --check` | **Diffs in `arxiv_production_run.rs` (bin) + 6 lib files** |
| Upstream warnings | 2 (primalSpring: `aarch64_depot_path`, `chrono_lite_cutoff` — known) |

**Clippy finding**: `block_on.rs:13` — manual `Wake` impl should use
`std::task::Waker::noop()` (available since Rust 1.85). Non-blocking.

**Format diffs**: Recent commit `c3d2770` (multi-GPU sweep) introduced
formatting deviations in `arxiv_production_run.rs`. Several lib files
(`fleet_client.rs`, `niche/mod.rs`, `serve/dispatch.rs`, `serve/mod.rs`,
`serve/transport.rs`, `toadstool_report.rs`) have minor formatting diffs.
All are rustfmt-fixable.

---

## Phase 2: Enrollment

| Check | Result |
|-------|--------|
| Hostname | `biomeGate` |
| WireGuard IP | 10.13.37.3 |
| WG status | LIVE (golgiBody ping 41.6 ms) |
| wave.toml listing | **NOT LISTED** — biomeGate absent from `gates.online` |
| VFIO devices | 3 bound: Titan V (`21:00.0`), K80 ×2 (`4b:00.0`, `4c:00.0`) |
| Host GPU | RTX 5060 (`02:00.0`) on nvidia driver |

**Action needed**: eastGate overwatch should add biomeGate to wave.toml gate roster.

---

## Phase 3: Code Team — hotSpring GPU Focus

### Active Workstreams

1. **Revalidation spec written** (`specs/BIOMEGATE_REVALIDATION_SPEC.md`, untracked):
   - Workstream 1: Diesel engine revalidation (sovereign GPU boot, VFIO dispatch)
   - Workstream 2: hotQCD revalidation (PRNG polyfill, plaquette parity)

2. **arXiv publication handoff received** (`HOTSPRING_QCD_PUBLICATION_HANDOFF.md`):
   - 5 `[TODO]` data sections to fill in `whitePaper/subGen/LATTICE_QCD_CONSUMER_GPU_ARXIV.md`
   - Plaquette measurements, DF64 precision, autocorrelation, multi-vendor benchmarks

3. **Deep debt sprint COMPLETE** (`HOTSPRING_WAVE155n_DEEP_DEBT_MODERNIZATION_2026-08-01.md`):
   - thiserror migration, file refactoring, stub completion, edition 2024

### GPU Dispatch Path Summary

| GPU | Dispatch | Status |
|-----|----------|--------|
| RTX 5060 | wgpu local (host driver) | READY |
| Titan V | VFIO sovereign (toadStool cylinder) | DEVICES BOUND, dispatch TBD |
| K80 ×2 | VFIO sovereign (toadStool cylinder) | DEVICES BOUND, dispatch TBD |

### Immediate Priorities

1. Profile all 3 GPU architectures via `bench_silicon_profile`
2. Run `hotspring_unibin validate` — 18 bare scenarios
3. Validate PRNG fix path (cpu_mom workaround) on RTX 5060
4. Begin diesel engine revalidation experiments on VFIO GPUs

---

*biomeGate sync report — 40/40 repos clean, 627 tests pass, 4 GPUs visible,
WireGuard LIVE at 10.13.37.3. Gate not yet in wave.toml roster.*
