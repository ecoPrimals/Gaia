# ToadStool Wave 155f — strandGate Deep Debt Evolution (S344)

**Date**: Jul 28, 2026 | **Gate**: strandGate | **Wave**: 155f
**Team**: toadStool code team (Compute Trio)
**Host**: Dual EPYC 7713 / RTX 3090 / 512GB

---

## Summary

Deep debt evolution sprint on strandGate. Expanded ecosystem compliance
(deny.toml), reduced overstep (feature-gated cross-primal deps), evolved
production stubs to proper errors, consolidated unsafe MMIO through hw-safe,
and centralized socket path resolution. All quality gates green.

**23,332 workspace tests, 0 failures.** Zero clippy. Zero fmt diff.

---

## Changes

### deny.toml — Pure Rust Crypto Standard (8 → 19+ bans)

Expanded banned crate list to align with `PURE_RUST_CRYPTO_PURITY_STANDARD.md`:

Added: `openssl`, `openssl-sys`, `boring`, `boring-sys`, `aws-lc-sys`,
`libsodium-sys`, `libsodium-ffi`, `sodiumoxide`, `secp256k1-sys`,
`libsecp256k1`, `blst`.

Pre-existing: `ring`, `aws-lc-rs`, `openssl-src`, `native-tls`,
`security-framework`, `security-framework-sys`, `schannel`, `async-trait`.

### Crypto Best-Effort Dispatch

`compute.dispatch.submit` crypto encryption evolved from hard failure
to graceful fallback. When `TOADSTOOL_FAMILY_ID` is unset or Tower crypto
unavailable, dispatch proceeds with unencrypted payload and logs a warning.
Fixes P0 test failures in environments without full Tower composition.

**File**: `crates/server/src/pure_jsonrpc/handler/dispatch/submit.rs`

### Overstep Reduction

| Dependency | Owner Primal | Gate |
|------------|-------------|------|
| `toadstool-display` | petalTongue | Feature-gated `display` (off default in cli + server) |
| `akida-driver` | squirrel | Feature-gated `npu` (off default in core/toadstool) |

### Clippy Evolution

3 `assigning_clones` fixes in distributed discovery crates:
- `coordination_integration/client/discovery.rs`
- `crypto_integration/client/discovery.rs`
- `security/discovery.rs`

Pattern: `*lock = val.clone()` → `(*lock).clone_from(&val)`

### Architecture Rename

`UniversalKernelCompiler` → `KernelStringOptimizer` — clarifies that this
performs string-level optimization, not compilation (which belongs to
coralReef).

### Socket Path Centralization

Eliminated inline `.join("crypto.sock")` fallbacks in:
- `integration/security/src/discovery.rs`
- `distributed/src/coordination/discovery/client.rs`
- `distributed/src/coordination_integration/client/rpc.rs`

All now use `get_socket_path_for_capability()` for consistent resolution.

### Production Stub Evolution

| Component | Before | After |
|-----------|--------|-------|
| Bluetooth connect/disconnect/execute | `Ok(())` (silent noop) | `ToadStoolError::not_supported` |
| macOS sandbox apply/remove | Compiled only on macOS | `SandboxError::PlatformNotSupported` on non-macOS |
| Webhook export | Silent log-only (no HTTP) | `ToadStoolError::not_supported` (needs songBird IPC) |
| `discover_nodes` RPC failure | Silently empty | Propagates error |

### MMIO Consolidation

Cylinder bins migrated from raw mmap/volatile to hw-safe containment:
- `rm_trigger/main.rs` — uses `Bar0` (delegates to `DeviceMmap`)
- `vfio/dma.rs` — volatile ops via `VolatileMmio`
- `vfio/channel/diagnostic/runner/mod.rs` — USERD reads via `VolatileMmio`
- `mmio.rs` — **deleted** (unified with hw-safe `VolatileMmio`)

### Migration CLI Gating

`UniversalCommands::Migrate` and associated tests gated behind
`migration-preview` feature (incomplete — not ready for default build).

### TCP Logging

riboCipher unhandled signal bytes on TCP connections now emit
`tracing::debug!` instead of silently dropping via `_ => {}`.

### SAFETY Documentation

`systemd_fdstore.rs`: `// Safe:` → `// SAFETY:` (convention alignment).

---

## Quality Gates

| Gate | Result |
|------|--------|
| `cargo build --workspace` | Clean |
| `cargo clippy --workspace -- -D warnings` | 0 warnings |
| `cargo test --workspace` | 23,332 passed, 0 failed |
| `cargo doc --workspace` | Clean |
| `cargo fmt --check` | 0 diffs |
| `cargo deny check bans` | Pass (19+ bans enforced) |

---

## Gaps for Upstream Review

| Gap | Owner | Notes |
|-----|-------|-------|
| 27 crates at `0.1.0` vs workspace `0.2.0` | toadStool | Version alignment pass needed |
| Local `infra/wateringHole/` mirror (71 files) | toadStool | Archive candidate — canonical copy at `ecoPrimals/infra/wateringHole/` |
| `crates/runtime/display/README.md` version stale | petalTongue | Shows `0.1.0` |
| Empty `tools/` directory | toadStool | Removed |
| `target/` = 112G | toadStool | `cargo clean` applied |

---

## For Upstream Teams

- **barraCuda**: `KernelStringOptimizer` rename (was `UniversalKernelCompiler`).
  If you import this type, update references.
- **coralReef**: No breaking changes.
- **petalTongue**: `toadstool-display` now behind `display` feature in cli + server.
  Add `features = ["display"]` if you depend on toadStool with display.
- **squirrel**: `akida-driver` now behind `npu` feature in core/toadstool.
  Add `features = ["npu"]` if you need neuromorphic dispatch.
- **Tower teams**: Crypto encryption in dispatch is now best-effort.
  If Tower crypto is unavailable, dispatch proceeds unencrypted with warning.
