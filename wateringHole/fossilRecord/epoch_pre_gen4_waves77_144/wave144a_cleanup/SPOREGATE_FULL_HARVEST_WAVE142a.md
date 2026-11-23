# sporeGate Full Harvest — Wave 142a

**Date**: Jul 16, 2026 | **Wave**: 142a | **From**: eastGate overwatch
**To**: sporeGate builder team
**Priority**: P0 — ALL BLOCKERS RESOLVED. Full genomeBin standard achieved.

---

## Directive

All 14 primals now compile for all 4 depot architectures. Execute full re-harvest
to produce **56 depot binaries** (14 primals × 4 architectures).

### What changed since last harvest (Wave 141b → 142a):

| Primal | Resolution | Commit |
|--------|-----------|--------|
| petalTongue | Full workspace Windows cross-compile (UDS abstraction) | `7abeb16` |
| squirrel | Windows harvest unblocked | `110c9939` |
| bearDog | libc removal (further Windows improvement) | `5d4258d95` |
| sourDough | Android platform parity (Os::Android + LibC::Bionic) | `6115e4a` |
| toadStool | S329 `#[cfg(target_os = "linux")]` confirmed to exclude Android | `592248618` |

## Phase 1: Full 4-Architecture Harvest (P0)

```bash
# Pull latest for all primals first
membrane temporal.cascade

# Windows — all 14 primals (was 11)
membrane plasmid.harvest --target x86_64-pc-windows-gnu --local

# Android — all 14 primals (was 11)
membrane plasmid.harvest --target aarch64-linux-android --local

# Linux (reference — verify still 14/14)
membrane plasmid.harvest --target x86_64-unknown-linux-musl --local
membrane plasmid.harvest --target aarch64-unknown-linux-musl --local
```

**Expected result**: 56 binaries (14 × 4 architectures).

Known platform-specific behaviors (NOT failures):
- toadStool on Windows/Android: headless mode (no GPU compute/VFIO — Linux kernel API)
- petalTongue on Android: binary compiles, but NDK cdylib integration is Phase 2

After harvest, push to VPS depot:
```bash
membrane plasmid.depot_sync --push
```

## Phase 2: Android Re-Harvest — SUPERSEDED

Previous Phase 2 is now merged into Phase 1. All 14 primals Android-ready.

## Phase 3: Exotic Architecture Expansion (P2)

With all primals cross-arch adopted, try RISC-V and ARMv7 for all primals
(not just songBird):

```bash
# RISC-V (open silicon — strategic)
for primal in songBird bearDog nestGate ...; do
  cargo check --target riscv64gc-unknown-linux-gnu --manifest-path $primal/Cargo.toml
done

# ARMv7 (Raspberry Pi / IoT)
for primal in songBird bearDog nestGate ...; do
  cargo check --target armv7-unknown-linux-gnueabihf --manifest-path $primal/Cargo.toml
done
```

Add passing architectures to the depot.

## Phase 4: portable-atomic (P1)

Enable `tokio` `portable-atomic` feature in all workspace `Cargo.toml` files:

```toml
[dependencies]
tokio = { version = "1", features = ["full", "portable-atomic"] }
```

Then test PPC32:
```bash
cargo check --target powerpc-unknown-linux-gnu
```

## Phase 5: Cross-Platform E2E Validation

After binaries are built, deploy and test on real hardware:

| Target | Hardware | Test |
|--------|----------|------|
| x86_64-windows-gnu | northGate (Windows, RTX 5090) | songbird.exe mesh enrollment, IPC via NamedPipe |
| aarch64-android | grapheneGate (Pixel 8) | Termux deploy, StrongBox interaction |
| x86_64-linux-musl | golgi (VPS) | Full NUCLEUS, depot serving, sporePrint |
| aarch64-linux-musl | sporeGate (if ARM board available) | Cross-compile validation |

### UDS vs NamedPipe vs TCP Validation Matrix

| Subsystem | Linux (UDS) | Windows (NamedPipe) | Android (TCP fallback) |
|-----------|------------|--------------------|-----------------------|
| Primal-to-primal IPC | `UnixStream` | `NamedPipeClient` | `TcpStream` |
| biomeOS Neural API | tarpc unix | tarpc TCP | tarpc TCP |
| Service lifecycle | systemd | Windows SCM | Termux init |
| Socket discovery | `/run/membrane/*.sock` | `\\.\pipe\primal-*` | `127.0.0.1:PORT` |
| Credential store | fs-based (0600) | DPAPI (future) | Android Keystore |

**Key validation**: primal A on Linux talks to primal B on Windows via songBird
mesh. The transport layer dispatches correctly based on platform.

---

## Success Criteria

```
Windows harvest:   14/14 binaries built (up from 11/14)
Android harvest:   14/14 binaries built (up from 11/14)
Total depot:       56 binaries (14 × 4 architectures)
Depot sync:        All binaries pushed to golgi VPS depot
BLAKE3+Ed25519:    All binaries signed
northGate test:    songbird.exe running, mesh enrolled
primalSpring:      full-cross-compile scenario GREEN
```

---

*Wave 142a: ALL BLOCKERS RESOLVED. Full genomeBin standard achieved for all 14 primals
across all 4 depot architectures. Execute full re-harvest. Target: 56 binaries.*
