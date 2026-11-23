# barraCuda — Wave 116 Deep Debt Sprint + Spring Absorption

**Status**: COMPLETE | **Gate**: eastGate | **Date**: 2026-06-19
**Repo**: `ecoPrimals/primals/barraCuda`
**Version**: 0.4.0 (Unreleased — Waves 109–116)

---

## Summary

Full deep debt audit and evolution pass on barraCuda. All quality gates green.
Spring absorption: `linalg.batched_tridiag_eigh` IPC handler wired (groundSpring Exp 012).
All root docs updated to current state. Zero files >800L, zero production mocks,
zero unsafe (except isolated SPIR-V passthrough), zero hardcoded primal names/ports.

---

## Executed Work

### Deep Debt — Code Quality
| Item | Before | After |
|------|--------|-------|
| Serialization | bincode (RUSTSEC-2025-0141) | postcard (format tag 2, advisory resolved) |
| Numerical ops | `a * b + c` (238 sites) | `a.mul_add(b, c)` (fused, IEEE 754) |
| Transport | `transport.rs` (780L monolith) | `transport/` module (server 455L + connection 233L + dispatch 89L) |
| Transport tests | `transport_tests.rs` (858L) | `transport_tests/` module (7 files, max 225L) |
| Doc examples | `println!()` (37 sites) | `tracing::info!()` |
| .expect() audit | Unaudited | 6 sites annotated with `#[expect(reason)]` |
| CI pipeline | fmt + clippy + test | + cargo deny + doc -D warnings + nextest |
| MSRV | 1.87 | 1.92 (Edition 2024, let-chains) |

### Spring Absorption
| Method | Source | Path | Status |
|--------|--------|------|--------|
| `linalg.batched_tridiag_eigh` | groundSpring Exp 012 | `ipc/methods/linalg.rs` | Done |
| Capability registry entry | groundSpring | `config/capability_registry.toml` | Done |
| method.describe schema | — | `ipc/methods/primal.rs` | Done |
| 12 coverage tests | — | `methods_coverage_tests/linalg_tridiag_tests.rs` | Done |

### Doc Updates
- STATUS.md — date, test counts, method count, spring absorption
- WHATS_NEXT.md — Wave 116 section, BatchedTridiag shipped, nextest in CI
- REMAINING_WORK.md — date, Waves 109–116 achieved section
- README.md — MSRV 1.92, test counts, method counts
- START_HERE.md — MSRV 1.92
- CHANGELOG.md — [Unreleased] section with full Wave 109–116 entries
- SPRING_ABSORPTION.md — Wave 116 groundSpring Exp 012 table
- PURE_RUST_EVOLUTION.md — date, metrics, postcard, transport modules
- SOVEREIGN_PIPELINE_TRACKER.md — date
- FRAGO_WAVE93 — superseded banner

---

## Quality Gates

| Gate | Status |
|------|--------|
| `cargo fmt --check` | PASS |
| `cargo clippy --workspace --all-targets -- -D warnings` | PASS (0 warnings) |
| `RUSTDOCFLAGS="-D warnings" cargo doc` | PASS |
| `cargo deny check` | PASS (advisories, bans, licenses, sources ok) |
| `cargo check --workspace` | PASS |

---

## Metrics

| Metric | Value |
|--------|-------|
| Registered JSON-RPC methods | 98 |
| Tests (barracuda-core) | 708 |
| Tests (barracuda) | 3,916 (3,852 pass + 51 GPU contention + 13 ignored) |
| Tests total | 4,624 |
| Line coverage (llvmpipe) | ~80% |
| Files >800L | 0 |
| Unsafe blocks (production) | 1 (barracuda-spirv SPIR-V passthrough, isolated + documented) |
| -sys crates | 0 |
| Production mocks | 0 |
| `Result<T, String>` in prod | 0 |
| `todo!()`/`unimplemented!()` | 0 |

---

## Known Issues (not barraCuda bugs)

- **51 GPU test failures under `cargo test`**: wgpu-core device resource contention when
  tests share a single process. Passes under `cargo nextest` (separate processes) and
  with `--test-threads=1`. CI uses nextest. Upstream wgpu-core limitation.

---

## For Upstream Overwatch Audit

### Gaps flagged for upstream primal teams

| Gap | Owner | Priority |
|-----|-------|----------|
| **DF64 NVK hardware verification** on Titan V (Mesa/NVK build path) | ironGate (when enrolled) | P1 |
| **Tensor-core GEMM E2E** (kernel_router → coralReef HMMA → toadStool dispatch) | coralReef + toadStool | P1 |
| **OOM auto-migration** (QuotaTracker detect + auto-migrate not wired) | barraCuda | P1 |
| **Sovereign pipeline readback** (compute.dispatch.result polish) | barraCuda + toadStool | P1.5 |
| **petalTongue physics ops** (math.physics.nbody in dispatch surface) | barraCuda | P2 |
| **90% test coverage** (requires real GPU hardware, llvmpipe ceiling ~80%) | ironGate hardware | P2 |
| **Kokkos/LAMMPS/SciPy parity benchmarks** (hardware run + published comparison) | ironGate hardware | P2 |
| **Tier-2 `barracuda.compute` API** (sporePrint doc/API convergence) | barraCuda + sporePrint | P2 |
| **GPU batched tridiag eigensolver** (IPC done, GPU shader dispatch optional) | barraCuda | P2 |
| **Optional tensor encryption** (BearDog ChaCha20-Poly1305 opt-in) | barraCuda + BearDog | P2 |

### False positives cleared

These items appeared in prior handoffs/audits but are resolved:
- ~~bincode unmaintained~~ → postcard (RUSTSEC-2025-0141)
- ~~transport.rs >800L~~ → transport/ module
- ~~println in library code~~ → tracing::info!()
- ~~Result<T, String> in production~~ → all thiserror typed
- ~~mocks in production~~ → FakeQuantize is legitimate ML QAT
- ~~hardcoded ports/primal names~~ → capability-based discovery with env overrides
- ~~nextest "consider"~~ → already in CI
- ~~2-gate mesh proof P1~~ → 4-gate mesh operational, 13/13 NUCLEUS on eastGate

---

## Cascade

Changes committed and pushed to origin. Upstream overwatch: audit gaps table
and coordinate with primal teams as needed.
