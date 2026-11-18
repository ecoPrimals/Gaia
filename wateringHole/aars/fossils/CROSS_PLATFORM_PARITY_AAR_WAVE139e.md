# AAR: Cross-Platform Parity Audit — Wave 139e

**Date**: 2026-07-15 | **Gate**: eastGate overwatch + sporeGate builder
**Scope**: Full ecosystem Windows + Android harvest, platform divergence triage
**Outcome**: 45 depot binaries across 4 architectures. First comprehensive
cross-platform portability map produced.

---

## Summary

Attempted full 14/14 primal harvest for all deployment targets:
- **x86_64-unknown-linux-musl**: 16/16 (COMPLETE — reference architecture)
- **aarch64-unknown-linux-musl**: 16/16 (COMPLETE)
- **aarch64-linux-android**: 12/14 (3 failures: petalTongue, toadStool, sourDough)
- **x86_64-pc-windows-gnu**: 1/14 (songBird only; 13 failures)

This audit maps every primal's platform portability status and identifies the
exact evolution required for OS Atheism Phase 2+.

---

## Toolchain Setup (RESOLVED)

Before this harvest, three pinned toolchains were **missing the Windows target**:

| Toolchain | Missing Target | Fixed |
|-----------|----------------|-------|
| `1.93.0` (bearDog) | `x86_64-pc-windows-gnu` | `rustup target add` |
| `1.94.0` (songBird) | already installed | — |
| `1.94.1` (nestGate, rhizoCrypt) | `x86_64-pc-windows-gnu` + `aarch64-linux-android` | `rustup target add` |

**Lesson**: Every workspace-pinned `rust-toolchain.toml` must include ALL
ecosystem deployment targets. This should be enforced by primalSpring scenario
or linted at cascade time.

---

## Per-Primal Cross-Platform Matrix

| Primal | Linux musl | Linux gnu | Android | Windows | Failure Category |
|--------|-----------|-----------|---------|---------|-----------------|
| songBird | OK | OK | OK | OK | — |
| bearDog | OK | — | OK | FAIL | UDS transport (tower-atomic) |
| biomeOS | OK | — | OK | FAIL | UDS transport + rustix::fs + tarpc::unix |
| nestGate | OK | — | OK | FAIL | rustix::fs (storage detector) |
| rhizoCrypt | OK | — | OK | FAIL | UDS transport (unix_socket adapter) |
| squirrel | OK | — | OK | FAIL | UDS transport (auth, mcp, ipc_client) |
| sweetGrass | OK | — | OK | FAIL | UDS transport (store-nestgate, service) |
| loamSpine | OK | — | OK | FAIL | UDS transport + signal::unix |
| skunkBat | OK | — | OK | FAIL | UDS transport + signal::unix |
| coralReef | OK | OK | OK | FAIL | UDS transport (primal-rpc-client) |
| barraCuda | OK | OK | OK | FAIL | UDS transport + unix signal literal |
| petalTongue | OK | — | FAIL | FAIL | UDS transport + android-activity NDK |
| toadStool | OK | — | FAIL | FAIL | VFIO/mmap (hw-safe: fd, ioctl, mm) |
| sourDough | OK | — | FAIL | FAIL | std::os::unix::fs::PermissionsExt |
| membrane | OK | — | — | — | (cellMembrane — not in harvest loop) |
| nucleus_launcher | OK | — | OK | — | (primalSpring — not in harvest loop) |

---

## Failure Category Analysis

### Category 1: UDS Transport — 11 primals affected (Windows only)

**Root Cause**: `tokio::net::UnixStream` is unconditionally imported.
On Windows, tokio compiles UDS support behind `cfg(unix)` — the import
simply doesn't exist.

**Affected crates** (the actual source of the compile error):

