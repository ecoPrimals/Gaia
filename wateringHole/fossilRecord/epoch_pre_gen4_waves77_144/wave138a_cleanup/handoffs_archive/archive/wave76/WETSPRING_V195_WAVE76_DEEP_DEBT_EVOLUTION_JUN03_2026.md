# wetSpring V195 — Wave 76 Deep Debt: Architecture Evolution

**Date:** June 3, 2026
**From:** wetSpring (southGate)
**To:** primalSpring coordination (eastGate)
**Phase:** Wave 76 — deep debt resolution, architecture evolution

---

## Summary

wetSpring V195 completes the Wave 76 deep debt sprint. TCP transport enables
cross-gate JSON-RPC, primal name literals are centralized into constants,
Songbird capability registration is fixed for IPC-only deployments, and ionic
bonding is modernized with safe casts and lazy allocation. All dependencies
are bumped to latest patch. Build passes with **0 clippy warnings** and
**2,089 tests (0 failures)**.

---

## Changes (V194 → V195)

### Architecture

| Change | Files | Impact |
|--------|-------|--------|
| TCP transport | `ipc/transport.rs` | `Transport::Tcp(addr)` variant, `tcp_jsonrpc_line()`, unified `jsonrpc_line()` dispatch, `{ENV_VAR}_TCP` resolution priority. 4 new tests. |
| Primal name centralization | `ncbi/sra.rs`, `ipc/handlers/mod.rs`, `ipc/composition_health.rs`, `facade/routes.rs` | Replaced scattered string literals with `primal_names::*` constants |
| Songbird registration fix | `ipc/songbird.rs` | Non-`barracuda-lib` builds now register `niche::CAPABILITIES` instead of `&[]` |
| macOS RSS support | `bench/mod.rs` | Safe `ps` subprocess (respects `#![forbid(unsafe_code)]`) |
| `--port` CLI wired | `bin/wetspring_unibin/main.rs` | TCP listen port parameter accepted and logged |
| Ionic bonding modernized | `ipc/bonding.rs` | `try_from` casts, dead match arm removed, `ok_or_else` lazy allocation |
| Registries const-ified | `validation/scenarios/{benchmark_registry,registry}.rs` | `new/len/is_empty` promoted to `const fn` |
| Stale lint expects removed | `validation/experiments/exp_cooperation.rs`, `exp_cross_ecosystem_pangenome.rs` | Unfulfilled `#[expect]` attributes cleaned |

### Dependencies

| Crate | Old | New |
|-------|-----|-----|
| axum | 0.8.8 | 0.8.9 |
| blake3 | 1.8.3 | 1.8.5 |
| proptest | 1.10 | 1.11 |
| tempfile | 3.26 | 3.27 |
| tower-http | 0.6.8 | 0.6.11 |

---

## Build Gate

| Check | Result |
|-------|--------|
| `cargo test --workspace` | **2,089 passed, 0 failed, 3 ignored** |
| `cargo test --workspace --features guidestone` | **2,089 passed, 0 failed, 3 ignored** |
| `cargo clippy --workspace --all-targets` | **0 warnings** |
| `cargo clippy --workspace --all-targets --features guidestone` | **0 warnings** |
| `cargo fmt --all -- --check` | **clean** |
| unsafe code | **0** (`#![forbid(unsafe_code)]`) |

---

## Audit Findings (Pre-Cleanup)

| Dimension | Finding |
|-----------|---------|
| Files >800 lines | **0** (largest: 939 LOC) |
| `unsafe` code | **0** (enforced by `#![forbid(unsafe_code)]`) |
| Production `.unwrap()` | **0** |
| Production mocks | **0** |
| `lazy_static!` | **0** (uses `std::sync::LazyLock`) |
| `Box<dyn Error>` | **0** (typed errors throughout) |
| Hardcoded primal names | Centralized into `primal_names::*` constants |
| Hardcoded socket paths | Resolved via `Transport::resolve()` with env-var discovery |

---

## Remaining Gaps (Not Code Debt)

| Gap | Owner | Status |
|-----|-------|--------|
| WS-9: L3 read mapper FASTQ parity | wetSpring | Needs FASTQ test dataset |
| WS-11: MAPQ calibration | wetSpring | Needs calibration dataset |
| Forgejo SSH key | eastGate ops | Cannot push — key needs API registration |
| `compute.fan_out` | toadStool | Tenaillon 264-clone batch blocked |
| `capability.call` remote dispatch | songbird | Cross-gate routing needs TCP mesh |
| `crypto.ionic_bond.seal` (Ed25519) | bearDog | Provenance seal signing |
| biomeOS `nest.sync` E2E | biomeOS | WS-2 cross-spring data exchange |

---

## For Upstream Primal Teams

### Songbird
- TCP mesh routing for cross-gate `capability.call` — wetSpring has TCP transport ready, waiting for Songbird relay support.

### bearDog
- `crypto.ionic_bond.seal` (Ed25519) — needed for provenance seal signing during bond termination.
- `crypto.ionic_bond.propose` / `verify_proposal` — E2E ionic contract negotiation.

### toadStool
- `compute.fan_out` scheduler — Tenaillon 264-clone batch (590 GB) still waiting.

### biomeOS
- `nest.sync` E2E integration — WS-2 cross-spring data exchange.

---

**Commit:** V195 on `syntheticChemistry/wetSpring`
**ACK:** FRAGO wave76-parity-sprint-springs complete. wetSpring ready for upstream audit.
