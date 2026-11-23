# rhizoCrypt — G66 Transport Abstraction Handoff

**Date**: Aug 6, 2026  
**Wave**: 156s  
**Primal**: rhizoCrypt v0.14.17  
**Spec**: G66 Transport Abstraction (sourDough reference)  
**Status**: IMPLEMENTED — silicon-agnostic IPC layer complete

---

## What Was Done

### Transport Layer Evolution (G66)

rhizoCrypt's transport layer (`rhizo-crypt-core/src/transport.rs`) already had
`TransportEndpoint`, `TransportStream`, and `connect_transport()` from prior
waves. G66 completes the pattern:

1. **`TransportListener`** — Server-side transport abstraction with `bind()`
   and `accept()` for UDS and TCP. `#[cfg(unix)]` confined to the enum
   variant and match arm.

2. **`TransportEndpoint::platform_default()`** — UDS on Unix, TCP localhost
   on non-Unix. No `#[cfg]` in the caller.

3. **`TransportEndpoint::from_env_or_default()`** — Reads `TRANSPORT_ENDPOINT`
   (JSON) or `{PREFIX}_ADDRESS` (string) from environment, falls back to
   `platform_default()`. Full G66 transport injection.

4. **`TransportEndpoint::is_local()`** — Returns true for UDS and TCP
   localhost. G63 local-trust integration for `SO_PEERCRED` decisions.

5. **`TransportStream::is_local()` + `supports_peer_cred()`** — Runtime
   transport capability queries.

### G65 Protocol Negotiation — Now Transport-Agnostic

- `try_negotiate()` and `negotiate_client()` genericized to
  `S: AsyncRead + AsyncWrite + Unpin` (was `tokio::net::UnixStream`).
- `serve_tarpc_on_stream()` genericized to
  `S: AsyncRead + AsyncWrite + Unpin + Send + 'static`.
- `RpcClient::connect_negotiated_transport()` — G65+G66 composed: negotiate
  protocol on any `TransportEndpoint`.
- Stream-based tests moved behind `#[cfg(unix)]`; new TCP-based negotiation
  test proves platform-agnostic operation.

### Silicon Deism Audit

| Metric | Before G66 | After G66 |
|--------|-----------|----------|
| Unconditional `UnixStream` in protocol negotiation | 2 functions | 0 (generic) |
| `#[cfg(unix)]` locations outside transport layer | 0 (already clean) | 0 |
| `rustix` usage | 0 | 0 |
| Windows cross-compile (`x86_64-pc-windows-gnu`) | Pass | Pass |
| Protocol negotiation on TCP | Not possible | Proven by test |

---

## Verification

```
cargo clippy --workspace --all-features -- -D warnings   → 0 warnings
cargo test --workspace --all-features                     → 1,825 passed, 0 failed
cargo check --target x86_64-pc-windows-gnu                → pass
```

---

## Files Changed

| File | Change |
|------|--------|
| `crates/rhizo-crypt-core/src/transport.rs` | Add `TransportListener`, `platform_default()`, `from_env_or_default()`, `is_local()`, `supports_peer_cred()` |
| `crates/rhizo-crypt-core/src/lib.rs` | Export `TransportListener` |
| `crates/rhizo-crypt-core/src/transport_tests/g66_transport.rs` | 17 new G66 tests |
| `crates/rhizo-crypt-core/src/transport_tests/mod.rs` | Register `g66_transport` module |
| `crates/rhizo-crypt-rpc/src/protocol_negotiation.rs` | Genericize `try_negotiate`/`negotiate_client`, add TCP test |
| `crates/rhizo-crypt-rpc/src/jsonrpc/uds/connection.rs` | Genericize `serve_tarpc_on_stream` |
| `crates/rhizo-crypt-rpc/src/client.rs` | Add `connect_negotiated_transport()` |
| `graphs/rhizocrypt_deploy.toml` | Add `tcp-negotiated` transport |
| `CHANGELOG.md` | G66 entry |
| `CONTEXT.md` | G66 in IPC section + updated metrics |
| `README.md` | Updated test/file counts |
| `docs/DEPLOYMENT_CHECKLIST.md` | Updated metrics |
| `specs/RHIZOCRYPT_SPECIFICATION.md` | Updated test count |
| `sporeprint/validation-summary.md` | Updated metrics |

---

## G66 Posture

| Component | Status |
|-----------|--------|
| `TransportEndpoint` | Complete (UDS/TCP/MeshRelay + `platform_default` + `from_env_or_default` + `is_local`) |
| `TransportStream` | Complete (`AsyncRead + AsyncWrite` + `is_local` + `supports_peer_cred`) |
| `TransportListener` | Complete (UDS/TCP + `bind` + `accept`) |
| `connect_transport()` | Complete (pre-existing, `#[cfg]`-guarded) |
| G65 on `TransportStream` | Complete (generic negotiation) |
| G65+G66 composed client | Complete (`connect_negotiated_transport`) |
| Windows cross-compile | Pass |
| Silicon deism | Eliminated from protocol layer |

---

## Unblocked Capabilities

- **TCP-based protocol negotiation** — primals can negotiate tarpc/jsonrpc over TCP
- **Transport injection via environment** — biomeOS/launcher can inject endpoints
- **Cross-gate composition** — `TransportEndpoint::Tcp` enables cross-gate RPC
- **Windows development** — full compile + protocol negotiation works on Windows
- **Future transports** — WebSocket, QUIC, named pipes = new enum variants, zero protocol changes
