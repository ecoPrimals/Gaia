# Cross-Architecture Adoption — Per-Primal Handoffs

**Date**: Jul 16, 2026 | **Wave**: 142a | **From**: eastGate overwatch
**Reference**: `SILICON_ATHEISM_CONVERGENCE_WAVE140b.md`, `CROSS_PLATFORM_PARITY_AAR_WAVE139e.md`
**Phase 2 reference**: petalTongue `petal-tongue-platform` (`1af1a98`)

## Guiding Principle: Abstraction Over Gating

Phase 1 (`#[cfg]` gating) is **COMPLETE** — all 14 primals compile on all 4
depot architectures. Phase 1 was necessary but insufficient: a headless binary
that compiles but has no platform capabilities is not a useful system.

**Phase 2**: Replace `#[cfg]` exclusion fences with **trait-based platform
abstractions**. Every platform is a first-class evolution substrate. The same
interface works everywhere; only the backend implementation changes.

```
BAD:  #[cfg(target_os = "linux")] pub mod vfio;     // absent on Android
GOOD: trait DeviceDiscovery { fn discover(); }       // Vulkan on Android, sysfs on Linux

BAD:  #[cfg(unix)] UnixStream::connect(path)         // absent on Windows
GOOD: connect_transport(&TransportEndpoint::local())  // NamedPipe on Windows, UDS on Unix

BAD:  #[cfg(target_os = "linux")] fn health_check()  // no health on Android
GOOD: trait HealthProbe { fn check(); }               // HAL on Android, sysfs on Linux
```

**Reference implementation**: petalTongue `petal-tongue-platform`:
- `Platform` enum with capability queries (not exclusion flags)
- `PlatformLifecycle` trait (universal lifecycle, Android-modeled)
- `EmbeddedRuntime` (same capabilities everywhere, different transport)
- C-FFI surface (host embedding from any language)

**Each primal team**: identify your `#[cfg]` boundaries and evolve them toward
trait abstractions. The `#[cfg]` gate becomes one backend implementation among
many — not the only path.

---

## bearDog — COMPLETE

**Status**: DONE (`1c3dc9d`, `5d4258d`)
**Fix applied**: `IpcStream` enum dispatching to `UnixStream` on Unix and `TcpStream` on Windows. UDS code gated behind `#[cfg(unix)]`. `connect_tcp()` added for Windows path. `cargo check --target x86_64-pc-windows-gnu` passes.

**Windows harvest**: Ready for sporeGate. No UDS abstraction gaps remain.

---

## biomeOS

**Blocked by**: UDS transport + platform FS (Categories 1, 3)
**Files to modify**:

| Crate | File | Line(s) | Issue |
|-------|------|---------|-------|
| `biomeos-primal-sdk` | `src/communication.rs` | L39 | `UnixStream` |
| `biomeos-primal-sdk` | `src/capabilities.rs` | L17 | `UnixStream` |
| `biomeos-primal-sdk` | `src/provider.rs` | L304 | `UnixStream` |
| `biomeos-primal-sdk` | `src/tarpc_transport.rs` | L47 | `tarpc::serde_transport::unix` |
| `neural-api-client` | `src/connection.rs` | L11 | `UnixStream` |
| (FS) | disk space detection | — | `rustix::fs` + `rustix::system` |

**Fix**: Transport via `TransportEndpoint`. tarpc transport needs `#[cfg]` branching (tarpc has no built-in Windows transport — use TCP fallback). FS: `Platform::detect()` for disk space queries.

**Estimated effort**: Medium (5-6 files, tarpc requires care)

---

## nestGate

**Blocked by**: Platform FS (Category 3)
**Files to modify**:

| Crate | File | Issue |
|-------|------|-------|
| nestGate core | storage detector | `rustix::fs::statfs` — Linux-specific |

**Fix**: Abstract behind `Platform::detect()` with fallback using `std::fs::metadata` or `GetDiskFreeSpaceEx` on Windows.

**Estimated effort**: Small (1 module)

---

## rhizoCrypt

**Blocked by**: UDS transport (Category 1)
**Files to modify**:

| Crate | File | Line(s) | Issue |
|-------|------|---------|-------|
| `rhizo-crypt-core` | `src/clients/adapters/unix_socket.rs` | L29, L144-170 | `UnixStream` |

**Fix**: Rename to `transport.rs`, add `#[cfg(windows)]` NamedPipe path or `TransportEndpoint`.

