# Silicon Atheism: Full Cross-Compile Convergence — Wave 140b

**Date**: Jul 15, 2026 | **Wave**: 140b | **From**: eastGate overwatch
**Scope**: Every primal compiles for every architecture. Subsystem convergence.
**Priority**: P1 — this IS the deployment evolution

---

## Directive

songBird proved 13 architectures compile. That's the scout. Now every primal
follows. The goal is not "songBird runs everywhere" — it's "the ecosystem runs
everywhere." This means solving three things simultaneously:

1. **PPC32 fix** — `portable-atomic` crate. Completes 9/9 exotic architectures.
2. **Per-primal adoption** — Phase 2 transport/signals shipped in cellMembrane
   but 11 primals still import `tokio::net::UnixStream` directly.
3. **Subsystem convergence** — UDS, IPC, data backends, and service lifecycle
   must converge into shared platform-agnostic abstractions.

---

## Fix 1: portable-atomic for PPC32 (and all 32-bit targets)

The PPC32 failure is `AtomicU64` unavailability on platforms where
`target_has_atomic = "64"` is false. This affects PPC32 and potentially other
32-bit embedded targets.

### Implementation

In the workspace root `Cargo.toml` (or in a new `primal-portable` crate):

```toml
[dependencies]
portable-atomic = { version = "1", features = ["fallback"] }
```

The `portable-atomic` crate provides `AtomicU64` on all platforms via CAS loop
or spin-lock fallback where hardware atomics don't exist. The dependency chain
is: our code → `portable-atomic::AtomicU64` (works everywhere) instead of
`std::sync::atomic::AtomicU64` (fails on 32-bit PPC).

**However**: the `AtomicU64` usage causing the failure is in **tokio** and
other deps, not our code directly. The fix is:

```toml
# In workspace Cargo.toml — forces all transitive deps to use portable-atomic
[patch.crates-io]
# Not needed if tokio adopts portable-atomic natively.
# Instead, set:
[target.'cfg(not(target_has_atomic = "64"))'.dependencies]
portable-atomic = { version = "1", features = ["require-cas"] }
```

**Preferred approach**: Enable `portable-atomic` as a Cargo feature on `tokio`:

```toml
[dependencies]
tokio = { version = "1", features = ["full", "portable-atomic"] }
```

Tokio has had `portable-atomic` support since 1.33. This is the clean fix —
no patching, no forks. Just a feature flag.

### Why this matters beyond PPC32

- **Consoles**: Nintendo Switch (ARM, but future variants may differ), retro
  console emulation platforms, Steam Deck (x86_64 but ecosystem consistency)
- **Embedded control**: Industrial PLCs, automotive ECUs, SCADA systems
- **32-bit IoT**: Older Raspberry Pi, ESP32 (via esp-idf Rust support)
- **Completeness**: 9/9 exotic architectures. No asterisks.

### Owner: cellMembrane team (affects all workspace Cargo.toml files)
### Effort: Small — single feature flag addition per workspace

---

## Fix 2: Per-Primal Phase 2 Adoption Tracker

cellMembrane shipped `TransportEndpoint::NamedPipe`, `InitSystem::detect()`,
and `ProcessManager`. But the individual primals have NOT adopted these
abstractions yet. They still import `tokio::net::UnixStream` directly.

### Adoption Matrix

