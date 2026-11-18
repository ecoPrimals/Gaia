# Handoff: toadStool G68 Platform Substrate Abstraction (S358)

**Date**: Aug 7, 2026 | **Wave**: 157a | **Author**: strandGate | **Sprint**: S358

---

## Summary

Implemented G68 Platform Substrate Abstraction for toadStool's L1 (filesystem links)
and L2 (access control) layers. Created centralized cross-platform primitives in
`toadstool-common::platform` that replace scattered inline `#[cfg(unix)]` blocks.

## New Module: `crates/core/common/src/platform/`

### `links.rs` — L1 Platform Links

```rust
pub fn platform_link(target: &Path, link: &Path) -> std::io::Result<()>
// Unix: std::os::unix::fs::symlink
// Windows: std::os::windows::fs::symlink_file / symlink_dir
// Other: Unsupported error
```

### `access.rs` — L2 Platform Access

```rust
pub enum PlatformAccess {
    OwnerOnly,             // unix: 0o600
    OwnerExclusive,        // unix: 0o700
    OwnerFullGroupTraverse,// unix: 0o750
    GroupShared,           // unix: 0o660
    Executable,            // unix: 0o755
    Custom(u32),           // env override passthrough
}

pub fn set_access(path: &Path, access: PlatformAccess) -> std::io::Result<()>
pub fn check_access(path: &Path, required: PlatformAccess) -> std::io::Result<bool>
```

## Migrated Call Sites

### L1 (3 sites)

| File | Purpose |
|------|---------|
| `server/src/unibin/mod.rs:241` | Legacy socket symlink (toadstool.sock → compute.sock) |
| `server/src/unibin/mod.rs:271` | C2 tarpc compat symlink |
| `core/toadstool/src/ipc/platform/unix.rs:97` | Capability symlink at bind time |

### L2 (7 production sites)

| File | Mode | Semantic |
|------|------|----------|
| `core/common/src/primal_sockets/api.rs` | 0o700 | OwnerExclusive |
| `server/src/unibin/format.rs` (x2) | 0o750 | OwnerFullGroupTraverse |
| `server/src/pure_jsonrpc/connection/unix.rs` | 0o660 (env override) | GroupShared / Custom |
| `server/src/tarpc_server/mod.rs` | 0o660 (env override) | GroupShared / Custom |
| `auto_config/src/installer/core.rs` | 0o755 | Executable |
| `core/nvpmu/src/permissions.rs` | caller-supplied | Custom |
| `core/common/src/secret_string.rs` | read 0o600 | check_access(OwnerOnly) |
| `runtime/native/src/validation.rs` | read executable | check_access(Executable) |

## Design Decisions

1. Module lives in `toadstool-common` — shared by all crates
2. Pure `std` on both platforms — no external deps
3. Windows L2 is best-effort (readonly flag / extension check) — proper ACL is follow-up
4. Socket server env override (`TOADSTOOL_SOCKET_MODE`) preserved via `PlatformAccess::Custom(mode)`
5. `#[cfg(unix)]` kept at socket-server call sites (policy: "only set socket perms when unix socket exists")

## Verification

| Check | Result |
|-------|--------|
| `cargo check -p toadstool-cli` (unix) | PASS |
| `cargo check -p toadstool-cli --target x86_64-pc-windows-msvc` | PASS |
| `cargo test -p toadstool-common -p toadstool-server -p nvpmu` | PASS (3,800+ tests) |
| `cargo fmt --check` | PASS |

## G68 Remaining Work

| Layer | Status | Next |
|-------|--------|------|
| L1 (links) | **DONE** — toadStool | Other primals converge independently |
| L2 (access) | **DONE** — toadStool | Other primals converge independently |
| L3 (device backends) | Already gated | Glacial: trait-based platform backends (hw-safe foundation) |
| Windows ACL | Best-effort stub | Follow-up: `windows-sys` ACL integration |

## Pushed To

- `golgiBody`: `020a19eba` on `main`