**Estimated effort**: Small (1 file, well-isolated adapter)

---

## squirrel

**Blocked by**: UDS transport (Category 1)
**Files to modify**:

| Crate | File | Line(s) | Issue |
|-------|------|---------|-------|
| `squirrel/core/auth` | `src/capability_crypto.rs` | L32 | `UnixStream` |
| `squirrel/core/auth` | `src/security_provider_client.rs` | L27 | `UnixStream` |
| `squirrel/universal-patterns` | `src/ipc_client/connection.rs` | L6 | `UnixStream` |
| `squirrel/universal-patterns` | `src/registry/discovery.rs` | L15 | `UnixStream` |

**Fix**: All 4 files: `TransportEndpoint` or `#[cfg]` guards.

**Estimated effort**: Small-Medium (4 files, mechanical)

---

## sweetGrass

**Blocked by**: UDS transport (Category 1)
**Files to modify**:

| Crate | File | Issue |
|-------|------|-------|
| `sweet-grass-store-nestgate` | `src/client.rs` L10 | `UnixStream` |
| `sweet-grass-service` | multiple (transport_connect, handlers) | `UnixStream` |

**Fix**: `TransportEndpoint` for store client and service transport.

**Estimated effort**: Small-Medium (2-3 files)

---

## loamSpine

**Blocked by**: UDS transport + Unix signals (Categories 1, 2)
**Files to modify**:

| Crate | File | Line(s) | Issue |
|-------|------|---------|-------|
| `loam-spine-core` | `src/btsp/provider_client.rs` | L18 | `UnixStream` |
| `loam-spine-core` | `src/transport/neural_api.rs` | L31 | `UnixStream` |
| `loam-spine-core` | `src/service/signals.rs` | L97 | `tokio::signal::unix` |

**Fix**: Transport: `TransportEndpoint`. Signals: `ProcessManager::wait_for_shutdown()` or `#[cfg]` with `ctrl_c()` on Windows.

**Estimated effort**: Small (3 files)

---

## skunkBat

**Blocked by**: UDS transport + Unix signals (Categories 1, 2)
**Files to modify**:

| Crate | File | Line(s) | Issue |
|-------|------|---------|-------|
| `skunk-bat-server` | `src/ipc/transport/btsp.rs` | L78 | `UnixStream` |
| `skunk-bat-server` | `src/ipc/mod.rs` | L178 | `tokio::signal::unix::signal()` |

**Fix**: Transport: `TransportEndpoint`. Signal: `#[cfg]` + `ctrl_c()`.

**Estimated effort**: Small (2 files)

---

## coralReef

**Blocked by**: UDS transport (Category 1)
**Files to modify**:

| Crate | File | Line(s) | Issue |
|-------|------|---------|-------|
| `coralReef/primal-rpc-client` | `src/transport.rs` | L64 | `UnixStream` |

**Fix**: `TransportEndpoint` or `#[cfg]` guards.

**Estimated effort**: Small (1 file)

---

## barraCuda

**Blocked by**: UDS transport + Unix signals (Categories 1, 2)
**Files to modify**:

| Crate | File | Line(s) | Issue |
|-------|------|---------|-------|
| `barracuda-core` | `src/ipc/btsp.rs` | L153-546 | `UnixStream` (extensive) |
| `barracuda-core` | `src/ipc/transport/server.rs` | L2-3 | `UnixStream` |
| `barracuda-core` | `src/bin/barracuda/main.rs` | L158 | literal `unix` signal setup |

**Fix**: Transport: `TransportEndpoint` — this is the largest transport adoption (btsp.rs is ~400 lines of UDS code). Signal: `#[cfg]` + `ctrl_c()`.

**Estimated effort**: Medium (3 files, btsp.rs requires careful extraction)

---

## petalTongue — COMPLETE (Windows + Android core)

**Status**: DONE
- `0c65a57`: cross-arch transport — petal-tongue-core compiles for Windows + Android
- `7abeb16`: full workspace cross-compile for Windows — UDS abstraction complete
- Transport: `TransportStream` gains `#[cfg(unix)]` Uds + `#[cfg(windows)]` NamedPipe variants
- `BiomeOsClient` evolved from raw `UnixStream` to `TransportEndpoint`-based connection
- `#[cfg(target_os = "android")]` platform constraint detection in IPC server

**Windows harvest**: Ready. Full workspace cross-compile.
**Android harvest**: Core compiles. cdylib target config pending for NDK integration.
**Estimated remaining**: Small (Android cdylib Cargo.toml target config only)