| Primal | UDS→Transport | Signals→ProcessManager | FS→Platform | Status |
|--------|--------------|----------------------|-------------|--------|
| songBird | **DONE** (reference impl) | **DONE** | N/A | **COMPLETE** |
| bearDog | **DONE** (`1c3dc9d` IpcStream enum) | N/A | N/A | **COMPLETE** |
| biomeOS | TODO (communication, capabilities, provider, tarpc_transport) | N/A | TODO (rustix::fs) | BLOCKED |
| nestGate | N/A | N/A | TODO (rustix::fs statfs) | BLOCKED |
| rhizoCrypt | TODO (unix_socket adapter L29,L144-170) | N/A | N/A | BLOCKED |
| squirrel | TODO (auth, mcp, ipc_client) | N/A | N/A | BLOCKED |
| sweetGrass | TODO (store-nestgate, service) | N/A | N/A | BLOCKED |
| loamSpine | TODO (btsp/provider_client, transport/neural_api) | TODO (signals.rs:97) | N/A | BLOCKED |
| skunkBat | TODO (ipc/transport/btsp.rs) | TODO (ipc/mod.rs:178) | N/A | BLOCKED |
| coralReef | TODO (primal-rpc-client transport.rs:64) | N/A | N/A | BLOCKED |
| barraCuda | TODO (ipc/btsp.rs, ipc/transport/server.rs) | TODO (main.rs:158) | N/A | BLOCKED |
| petalTongue | TODO (transport.rs, biomeos_discovery/client.rs) | N/A | N/A | BLOCKED |
| toadStool | N/A | N/A | N/A | **DONE** (S329: 134 files `cfg`-gated, `cargo check --target x86_64-pc-windows-gnu` passes) |
| sourDough | N/A | N/A | TODO (PermissionsExt) | BLOCKED |

**Score: 1/14 primals fully cross-platform. 13 remaining.**

### The Pattern

Each primal team applies the same mechanical transformation:

```rust
// BEFORE (unix-only):
use tokio::net::UnixStream;
let stream = UnixStream::connect(socket_path).await?;

// AFTER (platform-agnostic, using cellMembrane's TransportEndpoint):
use membrane_transport::TransportEndpoint;
let endpoint = TransportEndpoint::from_env_or_default();
let stream = endpoint.connect().await?;
```

songBird's implementation is the reference. The `TransportEndpoint` enum
dispatches to UDS on unix, NamedPipe on Windows, TCP as universal fallback.

---

## Fix 3: Subsystem Convergence Map

The primals share several subsystems that need convergence into unified
platform-agnostic abstractions. Currently each primal re-implements or
directly imports platform-specific versions.

### Transport Layer (IPC + Network)

| Subsystem | Current State | Convergence Target |
|-----------|--------------|-------------------|
| Primal-to-primal IPC | 11 primals use raw `UnixStream` | `TransportEndpoint` (cellMembrane Phase 2) |
| biomeOS Neural API | `tarpc::serde_transport::unix` | `TransportEndpoint` with tarpc adapter |
| rhizoCrypt DAG sync | Custom unix_socket adapter | `TransportEndpoint` |
| bearDog tower-atomic | Custom tower service over UDS | `TransportEndpoint` with tower layer |
| songBird mesh | UDS + NamedPipe + TCP | **REFERENCE** — already converged |

**Convergence**: Single `primal-transport` crate (or `membrane-transport`)
exporting `TransportEndpoint`, `PrimalStream`, `PrimalListener`. Every primal
depends on this instead of raw tokio socket types.

### Service Lifecycle (Init + Signals + Shutdown)

| Subsystem | Current State | Convergence Target |
|-----------|--------------|-------------------|
| Signal handling | 3 primals use `tokio::signal::unix` directly | `ProcessManager::wait_for_shutdown()` |
| Service init | Each primal has custom startup | `InitSystem::detect()` → systemd/launchd/SCM |
| Graceful shutdown | Mixed: some signal, some channel | Unified shutdown coordination |
| Process management | 3 primals fork/kill directly | `ProcessManager` trait |

**Convergence**: `ProcessManager` trait already in cellMembrane. Primals adopt it.

### Data Backends (Storage + State)

| Subsystem | Current State | Convergence Target |
|-----------|--------------|-------------------|
| nestGate CAS | Content-addressed store with fs-specific code | Platform-agnostic storage trait |
| rhizoCrypt DAG | LMDB/sled backend | Already cross-platform (LMDB works everywhere) |
| sweetGrass key-value | Custom store with UDS client | `TransportEndpoint` for client, store is cross-platform |
| squirrel credentials | fs-based with unix permissions | Platform credential store (Keyring on Windows, Keychain on macOS) |
| sourDough fs ops | `PermissionsExt::mode()` | `Platform::set_permissions()` abstraction |

