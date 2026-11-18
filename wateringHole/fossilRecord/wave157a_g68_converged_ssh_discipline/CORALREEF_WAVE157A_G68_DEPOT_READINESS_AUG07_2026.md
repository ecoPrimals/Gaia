# coralReef Wave 157a — G68 Platform Substrate Deep Evolution

**Date**: 2026-08-07 | **Author**: coralReef code team (strandGate)
**Wave**: 157a | **From**: eastGate overwatch
**Gate**: strandGate

---

## SUMMARY

coralReef G68 deep evolution complete. 18 silicon deism sites identified and
evolved across ecosystem registration, BTSP discovery, provenance signing,
and security provider handshake. All IPC paths now use `TransportEndpoint` —
TCP works on non-Unix platforms when discovered. L1 links evolved (prior pass).
L2/L3: zero exposure.

## G68 EVOLUTION — coralReef

### L1: Links (done in prior pass)

| Function | Before | After |
|----------|--------|-------|
| `create_local_symlink()` | `Unsupported` on non-Unix | `symlink_file` on Windows, `Unsupported` only on exotic targets |

### IPC Deism → Transport-Agnostic (this pass)

| Module | Before (silicon deism) | After (G68) |
|--------|----------------------|-------------|
| `ecosystem/mod.rs` | `jsonrpc_bind_to_unix_path()` rejected TCP binds | `parse_bind_to_endpoint()` → `TransportEndpoint` (UDS or TCP) |
| `ecosystem/mod.rs` | `send_jsonrpc_line(&Path)` | `send_jsonrpc_line(&TransportEndpoint)` via `connect_transport()` |
| `ecosystem/mod.rs` | `heartbeat_loop(PathBuf)` | `heartbeat_loop(TransportEndpoint)` |
| `ecosystem/mod.rs` | Registration skipped on non-Unix | Registration attempts TCP when discovered |
| `btsp.rs` | `discover_by_capability() → PathBuf` | `discover_by_capability() → TransportEndpoint` |
| `btsp.rs` | `discover_security_socket() → PathBuf` | `discover_security_socket() → TransportEndpoint` |
| `btsp.rs` | `check_discovery_file_for_method()` UDS-only | Checks UDS → TCP → jsonrpc.bind fallback chain |
| `btsp.rs` | `security_rpc(&Path)` | `security_rpc(&TransportEndpoint)` |
| `btsp.rs` | `create_btsp_session(&Path)` | `create_btsp_session(&TransportEndpoint)` |
| `btsp_client.rs` | `handshake_on_stream_sync(&SyncTransportStream, &Path)` | `handshake_on_stream_sync(&SyncTransportStream, &TransportEndpoint)` |
| `btsp_client.rs` | `provider_rpc(&Path)` | `provider_rpc(&TransportEndpoint)` |
| `provenance.rs` | `CRYPTO_SIGN_SOCKET: OnceLock<Option<PathBuf>>` | `CRYPTO_SIGN_ENDPOINT: OnceLock<Option<TransportEndpoint>>` |
| `provenance.rs` | `try_sign()` via `connect_local_sync(path)` | `try_sign()` via `connect_transport_sync(endpoint)` |

### New API: `TransportEndpoint::from_bind_string()`

Canonical parser for ecosystem bind strings. Handles all formats:
- `unix:///path/to/socket.sock` → `TransportEndpoint::Uds`
- `/absolute/path.sock` → `TransportEndpoint::Uds`
- `tcp://host:port` → `TransportEndpoint::Tcp`
- `host:port` → `TransportEndpoint::Tcp`

Lives in `transport.rs` — accessible from both lib and bin targets.

### L2 (Permissions) / L3 (Device backends)

Zero exposure. coralReef is a pure compiler primal — no `PermissionsExt`,
no `set_mode`, no `rustix`/`libc` for device backends.

## G68 AUDIT SUMMARY

| Classification | Count | Notes |
|----------------|------:|-------|
| Same thing differently | 45 | G66 transport enums, async/sync delegation, Windows symlinks, signal handling |
| Silicon deism (was) | 18 | All evolved to `TransportEndpoint`-based transport-agnostic paths |
| Silicon deism (remaining) | 0 | All `#[cfg(unix)]` now confined to `transport.rs` (G66 substrate) |