---

## sourDough — COMPLETE (all 3 targets green)

**Status**: DONE
- `320397e`: Windows target support (Wave 141a)
- `6115e4a`: Android platform parity — `Os::Android` + `LibC::Bionic` (Wave 141b)
- All 3 cross-targets green (Linux, Windows, Android). 490 tests passing.
- New tests: `target_triple_android`, `simple_target_android`, `libc_bionic`

**genomeBin standard**: FULL. All 4 depot architectures compile. Needs sporeGate harvest for Android binary.

---

## toadStool — COMPLETE (full cfg gating)

**Status**: DONE
- `592248618` (S329): Windows cargo check passes
- S330 + S331: Deep debt (clone elimination, borrowed deserialization, +31 tests, clippy zero)
- hw-safe: All modules gated behind `#[cfg(target_os = "linux")]` — excludes BOTH Windows and Android
- cylinder: VFIO gated behind `#[cfg(all(target_os = "linux", feature = "vfio"))]`
- ember: vfio_anchor/vfio_handle/warm_keepalive all `#[cfg(target_os = "linux")]`

**Key insight**: Uses `target_os = "linux"` (not `unix`), so Android (`target_os = "android"`)
is correctly excluded alongside Windows. Non-Linux binaries are "headless" toadStool (no GPU
compute/VFIO) — expected behavior since GPU compute is Linux kernel API.

**genomeBin standard**: FULL for all 4 depot architectures. Non-Linux platforms get compute
fallback mode. Needs sporeGate harvest for Windows + Android binaries to verify.

---

## Completion Tracking

| Primal | Categories | Effort | Status | Commit |
|--------|-----------|--------|--------|--------|
| songBird | — | — | **DONE** (reference) | `2091974d` cfg gate evolution |
| bearDog | 1 | Small | **DONE** | `1c3dc9de6` tower-atomic cross-platform IPC |
| barraCuda | 1,2 | Medium | **DONE** | `7582ac73` Windows cross-compilation |
| biomeOS | 1,3 | Medium | **DONE** | `16b25557` v4.34 cross-arch + capability discovery |
| coralReef | 1 | Small | **DONE** | `da5afe1` cfg-gate Unix-only code |
| skunkBat | 1,2 | Small | **DONE** | `6b3e6eb` cross-arch + deep debt sweep |
| squirrel | 1 | Small-Med | **DONE** | `110c9939` Windows harvest unblock + deep debt |
| toadStool | 4 | Small | **DONE** | `592248618`→`ebeac34` S329-S335 full cfg + Phase 2 GPU + structural debt (−2,991L extracted, doc-comment sweep) |
| petalTongue | 1,5 | Medium | **DONE** | `7abeb16` full workspace Windows cross-compile |
| sourDough | 3 | Small | **DONE** | `6115e4a` Android platform parity (all 3 green) |
| rhizoCrypt | 1 | Small | **DONE** | `614ef3e` cross-arch + Phase 2 transport + SessionTreeHash |
| sweetGrass | 1 | Small-Med | **DONE** | `d4f7da9` platform gates |
| loamSpine | 1,2 | Small | **DONE** | `850252c` cfg-gate Unix IPC |
| nestGate | 3 | Small | **DONE** | `839122d2` cross-arch adoption (Session 109) |

**Score: 14/14 adopted. All primals cross-arch complete.**

Deep debt delivered alongside cross-arch (Waves 141a-142a):
- loamSpine: refactor, deprecation, clone reduction, test fix
- rhizoCrypt: method_gate split, magic numbers, branch/vertex coverage, Phase 2 transport, SessionTreeHash
- sweetGrass: postgres store purged (pure Rust dogma), cross-platform warnings suppressed
- nestGate: Category 3 (rustix::fs::statvfs gated) + Category 1 (UDS transport gated across 9 files)
- toadStool: S329-S336 deep debt + Phase 2 GPU + structural debt (23 files extracted, −3,164L, security_impl→crypto_integration, dead channels removed, 15 phantom deps scrubbed, 32GB cache freed)
- bearDog: libc removal, BTreeMap batch 4, test extraction wave 2
- squirrel: Windows harvest unblock + deep debt sweep
- sourDough: Android platform parity (Os::Android + LibC::Bionic, 490 tests)
- petalTongue: full workspace Windows cross-compile, UDS abstraction complete
- (Wave 141a): barraCuda, bearDog, biomeOS, coralReef, skunkBat, songBird — all delivered deep debt alongside cross-arch