| Crate | File | Lines |
|-------|------|-------|
| `beardog-tower-atomic` | `src/lib.rs` | L61, L132-250 |
| `biomeos-primal-sdk` | `src/communication.rs`, `src/capabilities.rs`, `src/provider.rs` | L39, L17, L304 |
| `neural-api-client` | `src/connection.rs` | L11 |
| `biomeos-primal-sdk` | `src/tarpc_transport.rs` | L47 (`tarpc::serde_transport::unix`) |
| `rhizo-crypt-core` | `src/clients/adapters/unix_socket.rs` | L29, L144-170 |
| `sweet-grass-store-nestgate` | `src/client.rs` | L10 |
| `sweet-grass-service` | multiple files | transport_connect, handlers |
| `squirrel/core/auth` | `src/capability_crypto.rs`, `src/security_provider_client.rs` | L32, L27 |
| `squirrel/universal-patterns` | `src/ipc_client/connection.rs`, `src/registry/discovery.rs` | L6, L15 |
| `loam-spine-core` | `src/btsp/provider_client.rs`, `src/transport/neural_api.rs` | L18, L31 |
| `skunk-bat-server` | `src/ipc/transport/btsp.rs` | L78 |
| `coralReef/primal-rpc-client` | `src/transport.rs` | L64 |
| `petal-tongue-core` | `src/transport.rs`, `src/biomeos_discovery/client.rs` | L221-300, L16 |
| `barracuda-core` | `src/ipc/btsp.rs`, `src/ipc/transport/server.rs` | L153-546, L2-3 |

**Fix pattern** (OS Atheism Phase 2):
```rust
// Before (unix-only):
use tokio::net::UnixStream;

// After (platform-agnostic):
#[cfg(unix)]
use tokio::net::UnixStream;
#[cfg(windows)]
use tokio::net::windows::named_pipe::NamedPipeClient;

// Or, abstract behind a trait:
use crate::transport::PrimalStream; // platform-dispatched
```

**songBird already solved this** — it has `NamedPipeServer`/`NamedPipeClient`
support behind `#[cfg(windows)]` guards. This is the reference implementation
for all other primals.

**Effort estimate**: Medium per primal. The pattern is mechanical but each
primal has 2-8 files to update. songBird's implementation provides the template.

### Category 2: Unix Signal Handling — 3 primals affected

**Affected**: loamSpine, skunkBat, barraCuda

| Crate | File | Issue |
|-------|------|-------|
| `loam-spine-core` | `src/service/signals.rs:97` | `tokio::signal::unix` |
| `skunk-bat-server` | `src/ipc/mod.rs:178` | `tokio::signal::unix::signal()` |
| `barracuda-core` | `src/bin/barracuda/main.rs:158` | literal `unix` in signal setup |

**Fix pattern** (OS Atheism Phase 2 — ProcessManager trait):
```rust
#[cfg(unix)]
let mut sigterm = tokio::signal::unix::signal(SignalKind::terminate())?;
#[cfg(windows)]
let sigterm = tokio::signal::ctrl_c();
```

### Category 3: Platform-Specific FS — 3 primals affected

| Primal | Issue | Detail |
|--------|-------|--------|
| nestGate | `rustix::fs` | Storage detector uses linux-specific `statfs` |
| biomeOS | `rustix::fs` + `rustix::system` | Disk space detection |
| sourDough | `std::os::unix::fs::PermissionsExt` | Unix file permission `mode()` |

**Fix**: Abstract behind `Platform::detect()` with fallback implementations
for Windows (using `GetDiskFreeSpaceEx`, `GetFileAttributes`, etc.).

### Category 4: Hardware/Kernel Deps — 1 primal (toadStool)

| Crate | Issue |
|-------|-------|
| `toadstool-common/hw-safe` | `std::os::fd`, `rustix::mm` (mmap), `rustix::ioctl` (VFIO) |

**toadStool** is a GPU compute primal using VFIO DMA, huge pages, and
memory-mapped device files. These are fundamentally Linux kernel APIs.

**Resolution**: toadStool should be `cfg(unix)`-gated entirely or have its
hw-safe crate behind a `linux-hw` feature flag. Windows GPU access uses
different APIs (DXGI, Vulkan device memory).

### Category 5: Android NDK — 1 primal (petalTongue)

| Issue | Detail |
|-------|--------|
| `android-activity` crate | Requires `game-activity` or `native-activity` feature |
| `PointerImpl` not found | Missing Activity lifecycle bindings |

**petalTongue** pulls in `android-activity` as a dependency, which requires
NDK-specific Activity lifecycle setup. This is expected — petalTongue on Android
needs a proper Android Application harness, not a CLI binary.

**Resolution**: petalTongue's Android target should be a library (`cdylib`)
loaded by an Android Application, not a standalone binary.

---

## Evolution Recommendations for cellMembrane / Primal Teams

### Priority 1: Transport Abstraction Layer (Phase 2)

