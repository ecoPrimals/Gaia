# rhizoCrypt Wave 156m — G65 Protocol Negotiation (Aug 6, 2026)

**Date**: Aug 6, 2026 | **Wave**: 156m | **Head**: `a269b2c`

## What Was Done

### G65: Single-Socket Protocol Negotiation

rhizoCrypt now supports protocol negotiation on a single UDS socket, replacing
the C2 dual-socket pattern as Phase 3 of G64 cephalization.

```
Client: "PROTOCOLS: tarpc,jsonrpc\n"
Server: "PROTOCOL: tarpc\n"
→ Stream continues in tarpc binary (bincode + length-delimited)
```

No negotiation = JSON-RPC (full backward compatibility with existing clients).

**Server side** (`rhizo-crypt-rpc`):
- `protocol_negotiation.rs` (165 lines) — `IpcProtocol` enum, wire format parser/formatter, `try_negotiate()` server + `negotiate_client()` client
- Integration into `handle_uds_connection`: checks for `PROTOCOLS:` before BTSP/mito-beacon detection
- `serve_tarpc_on_stream()` — wraps already-connected `UnixStream` in bincode + length-delimited framing via `BaseChannel`
- `dispatch_g65()` + `extract_peer_caller()` helpers — keeps main handler under 100-line clippy limit

**Client side** (`rhizo-crypt-rpc`):
- `RpcClient::connect_negotiated(path)` — G65 client: negotiate then upgrade to tarpc binary framing on same socket

**Dependencies**:
- `tokio-serde` 0.9 + `tokio-util` 0.7 added as workspace dependencies for direct transport framing

**C2 dual-socket retained**: `.tarpc.sock` listener continues to operate for backward compatibility during ecosystem transition.

## Verification

| Check | Result |
|-------|--------|
| `cargo clippy --workspace --all-targets -- -D warnings` | PASS (0 warnings) |
| `cargo test --workspace --all-features` | **1,807 passing** (0 failures) |
| `cargo fmt --all --check` | PASS |
| `cargo deny check` | PASS (advisories ok, bans ok, licenses ok) |
| G65 tarpc negotiation E2E | PASS (negotiate tarpc → health check over same stream) |
| G65 JSON-RPC negotiation E2E | PASS (negotiate jsonrpc → health.check over same stream) |
| G65 backward compat E2E | PASS (no negotiation → JSON-RPC works unchanged) |
| G65 tarpc + session ops E2E | PASS (negotiate tarpc → create session → append → list) |

## Metrics

| Metric | Value |
|--------|-------|
| Tests | **1,807** (+13 over Wave 156j) |
| `.rs` files | **217** (+2: `protocol_negotiation.rs`, `uds_tests_g65.rs`) |
| Lines | **~60,800** (+800 net) |
| Clippy | 0 warnings |
| Debt markers | 0 |
| `cargo deny` | Clean |

## What This Unblocks

1. **G65 cephalization Phase 3**: rhizoCrypt serves tarpc + JSON-RPC on a single socket — eliminates socket proliferation (30→15 across ecosystem)
2. **Protocol-transparent routing**: songBird can route to rhizoCrypt without knowing which protocol to use — negotiation handles it
3. **Extensible**: future protocols (QUIC, gRPC) can be added to the `PROTOCOLS:` line without new sockets

## Recent History

| Wave | Head | Key Changes |
|------|------|-------------|
| **156m** | `a269b2c` | **G65 protocol negotiation on single socket** (Phase 3 of G64) |
| 156j | `0961875` | G64 C2 dual-socket: tarpc binary UDS + JSON-RPC UDS, clean audit |
| 156h | `061acfa` | G64 cephalization audit (confirmed tarpc-wired), blake3 1.8.6 |
| 156e | `ab701b0` | G63 SO_PEERCRED: peer credential extraction on UDS |
| 156c | `cce0cb9` | RPC integration port collision fix, BTSP env isolation |

## G65 Posture Update

rhizoCrypt has advanced from **C2 dual-socket** to **G65 protocol negotiation**:
- **G65 protocol negotiation** on `rhizocrypt.sock` — tarpc or JSON-RPC, client's choice
- **C2 dual-socket** retained for backward compatibility during transition
- **tarpc 0.37** service (28 ops) on TCP, UDS (C2), and negotiated single-socket
- **JSON-RPC 2.0** handler (39 methods, 7 domains) on TCP, UDS, and negotiated single-socket
- **BTSP Phase 2+3** + **G63 SO_PEERCRED** local-trust preserved through negotiation