---

## genomeBin Standard Readiness

All 14 primals now compile for all 4 depot architectures:

| Primal | Linux | aarch64 | Windows | Android | Notes |
|--------|-------|---------|---------|---------|-------|
| songBird | ✅ | ✅ | ✅ | ✅ | Reference implementation |
| bearDog | ✅ | ✅ | ✅ | ✅ | libc removed Wave 141b |
| barraCuda | ✅ | ✅ | ✅ | ✅ | |
| biomeOS | ✅ | ✅ | ✅ | ✅ | tarpc TCP fallback on non-Unix |
| coralReef | ✅ | ✅ | ✅ | ✅ | |
| skunkBat | ✅ | ✅ | ✅ | ✅ | |
| squirrel | ✅ | ✅ | ✅ | ✅ | Windows unblocked Wave 142a |
| toadStool | ✅ | ✅ | ✅ | ✅ | Phase 1 (gating) + Phase 2 (S332: `WgpuGpuDiscovery`, `PortableSwapExecutor`, `PortableResourceHandle`) |
| petalTongue | ✅ | ✅ | ✅ | ✅ | **Reference pattern**: petal-tongue-platform (cdylib + C-FFI + lifecycle) |
| sourDough | ✅ | ✅ | ✅ | ✅ | 490 tests, all 3 green |
| rhizoCrypt | ✅ | ✅ | ✅ | ✅ | Phase 2: `from_transport` shipped, `TransportHint` convergence TODO |
| sweetGrass | ✅ | ✅ | ✅ | ✅ | |
| loamSpine | ✅ | ✅ | ✅ | ✅ | |
| nestGate | ✅ | ✅ | ✅ | ✅ | |

**sporeGate re-harvest needed**: All 14 primals ready for full 4-architecture harvest.
Expected result: **56 depot binaries** (14 × 4 architectures).

---

## Phase 2: Abstraction Over Gating (Silicon Atheism Maturation)

**petalTongue established the reference pattern**: `petal-tongue-platform` (`1af1a98`).

Phase 1 (DONE): `#[cfg(target_os)]` gating — systems compile everywhere, but
platform-specific capabilities are excluded on non-native targets. This is
necessary but insufficient. A "headless" binary is not a useful system.

Phase 2 (NOW): **Universal platform abstraction** — don't exclude systems,
abstract them. Every platform gets the same interface with platform-appropriate
backends. petalTongue's pattern:

```
Platform enum    → capability queries (supports_uds?, prefers_tcp?, has_filesystem?)
PlatformLifecycle trait → universal lifecycle (create/start/resume/pause/stop/destroy)
EmbeddedRuntime  → same rendering + IPC everywhere, different transport per platform
C-FFI surface    → host embedding from Kotlin, Swift, C#, or direct Rust
cdylib + rlib    → shared library for host embedding AND Rust library for composition
```

### Primal abstraction targets (Phase 2)

| Primal | What to abstract | From → To |
|--------|-----------------|-----------|
| toadStool | glowplug DeviceDiscovery | sysfs → **`WgpuGpuDiscovery`** (S332: wgpu adapter enum, all platforms) |
| toadStool | glowplug SwapExecutor | sysfs unbind/rebind → **`PortableSwapExecutor`** (S332: logical personality swap) |
| toadStool | ember ResourceHandle | Linux VFIO fd → **`PortableResourceHandle`** (S332: `GpuBackend` enum, atomic liveness) |
| biomeOS | Neural API transport | tarpc unix → tarpc TCP (already done as fallback) |
| bearDog | HSM provider | Linux HIDRAW → Android Keystore / Windows DPAPI |
| squirrel | credential store | fs-based 0600 → Android Keystore / Windows DPAPI |

The key insight: `#[cfg()]` gating treats non-Linux as second-class. Platform
abstraction treats every target as a first-class evolution substrate. The
platform-specific code is not technical debt — it is constrained evolution where
the ecosystem adapts to hardware reality. But it should be **behind trait
boundaries**, not behind `#[cfg()]` exclusion fences.

---

*Updated Wave 142a: petalTongue petal-tongue-platform establishes Phase 2 reference
pattern (abstraction over gating). All 14 primals at genomeBin standard (Phase 1).
Phase 2 evolution targets identified for toadStool glowplug, bearDog HSM, squirrel
credentials.*
