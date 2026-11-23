# nestGate — G68 Platform Substrate Abstraction

**Date**: Aug 7, 2026 | **Wave**: 157a | **Session**: 141 | **From**: eastGate overwatch

## Summary

nestGate implements G68 Platform Substrate Abstraction across all three layers (L1 links, L2 permissions, L3 process/statvfs/hostname). The `nestgate-platform` crate is now the canonical home for all platform-divergent APIs, eliminating direct `std::os::unix::*`, `PermissionsExt`, and scattered `rustix` calls from business-logic crates.

## What Changed

### New: `nestgate-platform` G68 Substrate Modules

| Module | G68 Layer | API Surface |
|--------|-----------|-------------|
| `platform::links` | L1 | `create_link()`, `remove_link()`, `is_link()` |
| `platform::fs` | L2 | `set_executable()`, `set_mode()`, `get_mode()` |
| `platform::process` | L3 | `is_pid_alive()`, `hostname()`, `runtime_base_dir()` |
| `platform::uid` | L3 (pre-existing) | `get_current_uid()`, `get_current_gid()` |
| `linux_proc` | L3 (pre-existing) | `statvfs_space()` — now the single entrypoint |

### Migrated Callers

| Crate | File | Before | After |
|-------|------|--------|-------|
| `nestgate-rpc` | `socket_config.rs` | `std::os::unix::fs::symlink`, `rustix::process::test_kill_process`, `rustix::system::uname` | `platform::links::create_link`, `platform::process::is_pid_alive`, `platform::process::hostname` |
| `nestgate-rpc` | `btsp_client.rs` | `rustix::process::getuid()` + `/run/user/{uid}` | `platform::process::runtime_base_dir()` |
| `nestgate-rpc` | `isomorphic_ipc/atomic/discovery.rs` | `rustix::process::getuid()` + hardcoded `/run/user` | `platform::process::runtime_base_dir()` |
| `nestgate-rpc` | `isomorphic_ipc/launcher.rs` | `std::os::unix::fs::MetadataExt` for UID | `platform::get_current_uid()` |
| `nestgate-rpc` | `storage_paths.rs` | `rustix::fs::statvfs()` | `linux_proc::statvfs_space()` |
| `nestgate-config` | `substrate_tiers.rs` | `rustix::fs::statvfs()` | `linux_proc::statvfs_space()` |
| `nestgate-storage` | `filesystem_detection.rs` | local `statvfs_space()` wrapper | `linux_proc::statvfs_space()` |
| `nestgate-storage` | `detection.rs` | `rustix::fs::statvfs()` (cfg-guarded) | `linux_proc::statvfs_space()` |

### Deep Debt Fixes

| Fix | Impact |
|-----|--------|
| **Discovery fabrication purged** | `nestgate-discovery` storage.rs and security.rs: endpoints changed from `zfs://pool-management` / `security://authentication` (pretending to be "dynamic") to honest `local://zfs.pool` / `local://identity.authenticate` self-knowledge with `source: "self-knowledge"` metadata |
| **Hardcoded backup paths removed** | `nestgate-zfs/config/security.rs`: `/backup/nestgate/keys` and `/offsite/nestgate/keys` → env-driven via `NESTGATE_KEY_BACKUP_PATHS` |
| **ZFS binary PATH lookup** | `/usr/sbin/zfs` and `/usr/sbin/zpool` → bare `"zfs"` / `"zpool"` (OS PATH resolution); `NESTGATE_ZFS_BINARY` / `NESTGATE_ZPOOL_BINARY` env override retained |
| **Runtime base centralized** | All `/run/user/{uid}` derivation now through `platform::process::runtime_base_dir()` |
| **Registry crosscheck test fixed** | `protocol` field: `as_str()` → `as_array()` to match C2 `["jsonrpc-2.0", "tarpc"]` |
| **Server module split** | `isomorphic_ipc/server/mod.rs` 784→659 lines; JSON-RPC keep-alive loop extracted to `jsonrpc_loop.rs` |
| **nestgate-config promoted dependency** | `nestgate-platform` moved from dev-dependency to regular dependency in `nestgate-config` |

### Remaining `rustix` in nestgate-rpc

| File | Usage | Reason |
|------|-------|--------|
| `transport_stream.rs` | `rustix::net::recv(...PEEK)` | G66 transport layer — correct home |
| `atomic/tests.rs` | `rustix::process::getuid()` | Test-only; acceptable |

## Verification

- **cargo check**: PASS (all features, native Linux)
- **cargo clippy --all-features -- -D warnings**: ZERO warnings
- **cargo check --workspace --target x86_64-pc-windows-gnu**: PASS (excluding fuzz/installer pre-existing)
- **cargo test** (excl. nestgate-api pre-existing): 2,200+ passed
- **nestgate-platform tests**: 26/26 passed (including new L1/L2/L3 tests)
- **capability_registry_crosscheck**: 11/11 passed

## Pre-existing Failures (Not Introduced)

- `nestgate-api` websocket: `Hasher` trait not in scope (Rust 2024 edition)
- `connect_transport_mesh_relay_no_coordinator`: runtime-within-runtime panic
- `payload_methods_are_filtered_correctly`: stale assertion
