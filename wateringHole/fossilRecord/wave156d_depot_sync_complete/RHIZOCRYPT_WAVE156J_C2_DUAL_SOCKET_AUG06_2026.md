# rhizoCrypt Wave 156j — G64 C2 Dual-Socket Pattern (Aug 6, 2026)

**Date**: Aug 6, 2026 | **Wave**: 156j | **Head**: `0961875`

## What Was Done

### G64 C2: tarpc Binary UDS (Dual-Socket Pattern)

rhizoCrypt now serves two UDS sockets:

```
rhizocrypt.sock       → JSON-RPC 2.0 (discovery, diagnostics, browser)
rhizocrypt.tarpc.sock → tarpc binary  (high-frequency primal-to-primal, sub-ms)
```

**Server side** (`rhizo-crypt-rpc`):
- `TarpcUdsServer` in `tarpc_uds.rs` (168 lines) — mirrors TCP `RpcServer` but over `tarpc::serde_transport::unix`
- `default_tarpc_socket_path()` — ecosystem-standard path resolution with BTSP family scoping
- Wired into service startup: both UDS listeners spawn unconditionally on Unix, with dual shutdown senders

**Client side** (`rhizo-crypt-rpc`):
- `RpcClient::connect_uds(path)` — same bincode + length-delimited framing as TCP but over UDS

**Constants** (`rhizo-crypt-core`):
- `TARPC_SOCKET_FILE_EXTENSION = ".tarpc.sock"`
- `family_scoped_tarpc_socket_path()` — derives tarpc path from primal ID + family scope

**Service integration** (`rhizocrypt-service`):
- `start_uds_listener` returns `(jsonrpc_shutdown, tarpc_shutdown, socket_path)` tuple
- `resolve_tarpc_uds_path()` derives `.tarpc.sock` from JSON-RPC socket path
- Shutdown signal propagates to both UDS servers

**Infrastructure**:
- tarpc `unix` feature enabled in workspace `Cargo.toml`
- Deploy graph updated with `transport = ["uds-jsonrpc", "uds-tarpc"]`

## Verification

| Check | Result |
|-------|--------|
| `cargo clippy --workspace --all-targets -- -D warnings` | PASS (0 warnings) |
| `cargo test --workspace --all-features` | **1,794 passing** (0 failures) |
| `cargo fmt --all --check` | PASS |
| `cargo deny check` | PASS (advisories ok, bans ok, licenses ok) |
| tarpc UDS roundtrip test | PASS (health check over `.tarpc.sock`) |
| tarpc UDS multi-operation test | PASS (create session → append → list → merkle → get vertex) |

## Metrics

| Metric | Value |
|--------|-------|
| Tests | **1,794** (+3 new tarpc UDS tests) |
| `.rs` files | **215** (+1 `tarpc_uds.rs`) |
| Lines | **~60,000** (+350 net) |
| Clippy | 0 warnings |
| Debt markers | 0 |
| `cargo deny` | Clean |

## What This Unblocks

1. **G64 cephalization Phase 1**: rhizoCrypt now serves tarpc binary over UDS alongside JSON-RPC — eliminates 5ms JSON-RPC overhead for intra-gate hot paths (provenance braiding, CAS ops)
2. **Ecosystem convergence**: Other primals on tarpc 0.37 can connect to `rhizocrypt.tarpc.sock` for direct binary RPC
3. **Cross-gate elevated path** (Phase 2): With all primals on tarpc 0.37 + dual-socket, songBird relay can bridge tarpc connections across gates

## Wave 156j Late — Clean Audit (Aug 6, 2026)

- Fix stale SPDX file count in CONTEXT.md (214 → 215)
- `cargo update`: clap 4.6.5→4.6.6, zerocopy 0.8.55→0.8.56
- Full debris scan: zero backup/temp/log/empty/orphan files, zero scripts, zero stale TODOs
- Zero debt markers in all 215 `.rs` files
- `cargo clean`: 10.6 GiB reclaimed
- All gates green: 1,794 tests, 0 clippy warnings, cargo deny clean

## Recent History

| Wave | Head | Key Changes |
|------|------|-------------|
| **156j** | **`0961875`** | **G64 C2 dual-socket: tarpc binary UDS + JSON-RPC UDS**, clean audit, dep update |
| 156h | `061acfa` | G64 cephalization audit (confirmed tarpc-wired), blake3 1.8.6 |
| 156e | `ab701b0` | G63 SO_PEERCRED: peer credential extraction on UDS |
| 156c | `cce0cb9` | RPC integration port collision fix, BTSP env isolation |
| 156b | `275ac42` | Wire `notify_dehydration_batch` (N→1 RPC), dead vendor HTTP purge |

## G64 Posture Update

rhizoCrypt has advanced from **tarpc-wired** to **tarpc-default + dual-socket**:
- **tarpc 0.37** service (28 ops) on both TCP and UDS
- **JSON-RPC 2.0** handler (39 methods, 7 domains) on both TCP and UDS
- **Dual-socket C2 pattern** ships alongside songBird and petalTongue
- **BTSP Phase 2+3** + **G63 SO_PEERCRED** local-trust on UDS