Remaining `#[cfg(unix)]` in `transport.rs` is legitimate — that's where
platform gates belong per G66. Business logic never touches `#[cfg(unix)]`.

## PRE-EXISTING CLIPPY FIXES

- `protocol_negotiation.rs`: `items_after_statements` in 3 test functions
- `tolerances.rs`: `assertions_on_constants` in 12 test assertions

## CROSS-ARCH STATUS

- `cargo clippy --all-features --all-targets -- -D warnings` — zero warnings (Linux)
- `cargo clippy --target x86_64-pc-windows-gnu --all-features -- -D warnings` — zero warnings

## TEST STATUS

- All tests pass, 0 failures, 6 ignored (hardware-gated)
- Zero `unsafe` in production
- Zero clippy warnings on Linux + Windows

---

## SCANNER FALSE POSITIVE REPORT — sourDough G68 Audit

The `G68_CROSS_DEPLOYMENT_AUDIT_AUG07_2026.md` reports **56 L2 violations**
for coralReef (`PermissionsExt` / `set_mode` / `from_mode`). **All 56 are
false positives.** The scanner pattern-matched GPU texture instruction field
names as permission APIs:

| Scanner match | Actual code | Count |
|---------------|-------------|------:|
| `offset_mode` | `TexOffsetMode` (GPU tex instruction field) | 42 |
| `set_su_ga_offset_mode` | Surface address mode setter (GPU encoder) | 8 |
| `set_mode` | Never appears as `PermissionsExt::set_mode()` | 0 |
| `from_mode` | `TexOffsetMode::from(...)` pattern (GPU) | 6 |

**Verification**:
```
rg 'PermissionsExt' crates/ → 0 matches
rg 'set_mode\(0o'  crates/ → 0 matches
rg 'from_mode\(0o' crates/ → 0 matches
rg 'set_permissions' crates/ → 0 matches
```

**Root cause**: Scanner uses substring/regex on `_mode` / `set_mode` without
verifying the import is `std::os::unix::fs::PermissionsExt`. GPU compiler
code has hundreds of `*_mode` fields (texture offset modes, addressing modes,
comparison modes, etc.).

**Recommendation for sourDough team**: L2 scanner should require
`use std::os::unix::fs::PermissionsExt` import or `Permissions::from_mode`
full path to avoid false positives from domain-specific field names.

**Actual L2 status**: **ZERO violations**. coralReef is a pure compiler primal
with no filesystem permission manipulation.

## L1 STATUS

The audit reports 1 L1 violation in `transport.rs`. This is our
`create_local_symlink()` function which **already implements G68 L1**:
- Unix: `std::os::unix::fs::symlink`
- Windows: `std::os::windows::fs::symlink_file`
- Other: `Unsupported`

The scanner flags the raw `std::os::unix::fs::symlink` import inside the
platform abstraction function itself. This is legitimate per G68 spec:
"a `#[cfg(unix)]` on a backend implementation behind a trait is acceptable."

## G66 RAW % STATUS

Audit reports 8% raw (14 raw uses, 157 G66 adopted). Breakdown:

| File | Raw uses | Type | Justified? |
|------|---------|------|------------|
| `transport.rs` | 10 | G66 substrate (the abstraction itself) | Yes — cannot be further abstracted |
| `primal-rpc-client/transport.rs` | 3 | G66 substrate (LocalStream enum) | Yes — the abstraction |
| 9 test files | ~25 | Test code (mock listeners, stream pairs) | Yes — per G68 spec |

All production "raw" uses are inside the G66 substrate layer itself. They
ARE the abstraction — business logic never touches `UnixStream` directly.
The 8% ratio is irreducible for coralReef.

---

*coralReef Wave 157a. G68 deep evolution: 18 silicon deism sites evolved to
TransportEndpoint-based transport-agnostic paths. Ecosystem registration,
BTSP discovery, provenance signing all work on non-Unix via TCP when
discovered. Zero L2/L3 exposure (56 scanner L2 reports are false positives —
GPU texture field names, not PermissionsExt). Cross-arch PASS.*