Create `primal-transport` crate with:
```rust
pub enum PrimalStream {
    #[cfg(unix)]
    Unix(tokio::net::UnixStream),
    #[cfg(windows)]
    NamedPipe(tokio::net::windows::named_pipe::NamedPipeClient),
    Tcp(tokio::net::TcpStream),
}
```

All 11 UDS-affected primals should depend on `primal-transport` instead of
importing `tokio::net::UnixStream` directly. songBird's existing
Named Pipe support is the reference implementation.

### Priority 2: Signal Abstraction (Phase 2)

Part of the `ProcessManager` trait in OS Atheism Phase 2:
```rust
pub trait ProcessManager {
    async fn wait_for_shutdown(&self) -> ShutdownReason;
}
```

### Priority 3: Platform FS Abstraction (Phase 3)

For sourDough, nestGate, biomeOS — abstract `PermissionsExt`, `statfs`,
disk space queries behind `Platform`-dispatched implementations.

### Priority 4: Feature-Gate Hardware (Targeted)

toadStool `hw-safe` → `#[cfg(target_os = "linux")]` or feature flag.
petalTongue Android → library target, not binary.

---

## Depot State After Harvest

```
Architecture              Binaries  Status
x86_64-unknown-linux-musl    16     FRESH (Jul 15) — reference
aarch64-unknown-linux-musl   16     FRESH (Jul 15) — Pixel/ARM
aarch64-linux-android        12     FRESH (Jul 15) — 3 failures
x86_64-pc-windows-gnu         1     songbird.exe — 13 blocked on Phase 2
                              --
Total:                        45    BLAKE3 checksums + Ed25519 signed
```

Depot synced to golgi VPS. `membrane.primals.eco/depot/` serving all 45 binaries.

---

## Divergence from OS Atheism Phase 1

The `Platform` type system (shipped in 07c16a5) correctly models all 9 target
triples. But the **primals themselves** don't use it yet — they import
platform-specific APIs directly. The gap:

```
Phase 1: TargetOs/CpuArch/LinkModel/Platform TYPES  → SHIPPED
Phase 2: ProcessManager + Transport abstraction      → BLOCKS Windows (13 primals)
Phase 3: Shell-out elimination + FS abstraction      → BLOCKS 3 primals FS ops
Phase 4: Gate bootstrap Platform branching           → BLOCKS isomorphic deploy
Phase 5: Isomorphic depot pipeline (Platform-aware)  → BLOCKS auto-fetch-install
Phase 6: NUCLEUS composition (deploy.graph)          → BLOCKS USB kit
```

The critical insight: **Phase 2 (transport + signals) unblocks 11 of the 13
Windows-failing primals.** This is the highest-leverage evolution.

---

## primalSpring Validation

New `platform-type-parity` scenario shipped (b91dd41):
- 39 checks validating type definitions, depot triple coverage, gate assignments
- Cross-validated against live cellMembrane source
- 162 total scenarios, 1194 tests, 0 failures

---

## Action Items for Upstream

| ID | What | Owner | Priority |
|----|------|-------|----------|
| TRANSPORT-ABSTRACT | Create `primal-transport` crate with UDS/NamedPipe/TCP dispatch | cellMembrane | P1 |
| SIGNAL-ABSTRACT | Platform-agnostic shutdown signal in ProcessManager | cellMembrane | P1 |
| FS-ABSTRACT | Platform FS operations (permissions, statfs, disk) | cellMembrane | P2 |
| TOADSTOOL-CFGGATE | Feature-gate hw-safe behind `linux-hw` | toadStool team | P2 |
| PETALTONGUE-ANDROID | Android target = cdylib, not binary | petalTongue team | P3 |
| SOURDOUGH-PERMS | Replace `PermissionsExt::mode()` with cross-platform check | sourDough team | P2 |
| TOOLCHAIN-LINT | Enforce all targets in workspace `rust-toolchain.toml` | primalSpring | P3 |
| DEPOT-COVERAGE-SCENARIO | Update s_depot_binary_standard to track per-arch counts | primalSpring | P3 |

---

*Wave 139e: First comprehensive cross-platform harvest reveals the OS Atheism
evolution gap. Phase 1 (types) shipped. Phase 2 (transport) is the critical
unlock — a single `primal-transport` crate unblocks 11/13 Windows primals.
songBird's Named Pipe implementation is the reference. 45 binaries across 4
architectures deployed, signed, and serving from VPS depot.*