**Convergence**: Data backends are mostly cross-platform already (LMDB, sled,
SQLite all work everywhere). The convergence gap is in how they're **accessed**
(UDS transport to stores) and how **permissions** are set.

### Deployment & Discovery

| Subsystem | Current State | Convergence Target |
|-----------|--------------|-------------------|
| Binary discovery | Hardcoded paths, `which` shell-out | `Platform::bin_dir()` + manifest lookup |
| Socket discovery | `/run/primal/*.sock` hardcoded | `Platform::socket_dir()` + `\\.\pipe\primal-*` on Windows |
| Config location | `~/.config/`, `/etc/` hardcoded | `Platform::config_dir()` (dirs crate) |
| Log location | journald / file / stdout mixed | `Platform::log_target()` |

**Convergence**: `Platform` type system (Phase 1) provides the foundation.
Each discovery function dispatches on `Platform::current()`.

---

## Recommended Execution Order

### Wave 140b–141: Transport Convergence (highest leverage)

1. **cellMembrane**: Publish `primal-transport` crate with `TransportEndpoint`,
   `PrimalStream`, `PrimalListener` (extract from cellMembrane Phase 2 delivery)
2. **Each primal team**: Adopt `primal-transport` — mechanical replacement of
   raw `tokio::net::UnixStream` imports (see adoption matrix above)
3. **cellMembrane**: Add `tokio` feature `portable-atomic` to all workspace
   `Cargo.toml` files → PPC32 unblocked
4. **sporeGate**: Full 14-primal harvest for Windows target after transport adoption
5. **primalSpring**: `full-cross-compile` scenario validating all 14 primals
   compile for all 4 depot architectures

### Wave 141–142: Lifecycle + FS Convergence

6. **Each primal with signals**: Adopt `ProcessManager::wait_for_shutdown()`
7. **nestGate, biomeOS, sourDough**: Adopt `Platform::detect()` for FS ops
8. ~~**toadStool**: Feature-gate `hw-safe` behind `linux-hw`~~ **DONE** (S329: full workspace `cfg` gating)
9. **sporeGate**: Full 14-primal harvest for all 13 architectures
10. **primalSpring**: `depot-architecture-coverage` scenario

### Wave 142+: Discovery + Data Backend Convergence

11. **cellMembrane**: `Platform::socket_dir()`, `Platform::config_dir()`,
    `Platform::bin_dir()` implementations
12. **squirrel**: Platform credential store abstraction
13. **All primals**: Adopt platform-aware discovery
14. **sporeGate**: WASM target exploration (`wasm32-wasip2`)

---

## Success Criteria

```
14/14 primals compile for x86_64-linux-musl       (currently 16/16 — membrane included)
14/14 primals compile for aarch64-linux-musl       (currently 16/16)
14/14 primals compile for aarch64-linux-android     (currently 12/14)
14/14 primals compile for x86_64-pc-windows-gnu     (currently 1/14)
14/14 primals compile for riscv64gc-linux-gnu        (currently 1/14 — songBird only)
14/14 primals compile for powerpc-linux-gnu          (currently 0/14 — AtomicU64)
primalSpring scenario: full-cross-compile GREEN
Depot: all architectures serving signed binaries
```

**When this is done, any primal can run on any hardware — from IBM mainframes
to Raspberry Pi Zeros to game consoles to RISC-V open silicon boards.**

---

*Wave 140b: Silicon Atheism convergence plan. portable-atomic for PPC32 (consoles,
embedded). 13/14 primals need transport adoption. Subsystem convergence map across
transport, lifecycle, data backends, and discovery. songBird is the reference —
now every primal follows.*
